# 60-Day Study Plan & Daily Tracker — Claude Certified Architect (Foundations)

> **Goal:** walk into the exam able to score **≥ 720/1000** with margin — and *know* you're ready
> before you book it.
> **Window:** 60 days · **Start:** Tue 2026-06-16 · **Target exam:** ~Fri 2026-08-14
> **Pace:** ~3–4 focused hours/day, 6 days/week, **Sundays = rest**.
> **You've already done ~7–8 Anthropic courses** — this plan turns that exposure into retained,
> testable knowledge (notes), proven skill (projects), and exam stamina (timed practice).

---

## How to use this file (your daily ritual)

1. **Each morning:** open today's day block. The checklist is your to-do list for the session.
2. **Work the boxes top-to-bottom.** Every day starts with a 15-min *spaced-repetition* warm-up
   (review yesterday + one older topic) — do not skip it; this is what makes theory stick.
3. **Each night:** fill the `🌙 Evening log` line — confidence (1–5), what clicked, what to revisit.
   Be honest; the "revisit" notes drive Phase 3 remediation.
4. **End of each week:** complete the **Weekly checkpoint** and adjust if you're ahead/behind.
5. If a day slips, **don't cascade** — use a rest day or the built-in buffer days to catch up.

**Confidence scale:** 1 = lost · 2 = shaky · 3 = can follow with notes · 4 = can explain unaided ·
5 = can teach it + recite the tradeoff. **You want mostly 4–5 before Phase 4.**

---

## Improved preparation strategy (what actually moves the score)

The PDF's prep recommendations are a good start; here's the sharpened version this plan is built on:

1. **Notes before projects, projects before practice.** Theory first gives projects meaning;
   projects make theory concrete; practice exposes gaps. We interleave all three with review.
2. **Active recall > re-reading.** After writing a note, close it and say the tradeoff out loud or
   on paper. Re-reading feels productive but doesn't transfer to a timed MCQ.
3. **Spaced repetition.** Every topic gets revisited at least 3× across the 60 days (next day, ~1
   week later, in Phase 3). The daily 15-min warm-up is the engine.
4. **Master the answer-selection heuristics** (`EXAM-PREP.md` §4). The exam is *tradeoff judgment*,
   not recall. If you can name the heuristic a question tests, the right answer falls out and the
   distractors collapse.
5. **Build for observation, not polish.** In projects, the win is *seeing the behavior* (the gate
   blocks the refund; the narrow decomposition misses topics). Mock backends are fine. Don't gold-plate.
6. **Re-derive every sample question from first principles.** For all 12: state the answer **and why
   each of the 3 distractors is wrong.** That single skill basically *is* the exam.
7. **Track weak areas explicitly.** Your nightly "revisit" notes + practice misses become a living
   weak-list you grind down in Phase 3–4.
8. **Simulate the real thing.** At least one full **timed** practice exam under exam conditions
   (no notes, no breaks) before booking — then remediate misses.
9. **Respect out-of-scope** (`EXAM-PREP.md` §7). Don't burn hours on fine-tuning, OAuth, embeddings,
   vision, tokenization. If an option leans on those, it's usually a distractor.
10. **Go/No-Go gate.** Don't sit the exam until you clear the readiness checklist at the end of this file.

---

## Phase overview

| Phase | Days | Calendar | Theme | Deliverable |
|-------|------|----------|-------|-------------|
| 0 — Orientation | 1 | Jun 16 | Map the terrain | Plan understood, env ready |
| 1 — Theory notes | 2–21 | Jun 17 – Jul 6 | Write notes for all domains + glossary | `NOTES-TOPICS.md` fully ticked |
| 2 — Hands-on projects | 22–44 | Jul 7 – Jul 29 | Build all 6 projects | 6 projects "definition of done" met |
| 3 — Integration & practice | 45–54 | Jul 30 – Aug 8 | Sample Qs, scenario drills, weak-area grind, mock | ≥80% on mock |
| 4 — Final readiness | 56–60 | Aug 10 – Aug 14 | Practice exam, remediate, taper | Pass the Go/No-Go gate → exam |

