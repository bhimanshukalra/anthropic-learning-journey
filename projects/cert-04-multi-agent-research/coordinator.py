import asyncio


class Coordinator:
    def __init__(self, subagents: dict):
        self.subagents = subagents

    def decompose(self, query: str) -> list[dict]:
        """Query -> [{agent, prompt}]"""
        return [{"agent": "web_search", "prompt": f"Find sources on: {query}"}]

    async def spawn(self, agent: str, prompt: str) -> dict:
        return await self.subagents[agent].run(prompt)

    async def run(self, query: str) -> dict:
        tasks = self.decompose(query)
        # parallel = ONE step, MANY spawns, gather, don't await in a loop
        results = await asyncio.gather(
            *(self.spawn(t["agent"], t["prompt"]) for t in tasks)
        )
        return {"query": query, "results": results}
