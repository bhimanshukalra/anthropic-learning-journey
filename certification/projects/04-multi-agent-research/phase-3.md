# Project 04 · Phase 3 — Tools & error propagation ⭐

> **Companion to:** [`overview.md`](overview.md). Phases: [0](phase-0.md) · [1](phase-1.md) ·
> [2](phase-2.md) · [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). Build it yourself; the
> snippets are a reference. **Builds on the Phase 2 code.**

**Phase 3 covers build steps 4–5** (Domains **2.3** least-privilege tools, **2.2/5.3** structured
errors). Two exam-signature ideas, both credit-free: a **scoped `verify_fact`** tool (Q9) and
**structured error propagation** where a search timeout is recovered, not fatal (Q8).

**Milestone:** a search timeout returns a **structured error envelope**; the coordinator **retries**
the transient failure, then **proceeds with partial results + a coverage note** — the run still
produces a synthesis, and the workflow is never killed.

**Phase 3 Definition of done**
- [ ] `verify_fact` is a scoped tool on synthesis (`allowed_tools == ["verify_fact"]`, no web tools).
- [ ] Timeout → structured error (type/query/partial/alternatives/retryable); coordinator recovers and proceeds with partial + coverage note.

---

## 0. Mental model

```
  TOOLS (least privilege)              ERRORS (structured, recoverable)
  synthesis ─ verify_fact (scoped)     web_search timeout ─► {failureType, attemptedQuery,
        │ simple checks                                       partialResults, alternatives, isRetryable}
        └ complex ─► coordinator ─► web    coordinator ─► retry → still failing? proceed w/ PARTIAL + note
```

Give each agent only the tools its role needs, and make a failure **data the coordinator can act on** —
never a generic string, never empty-as-success, never a workflow kill.

---

## 1. Step 4 — Scoped cross-role tool `verify_fact` (Domain 2.3) ⭐

Synthesis needs to fact-check, but the **full web toolset would over-privilege it** and degrade tool
selection. Give it one **scoped** tool. Add it to `mock_sources.py` and restrict synthesis's tools:

```python
# mock_sources.py — a scoped, deterministic fact-checker (no credits)
def verify_fact(claim: str) -> dict:
    q = claim.lower()
    for sd, txt in _CORPUS.items():
        if sd in q:
            return {"verified": True, "source": txt}
    return {"verified": False, "source": None}     # complex/unknown → route via coordinator
```

```python
# main.py build(): synthesis gets ONLY verify_fact (least privilege), web_search only search
"synthesis": AgentDefinition("synthesis", "Combine findings; verify simple claims.", ["verify_fact"]),
"web_search": AgentDefinition("web_search", "Find credible, dated sources.", ["search"]),
```

> **Q9 → A (least privilege):** add **one** scoped cross-role tool for the frequent need. Wrong
> answers: hand synthesis the whole web toolset, route *everything* through the coordinator, batch all
> verifications, or speculatively cache. `verify_fact` returning `verified:false` is the signal to
> escalate the *complex* check back through the coordinator to `web_search`.

## 2. Step 5 — Structured error propagation (Domain 2.2 / 5.3) ⭐

### 2a. Make a search time out, and let the subagent normalize dict-or-text
Evolve the stub so a responder may return a **dict** (structured result/error) or a **str** (text):

```python
# subagent.py — run() stub branch
res = self.stub_responder(prompt) if self.stub_responder else f"[stub:{self.definition.name}]"
return {"agent": self.definition.name, **res} if isinstance(res, dict) \
       else {"agent": self.definition.name, "text": res}
```

```python
# mock_sources.py — a deterministic, switchable timeout
FAILING: set[str] = set()                 # subdomains whose search times out (tests set this)
class SourceTimeout(Exception): pass

def search(query: str) -> str:
    q = query.lower()
    if any(sd in q for sd in FAILING):
        raise SourceTimeout("order service unreachable")
    hits = [v for k, v in _CORPUS.items() if k in q]
    return " | ".join(hits) if hits else "(no sources found)"
```

```python
# main.py — the web_search stub turns a timeout into a STRUCTURED error envelope
def _web_search_stub(prompt):
    try:
        return mock_sources.search(prompt)
    except mock_sources.SourceTimeout:
        return {"isError": True, "failureType": "transient", "attemptedQuery": prompt,
                "partialResults": [], "suggestedAlternatives": ["retry", "narrow date range"],
                "isRetryable": True}
# ...stubs = {"web_search": _web_search_stub, "synthesis": lambda p: f"Overview ({p.count('- ')} findings)."}
```

### 2b. Coordinator: recover locally, then proceed with partial
Evolve the coordinator — `research()` **retries transient errors once** (local recovery), and `run()`
separates errors from successes and **proceeds with partial results + a coverage note**:

