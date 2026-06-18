import asyncio
from main import build

coord = build()
out = asyncio.run(coord.run("impact of AI on creative industries", parallel=True))

assert len(out["findings"]) == 4, out  # decomposed into 4 sub-domains, all spawned
assert "FINDINGS:" in out["synth_prompt"]  # explicit context handed to synthesis
assert "musicbiz" in out["synth_prompt"]  # an actual upstream finding reached synthesis
assert out["synthesis"]["text"] == "Overview built from 4 findings."
print("PHASE-1 TESTS OK")
