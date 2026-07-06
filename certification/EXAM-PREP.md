# Claude Certified Architect – Foundations: Master Study Guide

> **One file with everything you need to pass.** Read this top-to-bottom once, then use it
> as a reference while building the 6 projects in `certification/projects/`. The night before
> the exam, re-read the **Answer-Selection Heuristics** and **Fact Cheatsheet** sections —
> they are where most points are won or lost.

---

## 1. Exam mechanics (know these cold)

| Fact | Value |
|------|-------|
| Format | Multiple choice, **single best answer**, 1 correct + 3 distractors |
| Length | **60 questions** in **120 minutes** (~2 min/question) |
| Scoring | Scaled **100–1,000**, **pass = 720**, pass/fail |
| Answering | The platform **forces an answer** before you can advance — so effectively no blanks, no penalty for guessing |
| Scenarios | **4 scenarios** drawn at random from a pool of **6** |
| Delivery | Online proctored **or** at a test center |
| Fee | **$125 USD** |
| Validity | **12 months** from award date |
| Last updated | Guide **v0.2, June 30 2026** |

> **Guide v0.2 vs v0.1 (what changed):** only logistics. All 5 domains + weightings, all 28 task
> statements, all 12 sample questions, and all 4 preparation exercises are **word-for-word identical**.
> New in v0.2: the "Exam Details at a Glance" table above (60 Q / 120 min / $125 / delivery / 12-month
> validity), and the answering policy (the platform now forces an answer per question — v0.1 said
> "unanswered = incorrect, no guessing penalty"). Dropped in v0.2: the explicit "Complete the Practice
> Exam" prep recommendation (though sample questions are still described as drawn from the practice test).
> **No study-content changes — our prep material remains fully current.**

**Distractors are designed to look right to someone with incomplete knowledge.** The test
rewards *practical judgment about tradeoffs*, not memorized definitions. Almost every
question is "what is the **most effective** / **best first step** / **most likely root cause**" —
so you're choosing the *proportionate, root-cause* answer, not just a technically-valid one.

---

## 2. Domains and weightings

| # | Domain | Weight | Build focus |
|---|--------|--------|-------------|
| 1 | **Agentic Architecture & Orchestration** | **27%** | Agentic loop, coordinator/subagent, hooks, decomposition, sessions |
| 2 | **Tool Design & MCP Integration** | **18%** | Tool descriptions, structured errors, tool distribution, MCP config, built-in tools |
| 3 | **Claude Code Configuration & Workflows** | **20%** | CLAUDE.md hierarchy, commands/skills, path rules, plan mode, CI/CD |
| 4 | **Prompt Engineering & Structured Output** | **20%** | Explicit criteria, few-shot, tool_use schemas, validation/retry, batch, multi-pass review |
| 5 | **Context Management & Reliability** | **15%** | Context preservation, escalation, error propagation, codebase context, human review, provenance |

Domain 1 is the biggest single bucket — **prioritize the agentic loop, coordinator-subagent
patterns, and hooks**. Domains 3+4 together are 40% — Claude Code config and prompt/structured
output are equally heavy.

---

## 3. The 6 scenarios (and which project trains each)

| Scenario | Theme | Primary domains | Project |
|----------|-------|-----------------|---------|
| 1 | Customer Support Resolution Agent | 1, 2, 5 | `01-customer-support-agent` |
| 2 | Code Generation with Claude Code | 3, 5 | `02-claude-code-team-workflow` |
| 3 | Multi-Agent Research System | 1, 2, 5 | `04-multi-agent-research` |
| 4 | Developer Productivity with Claude | 2, 3, 1 | `06-developer-productivity-explorer` |
| 5 | Claude Code for Continuous Integration | 3, 4 | `05-claude-code-cicd` |
| 6 | Structured Data Extraction | 4, 5 | `03-structured-data-extraction` |

---

## 4. Answer-Selection Heuristics ⭐ (the highest-leverage section)

The sample questions reveal a consistent "house style" for the correct answer. Internalize
these decision rules — they let you eliminate distractors fast.

