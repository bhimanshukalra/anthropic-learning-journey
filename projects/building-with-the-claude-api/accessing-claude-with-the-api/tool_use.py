import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, ValidationError

from claude_helpers import (
    CLAUDE_MODEL,
    DEFAULT_TEMPERATURE,
    add_user_message,
    client,
    extract_text,
    print_message_metadata,
)

MAX_TOOL_LOOPS = 5


# Pydantic validates tool inputs after Claude asks for a tool call. The JSON
# schemas below guide Claude, but local validation is still the real guardrail.
class LookupOrderInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: str


class ConvertTemperatureInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    celsius: float


class SupportPolicyInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topic: Literal["shipping", "refunds", "warranty"]


@dataclass
class ToolSpec:
    validator: type[BaseModel]
    function: Callable[[BaseModel], dict[str, Any]]


ORDERS = {
    "A123": {
        "status": "in_transit",
        "carrier": "DHL",
        "eta": "2026-07-29",
        "destination": "Mumbai",
    },
    "B456": {
        "status": "delivered",
        "carrier": "Blue Dart",
        "eta": "2026-07-20",
        "destination": "Bengaluru",
    },
}

SUPPORT_POLICIES = {
    "shipping": "If an in-transit order is delayed beyond the ETA, offer tracking help before refund options.",
    "refunds": "Refunds can be started after delivery, failed delivery, or a confirmed lost shipment.",
    "warranty": "Warranty coverage lasts 12 months and excludes accidental damage.",
}


# These schemas are sent to Claude. They describe what tools exist, but they do
# not execute anything; Claude can only request a tool call.
TOOLS = [
    {
        "name": "lookup_order",
        "description": "Look up shipping status for a customer order by order ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The customer order ID, for example A123.",
                }
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "convert_celsius_to_fahrenheit",
        "description": "Convert a Celsius temperature to Fahrenheit.",
        "input_schema": {
            "type": "object",
            "properties": {
                "celsius": {
                    "type": "number",
                    "description": "Temperature in degrees Celsius.",
                }
            },
            "required": ["celsius"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_support_policy",
        "description": "Return a short internal support policy for a topic.",
        "input_schema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "enum": ["shipping", "refunds", "warranty"],
                    "description": "Support policy topic to retrieve.",
                }
            },
            "required": ["topic"],
            "additionalProperties": False,
        },
    },
]


# These are the actual local Python functions. In a real app, this is where you
# would call databases, internal APIs, search indexes, or business systems.
def lookup_order(args: BaseModel) -> dict[str, Any]:
    order_id = args.order_id
    order = ORDERS.get(order_id)
    if not order:
        raise ValueError(f"Unknown order ID: {order_id}")

    return {"order_id": order_id, **order}


def convert_celsius_to_fahrenheit(args: BaseModel) -> dict[str, Any]:
    fahrenheit = (args.celsius * 9 / 5) + 32
    return {
        "celsius": args.celsius,
        "fahrenheit": round(fahrenheit, 1),
    }


def get_support_policy(args: BaseModel) -> dict[str, Any]:
    return {
        "topic": args.topic,
        "policy": SUPPORT_POLICIES[args.topic],
    }


# Claude tool name -> Pydantic validator -> Python function
TOOL_REGISTRY = {
    "lookup_order": ToolSpec(LookupOrderInput, lookup_order),
    "convert_celsius_to_fahrenheit": ToolSpec(
        ConvertTemperatureInput, convert_celsius_to_fahrenheit
    ),
    "get_support_policy": ToolSpec(SupportPolicyInput, get_support_policy),
}


def serialize_content_blocks(content_blocks: list[Any]) -> list[dict[str, Any]]:
    # Claude's assistant message, including tool_use blocks, must be sent back
    # in the next request so the following tool_result blocks have context.
    return [block.model_dump(exclude_none=True) for block in content_blocks]


def find_tool_uses(message: Any) -> list[Any]:
    # A response can contain normal text, tool_use blocks, or both.
    return [block for block in message.content if block.type == "tool_use"]


def execute_tool(tool_use: Any) -> dict[str, Any]:
    tool_name = tool_use.name
    tool_spec = TOOL_REGISTRY.get(tool_name)

    if not tool_spec:
        return {
            "type": "tool_result",
            "tool_use_id": tool_use.id,
            "is_error": True,
            "content": f"Unknown tool: {tool_name}",
        }

    try:
        # Validate Claude's proposed input before trusting it.
        validated_input = tool_spec.validator.model_validate(tool_use.input)
        result = tool_spec.function(validated_input)
        content = json.dumps(result)
        is_error = False
    except (ValidationError, ValueError, KeyError) as error:
        content = str(error)
        is_error = True

    return {
        "type": "tool_result",
        # The ID is what lets Claude match this result to the exact tool_use block.
        "tool_use_id": tool_use.id,
        "is_error": is_error,
        "content": content,
    }


def create_tool_message(messages: list[dict[str, Any]]) -> Any:
    return client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=700,
        messages=messages,
        tools=TOOLS,
        temperature=DEFAULT_TEMPERATURE,
    )


def run_tool_loop(
    user_prompt: str,
) -> tuple[Any, list[dict[str, Any]], int, list[dict[str, Any]]]:
    messages = []
    tool_calls = []
    add_user_message(messages, user_prompt)

    for loop_count in range(1, MAX_TOOL_LOOPS + 1):
        message = create_tool_message(messages)
        tool_uses = find_tool_uses(message)

        # No tool_use blocks means Claude is done and has produced the final answer.
        if not tool_uses:
            return message, messages, loop_count, tool_calls

        messages.append(
            {
                "role": "assistant",
                "content": serialize_content_blocks(message.content),
            }
        )

        tool_results = []
        for tool_use in tool_uses:
            tool_result = execute_tool(tool_use)
            tool_calls.append(
                {
                    "name": tool_use.name,
                    "input": tool_use.input,
                    "is_error": tool_result["is_error"],
                }
            )
            tool_results.append(tool_result)

        # Send all tool results together. This supports multiple tool calls from
        # one assistant response before asking Claude to continue.
        messages.append({"role": "user", "content": tool_results})

    raise RuntimeError(f"Exceeded max tool loop count: {MAX_TOOL_LOOPS}")


def main():
    """
    User asks -> Claude requests tools -> Python runs tools ->
    Python sends results -> Claude answers
    """
    prompt = """
Order A123 is going to Mumbai where it is 32 C today.
Look up the order, convert the temperature to Fahrenheit, check the shipping policy,
and then give the customer a concise support update.
"""

    final_message, _, loop_count, tool_calls = run_tool_loop(prompt)

    print("Final answer:")
    print(extract_text(final_message))

    print()
    print("Tool loop summary:")
    print(f"- Loop count: {loop_count}")
    print("- Tool calls:")
    if not tool_calls:
        print("  - none")
    else:
        for tool_call in tool_calls:
            print(
                f"  - {tool_call['name']} "
                f"input={json.dumps(tool_call['input'])} "
                f"is_error={tool_call['is_error']}"
            )
    print_message_metadata(final_message)


if __name__ == "__main__":
    main()
