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

**`main.py`** — the entry point. Loads `.env`, launches the MCP server as a subprocess
(`async with MCPClient` handles startup and cleanup), wires the Claude wrapper and the MCP client
into a `SupportAgent`, then runs a terminal chat loop where each line you type becomes one
`agent.run()` call.

**`core/agent.py`** — the heart of the project. `SupportAgent.run()` drives the agentic loop purely
on `stop_reason` (`tool_use` → execute tools and continue; `end_turn` → reply; `max_steps` is only a
runaway guard that ends in a structured human handoff). Wraps every tool call in hooks: pre-hooks
enforce the identity gate (block) and the $500 refund cap (redirect to escalation); post-hooks latch
the verified customer and normalize dates/status codes before the model sees them. Also owns the
system prompt (policies, escalation triggers, few-shot) and the `case_facts` block re-injected into
every API call so IDs and amounts survive long conversations.

**`core/claude.py`** — a thin Anthropic SDK wrapper. `chat()` assembles the `messages.create()`
params (model, system, tools, temperature, optional extended thinking) and returns the raw
`Message`; `text_from_message()` joins the text blocks of a response. No agent logic lives here —
it's the transport layer.

**`mcp_server.py`** — a FastMCP server exposing the four support tools: `get_customer`,
`lookup_order`, `process_refund`, `escalate_to_human`. The tool docstrings are the exam lesson:
deliberately detailed descriptions (input formats, example queries, edge cases, "use X instead"
boundaries) are what let the model route between two similar-looking lookup tools. Failures return
the structured envelope `{isError, errorCategory, isRetryable, message}`; the magic order id
`TIMEOUT` simulates a transient backend outage.

**`mock_backend.py`** — a fake CRM/OMS: three customers and two orders in plain dicts, no network,
no DB. The data is deliberately awkward — two customers share a phone number (forces the
multiple-matches disambiguation path) and the two orders use different date formats and status
encodings (gives the normalization hook something real to fix). Also provides `err()`, the shared
error-envelope builder.

**`mcp_client.py`** — the stdio MCP client: spawns the server process, holds the `ClientSession`
via an `AsyncExitStack`, and exposes `list_tools` / `call_tool` (plus prompt/resource helpers).
Run directly, its `main()` doubles as an integration test that asserts the tool error contracts
(business vs transient vs valid-empty) and the handoff shape — no model or API key involved.

**`test_hooks.py`** — unit tests for the guardrail layer. Calls the hook functions and case-facts
methods directly against a stub agent — no API, no server, no model — proving the gate blocks,
the cap redirects, the latch latches, and facts are captured, deterministically.

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
