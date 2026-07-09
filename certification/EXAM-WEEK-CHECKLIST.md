# 🎯 Exam-Week Checklist — Saturday 11 July 2026

> **This file supersedes `STUDY-PLAN.md` for exam week.** The 60-day plan targeted Aug 14;
> the exam is now **Saturday 11 July**. This is your only source of truth from now until
> then — work the boxes top-to-bottom each day and you're covered.
>
> **The strategy in one line:** your theory is proven (mocks 19/20 and 20/20 on 27 Jun;
> **official practice exam 969/1000 on 1 Jul**) — so these 3 days are NOT for learning new
> material. They are for (1) closing the one standing gap (EXAM-PREP §4 heuristics + the 12
> sample questions), (2) re-proving retention with a **fresh timed mock**, and (3) arriving rested.

---

## Where you stand (verified 8 Jul)

| Area | Status |
|------|--------|
| Theory — all 119 topics, NOTES §1–§6 | ✅ Complete, every domain verification-tested |
| **Official practice exam (Skilljar, 1 Jul)** | ✅ **969/1000 — 58/60 (96.7%)**, pass = 720. Per scenario: Customer Support 14/15 · Multi-Agent Research 15/15 · Code Gen with Claude Code 15/15 · Claude Code CI 14/15. Proof: `practice-exam-2026-07-01-969.png` |
| Cross-domain mocks | ✅ 19/20 and 20/20 (27 Jun) — but 11 days ago → needs a fresh retention check |
| EXAM-PREP §4 heuristics formal pass | ❌ **The standing gap since Day 1 — do first** |
| 12 official sample questions re-derived | ❌ Not done |
| Projects | cert-01, cert-04 ✅ · cert-05, cert-06 partial · cert-02, cert-03 not started |

## Deliberate calls for this compressed window

1. **Do NOT build cert-02 / cert-03 (or finish 05/06).** The exam is scenario MCQs, not a
   practical. Instead, read those prep-exercise guides and answer their "Be able to answer"
   questions cold — that captures ~90% of the exam value in ~10% of the time.
2. **Do NOT study anything in EXAM-PREP §7 (out-of-scope).** Zero points there.
3. **One fresh mock is mandatory** (Thursday). A second only if you score <16/20.
4. **Friday after ~6pm and Saturday morning: no new material.** Taper beats cramming.

---

## ✅ Day 1 — Wednesday 8 July (today, ~3h)

**Theme: close the standing gap — heuristics + first half of sample questions.**

- [ ] **Formal pass of `EXAM-PREP.md` §4** (Answer-Selection Heuristics). Read all 12 slowly,
      twice. For each: say aloud *when it applies* and *which distractor pattern it kills*.
- [ ] Close the file. **Write all 12 heuristics from memory** (one line each). Re-open, patch gaps.
- [ ] Read §4's **distractor smell-test** + **§7 out-of-scope list** — recite both from memory.
- [ ] **Re-derive sample questions Q1–Q6** from the exam guide PDF: for each, write
      (a) the answer, (b) *why each of the 3 distractors is wrong*, (c) the §4 heuristic it tests.
      Check against the pattern log in `EXAM-PREP.md` §9. No peeking first.
- [ ] Skim `EXAM-PREP.md` §6 (Fact Cheatsheet) once before bed — just exposure, recall comes tomorrow.

🌙 **Evening log:** _Heuristics I couldn't reproduce: ____ · Sample Qs missed: _____

---

## ✅ Day 2 — Thursday 9 July (~3–4h)

**Theme: finish sample questions, then the fresh timed mock — your readiness signal.**

- [ ] **Warm-up (15m):** recite the 12 heuristics + distractor smell-test from memory.
- [ ] **Re-derive Q7–Q12** (answer + distractor analysis + heuristic), same drill as yesterday.
      You should now be able to do **all 12 cold** — if any wobble, redo it immediately.
- [ ] **📝 FRESH CROSS-DOMAIN MOCK** — open a *new chat*, run `certification/CROSS-DOMAIN-MOCK.md`.
      **Timed (~30–40 min), closed-book, all 20 as one batch.** Readiness bar: **≥16/20**.
      _Option: have the examiner draw the questions from `community-practice-exam-77q.md`
      (77 third-party Qs, mapped to the official task statements) instead of generating its
      own — genuinely unseen questions beat self-generated ones. **Don't read that file
      yourself first** (answers are inline)._
- [ ] **Remediate every miss same-day:** for each, write why the right answer wins, why you fell
      for the distractor, and which heuristic decides it. Re-test the concept phrased differently.
- [ ] **Unbuilt-project coverage (reading, not building):**
  - [ ] Read `tracks/prep-exercise-02-claude-code-team-workflow.md` → answer its
        "Be able to answer" questions cold (Scenario 2: Code Gen with Claude Code — D3).
  - [ ] Read `tracks/prep-exercise-03-structured-data-extraction.md` +
        `tracks/03-structured-data-extraction.md` → same drill (Scenario 6 — D4/D5).