```python
# coordinator.py
    def covered(self, findings):
        return {f["subdomain"] for f in findings
                if not f.get("isError") and "no sources found" not in f.get("text", "")}

    async def research(self, query, scope):
        tasks = self.decompose(query, scope)
        findings = await asyncio.gather(*(self.spawn(t["agent"], t["prompt"]) for t in tasks))
        for t, f in zip(tasks, findings):
            f["subdomain"] = t["subdomain"]
        for i, (t, f) in enumerate(zip(tasks, findings)):     # LOCAL RECOVERY: retry transient once
            if f.get("isError") and f.get("isRetryable"):
                r = await self.spawn(t["agent"], t["prompt"]); r["subdomain"] = t["subdomain"]
                findings[i] = r
        return findings

    async def run(self, query, scope, refine=False, max_rounds=3):
        findings = await self.research(query, scope)
        rounds = 0
        while refine and rounds < max_rounds:                 # (Phase 2 loop still composes)
            gaps = set(mock_sources.KNOWN_SUBDOMAINS) - self.covered(findings)
            if not gaps: break
            findings += await self.research(query, sorted(gaps)); rounds += 1

        ok     = [f for f in findings if not f.get("isError")]
        errors = [f for f in findings if f.get("isError")]
        failed = sorted({f["subdomain"] for f in errors})
        joined = "\n".join(f"- {f['subdomain']}: {f['text']}" for f in ok)
        note = (f"\nCOVERAGE NOTE: search errors on {failed} (retried, proceeding with partial)."
                if errors else "")
        synthesis = await self.spawn("synthesis", f"Synthesize for: {query}\nFINDINGS:\n{joined}{note}")
        return {"query": query, "findings": ok, "errors": errors, "failed": failed,
                "synthesis": synthesis}        # NOTE: never raises — the run still ships
```

Avoids all three anti-patterns: not a generic "search unavailable" (the envelope keeps context),
not empty-as-success (errors are separated, not silently dropped), not a workflow kill (run completes).

---

## 3. Run & observe (credit-free)

`test_phase3.py`:

```python
import asyncio
import mock_sources
from main import build

# verify_fact: scoped tool behavior
assert mock_sources.verify_fact("the AI music market grew")["verified"] is True
assert mock_sources.verify_fact("unrelated claim")["verified"] is False

coord = build()
assert coord.subagents["synthesis"].definition.allowed_tools == ["verify_fact"]   # least privilege
assert "search" not in coord.subagents["synthesis"].definition.allowed_tools

# structured error propagation: make "film" search time out
mock_sources.FAILING = {"film"}
out = asyncio.run(coord.run("AI in creative industries",
                            scope=list(mock_sources.KNOWN_SUBDOMAINS), refine=False))
assert out["failed"] == ["film"]                       # error surfaced, not swallowed
e = out["errors"][0]
assert e["failureType"] == "transient" and e["isRetryable"] is True and "attemptedQuery" in e
assert len(out["findings"]) == 4                       # proceeded with partial (the other 4)
assert out["synthesis"]["text"].startswith("Overview")  # workflow NOT killed — synthesis produced
mock_sources.FAILING = set()                           # reset
print("PHASE-3 TESTS OK")
```

Observe: print `out["errors"][0]` (the structured envelope) and `out["synthesis"]` (the run still
shipped) — Q8's "recover and proceed" in one view, no model.

---

## 4. Exam mapping

- **Least privilege / scoped tools** (EXAM-PREP §4.5, Q9 → A): one scoped `verify_fact`, not the full
  toolset, not everything-via-coordinator.
- **Structured errors** (§4.6 / §2.2 / §5.3, Q8 → A): failureType, attemptedQuery, partialResults,
  alternatives, `isRetryable`; recover transient **locally**, propagate only the unrecoverable, proceed
  with partial — never genericize, suppress, or kill.
- **Access failure ≠ valid empty result**: a timeout is retryable; "(no sources found)" is a successful
  empty (it counts as a gap, not an error).

## 5. Close out the phase

- [ ] Tick the two Phase 3 boxes in [`overview.md`](overview.md); `PHASE-3 TESTS OK`.
- [ ] Notes one-liner: *"Scoped verify_fact on synthesis (Q9, least privilege); timeout → structured
  envelope, retry transient locally, proceed with partial + coverage note, never kill (Q8)."*
- [ ] Commit; run `/log`.

### What Phase 4 will add (preview)
Provenance: upgrade the corpus to **structured records** (claim, source, date), preserve claim→source
mappings through synthesis, **annotate conflicting stats with both sources + dates**, and structure the
report into established vs contested — plus lean, facts-first handoffs.
