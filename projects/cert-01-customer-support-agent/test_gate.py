from core.agent import SupportAgent

a = SupportAgent(claude=None, client=None)  # we only exercise pure methods

assert a._gate("process_refund") is not None  # blocked before verification
assert a._gate("lookup_order") is not None  # blocked
assert a._gate("get_customer") is None  # never gated

a._latch_verification("get_customer", '{"matches":[{"id":"C001"}],"count":1}')
assert a.verified_customer_id == "C001"  # single match verifies
assert a._gate("process_refund") is None  # now allowed

b = SupportAgent(claude=None, client=None)
b._latch_verification(
    "get_customer", '{"matches":[{"id":"C001"},{"id":"C003"}],"count":2}'
)
assert b.verified_customer_id is None  # 2 matches → still NOT verified
assert b._gate("process_refund") is not None  # still blocked
print("GATE TESTS OK")
