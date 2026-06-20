# Project 06 · Phase 5 — Write up the answers ⭐

> **Companion to:** [`overview.md`](overview.md). Phases: [1](phase-1.md) · [2](phase-2.md) ·
> [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). **No config in this phase.**

This is the **exam payload** for Scenario 4 — it spans Domains 2, 3, and 1. Everything you practiced was
so you can answer these five cold.

**Phase 5 Definition of done**
- [ ] All five questions answered **in your own words** and added to your notes.

> **How to use this file:** write your own answer first, then read the reference and check the gap.

---

## Q1. Grep vs Glob — when each, with an example?

**Reference answer.** **Grep searches file *contents*; Glob searches file *paths/names*.** Use **Grep**
when you're looking for text *inside* files — who calls `process_refund`, where an error string is
raised, which files import a module. Use **Glob** when you're selecting files by a name/path pattern —
`**/*.test.tsx` to find all test files, `**/*.proto` to find schema files. Rule of thumb: "what's *in*
the code?" → Grep; "which *files*?" → Glob.

*Heuristic:* EXAM-PREP §2.5.

---

## Q2. Edit failed on a non-unique match — what's the reliable fallback?

**Reference answer.** **Read + Write.** The Edit tool needs a **unique** text anchor to know exactly
where to change; when the target text appears more than once (and even surrounding context repeats), it
can't pinpoint the spot. The reliable fallback is to **read the whole file, make the change at the right
position, and write the file back** — Read+Write doesn't depend on uniqueness. (Adding more surrounding
context to make the anchor unique is the first thing to try; Read+Write is the fallback when no unique
anchor exists.)

*Heuristic:* EXAM-PREP §2.5 (Edit → Read+Write fallback).

---

## Q3. A long session starts citing "typical patterns" — what's happening and which techniques fix it?

**Reference answer.** It's **context degradation**: over a long session the model loses its grip on the
specific classes/files it found earlier and falls back to generic "typical patterns" — the tell-tale
symptom. The fix is to stop relying on the conversation as memory and **externalize state**:
- **Scratchpad files** — write key findings to a file and re-read them.
- **Subagent delegation** — push verbose lookups into subagents' own contexts.
- **Summarize-before-next-phase** — carry a condensed summary forward, not the whole transcript.
- **`/compact`** — shrink a context full of verbose discovery.
- **Manifests** — export structured state for crash recovery/resume.

A bigger context window does **not** fix this — externalized, structured state does.

*Heuristic:* EXAM-PREP §5.4.

---

## Q4. When do you resume a session vs start fresh with a summary?

**Reference answer.** **Resume** (`--resume <name>`) when the prior context is **mostly still valid** —
you're continuing the same investigation and the earlier reads/findings still hold. **Start fresh with
an injected structured summary** when the prior **tool results are stale** — the code has changed enough
that old file reads would mislead the model. When you do resume, **tell the session exactly which files
changed** so it does targeted re-analysis rather than re-exploring everything.

*Heuristic:* EXAM-PREP §1.7.

---

## Q5. What is `fork_session` for, and how does it differ from `--resume`?

**Reference answer.** **`fork_session` branches from a shared baseline** so you can explore **multiple
approaches independently** — e.g. fork a codebase-analysis baseline into two refactors or two testing
strategies and develop each without one contaminating the other. **`--resume` continues a single named
session** along the same line of work. In short: `--resume` = *one line of work, picked up later*;
`fork_session` = *one baseline → several parallel lines of work*.

*Heuristic:* EXAM-PREP §1.7 (`fork_session` to branch; `--resume` to continue).

---

## Close out the project

- [ ] Write your own version of all five answers and paste them into your notes — *your wording*.
- [ ] Tick the Phase 5 box and the remaining boxes in [`overview.md`](overview.md).
- [ ] Commit and run `/log`.

> **Scenario 4 touches Domains 1, 2, and 3.** When you can answer all five from memory — and say why
> each wrong option is wrong — this scenario's points are banked.