- [ ] Start a **Weak List** at the bottom of this file: every miss from today goes on it.

🌙 **Evening log:** _Mock score: __/20 · Per-domain: ____ · Weak List items: _____

---

## ✅ Day 3 — Friday 10 July (~2–3h, then STOP)

**Theme: remediate, drill scenarios, recite, taper. No new material after ~6pm.**

- [ ] **Warm-up (15m):** re-test every Weak List item from yesterday until each feels ≥4/5.
- [ ] **Second mock — ONLY if Thursday was <16/20** (fresh chat, same examiner prompt, focus
      on the weak domain). If ≥16/20, skip — more mocks now add fatigue, not points.
- [ ] **Scenario drill (45m):** for each of the 6 scenarios in `EXAM-PREP.md` §3, write from
      memory: its primary domains + 2 plausible failure modes + the *most effective* fix for each.
      (The exam draws 4 of these 6 — this primes the exact contexts you'll see.)
- [ ] **Final recall pass (45m):** closed-book, reproduce on paper:
  - [ ] All 12 §4 heuristics
  - [ ] §6 Fact Cheatsheet (loop/stop_reason, Task + allowedTools, parallel = multiple Task
        calls in ONE turn, tool_choice trio, hooks, MCP scoping + `${ENV_VAR}`, CLAUDE.md
        hierarchy, SKILL.md frontmatter, `-p`/`--output-format json`/`--json-schema`,
        batch API constraints, built-in tools)
  - [ ] §7 out-of-scope list (so you can smell those distractors)
- [ ] **Go/No-Go gate** (below) — tick it honestly.
- [ ] **Logistics:** confirm booking time · ID ready · proctoring system check (webcam, browser,
      bandwidth) · quiet room arranged · phone/notes out of reach plan · alarm set.
- [ ] **Evening: fully off.** Good meal, no screens late, full night's sleep. Seriously.

🌙 **Evening log:** _Go/No-Go: ___ · Feeling: _____

---

## 🎯 Day 4 — Saturday 11 July — EXAM DAY

- [ ] **15-min warm-up only:** skim `EXAM-PREP.md` §4. Nothing else. No cramming.
- [ ] Arrive/log in early; bathroom, water, calm.

**In-exam technique (60 Q / 120 min ≈ 2 min each):**
1. Read the scenario → **name the heuristic** the question is testing.
2. **Eliminate 2 distractors fast** (smell-test: over-engineered ML/routing layer, prompt-where-
   determinism-needed, bigger-context-for-structure-problem, self-confidence/sentiment,
   generic/suppressed errors, §7 out-of-scope "fix", valid-but-disproportionate first step).
3. Between the last 2, pick the **most effective / proportionate / root-cause** answer.
4. The platform **forces an answer** — never agonise. Guess, move on. Momentum > perfection.
5. Pace check at Q20 (~40 min) and Q40 (~80 min).

🌙 **Result:** ____ 🎉

---

## ✅ Go/No-Go gate (tick Friday evening)

- [x] **Official practice exam ≥ ~80%** — ✅ done 1 Jul: **969/1000, 58/60 (96.7%)**.
- [ ] Can reproduce all 12 sample questions cold (answer + why each distractor fails + heuristic).
- [ ] Can recite all 12 §4 heuristics and the §6 cheatsheet from memory.
- [ ] Fresh mock (9 Jul) ≥ 16/20, all misses remediated.
- [ ] "Be able to answer" questions for scenarios 2 & 6 (the unbuilt projects) answered cold.
- [ ] Weak List empty (every item re-tested).
- [ ] Rested, not crammed.

**If ≥6 of 7 are green, sit the exam — three independent signals ≥95% (two mocks + the official
practice exam) put you far past the 72% bar.** Rebooking should only enter the picture if the
fresh mock collapses (<14/20) — very unlikely given the 1 Jul result.

---

## 📌 Additional todos (added 8 Jul)

> ⚠️ **Scheduling honesty:** these do NOT fit inside the 3-day core plan above without
> sacrificing the taper. Work them **only after the day's core boxes are done**, in the order
> below (highest exam-relevance first). Anything unfinished by Friday 6pm rolls to after the
> exam — do not trade sleep or the mock for these.

### A. Create/review each project from the exam guide

Full coverage audit against the official guide (v0.2): all **6 exam scenarios**, all **4
Preparation Exercises**, and all **7 Exam Preparation Recommendations**.

**The 6 exam scenarios (exam draws 4 at random):**
S1 Customer Support Resolution Agent · S2 Code Generation with Claude Code · S3 Multi-Agent
Research System · S4 Developer Productivity with Claude · S5 Claude Code for Continuous
Integration · S6 Structured Data Extraction.

**Preparation Exercises (the guide defines 4 — they cover only scenarios S1/S2/S3/S6):**

- [ ] **Exercise 1 — Multi-Tool Agent with Escalation Logic** · trains **S1**
      (`projects/cert-01-customer-support-agent` · ✅ built → **review**): re-open the code;
      trace the `stop_reason` loop, the structured errors (`errorCategory`/`isRetryable`),
      the >$500 interception hook, and the prerequisite gate. Answer
      `tracks/prep-exercise-01-multi-tool-agent.md` "Be able to answer" Qs cold.
- [ ] **Exercise 2 — Claude Code for a Team Dev Workflow** · trains **S2**
      (`projects/cert-02-*` · ❌ not started → **create**; config-only, ~60–90 min, no API key):
      project CLAUDE.md; `.claude/rules/` with `paths:` globs (verify a rule loads only on
      matching files); a skill with `context: fork` + `allowed-tools`; `.mcp.json` with
      `${ENV_VAR}` expansion + one user-scope server; try plan mode vs direct on 3 task sizes.
- [ ] **Exercise 3 — Structured Data Extraction Pipeline** · trains **S6**
      (`projects/cert-03-*` · ❌ not started → **create**; ~2h, needs API key): extraction tool
      schema (required/optional/nullable, enum+"other"); verify null-not-fabricated;
      validation-retry loop with error feedback; few-shot for varied layouts; batch strategy +
      `custom_id` resubmission; field-level confidence routing.
- [ ] **Exercise 4 — Multi-Agent Research Pipeline** · trains **S3**
      (`projects/cert-04-multi-agent-research` · ✅ built → **review**): trace coordinator
      `allowedTools: ["Task"]`, explicit context passing, parallel Task calls in one turn,
      structured error propagation, claim→source provenance. Answer
      `tracks/prep-exercise-04-multi-agent-research.md` self-quiz cold.
- [ ] **Scenarios S4 & S5 have NO official exercise** — the repo extras are their only hands-on
      coverage: finish `cert-05` → **S5** (CI/CD: `-p`, `--output-format json`, `--json-schema`)
      and `cert-06` → **S4** (built-in tools, MCP resources, sessions). Minimum bar if time runs
      out: answer both projects' "Be able to answer" Qs cold (S5 also hit 14/15 on the practice
      exam — one of your two misses).

