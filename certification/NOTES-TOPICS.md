# Notes Checklist — Topics to Write Notes On

> **Purpose:** the projects build *muscle memory*; these notes build the *theory and vocabulary* the
> multiple-choice questions test directly. Write a short note (½–1 page) for each topic below — in
> your own words, with the **why** and at least one **"when to use vs the alternative"** comparison,
> since almost every exam question is a tradeoff.
>
> **Sources combined here:** the 5 domains + task statements, the Appendix "Technologies and
> Concepts," "In-Scope Topics," and the "Out-of-Scope" list (so you don't waste time on untested
> material). Tick a box when the note is written *and* you can recite the key tradeoff from memory.
>
> **Note template (suggested):** `What it is → When to use → When NOT to (alternative) → Common
> distractor/trap → One concrete example.`

---

## How to prioritize (by exam weight)

| Priority | Domain | Weight | Notes sections |
|----------|--------|--------|----------------|
| 🔴 Highest | 1 — Agentic Architecture & Orchestration | 27% | §1 |
| 🟠 High | 3 — Claude Code Config & Workflows | 20% | §3 |
| 🟠 High | 4 — Prompt Engineering & Structured Output | 20% | §4 |
| 🟡 Medium | 2 — Tool Design & MCP Integration | 18% | §2 |
| 🟡 Medium | 5 — Context Management & Reliability | 15% | §5 |
| ⚪ Cross-cutting | Tech & concepts glossary | — | §6 |

---

## §1 — Agentic Architecture & Orchestration 🔴 (27%)

- [x] **The agentic loop lifecycle** — request → inspect `stop_reason` → execute tools → append
      results → repeat. Continue on `"tool_use"`, terminate on `"end_turn"`.
- [x] **Tool results in conversation history** — why results must be appended each turn so the model
      can reason about the next action.
- [x] **Model-driven vs pre-configured control** — Claude reasoning about the next tool vs hardcoded
      decision trees / fixed tool sequences.
- [x] **Agentic-loop anti-patterns** — parsing natural language for "done," iteration cap as the
      *primary* stop, treating assistant text as a completion signal. (Know *why* each is wrong.)
- [x] **Hub-and-spoke orchestration** — coordinator owns all inter-subagent comms, error handling, routing.
- [x] **Subagent context isolation** — subagents do NOT inherit coordinator history; context must be
      passed explicitly in the prompt.
- [x] **Coordinator responsibilities** — decomposition, delegation, aggregation, dynamic subagent
      selection by query complexity.
- [x] **Narrow-decomposition risk** — too-narrow task breakdown → incomplete topic coverage (the
      "creative industries → only visual arts" failure).
- [x] **Scope partitioning** — assigning distinct subtopics/source types to subagents to avoid duplication.
- [x] **Iterative refinement loop** — synthesis flags gaps → coordinator re-delegates targeted queries → re-synthesize.
- [x] **The `Task` tool & `allowedTools`** — `Task` spawns subagents; coordinator's `allowedTools`
      must include `"Task"`.
- [x] **`AgentDefinition`** — description + system prompt + tool restrictions per subagent type.
- [x] **Parallel subagent spawning** — multiple `Task` calls in ONE response (not across turns).
- [x] **Goal-based vs procedural coordinator prompts** — specify goals/quality criteria, not step-by-step.
- [x] **Programmatic enforcement vs prompt guidance** — deterministic gates/hooks vs probabilistic
      prompt instructions; prompts have non-zero failure rate.
- [x] **Prerequisite gates** — blocking downstream tools until a prerequisite returns (e.g. block
      `process_refund` until verified customer ID).
- [x] **Structured handoff protocols** — customer ID + root cause + amount + recommended action for
      humans who can't see the transcript.
- [x] **Hooks — `PostToolUse`** — intercept/transform tool results before the model sees them (data
      normalization: Unix vs ISO 8601 vs status codes).
- [x] **Hooks — tool-call interception** — block policy violations (refund > $500) and redirect to escalation.
- [x] **Hooks vs prompts for compliance** — when guaranteed compliance is required, choose hooks.
- [x] **Task decomposition strategies** — prompt chaining (fixed sequential) vs dynamic/adaptive
      decomposition; per-file + cross-file passes; mapping structure before planning open-ended work.
