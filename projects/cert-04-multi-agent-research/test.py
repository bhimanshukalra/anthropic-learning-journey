# Checks for the whole pipeline. Each block exercises one capability and prints
# "... TESTS OK" if its asserts pass. Run: python test.py

import asyncio
import mock_sources
from main import build

coord = build()  # stub mode
KNOWN = list(mock_sources.KNOWN_SUBDOMAINS)


# ---- fan-out: the coordinator spawns one subagent per sub-topic ----
p1 = asyncio.run(coord.run("impact of AI on creative industries", scope=KNOWN, refine=False))
assert len(p1["findings"]) == len(KNOWN)  # one result per topic
assert all(f.get("records") for f in p1["findings"])  # each came back with sources
print("FAN-OUT TESTS OK")


# ---- decomposition: a narrow scope leaves gaps; broad scope / refinement fills them ----
narrow = asyncio.run(coord.run("AI in creative industries", scope=["visual"], refine=False))
assert narrow["covered"] == ["visual"]  # only the one topic we asked for
assert set(narrow["gaps"]) == {"music", "film", "writing", "games"}, narrow["gaps"]

broad = asyncio.run(coord.run("AI in creative industries", scope=KNOWN, refine=False))
assert broad["gaps"] == []  # asking for everything leaves no gaps

refined = asyncio.run(coord.run("AI in creative industries", scope=["visual"], refine=True))
assert refined["gaps"] == [] and refined["rounds"] >= 1, refined  # loop closed the gaps
print("DECOMPOSITION TESTS OK")


# ---- scoped tool: synthesis may use verify_fact only (no web search) ----
assert mock_sources.verify_fact("the AI music market grew")["verified"] is True
assert mock_sources.verify_fact("unrelated claim")["verified"] is False
assert coord.subagents["synthesis"].definition.allowed_tools == ["verify_fact"]
assert "search" not in coord.subagents["synthesis"].definition.allowed_tools

# ---- structured errors: a timeout is recovered, and the run continues with partial results ----
mock_sources.FAILING = {"film"}  # make "film" search time out
err_out = asyncio.run(coord.run("AI in creative industries", scope=KNOWN, refine=False))
assert err_out["failed"] == ["film"]  # the failure is surfaced, not hidden
e = err_out["errors"][0]
assert e["failureType"] == "transient" and e["isRetryable"] is True and "attemptedQuery" in e
assert len(err_out["findings"]) == 4  # the other 4 topics still came through
mock_sources.FAILING = set()  # reset
print("TOOLS & ERRORS TESTS OK")


# ---- provenance: sources survive synthesis; conflicts keep BOTH sides ----
out = asyncio.run(coord.run("AI in creative industries", scope=KNOWN, refine=False))
established = {e["subdomain"]: e for e in out["established"]}
assert established["music"]["source"] == "musicbiz.example"  # source kept
assert established["music"]["date"] == "2025-01"  # date kept
contested = {c["subdomain"]: c for c in out["contested"]}
assert {x["source"] for x in contested["film"]["sources"]} == {"a.example", "b.example"}
assert len(contested["film"]["sources"]) == 2  # both conflicting sources retained
report = coord.run_report("AI in creative industries", out["findings"])
assert report.splitlines()[1].startswith("_established=") and "CONTESTED" in report
print("PROVENANCE TESTS OK")
