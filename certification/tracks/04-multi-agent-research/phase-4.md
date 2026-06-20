# Project 04 · Phase 4 — Provenance & context discipline ⭐

> **Companion to:** [`overview.md`](overview.md). Phases: [0](phase-0.md) · [1](phase-1.md) ·
> [2](phase-2.md) · [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). Build it yourself; the
> snippets are a reference. **Builds on the Phase 3 code.**

**Phase 4 covers build steps 6–7** (Domains **5.6** provenance, **5.1** context preservation). The
output-quality half: attribution must **survive synthesis**, conflicting stats are **annotated, not
resolved**, and handoffs stay **lean** — all credit-free.

**Milestone:** the report preserves every claim→source(+date) mapping, puts a subdomain with
conflicting stats in a **contested** section showing **both** sources, and the rest in **established**.

**Phase 4 Definition of done**
- [ ] Findings are structured claim→source→date records; synthesis preserves the mapping.
- [ ] Conflicting stats land in `contested` with **both** sources + dates (not arbitrarily picked).
- [ ] Report separates established vs contested; handoffs carry facts+citations, not reasoning.

---

## 0. Mental model — carry the citation, trim the reasoning

```
  web_search ─► [{claim, source, date}, …]  ──┐
                                               ├─► synthesize() KEEPS the mapping
  conflicting stats (same subdomain) ──────────┘     → established  (single, agreed)
                                                      → contested   (both sources + dates)
  handoff = facts + citations (NOT verbose reasoning); key summary at the START
```

Two jobs: **provenance** (every claim keeps its source/date through the merge) and **context
discipline** (pass distilled facts downstream, not the chain that produced them).

---

## 1. Step 6 — Provenance + conflict handling (Domain 5.6) ⭐

### 1a. Upgrade the corpus to structured records
Provenance starts at the source. Evolve `mock_sources.py` from strings to **records**, and seed a
deliberate **conflict** under `film`:

```python
# mock_sources.py
_CORPUS = {
    "music":   [{"claim": "AI music market grew sharply in 2025", "source": "musicbiz.example", "date": "2025-01"}],
    "film":    [{"claim": "AI VFX adoption ~30%", "source": "a.example", "date": "2024-11"},
                {"claim": "AI VFX adoption ~55%", "source": "b.example", "date": "2025-04"}],   # CONFLICT
    "writing": [{"claim": "Publishers piloting AI drafting", "source": "pubweekly.example", "date": "2025-03"}],
    "visual":  [{"claim": "Generative art went mainstream", "source": "artnews.example", "date": "2024-09"}],
    "games":   [{"claim": "Studios testing AI NPCs", "source": "gamedev.example", "date": "2025-02"}],
}
KNOWN_SUBDOMAINS = list(_CORPUS)

def search(query: str) -> list[dict]:
    q = query.lower()
    for sd in KNOWN_SUBDOMAINS:
        if sd in q:
            return _CORPUS[sd]          # list of claim→source records (a lean handoff)
    return []
```

### 1b. Findings carry records; synthesis preserves the mapping
The `web_search` stub now hands back **records** (facts + citations — Step 7's lean handoff), and a
pure `synthesize()` builds the report **without losing attribution**:

```python
# main.py — web_search stub returns structured records (dict → finding carries them)
def _web_search_stub(prompt):
    for sd in mock_sources.KNOWN_SUBDOMAINS:
        if sd in prompt.lower():
            return {"records": mock_sources.search(sd)}
    return {"records": []}
```

```python
# coordinator.py — synthesize() preserves claim→source and separates established vs contested
    def synthesize(self, query: str, findings: list[dict]) -> dict:
        established, contested = [], []
        for f in findings:
            recs = f.get("records", [])
            if not recs:
                continue
            if len(recs) > 1 and len({r["claim"] for r in recs}) > 1:   # conflicting credible stats
                contested.append({"subdomain": f["subdomain"], "sources": recs})  # annotate BOTH
            else:
                established.append({"subdomain": f["subdomain"], **recs[0]})       # keep claim+source+date
        return {"query": query, "established": established, "contested": contested}
```

- **Preserve** the mapping — every `established` item keeps `claim/source/date`; never flatten into
  unsourced prose.
- **Conflict** → put it in `contested` with **both** records (sources + dates); don't pick one.
- **Dates** travel so a 2024 figure vs a 2025 figure reads as *temporal*, not contradictory.

## 2. Step 7 — Context discipline across handoffs (Domain 5.1)

The handoff is already lean: `search()` returns **structured records (facts + citations)**, not a verbose
reasoning chain. When you aggregate, put the **summary/coverage at the start** (lost-in-the-middle) with
explicit headers — the same discipline as Project 01's case-facts block.

```python
    def run_report(self, query, findings) -> str:
        r = self.synthesize(query, findings)
        lines = [f"# {query}", f"_established={len(r['established'])} contested={len(r['contested'])}_"]  # summary FIRST
        lines += [f"- [{e['subdomain']}] {e['claim']} ({e['source']}, {e['date']})" for e in r["established"]]
        for c in r["contested"]:
            both = " vs ".join(f"{x['claim']} ({x['source']}, {x['date']})" for x in c["sources"])
            lines.append(f"- [{c['subdomain']} — CONTESTED] {both}")
        return "\n".join(lines)
```

---

## 3. Run & observe (credit-free)

`test_phase4.py`:

```python
import asyncio
import mock_sources
from main import build

coord = build()
findings = asyncio.run(coord.research("AI in creative industries", list(mock_sources.KNOWN_SUBDOMAINS)))
r = coord.synthesize("AI in creative industries", findings)

# provenance preserved: an established claim keeps its source + date
music = next(e for e in r["established"] if e["subdomain"] == "music")
assert music["source"] == "musicbiz.example" and music["date"] == "2025-01"

# conflict annotated, not resolved: film is contested with BOTH sources
film = next(c for c in r["contested"] if c["subdomain"] == "film")
assert {x["source"] for x in film["sources"]} == {"a.example", "b.example"}
assert len(film["sources"]) == 2                       # both kept, none dropped

# report separates established vs contested, summary first
report = coord.run_report("AI in creative industries", findings)
assert report.splitlines()[1].startswith("_established=") and "CONTESTED" in report
print("PHASE-4 TESTS OK")
```

> Observe: print `report` and see established findings each carry `(source, date)` and the film line
> shows **both** conflicting stats — provenance and conflict handling, no model.

(Note: this phase changes `search()` to return records, so the Phase 1–3 string-based `text`
assertions are superseded here — that's the intended evolution toward a provenance-preserving pipeline.)

---

## 4. Exam mapping

- **Provenance** (EXAM-PREP §5.6): keep claim→source mappings through synthesis; conflicting credible
  stats → annotate **both** with attribution + dates; render content types natively (here: established
  vs contested sections).
- **Context preservation** (§5.1): hand off structured facts + citations, not verbose reasoning; put
  the summary at the **start**. A bigger context window does not fix lost attribution — structure does.

## 5. Close out the phase

- [ ] Tick the two Phase 4 boxes in [`overview.md`](overview.md); `PHASE-4 TESTS OK`.
- [ ] Notes one-liner: *"Carry claim→source+date through synthesis; conflicts → contested with BOTH
  sources+dates (don't pick); established-vs-contested report, summary first; hand off facts+citations,
  not reasoning."*
- [ ] Commit; run `/log`.

### What Phase 5 will add
No more building. Answer the five **"Be able to answer"** questions in your own words — the exam payload
for this scenario. (See [`phase-5.md`](phase-5.md).)
