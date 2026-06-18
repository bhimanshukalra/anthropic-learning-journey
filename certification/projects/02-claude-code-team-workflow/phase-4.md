# Project 02 · Phase 4 — Plan mode vs direct execution (judgment) ⭐

> **Companion to:** [`overview.md`](overview.md). Phases: [1](phase-1.md) · [2](phase-2.md) ·
> [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). Build it yourself; the snippets are a reference.

**Phase 4 covers build step 6** (Domain **3.4** — plan mode vs direct execution). Phases 1–3 were
about *configuring* things; this is a **judgment** phase — choosing the execution mode from the
complexity that's *already stated*, not by trial and error.

**Milestone:** you pick (and can justify) the correct mode for all three tasks, and the Explore
subagent returns a summary rather than flooding the main context.

**Phase 4 Definition of done**
- [ ] You can justify plan vs direct for all three tasks.
- [ ] Explore subagent used for verbose discovery; returns a summary, not a raw flood.

---

## 0. Mental model — match the mode to the *stated* complexity

```
  complexity already known to be HIGH ───────────► PLAN MODE
    (large-scale / multi-file / architectural / multiple valid approaches)
  well-scoped SINGLE change with a clear path ───► DIRECT EXECUTION
    (single-file bug with a stack trace, one validation conditional)
```

The trap the exam tests: **"start direct and switch to plan if it gets complex."** Wrong when the
complexity is *already* stated — you start in plan mode. The decision is made from what you already
know about the task, not discovered mid-flight.

---

## 1. Step 6 — Plan mode vs direct execution (Domain 3.4)

Run three tasks and consciously pick a mode:

| Task | Mode | Why |
|---|---|---|
| Single-file bug fix with a clear stack trace | **Direct** | well-scoped, one obvious path |
| Library migration across many files / monolith→microservices | **Plan** | large-scale, multi-file, architectural |
| New feature with multiple valid approaches | **Plan** | choose an approach before executing, then execute the plan directly |

Also use the **Explore subagent** for a verbose discovery phase (mapping an unfamiliar area): it does
the noisy reading in an isolated context and **returns a summary**, so the main conversation isn't
flooded — the same isolation idea as `context: fork` in Phase 2.

> **Exam point (Q5):** when complexity is *already stated* (e.g. "migrate 45 files",
> "monolith→microservices"), **start in plan mode**. Don't "start direct and switch later," and don't
> assume you already know the structure — explore first.

---

## 2. Run & observe

- For each of the three tasks, **state your mode choice and the one-line reason** before acting. Then
  run it and check the outcome matched the reason (e.g. the migration genuinely benefited from a plan;
  the single-file fix didn't need one).
- Run the **Explore subagent** on an unfamiliar part of the repo and observe that the main thread
  receives a concise summary, not the full file dump.
- Anti-pattern check: deliberately try "start direct" on the migration and notice where it goes wrong
  (no upfront plan → thrashing) — that's *why* plan mode is the right call when complexity is stated.

---

## 3. Exam mapping

- **Plan vs direct** (EXAM-PREP §4.11 / Q5): plan mode when complexity is already stated
  (large-scale/multi-file/architectural/multiple valid approaches); direct for well-scoped single
  changes. "Start direct, switch later" is wrong when complexity is known.
- **Explore subagent** isolates verbose discovery and returns a summary (Domain 3.4) — context
  hygiene, like `context: fork`.

## 4. Close out the phase

- [ ] Tick the two Phase 4 boxes in [`overview.md`](overview.md).
- [ ] Notes one-liner: *"Plan mode when complexity is stated (multi-file/architectural/multiple
  approaches); direct for well-scoped single changes; never 'start direct, switch later'; Explore
  subagent returns a summary."*
- [ ] Commit; run `/log`.

### What Phase 5 will add (preview)
No more configuration. Answer the four **"Be able to answer"** questions in your own words — the actual
exam payload for this scenario.
