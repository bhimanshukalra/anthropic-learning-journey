# Project 04 — Multi-Agent Research Pipeline

> **Maps to:** Exam Scenario 3 + official Preparation Exercise 4
> **Domains:** 1 (Agentic Architecture, 27%) · 2 (Tool Design & MCP, 18%) · 5 (Context & Reliability, 15%)
> **Why it matters:** Domain 1 is the heaviest (27%) and multi-agent orchestration is its core. This
> project also drills error propagation and provenance — recurring exam themes.

## Objective
Build a coordinator that delegates to specialized subagents (web search, document analysis, synthesis,
report generation) to produce comprehensive, **cited** reports — and deliberately reproduce/fix the
classic failure modes the exam tests.

## Architecture: hub-and-spoke (Domain 1.2)
A **coordinator** owns all inter-agent communication, error handling, and routing. Subagents have
**isolated context** — they inherit nothing automatically.

## Build steps

### 1. Spawning + explicit context passing (Domain 1.3) ⭐
- Coordinator spawns subagents via the **`Task` tool**; its `allowedTools` must include **`"Task"`**.
- Pass each subagent **complete findings directly in its prompt** (e.g. web results + doc analysis
  into the synthesis prompt). Nothing is shared implicitly.
- Use **`AgentDefinition`** per subagent: description, system prompt, **restricted tool set**.
- Write coordinator prompts as **goals + quality criteria**, not step-by-step procedures, so
  subagents can adapt.

### 2. Parallel execution (Domain 1.3)
Emit **multiple `Task` calls in a single coordinator response** to run subagents in parallel; measure
the latency win vs sequential. (Parallel = one turn with many Task calls, not many turns.)

### 3. Reproduce + fix narrow decomposition (Domain 1.2) ⭐
Run "impact of AI on creative industries" and watch the coordinator over-narrow (e.g. only visual
arts). This is exam Q7: the **root cause is the coordinator's decomposition**, not the (correctly
working) search/analysis/synthesis agents. Fix by:
- Partitioning scope across subagents to **cover all sub-domains** and minimize duplication.
- An **iterative refinement loop**: synthesis flags coverage gaps → coordinator re-delegates targeted
  queries → re-synthesize until coverage is sufficient.

### 4. Scoped cross-role tool (Domain 2.3) ⭐
Give the synthesis agent a **scoped `verify_fact` tool** for the 85% simple fact-checks, while complex
verifications still route through the coordinator to the web-search agent. (Exam Q9 — least privilege:
don't hand synthesis the full web toolset, don't batch all verifications, don't speculatively cache.)

### 5. Structured error propagation (Domain 2.2 / 5.3) ⭐
Simulate a web-search **timeout**. The subagent must return **structured error context**: failure
type, attempted query, partial results, suggested alternatives, retryable flag. The coordinator then
recovers (retry/alternative/partial). Avoid all three anti-patterns:
- generic "search unavailable" (hides context),
- empty-result-as-success (silently suppresses),
- killing the whole workflow on one failure.
Subagents recover **transient** failures locally; propagate only the unrecoverable. (Exam Q8 → A.)

### 6. Provenance + conflict handling (Domain 5.6) ⭐
- Subagent outputs are **structured claim→source mappings**: claim, evidence excerpt, source
  URL/doc name, **publication date**. Synthesis must **preserve** attribution through merging.
- Conflicting credible statistics → **annotate both with sources**, don't pick one arbitrarily.
- Use dates so temporal differences aren't misread as contradictions.
- Structure the report to separate **well-established vs contested** findings; render financials as
  tables, news as prose — not one uniform format.
- Synthesis output carries **coverage annotations** (well-supported vs gap areas).

### 7. Context discipline across handoffs (Domain 5.1)
Upstream agents return **structured key facts + citations**, not verbose reasoning chains, when the
downstream agent's context budget is tight. Put key summaries at the **start** of aggregated inputs
(lost-in-the-middle) with explicit section headers.

## Definition of done (self-check)
- [ ] Coordinator spawns subagents via `Task` (with `"Task"` in `allowedTools`).
- [ ] Subagents get all needed context explicitly in their prompts.
- [ ] Parallel Task calls in one turn; measured latency improvement.
- [ ] Narrow-decomposition failure reproduced, then fixed with broad partition + refinement loop.
- [ ] Synthesis has a scoped `verify_fact` tool; complex cases still route via coordinator.
- [ ] Timeout returns structured error context; coordinator proceeds with partial results + coverage note.
- [ ] Final report preserves claim→source mappings, annotates conflicts with dates, separates
      established vs contested findings.

## Be able to answer
1. Why don't subagents inherit the coordinator's context, and what must you do about it?
2. Reports miss whole sub-topics though every subagent "succeeded" — what's the root cause and why?
3. Why give synthesis a scoped `verify_fact` tool instead of the full web toolset?
4. What four things belong in a structured subagent error, and which three error behaviors are anti-patterns?
5. How do you keep source attribution from being lost during synthesis?
