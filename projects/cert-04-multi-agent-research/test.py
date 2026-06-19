import asyncio
import mock_sources
from main import build

coord = build()
KNOWN = list(mock_sources.KNOWN_SUBDOMAINS)


# ---- Phase 1: spawning + explicit context passing + fan-out ----
p1 = asyncio.run(coord.run("impact of AI on creative industries", scope=KNOWN, refine=False))
assert len(p1["findings"]) == len(KNOWN)  # one subagent spawned per sub-domain (fan-out)
assert any("musicbiz" in f["text"] for f in p1["findings"])  # a real upstream finding came back
# synthesis's text reflects every finding → the findings reached it (explicit context passing)
assert p1["synthesis"]["text"] == f"Overview built from {len(KNOWN)} findings."
print("PHASE-1 TESTS OK")


# ---- Phase 2: decomposition quality (reproduce narrow, then fix) ----
# Reproduce: narrow scope, no refinement → gaps even though subagents succeeded
narrow = asyncio.run(coord.run("AI in creative industries", scope=["visual"], refine=False))
assert narrow["covered"] == ["visual"]
assert set(narrow["gaps"]) == {"music", "film", "writing", "games"}, narrow["gaps"]

# Fix A: broad partition
broad = asyncio.run(coord.run("AI in creative industries", scope=KNOWN, refine=False))
assert broad["gaps"] == []

# Fix B: refinement loop closes the gaps
refined = asyncio.run(coord.run("AI in creative industries", scope=["visual"], refine=True))
assert refined["gaps"] == [] and refined["rounds"] >= 1, refined
print("PHASE-2 TESTS OK")
