# coordinator.py
# The coordinator is the "brain" of the pipeline. Given a research query it:
#   1. splits the query into sub-topics            -> decompose()
#   2. runs a web_search subagent for each, at once -> research()  (parallel)
#   3. retries transient failures, keeps the rest   -> research()/run()
#   4. merges results into a sourced report,
#      keeping each claim's source and flagging conflicts -> synthesize()/run_report()

import asyncio
import mock_sources


class Coordinator:
    def __init__(self, subagents: dict):
        self.subagents = subagents  # name -> Subagent the coordinator can call

    def decompose(self, query: str, scope: list[str]) -> list[dict]:
        """Turn one query into a search task per sub-topic in `scope` (goals, not procedures)."""
        return [
            {
                "agent": "web_search",
                "subdomain": sd,
                "prompt": f"Goal: find dated, credible sources on {sd} for: {query}.",
            }
            for sd in scope
        ]

    async def spawn(self, agent: str, prompt: str) -> dict:
        """Call one subagent by name — our stand-in for the SDK's 'Task' tool."""
        return await self.subagents[agent].run(prompt)

    async def research(self, query: str, scope: list[str]) -> list[dict]:
        """Run every search task at once, tag each result with its topic, retry flaky ones."""
        tasks = self.decompose(query, scope)
        # asyncio.gather runs all the spawns in parallel (one step, many calls).
        findings = await asyncio.gather(
            *(self.spawn(t["agent"], t["prompt"]) for t in tasks)
        )
        for t, f in zip(tasks, findings):  # remember which topic each finding is for
            f["subdomain"] = t["subdomain"]
        # Local recovery: retry a transient (retryable) error once before giving up on it.
        for i, (t, f) in enumerate(zip(tasks, findings)):
            if f.get("isError") and f.get("isRetryable"):
                r = await self.spawn(t["agent"], t["prompt"])
                r["subdomain"] = t["subdomain"]
                findings[i] = r
        return findings

    def covered(self, findings: list[dict]) -> set:
        """Which topics actually came back with sources (ignore errors and empty results)."""
        return {
            f["subdomain"]
            for f in findings
            if not f.get("isError") and f.get("records")
        }

    def synthesize(self, query: str, findings: list[dict]) -> dict:
        """Merge findings while KEEPING each claim's source; sort into established vs contested."""
        established, contested = [], []
        for f in findings:
            recs = f.get("records", [])
            if not recs:
                continue
            # More than one source that disagree = a conflict: keep BOTH, never pick one.
            if len(recs) > 1 and len({r["claim"] for r in recs}) > 1:
                contested.append({"subdomain": f["subdomain"], "sources": recs})
            else:  # single agreed source = established; keep its claim+source+date
                established.append({"subdomain": f["subdomain"], **recs[0]})
        return {"query": query, "established": established, "contested": contested}

    def run_report(self, query: str, findings: list[dict]) -> str:
        """Render the synthesized result as a readable text report (summary line first)."""
        r = self.synthesize(query, findings)
        lines = [
            f"# {query}",
            f"_established={len(r['established'])} contested={len(r['contested'])}_",  # summary up top
        ]
        # One line per established finding, with its citation.
        lines += [
            f"- [{e['subdomain']}] {e['claim']} ({e['source']}, {e['date']})"
            for e in r["established"]
        ]
        # Contested topics show both sides side by side.
        for c in r["contested"]:
            both = " vs ".join(
                f"{x['claim']} ({x['source']}, {x['date']})" for x in c["sources"]
            )
            lines.append(f"- [{c['subdomain']} — CONTESTED] {both}")
        return "\n".join(lines)

    async def run(
        self, query: str, scope: list[str], refine: bool = False, max_rounds: int = 3
    ) -> dict:
        """Top-level: research the scope, optionally fill coverage gaps, return the report + diagnostics."""
        findings = await self.research(query, scope)

        # Refinement loop: keep re-searching any uncovered topics until none remain (or cap hit).
        rounds = 0
        while refine and rounds < max_rounds:
            gaps = set(mock_sources.KNOWN_SUBDOMAINS) - self.covered(findings)
            if not gaps:
                break
            findings += await self.research(query, sorted(gaps))
            rounds += 1

        # Separate successes from errors so one failure can't sink the whole run.
        ok = [f for f in findings if not f.get("isError")]
        errors = [f for f in findings if f.get("isError")]
        failed = sorted({f["subdomain"] for f in errors})
        report = self.synthesize(query, ok)  # build the sourced report from what succeeded
        covered = self.covered(findings)
        return {
            "query": query,
            "findings": ok,
            "errors": errors,
            "failed": failed,  # topics we couldn't fetch (even after a retry)
            "covered": sorted(covered),  # topics we did fetch
            "gaps": sorted(set(mock_sources.KNOWN_SUBDOMAINS) - covered),  # topics still missing
            "established": report["established"],
            "contested": report["contested"],
            "rounds": rounds,  # how many refinement passes it took
        }
