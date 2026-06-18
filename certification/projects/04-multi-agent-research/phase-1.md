# Project 04 · Phase 1 — Coordinator & subagents ⭐

> **Companion to:** [`overview.md`](overview.md). Phases: [1](phase-1.md) · [2](phase-2.md) ·
> [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). Build it yourself; the snippets are a reference.

**Phase 1 covers build steps 1–2** (Domain **1.3** — spawning + parallel execution). This is the
hub-and-spoke core, and Domain 1 is the heaviest on the exam (27%).

**Milestone:** the coordinator spawns subagents via `Task`, each receives its context **explicitly**,
and **parallel** Task calls in one turn beat sequential on wall-clock.

**Phase 1 Definition of done**
- [ ] Coordinator spawns subagents via `Task` (with `"Task"` in `allowedTools`).
- [ ] Subagents get all needed context explicitly in their prompts.
- [ ] Parallel Task calls in one turn; measured latency improvement.

---

## 0. Mental model — hub-and-spoke, isolated spokes

```
                 ┌──────────────┐
                 │ COORDINATOR  │  owns routing, error handling, aggregation
                 └──────┬───────┘
        Task ┌──────────┼──────────┐ Task      ← all in ONE response = parallel
             ▼          ▼          ▼
        ┌────────┐ ┌────────┐ ┌──────────┐
        │ search │ │ doc    │ │ synthesis│   each: ISOLATED context, restricted tools
        └────────┘ └────────┘ └──────────┘
```

The one idea that drives everything: **subagents inherit nothing.** A subagent is a fresh context — it
doesn't see the conversation, the coordinator's reasoning, or sibling outputs. So **everything it needs
must be in the prompt the coordinator hands it.** Forgetting this is the #1 multi-agent bug.

---

## 1. Step 1 — Spawning + explicit context passing (Domain 1.3) ⭐

- The coordinator spawns subagents via the **`Task` tool**, so its **`allowedTools` must include
  `"Task"`** (a coordinator that can't call Task can't delegate).
- Pass each subagent **complete inputs in its prompt** — e.g. the synthesis agent's prompt contains the
  web results *and* the doc analysis, verbatim. Nothing is shared implicitly.
- Define each subagent with an **`AgentDefinition`**: `description`, a focused `system prompt`, and a
  **restricted tool set** (least privilege — the search agent doesn't need write tools).
- Write coordinator prompts as **goals + quality criteria**, not step-by-step procedures — so a
  subagent can adapt its approach rather than follow a brittle script.

```python
# sketch — coordinator delegating with explicit context
search = await Task(agent="web_search",
                    prompt=f"Goal: find sources on {subtopic}. Quality bar: ≥3 credible, dated sources.")
synthesis = await Task(agent="synthesis",
                       prompt=f"Synthesize a cited section.\nWEB RESULTS:\n{search}\nDOC ANALYSIS:\n{doc}")
```

## 2. Step 2 — Parallel execution (Domain 1.3)

**Parallel = multiple `Task` calls in a *single* coordinator response**, not many sequential turns.
Emit the independent subagents (search subtopic A, search subtopic B, doc analysis) together and let
them run concurrently; measure wall-clock vs doing them one per turn.

> Mnemonic: *one turn, many Tasks = parallel; many turns, one Task each = sequential.*

---

## 3. Run & observe

- **Isolation proof:** omit a needed fact from a subagent's prompt and watch it fail/guess — that's the
  isolated-context reality. Then add it explicitly and watch it succeed.
- **`allowedTools`:** remove `"Task"` from the coordinator and confirm it can no longer spawn.
- **Parallel win:** time the same 3 subagents as (a) 3 Task calls in one response vs (b) 3 sequential
  turns; confirm the parallel version is faster.

---

## 4. Exam mapping

- **Spawning** (EXAM-PREP §1.3): `Task` spawns subagents; coordinator needs `"Task"` in `allowedTools`;
  `AgentDefinition` = description + system prompt + tool restriction.
- **Isolated context** — pass everything explicitly in the prompt (subagents inherit nothing).
- **Goals not procedures** — coordinator prompts specify outcomes/quality, not steps.
- **Parallel** = multiple Task calls in one assistant turn.

## 5. Close out the phase

- [ ] Tick the three Phase 1 boxes in [`overview.md`](overview.md).
- [ ] Notes one-liner: *"Subagents inherit nothing → pass context explicitly; coordinator needs Task in
  allowedTools; AgentDefinition restricts tools; parallel = many Task calls in one turn."*
- [ ] Commit; run `/log`.

### What Phase 2 will add (preview)
The decomposition-quality failure mode: reproduce a coordinator that over-narrows the topic (reports
miss whole sub-areas though every subagent "succeeded"), then fix it with broad scope partitioning and
an iterative refinement loop.
