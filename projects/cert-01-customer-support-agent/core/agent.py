"""The support agent: the agentic loop plus its guardrails.

Two enforcement layers work together here:
  - SYSTEM prompt -> probabilistic guidance (the model usually follows it)
  - hooks         -> deterministic guarantees (code the model cannot override)
"""

from __future__ import annotations

import json
from anthropic.types import Message
from core.claude import Claude
from mcp_client import MCPClient
from datetime import datetime, timezone

SYSTEM = """You are a customer-support resolution agent. Use the tools to look up customers and orders and resolve the request. Pick the single most appropriate tool for each step.

POLICIES (also enforced in code — violations are blocked — but follow them proactively so the
customer gets a graceful answer instead of a blocked call):
1. VERIFY IDENTITY FIRST: confirm a SINGLE matching customer via get_customer before calling
   lookup_order or process_refund. If identity isn't verified yet, verify it first.
2. REFUND LIMIT $500: refunds over $500 are NEVER auto-issued. Tell the customer amounts over
   $500 require manual review, and hand off via escalate_to_human with a self-contained summary
   instead of attempting process_refund.

ESCALATE TO A HUMAN only when one of these is true:
1. The customer EXPLICITLY asks for a human - escalate immediately, do NOT investigate first.
2. POLICY GAP / SILENCE - the policy does not cover the situation (e.g. a competitor price-match)
3. INABILITY TO PROGRESS — you are blocked and no tool or question can move the case forward.

Do NOT escalate because a case seems COMPLEX, because the customer sounds FRUSTRATED, or because you
feel UNSURE — none of those mean a human is needed. Resolve what you can.

If get_customer returns MORE THAN ONE match, do NOT guess — ASK the customer for another identifier
(order number, full name) to disambiguate.

When you do escalate, call escalate_to_human with a SELF-CONTAINED summary — the human cannot see this
conversation.

Examples:
- "This is broken and I want my money back, here's a photo" → damage replacement is covered → RESOLVE
  (process the return/refund); do NOT escalate.
- "Just connect me to a person." → explicit request → ESCALATE immediately.
- "Will you match Acme's lower price?" and policy only covers our own pricing → POLICY GAP → ESCALATE.
- "I'm furious this took so long!" with an otherwise normal refund → frustration is NOT a trigger →
  RESOLVE the refund.

When a message contains MULTIPLE concerns, address EACH one (use the right tool per concern) and then
combine the outcomes into a SINGLE clear reply. Do not drop a concern or answer only the first.
"""

GATED_TOOLS = {"lookup_order", "process_refund"}  # blocked until identity is verified
REFUND_LIMIT = 500.0  # refunds above this always go to a human
# The backend reports order status as ints; the model reasons better over words.
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
                    "customer_id": agent.verified_customer_id,
                    "root_cause": "refund_over_limit",
                    "recommended_action": "Review and approve/deny the refund manually.",
                    "refund_amount": float(tool_input.get("amount", 0)),
                },
            )
        }
    return None


def hook_latch_verification(tool_name: str, result: dict, agent) -> dict:
    """PostToolUse: latch the id when get_customer returns exactly one match."""
    if tool_name == "get_customer" and result.get("count") == 1:
        agent.verified_customer_id = result["matches"][0]["id"]
    return result


# Pre-hooks run BEFORE a tool call and can block or redirect it. Order matters:
# the verify gate rules first, so the refund cap can assume a verified customer.
PRE_HOOKS = [hook_verify_gate, hook_refund_cap]
# Post-hooks rewrite a result AFTER the call, before the model ever sees it.
POST_HOOKS = [hook_latch_verification, hook_normalize_order]


class SupportAgent:
    def __init__(self, claude: Claude, client: MCPClient):
        self.claude = claude
        self.client = client
        self.messages: list = []  # full conversation history, resent on every API call
        self.verified_customer_id: str | None = None  # latched one, in code
        self.case_facts: dict = {}  # durable numbers/IDs/dates

    def _capture_facts(self, tool_name: str, result: dict) -> None:
        """Pull the few fields worth keeping out of a (normalized) tool result."""
        if tool_name == "get_customer" and result.get("count") == 1:
            self.case_facts["customer_id"] = result["matches"][0]["id"]

        order = result.get("order")
        if isinstance(order, dict):
            self.case_facts["order"] = {
                k: order.get(k) for k in ("order_id", "status", "total", "placed_at")
            }
        if result.get("refunded"):
            self.case_facts["refund"] = {
                "order_id": result.get("order_id"),
                "amount": result.get("amount"),
            }

    def _case_facts_block(self) -> str:
        if not self.case_facts:
            return ""
        return (
            "\n\n## CASE FACTS (authoritative - never contradict these)\n"
            + json.dumps(self.case_facts, indent=2)
        )

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
                # Blocked: the tool never runs; the model gets a structured error.
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
                # Malformed output becomes a structured error — a bare {} would be
                # indistinguishable from a valid empty result.
                result = {
                    "isError": True,
                    "errorCategory": "transient",
                    "isRetryable": True,
                    "message": f"Tool '{name}' returned unparseable output: {text[:200]!r}",
                }

            result = self._run_post_hooks(name, result)
            self._capture_facts(name, result)

            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                    "is_error": bool(result.get("isError")),
                }
            )

        return results

    async def _escalate_exhausted(self) -> str:
        """Runaway guard hit: hand off to a human with a structured handoff, and leave
        self.messages ending on an assistant turn so a reused agent stays well-formed.
        """
        await self.client.call_tool(
            "escalate_to_human",
            {
                "customer_id": self.verified_customer_id or "unknown",
                "root_cause": "unresolved_after_max_steps",
                "recommended_action": (
                    "Agent could not resolve within the step limit; "
                    "review the conversation and resolve manually."
                ),
            },
        )
        msg = (
            "I'm escalating this to a human who will follow up — "
            "I couldn't resolve it automatically."
        )
        self.messages.append({"role": "assistant", "content": msg})
        return msg

    async def run(self, user_text: str, max_steps: int = 8) -> str:
        self.messages.append({"role": "user", "content": user_text})
        tools = await self._tool_schemas()

        for _ in range(max_steps):  # runaway guard, NOT the stop condition
            response = self.claude.chat(
                messages=self.messages,
                # Case facts ride along on every call so IDs/amounts survive long chats.
                system=SYSTEM + self._case_facts_block(),
                tools=tools,
                temperature=0,  # consistent tool routing / escalation decisions
            )
            self.messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "tool_use":  # the real driver
                tool_results = await self._run_tools(response)
                self.messages.append({"role": "user", "content": tool_results})
                continue

            # stop_reason == "end_turn" (or any non-tool stop) -> we're done
            return self.claude.text_from_message(response)
        return await self._escalate_exhausted()
