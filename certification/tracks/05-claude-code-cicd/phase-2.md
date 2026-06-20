# Project 05 · Phase 2 — Review quality (precision) ⭐

> **Companion to:** [`overview.md`](overview.md). Phases: [1](phase-1.md) · [2](phase-2.md) ·
> [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). Build it yourself; the snippets are a reference.

**Phase 2 covers build steps 3–4** (Domains **4.1** explicit criteria, **4.2** few-shot). Phase 1 made
the output *structured*; this phase makes it *trustworthy* — actionable findings with **few false
positives**.

**Milestone:** the review prompt uses categorical criteria + per-severity examples + few-shot, and any
noisy category is quarantined rather than left to poison trust in the rest.

**Phase 2 Definition of done**
- [ ] Review prompt uses explicit categorical criteria + per-severity examples.
- [ ] Few-shot examples demonstrate format and acceptable-vs-issue distinctions.

---

## 0. Mental model — false positives poison trust

A schema-valid finding can still be *wrong*. If a category fires noisy false positives, developers stop
reading **all** the comments — including the accurate ones. Precision isn't a vibe you can request
("be conservative"); it comes from **specific, checkable criteria** plus **examples** that show the
boundary between an acceptable pattern and a real bug.

```
  "be conservative / only high-confidence"   → vague → model can't operationalize → noisy
  "flag X only when <concrete condition>"     → checkable → precise
  + few-shot showing acceptable vs genuine    → model generalizes the boundary
```

---

## 1. Step 3 — Explicit review criteria to cut false positives (Domain 4.1) ⭐

Replace vague confidence asks with **specific categorical criteria**:

- **Report:** real bugs, security issues. **Skip:** minor style, locally-consistent patterns.
- Make each rule a *checkable condition*: *"Flag a comment only when the claimed behavior
  **contradicts** the code"* — not the vague *"check that comments are accurate."*
- Define each **severity with a concrete code example**, so "high" vs "low" isn't guesswork.
- **General instructions like "be conservative" / "only high-confidence" do NOT improve precision** —
  the model has no concrete bar to apply.
- If one category is noisy, **temporarily disable it** while you fix its prompt. High false positives
  in a single category poison trust in the accurate ones — quarantine beats leaving it on.

> The `detected_pattern` field from Phase 1 is what makes this measurable: group findings by pattern to
> see *which* rule is generating the noise, then fix or disable just that rule.

## 2. Step 4 — Few-shot for consistent, actionable output (Domain 4.2)

Add **2–4 few-shot examples** that:
1. show the **exact output format** (so the model matches your schema and tone), and
2. **distinguish an acceptable pattern from a genuine issue**, so the model **generalizes** the rule
   rather than only catching the literal cases you listed.

```text
Example — acceptable (do NOT flag):
  Code: `# fast path for the common case` above an early return that IS the common case.
  → consistent comment; no finding.

Example — genuine issue (DO flag, severity: high):
  Code: `# returns a copy` above `return self._items` (returns the live list).
  → finding: comment contradicts behavior; suggest returning `list(self._items)`.
```

Showing *why* one is acceptable and the other isn't teaches the boundary — far more effective than a
longer list of "don't flag" rules.

---

## 3. Run & observe

- **Measure precision:** run the review on a PR with known issues; count true vs false positives.
  Vague-prompt baseline vs categorical-criteria-plus-few-shot should show fewer false positives.
- **Find the noisy rule:** group findings by `detected_pattern`; the category with the worst
  false-positive rate is the one to fix or temporarily disable.
- **Generalization check:** introduce a *new* variant of an issue not in your examples and confirm the
  model still flags it (few-shot generalized) rather than missing it.

**Scaffold:** the criteria live in `projects/cert-05-claude-code-cicd/CLAUDE.md`; the two seeded bugs in
`app/calculator.py` map to the `detected_pattern` values (`unhandled-edge-case`,
`comment-contradicts-code`) you'd group findings by.

---

## 4. Exam mapping

- **Explicit criteria** (EXAM-PREP §4.1): specific categorical criteria beat vague "be conservative";
  define severity with concrete examples; temporarily disable a high-false-positive category to
  preserve trust.
- **Few-shot** (§4.2): the most effective technique when detailed instructions still vary — show format
  *and* acceptable-vs-genuine so the model generalizes.
- Structured output fixes syntax, **not** semantic correctness — that's what this phase is for.

## 5. Close out the phase

- [ ] Tick the two Phase 2 boxes in [`overview.md`](overview.md).
- [ ] Notes one-liner: *"Cut false positives with specific categorical criteria + per-severity examples
  + few-shot (acceptable vs genuine); 'be conservative' doesn't work; quarantine a noisy category so it
  doesn't poison trust."*
- [ ] Commit; run `/log`.

### What Phase 3 will add (preview)
Even a precise prompt fails if the review is structured wrong: review in an **independent instance**
(not the code's generator), and split a large PR into **per-file + cross-file integration** passes to
beat attention dilution.