### 4.1 Determinism vs. probability
- **Business rule that MUST hold every time → programmatic enforcement** (hook / prerequisite
  gate), **never** prompt instructions. Prompts have a non-zero failure rate.
  - *e.g. "block `process_refund` until `get_customer` returned a verified ID" → a prerequisite
    gate, not "tell the model it's mandatory."* (Q1 → A)
- Prompt-based guidance is fine for *soft* ordering preferences, not for financial/identity gates.

### 4.2 Root cause, not symptom
- Fix the agent/component that is **actually wrong**, not a downstream one that is working
  correctly. If the coordinator decomposed the topic too narrowly, the bug is the
  **coordinator's decomposition** — not the search/synthesis agents. (Q7 → B)
- Bad tool selection between similar tools → the **descriptions** are the root cause. (Q2 → B)

### 4.3 Proportionate "first step"
- Prefer the **low-effort, high-leverage** fix before adding infrastructure.
  - Improve tool **descriptions** before adding a routing classifier or consolidating tools. (Q2 → B)
  - Add **explicit criteria + few-shot** before training a classifier or building sentiment analysis. (Q3 → A)
- Distractors that "build a separate ML classifier / routing layer / sentiment model" are almost
  always **over-engineered** — wrong unless prompt-level fixes have demonstrably failed.

### 4.4 Self-report confidence and sentiment are unreliable
- **LLM self-reported confidence is poorly calibrated** — the model is *already* wrongly confident
  on hard cases. Don't route escalation on a self-scored 1–10. (Q3 distractor B is wrong)
- **Sentiment ≠ complexity.** Frustration doesn't tell you a case is hard. (Q3 distractor D is wrong)
- Calibrate confidence only against a **labeled validation set**; use **stratified sampling** to
  measure true error rates.

### 4.5 Least privilege / scoped tools
- Give each agent **only the tools its role needs** (4–5, not 18). Too many tools degrades selection.
- For a frequent cross-role need, add **one scoped tool** (e.g. `verify_fact` for the synthesis
  agent) — don't hand it the entire toolset, and don't route everything through the coordinator. (Q9 → A)

### 4.6 Structured everything (errors, context, output)
- Errors → **structured error context**: failure type, attempted query, partial results,
  alternatives, `isRetryable`. Never a generic "operation failed" / "search unavailable",
  never silently swallow (return empty as success), never kill the whole workflow on one failure. (Q8 → A)
- Output → **tool_use with a JSON schema** is the most reliable structured output (eliminates
  *syntax* errors; does **not** fix *semantic* errors like totals not summing).
- Context handoff → pass **structured data with metadata** (source URL, date, page) so attribution survives.

### 4.7 Attention dilution → split passes
- Inconsistent/contradictory review of many files at once = **attention dilution**. Fix by
  **per-file passes + a separate cross-file integration pass** — not a bigger context window,
  not forcing devs to split PRs, not 2-of-3 voting. (Q12 → A)
- A larger context window does **not** fix attention *quality*.

### 4.8 Independent review beats self-review
- A model that **generated** code retains its reasoning and won't question itself well.
  Use a **second independent instance** (no prior reasoning context). Extended thinking ≠ independence.

### 4.9 Match the API to the latency requirement
- **Message Batches API** = 50% cheaper, up to **24h**, no latency SLA → great for overnight/weekly
  jobs, **wrong for blocking** pre-merge checks. Don't switch a blocking workflow to batch. (Q11 → A)

### 4.10 Honor explicit human requests immediately
- If a customer **explicitly asks for a human**, escalate immediately — don't investigate first.
- Escalate on **policy gaps/silence** (e.g. competitor price-matching not in policy), customer
  request, or inability to progress — *not* on "it's complex" or "they sound angry."
- Multiple matches → **ask for another identifier**, never pick heuristically.

### 4.11 Plan mode vs direct execution
- **Plan mode** when complexity is *already stated*: large-scale/multi-file, architectural
  decisions, multiple valid approaches (e.g. monolith→microservices, 45-file migration). (Q5 → A)
