# Project 06 · Phase 1 — Built-in tools & MCP augmentation ⭐

> **Companion to:** [`overview.md`](overview.md). Phases: [1](phase-1.md) · [2](phase-2.md) ·
> [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). Build it yourself; the snippets are a reference.

**Phase 1 covers build steps 1–2** (Domains **2.5** built-in tools, **2.4** MCP). The agent's job is
exploring an unfamiliar codebase — so it has to **pick the right search/edit tool deliberately** and
**augment** with MCP where a built-in falls short.

**Milestone:** for any task you can name the right built-in tool and why, fall back Edit→Read+Write
when there's no unique anchor, and an MCP **resource** gives the agent a catalog without exploratory calls.

**Phase 1 Definition of done**
- [ ] You can state, for any task, whether to use Grep / Glob / Read / Write / Edit and why.
- [ ] Edit→Read+Write fallback used when no unique anchor exists.
- [ ] Codebase understanding built incrementally (Grep entry → Read flows), not all-at-once.
- [ ] An MCP resource exposes a catalog that removes exploratory calls.

---

## 0. Mental model — match the tool to the question

```
  "where is this STRING / symbol used?"   → Grep   (searches file CONTENTS)
  "which FILES match this name pattern?"  → Glob   (searches PATHS/names)
  "show / replace a whole file"           → Read / Write
  "change this one spot"                  → Edit   (needs a UNIQUE anchor; else Read+Write)
```

And don't read everything up front — **build understanding incrementally**: Grep to a few entry points,
then Read to follow the imports/flows from there.

---

## 1. Step 1 — Built-in tool selection (Domain 2.5) ⭐

| Tool | Use for | Example |
|---|---|---|
| **Grep** | file **contents** | callers of `process_refund`, an error string, imports of a module |
| **Glob** | file **paths/names** | `**/*.test.tsx`, `**/*.proto` |
| **Read / Write** | full-file ops | read a config; rewrite a generated file |
| **Edit** | a targeted change at a **unique** text anchor | rename one call site |

- **Edit → Read+Write fallback:** when the target text isn't unique (the same block repeats), Edit
  can't pinpoint it — **read the whole file, change the right spot, write it back.**
- **Incremental:** Grep entry points → Read to follow imports/trace flows. Don't read every file upfront.
- **Trace across wrappers:** list all **exported names** first, then Grep each name to find real usage.

## 2. Step 2 — MCP augmentation (Domain 2.4)

When built-ins aren't enough, add an MCP server — and, crucially, expose a **resource**:

- **MCP tools** (actions) — e.g. a code-index server. Write **rich descriptions** so the agent prefers
  the capable MCP tool over a built-in like Grep *when appropriate*.
- **MCP resources** (content) — expose a **catalog** the agent can read directly: a module map, DB
  schema, or doc hierarchy. This gives visibility **without exploratory tool calls** — the agent reads
  the map instead of grepping around to build one.
- Prefer a **community** server for standard integrations; **custom** only for team-specific needs.

> Tools = *do something*; resources = *here's the content/catalog*. The resource is the exam's lever
> for cutting exploratory calls.

---

## 3. Run & observe

- **Tool choice:** for a few real questions ("who calls X?", "where are the proto files?", "change this
  one line"), state Grep/Glob/Edit/etc. and why — then run it and confirm the choice was right.
- **Fallback:** find a non-unique string, watch Edit refuse, then do Read+Write.
- **Incremental vs dump:** Grep to an entry point and Read outward; notice you understood the flow
  without reading the whole tree.
- **Resource:** point the agent at an MCP catalog resource and confirm it answers structure questions
  from the catalog instead of grepping.

---

## 4. Exam mapping

- **Built-in tools** (EXAM-PREP §2.5): Grep (content) · Glob (paths) · Read/Write (full) · Edit
  (unique anchor; fallback Read+Write) · build understanding incrementally.
- **MCP** (§2.4): rich descriptions so the agent prefers MCP over built-ins; **resources expose content
  catalogs to cut exploratory calls**; community vs custom.

## 5. Close out the phase

- [ ] Tick the four Phase 1 boxes in [`overview.md`](overview.md).
- [ ] Notes one-liner: *"Grep=content, Glob=paths, Edit needs a unique anchor (else Read+Write); build
  understanding incrementally; MCP resources = catalogs that remove exploratory calls."*
- [ ] Commit; run `/log`.

### What Phase 2 will add (preview)
The *workflow* around exploration: plan mode for an architectural task, and the Explore subagent to run
verbose discovery and hand back a summary — keeping the main context clean.
