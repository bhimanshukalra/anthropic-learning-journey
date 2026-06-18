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
