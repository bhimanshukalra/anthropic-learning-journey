import asyncio
from subagent import AgentDefinition, Subagent
from coordinator import Coordinator


def build(claude=None):
    defs = {
        "web_search": AgentDefinition(
            "web_search", "Find credible, dated sources.", ["search"]
        )
    }
    subagents = {name: Subagent(d, claude=claude) for name, d in defs.items()}
    return Coordinator(subagents)


if __name__ == "__main__":
    coord = build()
    out = asyncio.run(coord.run("impact of AI on creative industries"))
    print(out)
