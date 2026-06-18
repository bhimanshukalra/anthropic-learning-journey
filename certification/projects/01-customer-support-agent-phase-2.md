# Project 01 · Phase 2 — Implementation Guide: *Reliability core* ⭐

> **Companion to:** [`01-customer-support-agent.md`](01-customer-support-agent.md) (overview) and
> [`01-customer-support-agent-phase-1.md`](01-customer-support-agent-phase-1.md) (the runnable agent
> you already built). This file is the in-depth walkthrough for **Phase 2 only** — build it yourself;
> the snippets are a reference to compare against.

**Phase 2 covers build steps 3–4** (Domains 2.2 + 1.4). This is the **single highest-tested material
in the whole project** — the exam loves structured errors and deterministic enforcement.

**Milestone:** a refund attempted *before* identity is verified is **blocked in code** (not by the
prompt), and a `process_refund` on an expired-window order returns a **business error the agent
explains rather than retries**.

**Phase 2 Definition of done**
- [ ] Each error category produces the right agent behavior (retry vs explain).
- [ ] Refund is impossible without a verified `get_customer` ID — enforced in code, not prompt.

What Phase 2 deliberately leaves out (don't build these yet): the $500 interception hook and the
`PostToolUse` date/status normalization (Phase 3), and escalation *calibration* + the case-facts
block (Phase 4). In particular, **don't try to fix the mixed `placed_at` formats here** — that's
Phase 3's job. Phase 2 is errors + the gate, nothing more.

---

## 0. Mental model — two changes to the loop

Phase 1's `_run_tools` did one thing: call the tool, send the result back. Phase 2 adds a step
**before** the call and enriches the step **after** it:

```
        ┌──────────────────────────────────────────────────────────┐
        │  for each tool_use block the model emitted:                │
        │                                                            │
        │   ① GATE  ──► is this a gated tool with no verified ID?    │
        │              yes → return a permission error, SKIP call    │   ← step 4 (the ⭐)
        │              no  → continue                                │
        │                                                            │
        │   ② CALL  ──► run the tool                                 │
        │                                                            │
        │   ③ AFTER ──► if get_customer returned exactly 1 match,    │
        │              latch the verified customer ID                │   ← step 4
        │              tool may also return an isError envelope      │   ← step 3
        └──────────────────────────────────────────────────────────┘
```

Two ideas, and they're different in *where* they live:

- **Structured errors (step 3)** live in the **tools** (server-side). A tool can return a normal
  result *or* an error envelope; the model reads the envelope and decides retry-vs-explain.
- **The gate (step 4)** lives in the **agent harness** (`_run_tools`), in *code*. It runs before the
  tool, and no prompt can talk the model past it. This is the exam's whole point (Q1).

---

## 1. Step 3 — Structured error responses (Domain 2.2)

### 1a. The envelope
Every tool error returns the same shape so the agent can reason about it uniformly:

```json
{ "isError": true,
  "errorCategory": "transient | validation | business | permission",
  "isRetryable": true,
  "message": "human-readable explanation" }
```

The **two fields that drive behavior** are `errorCategory` and `isRetryable`:

| Category | `isRetryable` | What the agent should do |
|----------|---------------|--------------------------|
| `transient` (timeout, service down) | `true` | **Retry** the same call |
| `validation` (bad input) | `false` | Fix the input or ask the user |
| `business` (policy, e.g. refund window expired) | `false` | **Explain** to the customer; do *not* retry |
| `permission` (not allowed yet — e.g. unverified) | `false` | Satisfy the prerequisite first |

### 1b. A shared helper in `mock_backend.py`
```python
def err(category: str, retryable: bool, message: str) -> dict:
    return {"isError": True, "errorCategory": category, "isRetryable": retryable, "message": message}
```

### 1c. Make the tools return errors (`mcp_server.py`)

**`process_refund` → business error when the window has closed.** First add a flag to the seed data
so you don't need date math yet (date parsing is Phase 3):

```python
# mock_backend.py — add to each ORDERS entry:
#   "12345": {... , "refund_window_open": True},    # recent
#   "67890": {... , "refund_window_open": False},   # delivered long ago
```

```python
# mcp_server.py
@mcp.tool()
def process_refund(order_id: str, amount: float) -> dict:
    """Issue a refund against an order. Fails (business) if the refund window has closed."""
    order = db.get_order(order_id)
    if order is None:
        return db.err("validation", False, f"No order '{order_id}' exists to refund.")
    if not order["refund_window_open"]:
        return db.err("business", False,
                      f"The refund window has expired for order {order['order_id']}; "
                      f"it can no longer be refunded automatically.")
    return {"refunded": True, "order_id": order["order_id"], "amount": amount}
```

**`lookup_order` → distinguish an access failure from a valid empty result.** This is the subtle
Domain-2.2 idea: *"no such order"* is a **success** (`found: false`), but *"couldn't reach the order
service"* is a **retryable error**. Same tool, two very different signals:

```python
@mcp.tool()
def lookup_order(order_id: str) -> dict:
    """... (Phase 1 docstring unchanged) ..."""
    if order_id.strip().upper() == "TIMEOUT":          # simulate the backend being unreachable
        return db.err("transient", True, "Order service timed out — safe to retry.")
    order = db.get_order(order_id)
    return {"order": order, "found": order is not None}  # found:false is a VALID empty result, NOT an error
```

> **The trap the exam tests:** if you treated a valid empty result (`found: false`) as an error, the
> agent would uselessly retry a lookup for an order that simply doesn't exist. Empty ≠ error.

> **Note on FastMCP:** returning these dicts is a *soft error* — the tool succeeds at the protocol
> level and the envelope rides in the result content. That's deliberate: the model reads the JSON and
> decides what to do. (Raising an exception would set MCP's protocol-level `isError`; the soft-error
> envelope is simpler and gives the model the `errorCategory`/`isRetryable` fields to reason with.)

---

## 2. Step 4 — Deterministic prerequisite gate ⭐ (Domain 1.4)

**The single most-tested idea in this project (exam Q1):** block `lookup_order` and `process_refund`
until `get_customer` has returned a **verified** customer ID — and enforce it **in code**, not in the
system prompt.

> Why not just write *"verification is mandatory"* in `SYSTEM`? Because a prompt instruction is a
> *strong suggestion* the model follows *most* of the time — and "most of the time" is exactly what
> fails a compliance check. A code gate is a hard invariant: it cannot be talked past, prompt-injected
> around, or skipped on an off day. Prove it to yourself: even with the instruction in the prompt, the
> model will occasionally jump straight to a refund. The gate makes that impossible.

### 2a. Add state + the gate to `SupportAgent` (`core/agent.py`)

```python
import json

GATED_TOOLS = {"lookup_order", "process_refund"}   # require a verified customer first

class SupportAgent:
    def __init__(self, claude, client):
        self.claude = claude
        self.client = client
        self.messages: list = []
        self.verified_customer_id: str | None = None     # ← latched once, in code

    def _gate(self, tool_name: str) -> dict | None:
        """Return an error envelope if this call must be blocked, else None. Pure + testable."""
        if tool_name in GATED_TOOLS and self.verified_customer_id is None:
            return {
                "isError": True, "errorCategory": "permission", "isRetryable": False,
                "message": ("Identity not verified. Call get_customer and confirm a SINGLE "
                            "matching customer before looking up orders or issuing refunds."),
            }
        return None

    def _latch_verification(self, tool_name: str, result_text: str) -> None:
        """After get_customer, latch the id ONLY when exactly one customer matched."""
        if tool_name != "get_customer":
            return
        data = json.loads(result_text)
        if data.get("count") == 1:                       # ambiguous (0 or >1) does NOT verify
            self.verified_customer_id = data["matches"][0]["id"]
```

### 2b. Wire it into `_run_tools`

```python
    async def _run_tools(self, response) -> list[dict]:
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            print(f"tool_use: {block.name}({json.dumps(block.input)})")

            blocked = self._gate(block.name)                          # ① GATE — before the call
            if blocked is not None:
                print(f"  ⛔ gated: {block.name} (no verified customer)")
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": json.dumps(blocked), "is_error": True})
                continue                                              # SKIP the tool entirely

            output = await self.client.call_tool(block.name, block.input)   # ② CALL
            text = output.content[0].text if output and output.content else "{}"

            self._latch_verification(block.name, text)                # ③ AFTER — maybe verify
            results.append({"type": "tool_result", "tool_use_id": block.id,
                            "content": text, "is_error": self._is_error_envelope(text)})
        return results

    @staticmethod
    def _is_error_envelope(text: str) -> bool:
        """True if a tool returned the isError envelope (so the API marks the result as an error)."""
        try:
            return bool(json.loads(text).get("isError"))
        except (ValueError, AttributeError):
            return False
```

Three things to notice:
- The gate **short-circuits with `continue`** — the gated tool is never called. That's the deterministic guarantee.
- `_latch_verification` only verifies on **`count == 1`**. This wires Phase 1's multi-match case (`555-0100` → 2 matches) straight into the gate: an *ambiguous* lookup does **not** unlock refunds. Nice and strict.
- We now set `is_error` on the tool_result (Phase 1 omitted it). That tells the model the result is an error, reinforcing the `errorCategory` it reads in the content.

---

## 3. Make the loop react correctly (and not spin forever)

The model decides retry-vs-explain by **reading `isRetryable`** in the envelope — you don't code that
branch, the model does. But a `transient` (`isRetryable: true`) error means the model may call the
same tool again, and a flaky tool could loop forever. Add a **runaway guard** to `run()` — a safety
net, *not* the primary terminator (the terminator is still `stop_reason`, per Phase 1):

```python
    async def run(self, user_text: str, max_steps: int = 8) -> str:
        self.messages.append({"role": "user", "content": user_text})
        tools = await self._tool_schemas()

        for _ in range(max_steps):                       # runaway guard, NOT the stop condition
            response = self.claude.chat(messages=self.messages, system=SYSTEM, tools=tools)
            self.messages.append({"role": "assistant", "content": response.content})
            if response.stop_reason == "tool_use":       # ← still the real driver
                self.messages.append({"role": "user", "content": await self._run_tools(response)})
                continue
            return self.claude.text_from_message(response)
        return "Stopped after too many steps — please rephrase or contact support."
```

> Keep `stop_reason` as the thing that *normally* ends the loop. `max_steps` only catches a runaway
> (e.g. the model retrying a `transient` error that never clears). Making the cap the primary stop is
> the Phase 1 anti-pattern — this is the allowed exception: a high safety ceiling.

---

## 4. Run & observe — most of this needs **no API credits**

The headline of Phase 2 is that the gate and the error envelopes are **deterministic code**, so you
can verify them exactly like your Phase 1 smoke test — no model, no credits.

### 4a. Gate test (pure, no server, no model)
```python
# test_gate.py — run with: uv run python test_gate.py
from core.agent import SupportAgent
a = SupportAgent(claude=None, client=None)           # we only exercise pure methods

assert a._gate("process_refund") is not None         # blocked before verification
assert a._gate("lookup_order") is not None            # blocked
assert a._gate("get_customer") is None                # never gated

a._latch_verification("get_customer", '{"matches":[{"id":"C001"}],"count":1}')
assert a.verified_customer_id == "C001"               # single match verifies
assert a._gate("process_refund") is None              # now allowed

b = SupportAgent(claude=None, client=None)
b._latch_verification("get_customer", '{"matches":[{"id":"C001"},{"id":"C003"}],"count":2}')
assert b.verified_customer_id is None                 # 2 matches → still NOT verified
assert b._gate("process_refund") is not None          # still blocked
print("GATE TESTS OK")
```

### 4b. Tool-error test (server + client, like Phase 1 — still no model)
Reuse your Phase 1 smoke-test harness and assert the envelopes:
```python
r = await c.call_tool("process_refund", {"order_id": "67890", "amount": 10})
#   → {"isError": true, "errorCategory": "business", "isRetryable": false, ...}
r = await c.call_tool("lookup_order", {"order_id": "TIMEOUT"})
#   → {"isError": true, "errorCategory": "transient", "isRetryable": true, ...}
r = await c.call_tool("lookup_order", {"order_id": "99999"})
#   → {"order": null, "found": false}    ← VALID empty, NOT an error envelope
```

### 4c. Model-level behavior (when you have auth/credits — the deferred Phase 1 check too)
With `uv run main.py`:
- `"refund order 12345 for $20"` *(no prior verification)* → gate blocks it; the agent, seeing the
  `permission` error, calls `get_customer` first, then proceeds. **It cannot refund first even though
  nothing in the prompt forbids it.**
- `"refund order 67890"` (after verifying) → `business` error → agent **explains** the window expired,
  does **not** retry.
- A `TIMEOUT` lookup → `transient` → agent **retries**.

---

## 5. Close out the phase

- [ ] Tick the two Phase 2 boxes in [`01-customer-support-agent.md`](01-customer-support-agent.md).
- [ ] Notes one-liner: *"Gate > prompt for hard prerequisites (Q1); empty result ≠ access error;
  isRetryable drives retry-vs-explain."*
- [ ] Commit (this repo commits straight to `main`):
  ```bash
  git add projects/cert-01-customer-support-agent certification/projects/01-customer-support-agent.md
  git commit -m "Project 01 Phase 2: structured errors + deterministic verification gate"
  ```
- [ ] Run `/log`.

### What Phase 3 will add (preview)
You'll **generalize the gate into hooks**: a `PreToolUse`-style hook that blocks `process_refund`
over **$500** and redirects to `escalate_to_human`, plus a `PostToolUse` hook that **normalizes** the
mixed `placed_at` formats (Unix `1717200000` vs ISO `2026-05-30T10:00:00Z`) and the numeric `status`
codes into one shape *before the model reads them*. The gate you built here is the first, hard-coded
version of that interception pattern — Phase 3 makes it a reusable mechanism.
```
