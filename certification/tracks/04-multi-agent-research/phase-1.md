# Project 04 · Phase 1 — Coordinator & subagents ⭐

> **Companion to:** [`overview.md`](overview.md). Phases: [0](phase-0.md) · [1](phase-1.md) ·
> [2](phase-2.md) · [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). Build it yourself; the
> snippets are a reference. **Assumes the Phase 0 skeleton exists and runs.**

**Phase 1 covers build steps 1–2** (Domain **1.3** — spawning + parallel execution). You'll grow the
Phase 0 stub into a real coordinator that spawns **multiple role-specialized subagents**, passes each
its context **explicitly**, and runs them **in parallel** — all observable **without API credits**
(stub mode with simulated latency).

**Milestone:** the coordinator spawns several subagents, feeds synthesis the upstream findings in its
prompt, and **parallel execution is measurably faster than sequential** — printed, no API key.

**Phase 1 Definition of done**
- [ ] Coordinator spawns subagents via `spawn()` (the `Task` stand-in); `AgentDefinition` per role with restricted tools.
- [ ] Subagents get all needed context explicitly in their prompts (synthesis sees the findings).
- [ ] Parallel run measurably beats sequential; you can show the numbers.

---

## 0. Mental model — hub-and-spoke, isolated spokes

```
                 ┌──────────────┐
                 │ COORDINATOR  │  decompose → spawn → aggregate
                 └──────┬───────┘
        spawn ┌─────────┼─────────┐ spawn      ← all awaited together = parallel
              ▼         ▼         ▼
        ┌────────┐ ┌────────┐ ┌──────────┐
        │search 1│ │search 2│ │  …       │   each: ISOLATED context, restricted tools
        └────────┘ └────────┘ └──────────┘
                          │ findings (passed EXPLICITLY)
                          ▼
                    ┌──────────┐
                    │ synthesis│   sees ONLY what the coordinator puts in its prompt
                    └──────────┘
```

The one rule that drives the code: **subagents inherit nothing.** Synthesis doesn't see the searches
unless the coordinator pastes their findings into synthesis's prompt. Forgetting this is the #1
multi-agent bug — so Phase 1 makes the explicit hand-off visible.

---

## 1. Step 1 — Spawning + explicit context passing (Domain 1.3) ⭐

### 1a. Give the stub real, deterministic behavior + simulated latency
Phase 0's stub just echoed. To *observe* parallelism credit-free, make stub mode **take time** and let
each role plug in its own deterministic behavior. Evolve `subagent.py`:

```python
# subagent.py
import asyncio
from dataclasses import dataclass, field

STUB_LATENCY_S = 0.5   # pretend each subagent does real work — makes the parallel win measurable

@dataclass
class AgentDefinition:
    name: str
    system: str
    allowed_tools: list[str] = field(default_factory=list)   # least privilege (matters in Phase 3)

class Subagent:
    def __init__(self, definition: AgentDefinition, claude=None, stub_responder=None):
        self.definition = definition
        self.claude = claude                 # None → STUB mode (no credits)
        self.stub_responder = stub_responder # prompt -> str: this role's deterministic behavior

    async def run(self, prompt: str) -> dict:
        if self.claude is None:
            await asyncio.sleep(STUB_LATENCY_S)
            text = self.stub_responder(prompt) if self.stub_responder else f"[stub:{self.definition.name}]"
            return {"agent": self.definition.name, "text": text}
        msg = self.claude.chat(messages=[{"role": "user", "content": prompt}],
                               system=self.definition.system)
        return {"agent": self.definition.name, "text": self.claude.text_from_message(msg)}
```

### 1b. Deterministic fake corpus — fill in `mock_sources.py`
This stands in for the web; no network, no credits:

```python
# mock_sources.py
_CORPUS = {
    "music":   "AI music tools surged (musicbiz.example, 2025-01).",
    "film":    "Studios pilot AI VFX pipelines (filmtech.example, 2024-11).",
    "writing": "Publishers debate AI-assisted drafting (pubweekly.example, 2025-03).",
    "visual":  "Generative art went mainstream (artnews.example, 2024-09).",
}

def search(query: str) -> str:
    q = query.lower()
    hits = [v for k, v in _CORPUS.items() if k in q]
    return " | ".join(hits) if hits else "(no sources found)"
```

### 1c. Define role-specialized agents (AgentDefinition + restricted tools)
Each subagent is description + system prompt + **restricted tool set** — and the coordinator prompts
state **goals + quality criteria, not step-by-step procedures**, so a subagent can adapt. Evolve
`main.py`'s `build()`:

```python
# main.py (excerpt)
import mock_sources
from subagent import AgentDefinition, Subagent
from coordinator import Coordinator

def build(claude=None):
    defs = {
        "web_search": AgentDefinition("web_search", "Find credible, dated sources.", ["search"]),
        "synthesis":  AgentDefinition("synthesis",  "Combine findings into a cited overview.", ["verify_fact"]),
    }
    stubs = {                                    # each role's credit-free behavior
        "web_search": lambda p: mock_sources.search(p),
        "synthesis":  lambda p: f"Overview built from {p.count('- ')} findings.",
    }
    subagents = {n: Subagent(d, claude=claude, stub_responder=stubs.get(n)) for n, d in defs.items()}
    return Coordinator(subagents)
```

> **Explicit context** is the heart of Step 1: synthesis only knows what the coordinator hands it (§2's
> `synth_prompt`). The `web_search` agent gets only its sub-topic — not the whole conversation.

