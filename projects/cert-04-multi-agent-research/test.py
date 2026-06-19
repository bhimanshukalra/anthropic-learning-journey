import asyncio
from main import build

coord = build()
out = asyncio.run(
    coord.run("impact of AI on creative industries", scope=["visual"], refine=False)
)

assert len(out["findings"]) == 4, out  # decomposed into 4 sub-domains, all spawned
assert "FINDINGS:" in out["synth_prompt"]  # explicit context handed to synthesis
assert "musicbiz" in out["synth_prompt"]  # an actual upstream finding reached synthesis
assert out["synthesis"]["text"] == "Overview built from 4 findings."
print("PHASE-1 TESTS OK")

# Reproduce: narrow scope, no refinement → gaps even though subagents succeeded
narrow = asyncio.run(
    coord.run("AI in creative industries", scope=["visual"], refine=False)
)
assert narrow["covered"] == ["visual"]
assert set(narrow["gaps"]) == {"music", "film", "writing", "games"}, narrow["gaps"]

# Fix A: broad partition
broad = asyncio.run(
    coord.run(
        "AI in creative industries",
        scope=list(__import__("mock_sources").KNOWN_SUBDOMAINS),
        refine=False,
    )
)
assert broad["gaps"] == []

# Fix B: refinement loop closes the gaps
refined = asyncio.run(
    coord.run("AI in creative industries", scope=["visual"], refine=True)
)
assert refined["gaps"] == [] and refined["rounds"] >= 1, refined
print("PHASE-2 TESTS OK")
