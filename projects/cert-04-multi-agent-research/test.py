import asyncio
import mock_sources
from main import build

coord = build()
KNOWN = list(mock_sources.KNOWN_SUBDOMAINS)


# ---- Phase 1: spawning + explicit context passing + fan-out ----
p1 = asyncio.run(
    coord.run("impact of AI on creative industries", scope=KNOWN, refine=False)
)
assert len(p1["findings"]) == len(
    KNOWN
)  # one subagent spawned per sub-domain (fan-out)
assert any(
    "musicbiz" in f["text"] for f in p1["findings"]
)  # a real upstream finding came back
# synthesis's text reflects every finding → the findings reached it (explicit context passing)
assert p1["synthesis"]["text"] == f"Overview built from {len(KNOWN)} findings."
print("PHASE-1 TESTS OK")


# ---- Phase 2: decomposition quality (reproduce narrow, then fix) ----
# Reproduce: narrow scope, no refinement → gaps even though subagents succeeded
narrow = asyncio.run(
    coord.run("AI in creative industries", scope=["visual"], refine=False)
)
assert narrow["covered"] == ["visual"]
assert set(narrow["gaps"]) == {"music", "film", "writing", "games"}, narrow["gaps"]

# Fix A: broad partition
broad = asyncio.run(coord.run("AI in creative industries", scope=KNOWN, refine=False))
assert broad["gaps"] == []

# Fix B: refinement loop closes the gaps
refined = asyncio.run(
    coord.run("AI in creative industries", scope=["visual"], refine=True)
)
assert refined["gaps"] == [] and refined["rounds"] >= 1, refined
print("PHASE-2 TESTS OK")


# verify_fact: scoped tool behavior
assert mock_sources.verify_fact("the AI music market grew")["verified"] is True
assert mock_sources.verify_fact("unrelated claim")["verified"] is False

coord = build()
assert coord.subagents["synthesis"].definition.allowed_tools == [
    "verify_fact"
]  # least privilege
assert "search" not in coord.subagents["synthesis"].definition.allowed_tools

# structured error propagation: make "film" search time out
mock_sources.FAILING = {"film"}
out = asyncio.run(
    coord.run(
        "AI in creative industries",
        scope=list(mock_sources.KNOWN_SUBDOMAINS),
        refine=False,
    )
)
assert out["failed"] == ["film"]  # error surfaced, not swallowed
e = out["errors"][0]
assert (
    e["failureType"] == "transient"
    and e["isRetryable"] is True
    and "attemptedQuery" in e
)
assert len(out["findings"]) == 4  # proceeded with partial (the other 4)
assert out["synthesis"]["text"].startswith(
    "Overview"
)  # workflow NOT killed — synthesis produced
mock_sources.FAILING = set()  # reset
print("PHASE-3 TESTS OK")
