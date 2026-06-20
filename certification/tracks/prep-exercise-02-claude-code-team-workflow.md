# Prep Exercise 2 — Configure Claude Code for a Team Development Workflow

> **Source:** Official Claude Certified Architect – Foundations Exam Guide, *Preparation Exercises*, p. 34.
> This file records the exercise **verbatim**. Our deeper build guide is
> [`overview.md`](02-claude-code-team-workflow/overview.md).
> **Domains reinforced:** 3 (Claude Code Configuration & Workflows), 2 (Tool Design & MCP).

## Objective (verbatim)
Practice configuring CLAUDE.md hierarchies, custom slash commands, path-specific rules, and MCP server
integration for a multi-developer project.

## Steps (verbatim)
1. **Create a project-level CLAUDE.md** with universal coding standards and testing conventions. Verify
   that instructions placed at the project level are consistently applied across all team members.
2. **Create `.claude/rules/` files** with YAML frontmatter glob patterns for different code areas (e.g.,
   `paths: ["src/api/**/*"]` for API conventions, `paths: ["**/*.test.*"]` for testing conventions).
   Test that rules load only when editing matching files.
3. **Create a project-scoped skill** in `.claude/skills/` with `context: fork` and `allowed-tools`
   restrictions. Verify the skill runs in isolation without polluting the main conversation context.
4. **Configure an MCP server** in `.mcp.json` with environment variable expansion for credentials. Add
   a personal experimental MCP server in `~/.claude.json` and verify both are available simultaneously.
5. **Test plan mode versus direct execution** on tasks of varying complexity: a single-file bug fix, a
   multi-file library migration, and a new feature with multiple valid implementation approaches.
   Observe when plan mode provides value.

## How these official steps map to our build
| Official step | Our build (`overview.md`) |
|---------------|-----------------------------------------------|
| 1 — project-level CLAUDE.md | CLAUDE.md hierarchy (user/project/directory) |
| 2 — `.claude/rules/` glob scoping | Path-specific rule files |
| 3 — `context: fork` skill | Project-scoped skill with `allowed-tools` |
| 4 — `.mcp.json` + `~/.claude.json` | MCP config, env-var expansion, multi-server access |
| 5 — plan mode vs direct | Complexity-based plan-mode assessment |
