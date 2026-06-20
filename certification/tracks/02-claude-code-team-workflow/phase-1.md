# Project 02 · Phase 1 — Standards & context ⭐

> **Companion to:** [`overview.md`](overview.md). Phases: [1](phase-1.md) · [2](phase-2.md) ·
> [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). Build it yourself; the snippets are a reference.

**Phase 1 covers build steps 1–2** (Domains **3.1** CLAUDE.md hierarchy, **3.3** path-specific rules).
This is the heart of Domain 3 (20% of the exam): *where config lives* and *which mechanism applies
automatically*.

**Milestone:** a teammate cloning the repo gets the project standards (not your personal ones), and a
glob rule fires **only** on the files it targets — wherever they live in the tree.

**Phase 1 Definition of done**
- [ ] Project vs user CLAUDE.md behavior confirmed (teammate gets project, not user).
- [ ] `@import` pulls package standards; `/memory` shows loaded files.
- [ ] `.claude/rules/` glob rule loads only on matching files.

What Phase 1 leaves out: commands/skills (Phase 2), MCP (Phase 3), plan mode (Phase 4).

---

## 0. Mental model — what loads, when, and from where

Two independent axes decide whether an instruction reaches Claude:

```
  SCOPE (where it lives) ───────────────┐
    ~/.claude/CLAUDE.md   user    → you only, NOT shared (not in git)
    ./CLAUDE.md or .claude/CLAUDE.md  project → everyone on clone (in git)
    sub/dir/CLAUDE.md     directory → only when working in that subtree

  LOAD TRIGGER (when it applies) ────────┐
    CLAUDE.md            ALWAYS loaded  → universal standards
    .claude/rules/*.md   CONDITIONAL    → only when editing files matching its paths: glob
```

The classic exam bug lives on the **scope** axis: a teammate "isn't getting your conventions" almost
always means they were written to **user** scope (`~/.claude/CLAUDE.md`), which isn't shared, instead
of **project** scope. The Phase-1 skill is choosing the right cell in this grid for each instruction.

---

## 1. Step 1 — CLAUDE.md hierarchy (Domain 3.1)

```
repo/
  CLAUDE.md                      # project, shared: universal standards for everyone
  .claude/
    rules/
      testing.md                 # split-out topic (Step 2)
      api-conventions.md
  packages/
    api/
      CLAUDE.md                  # directory-scoped: applies under packages/api/
```

- **Project** `CLAUDE.md` (root or `.claude/CLAUDE.md`) — universal coding/testing standards, **shared
  via git**, applies to everyone.
- **User** `~/.claude/CLAUDE.md` — a personal preference (e.g. "explain your reasoning tersely").
  Confirm teammates do **not** inherit it.
- **`@import`** to pull a package-specific standards file into a package's CLAUDE.md:
  ```markdown
  # packages/api/CLAUDE.md
  @import ../../.claude/rules/api-conventions.md
  ```
- Split a large CLAUDE.md into **`.claude/rules/`** topic files for modularity.
- Run **`/memory`** to see exactly which memory files are loaded right now.

> Decision rule: **shared → project scope; personal → user scope.** CLAUDE.md = always-loaded
> universal standards.

## 2. Step 2 — Path-specific rules with glob frontmatter (Domain 3.3) ⭐

```yaml
# .claude/rules/testing.md
---
paths: ["**/*.test.tsx", "**/*.test.ts"]
---
# Testing conventions that apply to every test file, wherever it lives
- Use the project's `render()` helper, never raw `@testing-library` render.
- One assertion theme per `it()`.
```

Add a second rule with `paths: ["src/api/**/*"]`. The rule's body loads **only** when you edit a file
matching its glob — so it costs zero tokens the rest of the time.

> **Exam point (Q6):** for conventions on files **spread across directories** (all `*.test.tsx`
> everywhere), glob `paths:` rules beat the alternatives:
> - a **monolithic root CLAUDE.md** — always-on, relies on the model *inferring* when it applies, wastes context;
> - a **per-directory CLAUDE.md** — directory-bound, so it misses test files scattered across the tree;
> - a **skill** — manual/on-demand, not automatic.

---

## 3. Run & observe (no API credits needed for most of this)

- **Scope test:** put a distinctive line in project `CLAUDE.md` and a different one in
  `~/.claude/CLAUDE.md`. Run `/memory` — both show for you. Then simulate a teammate (fresh clone /
  another machine / temporarily move your user file) and confirm only the **project** line is present.
- **`@import` test:** `/memory` lists the imported file as loaded when you're in that package.
- **Glob test:** open a `*.test.tsx` file and confirm the testing rule is active; open a
  non-matching file (e.g. a `.css`) and confirm it is **not**. Edit a `src/api/**` file for the API rule.

---

## 4. Exam mapping

- **Right config location** (EXAM-PREP §4.12): shared → `.claude/` project scope; personal → user
  scope; conventions for files **spread across directories** → `.claude/rules/` with glob `paths:`
  frontmatter (Q6 → A).
- **The teammate bug** (§3.1): missing instructions ⇒ they're in user scope, not project.
- CLAUDE.md = always-loaded; rules/ = conditional-by-path; `@import` = modular composition; `/memory`
  = the debug tool that shows what's actually loaded.

## 5. Close out the phase

- [ ] Tick the three Phase 1 boxes in [`overview.md`](overview.md).
- [ ] Notes one-liner: *"Shared→project, personal→user; CLAUDE.md always-on, rules/ glob = conditional
  by path (beats per-dir + monolithic for scattered files); `/memory` shows what loaded."*
- [ ] Commit; run `/log`.

### What Phase 2 will add (preview)
Move from *standards that apply automatically* to *workflows you invoke*: a project `/review` slash
command (shared via git) and a `.claude/skills/` skill with `context: fork`, `allowed-tools`, and
`argument-hint`.
