from dataclasses import dataclass, field


@dataclass
class AgentDefinition:
    name: str
    system: str
    allowed_tools: list[str] = field(default_factory=list)


class Subagent:
    def __init__(self, definition: AgentDefinition, claude=None):
        self.definition = definition
        self.claude = claude

    async def run(self, prompt: str) -> dict:
        """Run on an explicit prompt. Stub mode returns deterministic output - zero credits"""
        if self.claude is None:
            return {"agent": self.definition.name, "stub": True, "saw": prompt[:60]}
        msg = self.claude.chat(
            messages=[{"role": "user", "content": prompt}],
            system=self.definition.system,
        )

        return {
            "agent": self.definition.name,
            "text": self.claude.text_from_message(msg),
        }
