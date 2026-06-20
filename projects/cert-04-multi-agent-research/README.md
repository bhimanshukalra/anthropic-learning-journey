# Multi-Agent Research Pipeline

Implements [Prep Exercise 4](../../certification/tracks/prep-exercise-04-multi-agent-research.md) and
the full phased build from
[certification/tracks/04-multi-agent-research/overview.md](../../certification/tracks/04-multi-agent-research/overview.md).

A hub-and-spoke pipeline: a **coordinator** decomposes a research query into sub-topics, fans out a
**web_search subagent per topic in parallel**, retries transient failures, then **synthesizes** a
cited report that separates established findings from contested ones.

## Running (no API key — runs on stubs)

```bash
python3 main.py     # demo report + latency comparison
python3 test.py     # full pipeline test suite
```

## Project structure

| File | Role |
|------|------|
| `coordinator.py` | The brain: decompose → parallel research → synthesize, with refinement + error recovery |
| `subagent.py` | One isolated worker (`AgentDefinition` + `Subagent`); no implicit context |
| `mock_sources.py` | Fake "internet" — pure Python data, conflict + timeout fixtures |
| `main.py` | Wiring, demo run, and the `measure_latency` parallel-vs-sequential helper |
| `test.py` | Capability tests (latency, fan-out, decomposition, errors, provenance) |

---

## Phase walkthrough

### Phase 1 — Coordinator & subagents
`Coordinator.decompose()` turns one query into a search task per sub-topic, each carrying its
context **explicitly in the prompt** (subagents inherit nothing). `research()` runs all spawns
concurrently with `asyncio.gather` — the analogue of emitting multiple `Task` calls in one
coordinator turn. `measure_latency()` proves the win: with 5 topics at ~0.5s each, parallel
finishes in ~0.5s vs ~2.5s sequential — a **5× speedup**.

### Phase 2 — Decomposition quality
A narrow `scope` reproduces the over-narrowing failure (only `visual` covered, the rest reported as
`gaps`). The `refine=True` loop closes those gaps: `covered()` flags missing topics, the
coordinator re-delegates targeted searches, and re-synthesizes until coverage is complete.

### Phase 3 — Tools & error propagation
The synthesis agent gets a scoped `verify_fact` tool only (least privilege) — not the full search
toolset. A simulated timeout returns a **structured error envelope** (`failureType`,
`attemptedQuery`, `partialResults`, `isRetryable`) rather than a crash or a silent empty result.
The coordinator retries transient failures once, then proceeds with partial results and surfaces
the failed topics in `failed`/`gaps` — one failure never sinks the run.

### Phase 4 — Provenance & conflict handling
Every finding is a structured claim→source→date record. `synthesize()` preserves attribution
through merging and sorts findings into `established` (single agreed source) vs `contested`
(multiple disagreeing sources, **both kept with their citations** — never arbitrarily resolved).
Dates are retained so temporal differences aren't misread as contradictions.

---

## Phase 5 — Exam answers

### 1. Why don't subagents inherit the coordinator's context, and what must you do about it?

Each subagent runs in its own isolated context window — it is a separate invocation with its own
system prompt and message history, not a continuation of the coordinator's. This isolation is a
feature: it keeps each subagent's context lean and focused, and prevents one agent's noise from
polluting another's reasoning. The consequence is that anything a subagent needs to do its job
must be passed **explicitly in its prompt**. In this pipeline `decompose()` builds a complete,
self-contained prompt per topic, and the synthesis step receives the gathered findings directly
rather than assuming it can "see" what web_search saw.

### 2. Reports miss whole sub-topics though every subagent "succeeded" — what's the root cause and why?

The root cause is the **coordinator's decomposition**, not the subagents. Each web_search agent
correctly returns sources for the topic it was given — they all "succeed." But if the coordinator
only delegated `visual`, no agent was ever asked about music, film, writing, or games, so those
sub-topics are simply absent from the final report. The failure is upstream of the workers:
partitioning the scope too narrowly. The fix is broad partitioning plus an iterative refinement
loop that detects coverage gaps and re-delegates — which is exactly what `covered()` + the
`refine` loop do.

### 3. Why give synthesis a scoped `verify_fact` tool instead of the full web toolset?

Least privilege. The synthesis agent's job is to combine findings and do simple fact-checks — the
~85% of verifications that are quick lookups. Handing it the full web-search toolset gives it far
more capability than its role needs, which widens the blast radius of mistakes, makes its behavior
harder to reason about, and invites it to go off and re-research instead of synthesizing. A
narrow `verify_fact` tool covers the common case; the rare complex verification routes back
through the coordinator to the dedicated web_search agent. Scope the tool to the role.

### 4. What four things belong in a structured subagent error, and which three error behaviors are anti-patterns?

A structured error should carry: **failure type** (e.g. transient), the **attempted query**,
any **partial results** gathered before failing, and a **retryable flag** (here also
`suggestedAlternatives`). The three anti-patterns:
1. A generic "search unavailable" string that **hides the context** the coordinator needs to
   recover.
2. Returning an **empty result as success**, which silently suppresses the failure so no one
   retries or notes the gap.
3. **Killing the whole workflow** on a single subagent failure instead of isolating it and
   proceeding with partial results.
Subagents recover transient failures locally and only propagate the unrecoverable.

### 5. How do you keep source attribution from being lost during synthesis?

Make provenance part of the data structure, not free-form prose. Each subagent returns structured
claim→source→date records, and the synthesis step carries those fields through the merge rather
than collapsing claims into a summary that drops citations. Conflicts are preserved explicitly —
when two credible sources disagree, both are kept with their own source and date in the
`contested` bucket instead of one being arbitrarily chosen. Retaining dates also lets the reader
distinguish a genuine contradiction from a figure that simply changed over time.
