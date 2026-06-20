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

KNOWN_SUBDOMAINS = list(_CORPUS)
FAILING: set[str] = set()  # sub-domains whose search times out (tests set this)


class SourceTimeout(Exception):
    pass


def search(query: str) -> list[dict]:
    """Return structured claim→source records for a sub-domain, or raise a (simulated) timeout."""
    q = query.lower()
    if any(sd in q for sd in FAILING):
        raise SourceTimeout("source service unreachable")
    for sd in KNOWN_SUBDOMAINS:
        if sd in q:
            return _CORPUS[sd]
    return []


def verify_fact(claim: str) -> dict:
    """Scoped fact-check: match a claim to its sub-domain's records (no full web toolset)."""
    q = claim.lower()
    for sd, recs in _CORPUS.items():
        if sd in q:
            return {"verified": True, "sources": recs}
    return {"verified": False, "sources": []}
