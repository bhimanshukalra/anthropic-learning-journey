# Project 02 · Phase 3 — MCP integration

> **Companion to:** [`overview.md`](overview.md). Phases: [1](phase-1.md) · [2](phase-2.md) ·
> [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). Build it yourself; the snippets are a reference.

**Phase 3 covers build step 5** (Domain **2.4** — MCP configuration). Same scope hierarchy as Phases
1–2, applied to MCP servers: shared servers live in the repo, personal/experimental ones stay local,
and **both are available simultaneously**.

**Milestone:** a project `.mcp.json` server and a user-scope server are both live at once, secrets come
from environment variables (never the repo), and Claude prefers your MCP tool over a built-in.

**Phase 3 Definition of done**
- [ ] `.mcp.json` with env-var expansion + a user-scope server, both live at once.
- [ ] MCP tool description strong enough that Claude prefers it over a built-in.

---

## 0. Mental model — MCP config follows the same scope axis

```
  .mcp.json            project scope → shared with the team (in git)   ← secrets via ${ENV_VAR}
  ~/.claude.json       user scope    → personal/experimental, not shared
```

Just like CLAUDE.md and commands, MCP server config has a **shared (project)** form and a **personal
(user)** form — and all configured servers' tools are available **at connection time, simultaneously**.
The secret-handling twist: project config is committed, so credentials must come from **environment
variables**, never hard-coded.

---

## 1. Step 5 — MCP server integration (Domain 2.4)

**Shared server — `.mcp.json` (committed):**
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    }
  }
}
```
`${GITHUB_TOKEN}` is **expanded from the environment** at launch — the token never lands in git.

**Personal server — `~/.claude.json` (user scope, not shared):**
```json
{
  "mcpServers": {
    "scratch": { "command": "python", "args": ["/Users/me/experiments/mcp_scratch.py"] }
  }
}
```

- Confirm **both servers' tools are available simultaneously** once connected.
- Write **rich tool descriptions** (purpose, inputs, example queries, when-to-use-vs-built-in) so
  Claude prefers the MCP tool over a built-in like **Grep** instead of defaulting to the built-in.
- Prefer a **community server** (e.g. Jira) for a standard integration; reserve **custom** servers for
  team-specific workflows.

> Decision rule: shared integration → **`.mcp.json`** (env-var secrets); personal/experimental →
> **`~/.claude.json`**. Community server for standard tools; custom only when nothing standard fits.

---

## 2. Run & observe

- **Both live at once:** with `GITHUB_TOKEN` set in your environment, start Claude Code and confirm
  the tools from *both* the project `github` server and the user `scratch` server are listed.
- **Secret hygiene:** confirm `.mcp.json` contains only `${GITHUB_TOKEN}`, not the literal token —
  `git grep` for the token value should return nothing.
- **Description wins:** ask something the MCP tool should handle and confirm Claude routes to it rather
  than to Grep/Read. If it defaults to a built-in, the **description** is too thin (the Domain 2 fix —
  same root cause as Project 01's tool-routing lesson).

---

## 3. Exam mapping

- **MCP config scope** (EXAM-PREP §2.4 / §4.12): `.mcp.json` (project, shared) vs `~/.claude.json`
  (user, personal); **`${ENV_VAR}` expansion** keeps secrets out of git; all servers' tools available
  simultaneously at connection time.
- **Descriptions drive adoption** — enhance MCP tool descriptions so the agent doesn't fall back to
  built-ins (Grep). Same principle as tool-selection in Domain 2.
- **Community vs custom** — prefer community servers for standard integrations.

## 4. Close out the phase

- [ ] Tick the two Phase 3 boxes in [`overview.md`](overview.md).
- [ ] Notes one-liner: *"`.mcp.json` (project/shared, `${ENV_VAR}` secrets) + `~/.claude.json`
  (user/personal), both live at once; rich descriptions so Claude prefers MCP over built-ins; community
  server for standard integrations."*
- [ ] Commit; run `/log`.

### What Phase 4 will add (preview)
The judgment phase: choosing **plan mode vs direct execution** from the *stated* complexity (single-file
fix → direct; multi-file migration / multiple valid approaches → plan), plus the **Explore subagent**
for verbose discovery that returns a summary instead of flooding context.
