# Project 04 · Phase 2 — Decomposition quality ⭐

> **Companion to:** [`overview.md`](overview.md). Phases: [1](phase-1.md) · [2](phase-2.md) ·
> [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). Build it yourself; the snippets are a reference.

**Phase 2 covers build step 3** (Domain **1.2** — decomposition). This is one of the exam's signature
root-cause questions (Q7), so it gets its own phase.

**Milestone:** you reproduce the narrow-decomposition failure, then fix it — the coordinator partitions
the topic broadly and refines until coverage is sufficient.

**Phase 2 Definition of done**
- [ ] Narrow-decomposition failure reproduced, then fixed with broad partition + refinement loop.

---

## 0. Mental model — the failure is upstream of the subagents

```
  "impact of AI on creative industries"
        │
        ▼  coordinator decomposes  ──►  only "visual arts"   ← TOO NARROW (the bug)
        │                               (music, writing, film, games … never assigned)
        ▼
  search/analysis/synthesis  ──►  each does its job PERFECTLY on the narrow slice
        │
        ▼
  report looks complete but MISSES whole sub-topics
```

The trap: every subagent "succeeded," so it's tempting to blame search or synthesis. But they only
worked on what they were *given*. **The root cause is the coordinator's decomposition** — it never
assigned the missing sub-domains. Fix the component that's actually wrong, not a downstream one that's
working correctly.

---

## 1. Step 3 — Reproduce, then fix (Domain 1.2) ⭐

**Reproduce.** Run a broad topic ("impact of AI on creative industries") and watch the coordinator
over-narrow. Confirm the subagents did fine on their slice — the gap is unassigned scope.

**Fix — two parts:**
1. **Broad scope partition.** Have the coordinator enumerate the sub-domains *first* and assign each to
   a subagent, partitioning to **cover all of them** while minimizing overlap (music, writing, film,
   visual arts, games, …).
2. **Iterative refinement loop.** Synthesis evaluates its own output for **coverage gaps** → coordinator
   **re-delegates targeted queries** for the missing areas → re-synthesize. Repeat until coverage is
   sufficient.

```
  decompose broadly ─► run subagents ─► synthesize
                            ▲                 │
                            └── re-delegate ◄─┘  while synthesis reports gaps
```

> Don't "fix" this by making the search agent search harder or the synthesis agent infer the missing
> areas — that's patching a working component. The decomposition is the lever.

---

## 2. Run & observe

- **Before:** log the coordinator's sub-topic list for the broad query; note which sub-domains are
  missing. Confirm the report omits them despite green subagents.
- **After:** confirm the coordinator's partition now spans all sub-domains, and that the refinement loop
  fires when synthesis flags a gap (re-delegation → fuller coverage on the next pass).
- **Coverage annotation:** synthesis should explicitly report which areas are well-covered vs thin
  (feeds Phase 4).

---

## 3. Exam mapping

- **Root cause, not symptom** (EXAM-PREP §4.2, Q7 → B): reports miss sub-topics though subagents
  succeeded ⇒ blame the **coordinator's decomposition**, not search/synthesis.
- **Iterative refinement** (§1.2): evaluate synthesis for gaps → re-delegate targeted queries →
  re-synthesize.
- **Partition scope** to avoid duplication *and* gaps.

## 4. Close out the phase

- [ ] Tick the Phase 2 box in [`overview.md`](overview.md).
- [ ] Notes one-liner: *"Reports miss sub-topics but subagents succeeded → root cause is coordinator
  decomposition (Q7); fix = broad scope partition + synthesis-flags-gaps refinement loop."*
- [ ] Commit; run `/log`.

### What Phase 3 will add (preview)
Tool design + reliability: a **scoped `verify_fact` tool** for the synthesis agent (least privilege,
Q9), and **structured error propagation** when a search times out (Q8) — distinguishing local recovery
from what must propagate to the coordinator.