- [x] **Session resumption** — `--resume <session-name>` for named sessions.
- [x] **`fork_session`** — branch from a shared baseline to explore divergent approaches.
- [x] **Resume vs fresh-with-summary** — resume when context mostly valid; start fresh with injected
      summary when prior tool results are stale; inform resumed sessions which files changed.

## §2 — Tool Design & MCP Integration 🟡 (18%)

- [x] **Tool descriptions as the selection mechanism** — minimal descriptions → unreliable selection
      among similar tools.
- [x] **What a good description contains** — input formats, example queries, edge cases, boundaries,
      "use this vs that."
- [x] **Overlapping-tool misrouting** — `analyze_content` vs `analyze_document`; fix by renaming +
      specializing (`extract_web_results`) or splitting generic tools.
- [x] **System-prompt keyword sensitivity** — wording that creates unintended tool associations and
      overrides good descriptions.
- [x] **MCP `isError` flag** — communicating tool failures back to the agent.
- [x] **Error taxonomy** — transient vs validation vs business vs permission; retryable vs non-retryable.
- [x] **Structured error metadata** — `errorCategory`, `isRetryable`, human-readable text,
      `retriable:false` + customer-friendly message for business rules.
- [x] **Access failure vs valid empty result** — retry decision vs successful query with no matches.
- [x] **Why generic errors are bad** — "operation failed" prevents informed recovery.
- [x] **Too-many-tools degradation** — 18 vs 4–5 tools hurts selection reliability.
- [x] **Cross-specialization misuse** — agents with off-role tools misuse them (synthesis agent doing web search).
- [x] **Scoped tool access + scoped cross-role tools** — role-only tools + one high-frequency
      exception (`verify_fact`).
- [x] **`tool_choice` options** — `"auto"` (text allowed) / `"any"` (must call some tool) / forced
      `{"type":"tool","name":"..."}`.
- [x] **MCP server scoping** — project `.mcp.json` (shared) vs user `~/.claude.json` (personal/experimental).
- [x] **Env var expansion** — `${GITHUB_TOKEN}` in `.mcp.json` keeps secrets out of git.
- [x] **Simultaneous multi-server availability** — all configured servers' tools discovered at connection time.
- [x] **MCP resources** — content catalogs (issue summaries, doc hierarchies, DB schemas) to reduce
      exploratory tool calls. Resources = content/read; tools = actions.
- [x] **Community vs custom MCP servers** — community (Jira) for standard integrations; custom for
      team-specific workflows.
- [x] **Built-in tools** — Grep (content) vs Glob (paths) vs Read/Write (full) vs Edit (unique anchor)
      vs Bash; Edit → Read+Write fallback; incremental codebase exploration.

## §3 — Claude Code Configuration & Workflows 🟠 (20%)

- [x] **CLAUDE.md hierarchy** — user (`~/.claude/CLAUDE.md`) vs project (`.claude/CLAUDE.md` or root)
      vs directory; user-level is NOT shared via git.
- [x] **`@import` syntax** — modular CLAUDE.md referencing external standards files.
- [x] **`.claude/rules/`** — topic-specific rule files as an alternative to a monolithic CLAUDE.md.
- [x] **Config hierarchy diagnosis** — teammate missing instructions because they're user-level not project-level.
- [x] **`/memory` command** — verify which memory files are loaded; diagnose inconsistency.
- [x] **Custom slash commands** — `.claude/commands/` (shared) vs `~/.claude/commands/` (personal).
- [x] **Skills & SKILL.md frontmatter** — `context: fork`, `allowed-tools`, `argument-hint`.
- [x] **`context: fork`** — isolate verbose/exploratory skill output from the main conversation.
- [x] **Skills vs CLAUDE.md** — on-demand task workflows vs always-loaded universal standards.
- [x] **Path-specific rules** — `.claude/rules/` with YAML `paths:` globs; load only on matching files.
- [x] **Glob rules vs directory CLAUDE.md** — for conventions spanning many directories (all test files).
- [x] **Plan mode vs direct execution** — complex/architectural/multi-file/multiple-approaches vs
      simple well-scoped single change.
- [x] **Explore subagent** — isolate verbose discovery, return summaries, preserve main context.
- [x] **Iterative refinement techniques** — concrete input/output examples; test-driven iteration;
      interview pattern; interacting (one message) vs independent (sequential) fixes.
