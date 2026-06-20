# Project 06 — Developer Productivity / Codebase Exploration Agent

> **Maps to:** Exam Scenario 4 (Developer Productivity with Claude)
> **Domains:** 2 (Tool Design & MCP, 18%) · 3 (Claude Code Config, 20%) · 1 (Agentic Architecture, 27%)
> **Why this is a dedicated project:** it's the one scenario with no official exercise, and it's where
> built-in tool selection (Domain 2.5), session management (1.7), and large-codebase context (5.4) get drilled.

## Objective
Build an agent that helps engineers explore unfamiliar/legacy codebases, generate boilerplate, and
automate repetitive tasks using built-in tools (Read, Write, Edit, Bash, Grep, Glob) plus MCP servers —
while staying coherent across a long session.

## Build steps (phased)

Build one phase at a time. Each phase ends at a **milestone** you can run and observe before moving on.
Tick the phase's Definition-of-done boxes before starting the next. Each phase has an in-depth companion
guide.

---

### Phase 1 — Built-in tools & MCP augmentation · [`phase-1.md`](phase-1.md)
*Steps 1–2 · Domains 2.5, 2.4 · Outcome: pick the right tool deliberately and augment with MCP.*

#### 1. Built-in tool selection (Domain 2.5) ⭐
Practice picking the right tool deliberately:
- **Grep** → search file *contents* (callers of a function, error strings, imports).
- **Glob** → find files by *path/name* pattern (`**/*.test.tsx`, `**/*.proto`).
- **Read/Write** → full-file operations.
- **Edit** → targeted change via a **unique** text anchor; when no unique anchor exists, **fall back
  to Read + Write**.
- **Build understanding incrementally:** Grep for entry points → Read to follow imports/trace flows.
  Don't read every file upfront.
- Trace a function across wrapper modules: first list all **exported names**, then Grep each name.

#### 2. MCP augmentation (Domain 2.4)
- Add an MCP server (e.g. a code-index or Jira server) and write **rich tool descriptions** so the
  agent prefers the capable MCP tool over a built-in like Grep when appropriate.
- Expose a **content catalog as an MCP resource** (e.g. module map, DB schema, doc hierarchy) so the
  agent gets visibility **without** exploratory tool calls.
- Prefer a community server for standard integrations; custom only for team-specific needs.

**Phase 1 milestone:** for any task you can name the right built-in tool and why, fall back Edit→Read+Write when there's no unique anchor, and an MCP resource gives the agent a catalog without exploratory calls.
- [ ] You can state, for any task, whether to use Grep / Glob / Read / Write / Edit and why.
- [ ] Edit→Read+Write fallback used when no unique anchor exists.
- [ ] Codebase understanding built incrementally (Grep entry → Read flows), not all-at-once.
- [ ] An MCP resource exposes a catalog that removes exploratory calls.

---

### Phase 2 — Exploration workflow · [`phase-2.md`](phase-2.md)
*Step 3 · Domain 3.4 · Outcome: plan the investigation, isolate verbose discovery.*

#### 3. Plan mode + Explore subagent (Domain 3.4)
- Use **plan mode** for an architectural task (e.g. "introduce a service boundary").
- Use the **Explore subagent** to run a verbose discovery phase and return a **summary**, keeping the
  main conversation's context clean. Combine: plan to investigate, direct execution to implement.

**Phase 2 milestone:** an architectural task is run in plan mode, and the Explore subagent returns a summary instead of flooding the main context.
- [ ] Plan mode used for the architectural task; direct execution for the implementation.
- [ ] Explore subagent returns a summary; main context stays clean.

---

### Phase 3 — Long-session context · [`phase-3.md`](phase-3.md)
*Step 4 · Domain 5.4 · Outcome: the agent stays coherent across a long investigation.*

#### 4. Large-codebase context management (Domain 5.4) ⭐
This is the heart of the project — make the agent survive a long session:
- **Scratchpad files:** have the agent record key findings to a file and re-read them later, to
  counteract context degradation (the tell-tale symptom: it starts citing "typical patterns" instead
  of the specific classes it found earlier).
- **Subagent delegation:** spawn subagents for narrow questions ("find all test files," "trace the
  refund-flow dependencies") while the main agent keeps high-level coordination.
- **Summarize-before-next-phase:** condense phase 1 findings and inject them into phase 2's initial context.
- **`/compact`** to reduce context when it fills with verbose discovery.
- **Crash recovery via manifests:** each agent exports structured state to a known location; on
  resume, the coordinator loads the manifest and injects it into prompts.

**Phase 3 milestone:** a long session stays coherent (no "typical patterns" drift) via scratchpad + delegation + `/compact`, and crash recovery via a manifest works on resume.
- [ ] Scratchpad + subagent delegation + `/compact` keep a long session coherent.
- [ ] Crash recovery via a manifest works on resume.

---

### Phase 4 — Sessions & iterative refinement · [`phase-4.md`](phase-4.md)
*Steps 5–6 · Domains 1.7, 3.5 · Outcome: continue/branch sessions correctly and refine deliberately.*

#### 5. Session management (Domain 1.7) ⭐
- **`--resume <session-name>`** to continue a named investigation across work sessions.
- **`fork_session`** to branch from a shared codebase-analysis baseline and explore two approaches
  (e.g. two refactors / two testing strategies) independently.
- **Resume vs fresh:** resume when prior context is mostly valid; **start fresh with an injected
  structured summary** when prior tool results are **stale**. Tell a resumed session exactly which
  files changed for targeted re-analysis instead of full re-exploration.

#### 6. Iterative refinement (Domain 3.5)
- Use the **interview pattern**: have Claude ask clarifying questions (cache invalidation, failure
  modes) before implementing in an unfamiliar area.
- Provide **concrete input/output examples** when prose is ambiguous.
- Fix **interacting** issues in one message; **independent** issues sequentially.

**Phase 4 milestone:** you resume a named session, fork to explore two approaches, pick resume-vs-fresh correctly, and use the interview pattern before implementing in an unfamiliar area.
- [ ] `--resume` and `fork_session` used correctly; you can pick resume vs fresh.
- [ ] Interview pattern used before implementing in an unfamiliar area.

---

### Phase 5 — Write up the answers · [`phase-5.md`](phase-5.md)
*Outcome: the actual exam payload — answer the five "Be able to answer" questions in writing.*
- [ ] All five questions answered in your own words (add to your notes).

## Be able to answer
1. Grep vs Glob — when each, with an example?
2. Edit failed on a non-unique match — what's the reliable fallback?
3. A long session starts citing "typical patterns" — what's happening and which techniques fix it?
4. When do you resume a session vs start fresh with a summary?
5. What is `fork_session` for, and how does it differ from `--resume`?
