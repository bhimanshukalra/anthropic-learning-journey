# Project 04 · Phase 2 — Decomposition quality ⭐

> **Companion to:** [`overview.md`](overview.md). Phases: [0](phase-0.md) · [1](phase-1.md) ·
> [2](phase-2.md) · [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). Build it yourself; the
> snippets are a reference. **Builds on the Phase 1 code.**

**Phase 2 covers build step 3** (Domain **1.2** — decomposition). You'll **reproduce** the exam's
signature failure (Q7: reports miss whole sub-topics though every subagent "succeeded"), then **fix**
it two ways — a broad scope partition and an **iterative refinement loop** — all credit-free.

**Milestone:** with a narrow decompose, the run reports **gaps** (missed sub-domains) even though every
subagent succeeded; with the refinement loop on, the coordinator re-delegates the gaps until coverage
is complete.

**Phase 2 Definition of done**
- [ ] Narrow-decomposition failure reproduced (non-empty `gaps`, all subagents "succeeded").
- [ ] Fixed with broad partition + a refinement loop (`gaps` empties; you can show the rounds).

---

## 0. Mental model — the failure is upstream of the subagents

```
  query ─► coordinator.decompose() ─► scope = ["visual"]   ← TOO NARROW (the bug)
                                       (music, film, writing, games never assigned)
        ─► subagents run PERFECTLY on the narrow scope
        ─► report looks done but MISSES whole sub-domains
  FIX: decompose broadly  ──OR──  detect gaps → re-delegate → re-synthesize (refine)
```

Every subagent "succeeded" — they only worked on what they were *given*. The root cause is
**`decompose()`**, not search/synthesis. The fix lives in the coordinator.

---

## 1. Step 3 — Reproduce, then fix (Domain 1.2) ⭐

### 1a. Know the full space (so "gap" is measurable)
Add the complete sub-domain set to `mock_sources.py` (and a `games` entry so there are five):

```python
# mock_sources.py
_CORPUS = {
    "music":   "AI music tools surged (musicbiz.example, 2025-01).",
    "film":    "Studios pilot AI VFX pipelines (filmtech.example, 2024-11).",
    "writing": "Publishers debate AI-assisted drafting (pubweekly.example, 2025-03).",
    "visual":  "Generative art went mainstream (artnews.example, 2024-09).",
    "games":   "Studios test AI NPCs and asset generation (gamedev.example, 2025-02).",
}
KNOWN_SUBDOMAINS = list(_CORPUS)

def search(query: str) -> str:
    q = query.lower()
    hits = [v for k, v in _CORPUS.items() if k in q]
    return " | ".join(hits) if hits else "(no sources found)"
```

### 1b. Decompose by scope, tag each task, measure coverage
Evolve `coordinator.py` so `decompose()` takes a **scope**, each task carries its `subdomain`, and the
coordinator can compute **coverage** and **gaps**:

```python
# coordinator.py
import asyncio
import mock_sources

class Coordinator:
    def __init__(self, subagents: dict):
        self.subagents = subagents

    def decompose(self, query: str, scope: list[str]) -> list[dict]:
        """Goals, not procedures. SCOPE is the lever this phase is about."""
        return [{"agent": "web_search", "subdomain": sd,
                 "prompt": f"Goal: find dated, credible sources on {sd} for: {query}."}
                for sd in scope]

    async def spawn(self, agent: str, prompt: str) -> dict:
        return await self.subagents[agent].run(prompt)

    async def research(self, query: str, scope: list[str]) -> list[dict]:
        tasks = self.decompose(query, scope)
        findings = await asyncio.gather(*(self.spawn(t["agent"], t["prompt"]) for t in tasks))
        for t, f in zip(tasks, findings):          # carry the subdomain onto its finding
            f["subdomain"] = t["subdomain"]
        return findings

    def covered(self, findings: list[dict]) -> set:
        return {f["subdomain"] for f in findings if "no sources found" not in f["text"]}
```

