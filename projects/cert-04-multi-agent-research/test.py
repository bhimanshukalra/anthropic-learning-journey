import asyncio
import mock_sources
from main import build

coord = build()
KNOWN = list(mock_sources.KNOWN_SUBDOMAINS)


# ---- Phase 1: spawning + fan-out (one subagent per sub-domain) ----
p1 = asyncio.run(coord.run("impact of AI on creative industries", scope=KNOWN, refine=False))
assert len(p1["findings"]) == len(KNOWN)  # fan-out: one spawn per sub-domain
assert all(f.get("records") for f in p1["findings"])  # each subagent returned structured records
print("PHASE-1 TESTS OK")


# ---- Phase 2: decomposition quality (narrow → gaps; broad / refine → fixed) ----
narrow = asyncio.run(coord.run("AI in creative industries", scope=["visual"], refine=False))
assert narrow["covered"] == ["visual"]
assert set(narrow["gaps"]) == {"music", "film", "writing", "games"}, narrow["gaps"]

broad = asyncio.run(coord.run("AI in creative industries", scope=KNOWN, refine=False))
assert broad["gaps"] == []

refined = asyncio.run(coord.run("AI in creative industries", scope=["visual"], refine=True))
assert refined["gaps"] == [] and refined["rounds"] >= 1, refined
print("PHASE-2 TESTS OK")


# ---- Phase 3: scoped tool (least privilege) ----
assert mock_sources.verify_fact("the AI music market grew")["verified"] is True
assert mock_sources.verify_fact("unrelated claim")["verified"] is False
assert coord.subagents["synthesis"].definition.allowed_tools == ["verify_fact"]
assert "search" not in coord.subagents["synthesis"].definition.allowed_tools

# ---- Phase 3: structured error propagation (timeout → recover → proceed with partial) ----
mock_sources.FAILING = {"film"}
err_out = asyncio.run(coord.run("AI in creative industries", scope=KNOWN, refine=False))
assert err_out["failed"] == ["film"]  # error surfaced, not swallowed
e = err_out["errors"][0]
assert e["failureType"] == "transient" and e["isRetryable"] is True and "attemptedQuery" in e
assert len(err_out["findings"]) == 4  # proceeded with partial (the other 4)
mock_sources.FAILING = set()  # reset
print("PHASE-3 TESTS OK")


# ---- Phase 4: provenance + conflict handling ----
out = asyncio.run(coord.run("AI in creative industries", scope=KNOWN, refine=False))
established = {e["subdomain"]: e for e in out["established"]}
# provenance preserved through synthesis
assert established["music"]["source"] == "musicbiz.example"
assert established["music"]["date"] == "2025-01"
# conflicting stats annotated with BOTH sources, not arbitrarily resolved
contested = {c["subdomain"]: c for c in out["contested"]}
assert {x["source"] for x in contested["film"]["sources"]} == {"a.example", "b.example"}
assert len(contested["film"]["sources"]) == 2
# report separates established vs contested, summary first
report = coord.run_report("AI in creative industries", out["findings"])
assert report.splitlines()[1].startswith("_established=") and "CONTESTED" in report
print("PHASE-4 TESTS OK")
