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
        return findings

    def covered(self, findings: list[dict]) -> set:
        return {f["subdomain"] for f in findings if "no sources found" not in f["text"]}

    async def gather_findings(
        self, tasks: list[dict], parallel: bool = True
    ) -> list[dict]:
        if parallel:
            return await asyncio.gather(
                *(self.spawn(t["agent"], t["prompt"]) for t in tasks)
            )
        out = []
        for t in tasks:
            out.append(await self.spawn(t["agent"], t["prompt"]))
        return out

    async def run(
        self, query: str, scope: list[str], refine: bool = True, max_rounds: int = 3
    ) -> dict:
        findings = await self.research(query, scope)
        rounds = 0
        while refine and rounds < max_rounds:
            gaps = set(mock_sources.KNOWN_SUBDOMAINS) - self.covered(findings)
            if not gaps:
                break
            findings += await self.research(query, sorted(gaps))

            rounds += 1

        gaps = sorted(set(mock_sources.KNOWN_SUBDOMAINS) - self.covered(findings))
        joined = "\n".join(f"- {f['subdomain']}: {f['text']}" for f in findings)
        synth_prompt = (
            f"Synthesize a cited overview for: {query}\nFINDINGS:\n{joined}\n"
            f"COVERAGE: covered={sorted(self.covered(findings))} gaps={gaps}"
        )
        synthesis = await self.spawn("synthesis", synth_prompt)
        return {
            "query": query,
            "findings": findings,
            "covered": sorted(self.covered(findings)),
            "gaps": gaps,
            "rounds": rounds,
            "synthesis": synthesis,
        }
