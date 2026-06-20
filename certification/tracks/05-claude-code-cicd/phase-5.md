# Project 05 · Phase 5 — Write up the answers ⭐

> **Companion to:** [`overview.md`](overview.md). Phases: [1](phase-1.md) · [2](phase-2.md) ·
> [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). **No config in this phase.**

This is the **exam payload** for Scenario 5 — which blends two 20% domains (Claude Code config + prompt
engineering), so it's high-ROI. Everything you built was so you can answer these four cold.

**Phase 5 Definition of done**
- [ ] All four questions answered **in your own words** and added to your notes.

> **How to use this file:** write your own answer first, then read the reference and check the gap.

---

## Q1. The CI job hangs — what's the fix and why are the alternatives wrong?

**Reference answer.** Run Claude Code with **`-p` / `--print`**. That puts it in non-interactive mode:
it processes the prompt, prints the result to stdout, and **exits** instead of waiting for input —
which is what a CI runner (no human, no TTY) requires. Why the distractors fail:
- **`CLAUDE_HEADLESS=1`** — not a real environment variable; does nothing.
- **`--batch`** — not the flag; also conflates with the Message Batches API, which is unrelated.
- **`< /dev/null`** — closing stdin doesn't switch the CLI into print mode; it still runs interactively
  and stalls.

*Heuristic:* EXAM-PREP §3.6 / Cheatsheet, Q10 → `-p`/`--print`.

---

## Q2. Why do vague "be conservative" instructions fail to reduce false positives?

**Reference answer.** Because "be conservative" gives the model **no concrete bar to apply** — it can't
operationalize a vague confidence ask, so its precision doesn't actually improve. What works is
**specific categorical criteria** (what to report vs skip, each rule stated as a checkable condition
like *"flag a comment only when its claimed behavior contradicts the code"*), **severity defined with
concrete code examples**, and **few-shot examples** that show the boundary between an acceptable pattern
and a genuine issue so the model generalizes. And precision matters disproportionately: a single noisy
category produces false positives that **poison trust in the accurate findings**, so quarantine
(temporarily disable) a bad category while you fix its prompt.

*Heuristic:* EXAM-PREP §4.1 (explicit criteria) + §4.2 (few-shot).

---

## Q3. Why is an independent review instance better than telling the generator to review itself?

**Reference answer.** The instance that **generated** the code retains its own reasoning and
assumptions — it won't question the very choices it just made, so self-review tends to **confirm rather
than challenge**. A **fresh, independent instance** sees only the diff and the criteria, with none of
the generator's rationalizations, so it catches what the author is blind to. Crucially, **extended
thinking is not a substitute for independence** — more reasoning inside the *same* context still carries
the same blind spots. In CI this means the review is a separate `claude -p` invocation with no shared
session/history with whatever produced the code.

*Heuristic:* EXAM-PREP §4.8 (independent review > self-review; thinking ≠ independence).

---

## Q4. A 14-file review is contradictory — what restructuring fixes it and why not just a bigger model?

**Reference answer.** The contradictions are **attention dilution** — one pass spread across 14 files
gives each too little focus, so results are inconsistent. The fix is **structural**: **per-file local
passes** (full attention on each file) **plus a separate cross-file integration pass** that only checks
how the pieces fit (interfaces, shared state, call-site mismatches). Why the alternatives are wrong:
- **A bigger context window / bigger model** doesn't fix attention *quality* — same dilution, more
  tokens.
- **Forcing devs to split the PR** offloads the tool's problem onto people.
- **2-of-3 voting** suppresses real *intermittent* findings — a true bug only one pass caught gets
  voted out.

*Heuristic:* EXAM-PREP §4.7 (attention dilution → split passes), Q12 → A.

---

## Close out the project

- [ ] Write your own version of all four answers and paste them into your notes — *your wording*.
- [ ] Tick the Phase 5 box and the remaining boxes in [`overview.md`](overview.md).
- [ ] Commit and run `/log`.

> **Scenario 5 spans Domains 3 and 4 (40% of the exam combined).** When you can answer all four from
> memory — and say why each wrong option is wrong — this high-ROI scenario's points are banked.