- **Direct execution** for well-scoped single changes (single-file bug with a clear stack trace,
  adding one validation conditional). "Start direct, switch later" is wrong when complexity is known.

### 4.12 Right config location (Claude Code)
- Shared with the team via git → **project scope** (`.claude/commands/`, `.claude/CLAUDE.md`,
  `.mcp.json`, `.claude/rules/`).
- Personal/not shared → **user scope** (`~/.claude/commands/`, `~/.claude/CLAUDE.md`, `~/.claude.json`).
- Conventions for files **spread across directories** (e.g. all `*.test.tsx`) → **`.claude/rules/`
  with glob `paths:` frontmatter**, *not* per-directory CLAUDE.md (directory-bound) and *not* a
  monolithic root CLAUDE.md relying on inference. (Q6 → A)

### Quick distractor smell-test
A distractor is probably wrong if it: trains/deploys a separate ML model; builds a routing/keyword
parser to bypass the LLM; relies on self-reported confidence or sentiment; uses a bigger model/context
to fix a *structure* problem; suppresses or genericizes errors; uses prompt instructions where a
deterministic guarantee is required; or is "valid but disproportionate" for a *first step*.

---

## 5. Domain task-statement digest

### Domain 1 — Agentic Architecture & Orchestration (27%)
- **1.1 Agentic loop:** loop while `stop_reason == "tool_use"`, stop on `"end_turn"`. Append tool
  results to conversation history each turn. **Anti-patterns:** parsing natural-language to decide
  termination, arbitrary iteration caps as the *primary* stop, checking for assistant text as "done."
- **1.2 Coordinator–subagent (hub-and-spoke):** coordinator owns all inter-agent comms, error
  handling, routing. Subagents have **isolated context** (no inherited history). Coordinator does
  decomposition/delegation/aggregation and **dynamically selects** which subagents to run.
  Partition scope to avoid duplication. **Iterative refinement:** evaluate synthesis for gaps,
  re-delegate targeted queries, re-synthesize. Risk: **too-narrow decomposition → missed coverage.**
- **1.3 Spawning/context passing:** `Task` tool spawns subagents; coordinator's `allowedTools` must
  include `"Task"`. Context must be **explicitly in the prompt**. `AgentDefinition` = description +
  system prompt + tool restrictions. **Parallel** subagents = multiple `Task` calls in **one**
  response. Coordinator prompts specify **goals/quality criteria**, not step-by-step procedures.
- **1.4 Enforcement & handoff:** programmatic gates/hooks for required ordering (deterministic) vs
  prompt guidance (probabilistic). Decompose multi-concern requests, investigate in parallel,
  synthesize one resolution. **Structured handoff** to humans = customer ID, root cause, amount,
  recommended action (the human can't see the transcript).
- **1.5 Hooks:** `PostToolUse` to **normalize** heterogeneous tool data (Unix vs ISO 8601 vs status
  codes) before the model sees it. **Tool-call interception** to **block** policy violations (refund
  > $500) and redirect to escalation. Use hooks when compliance must be guaranteed.
- **1.6 Decomposition:** **prompt chaining** (fixed sequential) for predictable multi-aspect reviews;
  **dynamic/adaptive** for open-ended investigation. Split big reviews into per-file + cross-file passes.
- **1.7 Sessions:** `--resume <name>` to continue a named session; `fork_session` to branch from a
  shared baseline for divergent approaches. Resume when prior context is mostly valid; **start fresh
  with a structured summary** when prior tool results are **stale**. Tell a resumed session which files changed.

### Domain 2 — Tool Design & MCP Integration (18%)
- **2.1 Tool interfaces:** descriptions are the **primary** selection mechanism. Include input
  formats, example queries, edge cases, boundaries, and *when to use vs similar tools*. Rename/split
  overlapping tools (`analyze_content` → `extract_web_results`; split generic `analyze_document`).
  Watch keyword-sensitive system prompts that override good descriptions.
- **2.2 Structured errors:** MCP **`isError`** flag. Categorize **transient / validation / business /
  permission**; return `errorCategory`, `isRetryable`, human-readable text, `retriable:false` +
  customer-friendly text for business rules. Distinguish **access failure** (retry decision) from a
  **valid empty result** (success, no matches). Subagents recover transient errors locally; only
  propagate the unrecoverable, with partial results + what was attempted.
- **2.3 Tool distribution / `tool_choice`:** too many tools (18 vs 4–5) hurts selection. Scope tools
  to role; add limited cross-role tools for high-frequency needs. `tool_choice`: **`"auto"`** (may
  return text), **`"any"`** (must call *some* tool), **forced** `{"type":"tool","name":"..."}` (must
  call *that* tool — e.g. force `extract_metadata` first).
- **2.4 MCP config:** **project** `.mcp.json` (shared team) vs **user** `~/.claude.json`
  (personal/experimental). **Env var expansion** `${GITHUB_TOKEN}` keeps secrets out of git. All
  configured servers' tools are available simultaneously at connection time. **MCP resources** expose
  content catalogs (issue summaries, schemas, doc hierarchies) to cut exploratory tool calls. Prefer
  community servers (Jira) over custom for standard integrations. Enhance MCP tool descriptions so the
  agent doesn't default to built-ins like Grep.
- **2.5 Built-in tools:** **Grep** = content search; **Glob** = filename/path patterns (`**/*.test.tsx`);
  **Read/Write** = full file; **Edit** = targeted unique-text change → fall back to **Read+Write** when
  Edit can't find a unique anchor. Build understanding **incrementally** (Grep entry points → Read to
  follow imports), don't read everything upfront.

