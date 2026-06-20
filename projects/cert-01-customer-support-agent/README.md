# Multi-Tool Customer Support Resolution Agent

Implements [Prep Exercise 1](../../certification/tracks/prep-exercise-01-multi-tool-agent.md) and
the full phased build from
[certification/tracks/01-customer-support-agent/overview.md](../../certification/tracks/01-customer-support-agent/overview.md).

## Running

```bash
cp .env.example .env          # add your ANTHROPIC_API_KEY and CLAUDE_MODEL
uv run main.py
```

## Tests (no API key needed)

```bash
uv run test_hooks.py          # unit-tests all hooks and case-facts logic
uv run mcp_client.py          # integration-tests the MCP server tool contracts
```

## Project structure

| File | Role |
|------|------|
| `mcp_server.py` | Four MCP tools: `get_customer`, `lookup_order`, `process_refund`, `escalate_to_human` |
| `mock_backend.py` | Fake CRM/OMS — no network, no DB |
| `core/agent.py` | Agentic loop, all hooks, case-facts, system prompt |
| `core/claude.py` | Thin Anthropic SDK wrapper |
| `mcp_client.py` | MCP stdio client + integration tests |
| `test_hooks.py` | Hook and case-facts unit tests |

---

## Phase walkthrough

### Phase 1 — Runnable agent
Two deliberately similar tools (`get_customer` vs `lookup_order`) are disambiguated purely through
description: `get_customer` keys on *who* (email / phone / customer ID); `lookup_order` keys on
*order number*. The agentic loop in `agent.py:SupportAgent.run()` drives entirely on `stop_reason`:
it continues while `stop_reason == "tool_use"` and exits on `end_turn` — no NL-parsing, no
iteration-cap as primary stop.

### Phase 2 — Reliability core
Every tool returns the structured error envelope `{isError, errorCategory, isRetryable, message}`
on failure. The `hook_verify_gate` pre-hook programmatically blocks `lookup_order` and
`process_refund` until `get_customer` has returned exactly one match and latched a
`verified_customer_id`. A prompt instruction saying "verify first" can still be ignored by the
model; the gate cannot.

### Phase 3 — Hooks
`hook_refund_cap` (pre-hook) intercepts any `process_refund` call over $500 and redirects it to
`escalate_to_human` — the model never executes the original call. `hook_normalize_order`
(post-hook) rewrites Unix timestamps and integer status codes into ISO-8601 dates and human labels
before the model reads the result, so the model always sees one consistent shape regardless of
which order is fetched.

### Phase 4 — Judgment and context
The system prompt defines escalation triggers with few-shot examples: explicit human request,
policy gap/silence, inability to progress — and explicitly rules out frustration, complexity, and
self-confidence as triggers. A `case_facts` dict is injected into every prompt turn so that
progressive context summarization cannot lose order totals, IDs, or dates. On escalation,
`escalate_to_human` receives a self-contained handoff (customer ID, root cause, recommended
action, amount) because the human agent cannot see the conversation.

---

## Phase 5 — Exam answers

### 1. Why is a prerequisite gate better than a strongly-worded system prompt for identity verification?

A system prompt is a suggestion to the model; a sufficiently confident or multi-step conversation
can cause the model to skip or reorder steps, especially under instruction pressure. A
programmatic gate — checking `verified_customer_id is None` before allowing `lookup_order` or
`process_refund` to execute — runs in Python, not inside the model's inference. It cannot be
talked around, overridden by a user message, or forgotten in a long context. The gate makes the
invariant unconditional; the prompt makes it probabilistic.

### 2. Why are sentiment and self-reported confidence bad escalation signals?

Sentiment tells you how the customer *feels*, not whether the tools can resolve the issue.
A furious customer with a straightforward returnable item should be resolved, not escalated —
handing them off would be worse service. Self-confidence is equally unreliable: the model's
uncertainty is not the same as an actual resolution gap. A model that says "I'm not sure" may
still have all the tools it needs to resolve the case. Both signals consistently produce
over-escalation, removing cases from automated resolution that the agent could have handled.
The correct signal is *operational*: are there tools available that can move the case forward,
or not?

### 3. What's the difference between an access failure and a valid empty result, and why does it matter?

An access failure means the system could not attempt the operation — a timeout, a permissions
error, a service being unreachable. It is retryable (transient) or needs a different path
(permission). A valid empty result means the operation succeeded and the answer is "nothing
found" — e.g. `lookup_order` returning `{found: false}` for an order that doesn't exist. If the
agent treats an empty result as an error it will retry unnecessarily or misreport the situation.
If it treats an access failure as "no results" it will give the customer incorrect information
and stop trying. The distinction is encoded in the error envelope: `isError: true` with an error
category vs a success envelope with `found: false`.

### 4. When would you choose a hook over prompt-based enforcement?

Use a hook when the rule must *never* fail: financial thresholds, identity gates, data
normalization that downstream tools depend on, any policy where a single slip has real-world
consequences (money moved, data exposed). Hooks run deterministically in code; the model cannot
skip, forget, or be argued out of them. Use prompt-based guidance when the rule is about
*judgment* — how to phrase something, which tone to take, when to ask a clarifying question —
where some flexibility is acceptable and the cost of a rare deviation is low. The general
principle: deterministic enforcement in code, soft guidance in prompts.
