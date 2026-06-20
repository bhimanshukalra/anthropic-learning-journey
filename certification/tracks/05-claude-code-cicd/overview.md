# Project 05 — Claude Code in CI/CD (Automated Review, Test Gen, PR Feedback)

> **Maps to:** Exam Scenario 5 (Claude Code for Continuous Integration)
> **Domains:** 3 (Claude Code Config & Workflows, 20%) · 4 (Prompt Engineering & Structured Output, 20%)
> **Why this is a dedicated project:** the official exercises don't drill the CI/CD scenario, yet it
> blends two 20% domains. High ROI.

## Objective
Wire Claude Code into a CI pipeline that runs automated code reviews, generates tests, and posts PR
feedback that is **actionable with few false positives** — using non-interactive mode and structured output.

> **Hands-on scaffold:** a runnable version lives at `projects/cert-05-claude-code-cicd/`. It runs
> **credit-free** — `./review.sh` falls back to `sample_findings.json` when no API key is set — so you
> can exercise the whole review path before wiring in live `claude -p` calls.

## Build steps (phased)

Build one phase at a time. Each phase ends at a **milestone** you can run and observe before moving on.
Tick the phase's Definition-of-done boxes before starting the next. Each phase has an in-depth companion
guide.

---

### Phase 1 — Headless invocation & structured output · [`phase-1.md`](phase-1.md)
*Steps 1–2 · Domains 3.6, 4.3 · Outcome: Claude Code runs in CI non-interactively and emits machine-parseable findings.*

#### 1. Non-interactive invocation (Domain 3.6) ⭐
Run Claude Code with **`-p` / `--print`** so it processes the prompt, prints to stdout, and exits
without hanging on input. (Exam Q10: the hang is fixed by `-p`, *not* a fake `CLAUDE_HEADLESS` env
var, a `--batch` flag, or `< /dev/null`.)
```bash
claude -p "Review the staged diff for security issues" --output-format json --json-schema ./schema.json
```

#### 2. Structured, machine-parseable findings (Domain 3.6 / 4.3)
Use **`--output-format json`** + **`--json-schema`** to emit findings you can post as inline PR
comments. Schema per finding: `location` (file:line), `issue`, `severity`, `suggested_fix`,
`detected_pattern`.

**Phase 1 milestone:** the CI job runs `claude -p ...` to completion (no hang) and produces schema-valid JSON that posts as inline PR comments.
- [ ] Pipeline runs Claude Code with `-p` and doesn't hang.
- [ ] JSON-schema output posts as structured inline PR comments.

---

### Phase 2 — Review quality (precision) · [`phase-2.md`](phase-2.md)
*Steps 3–4 · Domains 4.1, 4.2 · Outcome: reviews are actionable with few false positives.*

#### 3. Explicit review criteria to cut false positives (Domain 4.1) ⭐
Define **specific categorical criteria**, not vague confidence asks:
- Report: real bugs, security issues. Skip: minor style, locally-consistent patterns.
- "Flag a comment only when claimed behavior **contradicts** the code" — not "check comments are accurate."
- Define each **severity** with a concrete code example.
- General instructions like "be conservative" / "only high-confidence" **don't** improve precision.
- If a category is noisy, **temporarily disable it** to preserve trust while you fix its prompt —
  high false positives in one category poison trust in the accurate ones.

#### 4. Few-shot for consistent, actionable output (Domain 4.2)
Add 2–4 few-shot examples that (a) show the exact output format, and (b) distinguish acceptable
patterns from genuine issues so the model **generalizes** rather than matching only listed cases.

**Phase 2 milestone:** the review prompt uses categorical criteria + per-severity examples + few-shot, and noisy categories are quarantined rather than left to poison trust.
- [ ] Review prompt uses explicit categorical criteria + per-severity examples.
- [ ] Few-shot examples demonstrate format and acceptable-vs-issue distinctions.

---

### Phase 3 — Review architecture · [`phase-3.md`](phase-3.md)
*Steps 5–6 · Domains 4.6, 1.6 · Outcome: independent review and a structure that scales to large PRs.*

#### 5. Independent review instance (Domain 4.6) ⭐
Review with a **fresh Claude instance**, not the session that generated the code — a generator retains
its reasoning and won't question itself. Extended thinking / "review your own work" is **not** a
substitute for independence.

#### 6. Multi-pass review for large PRs (Domain 1.6 / 4.6) ⭐
For a 14-file PR with inconsistent/contradictory single-pass results (**attention dilution**):
**per-file local passes + a separate cross-file integration pass**. *Not* a bigger context window,
*not* forcing devs to split the PR, *not* 2-of-3 voting (which suppresses real intermittent findings).
(Exam Q12 → A.)

**Phase 3 milestone:** review runs in a fresh instance (not the generator), and a 14-file PR is reviewed per-file then reconciled with a cross-file integration pass.
- [ ] Review runs in an independent instance, not the generator session.
- [ ] Large PR uses per-file + integration passes.

---

### Phase 4 — CI integration & cost · [`phase-4.md`](phase-4.md)
*Steps 7–9 · Domains 3.6, 4.5 · Outcome: project context, clean re-runs, and the right API per workload.*

#### 7. CLAUDE.md as CI project context (Domain 3.6)
Put **testing standards, fixture conventions, valuable-test criteria, and review criteria** in
CLAUDE.md so CI-invoked Claude generates high-value tests and reviews. Provide **existing test files**
in context so test generation doesn't duplicate covered scenarios.

#### 8. Re-run hygiene (Domain 3.6)
On re-review after new commits, include **prior findings** in context and instruct Claude to report
only **new or still-unaddressed** issues — avoids duplicate PR comments.

#### 9. Sync vs batch for CI (Domain 4.5)
Blocking **pre-merge** check → **synchronous** API. Overnight **tech-debt report** → **Message Batches
API** (50% off, ≤24h, no SLA). Don't batch a blocking workflow (exam Q11 → A).

**Phase 4 milestone:** CLAUDE.md drives test/review standards, re-runs report only new/unaddressed issues, and blocking checks run sync while the overnight report runs as a batch.
- [ ] CLAUDE.md supplies test/fixture/review standards; existing tests passed in.
- [ ] Re-runs report only new/unaddressed issues.
- [ ] Blocking check is sync; overnight report is batch.

---

### Phase 5 — Write up the answers · [`phase-5.md`](phase-5.md)
*Outcome: the actual exam payload — answer the four "Be able to answer" questions in writing.*
- [ ] All four questions answered in your own words (add to your notes).

## Be able to answer
1. The CI job hangs — what's the fix and why are the alternatives wrong?
2. Why do vague "be conservative" instructions fail to reduce false positives?
3. Why is an independent review instance better than telling the generator to review itself?
4. A 14-file review is contradictory — what restructuring fixes it and why not just a bigger model?