### Domain 3 — Claude Code Configuration & Workflows (20%)
- **3.1 CLAUDE.md hierarchy:** user (`~/.claude/CLAUDE.md`, not shared) → project (`.claude/CLAUDE.md`
  or root `CLAUDE.md`) → directory. `@import` for modularity. `.claude/rules/` for topic files.
  `/memory` shows which memory files are loaded. Classic bug: a teammate misses instructions because
  they live in **user** scope, not project.
- **3.2 Commands & skills:** `.claude/commands/` (shared) vs `~/.claude/commands/` (personal). Skills
  = `.claude/skills/<name>/SKILL.md` with frontmatter **`context: fork`** (isolated subagent context),
  **`allowed-tools`** (restrict tools), **`argument-hint`** (prompt for args). Skills = on-demand;
  CLAUDE.md = always-loaded universal standards.
- **3.3 Path-specific rules:** `.claude/rules/` files with YAML **`paths:`** globs load only when
  editing matching files (saves tokens). Glob rules beat directory CLAUDE.md for files **spread across**
  the tree (all test files everywhere).
- **3.4 Plan mode vs direct:** plan = complex/architectural/multi-file/multiple valid approaches;
  direct = simple well-scoped. **Explore subagent** isolates verbose discovery and returns a summary.
- **3.5 Iterative refinement:** concrete **input/output examples** beat prose. **Test-driven iteration**
  (write tests, share failures). **Interview pattern** (have Claude ask questions first). Fix
  **interacting** problems in one message; **independent** ones sequentially.
- **3.6 CI/CD:** **`-p`/`--print`** = non-interactive (prevents hangs). **`--output-format json`** +
  **`--json-schema`** = machine-parseable findings for inline PR comments. CLAUDE.md supplies project
  context (test standards, fixtures, review criteria). **A fresh instance reviews better than the
  session that wrote the code.** Pass prior findings so re-runs only report new/unaddressed issues.

