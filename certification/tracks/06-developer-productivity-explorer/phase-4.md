# Project 06 · Phase 4 — Sessions & iterative refinement ⭐

> **Companion to:** [`overview.md`](overview.md). Phases: [1](phase-1.md) · [2](phase-2.md) ·
> [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). Build it yourself; the snippets are a reference.

**Phase 4 covers build steps 5–6** (Domains **1.7** sessions, **3.5** iterative refinement). Phase 3
kept one long session alive; this phase is about **continuing and branching** investigations across
sessions, and **refining** deliberately.

**Milestone:** you resume a named session, fork to explore two approaches, pick resume-vs-fresh
correctly, and use the interview pattern before implementing in an unfamiliar area.

**Phase 4 Definition of done**
- [ ] `--resume` and `fork_session` used correctly; you can pick resume vs fresh.
- [ ] Interview pattern used before implementing in an unfamiliar area.

---

## 0. Mental model — continue, branch, or restart?

```
  continue the same investigation later   → --resume <name>
  branch from a baseline into 2 approaches → fork_session
  prior context mostly valid               → resume
  prior tool results STALE                 → start fresh + inject a structured summary
```

---

## 1. Step 5 — Session management (Domain 1.7) ⭐

- **`--resume <session-name>`** — continue a **named** investigation across work sessions (pick up
  tomorrow where you left off).
- **`fork_session`** — **branch from a shared baseline** to explore two approaches independently (e.g.
  two refactors, or two testing strategies) without them contaminating each other.
- **Resume vs fresh:**
  - **Resume** when prior context is **mostly valid**.
  - **Start fresh with an injected structured summary** when prior tool results are **stale** (the code
    changed enough that old reads are wrong).
  - When resuming, **tell the session exactly which files changed** so it does targeted re-analysis
    instead of full re-exploration.

> `--resume` = *same line of work, later*. `fork_session` = *one baseline → many parallel lines of work*.

## 2. Step 6 — Iterative refinement (Domain 3.5)

- **Interview pattern:** in an unfamiliar area, have Claude **ask clarifying questions first** (cache
  invalidation, failure modes, edge cases) *before* implementing — cheaper than guessing wrong.
- **Concrete input/output examples** beat prose when a requirement is ambiguous.
- Fix **interacting** issues **in one message** (they affect each other); fix **independent** issues
  **sequentially**.

---

## 3. Run & observe

- **Resume:** name a session, stop, `--resume <name>` later, and confirm it continues with prior
  context; tell it which files changed and watch it re-analyze just those.
- **Fork:** `fork_session` from a baseline analysis and take two approaches in parallel; confirm they're
  independent.
- **Resume-vs-fresh:** after a big code change, notice stale tool results and choose fresh-with-summary
  instead of resume.
- **Interview:** ask for a change in an unfamiliar module and confirm Claude asks the right clarifying
  questions before coding.

---

## 4. Exam mapping

- **Sessions** (EXAM-PREP §1.7): `--resume <name>` to continue; `fork_session` to branch from a baseline
  for divergent approaches; resume when prior context is valid, start fresh with a structured summary
  when tool results are stale; tell a resumed session which files changed.
- **Iterative refinement** (§3.5): interview pattern; concrete examples beat prose; interacting issues
  in one message, independent ones sequentially.

## 5. Close out the phase

- [ ] Tick the two Phase 4 boxes in [`overview.md`](overview.md).
- [ ] Notes one-liner: *"`--resume` = continue named session; `fork_session` = branch a baseline into
  parallel approaches; resume if context valid, fresh+summary if stale; interview pattern before
  implementing in unfamiliar code."*
- [ ] Commit; run `/log`.

### What Phase 5 will add
No more building. Answer the five **"Be able to answer"** questions in your own words — the exam payload
for this scenario.