Rest days (Sundays): Jun 21, 28 · Jul 5, 12, 19, 26 · Aug 2, 9.

---

## Weekly checkpoints (fill at end of each week)

- [x] **Week 1 (Jun 16–21):** Oriented; Domain 1 notes drafted (all 24 §1 topics, MCQ-tested ≥4). Weakest topic: narrow-decomposition blame-attribution (root cause = coordinator, not synthesis). _Outstanding: EXAM-PREP §4 heuristics not yet read; API key pending._
- [ ] **Week 2 (Jun 22–28):** Domains 2–3 notes done. Weakest: ____
- [ ] **Week 3 (Jun 29–Jul 5):** Domains 4–5 notes done. Weakest: ____
- [ ] **Week 4 (Jul 6–12):** Glossary + consolidation done; Projects 1–2 underway. Weakest: ____
- [ ] **Week 5 (Jul 13–19):** Projects 3–4 done. Weakest: ____
- [ ] **Week 6 (Jul 20–26):** Projects 5–6 done. Weakest: ____
- [ ] **Week 7 (Jul 27–Aug 2):** All projects done; sample-Q deep dive done. Mock score: ____
- [ ] **Week 8 (Aug 3–9):** Weak areas remediated; practice exam taken. Score: ____
- [ ] **Week 9 (Aug 10–14):** Go/No-Go passed → exam booked/sat. Result: ____

---

# The 60-Day Tracker

> Tip: each `🌙 Evening log` is yours to fill in at night. Keep it to one line.

## Week 1 — Orientation + Domain 1 (Agentic Architecture, 27%) 🔴