### Domain 4 — Prompt Engineering & Structured Output (20%)
- **4.1 Explicit criteria:** specific categorical criteria ("flag a comment only when claimed behavior
  contradicts the code") beat vague "be conservative / only high-confidence." High false-positive
  categories destroy trust — temporarily disable them while you fix the prompt. Define severity with
  concrete code examples.
- **4.2 Few-shot:** the most effective technique when detailed instructions still vary. 2–4 targeted
  examples for **ambiguous** cases that show *reasoning for why one choice over alternatives*; demo the
  exact output format; show acceptable-vs-genuine-issue to cut false positives; cover varied document structures.
- **4.3 Structured output:** **tool_use + JSON schema** = guaranteed schema-compliance, no syntax
  errors (but **semantic** errors remain). `tool_choice:"any"` when doc type/schema is unknown; forced
  tool to run a specific extraction first. Make fields **optional/nullable** so the model returns null
  instead of fabricating. Use enum + `"other"`+detail and `"unclear"`. Put normalization rules in the prompt.
- **4.4 Validation/retry:** **retry-with-error-feedback** = resend doc + failed extraction + the
  specific validation error. Retries fix **format/structure** errors, **not missing information**.
  `detected_pattern` field enables false-positive analysis. Extract `calculated_total` alongside
  `stated_total`; add `conflict_detected` for inconsistent sources.
- **4.5 Batch:** Message Batches API = 50% off, ≤24h, no SLA, **no multi-turn tool calling in one
  request**, `custom_id` correlates pairs. Sync for blocking, batch for overnight/weekly. Compute
  submission cadence vs SLA (4h windows → 30h SLA with 24h processing). Resubmit only failed
  `custom_id`s (chunk oversized). Refine prompt on a sample before the full run.
- **4.6 Multi-instance/multi-pass:** independent review instance > self-review/extended thinking.
  Split big reviews per-file + cross-file. Have the model self-report confidence per finding for
  calibrated routing.

### Domain 5 — Context Management & Reliability (15%)
- **5.1 Preserve context:** progressive summarization loses numbers/dates/percentages — extract a
  persistent **"case facts"** block included every prompt. **Lost-in-the-middle:** put key summaries
  at the **start**, use explicit section headers. **Trim verbose tool outputs** to relevant fields
  before they accumulate (40-field order → keep 5). Upstream agents return **structured key facts +
  citations**, not verbose reasoning, when downstream budgets are tight.
- **5.2 Escalation:** triggers = explicit human request, **policy gap/silence**, inability to progress
  (**not** "complex," **not** sentiment, **not** self-confidence). Honor explicit requests immediately.
  Multiple matches → ask for another identifier. Add escalation few-shot to the system prompt.
- **5.3 Error propagation (multi-agent):** structured context (type, attempted, partial, alternatives)
  for coordinator recovery. Distinguish access failure vs valid empty. Local recovery first; propagate
  only the unrecoverable. Synthesis output carries **coverage annotations** (well-supported vs gaps).
- **5.4 Large codebase context:** extended sessions **degrade** (model cites "typical patterns" not the
  specific classes it found). Use **scratchpad files**, **subagent delegation** for verbose discovery,
  **structured state exports/manifests** for crash recovery, summarize-before-next-phase, **`/compact`**.
- **5.5 Human review & calibration:** aggregate accuracy (97%) can hide bad per-type/per-field
  performance. **Stratified sampling** of high-confidence extractions for ongoing error measurement.
  Field-level confidence calibrated on a **labeled validation set**. Validate by document type and
  field **before** automating. Route low-confidence/ambiguous to humans.
- **5.6 Provenance:** keep **claim→source mappings** through summarization. Conflicting credible stats
  → **annotate both with attribution**, don't pick one. Require **publication/collection dates** so
  temporal differences aren't read as contradictions. Render content types natively (financials as
  tables, news as prose), not one uniform format.

---

## 6. Fact Cheatsheet (rapid recall)

**Agent SDK / API**
- Loop: `tool_use` → run tools, append results, continue; `end_turn` → done.
- `Task` tool spawns subagents; coordinator needs `"Task"` in `allowedTools`.
- Subagents = isolated context; pass everything explicitly in the prompt.
- Parallel subagents = multiple `Task` calls in one assistant turn.
- Hooks: `PostToolUse` (normalize results), tool-call interception (block/redirect).
- `tool_choice`: `auto` (text allowed) | `any` (some tool) | `{"type":"tool","name":"X"}` (that tool).
- `stop_reason`: `tool_use`, `end_turn`. Also `max_tokens`, system prompts.

