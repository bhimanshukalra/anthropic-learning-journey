# Project 05 · Phase 4 — CI integration & cost

> **Companion to:** [`overview.md`](overview.md). Phases: [1](phase-1.md) · [2](phase-2.md) ·
> [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). Build it yourself; the snippets are a reference.

**Phase 4 covers build steps 7–9** (Domains **3.6** project context, **4.5** batch). The mechanics
(Phase 1), precision (Phase 2), and architecture (Phase 3) are in place — now wire it into the real
pipeline: project context, clean re-runs, and the right API per workload.

**Milestone:** CLAUDE.md drives test/review standards, re-runs report only new/unaddressed issues, and
blocking checks run sync while the overnight report runs as a batch.

**Phase 4 Definition of done**
- [ ] CLAUDE.md supplies test/fixture/review standards; existing tests passed in.
- [ ] Re-runs report only new/unaddressed issues.
- [ ] Blocking check is sync; overnight report is batch.

---

## 0. Mental model

```
  CLAUDE.md   →  the standards CI-Claude reviews/generates against (always loaded)
  prior findings → fed back so re-runs don't repeat themselves
  latency need  →  blocking pre-merge = SYNC ;  overnight report = BATCH
```

---

## 1. Step 7 — CLAUDE.md as CI project context (Domain 3.6)

CI-invoked Claude has no tribal knowledge — give it the project's standards via **CLAUDE.md** so its
reviews and generated tests match your conventions:

- **testing standards** (framework, structure), **fixture conventions**, **what makes a test
  valuable**, and the **review criteria** from Phase 2.
- For test generation, **pass the existing test files in context** so Claude doesn't duplicate
  scenarios already covered.

Because it's committed at project scope, every CI run picks it up automatically — the same hierarchy
rule as Project 02.

## 2. Step 8 — Re-run hygiene (Domain 3.6)

When CI re-reviews after new commits, a naive re-run re-posts the same comments. Fix it: include the
**prior findings** in context and instruct Claude to report only **new or still-unaddressed** issues.

```bash
claude -p "Review the new commits. Here are findings already reported: $(cat prior_findings.json).
Report ONLY new issues or previously-reported issues that are still unaddressed." \
  --output-format json --json-schema ./schema.json
```

This keeps the PR thread clean across pushes instead of accumulating duplicate comments.

## 3. Step 9 — Sync vs batch for CI (Domain 4.5)

Match the API to the latency requirement:

| Workload | API | Why |
|---|---|---|
| **Blocking pre-merge check** | **Synchronous** | a human/PR is waiting; needs a result now |
| **Overnight tech-debt report** | **Message Batches API** | 50% cheaper, ≤24h, no latency SLA |

> **Exam point (Q11 → A):** don't switch a **blocking** workflow to batch — Batches has no latency SLA
> (up to 24h), so a pre-merge gate would stall. Batch is for the overnight/non-blocking report.

---

## 4. Run & observe

- **CLAUDE.md:** add a distinctive convention (e.g. "tests use the `make_user()` fixture") and confirm
  generated tests follow it; confirm existing tests in context aren't duplicated.
- **Re-run:** review, push a commit fixing one issue, re-review with prior findings passed in — confirm
  the fixed issue isn't re-reported and only genuinely new/unaddressed ones appear.
- **Sync vs batch:** confirm the pre-merge job is synchronous (blocks the PR), and the scheduled
  tech-debt job submits to Batches and polls for completion.

**Scaffold:** `projects/cert-05-claude-code-cicd/CLAUDE.md` is the CI context; `ci/claude-review.yml`
shows the `synchronize` trigger (the re-run-hygiene hook) and notes that the blocking job is sync while
the overnight report is a separate Batches job.

---

## 5. Exam mapping

- **CLAUDE.md as CI context** (EXAM-PREP §3.6): supplies test/fixture/review standards; pass existing
  tests so generation doesn't duplicate coverage. A fresh instance reviews better than the session that
  wrote the code (ties to Phase 3).
- **Re-run hygiene** (§3.6): pass prior findings; report only new/unaddressed.
- **Batch vs sync** (§4.5 / §4.9, Q11 → A): Batches = 50% off, ≤24h, no SLA → overnight only; sync for
  blocking pre-merge.

## 6. Close out the phase

- [ ] Tick the three Phase 4 boxes in [`overview.md`](overview.md).
- [ ] Notes one-liner: *"CLAUDE.md = CI standards (+ pass existing tests); re-runs pass prior findings →
  only new/unaddressed; blocking=sync, overnight report=Batches (Q11)."*
- [ ] Commit; run `/log`.

### What Phase 5 will add
No more building. Answer the four **"Be able to answer"** questions in your own words — the exam payload
for this scenario.
