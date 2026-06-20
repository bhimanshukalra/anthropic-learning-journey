# Project 06 · Phase 2 — Exploration workflow

> **Companion to:** [`overview.md`](overview.md). Phases: [1](phase-1.md) · [2](phase-2.md) ·
> [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). Build it yourself; the snippets are a reference.

**Phase 2 covers build step 3** (Domain **3.4** — plan mode + Explore subagent). Phase 1 gave the agent
the right *tools*; this phase is the *workflow* around them: plan an architectural task, and isolate
verbose discovery so it doesn't drown the main conversation.

**Milestone:** an architectural task runs in plan mode, and the Explore subagent returns a summary
instead of flooding the main context.

**Phase 2 Definition of done**
- [ ] Plan mode used for the architectural task; direct execution for the implementation.
- [ ] Explore subagent returns a summary; main context stays clean.

---

## 0. Mental model — plan first, explore in isolation

```
  complexity stated (architectural / multi-file / multiple approaches) → PLAN MODE
  verbose discovery (read many files to map an area)                   → EXPLORE subagent → summary
  then: execute the agreed plan directly
```

Two distinct levers: **plan mode** decides *what* to do before touching code; the **Explore subagent**
does the noisy reading in a side context and returns only a digest, so the main thread stays focused.

---

## 1. Step 3 — Plan mode + Explore subagent (Domain 3.4)

- **Plan mode** for an architectural task (e.g. "introduce a service boundary between billing and
  notifications"). Complexity is *already stated*, so start in plan mode — don't "start direct and
  switch if it gets complex."
- **Explore subagent** for the discovery phase: it reads broadly to map the area and returns a
  **summary**, keeping the main conversation's context clean (it doesn't dump every file it read).
- **Combine them:** plan to *investigate*, then **direct execution** to *implement* the agreed plan.

> Same isolation idea as a forked skill or a subagent's isolated context: push verbose work off to the
> side and bring back only the conclusion.

---

## 2. Run & observe

- **Plan mode:** give the architectural task in plan mode and confirm you get a plan to review *before*
  any edits. Try it in direct mode to feel why plan mode is better when complexity is known.
- **Explore summary:** run the Explore subagent on an unfamiliar area and confirm the main thread
  receives a concise map, not the raw file contents — your main context stays small.
- **Hand-off:** approve the plan, then implement directly and confirm the discovery digest was enough
  to proceed without re-reading everything.

---

## 3. Exam mapping

- **Plan vs direct** (EXAM-PREP §3.4 / §4.11): plan mode when complexity is already stated
  (architectural/multi-file/multiple approaches); direct for well-scoped changes. Don't "start direct,
  switch later."
- **Explore subagent** (§3.4): isolates verbose discovery and returns a summary — context hygiene.

## 4. Close out the phase

- [ ] Tick the two Phase 2 boxes in [`overview.md`](overview.md).
- [ ] Notes one-liner: *"Plan mode for stated-complexity/architectural tasks (then execute directly);
  Explore subagent runs verbose discovery and returns a summary to keep main context clean."*
- [ ] Commit; run `/log`.

### What Phase 3 will add (preview)
The heart of the project: keeping a **long** session coherent — scratchpad files, subagent delegation,
summarize-before-next-phase, `/compact`, and crash recovery via manifests.
