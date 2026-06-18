# Project 04 · Phase 3 — Tools & error propagation ⭐

> **Companion to:** [`overview.md`](overview.md). Phases: [1](phase-1.md) · [2](phase-2.md) ·
> [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). Build it yourself; the snippets are a reference.

**Phase 3 covers build steps 4–5** (Domains **2.3** tool distribution, **2.2/5.3** structured errors).
Two exam-signature ideas: least-privilege tooling (Q9) and structured, recoverable failures (Q8).

**Milestone:** synthesis fact-checks with a scoped tool; a search timeout returns structured context
and the coordinator proceeds with partial results + a coverage note (it does **not** die).

**Phase 3 Definition of done**
- [ ] Synthesis has a scoped `verify_fact` tool; complex cases still route via coordinator.
- [ ] Timeout returns structured error context; coordinator proceeds with partial results + coverage note.

---

## 0. Mental model

```
  TOOLS (least privilege)            ERRORS (structured, recoverable)
  synthesis ─ verify_fact (scoped)   subagent ─► {type, query, partial, alternatives, retryable}
        │ 85% simple checks                          │
        └ complex ─► coordinator ─► web   coordinator ─► retry / alternative / proceed-with-partial
```

Two principles: give each agent **only the tools its role needs** (a narrow `verify_fact`, not the full
web toolset), and make failures **structured data the coordinator can act on**, not dead ends.

---

## 1. Step 4 — Scoped cross-role tool (Domain 2.3) ⭐

The synthesis agent needs to fact-check, but handing it the **entire web toolset** is over-privileged
and degrades tool selection. Instead give it a **scoped `verify_fact` tool** that handles the ~85%
simple checks; **complex** verifications still route through the **coordinator** to the web-search
agent.

> **Exam point (Q9 → A, least privilege):** add **one scoped tool** for the high-frequency cross-role
> need. The wrong answers: hand synthesis the full web toolset, route *everything* through the
> coordinator, batch all verifications, or speculatively cache.

## 2. Step 5 — Structured error propagation (Domain 2.2 / 5.3) ⭐

Simulate a web-search **timeout**. The subagent returns **structured error context**, not a dead end:

```json
{ "isError": true,
  "failureType": "transient",
  "attemptedQuery": "AI music generation market size 2025",
  "partialResults": [ ... ],
  "suggestedAlternatives": ["narrow to 2024", "try industry-report source"],
  "isRetryable": true }
```

The coordinator then **recovers**: retry, try an alternative, or **proceed with partial results +
a coverage note**. Avoid all three anti-patterns:
- generic **"search unavailable"** (hides the context the coordinator needs),
- **empty-result-as-success** (silently suppresses the failure),
- **killing the whole workflow** on one subagent failure.

> Division of labor: subagents **recover transient failures locally**; only the **unrecoverable**
> propagates up — with partial results + what was attempted. (Exam Q8 → A.) And recall an **access
> failure ≠ a valid empty result** (Domain 2.2): "couldn't search" is retryable; "no results found"
> is a successful empty.

---

## 3. Run & observe

- **Scoped tool:** confirm synthesis resolves simple fact-checks via `verify_fact` directly, and that a
  complex/ambiguous check routes back through the coordinator to web search.
- **Timeout path:** inject the timeout and confirm the subagent returns the structured envelope (not a
  generic string, not empty-as-success), and the coordinator **continues** with partial results and
  annotates the gap — the report still ships.
- **No total failure:** verify one subagent timing out does not kill the run.

---

## 4. Exam mapping

- **Least privilege / scoped tools** (EXAM-PREP §4.5, Q9 → A): one scoped cross-role tool for a frequent
  need; not the full toolset, not everything-via-coordinator.
- **Structured errors** (§4.6 / §2.2 / §5.3, Q8 → A): failure type, attempted query, partial results,
  alternatives, `isRetryable`; recover locally, propagate only the unrecoverable; never genericize,
  suppress, or kill the workflow.

## 5. Close out the phase

- [ ] Tick the two Phase 3 boxes in [`overview.md`](overview.md).
- [ ] Notes one-liner: *"One scoped verify_fact tool (Q9, least privilege); structured error envelope
  (type/query/partial/alternatives/retryable), recover transient locally, proceed on partial — never
  genericize/suppress/kill (Q8)."*
- [ ] Commit; run `/log`.

### What Phase 4 will add (preview)
The output-quality half: **provenance** (claim→source mappings preserved through synthesis, conflicts
annotated with dates, established-vs-contested structure) and **context discipline** across handoffs
(structured key facts, not verbose reasoning; key summaries at the start).