- [x] **CI/CD: `-p`/`--print`** — non-interactive mode (prevents hangs).
- [x] **CI/CD: `--output-format json` + `--json-schema`** — machine-parseable findings for PR comments.
- [x] **CLAUDE.md as CI context** — testing standards, fixtures, review criteria for CI-invoked Claude.
- [x] **Session context isolation in CI** — a fresh instance reviews code better than the session that wrote it.
- [x] **Re-run hygiene** — pass prior findings so re-reviews report only new/unaddressed issues; pass
      existing tests to avoid duplicate test generation.

## §4 — Prompt Engineering & Structured Output 🟠 (20%)

- [x] **Explicit criteria vs vague instructions** — categorical criteria beat "be conservative / only
      high-confidence."
- [x] **False positives & developer trust** — noisy categories poison trust in accurate ones;
      temporarily disable while fixing.
- [x] **Severity definitions** — concrete code examples per severity level for consistent classification.
- [x] **Few-shot prompting — core** — most effective when detailed instructions still vary; 2–4
      targeted examples for ambiguous cases.
- [x] **Few-shot — reasoning & generalization** — show *why* one choice over alternatives; generalize
      to novel patterns, not just listed cases.
- [x] **Few-shot — extraction** — reduce hallucination across varied document structures (citations vs
      bibliographies, tables vs narrative).
- [x] **tool_use + JSON schema** — most reliable structured output; eliminates syntax errors, NOT
      semantic errors.
- [x] **`tool_choice` for output** — `"any"` when doc type unknown; forced tool to run a specific
      extraction first.
- [x] **Schema design** — required vs optional, nullable fields to prevent fabrication, enum +
      `"other"`+detail, `"unclear"` value.
- [x] **Format normalization in prompts** — alongside the strict schema for inconsistent source formatting.
- [x] **Validation + retry-with-error-feedback** — resend doc + failed extraction + specific error.
- [x] **Limits of retry** — useless when info is absent from the source (vs format/structural errors).
- [x] **Semantic self-validation** — `calculated_total` vs `stated_total`, `conflict_detected`,
      `detected_pattern` for false-positive analysis.
- [x] **Message Batches API** — 50% cheaper, ≤24h, no SLA, `custom_id` correlation, no multi-turn
      tool calling in one request.
- [x] **Batch appropriateness** — overnight/weekly (yes) vs blocking pre-merge (no); SLA cadence math;
      resubmit failed `custom_id`s; sample-first prompt refinement.
- [x] **Multi-instance review** — independent instance > self-review/extended thinking (generator
      retains reasoning).
- [x] **Multi-pass review** — per-file local + cross-file integration passes to avoid attention dilution.
- [x] **Confidence per finding** — self-reported confidence alongside findings for calibrated routing.

## §5 — Context Management & Reliability 🟡 (15%)

- [ ] **Progressive summarization risk** — losing numbers/dates/percentages/customer expectations.
- [ ] **"Case facts" block** — persistent transactional facts injected every prompt, outside summarized history.
- [ ] **Lost-in-the-middle** — models favor start/end; put key summaries first, use section headers.
- [ ] **Tool-output token bloat** — trim verbose outputs to relevant fields before accumulation.
- [ ] **Structured upstream output** — key facts + citations + relevance scores instead of verbose
      reasoning when downstream budgets are tight.
- [ ] **Escalation triggers** — explicit human request, policy gap/silence, inability to progress.
- [ ] **Escalate-immediately vs offer-to-resolve** — honor explicit human requests at once.
- [ ] **Unreliable escalation signals** — sentiment and self-reported confidence don't track complexity.
- [ ] **Multiple matches → clarify** — request another identifier, don't pick heuristically.
- [ ] **Error propagation (multi-agent)** — structured context (type, attempted, partial, alternatives)
      for coordinator recovery.
- [ ] **Anti-patterns in propagation** — generic statuses, silent suppression (empty-as-success),
      whole-workflow termination on one failure.
- [ ] **Local recovery first** — subagents handle transient failures locally; propagate only unrecoverable + partials.
- [ ] **Coverage annotations** — synthesis marks well-supported vs gap areas.
- [ ] **Context degradation in long sessions** — model cites "typical patterns" instead of specific
      discovered classes.
