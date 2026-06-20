# Project 02 · Phase 5 — Write up the answers ⭐

> **Companion to:** [`overview.md`](overview.md). Phases: [1](phase-1.md) · [2](phase-2.md) ·
> [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). **No config in this phase.**

This is the **exam payload** for Scenario 2. Everything you configured was so you can answer these four
questions *cold*, explaining the tradeoff — not reciting a definition. Domain 3 is 20% of the exam and
these are its core judgments.

**Phase 5 Definition of done**
- [ ] All four questions answered **in your own words** and added to your notes.

> **How to use this file:** write your own answer first (a few sentences, from memory), *then* read the
> reference and check what you missed. The gap is your revision list.

---

## Q1. A teammate isn't getting your conventions — what's the most likely misconfiguration?

**Reference answer.** The conventions were put in **user scope** (`~/.claude/CLAUDE.md`) instead of
**project scope**. User config is personal and **not shared via git**, so a teammate who clones the
repo never receives it. Fix: move the shared standards into the project's **`CLAUDE.md`** (root or
`.claude/CLAUDE.md`), which *is* committed and applies to everyone. Verify with **`/memory`**, which
shows exactly which memory files are loaded.

*Heuristic:* shared → project scope, personal → user scope (EXAM-PREP §3.1 / §4.12). This is the
canonical Domain 3 bug.

---

## Q2. Test files are everywhere; why is `.claude/rules/` glob scoping better than per-directory CLAUDE.md?

**Reference answer.** Because test files are **spread across directories**, and the three alternatives
each fail:
- **Per-directory CLAUDE.md** is **directory-bound** — you'd need a copy in every folder that contains
  tests, and you'd miss new locations.
- **A monolithic root CLAUDE.md** is **always loaded** and relies on the model *inferring* when the
  testing rules apply — it wastes context on every turn and applies the rules fuzzily.
- **A skill** is **manual/on-demand**, not automatic.

A **`.claude/rules/` file with a `paths: ["**/*.test.*"]` glob** loads its body **only when editing a
matching file, wherever it lives** — automatic, precise, and zero token cost the rest of the time.

*Heuristic:* glob `paths:` rules for conventions on files spread across the tree (EXAM-PREP §3.3 /
§4.12, Q6 → A).

---

## Q3. When do you reach for a skill vs CLAUDE.md vs a rules file?

**Reference answer.** Choose by **when the thing should apply**:
- **CLAUDE.md** — an **always-on** universal standard (loaded every turn).
- **`.claude/rules/`** — a **conditional-by-path** standard (loads only on files matching its glob).
- **Skill** — an **on-demand task workflow** you invoke (optionally isolated with `context: fork` and
  restricted with `allowed-tools`).

So: universal truth → CLAUDE.md; per-area truth → rules/; a *task you run* → skill. The mistake is
encoding an always-true standard as a skill (it won't fire automatically) or a one-off task as a
CLAUDE.md standard (it bloats every turn).

*Heuristic:* EXAM-PREP §3.2 — skill = on-demand; CLAUDE.md = always-on; rules/ = conditional-by-path.

---

## Q4. What does `context: fork` protect, and why restrict `allowed-tools` in a skill?

**Reference answer.**
- **`context: fork`** runs the skill in an **isolated subagent context**, so its (often verbose) output
  doesn't **pollute the main conversation** or burn the main thread's token budget — the skill returns
  a **summary** instead of dumping everything inline. It protects the *main context's* focus and cost.
- **`allowed-tools`** applies **least privilege** for the duration of the skill: a read-only analyzer
  restricted to `[Read, Grep, Glob]` **can't accidentally Write or run Bash**, so an exploratory skill
  can't take destructive or unintended actions.

Together they make a skill safe to run on autopilot: isolated (won't derail the conversation) and
scoped (can't do damage).

*Heuristic:* EXAM-PREP §3.2 — `context: fork` for isolation; `allowed-tools` for least privilege.

---

## Close out the project

- [ ] Write your own version of all four answers and paste them into your notes — *your wording*.
- [ ] Tick the Phase 5 box and the remaining boxes in [`overview.md`](overview.md).
- [ ] Commit and run `/log`.

> **Domain 3 is 20% of the exam and is almost entirely "where does this config live / which mechanism
> applies."** When you can answer all four from memory — and say why each wrong option is wrong — this
> scenario's points are banked.
