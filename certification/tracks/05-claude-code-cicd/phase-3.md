# Project 05 · Phase 3 — Review architecture ⭐

> **Companion to:** [`overview.md`](overview.md). Phases: [1](phase-1.md) · [2](phase-2.md) ·
> [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). Build it yourself; the snippets are a reference.

**Phase 3 covers build steps 5–6** (Domains **4.6** independent review, **1.6** decomposition). Even a
precise prompt (Phase 2) fails if the review is *structured* wrong. Two structural fixes: review with an
**independent instance**, and split large PRs into **per-file + integration** passes.

**Milestone:** the review runs in a fresh instance (not the generator), and a 14-file PR is reviewed
per-file then reconciled with a cross-file integration pass.

**Phase 3 Definition of done**
- [ ] Review runs in an independent instance, not the generator session.
- [ ] Large PR uses per-file + integration passes.

---

## 0. Mental model — independence and attention

```
  who reviews?                     how much at once?
  ───────────                      ────────────────
  generator reviews itself  → blind   14 files in one pass → attention dilution
  fresh instance reviews    → catches  per-file + integration → consistent
```

Two independent failure modes: a model that **wrote** the code can't objectively critique it, and a
single pass over **too many files** spreads attention thin and produces inconsistent results.

---

## 1. Step 5 — Independent review instance (Domain 4.6) ⭐

Review with a **fresh Claude instance**, not the session that generated the code. A generator retains
its own reasoning and rationalizations — it won't question the assumptions it just made.

- **Extended thinking is NOT a substitute** for independence — more thinking in the *same* context
  still carries the generator's blind spots.
- "Ask the model to review its own work" is the trap: it tends to confirm, not challenge.

Practically: the CI review job is a **separate `claude -p` invocation** with no shared session/history
with whatever produced the code — a clean context that sees only the diff + review criteria.

## 2. Step 6 — Multi-pass review for large PRs (Domain 1.6 / 4.6) ⭐

A 14-file PR reviewed in **one pass** yields inconsistent/contradictory findings — **attention
dilution**. Fix the *structure*, not the model:

1. **Per-file local passes** — review each file in its own focused pass (full attention per file).
2. **A separate cross-file integration pass** — one pass that looks only at how the pieces fit
   (interfaces, shared state, call-site mismatches) — issues no single-file pass can see.

```
  file1 ─► review ─┐
  file2 ─► review ─┤→  per-file findings ─┐
  …               │                       ├─► integration pass ─► combined report
  file14 ─► review ┘                      ┘   (cross-file consistency only)
```

> **Exam point (Q12 → A):** the fix is **per-file + integration passes**. The distractors are wrong:
> - **a bigger context window** doesn't fix attention *quality* — more tokens, same dilution;
> - **forcing devs to split the PR** pushes the tool's problem onto people;
> - **2-of-3 voting** suppresses real *intermittent* findings (a true bug only one pass caught gets
>   voted out).

---

## 3. Run & observe

- **Independence:** run the review as a fresh `claude -p` with only the diff + criteria; confirm it has
  no generator history. Compare against a self-review and note what the independent pass catches.
- **Dilution:** review a 14-file PR single-pass twice and observe inconsistent/contradictory findings.
  Then run per-file + integration and confirm the results are stable and the cross-file pass surfaces
  interface/consistency issues the single pass missed.

**Scaffold:** in `projects/cert-05-claude-code-cicd/`, `review.sh` already runs as its own `claude -p`
(independent of whatever wrote the code). To scale it, loop `review.sh` per file and add a final
cross-file pass.

---

## 4. Exam mapping

- **Independent review** (EXAM-PREP §4.8): a second independent instance beats self-review; extended
  thinking ≠ independence.
- **Attention dilution → split passes** (§4.7, Q12 → A): per-file + cross-file integration; a larger
  context window does not fix attention quality; not split-the-PR, not 2-of-3 voting.

## 5. Close out the phase

- [ ] Tick the two Phase 3 boxes in [`overview.md`](overview.md).
- [ ] Notes one-liner: *"Review in a fresh instance (generator can't self-critique; thinking ≠
  independence); large PR → per-file + cross-file integration passes (Q12), not bigger context / split
  PR / 2-of-3 voting."*
- [ ] Commit; run `/log`.

### What Phase 4 will add (preview)
Wire it into the real pipeline: CLAUDE.md as CI project context, re-run hygiene (only new/unaddressed
issues), and choosing sync vs the Message Batches API per workload.
