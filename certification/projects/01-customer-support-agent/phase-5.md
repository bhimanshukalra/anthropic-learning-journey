# Project 01 · Phase 5 — Write up the answers ⭐

> **Companion to:** [`overview.md`](overview.md) (overview) and the
> four build-phase guides ([1](phase-1.md) ·
> [2](phase-2.md) · [3](phase-3.md) ·
> [4](phase-4.md)). **No code in this phase.**

This is the **actual exam payload**. Everything you built was so you can answer these four questions
*cold*, in your own words, explaining the tradeoff — not reciting a definition. The exam is "what is
the **most effective** / **best first step**" judgment, and these four are the core judgments Project
01 trains.

**Phase 5 Definition of done**
- [ ] All four questions answered **in your own words** and added to your notes.

> **How to use this file:** for each question, **write your own answer first** (a few sentences,
> from memory), *then* read the reference answer below and check what you missed. The gap between your
> answer and the reference is your revision list. Don't read the reference cold — that wastes the rep.

---

## Q1. Why is a prerequisite gate better than a strongly-worded system prompt for identity verification?

**Reference answer.** Because a prompt instruction is **probabilistic** and a gate is
**deterministic**. "Verification is mandatory" in the system prompt is a *strong suggestion* the model
follows *most* of the time — but it has a non-zero failure rate, and on some turn it will jump straight
to a refund. For a rule that **must hold every time** (identity before any order/refund access), "most
of the time" is exactly what fails a compliance check. A code gate (your `hook_verify_gate` /
Phase 2 `_gate`) is a **hard invariant**: it cannot be talked past, prompt-injected around, or skipped
on an off day. It also **fails closed** (returns a `permission` error envelope, not a refund) and is
**pure + testable** — you proved in code that `count==1` verifies and `count==2` does not.

*Heuristic:* determinism vs. probability (EXAM-PREP §4.1). A business/identity/financial rule that
MUST hold → programmatic enforcement, never prompt instructions. *(This is sample Q1.)*

---

## Q2. Why are sentiment and self-reported confidence bad escalation signals?

**Reference answer.** Both measure the wrong thing.

- **Sentiment ≠ complexity.** A *furious* customer can have a trivially resolvable issue (your
  "I'm furious it's late" → normal refund → RESOLVE example), and a *calm* one can have a real policy
  gap. Frustration tells you nothing about whether a **human** is actually needed — routing on it
  over-escalates the angry-but-easy cases and under-escalates the polite-but-stuck ones.
- **Self-reported confidence is poorly calibrated.** LLMs are *already* confidently wrong on hard
  cases — precisely the cases where you'd most want to escalate. A self-scored 1–10 is least reliable
  exactly when it matters. Confidence should be calibrated against a **labeled validation set**, not
  trusted raw.

The **real** triggers are: explicit human request, policy gap/silence, and inability to progress —
none of which is "it's complex," "they sound angry," or "I feel unsure."

*Heuristic:* EXAM-PREP §4.4 / §4.10. *(Sample Q3.)*

---

## Q3. What's the difference between an access failure and a valid empty result, and why does it matter to the agent?

**Reference answer.**

- **Access failure** = the operation *couldn't complete* (e.g. the order service timed out). It's a
  **transient, retryable error** (`isError:true`, `isRetryable:true`) → the agent should **retry**.
- **Valid empty result** = the operation *succeeded* and the answer is genuinely "nothing matches"
  (order `99999` doesn't exist). It's a **success** (`found:false`), **not an error** → the agent
  should **accept it** and tell the customer / move on.

**Why it matters:** conflating them produces opposite failures. Treat a valid-empty as an error and
the agent **uselessly retries** a lookup for an order that will never exist. Treat an access-failure as
empty (silently swallow it) and the agent reports "no such order" when the backend was simply down —
a **wrong answer** the customer acts on. The distinction is what drives **retry vs. accept**, so the
same tool must signal them differently (your `lookup_order`: `TIMEOUT` → transient error,
`99999` → `found:false`).

*Heuristic:* Domain 2.2 — distinguish access failure from a valid empty result; empty ≠ error.

---

## Q4. When would you choose a hook over prompt-based enforcement?

**Reference answer.** Choose a **hook** when compliance or consistency must be **guaranteed** — a
deterministic, non-bypassable rule. Use the **prompt** for **soft preferences and judgment** that can
tolerate a non-zero failure rate.

- **Hook** (deterministic, can't be prompt-injected around):
  - **`PreToolUse`** to *intercept* a policy violation — block a refund > $500 and redirect to
    `escalate_to_human` (your `hook_refund_cap`).
  - **`PostToolUse`** to *normalize* heterogeneous tool output (Unix vs ISO dates, numeric status
    codes) **before the model reads it** (your `hook_normalize_order`).
- **Prompt** (probabilistic, judgment): *when* to escalate, tone, multi-concern decomposition — things
  with no single correct answer, where few-shot calibration is the right lever.

*Rule of thumb:* hard invariant / financial / regulatory / safety / consistency → **hook** (or gate);
probabilistic judgment → **prompt + few-shot**. If a wrong outcome is unacceptable even 1% of the
time, it belongs in a hook.

*Heuristic:* Domain 1.5 + EXAM-PREP §4.1 ("use hooks when compliance must be guaranteed").

---

## Close out the project

- [ ] Write your own version of all four answers and paste them into your notes (the file in your
  `memory/` notes, or `NOTES-TOPICS.md`) — *your wording*, not this file's.
- [ ] Tick the Phase 5 box and the remaining boxes in
  [`overview.md`](overview.md).
- [ ] (When you have credits) run the deferred **model-level** checks — Phase 2 §4c, Phase 3 §5c,
  Phase 4 §5c — to confirm the *behaviors*, not just the deterministic code.
- [ ] Commit and run `/log`.

> **Project 01 is the highest-value scenario on the exam** (Scenario 1; Domains 1, 2, 5). When you can
> produce all four answers from memory — *and* explain why each tempting wrong answer is wrong — you've
> banked the points this project was built to earn.
