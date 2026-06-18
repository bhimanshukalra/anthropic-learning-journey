import asyncio
from dataclasses import dataclass, field

STUB_LATENCY_S = 0.5


@dataclass
class AgentDefinition:
    name: str
    system: str
    allowed_tools: list[str] = field(default_factory=list)


class Subagent:
    def __init__(self, definition: AgentDefinition, claude=None, stub_responder=None):
        self.definition = definition
        self.claude = claude
        self.stub_responder = stub_responder

    async def run(self, prompt: str) -> dict:
        """Run on an explicit prompt."""
        if self.claude is None:
            await asyncio.sleep(STUB_LATENCY_S)
            text = (
                self.stub_responder(prompt)
                if self.stub_responder
                else f"[stub: {self.definition.name}]"
            )
            return {"agent": self.definition.name, "text": text}
        msg = self.claude.chat(
            messages=[{"role": "user", "content": prompt}],
            system=self.definition.system,
        )

        return {
            "agent": self.definition.name,
            "text": self.claude.text_from_message(msg),
        }
