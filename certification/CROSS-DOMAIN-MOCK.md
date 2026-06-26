# Cross-Domain Mock Exam — Examiner Prompt

> **How to use:** open a **fresh chat** in this repo and paste the "Examiner instructions"
> block below (or just say *"Run the cross-domain mock in `certification/CROSS-DOMAIN-MOCK.md`"*).
> The examiner generates **unseen** questions, so don't read past the instructions if you want a
> clean run. Take it **timed and closed-book** for a real signal.

---

## Candidate status (for calibration)

- Preparing for the **Claude Certified Architect (Foundations)** exam. Pass mark **720/1000 (~72%)**.
- **Phase 1 theory complete:** all of `NOTES-TOPICS.md` §1–§6 ticked, every domain practice exam
  passed (D1 10/10, D2 7/7, D3 9/9; D4 & D5 all batches passed).
- This mock is a **cross-domain retention check** — pitch questions at **real exam difficulty**
  (scenario-based judgement, not recall), not an intro quiz.
- Reference material in this repo: `NOTES-TOPICS.md` (topics), `EXAM-PREP.md` (§4 heuristics,
  §3 scenarios, §7 out-of-scope).

---

## Examiner instructions (paste into the fresh chat)

You are the examiner for a cross-domain mock for the Claude Certified Architect (Foundations) exam.
Follow this exactly:

**1. Generate 20 fresh scenario MCQs**, distributed by exam weight:

| Domain | Weight | Questions |
|--------|--------|-----------|
| 1 — Agentic Architecture & Orchestration | 27% | 5 |
| 2 — Tool Design & MCP Integration | 18% | 4 |
| 3 — Claude Code Config & Workflows | 20% | 4 |
| 4 — Prompt Engineering & Structured Output | 20% | 4 |
| 5 — Context Management & Reliability | 15% | 3 |

**2. Question quality:**
- Each is a **production scenario**, one correct answer + three **plausible** distractors.
- **Randomise the correct-answer position** — distribute A/B/C/D roughly evenly; never cluster on one
  letter, never make the position predictable.
- Build distractors from real failure modes (the `EXAM-PREP.md` §4 distractor smell-test): over-
  engineering (train a classifier / routing layer), prompt-where-determinism-is-needed, bigger-
  model/context for a *structure* problem, self-reported confidence or sentiment, generic/suppressed
  errors, "valid but disproportionate" first steps, and `EXAM-PREP.md` §7 out-of-scope "fixes".
- Mix the three exam scenarios: Customer Support Agent, Multi-Agent Research, Developer Productivity /
  Claude Code CI. **Do not label** each question with its domain (the exam doesn't telegraph it).
- British English throughout.

**3. Administer:**
- Present **all 20 questions at once**. Tell the candidate to answer closed-book, ideally timed
  (~30 min), as a single batch (e.g. "1C, 2A, …"), and to add distractor reasoning where they can.
- **Do not reveal any answers** until the candidate submits all 20.

**4. Score and remediate:**
- Score out of 20. **Readiness bar: ≥16/20 (80%)** — comfortably above the 72% pass mark.
- For **every** question: give the correct letter, **why each distractor is wrong**, and the
  **heuristic** that decides it (cite the `EXAM-PREP.md` §4 number).
- Tag each question with its domain, then report a **per-domain breakdown** (e.g. "D1 5/5, D4 2/4").
- Identify the **weakest domain(s)** and any recurring distractor type the candidate fell for.
- Offer a short **targeted re-drill** (3–5 questions) on the weakest area.

**5. Log the result** (so progress is tracked):
- Append the score + weak domains to the candidate's notes, and suggest updating the
  `STUDY-PLAN.md` Day-52 self-made-mock line / Week-7 checkpoint "Mock score".

---

## After the mock

- **≥16/20:** theory is exam-solid. Pivot to **projects** (build cert-02 & cert-03; finish 05 & 06)
  and then the **official Anthropic practice exam** under timed conditions (`STUDY-PLAN.md` Day 54).
- **<16/20:** remediate the weak domain against `NOTES-TOPICS.md` §X, then re-take a fresh mock.
- Either way: do a formal pass over **`EXAM-PREP.md` §4** (the named heuristics) and re-derive the
  **12 official sample questions** with full distractor analysis — the highest-leverage drill left.
