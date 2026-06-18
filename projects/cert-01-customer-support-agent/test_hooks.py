import asyncio

from core.agent import SupportAgent, hook_latch_verification

a = SupportAgent(claude=None, client=None)
a.verified_customer_id = "C001"  # pretend already verified

# refund within limit → allowed (no decision)
assert a._run_pre_hooks("process_refund", {"order_id": "12345", "amount": 50}) is None

# refund over $500 → redirected to escalate_to_human, NOT executed
d = a._run_pre_hooks("process_refund", {"order_id": "67890", "amount": 600})
assert d and d["redirect"][0] == "escalate_to_human", d

# gate still fires when unverified
b = SupportAgent(claude=None, client=None)
assert "block" in b._run_pre_hooks(
    "process_refund", {"order_id": "12345", "amount": 50}
)
print("PRE-HOOK TESTS OK")

unix = a._run_post_hooks(
    "lookup_order",
    {
        "order": {"order_id": "12345", "status": 2, "placed_at": 1717200000},
        "found": True,
    },
)
iso = a._run_post_hooks(
    "lookup_order",
    {
        "order": {
            "order_id": "67890",
            "status": 4,
            "placed_at": "2026-05-30T10:00:00Z",
        },
        "found": True,
    },
)

# both now carry an ISO-8601 string date and a human status label — ONE shape
assert unix["order"]["status"] == "shipped" and "T" in unix["order"]["placed_at"]
assert iso["order"]["status"] == "delivered" and iso["order"]["placed_at"].endswith(
    "+00:00"
)
print("POST-HOOK TESTS OK")

# --- verification latch: single match verifies, ambiguous (2 matches) does NOT ---
v = SupportAgent(claude=None, client=None)
hook_latch_verification("get_customer", {"matches": [{"id": "C001"}], "count": 1}, v)
assert v.verified_customer_id == "C001"

m = SupportAgent(claude=None, client=None)
hook_latch_verification(
    "get_customer", {"matches": [{"id": "C001"}, {"id": "C003"}], "count": 2}, m
)
assert m.verified_customer_id is None
print("LATCH TESTS OK")

a = SupportAgent(claude=None, client=None)
a._capture_facts("get_customer", {"matches": [{"id": "C001"}], "count": 1})
a._capture_facts(
    "lookup_order",
    {
        "order": {
            "order_id": "12345",
            "status": "shipped",
            "total": 49.99,
            "placed_at": "2024-06-01T00:00:00+00:00",
            "customer_id": "C001",
        },
        "found": True,
    },
)
facts = a._case_facts_block()
assert "C001" in facts and "12345" in facts and "49.99" in facts
assert "customer_id" not in a.case_facts["order"]  # verbose field trimmed out
print("CASE-FACTS TESTS OK")


# --- exhaustion path: escalates via the tool AND leaves messages reuse-safe ---
class _FakeClient:
    def __init__(self):
        self.calls = []

    async def call_tool(self, name, args):
        self.calls.append((name, args))
        return None


# verified customer → handoff carries the latched id
ex = SupportAgent(claude=None, client=_FakeClient())
ex.verified_customer_id = "C001"
ex.messages.append({"role": "user", "content": [{"type": "tool_result"}]})  # loop ended on tool_results
msg = asyncio.run(ex._escalate_exhausted())
assert ex.client.calls[0][0] == "escalate_to_human"
assert ex.client.calls[0][1]["customer_id"] == "C001"
assert ex.client.calls[0][1]["root_cause"] == "unresolved_after_max_steps"
assert ex.messages[-1]["role"] == "assistant"  # ends on assistant → reuse-safe
assert ex.messages[-1]["content"] == msg

# unverified → customer_id falls back to "unknown" (escalate_to_human requires a str)
ex2 = SupportAgent(claude=None, client=_FakeClient())
asyncio.run(ex2._escalate_exhausted())
assert ex2.client.calls[0][1]["customer_id"] == "unknown"
print("EXHAUSTION-ESCALATION TESTS OK")
