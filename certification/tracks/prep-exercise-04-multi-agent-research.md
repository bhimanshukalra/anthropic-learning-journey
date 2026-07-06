# Prep Exercise 4 — Design and Debug a Multi-Agent Research Pipeline

> **Source:** Official Claude Certified Architect – Foundations Exam Guide (v0.2, Jun 30 2026), *Preparation Exercises*, pp. 33–34. Content unchanged from v0.1.
> This file records the exercise **verbatim**. Our deeper build guide is
> [`overview.md`](04-multi-agent-research/overview.md).
> **Domains reinforced:** 1 (Agentic Architecture), 2 (Tool Design & MCP), 5 (Context & Reliability).

## Objective (verbatim)
Practice orchestrating subagents, managing context passing, implementing error propagation, and
handling synthesis with provenance tracking.

## Steps (verbatim)
1. **Build a coordinator agent** that delegates to at least two subagents (e.g., web search and
   document analysis). Ensure the coordinator's `allowedTools` includes `"Task"` and that each subagent
   receives its research findings directly in its prompt rather than relying on automatic context
   inheritance.
2. **Implement parallel subagent execution** by having the coordinator emit multiple `Task` tool calls
   in a single response. Measure the latency improvement compared to sequential execution.
3. **Design structured output for subagents** that separates content from metadata: each finding should
   include a claim, evidence excerpt, source URL/document name, and publication date. Verify that the
   synthesis subagent preserves source attribution when combining findings.
4. **Implement error propagation:** simulate a subagent timeout and verify the coordinator receives
   structured error context (failure type, attempted query, partial results). Test that the coordinator
   can proceed with partial results and annotate the final output with coverage gaps.
5. **Test with conflicting source data** (e.g., two credible sources with different statistics) and
   verify the synthesis output preserves both values with source attribution rather than arbitrarily
   selecting one, and structures the report to distinguish well-established from contested findings.

## How these official steps map to our build
| Official step | Our build (`overview.md`) |
|---------------|------------------------------------------|
| 1 — coordinator + `Task`, explicit context | Coordinator/subagent, explicit context passing |
| 2 — parallel `Task` calls | Parallel spawn, latency measurement |
| 3 — content/metadata separation | Provenance-bearing structured findings |
| 4 — error propagation | Structured error context, partial-result coverage gaps |
| 5 — conflicting sources | Conflict annotation, established vs contested |