- [ ] **Scratchpad files** — persist key findings across context boundaries.
- [ ] **Subagent delegation for discovery** — isolate verbose exploration; main agent coordinates.
- [ ] **Crash recovery via manifests** — structured state exports loaded on resume.
- [ ] **`/compact`** — reduce context during extended exploration.
- [ ] **Human review & confidence calibration** — aggregate accuracy hides per-type/field weakness;
      field-level confidence calibrated on labeled validation sets.
- [ ] **Stratified sampling** — measure error rates in high-confidence extractions; detect novel patterns.
- [ ] **Accuracy segmentation** — validate by document type and field before automating.
- [ ] **Information provenance** — claim→source mappings preserved through summarization.
- [ ] **Conflicting credible sources** — annotate both with attribution, don't pick one.
- [ ] **Temporal data** — require publication/collection dates so time differences aren't read as conflicts.
- [ ] **Content-type rendering** — financials as tables, news as prose, technical as lists (not uniform).

## §6 — Technologies & Concepts glossary (Appendix) ⚪

Write a one-liner definition + "what it's for" for each. These are the exact terms the Appendix says
may appear.

- [ ] **Claude Agent SDK** — agent definitions, agentic loops, `stop_reason`, hooks, `Task` spawning, `allowedTools`.
- [ ] **MCP** — servers, tools, resources, `isError`, descriptions, distribution, `.mcp.json`, env expansion.
- [ ] **Claude Code** — CLAUDE.md hierarchy, `.claude/rules/`, `.claude/commands/`, `.claude/skills/`,
      plan mode, direct execution, `/memory`, `/compact`, `--resume`, `fork_session`, Explore subagent.
- [ ] **Claude Code CLI** — `-p`/`--print`, `--output-format json`, `--json-schema`.
- [ ] **Claude API** — `tool_use` + JSON schemas, `tool_choice`, `stop_reason` values, `max_tokens`, system prompts.
- [ ] **Message Batches API** — 50% savings, ≤24h, `custom_id`, polling, no multi-turn tool calling.
- [ ] **JSON Schema** — required/optional, enum, nullable, `"other"`+detail, strict mode.
- [ ] **Pydantic** — schema validation, semantic validation errors, validation-retry loops.
- [ ] **Built-in tools** — Read, Write, Edit, Bash, Grep, Glob purposes & selection criteria.
- [ ] **Few-shot prompting** — targeted examples, format demonstration, generalization.
- [ ] **Prompt chaining** — sequential decomposition into focused passes.
- [ ] **Context window management** — token budgets, progressive summarization, lost-in-the-middle,
      context extraction, scratchpads.
- [ ] **Session management** — resumption, `fork_session`, named sessions, session context isolation.
- [ ] **Confidence scoring** — field-level confidence, calibration with labeled sets, stratified sampling.

---

## ⛔ Out-of-scope — do NOT write notes on these (not tested)

Skip to save time. If an answer option relies on one of these as the "fix," it's almost certainly a distractor.

- Fine-tuning / training custom models
- API authentication, billing, account management
- Deep language/framework implementation (beyond tool/schema config)
- Deploying/hosting MCP servers (infra, networking, containers)
- Model internals, training process, weights
- Constitutional AI, RLHF, safety training
- Embeddings / vector DB implementation
- Computer use (browser/desktop automation)
- Vision / image analysis
- Streaming API / SSE implementation
- Rate limits, quotas, pricing math
- OAuth, key rotation, auth protocols
- Specific cloud configs (AWS/GCP/Azure)
- Benchmarking / model comparison metrics
- Prompt-caching implementation details (just know it exists)
- Tokenization specifics

---

## Progress

- [ ] §1 Agentic Architecture notes complete (24 topics)
- [ ] §2 Tool Design & MCP notes complete (19 topics)
- [ ] §3 Claude Code Config notes complete (19 topics)
- [ ] §4 Prompt Engineering & Structured Output notes complete (19 topics)
- [ ] §5 Context & Reliability notes complete (25 topics)
- [ ] §6 Glossary complete (14 terms)
- [ ] Can recite the key tradeoff for every 🔴/🟠 topic from memory
