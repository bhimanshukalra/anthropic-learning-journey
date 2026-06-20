import asyncio
from subagent import AgentDefinition, Subagent
from coordinator import Coordinator
import mock_sources


def _web_search_stub(prompt: str):
    """Return structured records, or a structured error envelope on a (simulated) timeout."""
    for sd in mock_sources.KNOWN_SUBDOMAINS:
        if sd in prompt.lower():
            try:
                return {"records": mock_sources.search(sd)}
            except mock_sources.SourceTimeout:
                return {
                    "isError": True,
                    "failureType": "transient",
                    "attemptedQuery": prompt,
                    "partialResults": [],
                    "suggestedAlternatives": ["retry", "narrow date range"],
                    "isRetryable": True,
                }
    return {"records": []}


def build(claude=None):
    defs = {
        "web_search": AgentDefinition(
            "web_search", "Find credible, dated sources.", ["search"]
        ),
        "synthesis": AgentDefinition(
            "synthesis", "Combine findings; verify simple claims.", ["verify_fact"]
        ),
    }
    stubs = {"web_search": _web_search_stub}
    subagents = {
        n: Subagent(d, claude=claude, stub_responder=stubs.get(n))
        for n, d in defs.items()
    }
    return Coordinator(subagents)


if __name__ == "__main__":
    coord = build()  # no claude → stub mode, no credits
    q = "impact of AI on creative industries"
    findings = asyncio.run(coord.research(q, list(mock_sources.KNOWN_SUBDOMAINS)))
    print(coord.run_report(q, findings))
