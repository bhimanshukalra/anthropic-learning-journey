# Project 04 · Phase 0 — Project setup (from complete scratch)

> **Companion to:** [`overview.md`](overview.md). Phases: [0](phase-0.md) · [1](phase-1.md) ·
> [2](phase-2.md) · [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). Build it yourself; the
> snippets are a reference.

**Phase 0 answers "where do I start from nothing?"** — the directory, what to reuse from Project 01,
the first file to create, and a **runnable skeleton that needs zero API credits.**

> **Build approach (decided):** a **custom harness** extending Project 01's stack (Anthropic SDK + your
> existing `core/claude.py`), with the model call **injectable** so the whole pipeline runs on **stubs,
> no credits**. The hand-built coordinator/subagent map onto the real Claude Agent SDK `Task` /
> `AgentDefinition` — see §4. (We chose this over the SDK precisely because the SDK's real subagents are
> model-driven and can't be observed without credits.)

**Phase 0 milestone:** a coordinator spawns **one stub subagent** and prints its result — the skeleton
runs end-to-end with **no API key set**.

**Phase 0 Definition of done**
- [ ] Project directory + env created; `core/claude.py` reused from Project 01.
- [ ] `subagent.py` + `coordinator.py` skeleton runs on stubs with **no credits**.
- [ ] You can explain how `spawn()` maps to the real `Task` tool (§4).

---

## 0. Where it lives & what to reuse

Mirror the Project 01 layout (`projects/cert-01-customer-support-agent/`):

```
projects/cert-04-multi-agent-research/
  core/
    claude.py          # ← REUSE from Project 01 (thin Anthropic wrapper; injectable, can be None)
  subagent.py          # the unit: AgentDefinition + a run() that's credit-free in stub mode
  coordinator.py       # hub: decompose → spawn (parallel) → synthesize
  mock_sources.py      # deterministic fake web/doc data (no network, no credits) — like mock_backend.py
  main.py              # wire it together
  pyproject.toml       # deps: anthropic (only needed once you have credits)
```

```bash
mkdir -p projects/cert-04-multi-agent-research/core
cp projects/cert-01-customer-support-agent/core/claude.py projects/cert-04-multi-agent-research/core/
```

`core/claude.py` already takes the API call as a method — keep the model **injectable** (`claude=None`
→ stub mode) so nothing calls the API until you choose to.

---

## 1. The first file: `subagent.py` (the unit everything builds on)

Start here, not the coordinator — the coordinator orchestrates *subagents*, so the subagent is the
foundational abstraction. An `AgentDefinition` (the exam term) is just description + system prompt +
**restricted tool set**; the `Subagent` runs on an **explicit, self-contained prompt** (subagents
inherit nothing — Phase 1).

```python
# subagent.py
from dataclasses import dataclass, field

@dataclass
class AgentDefinition:
    name: str
    system: str
    allowed_tools: list[str] = field(default_factory=list)   # least privilege (Phase 3)

class Subagent:
    def __init__(self, definition: AgentDefinition, claude=None):
        self.definition = definition
        self.claude = claude                      # None → STUB mode (no credits)

    async def run(self, prompt: str) -> dict:
        """Run on an explicit prompt. Stub mode returns deterministic output — zero credits."""
        if self.claude is None:
            return {"agent": self.definition.name, "stub": True, "saw": prompt[:60]}
        msg = self.claude.chat(messages=[{"role": "user", "content": prompt}],
                               system=self.definition.system)
        return {"agent": self.definition.name, "text": self.claude.text_from_message(msg)}
```

## 2. Then `coordinator.py` (the hub)

```python
# coordinator.py
import asyncio

class Coordinator:
    def __init__(self, subagents: dict):
        self.subagents = subagents                 # name -> Subagent

    def decompose(self, query: str) -> list[dict]:
        """Query -> [{agent, prompt}]. Phase 2 fixes narrow decomposition HERE."""
        return [{"agent": "web_search", "prompt": f"Find sources on: {query}"}]

    async def spawn(self, agent: str, prompt: str) -> dict:
        return await self.subagents[agent].run(prompt)   # ← stands in for the SDK Task tool

    async def run(self, query: str) -> dict:
        tasks = self.decompose(query)
        # parallel = ONE step, MANY spawns (Phase 1): gather, don't await in a loop
        results = await asyncio.gather(*(self.spawn(t["agent"], t["prompt"]) for t in tasks))
        return {"query": query, "results": results}     # synthesize() comes in later phases
```

## 3. Wire a credit-free skeleton: `main.py`

```python
# main.py
import asyncio
from subagent import AgentDefinition, Subagent
from coordinator import Coordinator

def build(claude=None):   # claude=None → stub mode, no credits
    defs = {
        "web_search": AgentDefinition("web_search", "Find credible, dated sources.", ["search"]),
    }
    subagents = {name: Subagent(d, claude=claude) for name, d in defs.items()}
    return Coordinator(subagents)

if __name__ == "__main__":
    coord = build()                               # no claude → stub
    out = asyncio.run(coord.run("impact of AI on creative industries"))
    print(out)
```

```bash
cd projects/cert-04-multi-agent-research && python main.py
# → {'query': '...', 'results': [{'agent': 'web_search', 'stub': True, 'saw': '...'}]}
```

That print **with no API key set** is the Phase 0 milestone: the orchestration shape works, and you'll
swap stubs for real model calls (or richer mock data in `mock_sources.py`) as later phases need them —
still credit-free, by injecting canned responses instead of calling the API.

---

## 4. Exam mapping — how this maps to the real Claude Agent SDK

You're hand-building the primitives so you can see and test them; on the exam they're SDK features:

| Your custom harness | Real Claude Agent SDK |
|---|---|
| `Coordinator.spawn(agent, prompt)` | the **`Task`** tool (coordinator's `allowedTools` must include `"Task"`) |
| `AgentDefinition(name, system, allowed_tools)` | **`AgentDefinition`** (description + system prompt + restricted tools) |
| `asyncio.gather(...)` over many spawns | **multiple `Task` calls in one assistant turn** (parallel) |
| passing the full prompt into `run()` | subagents have **isolated context** — pass everything explicitly |

Know the SDK names for the exam; build the harness to understand *why* they exist.

---

## 5. Close out the phase

- [ ] Tick the Phase 0 boxes in [`overview.md`](overview.md).
- [ ] Notes one-liner: *"Multi-agent from scratch = Subagent (AgentDefinition + injectable model) +
  Coordinator (decompose→spawn→synthesize); `spawn` = the Task tool; `asyncio.gather` = parallel;
  stub mode (claude=None) runs credit-free."*
- [ ] Commit; run `/log`.

### What Phase 1 will add
Flesh out the coordinator/subagent mechanics: explicit context passing, `AgentDefinition` per role with
restricted tools, and measuring the parallel-vs-sequential latency win.