#### Day 1 · Tue Jun 16 — Phase 0: Orientation
**Focus:** Understand the exam and this plan; set up your workspace.
- [ ] Read `EXAM-PREP.md` end-to-end (don't memorize — absorb the shape).
- [x] Skim `NOTES-TOPICS.md` and all 6 project guides so you know what's coming.
- [ ] Set up a notes folder/app and a dev environment (Agent SDK + API key) for projects. _(env/notes done; API key still pending)_
- [ ] Read `EXAM-PREP.md` §4 (heuristics) a second time — this is your north star.

🌙 **Evening log:** _Confidence (1–5): 4 · What clicked: plan critique — projects already built, so theory = consolidation not first-exposure · Revisit: EXAM-PREP §4 heuristics (skipped, the real gap)_

#### Day 2 · Wed Jun 17 — Phase 1: Domain 1 notes
**Focus:** Agentic loop fundamentals.
- [ ] Warm-up (15m): re-read §4 heuristics 4.1–4.3. _(skipped — §4 not yet read)_
- [x] Notes: agentic loop lifecycle, tool results in history, model-driven vs pre-configured control,
      loop anti-patterns (NOTES §1, first 4 topics).
- [x] Active recall: from memory, write the loop control flow and the 3 anti-patterns + why each is wrong.

🌙 **Evening log:** _Confidence (1–5): 5 · What clicked: stop_reason is the only control signal; text ≠ completion · Revisit: — (Batch 1 quiz 5/5)_

#### Day 3 · Thu Jun 18 — Phase 1: Domain 1 notes
**Focus:** Coordinator–subagent orchestration.
- [x] Warm-up (15m): recite yesterday's loop anti-patterns.
- [x] Notes: hub-and-spoke, subagent context isolation, coordinator responsibilities,
      narrow-decomposition risk, scope partitioning, iterative refinement (NOTES §1).
- [x] Active recall: explain why subagents don't inherit context and what you must do about it.

🌙 **Evening log:** _Confidence (1–5): 4 · What clicked: scope partitioning (prevent) + refinement loop (cure) are complementary · Revisit: narrow-decomposition blame-attribution — initially blamed synthesis, not the coordinator_

#### Day 4 · Fri Jun 19 — Phase 1: Domain 1 notes
**Focus:** Spawning, context passing, enforcement & handoff.
- [x] Warm-up (15m): coordinator responsibilities from memory.
- [x] Notes: `Task` tool + `allowedTools`, `AgentDefinition`, parallel spawning, goal-vs-procedural
      prompts, programmatic enforcement vs prompt, prerequisite gates, structured handoff (NOTES §1).
- [x] Active recall: when do you use a hook/gate instead of a prompt instruction?

🌙 **Evening log:** _Confidence (1–5): 5 · What clicked: prompts are probabilistic, gates/hooks deterministic — enforce money/safety in code · Revisit: — (Batch 3 quiz 7/7)_

#### Day 5 · Sat Jun 20 — Phase 1: Domain 1 notes
**Focus:** Hooks, decomposition, sessions.
- [x] Warm-up (15m): prerequisite-gate example (refund) from memory.
- [x] Notes: `PostToolUse` normalization, tool-call interception, hooks-vs-prompts, prompt chaining vs
      dynamic decomposition, `--resume`, `fork_session`, resume-vs-fresh (NOTES §1, remaining topics).
- [x] Active recall: resume vs start-fresh-with-summary — when each?
- [x] ✅ Mark NOTES §1 progress box if all 24 Domain-1 topics are noted.

🌙 **Evening log:** _Confidence (1–5): 5 · What clicked: resume when context valid; fresh+summary when tool results stale (name changed files) · Revisit: — (Batch 4 quiz 7/7)_

#### Day 6 · Sun Jun 21 — 🛌 REST
- [x] Optional 15-min skim of anything flagged "revisit" this week. Otherwise rest.

🌙 **Evening log:** _Domain 1 closed out: 10/10 on a fresh full-domain practice exam (1.1–1.7), exam-ready. Re-tested the narrow-decomposition revisit item in a new scenario — passed. Next: EXAM-PREP §4 heuristics (standing gap), then the coordinator+gate+hook build exercise._

---

## Week 2 — Domains 2 & 3 (Tool Design/MCP 18% · Claude Code 20%)

#### Day 7 · Mon Jun 22 — Phase 1: Domain 1 buffer + recall
**Focus:** Lock in the 27% domain before moving on.
- [ ] Warm-up (15m): one topic from each of Days 2–5.
- [ ] Self-quiz: answer Project 01 & 04 "Be able to answer" questions from memory (no peeking).
- [ ] Fill any Domain-1 note gaps revealed by the quiz.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 8 · Tue Jun 23 — Phase 1: Domain 2 notes
**Focus:** Tool interfaces & errors.
- [ ] Warm-up (15m): Domain-1 weak topic.
- [ ] Notes: tool descriptions as selection mechanism, good-description contents, overlapping-tool
      misrouting, system-prompt keyword sensitivity, `isError`, error taxonomy, structured error
      metadata, access-failure-vs-empty (NOTES §2, first ~8).
- [ ] Active recall: the 4 error categories + which are retryable.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 9 · Wed Jun 24 — Phase 1: Domain 2 notes
**Focus:** Tool distribution & MCP config.
- [ ] Warm-up (15m): error taxonomy from memory.
- [ ] Notes: too-many-tools, cross-specialization misuse, scoped tools, `tool_choice` options,
      MCP server scoping, env var expansion, simultaneous servers, MCP resources, community-vs-custom,
      built-in tools (NOTES §2, remaining).
- [ ] Active recall: `auto` vs `any` vs forced `tool_choice`.
- [ ] ✅ Mark NOTES §2 progress box.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 10 · Thu Jun 25 — Phase 1: Domain 3 notes
**Focus:** CLAUDE.md hierarchy & config.
- [ ] Warm-up (15m): `tool_choice` options.
- [ ] Notes: CLAUDE.md hierarchy, `@import`, `.claude/rules/`, config-hierarchy diagnosis, `/memory`
      (NOTES §3, first ~5).
- [ ] Active recall: where does a *shared* vs *personal* instruction live?

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 11 · Fri Jun 26 — Phase 1: Domain 3 notes
**Focus:** Commands, skills, path rules.
- [ ] Warm-up (15m): shared-vs-personal config locations.
- [ ] Notes: slash commands (project vs user), skills + SKILL.md frontmatter, `context: fork`,
      skills-vs-CLAUDE.md, path-specific rules, glob-vs-directory-CLAUDE.md (NOTES §3, middle).
- [ ] Active recall: test files everywhere → which mechanism and why?

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 12 · Sat Jun 27 — Phase 1: Domain 3 notes
**Focus:** Plan mode, refinement, CI/CD.
- [ ] Warm-up (15m): glob rules vs directory CLAUDE.md.
- [ ] Notes: plan mode vs direct, Explore subagent, iterative refinement techniques, CI `-p/--print`,
      `--output-format json`/`--json-schema`, CLAUDE.md as CI context, session isolation in CI,
      re-run hygiene (NOTES §3, remaining).
- [ ] Active recall: why does a fresh instance review better than the generator session?
- [ ] ✅ Mark NOTES §3 progress box.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 13 · Sun Jun 28 — 🛌 REST
- [ ] Optional light skim of week's "revisit" notes.

🌙 **Evening log:** _Energy/notes: ____

---

## Week 3 — Domains 4 & 5 (Prompt/Structured 20% · Context/Reliability 15%)

#### Day 14 · Mon Jun 29 — Phase 1: Domain 4 notes
**Focus:** Explicit criteria & few-shot.
- [ ] Warm-up (15m): Domain-3 weak topic.
- [ ] Notes: explicit-criteria-vs-vague, false positives & trust, severity definitions, few-shot core,
      few-shot reasoning/generalization, few-shot for extraction (NOTES §4, first ~6).
- [ ] Active recall: why does "be conservative" fail to reduce false positives?

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 15 · Tue Jun 30 — Phase 1: Domain 4 notes
**Focus:** Structured output & schemas.
- [ ] Warm-up (15m): few-shot use cases.
- [ ] Notes: tool_use + JSON schema, `tool_choice` for output, schema design (nullable/enum/other),
      format normalization in prompts (NOTES §4, middle).
- [ ] Active recall: tool_use eliminates *which* errors but not which?

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 16 · Wed Jul 1 — Phase 1: Domain 4 notes
**Focus:** Validation, batch, multi-pass review.
- [ ] Warm-up (15m): syntax vs semantic errors.
- [ ] Notes: validation + retry-with-feedback, limits of retry, semantic self-validation, Message
      Batches API, batch appropriateness, multi-instance review, multi-pass review, confidence per
      finding (NOTES §4, remaining).
- [ ] Active recall: the 4 defining constraints of the batch API.
- [ ] ✅ Mark NOTES §4 progress box.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 17 · Thu Jul 2 — Phase 1: Domain 5 notes
**Focus:** Context preservation & escalation.
- [ ] Warm-up (15m): batch API constraints.
- [ ] Notes: progressive-summarization risk, case-facts block, lost-in-the-middle, tool-output bloat,
      structured upstream output, escalation triggers, escalate-now-vs-offer, unreliable signals,
      multiple-matches-clarify (NOTES §5, first ~9).
- [ ] Active recall: 3 valid escalation triggers vs 2 invalid signals.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 18 · Fri Jul 3 — Phase 1: Domain 5 notes
**Focus:** Error propagation & large-codebase context.
- [ ] Warm-up (15m): escalation triggers.
- [ ] Notes: multi-agent error propagation, propagation anti-patterns, local-recovery-first, coverage
      annotations, context degradation, scratchpad files, subagent delegation, crash-recovery manifests,
      `/compact` (NOTES §5, middle).
- [ ] Active recall: 3 error-propagation anti-patterns.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 19 · Sat Jul 4 — Phase 1: Domain 5 notes
**Focus:** Human review, calibration, provenance.
- [ ] Warm-up (15m): propagation anti-patterns.
- [ ] Notes: human review & confidence calibration, stratified sampling, accuracy segmentation,
      provenance/claim-source mappings, conflicting sources, temporal data, content-type rendering
      (NOTES §5, remaining).
- [ ] Active recall: why is a 97% aggregate accuracy dangerous?
- [ ] ✅ Mark NOTES §5 progress box.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 20 · Sun Jul 5 — 🛌 REST
- [ ] Optional light skim of "revisit" notes.

🌙 **Evening log:** _Energy/notes: ____

---

## Week 4 — Glossary + Consolidation, then Projects begin

#### Day 21 · Mon Jul 6 — Phase 1: Glossary + consolidation
**Focus:** Close out theory; prove retention.
- [ ] Warm-up (15m): one topic from each domain.
- [ ] Notes: §6 glossary — one-liner + "what it's for" for all 14 terms.
- [ ] Self-quiz: re-derive sample questions **Q1–Q4** from memory (answer + why each distractor fails).
- [ ] ✅ Mark NOTES §6 progress box. **Phase 1 complete** if all sections ticked.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 22 · Tue Jul 7 — Phase 2: Project 01 (Customer Support Agent)
**Focus:** Tools + agentic loop. (Domains 1,2,5)
- [ ] Warm-up (15m): loop anti-patterns + prerequisite gate.
- [ ] Build steps 1–2: differentiating tool descriptions; `stop_reason`-driven loop.
- [ ] Verify the loop continues on `tool_use`, ends on `end_turn`.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 23 · Wed Jul 8 — Phase 2: Project 01
**Focus:** Structured errors + deterministic gate.
- [ ] Warm-up (15m): error taxonomy.
- [ ] Build steps 3–5: structured error responses; **prerequisite gate** (no refund without verified
      ID); tool-call interception hook (>$500) + `PostToolUse` normalization.
- [ ] Prove the gate blocks the refund even when the prompt would allow it.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 24 · Thu Jul 9 — Phase 2: Project 01
**Focus:** Escalation + context discipline; close out.
- [ ] Warm-up (15m): escalation triggers.
- [ ] Build steps 6–7: escalation few-shot + multi-concern decomposition + structured handoff +
      "case facts" block.
- [ ] ✅ Tick Project 01 "Definition of done"; answer its self-quiz from memory.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 25 · Fri Jul 10 — Phase 2: Project 02 (Claude Code Team Workflow)
**Focus:** CLAUDE.md hierarchy + path rules. (Domains 3,2,5)
- [ ] Warm-up (15m): shared-vs-personal config.
- [ ] Build steps 1–2: CLAUDE.md hierarchy + `@import` + `/memory`; `.claude/rules/` glob rule.
- [ ] Verify a rule loads only on matching files.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 26 · Sat Jul 11 — Phase 2: Project 02
**Focus:** Commands, skills, MCP.
- [ ] Warm-up (15m): skills vs CLAUDE.md vs rules.
- [ ] Build steps 3–5: `/review` command; skill with `context: fork`/`allowed-tools`/`argument-hint`;
      `.mcp.json` with env-var expansion + a user-scope server.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 27 · Sun Jul 12 — 🛌 REST
🌙 **Evening log:** _Energy/notes: ____

---

## Week 5 — Projects 02–04

#### Day 28 · Mon Jul 13 — Phase 2: Project 02 close-out
**Focus:** Plan mode vs direct; finish.
- [ ] Warm-up (15m): plan-vs-direct triggers.
- [ ] Build step 6: run 3 tasks (single-file fix / migration / new feature) and pick modes; use Explore subagent.
- [ ] ✅ Tick Project 02 "Definition of done"; self-quiz from memory.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 29 · Tue Jul 14 — Phase 2: Project 03 (Structured Data Extraction)
**Focus:** Schema + tool_use. (Domains 4,5)
- [ ] Warm-up (15m): tool_use eliminates which errors?
- [ ] Build steps 1–2: extraction tool with required/optional/nullable + enum/"other"; `tool_choice` control.
- [ ] Verify missing fields return `null`, not fabricated values.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 30 · Wed Jul 15 — Phase 2: Project 03
**Focus:** Validation/retry + few-shot.
- [ ] Warm-up (15m): limits of retry.
- [ ] Build steps 3–5: retry-with-error-feedback loop; semantic self-validation; few-shot for varied layouts.
- [ ] Prove the loop *gives up* correctly when info is absent from source.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 31 · Thu Jul 16 — Phase 2: Project 03 close-out
**Focus:** Batch + human review.
- [ ] Warm-up (15m): batch API constraints.
- [ ] Build steps 6–7: batch run with `custom_id` failure resubmission; field-level confidence routing
      + per-field accuracy analysis.
- [ ] ✅ Tick Project 03 "Definition of done"; self-quiz from memory.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 32 · Fri Jul 17 — Phase 2: Project 04 (Multi-Agent Research)
**Focus:** Spawning + parallel. (Domains 1,2,5)
- [ ] Warm-up (15m): why subagents don't inherit context.
- [ ] Build steps 1–2: coordinator with `Task` in `allowedTools`; explicit context passing;
      parallel Task calls in one turn (measure latency win).

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 33 · Sat Jul 18 — Phase 2: Project 04
**Focus:** Narrow-decomposition bug + scoped tool.
- [ ] Warm-up (15m): narrow-decomposition risk.
- [ ] Build steps 3–4: reproduce the narrow-decomposition failure, then fix with broad partition +
      refinement loop; add scoped `verify_fact` tool to synthesis.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 34 · Sun Jul 19 — 🛌 REST
🌙 **Evening log:** _Energy/notes: ____

---

## Week 6 — Projects 04–06

#### Day 35 · Mon Jul 20 — Phase 2: Project 04 close-out
**Focus:** Error propagation + provenance.
- [ ] Warm-up (15m): propagation anti-patterns.
- [ ] Build steps 5–7: structured error context on timeout; claim→source provenance; conflict
      annotation with dates; coverage annotations.
- [ ] ✅ Tick Project 04 "Definition of done"; self-quiz from memory.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 36 · Tue Jul 21 — Phase 2: Project 05 (Claude Code in CI/CD)
**Focus:** Non-interactive + structured output. (Domains 3,4)
- [ ] Warm-up (15m): why CI jobs hang and the fix.
- [ ] Build steps 1–2: `-p/--print` invocation; `--output-format json` + `--json-schema` findings.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 37 · Wed Jul 22 — Phase 2: Project 05
**Focus:** Explicit criteria + few-shot + independence.
- [ ] Warm-up (15m): why "be conservative" fails.
- [ ] Build steps 3–5: explicit categorical review criteria + per-severity examples; few-shot;
      independent review instance.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 38 · Thu Jul 23 — Phase 2: Project 05 close-out
**Focus:** Multi-pass review + CI context + sync/batch.
- [ ] Warm-up (15m): attention dilution fix.
- [ ] Build steps 6–9: per-file + integration passes; CLAUDE.md as CI context; re-run hygiene; sync vs batch.
- [ ] ✅ Tick Project 05 "Definition of done"; self-quiz from memory.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 39 · Fri Jul 24 — Phase 2: Project 06 (Developer Productivity / Explorer)
**Focus:** Built-in tools + MCP resources. (Domains 2,3,1)
- [ ] Warm-up (15m): Grep vs Glob; Edit→Read+Write fallback.
- [ ] Build steps 1–2: deliberate built-in tool selection; MCP server + content-catalog resource.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 40 · Sat Jul 25 — Phase 2: Project 06
**Focus:** Plan/Explore + large-codebase context.
- [ ] Warm-up (15m): context degradation symptoms.
- [ ] Build steps 3–4: plan mode + Explore subagent; scratchpads + subagent delegation + `/compact`
      + crash-recovery manifest.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 41 · Sun Jul 26 — 🛌 REST
🌙 **Evening log:** _Energy/notes: ____

---

## Week 7 — Finish projects, begin practice

#### Day 42 · Mon Jul 27 — Phase 2: Project 06 close-out
**Focus:** Sessions; finish all projects.
- [ ] Warm-up (15m): resume vs fork vs fresh.
- [ ] Build steps 5–6: `--resume` + `fork_session`; interview pattern + input/output examples.
- [ ] ✅ Tick Project 06 "Definition of done". **Phase 2 complete — all 6 projects done.**

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 43 · Tue Jul 28 — Phase 2: Buffer / catch-up
**Focus:** Finish anything unfinished from any project.
- [ ] Warm-up (15m): a weak topic from your nightly logs.
- [ ] Close out any incomplete "definition of done" boxes across all 6 projects.
- [ ] If fully ahead: re-derive sample questions **Q5–Q8** from memory.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 44 · Wed Jul 29 — Phase 2→3: Integration review
**Focus:** Connect projects back to theory.
- [ ] Warm-up (15m): scan all nightly "revisit" notes; build a **Weak List**.
- [ ] For each project, answer all "Be able to answer" questions cold; patch weak notes.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 45 · Thu Jul 30 — Phase 3: Sample questions deep dive (1/2)
**Focus:** Q1–Q6.
- [ ] Warm-up (15m): EXAM-PREP §4 heuristics 4.1–4.6.
- [ ] For Q1–Q6: write the answer **and** why each of the 3 distractors is wrong, and which heuristic applies.
- [ ] Add any concept you fumbled to the Weak List.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 46 · Fri Jul 31 — Phase 3: Sample questions deep dive (2/2)
**Focus:** Q7–Q12.
- [ ] Warm-up (15m): EXAM-PREP §4 heuristics 4.7–4.12.
- [ ] For Q7–Q12: answer + distractor analysis + heuristic, from memory.
- [ ] You should now be able to do all 12 cold.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 47 · Sat Aug 1 — Phase 3: Scenario drills
**Focus:** Think in scenarios (the exam shows 4 of 6).
- [ ] Warm-up (15m): the 6 scenarios + their primary domains (EXAM-PREP §3).
- [ ] For each scenario, write 2 plausible failure modes and the *most effective* fix for each.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 48 · Sun Aug 2 — 🛌 REST
🌙 **Evening log:** _Energy/notes: ____

---

## Week 8 — Weak-area grind + practice exam

#### Day 49 · Mon Aug 3 — Phase 3: Full active-recall pass
**Focus:** Re-quiz every domain.
- [ ] Warm-up (15m): Weak List review.
- [ ] Closed-book: write the key tradeoff for every 🔴/🟠 topic in NOTES-TOPICS. Mark any <4 confidence.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 50 · Tue Aug 4 — Phase 3: Weak-area remediation
**Focus:** Grind the Weak List.
- [ ] Warm-up (15m): yesterday's <4 topics.
- [ ] Rewrite/expand notes for every weak topic; re-test until each is ≥4.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 51 · Wed Aug 5 — Phase 3: Heuristics + cheatsheet mastery
**Focus:** EXAM-PREP §4 and §6.
- [ ] Warm-up (15m): recite the distractor smell-test.
- [ ] From memory, reproduce all 12 heuristics (§4) and the fact cheatsheet (§6). Patch gaps.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 52 · Thu Aug 6 — Phase 3: Self-made mock (timed)
**Focus:** Exam stamina.
- [ ] Write/collect ~20 scenario MCQs (reuse the 12 samples + invent 8 from your projects).
- [ ] Take them **timed, closed-book**. Score yourself. Log every miss to the Weak List.

🌙 **Evening log:** _Mock score: __ / 20 · Weakest: ____

#### Day 53 · Fri Aug 7 — Phase 3: Mock review + remediate
**Focus:** Convert misses into mastery.
- [ ] For every mock miss: write why the right answer wins and why you fell for the distractor.
- [ ] Re-test the same concepts a different way.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 54 · Sat Aug 8 — Phase 3: Official Practice Exam (timed) ⭐
**Focus:** The real dress rehearsal.
- [ ] Take the **official Anthropic Practice Exam** (link provided separately) under exam conditions:
      timed, no notes, no interruptions.
- [ ] Record score and every missed topic. **This is your primary readiness signal.**

🌙 **Evening log:** _Practice exam score: ____ · Weak domains: ____

#### Day 55 · Sun Aug 9 — 🛌 REST
🌙 **Evening log:** _Energy/notes: ____

---

## Week 9 — Final readiness & exam

#### Day 56 · Mon Aug 10 — Phase 4: Practice-exam remediation
**Focus:** Close every gap the practice exam exposed.
- [ ] Warm-up (15m): review practice-exam misses.
- [ ] Deep-dive each missed topic: re-read the note, the relevant project step, and the heuristic.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 57 · Tue Aug 11 — Phase 4: Second practice pass / targeted drills
**Focus:** Verify remediation worked.
- [ ] Re-take the practice exam (or your Day-52 mock) — aim notably higher.
- [ ] Any remaining miss → same-day fix.

🌙 **Evening log:** _Score: ____ · Remaining weak: ____

#### Day 58 · Wed Aug 12 — Phase 4: Final consolidation
**Focus:** One clean pass over the highest-leverage material.
- [ ] EXAM-PREP §4 (heuristics) + §6 (cheatsheet) + §7 (out-of-scope) — recite cold.
- [ ] Skim each project's "Be able to answer" — all should be effortless now.

🌙 **Evening log:** _Confidence (1–5): __ · What clicked: ___ · Revisit: ____

#### Day 59 · Thu Aug 13 — Phase 4: Taper + logistics + Go/No-Go
**Focus:** Arrive fresh, not crammed.
- [ ] Light review only (≤1 hr): re-read your nightly "revisit" highlights.
- [ ] Complete the **Go/No-Go readiness gate** below. If green → confirm exam booking for tomorrow.
- [ ] Logistics: ID, system check, quiet space, good sleep. **No new material today.**

🌙 **Evening log:** _Go/No-Go: ___ · Ready? ____

#### Day 60 · Fri Aug 14 — 🎯 EXAM DAY (or buffer)
**Focus:** Execute.
- [ ] 15-min warm-up: skim heuristics §4 only. No cramming.
- [ ] Take the exam. Per question: name the heuristic, eliminate 2 distractors, pick the *most
      effective/proportionate/root-cause* answer. **Answer everything — no penalty for guessing.**
- [ ] _(If not ready: use this as a buffer day and rebook within the week.)_

🌙 **Evening log:** _Result: ___ · 🎉_

---

## ✅ Go/No-Go readiness gate (must all be true before you sit the exam)

- [ ] All 6 projects' "Definition of done" checklists complete.
- [ ] Every topic in `NOTES-TOPICS.md` §1–§6 noted; all 🔴/🟠 topics at confidence ≥ 4.
- [ ] Can reproduce all 12 sample questions cold (answer + why each distractor fails + heuristic).
- [ ] Can recite all of EXAM-PREP §4 heuristics and §6 cheatsheet from memory.
- [ ] **Official practice exam ≥ ~80%** (comfortable margin above the 720/1000 ≈ 72% bar).
- [ ] Weak List is empty (every flagged item remediated and re-tested ≥ 4).
- [ ] You feel rested, not crammed.

**If any box is unchecked, use a buffer/rest day to fix it and push the exam a few days — a delayed
pass beats a rushed fail.**

---

## If you're ahead of schedule

You've got generous time. If you're consistently finishing early:
- Add a 3rd full pass over the sample questions and a second self-made mock.
- Re-build the *trickiest* project step without looking at the guide (pure recall).
- Teach a domain out loud to an imaginary colleague — the fastest way to find soft spots.
- **Do not** start studying out-of-scope topics (EXAM-PREP §7). More breadth there ≠ more points.

## If you fall behind

- Protect the **non-negotiables**: Domain-1 notes, all 6 projects, the 12 sample questions, and one
  timed practice exam.
- Trim: glossary one-liners can be skimmed; scenario drills (Day 47) can fold into Day 49.
- Use rest days as catch-up *only when needed* — don't sacrifice all recovery.
