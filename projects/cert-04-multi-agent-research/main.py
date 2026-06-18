import asyncio, time
from subagent import AgentDefinition, Subagent
from coordinator import Coordinator
import mock_sources


async def _timed(coord, query, parallel):
    t0 = time.perf_counter()
    out = await coord.run(query, parallel=parallel)
    return out, time.perf_counter() - t0


def build(claude=None):
    defs = {
        "web_search": AgentDefinition(
            "web_search", "Find credible, dated sources.", ["search"]
        ),
        "synthesis": AgentDefinition(
            "synthesis", "Combine findings into a cited overview.", ["verify_fact"]
        ),
    }
    stubs = {
        "web_search": lambda p: mock_sources.search(p),
        "synthesis": lambda p: f"Overview built from {p.count("- ")} findings.",
    }
    subagents = {
        n: Subagent(d, claude=claude, stub_responder=stubs.get(n))
        for n, d in defs.items()
    }
    return Coordinator(subagents)


if __name__ == "__main__":
    coord = build()
    q = "impact of AI on creative industries"
    par, t_par = asyncio.run(_timed(coord, q, parallel=True))
    seq, t_seq = asyncio.run(_timed(coord, q, parallel=False))
    print(par["synthesis"]["text"])
    print(f"parallel={t_par:.2f}s sequential={t_seq:.2f}s")
