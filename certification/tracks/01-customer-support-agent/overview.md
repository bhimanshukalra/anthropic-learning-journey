# Project 01 — Multi-Tool Customer Support Resolution Agent

> **Maps to:** Exam Scenario 1 + official Preparation Exercise 1
> **Domains:** 1 (Agentic Architecture, 27%) · 2 (Tool Design & MCP, 18%) · 5 (Context & Reliability, 15%)
> **Why this one first:** it touches the three highest-value reliability ideas the exam loves —
> deterministic enforcement, structured errors, and escalation calibration.

## Objective
Build a customer-support agent (Claude Agent SDK) that resolves returns, billing disputes, and
account issues through MCP tools, hitting **80%+ first-contact resolution** while escalating
correctly. You are practicing the *judgment*, so build the smallest thing that lets you observe
each behavior — a mocked backend is fine.

## Tech stack
- Claude Agent SDK (Python or TS) against the latest model (`claude-opus-4-8` or `claude-sonnet-4-6`).
- A tiny local MCP server (or in-process tools) exposing mocked data. No real backend needed.

## The tools (build these four)
| Tool | Purpose | Notes |
|------|---------|-------|
| `get_customer` | Verify identity, return a customer ID | Must run **before** order/refund ops |
| `lookup_order` | Order details by order/customer ID | Similar shape to `get_customer` on purpose |
| `process_refund` | Issue a refund | Gated; blocked above a $ threshold |
| `escalate_to_human` | Hand off with a structured summary | Terminal action |

Make `get_customer` and `lookup_order` *deliberately similar* so you can practice writing
descriptions that disambiguate them (this is literally exam Q2).

## Build steps (phased)

Build one phase at a time. Each phase ends at a **milestone** you can run and observe before moving
on — that observing-as-you-go is the actual learning. Tick the phase's Definition-of-done boxes
before starting the next.

---

### Phase 1 — Runnable agent
*Steps 1–2 · Domains 2.1, 1.1 · Outcome: an agent that resolves a simple request end-to-end.*

#### 1. Write differentiating tool descriptions (Domain 2.1)
Each description must state: purpose, **input formats accepted**, 1–2 **example queries**, **edge
cases**, and **when to use this vs the similar tool**. Then deliberately test with ambiguous input
like *"check my order #12345"* and confirm it routes to `lookup_order`, not `get_customer`.
> Exam point: minimal descriptions are the root cause of misrouting. Fixing descriptions is the
> low-effort/high-leverage first step — *before* few-shot, routing layers, or tool consolidation.

#### 2. Implement the agentic loop (Domain 1.1)
- Loop **while `stop_reason == "tool_use"`**: execute the requested tool(s), **append results to
  conversation history**, send back.
- Terminate **only on `stop_reason == "end_turn"`**.
- Deliberately *avoid* the anti-patterns so you can articulate them: don't parse natural-language
  for "I'm done", don't use an iteration cap as the primary stop, don't treat assistant text as completion.

**Phase 1 milestone:** ask *"check my order #12345"*; agent routes to `lookup_order` and replies, loop terminating on `end_turn`.
- [x] Two similar tools reliably selected via descriptions alone (no routing layer).
- [x] Loop driven purely by `stop_reason`; no NL-parsing / iteration-cap / text-content stop.

---

### Phase 2 — Reliability core ⭐
*Steps 3–4 · Domains 2.2, 1.4 · The highest-tested material in this project.*

#### 3. Structured error responses (Domain 2.2)
Make tools return the MCP `isError` pattern with metadata:
```json
{ "isError": true, "errorCategory": "transient|validation|business|permission",
  "isRetryable": true, "message": "human-readable explanation" }
```
- Transient (timeout) → agent retries.
- Business (e.g. "refund window expired") → `isRetryable:false` + customer-friendly text; agent explains, doesn't retry.
- Distinguish an **access failure** (retry decision) from a **valid empty result** (success, no matches).

#### 4. Deterministic prerequisite gate (Domain 1.4) ⭐
Programmatically **block `lookup_order` and `process_refund` until `get_customer` has returned a
verified customer ID.** This is the single most-tested idea here (Q1). Prove to yourself that a
prompt instruction ("verification is mandatory") still fails sometimes, but the gate never does.

**Phase 2 milestone:** a refund attempt before verification is blocked in code; a "refund window expired" error is explained, not retried.
- [x] Each error category produces the right agent behavior (retry vs explain).
- [x] Refund is impossible without a verified `get_customer` ID — enforced in code, not prompt.

---

### Phase 3 — Hooks
*Step 5 · Domain 1.5 · Outcome: enforcement and normalization that the model can't bypass.*

#### 5. Tool-call interception hook (Domain 1.5)
Add a hook that **blocks `process_refund` over $500** and redirects to `escalate_to_human`.
Also add a `PostToolUse` hook that **normalizes** mixed date formats (Unix vs ISO 8601) and numeric
status codes from different tools into one shape before the model reads them.

**Phase 3 milestone:** a $600 refund is intercepted and escalated; tool outputs reach the model in one consistent date/status shape.
- [x] Refund > $500 is blocked and redirected by a hook.
- [x] Mixed date/status formats normalized by a `PostToolUse` hook.

---

### Phase 4 — Judgment & context
*Steps 6–7 · Domains 5.2, 1.4, 5.1 · Outcome: correct escalation calibration and durable case state.*

#### 6. Escalation calibration (Domain 5.2) ⭐
Add explicit escalation criteria **with few-shot examples** to the system prompt:
- Escalate immediately on an **explicit human request** (don't investigate first).
- Escalate on **policy gaps/silence** (e.g. competitor price-match when policy only covers own-site).
- Escalate on **inability to progress** — *not* on "complex," *not* on sentiment, *not* on self-confidence.
- On **multiple customer matches**, ask for another identifier instead of guessing.
Confirm straightforward cases (damage replacement + photo) are resolved, not escalated.

#### 7. Multi-concern decomposition + structured handoff (Domain 1.4, 5.1)
- Send a message with several issues; verify the agent splits them, handles each, synthesizes one reply.
- On escalation, compile a **structured handoff**: customer ID, root cause, refund amount,
  recommended action — because the human can't see the transcript.
- Maintain a persistent **"case facts"** block (amounts, dates, order #s, statuses) injected each
  prompt so progressive summarization can't lose the numbers. Trim verbose order lookups to relevant fields.

**Phase 4 milestone:** a multi-issue message is decomposed and synthesized into one reply; an escalation emits a structured handoff; numbers survive a long conversation.
- [x] Escalation happens on request/policy-gap/no-progress only; multi-match asks for an identifier.
- [x] Escalation produces a structured handoff summary.
- [x] "Case facts" block survives long multi-turn conversations.

---

### Phase 5 — Write up the answers
*Outcome: the actual exam payload — answer the four "Be able to answer" questions below in writing.*
- [x] All four questions answered in your own words (add to your notes).

## Be able to answer
1. Why is a prerequisite gate better than a strongly-worded system prompt for identity verification?
2. Why are sentiment and self-reported confidence bad escalation signals?
3. What's the difference between an access failure and a valid empty result, and why does it matter to the agent?
4. When would you choose a hook over prompt-based enforcement?
