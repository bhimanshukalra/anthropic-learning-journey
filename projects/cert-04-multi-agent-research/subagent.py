# subagent.py
# A "subagent" is one specialized worker (e.g. web search). It runs on an explicit prompt
# and returns a result dict. It has NO memory of the conversation — everything it needs must
# be passed in the prompt the coordinator gives it.

import asyncio
from dataclasses import dataclass, field

# How long a stubbed subagent pretends to "work" — makes parallel-vs-sequential visible.
STUB_LATENCY_S = 0.5


@dataclass
class AgentDefinition:
    """Describes a subagent: its name, system prompt, and the tools it may use."""
    name: str
    system: str
    allowed_tools: list[str] = field(default_factory=list)  # least privilege: only what it needs


class Subagent:
    def __init__(self, definition: AgentDefinition, claude=None, stub_responder=None):
        self.definition = definition
        self.claude = claude  # None = stub mode (use stub_responder instead of a model)
        self.stub_responder = stub_responder  # function that produces fake output in stub mode

    async def run(self, prompt: str) -> dict:
        """Run the subagent on one explicit prompt; return a result dict."""
        # --- Stub mode: use the fake responder. ---
        if self.claude is None:
            await asyncio.sleep(STUB_LATENCY_S)  # pretend the work took real time
            res = (
                self.stub_responder(prompt)
                if self.stub_responder
                else f"[stub: {self.definition.name}]"
            )
            # A responder may return a dict (structured records / error) or a plain string.
            return (
                {"agent": self.definition.name, **res}
                if isinstance(res, dict)
                else {"agent": self.definition.name, "text": res}
            )
        # --- Real mode: call the model. ---
        msg = self.claude.chat(
            messages=[{"role": "user", "content": prompt}],
            system=self.definition.system,
        )
        return {
            "agent": self.definition.name,
            "text": self.claude.text_from_message(msg),
        }
