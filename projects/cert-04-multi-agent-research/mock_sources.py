_CORPUS = {
    "music": "AI music tools surged (musicbiz.example, 2025-01).",
    "film": "Studios pilot AI VFX pipelines (filmtech.example, 2024-11).",
    "writing": "Publishers debate AI-assisted drafting (pubweekly.example, 2025-03).",
    "visual": "Generative art went mainstream (artnews.example, 2024-09).",
    "games": "Studios test AI NPCs and asset generation (gamedev.example, 2025-02).",
}

KNOWN_SUBDOMAINS = list(_CORPUS)
FAILING: set[str] = set()


class SourceTimeout(Exception):
    pass


def search(query: str) -> str:
    q = query.lower()
    if any(sd in q for sd in FAILING):
        raise SourceTimeout("order service unreachable")
    hits = [v for k, v in _CORPUS.items() if k in q]
    return " | ".join(hits) if hits else "(no sources found)"


def search(query: str) -> str:
    q = query.lower()
    hits = [v for k, v in _CORPUS.items() if k in q]
    return " | ".join(hits) if hits else "(no sources found)"


def verify_fact(claim: str) -> dict:
    q = claim.lower()
    for sd, txt in _CORPUS.items():
        if sd in q:
            return {"verified": True, "source": txt}
    return {"verified": False, "source": None}
