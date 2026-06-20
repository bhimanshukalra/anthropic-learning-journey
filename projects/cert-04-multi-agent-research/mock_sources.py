# mock_sources.py
# A fake "internet" for the research agents — pure Python data, no network calls.
# Each sub-topic maps to a list of source "records".

# topic -> list of {claim, source, date} records the web_search agent can return.
# "film" deliberately holds TWO conflicting records so we can test conflict handling.
_CORPUS = {
    "music": [
        {"claim": "AI music market grew sharply in 2025", "source": "musicbiz.example", "date": "2025-01"}
    ],
    "film": [
        {"claim": "AI VFX adoption ~30%", "source": "a.example", "date": "2024-11"},
        {"claim": "AI VFX adoption ~55%", "source": "b.example", "date": "2025-04"},  # CONFLICT
    ],
    "writing": [
        {"claim": "Publishers piloting AI drafting", "source": "pubweekly.example", "date": "2025-03"}
    ],
    "visual": [
        {"claim": "Generative art went mainstream", "source": "artnews.example", "date": "2024-09"}
    ],
    "games": [
        {"claim": "Studios testing AI NPCs", "source": "gamedev.example", "date": "2025-02"}
    ],
}

# Every topic we know about — the coordinator compares against this to find coverage gaps.
KNOWN_SUBDOMAINS = list(_CORPUS)

# Test switch: any topic listed here makes search() "time out" (simulates a flaky backend).
FAILING: set[str] = set()


# Raised by search() to simulate a transient backend/network failure.
class SourceTimeout(Exception):
    pass


def search(query: str) -> list[dict]:
    """Look up sources for a topic."""
    q = query.lower()
    if any(sd in q for sd in FAILING):  # simulate an outage for the chosen topic
        raise SourceTimeout("source service unreachable")
    for sd in KNOWN_SUBDOMAINS:  # return the matching topic's records...
        if sd in q:
            return _CORPUS[sd]
    return []  # ...or an empty list (a valid "no results", NOT an error)


def verify_fact(claim: str) -> dict:
    """A small, scoped fact-checker the synthesis agent is allowed to use."""
    q = claim.lower()
    for sd, recs in _CORPUS.items():  # claim mentions a known topic -> verified, with its sources
        if sd in q:
            return {"verified": True, "sources": recs}
    return {"verified": False, "sources": []}
