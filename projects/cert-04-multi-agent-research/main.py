import asyncio
from subagent import AgentDefinition, Subagent
from coordinator import Coordinator
import mock_sources


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
    out = asyncio.run(coord.run(q, scope=["visual"], refine=True))
    print(out["synthesis"]["text"])
    print(f"covered={out['covered']} gaps={out['gaps']} rounds={out['rounds']}")