**Exam Preparation Recommendations cross-check (guide appendix — 7 items):**

- [x] 1. Build an agent with the Agent SDK (loop, tools, errors, sessions, subagents + context
      passing) — ✅ cert-01 + cert-04 built and verified.
- [ ] 2. Configure Claude Code for a real project (CLAUDE.md hierarchy, `.claude/rules/`,
      skills frontmatter, MCP server) — ⏳ closes when **Exercise 2 / cert-02** is done. (This
      repo's own `.claude/commands/` + skills setup already covers part of it.)
- [x] 3. Design and test MCP tools (differentiated descriptions, structured errors, retryable
      flags, selection reliability) — ✅ cert-01 tools + Domain 2 verification-tested.
- [ ] 4. Build a structured data extraction pipeline (tool_use schemas, validation-retry,
      nullable fields, Batch API) — ⏳ closes when **Exercise 3 / cert-03** is done.
- [x] 5. Practice prompt engineering (few-shot for ambiguity, explicit criteria vs false
      positives, multi-pass review) — ✅ Domain 4 theory verified; cert-05 partial adds hands-on.
- [x] 6. Study context management patterns (structured facts from verbose output, scratchpads,
      subagent delegation) — ✅ Domain 5 theory verified; practiced in cert-04.
- [x] 7. Review escalation & human-in-the-loop patterns (valid triggers, confidence-based
      routing) — ✅ cert-01 escalation build + Domain 5 theory verified.

### B. Go through all the courses again

> Realistic form before Saturday: **skim your notes/projects per course, not full re-watches**
> (a full re-run of 7–8 courses is a 20+ hour job). Full re-watch = post-exam, as part of the
> AI-Engineer roadmap.

- [ ] Claude with the Anthropic API (Anthropic Academy)
- [ ] Introduction to Model Context Protocol (→ `projects/01-introduction-to-model-context-protocol`)
- [ ] Model Context Protocol: Advanced Topics (→ `projects/02-model-context-protocol-advanced-topic`)
- [ ] Claude Code in Action
- [ ] _Fill in the remaining courses you completed: ________________________________________

---

## 📋 Weak List (living — add every miss, strike when re-tested ≥4/5)

- [ ] Practice-exam miss #1 (1 Jul): **Customer Support Resolution Agent** scenario, 14/15 —
      recall the question if you can; likely D1/D2/D5 (escalation, gates, or tool errors).
- [ ] Practice-exam miss #2 (1 Jul): **Claude Code for Continuous Integration** scenario,
      14/15 — likely D3/D4 (`-p`, output schemas, review criteria, sync-vs-batch).

---

## Exam facts (memorise)

60 questions · 120 minutes · single best answer (1 correct + 3 distractors) · scaled 100–1,000,
**pass = 720 (~72%)** · answer forced per question, no penalty for guessing · 4 scenarios drawn
from a pool of 6 · online proctored or test centre · guide v0.2 (30 Jun 2026) — no content changes
from what you studied.
