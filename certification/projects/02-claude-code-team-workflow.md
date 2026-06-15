# Project 02 — Claude Code Team Development Workflow

> **Maps to:** Exam Scenario 2 (Code Generation with Claude Code) + official Preparation Exercise 2
> **Domains:** 3 (Claude Code Config & Workflows, 20%) · 2 (Tool Design & MCP, 18%) · 5 (Context, 15%)
> **Why it matters:** Domain 3 is 20% of the exam and is almost entirely about *where config lives*
> and *which mechanism to use*. This project makes those choices muscle memory.

## Objective
Configure a realistic multi-package repo so Claude Code applies the right conventions automatically,
shares team tooling via version control, keeps personal tweaks private, and uses plan mode only when
it earns its keep. Use any repo with at least two distinct areas (e.g. `src/api/`, `src/components/`)
and test files spread alongside code (`Button.test.tsx` next to `Button.tsx`).

## Build steps

### 1. CLAUDE.md hierarchy (Domain 3.1)
- Project-level `CLAUDE.md` (or `.claude/CLAUDE.md`) with **universal** coding/testing standards —
  shared via git, applies to everyone.
- A user-level `~/.claude/CLAUDE.md` with a **personal** preference. Confirm teammates do **not**
  get it (this is the classic exam bug: "new teammate missing instructions" = they were put in user scope).
- Use **`@import`** to pull a package-specific standards file into a package's CLAUDE.md.
- Split a large CLAUDE.md into `.claude/rules/` topic files (`testing.md`, `api-conventions.md`).
- Run **`/memory`** to verify which memory files are actually loaded.

> Decision rule: **shared → project scope; personal → user scope.** CLAUDE.md = always-loaded
> universal standards.

### 2. Path-specific rules with glob frontmatter (Domain 3.3) ⭐
Create `.claude/rules/` files with YAML frontmatter:
```yaml
---
paths: ["**/*.test.tsx", "**/*.test.ts"]
---
# Testing conventions that apply to every test file, wherever it lives
```
Add another with `paths: ["src/api/**/*"]`. Edit a matching and a non-matching file and confirm the
rule loads **only** for matches.
> Exam point (Q6): for conventions on files **spread across directories**, glob `paths:` rules beat
> (a) a monolithic root CLAUDE.md relying on inference, (b) per-directory CLAUDE.md (directory-bound),
> and (c) skills (manual/on-demand, not automatic).

### 3. Custom slash command (Domain 3.2)
Create a project `/review` command in **`.claude/commands/`** that runs your team's review checklist.
Because it's in the repo, every dev gets it on clone/pull (exam Q4). Note `~/.claude/commands/` is
the personal-only equivalent.

### 4. A skill with frontmatter controls (Domain 3.2)
Create `.claude/skills/<name>/SKILL.md` with:
```yaml
---
context: fork          # run in an isolated subagent context — keep verbose output out of main chat
allowed-tools: [Read, Write]   # restrict tools during the skill (prevent destructive actions)
argument-hint: "<path to analyze>"   # prompt the dev when invoked without args
---
```
Use `context: fork` for a verbose codebase-analysis or brainstorming skill so its output doesn't
pollute the main conversation.
> Decision rule: **skill** = on-demand task workflow; **CLAUDE.md** = always-on standards;
> **rules/** = conditional-by-path standards.

### 5. MCP server integration (Domain 2.4)
- Configure a shared server in **`.mcp.json`** using **`${ENV_VAR}`** expansion for the token (no
  secrets in git).
- Add a personal/experimental server in **`~/.claude.json`**. Confirm both servers' tools are
  available **simultaneously**.
- Write rich MCP tool descriptions so Claude prefers the MCP tool over a built-in like Grep.
- Prefer a community server for a standard integration (Jira); reserve custom servers for
  team-specific workflows.

### 6. Plan mode vs direct execution (Domain 3.4) ⭐
Run three tasks and consciously pick a mode:
- Single-file bug fix with a clear stack trace → **direct execution**.
- Library migration affecting many files / monolith→microservices → **plan mode**.
- New feature with multiple valid approaches → **plan mode** (explore, then execute the plan directly).
Also use the **Explore subagent** for a verbose discovery phase and observe how it returns a summary
instead of flooding the main context.
> Exam point (Q5): when complexity is *already stated*, start in plan mode — don't "start direct and
> switch if it gets complex," and don't assume you already know the structure.

## Definition of done (self-check)
- [ ] Project vs user CLAUDE.md behavior confirmed (teammate gets project, not user).
- [ ] `@import` pulls package standards; `/memory` shows loaded files.
- [ ] `.claude/rules/` glob rule loads only on matching files.
- [ ] `/review` command in `.claude/commands/` available repo-wide.
- [ ] Skill runs with `context: fork`, `allowed-tools`, `argument-hint` working.
- [ ] `.mcp.json` with env-var expansion + a user-scope server, both live at once.
- [ ] You can justify plan vs direct for all three tasks.

## Be able to answer
1. A teammate isn't getting your conventions — what's the most likely misconfiguration?
2. Test files are everywhere; why is `.claude/rules/` glob scoping better than per-directory CLAUDE.md?
3. When do you reach for a skill vs CLAUDE.md vs a rules file?
4. What does `context: fork` protect, and why restrict `allowed-tools` in a skill?
