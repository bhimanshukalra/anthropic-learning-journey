import asyncio


class Coordinator:
    def __init__(self, subagents: dict):
        self.subagents = subagents

    def decompose(self, query: str) -> list[dict]:
        """Goals, not procedures."""
        subdomains = ["music", "film", "writing", "visual"]
        return [
            {
                "agent": "web_search",
                "prompt": f"Goal: find dated, credible sources on {sd} for: {query}.",
            }
            for sd in subdomains
        ]

    async def spawn(self, agent: str, prompt: str) -> dict:
        return await self.subagents[agent].run(prompt)

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

    async def run(self, query: str, parallel: bool = True) -> dict:
        tasks = self.decompose(query)
        findings = await self.gather_findings(tasks, parallel=parallel)
        joined = "\n".join(f"- {f['agent']}: {f['text']}" for f in findings)
        synth_prompt = f"Synthesize a cited overview for: {query}\nFINDINGS:\n{joined}"
        synthesis = await self.spawn("synthesis", synth_prompt)
        return {
            "query": query,
            "findings": findings,
            "synthesis": synthesis,
            "synth_prompt": synth_prompt,
        }
