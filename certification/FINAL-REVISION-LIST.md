# 📝 Final Revision List — before the exam (Sat 11 July 2026)

> Distilled from `EXAM-WEEK-CHECKLIST.md` + `EXAM-PREP.md`, ordered by exam value.
> Everything here is **revision of known material** — no new content. Stop by ~6pm Friday
> (taper rule). Exam morning: 15-min skim of §1 below only.

---

## 1. The 12 answer-selection heuristics (EXAM-PREP §4) — must be cold

Recite all 12 from memory, one line each:

- [ ] 1. **Determinism vs probability** — business rules that must always hold → hooks/gates, never prompt instructions
- [ ] 2. **Root cause, not symptom** — fix the component that's actually wrong (e.g. coordinator's decomposition, not the search agents)
- [ ] 3. **Proportionate first step** — descriptions/few-shot before ML classifiers or routing layers
- [ ] 4. **Self-confidence & sentiment are unreliable** — never route escalation on self-scored confidence or frustration
- [ ] 5. **Least privilege / scoped tools** — 4–5 tools per role; one scoped cross-role tool, not the whole toolset
- [ ] 6. **Structured everything** — errors (`errorCategory`, `isRetryable`, partial results), context handoffs with metadata, tool_use for output
- [ ] 7. **Attention dilution → split passes** — per-file + cross-file integration pass; bigger context ≠ better attention
- [ ] 8. **Independent review beats self-review** — fresh instance, not extended thinking
- [ ] 9. **Match API to latency** — Batch = 50% off, ≤24h, no SLA → never for blocking checks
- [ ] 10. **Honor explicit human requests immediately** — escalate on request / policy gap / stuck, not on "complex" or "angry"
- [ ] 11. **Plan mode vs direct** — plan when complexity is already known (multi-file, architectural); direct for well-scoped single changes
- [ ] 12. **Right config location** — shared → project scope (`.claude/`, `.mcp.json`); personal → user scope; spread-across-tree conventions → `.claude/rules/` with `paths:` globs

## 2. Distractor smell-test

An option is probably wrong if it:

- [ ] Trains/deploys a separate ML model or routing/keyword layer
- [ ] Relies on self-reported confidence or sentiment
- [ ] Uses a bigger model/context to fix a *structure* problem
- [ ] Suppresses or genericizes errors
- [ ] Uses prompts where a deterministic guarantee is needed
- [ ] Leans on a §7 out-of-scope topic as the "fix"
- [ ] Is valid but disproportionate as a *first* step

## 3. The 12 sample questions (EXAM-PREP §9 pattern log)

Reproduce each cold: **answer + heuristic it tests + why each of the 3 distractors fails.**

- [ ] Q1 gate > prompt · Q2 descriptions · Q3 criteria + few-shot · Q4 project commands
- [ ] Q5 plan mode · Q6 rules globs · Q7 coordinator decomposition · Q8 structured errors
- [ ] Q9 scoped tool · Q10 `-p` flag · Q11 not-batch-for-blocking · Q12 split passes

## 4. Fact cheatsheet (EXAM-PREP §6) — rapid recall

- [ ] **Agentic loop:** loop while `stop_reason == "tool_use"`, append results, stop on `end_turn`
- [ ] **Subagents:** `Task` tool · coordinator needs `"Task"` in `allowedTools` · isolated context (pass everything explicitly) · parallel = multiple Task calls in **one** turn
- [ ] **Hooks:** `PostToolUse` normalizes; tool-call interception blocks (e.g. refund > $500)
- [ ] **`tool_choice`:** `auto` (text allowed) · `any` (some tool) · `{"type":"tool","name":"X"}` (that tool)
- [ ] **MCP:** `isError` flag · `.mcp.json` project vs `~/.claude.json` user · `${ENV_VAR}` expansion · resources = read catalogs, tools = actions
- [ ] **Claude Code:** CLAUDE.md hierarchy (user/project/directory) · `@import` · `.claude/rules/` + `paths:` · SKILL.md frontmatter (`context: fork`, `allowed-tools`, `argument-hint`) · `/memory`, `/compact`, `--resume <name>`, `fork_session`
- [ ] **CI/CD:** `-p`/`--print` · `--output-format json` · `--json-schema` · fresh instance reviews better than the session that wrote the code
- [ ] **Batch API:** 50% cheaper · ≤24h · no SLA · `custom_id` correlation · no multi-turn tool calling · resubmit only failed `custom_id`s
- [ ] **Built-ins:** Grep = content · Glob = paths · Read/Write = full file · Edit = unique anchor (fallback Read+Write)

## 5. Out-of-scope list (EXAM-PREP §7) — for smelling distractors

- [ ] Fine-tuning · auth/billing · MCP server hosting/infra · model internals/RLHF ·
      embeddings/vector DBs · computer use · vision · streaming impl · rate limits/pricing math ·
      OAuth · cloud specifics · benchmarking · caching internals · tokenization

## 6. Scenario drill — 6 scenarios (exam draws 4)

For each, write from memory: **primary domains + 2 failure modes + most effective fix.**

- [ ] S1 Customer Support Resolution Agent (D1/2/5)
- [ ] S2 Code Generation with Claude Code (D3/5)
- [ ] S3 Multi-Agent Research System (D1/2/5)
- [ ] S4 Developer Productivity with Claude (D2/3/1)
- [ ] S5 Claude Code for Continuous Integration (D3/4)
- [ ] S6 Structured Data Extraction (D4/5)

## 7. Known weak spots (practice-exam misses, 1 Jul)

- [ ] **Customer Support scenario (14/15)** — re-drill escalation triggers, prerequisite gates, structured tool errors
- [ ] **Claude Code CI scenario (14/15)** — re-drill `-p`, output schemas, review criteria, sync-vs-batch

## 8. Unbuilt-project coverage (reading only)

- [ ] `tracks/prep-exercise-02-claude-code-team-workflow.md` — answer its "Be able to answer" Qs cold (S2)
- [ ] `tracks/prep-exercise-03-structured-data-extraction.md` + `tracks/03-structured-data-extraction.md` — same drill (S6): extraction schemas, null-not-fabricated, validation-retry, few-shot, batch `custom_id`

## 9. Non-study items (Friday evening)

- [ ] Confirm booking time · ID ready
- [ ] Proctoring system check (webcam, browser, bandwidth)
- [ ] Quiet room arranged · phone/notes out of reach · alarm set
- [ ] Evening fully off — good meal, no late screens, full night's sleep

## Exam facts (memorise)

60 Q · 120 min (~2 min each) · single best answer · scaled 100–1,000, **pass = 720 (~72%)** ·
answer forced per question, no guessing penalty · 4 of 6 scenarios · pace check at Q20 (~40 min)
and Q40 (~80 min).