**MCP**
- `isError` flag for failures; structured error metadata (`errorCategory`, `isRetryable`).
- `.mcp.json` (project) vs `~/.claude.json` (user); `${ENV_VAR}` expansion.
- Resources = content catalogs (read) ; Tools = actions. Good descriptions drive adoption.

**Claude Code**
- Hierarchy: `~/.claude/CLAUDE.md` (user) > `.claude/CLAUDE.md`/`CLAUDE.md` (project) > dir.
- `@import`; `.claude/rules/` (+ `paths:` globs); `.claude/commands/`; `.claude/skills/SKILL.md`.
- SKILL.md frontmatter: `context: fork`, `allowed-tools`, `argument-hint`.
- `/memory`, `/compact`, plan mode, `--resume <name>`, `fork_session`, Explore subagent.

**Claude Code CLI**
- `-p`/`--print` non-interactive; `--output-format json`; `--json-schema`.

**Message Batches API**
- 50% cheaper, ≤24h window, no SLA, `custom_id` correlation, no multi-turn tool calling, poll for completion.

**Built-in tools**
- Grep (content) · Glob (paths) · Read/Write (full) · Edit (unique anchor; fallback Read+Write) · Bash.

---

## 7. Out-of-scope (don't over-study these — they're NOT tested)

Fine-tuning/training · API auth/billing/account mgmt · deep language/framework impl · deploying/hosting
MCP servers (infra/networking/containers) · model internals/training/weights · Constitutional AI/RLHF/safety
training · embeddings/vector DB impl · computer use (browser/desktop) · vision/image analysis · streaming/SSE
impl · rate limits/quotas/pricing math · OAuth/key rotation/auth protocols · specific cloud (AWS/GCP/Azure) ·
benchmarking/model comparison · prompt-caching impl details (just know it exists) · tokenization specifics.

If an answer option leans on one of these as the "fix," it's almost certainly a distractor.

---

## 8. Suggested study sequence

1. Read this file once end-to-end. ✅
2. Build the 6 projects (`certification/projects/`) in order — each maps to a scenario/domains.
3. After each project, re-read that domain's digest (§5) and the relevant heuristics (§4).
4. Re-derive every sample question (12 in the PDF) from first principles — explain *why each
   distractor is wrong*, not just the right letter. That skill is the whole exam.
5. Take the official **Practice Exam** under timed conditions if you can get access. (Guide v0.2
   dropped the explicit recommendation/link, but the practice test still exists — the sample
   questions are drawn from it. If no link is provided, use `CROSS-DOMAIN-MOCK.md` as the timed mock.)
6. Night before: §4 (heuristics) + §6 (cheatsheet) + §7 (out-of-scope).

---

## 9. Sample-question pattern log (from the PDF)

| Q | Topic | Answer | Heuristic it tests |
|---|-------|--------|--------------------|
| 1 | Skips `get_customer` before refund | A | Deterministic gate > prompt (§4.1) |
| 2 | Confuses similar tools | B | Descriptions are root cause; proportionate first step (§4.2/4.3) |
| 3 | Poor escalation calibration | A | Explicit criteria+few-shot; self-confidence/sentiment unreliable (§4.4/4.10) |
| 4 | Where to put a shared `/review` command | A | `.claude/commands/` project scope (§4.12) |
| 5 | Monolith→microservices approach | A | Plan mode for known complexity (§4.11) |
| 6 | Conventions for test files everywhere | A | `.claude/rules/` glob `paths:` (§4.12) |
| 7 | Reports miss whole sub-topics | B | Coordinator decomposition too narrow; blame the right component (§4.2) |
| 8 | Subagent timeout propagation | A | Structured error context (§4.6) |
| 9 | Synthesis verification round-trips | A | Scoped cross-role tool, least privilege (§4.5) |
| 10 | CI job hangs on input | A | `-p`/`--print` (§5/Cheatsheet) |
| 11 | Batch both workflows? | A | Match API to latency; batch ≠ blocking (§4.9) |
| 12 | Inconsistent 14-file review | A | Attention dilution → split passes (§4.7) |

When you can produce the "Answer + heuristic + why each distractor fails" for all 12 from memory,
you are ready.