### 1c. Reproduce the failure, then fix it (broad partition + refinement loop)
Add the orchestration `run()` that supports both fixes:

```python
    async def run(self, query: str, scope: list[str], refine: bool = True, max_rounds: int = 3) -> dict:
        findings = await self.research(query, scope)

        rounds = 0
        while refine and rounds < max_rounds:                       # ITERATIVE REFINEMENT LOOP
            gaps = set(mock_sources.KNOWN_SUBDOMAINS) - self.covered(findings)
            if not gaps:
                break
            findings += await self.research(query, sorted(gaps))     # re-delegate ONLY the gaps
            rounds += 1

        gaps = sorted(set(mock_sources.KNOWN_SUBDOMAINS) - self.covered(findings))
        joined = "\n".join(f"- {f['subdomain']}: {f['text']}" for f in findings)
        synth_prompt = (f"Synthesize a cited overview for: {query}\nFINDINGS:\n{joined}\n"
                        f"COVERAGE: covered={sorted(self.covered(findings))} gaps={gaps}")
        synthesis = await self.spawn("synthesis", synth_prompt)
        return {"query": query, "findings": findings, "covered": sorted(self.covered(findings)),
                "gaps": gaps, "rounds": rounds, "synthesis": synthesis}
```

- **Reproduce:** `run(query, scope=["visual"], refine=False)` → `gaps` lists the 4 missing sub-domains
  even though the visual subagent succeeded. That's Q7.
- **Fix A — broad partition:** `run(query, scope=KNOWN_SUBDOMAINS, refine=False)` → `gaps == []`.
- **Fix B — refinement loop:** `run(query, scope=["visual"], refine=True)` → the loop re-delegates the
  gaps and `gaps` empties in `rounds=1`.

> Don't "fix" this by making the search agent search harder — that patches a working component. The
> lever is **decomposition scope** + the **coverage-gap refinement loop**.

---

## 2. Run & observe (credit-free)

`test_phase2.py`:

```python
import asyncio
from main import build

coord = build()                                  # stub mode — no credits

# Reproduce: narrow scope, no refinement → gaps even though subagents succeeded
narrow = asyncio.run(coord.run("AI in creative industries", scope=["visual"], refine=False))
assert narrow["covered"] == ["visual"]
assert set(narrow["gaps"]) == {"music", "film", "writing", "games"}, narrow["gaps"]

# Fix A: broad partition
broad = asyncio.run(coord.run("AI in creative industries", scope=list(__import__('mock_sources').KNOWN_SUBDOMAINS), refine=False))
assert broad["gaps"] == []

# Fix B: refinement loop closes the gaps
refined = asyncio.run(coord.run("AI in creative industries", scope=["visual"], refine=True))
assert refined["gaps"] == [] and refined["rounds"] >= 1, refined
print("PHASE-2 TESTS OK")
```

Observe: print `narrow["gaps"]` (the failure), then `refined["rounds"]` (the loop healing it) — the
whole Q7 story, no model needed.

---

## 3. Exam mapping

- **Root cause, not symptom** (EXAM-PREP §4.2, Q7 → B): missed sub-topics + succeeding subagents ⇒
  blame the **coordinator's decomposition**.
- **Iterative refinement** (§1.2): evaluate coverage → re-delegate targeted queries → re-synthesize.
- **Partition scope** to cover all sub-domains and minimize duplication.

## 4. Close out the phase

- [ ] Tick the Phase 2 box in [`overview.md`](overview.md); `PHASE-2 TESTS OK`.
- [ ] Notes one-liner: *"Reports miss sub-topics but subagents succeeded → root cause = decompose() too
  narrow (Q7); fix = broad scope partition + coverage-gap refinement loop."*
- [ ] Commit; run `/log`.

### What Phase 3 will add (preview)
A scoped `verify_fact` tool for synthesis (least privilege, Q9) and **structured error propagation** —
a search timeout returns a structured envelope, the coordinator retries then proceeds with partial
results + a coverage note, never killing the workflow (Q8).
