# Entry point + wiring for the multi-agent research pipeline.
#
# THE BIG PICTURE
#   A Coordinator splits a question into sub-topics, runs a web_search Subagent for each
#   (in parallel), retries flaky ones, then synthesizes a sourced report that flags
#   conflicting facts. It uses stub data from mock_sources.py.
#
#   Files:  mock_sources.py = fake web data | subagent.py = one worker
#           coordinator.py = the brain       | this file  = wiring + a demo run
#
# Run it:  python main.py   (or: uv run python main.py)

import asyncio
import time
from subagent import AgentDefinition, Subagent
from coordinator import Coordinator
import mock_sources


async def measure_latency(coord, query, scope):
    """Time parallel vs sequential research so the fan-out win (Step 2) is observable.

    With N topics each taking ~STUB_LATENCY_S, sequential ≈ N×latency (they add up) while
    parallel ≈ 1×latency (they overlap). Returns (parallel_s, sequential_s, speedup)."""
    t0 = time.perf_counter()
    await coord.research(query, scope)
    parallel = time.perf_counter() - t0

    t0 = time.perf_counter()
    await coord.research_sequential(query, scope)
    sequential = time.perf_counter() - t0

    return parallel, sequential, sequential / parallel


def _web_search_stub(prompt: str):
    """Fake 'web search' used in stub mode: return a topic's records, or a structured
    error envelope if mock_sources says that topic is timing out."""
    for sd in mock_sources.KNOWN_SUBDOMAINS:
        if sd in prompt.lower():
            try:
                return {"records": mock_sources.search(sd)}
            except mock_sources.SourceTimeout:
                # Errors are structured data the coordinator can act on (retry/skip), not crashes.
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
    """Assemble the coordinator and its subagents (claude=None -> stub mode)."""
    # Each role gets only the tools it needs (least privilege).
    defs = {
        "web_search": AgentDefinition(
            "web_search", "Find credible, dated sources.", ["search"]
        ),
        "synthesis": AgentDefinition(
            "synthesis", "Combine findings; verify simple claims.", ["verify_fact"]
        ),
    }
    stubs = {"web_search": _web_search_stub}  # web_search uses the fake search above
    subagents = {
        n: Subagent(d, claude=claude, stub_responder=stubs.get(n))
        for n, d in defs.items()
    }
    return Coordinator(subagents)


if __name__ == "__main__":
    # Demo: research every topic and print the sourced report.
    coord = build()  # no claude -> stub mode
    q = "impact of AI on creative industries"
    scope = list(mock_sources.KNOWN_SUBDOMAINS)
    findings = asyncio.run(coord.research(q, scope))
    print(coord.run_report(q, findings))

    # Step 2: show the parallel fan-out actually beats sequential on wall-clock.
    par, seq, speedup = asyncio.run(measure_latency(coord, q, scope))
    print(
        f"\n_latency over {len(scope)} subagents: "
        f"parallel={par:.2f}s sequential={seq:.2f}s -> {speedup:.1f}x faster_"
    )
