# cert-06-developer-productivity-explorer MCP Server

MCP server for the [Project 06 — Developer Productivity / Codebase Exploration Agent](../../certification/projects/06-developer-productivity-explorer/overview.md) cert project. Built in Phase 1 (Step 2) to demonstrate Domain 2.4: MCP augmentation.

## Files

### `server.py`

Minimal stdio MCP server (JSON-RPC 2.0) that exposes two tools and one resource to Claude Code.

**Resource**

| URI | Description |
|---|---|
| `project://catalog` | Structured JSON map of every project phase — titles, domains, build steps, milestones, and definition-of-done checklists. Read this first to understand project structure without making any exploratory tool calls (Grep/Glob). |

**Tools**

| Tool | Description |
|---|---|
| `search_phases(query)` | Case-insensitive keyword search across all phase `.md` files. Returns matching lines with file attribution. Prefer this over raw Grep when searching within the structured phase documents. |
| `get_phase(phase_id)` | Returns the full text of a specific phase guide (e.g. `phase-3`). Use after `search_phases` identifies the right phase. |

Run the server:

```bash
python3 server.py
```

It is registered in `.claude/settings.json` and starts automatically when Claude Code opens the project.

---

### `catalog.json`

The data file backing the `project://catalog` resource. Contains a structured map of the five project phases with:

- `id` and `file` — phase identifier and corresponding markdown filename
- `title` — human-readable phase name
- `domains` — cert exam domains covered (e.g. `2.5 built-in tools`, `1.7 session management`)
- `steps` — build step numbers covered in that phase
- `milestone` — one-line outcome statement
- `definition_of_done` — checklist items required before moving to the next phase

Also includes the five `exam_questions` from the project overview.

Edit this file to keep the catalog in sync as the project evolves.
