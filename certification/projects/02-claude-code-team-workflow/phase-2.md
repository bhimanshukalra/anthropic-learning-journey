# Project 02 · Phase 2 — Reusable team tooling

> **Companion to:** [`overview.md`](overview.md). Phases: [1](phase-1.md) · [2](phase-2.md) ·
> [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). Build it yourself; the snippets are a reference.

**Phase 2 covers build steps 3–4** (Domain **3.2** — commands & skills). Phase 1 was about standards
that load *automatically*; Phase 2 is about workflows you *invoke on demand*, shared with the team via
git, with the right isolation and tool limits.

**Milestone:** `/review` works for every dev on clone, and a forked skill runs with restricted tools
and keeps its verbose output out of the main conversation.

**Phase 2 Definition of done**
- [ ] `/review` command in `.claude/commands/` available repo-wide.
- [ ] Skill runs with `context: fork`, `allowed-tools`, `argument-hint` working.

---

## 0. Mental model — three mechanisms, picked by *when they apply*

| Mechanism | When it applies | Shared via | Use for |
|---|---|---|---|
| **CLAUDE.md** (Phase 1) | always loaded | project scope | universal standards |
| **`.claude/rules/`** (Phase 1) | conditionally, by path glob | project scope | per-area standards |
| **slash command** | when you type `/name` | `.claude/commands/` | a repeatable team workflow |
| **skill** | when invoked (or auto-matched) | `.claude/skills/` | an on-demand task, optionally isolated |

The Phase-2 judgment: a **command/skill** is for a *task you run*, not a *standard that's always true*.
Don't encode "always lint before commit" as a command (that's a CLAUDE.md standard); do encode "run our
multi-step review checklist" as a command.

---

## 1. Step 3 — Custom slash command (Domain 3.2)

```markdown
<!-- .claude/commands/review.md -->
Run our team code-review checklist on the current diff:
1. Tests cover the change and pass.
2. Public APIs have docstrings.
3. No secrets or debug logging left in.
Report findings grouped by severity.
```

- In **`.claude/commands/`** → committed, so **every dev gets `/review` on clone/pull** (exam Q4).
- `~/.claude/commands/` is the **personal-only** equivalent (not shared).

> Decision rule (same as Phase 1's scope axis): team workflow → **project** `.claude/commands/`;
> personal helper → **user** `~/.claude/commands/`.

## 2. Step 4 — A skill with frontmatter controls (Domain 3.2)

```yaml
# .claude/skills/analyze-module/SKILL.md
---
context: fork                       # isolated subagent context — keep verbose output out of main chat
allowed-tools: [Read, Grep, Glob]   # restrict tools during the skill (no Write/Bash → can't mutate)
argument-hint: "<path to analyze>"  # prompts the dev when invoked without args
---
Analyze the module at the given path: map its public surface, dependencies, and risks.
Return a concise summary.
```

- **`context: fork`** runs the skill in an **isolated subagent context** — a verbose
  codebase-analysis or brainstorming skill won't pollute (or blow the token budget of) the main chat;
  it returns a summary.
- **`allowed-tools`** applies **least privilege** during the skill — e.g. a read-only analyzer can't
  accidentally Write or run Bash.
- **`argument-hint`** prompts the dev for the expected argument when they invoke it bare.

> Decision rule: **skill** = on-demand task workflow; **CLAUDE.md** = always-on standards;
> **`rules/`** = conditional-by-path standards. Choose by *when it should apply*.

---

## 3. Run & observe

- **Command sharing:** commit `.claude/commands/review.md`, then from a fresh clone (or a teammate's
  machine) type `/review` and confirm it's available without any personal setup.
- **Skill isolation:** invoke the skill on a large module and confirm the verbose analysis runs in a
  fork and only a **summary** returns to the main conversation (the main context isn't flooded).
- **Tool restriction:** confirm the skill cannot Write/Bash while `allowed-tools` excludes them.
- **Arg hint:** invoke the skill with no argument and confirm it prompts you per `argument-hint`.

---

## 4. Exam mapping

- **Where a shared command lives** (Q4 → A): `.claude/commands/` (project scope), not `~/.claude/`.
- **`context: fork`** protects the main conversation context (isolation) and keeps verbose output/
  token cost out of the main thread.
- **`allowed-tools`** = least privilege; prevents a skill from taking destructive/unintended actions.
- Skill vs CLAUDE.md vs rules/ = on-demand task vs always-on standard vs conditional-by-path standard.

## 5. Close out the phase

- [ ] Tick the two Phase 2 boxes in [`overview.md`](overview.md).
- [ ] Notes one-liner: *"Commands/skills = invokable workflows (project scope to share); `context: fork`
  isolates verbose skills; `allowed-tools` = least privilege; pick command/skill vs CLAUDE.md/rules by
  on-demand vs always/conditional."*
- [ ] Commit; run `/log`.

### What Phase 3 will add (preview)
MCP integration: a shared `.mcp.json` server with `${ENV_VAR}` expansion (secrets out of git) plus a
personal `~/.claude.json` server, both available at once — and tool descriptions strong enough that
Claude prefers the MCP tool over a built-in.
