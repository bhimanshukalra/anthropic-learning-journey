# Project 04 · Phase 4 — Provenance & context discipline ⭐

> **Companion to:** [`overview.md`](overview.md). Phases: [1](phase-1.md) · [2](phase-2.md) ·
> [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). Build it yourself; the snippets are a reference.

**Phase 4 covers build steps 6–7** (Domains **5.6** provenance, **5.1** context preservation). The
output-quality half: attribution must survive synthesis, and handoffs must stay lean.

**Milestone:** the final report preserves claim→source mappings, annotates conflicts with dates, and
separates established vs contested findings; upstream handoffs carry trimmed key facts, not reasoning
dumps.

**Phase 4 Definition of done**
- [ ] Final report preserves claim→source mappings, annotates conflicts with dates, separates
      established vs contested findings.
- [ ] Upstream agents hand off structured key facts + citations; key summaries placed at the start.

---

## 0. Mental model — carry the citation, trim the reasoning

```
  subagent claim ─► {claim, evidence, source, date}  ──┐
                                                        ├─► synthesis MERGES while KEEPING the mapping
  conflicting stat ─► {claim, source A, date} + {claim, source B, date}   (annotate BOTH, don't pick)
                                                        │
                                                        ▼
  report: established vs contested · tables for financials · prose for news · coverage notes
```

Two jobs: **provenance** (every claim keeps its source through every merge) and **context discipline**
(hand the *facts + citations* downstream, not the verbose chain that produced them).

---

## 1. Step 6 — Provenance + conflict handling (Domain 5.6) ⭐

- Subagent outputs are **structured claim→source mappings**: `claim`, `evidence` excerpt, `source`
  (URL/doc), and **`publication_date`**. Synthesis must **preserve** the mapping through merging — never
  flatten claims into unsourced prose.
- **Conflicting credible statistics → annotate both with their sources**, don't silently pick one.
- **Use dates** so a 2023 figure vs a 2025 figure isn't misread as a contradiction (it's temporal).
- Structure the report to separate **well-established vs contested** findings; render **financials as
  tables, news as prose** — not one uniform format.
- Synthesis output carries **coverage annotations** (well-supported vs gap areas — feeds back to the
  Phase 2 refinement loop).

```json
{ "claim": "AI music tools reached $X market size",
  "evidence": "…", "source": "https://…", "publication_date": "2025-02" }
```

## 2. Step 7 — Context discipline across handoffs (Domain 5.1)

When the downstream agent's context budget is tight, upstream agents return **structured key facts +
citations**, *not* verbose reasoning chains. Place **key summaries at the start** of aggregated inputs
(lost-in-the-middle) with explicit section headers so nothing important gets buried mid-context.

> This is the same trimming/positioning discipline as Project 01's case-facts block — return the
> distilled facts, pin the important ones at the top.

---

## 3. Run & observe

- **Attribution survives:** trace one claim from a subagent through synthesis into the report and
  confirm its source + date are intact (not dropped in the merge).
- **Conflict:** feed two credible, differing stats and confirm the report **shows both with sources**
  and dates, rather than picking one.
- **Format fit:** confirm financials render as a table and narrative findings as prose.
- **Lean handoff:** confirm upstream agents pass facts+citations (not full reasoning), with summaries
  at the start of the aggregated input.

---

## 4. Exam mapping

- **Provenance** (EXAM-PREP §5.6): keep claim→source mappings through summarization; conflicting
  credible stats → annotate both with attribution; require publication dates; render content types
  natively (tables vs prose).
- **Context preservation** (§5.1): structured key facts + citations downstream, not verbose reasoning;
  key summaries at the **start**; trim verbose outputs. A bigger context window does **not** fix this.

## 5. Close out the phase

- [ ] Tick the two Phase 4 boxes in [`overview.md`](overview.md).
- [ ] Notes one-liner: *"Carry claim→source+date through synthesis; annotate conflicts (both sources,
  dates) don't pick; established-vs-contested + tables/prose; hand off facts+citations not reasoning,
  summaries at the start."*
- [ ] Commit; run `/log`.

### What Phase 5 will add (preview)
No more building. Answer the five **"Be able to answer"** questions in your own words — the exam payload
for this scenario.
