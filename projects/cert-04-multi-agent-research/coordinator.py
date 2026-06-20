import asyncio
import mock_sources


class Coordinator:
    def __init__(self, subagents: dict):
        self.subagents = subagents

    def decompose(self, query: str, scope: list[str]) -> list[dict]:
        """Goals, not procedures SCOPE is the lever this phase is about."""
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

        for i, (t, f) in enumerate(zip(tasks, findings)):
            if f.get("isError") and f.get("isRetryable"):
                r = await self.spawn(t["agent"], t["prompt"])
                r["subdomain"] = t["subdomain"]
                findings = r

        return findings

    def covered(self, findings: list[dict]) -> set:
        return {
            f["subdomain"]
            for f in findings
            if not f.get("isError") and "no sources found" not in f.get("text", "")
        }

    async def run(
        self, query: str, scope: list[str], refine: bool = False, max_rounds: int = 3
    ) -> dict:
        findings = await self.research(query, scope)
        rounds = 0
        while refine and rounds < max_rounds:
            gaps = set(mock_sources.KNOWN_SUBDOMAINS) - self.covered(findings)
            if not gaps:
                break
            findings += await self.research(query, sorted(gaps))
            rounds += 1

        ok = [f for f in findings if not f.get("isError")]
        errors = [f for f in findings if f.get("isError")]
        failed = sorted({f["subdomain"] for f in errors})
        joined = "\n".join(f"- {f['subdomain']}: {f['text']}" for f in ok)
        note = (
            f"\nCOVERAGE NOTE: search errors on {failed} (retried, proceeding with partial)."
            if errors
            else ""
        )

        synthesis = await self.spawn(
            "synthesis", f"Synthesize for: {query}\nFINDINGS:\n{joined}{note}"
        )
        return {
            "query": query,
            "findings": ok,
            "errors": errors,
            "failed": failed,
            "synthesis": synthesis,
        }
