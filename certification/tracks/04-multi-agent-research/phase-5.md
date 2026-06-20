# Project 04 · Phase 5 — Write up the answers ⭐

> **Companion to:** [`overview.md`](overview.md). Phases: [1](phase-1.md) · [2](phase-2.md) ·
> [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). **No code in this phase.**

This is the **exam payload** for Scenario 3. Domain 1 is the heaviest on the exam (27%) and
multi-agent orchestration is its core, so these five answers carry weight.

**Phase 5 Definition of done**
- [ ] All five questions answered **in your own words** and added to your notes.

> **How to use this file:** write your own answer first, then read the reference and check the gap.

---

## Q1. Why don't subagents inherit the coordinator's context, and what must you do about it?

**Reference answer.** Each subagent runs in an **isolated context** — a fresh instance that sees none
of the conversation, the coordinator's reasoning, or sibling subagents' outputs. (That isolation is a
feature: it keeps each agent focused and its context small.) The consequence: **everything a subagent
needs must be passed explicitly in its prompt** — e.g. the synthesis agent's prompt must contain the
web results and the doc analysis verbatim. Relying on implicit sharing is the #1 multi-agent bug.

*Heuristic:* EXAM-PREP §1.2/§1.3 — isolated context; pass everything explicitly.

---

## Q2. Reports miss whole sub-topics though every subagent "succeeded" — what's the root cause and why?

**Reference answer.** The root cause is the **coordinator's decomposition** — it over-narrowed the
topic and never *assigned* the missing sub-domains. The search/analysis/synthesis agents only worked on
the scope they were given, and they did it correctly — so blaming them (or making them "search harder")
patches a working component. Fix the decomposition: **partition scope broadly to cover all sub-domains**,
and add an **iterative refinement loop** where synthesis flags coverage gaps and the coordinator
re-delegates targeted queries until coverage is sufficient.

*Heuristic:* root cause not symptom (EXAM-PREP §4.2, Q7 → B); fix the component that's actually wrong.

---

## Q3. Why give synthesis a scoped `verify_fact` tool instead of the full web toolset?

**Reference answer.** **Least privilege.** Synthesis needs to fact-check, but handing it the entire web
toolset over-privileges it and degrades tool selection (too many tools → worse choices). A single
**scoped `verify_fact`** tool covers the ~85% of simple checks it actually needs; **complex**
verifications still route through the coordinator to the web-search agent. The wrong alternatives:
give it the full toolset, route *everything* through the coordinator (bottleneck), batch all
verifications, or speculatively cache.

*Heuristic:* EXAM-PREP §4.5 (least privilege / scoped cross-role tool), Q9 → A.

---

## Q4. What four things belong in a structured subagent error, and which three error behaviors are anti-patterns?

**Reference answer.** A structured error carries (at least): **failure type**, the **attempted query**,
any **partial results**, **suggested alternatives**, and a **retryable** flag — enough for the
coordinator to *decide* (retry / try an alternative / proceed with partial). The three anti-patterns:
1. **generic "search unavailable"** — hides the context the coordinator needs;
2. **empty-result-as-success** — silently suppresses the failure;
3. **killing the whole workflow** on one subagent's failure.
Subagents recover **transient** failures locally; only the **unrecoverable** propagates up, with
partial results + what was attempted.

*Heuristic:* EXAM-PREP §4.6 / §2.2 / §5.3, Q8 → A. (And access failure ≠ valid empty result.)

---

## Q5. How do you keep source attribution from being lost during synthesis?

**Reference answer.** Make subagent outputs **structured claim→source mappings** — `claim`, `evidence`
excerpt, `source` (URL/doc), and **publication date** — and require synthesis to **preserve** the
mapping through every merge, never flattening claims into unsourced prose. For **conflicting** credible
statistics, **annotate both with their sources** (and dates) instead of picking one; dates also prevent
a temporal difference from being misread as a contradiction. Keep summaries/citations at the **start**
of aggregated inputs so attribution isn't lost-in-the-middle.

*Heuristic:* EXAM-PREP §5.6 (provenance) + §5.1 (context preservation).

---

## Close out the project

- [ ] Write your own version of all five answers and paste them into your notes — *your wording*.
- [ ] Tick the Phase 5 box and the remaining boxes in [`overview.md`](overview.md).
- [ ] Commit and run `/log`.

> **Scenario 3 is pure Domain-1 territory (the 27% bucket) plus error propagation and provenance.** When
> you can answer all five from memory — and say why each wrong option is wrong — these points are banked.
