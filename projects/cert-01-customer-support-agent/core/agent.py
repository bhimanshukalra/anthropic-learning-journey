import json
from anthropic.types import Message
from core.claude import Claude
from mcp_client import MCPClient
from datetime import datetime, timezone

SYSTEM = """You are a customer-support resolution agent. Use the tools to look up customers and orders and answer the user. Pick the single most appropriate tool for each step."""
GATED_TOOLS = {"lookup_order", "process_refund"}
REFUND_LIMIT = 500.0
STATUS_LABELS = {
    0: "pending",
    1: "processing",
    2: "shipped",
    3: "out_for_delivery",
    4: "delivered",
    5: "cancelled",
}


def _to_iso(value) -> str:
    """Unix epoch (int/float) OR an ISO-ish string -> a single canonical ISO-8601 UTC string."""
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()
    return str(value).replace("Z", "+00:00")


def hook_normalize_order(tool_name: str, result: dict, agent: SupportAgent) -> dict:
    """PostToolUse: rewrite an order payload into one consistent date/status shape."""
    order = result.get("order")
    if isinstance(order, dict):
        if "placed_at" in order:
            order["placed_at"] = _to_iso(order["placed_at"])
        if isinstance(order.get("status"), int):
            order["status"] = STATUS_LABELS.get(
                order["status"], f"unknown({order['status']})"
            )
    return result


def hook_verify_gate(
    tool_name: str, tool_input: dict, agent: SupportAgent
) -> dict | None:
    """PreToolUse: block gated tools until a single customer is verified."""

    if tool_name in GATED_TOOLS and agent.verified_customer_id is None:
        return {
            "block": {
                "isError": True,
                "errorCategory": "permission",
                "isRetryable": False,
                "message": (
                    "Identity not verified. Call get_customer and confirm a SINGLE "
                    "matching customer before looking up orders or issuing refunds."
                ),
            }
        }
    return None


def hook_refund_cap(tool_name: str, tool_input: dict, agent) -> dict | None:
    """PreToolUse: a refund over $500 is never auto-issued, redirect it to a human."""
    if (
        tool_name == "process_refund"
        and float(tool_input.get("amount", 0)) > REFUND_LIMIT
    ):
        return {
            "redirect": (
                "escalate_to_human",
                {
                    "reason": "refund_over_limit",
                    "summary": (
                        f"Refund of ${tool_input.get('amount')} on order "
                        f"{tool_input.get('order_id')} exceeds the ${REFUND_LIMIT:.0f} "
                        f"auto-approve limit; routing to a human for approval."
                    ),
                },
            )
        }
    return None


def hook_latch_verification(tool_name: str, result: dict, agent) -> dict:
    """PostToolUse: latch the id when get_customer returns exactly one match."""
    if tool_name == "get_customer" and result.get("count") == 1:
        agent.verified_customer_id = result["matches"][0]["id"]
    return result


PRE_HOOKS = [hook_verify_gate, hook_refund_cap]
POST_HOOKS = [hook_latch_verification, hook_normalize_order]


class SupportAgent:
    def __init__(self, claude: Claude, client: MCPClient):
        self.claude = claude
        self.client = client
        self.messages: list = []
        self.verified_customer_id: str | None = None  # latched one, in code

    async def _tool_schemas(self) -> list[dict]:
        tools = await self.client.list_tools()
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.inputSchema,
            }
            for t in tools
        ]

    def _run_pre_hooks(self, tool_name, tool_input):
        for hook in PRE_HOOKS:
            decision = hook(tool_name, tool_input, self)
            if decision is not None:
                return decision
        return None

    def _run_post_hooks(self, tool_name, result: dict) -> dict:
        for hook in POST_HOOKS:
            result = hook(tool_name, result, self)
        return result

    async def _run_tools(self, response: Message) -> list[dict]:
        """Execute every tool_use block the model emitted; return tool_result blocks."""
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            name, args = block.name, block.input
            print(f"tool_use: {name}({json.dumps(args)})")

            decision = self._run_pre_hooks(name, args)  # PreToolUse
            if decision and "block" in decision:
                print(f"⛔ blocked: {name}")
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(decision["block"]),
                        "is_error": True,
                    }
                )
                continue

            if decision and "redirect" in decision:
                name, args = decision["redirect"]  # swap the call
                print(f"redirected to: {name}({json.dumps(args)})")

            output = await self.client.call_tool(name, args)
            text = output.content[0].text if output and output.content else "{}"

            try:
                result = json.loads(text)
            except (ValueError, TypeError):
                result = {}

            result = self._run_post_hooks(name, result)
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                    "is_error": bool(result.get("isError")),
                }
            )

        return results

    @staticmethod
    def _is_error_envelope(text: str) -> bool:
        """True if a tool returned the isError envelope (so the API marks the result as an error.)"""
        try:
            return bool(json.loads(text).get("isError"))
        except (ValueError, AttributeError):
            return False

    async def run(self, user_text: str, max_steps: int = 8) -> str:
        self.messages.append({"role": "user", "content": user_text})
        tools = await self._tool_schemas()

        for _ in range(max_steps):  # runaway guard, NOT the stop condition
            response = self.claude.chat(
                messages=self.messages, system=SYSTEM, tools=tools
            )
            self.messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "tool_use":  # the real driver
                tool_results = await self._run_tools(response)
                self.messages.append({"role": "user", "content": tool_results})
                continue

            # stop_reason == "end_turn" (or any non-tool stop) -> we're done
            return self.claude.text_from_message(response)
        return "Stopped after too many steps - please rephrase or contact support."
