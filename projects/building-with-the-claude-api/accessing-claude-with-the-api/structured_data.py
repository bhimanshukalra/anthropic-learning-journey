import json
from typing import Any, Literal

from anthropic import transform_schema
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from claude_helpers import (
    CLAUDE_MODEL,
    DEFAULT_TEMPERATURE,
    add_user_message,
    client,
    extract_text,
    print_message_metadata,
)

MAX_ATTEMPTS = 3


class EventBridgeRule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="Short kebab-case rule name.")
    description: str = Field(
        description="One sentence explaining what the rule catches."
    )
    event_source: Literal["aws.ec2", "aws.s3", "aws.iam", "custom.app"]
    detail_type: str
    enabled: bool
    targets: list[str] = Field(
        description="Target names that should receive the event."
    )
    risk_level: Literal["low", "medium", "high"]


SYSTEM_PROMPT = """
You generate AWS EventBridge rule drafts for engineers.
Return only JSON that matches the requested schema.
Do not include markdown fences, comments, or prose outside the JSON object.
"""

USER_PROMPT = """
Create a short EventBridge rule for detecting EC2 instance state changes.
Use realistic field values and one or two targets.
"""

BAD_RULE_FOR_REPAIR = """
{
  "name": "ec2-state-change",
  "description": "Detects EC2 state changes.",
  "event_source": "aws.lambda",
  "detail_type": "EC2 Instance State-change Notification",
  "enabled": "yes"
}
"""


def event_bridge_schema() -> dict[str, Any]:
    """Turning Pydantic Into Claude JSON Schema"""
    return transform_schema(EventBridgeRule)


def request_event_rule(prompt: str) -> Any:
    """Calling Claude With Structured Output"""
    messages = []
    add_user_message(messages, prompt)

    return client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=messages,
        temperature=DEFAULT_TEMPERATURE,
        output_config={
            "format": {
                "type": "json_schema",
                "schema": event_bridge_schema(),
            }
        },
    )


def parse_and_validate(raw_json: str) -> EventBridgeRule:
    parsed = json.loads(raw_json)
    return EventBridgeRule.model_validate(parsed)


def build_repair_prompt(raw_json: str, error: Exception) -> str:
    return f"""
The JSON below failed validation against the EventBridgeRule schema.

Validation error:
{error}

Invalid JSON:
{raw_json}

Return corrected JSON only.
"""


def generate_valid_rule(
    prompt: str, *, max_attempts: int = MAX_ATTEMPTS
) -> tuple[EventBridgeRule, Any, int]:
    current_prompt = prompt

    for attempt in range(1, max_attempts + 1):
        # ask Claude
        message = request_event_rule(current_prompt)
        # extract JSON text
        raw_json = extract_text(message).strip()

        try:
            # try to parse + validate, if valid: return it
            return parse_and_validate(raw_json), message, attempt
        except (json.JSONDecodeError, ValidationError) as error:
            if attempt == max_attempts:
                raise
            # if invalid: send repair prompt
            current_prompt = build_repair_prompt(raw_json, error)

    raise RuntimeError("Structured output retry loop ended unexpectedly.")


def repair_invalid_rule(
    raw_json: str, *, max_attempts: int = 2
) -> tuple[EventBridgeRule, Any, int]:
    """Repair Known Bad JSON"""
    current_json = raw_json

    for attempt in range(1, max_attempts + 1):
        try:
            # try to parse + validate, if valid: return it
            return parse_and_validate(current_json), None, attempt
        except (json.JSONDecodeError, ValidationError) as error:
            # ask Claude to repair
            message = request_event_rule(build_repair_prompt(current_json, error))
            # extract JSON text
            current_json = extract_text(message).strip()

            try:
                # try to parse + validate, if valid: return it
                return parse_and_validate(current_json), message, attempt
            except (json.JSONDecodeError, ValidationError):
                if attempt == max_attempts:
                    raise

    raise RuntimeError("Repair loop ended unexpectedly.")


def print_validated_rule(label: str, rule: EventBridgeRule, attempts: int) -> None:
    print(label)
    print(f"Attempts: {attempts}")
    print(json.dumps(rule.model_dump(), indent=2))


def main():
    """
    Define schema -> ask Claude for JSON -> parse JSON ->
    validate with Pydantic -> retry if invalid
    """
    generated_rule, generated_message, generated_attempts = generate_valid_rule(
        USER_PROMPT
    )
    print_validated_rule(
        "Validated generated rule:", generated_rule, generated_attempts
    )
    print_message_metadata(generated_message)

    print()
    print("Deliberate failure case:")
    repaired_rule, repair_message, repair_attempts = repair_invalid_rule(
        BAD_RULE_FOR_REPAIR
    )
    print_validated_rule("Validated repaired rule:", repaired_rule, repair_attempts)
    if repair_message:
        print_message_metadata(repair_message)


if __name__ == "__main__":
    main()
