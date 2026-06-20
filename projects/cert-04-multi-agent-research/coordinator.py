import asyncio
import mock_sources


class Coordinator:
    def __init__(self, subagents: dict):
        self.subagents = subagents

    def decompose(self, query: str, scope: list[str]) -> list[dict]:
        """Goals, not procedures. SCOPE is the decomposition lever (Phase 2)."""
        return [
            {
                "agent": "web_search",
                "subdomain": sd,
                "prompt": f"Goal: find dated, credible sources on {sd} for: {query}.",
            }
            for sd in scope
        ]

    async def spawn(self, agent: str, prompt: str) -> dict:
        return await self.subagents[agent].run(prompt)

    async def research(self, query: str, scope: list[str]) -> list[dict]:
        tasks = self.decompose(query, scope)
        findings = await asyncio.gather(
            *(self.spawn(t["agent"], t["prompt"]) for t in tasks)
        )
        for t, f in zip(tasks, findings):
            f["subdomain"] = t["subdomain"]
        # local recovery: retry a transient error once before propagating (Phase 3)
        for i, (t, f) in enumerate(zip(tasks, findings)):
            if f.get("isError") and f.get("isRetryable"):
                r = await self.spawn(t["agent"], t["prompt"])
                r["subdomain"] = t["subdomain"]
                findings[i] = r
        return findings

    def covered(self, findings: list[dict]) -> set:
        return {
            f["subdomain"]
            for f in findings
            if not f.get("isError") and f.get("records")
        }

    def synthesize(self, query: str, findings: list[dict]) -> dict:
        """Preserve claim→source through merge; split established vs contested (Phase 4)."""
        established, contested = [], []
        for f in findings:
            recs = f.get("records", [])
            if not recs:
                continue
            if len(recs) > 1 and len({r["claim"] for r in recs}) > 1:  # conflicting credible stats
                contested.append({"subdomain": f["subdomain"], "sources": recs})  # annotate BOTH
            else:
                established.append({"subdomain": f["subdomain"], **recs[0]})  # keep claim+source+date
        return {"query": query, "established": established, "contested": contested}

    def run_report(self, query: str, findings: list[dict]) -> str:
        r = self.synthesize(query, findings)
        lines = [
            f"# {query}",
            f"_established={len(r['established'])} contested={len(r['contested'])}_",  # summary FIRST
        ]
        lines += [
            f"- [{e['subdomain']}] {e['claim']} ({e['source']}, {e['date']})"
            for e in r["established"]
        ]
        for c in r["contested"]:
            both = " vs ".join(
                f"{x['claim']} ({x['source']}, {x['date']})" for x in c["sources"]
            )
            lines.append(f"- [{c['subdomain']} — CONTESTED] {both}")
        return "\n".join(lines)

    async def run(
        self, query: str, scope: list[str], refine: bool = False, max_rounds: int = 3
    ) -> dict:
        findings = await self.research(query, scope)
        rounds = 0
        while refine and rounds < max_rounds:  # Phase 2 refinement loop
            gaps = set(mock_sources.KNOWN_SUBDOMAINS) - self.covered(findings)
            if not gaps:
                break
            findings += await self.research(query, sorted(gaps))
            rounds += 1

        ok = [f for f in findings if not f.get("isError")]
        errors = [f for f in findings if f.get("isError")]  # Phase 3: proceed with partial
        failed = sorted({f["subdomain"] for f in errors})
        report = self.synthesize(query, ok)  # Phase 4: provenance-preserving report
        covered = self.covered(findings)
        return {
            "query": query,
            "findings": ok,
            "errors": errors,
            "failed": failed,
            "covered": sorted(covered),  # Phase 2: which sub-domains came back
            "gaps": sorted(set(mock_sources.KNOWN_SUBDOMAINS) - covered),
            "established": report["established"],
            "contested": report["contested"],
            "rounds": rounds,
        }
