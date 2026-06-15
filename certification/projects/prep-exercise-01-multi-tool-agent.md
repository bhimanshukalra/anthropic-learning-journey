# Prep Exercise 1 — Build a Multi-Tool Agent with Escalation Logic

> **Source:** Official Claude Certified Architect – Foundations Exam Guide, *Preparation Exercises*, p. 33.
> This file records the exercise **verbatim**. Our deeper build guide is
> [`01-customer-support-agent.md`](01-customer-support-agent.md) (phased) with the Phase 1 walkthrough
> in [`01-customer-support-agent-phase-1.md`](01-customer-support-agent-phase-1.md).
> **Domains reinforced:** 1 (Agentic Architecture), 2 (Tool Design & MCP), 5 (Context & Reliability).

## Objective (verbatim)
Practice designing an agentic loop with tool integration, structured error handling, and escalation
patterns.

## Steps (verbatim)
1. **Define 3–4 MCP tools** with detailed descriptions that clearly differentiate each tool's purpose,
   expected inputs, and boundary conditions. Include at least two tools with similar functionality
   that require careful description to avoid selection confusion.
2. **Implement an agentic loop** that checks `stop_reason` to determine whether to continue tool
   execution or present the final response. Handle both `"tool_use"` and `"end_turn"` stop reasons
   correctly.
3. **Add structured error responses** to your tools: include `errorCategory`
   (transient/validation/permission), `isRetryable` boolean, and human-readable descriptions. Test
   that the agent handles each error type appropriately (retrying transient errors, explaining
   business errors to the user).
4. **Implement a programmatic hook** that intercepts tool calls to enforce a business rule (e.g.,
   blocking operations above a threshold amount), redirecting to an escalation workflow when triggered.
5. **Test with multi-concern messages** (e.g., requests involving multiple issues) and verify the agent
   decomposes the request, handles each concern, and synthesizes a unified response.

## How these official steps map to our build
| Official step | Our build (`01-customer-support-agent.md`) |
|---------------|--------------------------------------------|
| 1 — differentiate 3–4 tools, ≥2 similar | Phase 1, step 1 (`get_customer` vs `lookup_order`) |
| 2 — `stop_reason` agentic loop | Phase 1, step 2 |
| 3 — structured error responses | Phase 2, step 3 |
| 4 — interception hook + escalation | Phase 3, step 5 |
| 5 — multi-concern decomposition | Phase 4, step 7 |

> Our build adds material **beyond** this exercise (deterministic verification gate, `PostToolUse`
> normalization hook, escalation *calibration* with few-shot, persistent "case facts") drawn from the
> exam scenarios and domain weights.