## 2. Step 2 — Parallel execution (Domain 1.3)

**Parallel = await many spawns together (`asyncio.gather`), not a loop of `await`s.** Evolve
`coordinator.py` to decompose into several search tasks, run them in parallel *or* sequentially (for
comparison), then feed the findings **explicitly** into synthesis:

```python
# coordinator.py
import asyncio

class Coordinator:
    def __init__(self, subagents: dict):
        self.subagents = subagents

    def decompose(self, query: str) -> list[dict]:
        """Goals, not procedures. (Phase 2 fixes narrow decomposition here.)"""
        subdomains = ["music", "film", "writing", "visual"]
        return [{"agent": "web_search",
                 "prompt": f"Goal: find dated, credible sources on {sd} for: {query}."}
                for sd in subdomains]

    async def spawn(self, agent: str, prompt: str) -> dict:
        return await self.subagents[agent].run(prompt)        # ← stands in for the Task tool

    async def gather_findings(self, tasks: list[dict], parallel: bool = True) -> list[dict]:
        if parallel:                                          # one step, many spawns
            return await asyncio.gather(*(self.spawn(t["agent"], t["prompt"]) for t in tasks))
        out = []                                              # sequential: await in a loop
        for t in tasks:
            out.append(await self.spawn(t["agent"], t["prompt"]))
        return out

    async def run(self, query: str, parallel: bool = True) -> dict:
        tasks = self.decompose(query)
        findings = await self.gather_findings(tasks, parallel=parallel)

        # EXPLICIT CONTEXT PASSING — synthesis inherits nothing, so paste findings into its prompt:
        joined = "\n".join(f"- {f['agent']}: {f['text']}" for f in findings)
        synth_prompt = f"Synthesize a cited overview for: {query}\nFINDINGS:\n{joined}"
        synthesis = await self.spawn("synthesis", synth_prompt)

        return {"query": query, "findings": findings,
                "synthesis": synthesis, "synth_prompt": synth_prompt}
```

---

## 3. Run & observe (credit-free)

### 3a. Time parallel vs sequential — the Phase 1 milestone
Add a timing harness to `main.py`:

```python
# main.py (excerpt)
import asyncio, time

async def _timed(coord, query, parallel):
    t0 = time.perf_counter()
    out = await coord.run(query, parallel=parallel)
    return out, time.perf_counter() - t0

if __name__ == "__main__":
    coord = build()                       # no claude → stub, no credits
    q = "impact of AI on creative industries"
    par, t_par = asyncio.run(_timed(coord, q, parallel=True))
    seq, t_seq = asyncio.run(_timed(coord, q, parallel=False))
    print(par["synthesis"]["text"])
    print(f"parallel={t_par:.2f}s  sequential={t_seq:.2f}s")
```

Expected (with `STUB_LATENCY_S = 0.5`, 4 searches + 1 synthesis):
```
Overview built from 4 findings.
parallel=1.00s  sequential=2.50s     # 4 concurrent searches (~0.5s) vs 4 serial (~2.0s), + synthesis
```
The ~1.5s gap is the parallelism win — visible with zero credits because the latency is simulated.

### 3b. Credit-free assertions — `test_phase1.py`
```python
import asyncio
from main import build

coord = build()                                  # stub mode
out = asyncio.run(coord.run("impact of AI on creative industries", parallel=True))

assert len(out["findings"]) == 4, out            # decomposed into 4 sub-domains, all spawned
assert "FINDINGS:" in out["synth_prompt"]         # explicit context handed to synthesis
assert "musicbiz" in out["synth_prompt"]          # an actual upstream finding reached synthesis
assert out["synthesis"]["text"] == "Overview built from 4 findings."
print("PHASE-1 TESTS OK")
```
Run: `uv run python test_phase1.py` (or `python3`). This proves spawning, explicit context passing, and
fan-out **without a model**.

> Observe the isolation directly: temporarily build `synth_prompt` *without* `joined` and watch the
> synthesis stub report `0 findings` — that's what "subagents inherit nothing" feels like.

---

## 4. Exam mapping

- **Spawning** (EXAM-PREP §1.3): `Task` spawns subagents (your `spawn()`); coordinator needs `"Task"`
  in `allowedTools`; `AgentDefinition` = description + system prompt + **restricted tools**.
- **Isolated context** — pass everything explicitly in the prompt; synthesis sees only `synth_prompt`.
- **Goals not procedures** — coordinator prompts specify outcomes/quality, not steps.
- **Parallel** = many spawns in one step (`asyncio.gather`) ≈ multiple `Task` calls in one assistant turn.

## 5. Close out the phase

- [ ] Tick the three Phase 1 boxes in [`overview.md`](overview.md).
- [ ] `PHASE-1 TESTS OK`, and you can show `parallel < sequential` numbers.
- [ ] Notes one-liner: *"Subagents inherit nothing → paste findings into the prompt; AgentDefinition
  restricts tools; parallel = gather many spawns in one step (≈ many Task calls/turn)."*
- [ ] Commit; run `/log`.

### What Phase 2 will add (preview)
The decomposition-quality failure mode: make `decompose()` over-narrow (e.g. only `["visual"]`),
reproduce the report that misses whole sub-topics though every subagent "succeeded" (Q7 — root cause is
the coordinator), then fix it with a broad partition + a synthesis-flags-gaps refinement loop.
