import json
from anthropic.types import Message
from core.claude import Claude
from mcp_client import MCPClient

SYSTEM = """You are a customer-support resolution agent. Use the tools to look up customers and orders and answer the user. Pick the single most appropriate tool for each step."""

GATED_TOOLS = {"lookup_order", "process_refund"}


class SupportAgent:
    def __init__(self, claude: Claude, client: MCPClient):
        self.claude = claude
        self.client = client
        self.messages: list = []
        self.verified_customer_id: str | None = None  # latched one, in code

    def _gate(self, tool_name: str) -> dict | None:
        """Return an error envelope if this call must be blocked, else None. Pure + testable."""
        if tool_name in GATED_TOOLS and self.verified_customer_id is None:
            return {
                "isError": True,
                "errorCategory": "permission",
                "isRetryable": False,
                "message": (
                    "Identity not verified. Call get_customer and confirm a SINGLE "
                    "matching customer before looking up orders or issuing refunds."
                ),
            }
        return None

    def _latch_verification(self, tool_name: str, result_text: str) -> None:
        """After get_customer, latch the id ONLY when exactly one customer matched."""
        if tool_name != "get_customer":
            return
        data = json.loads(result_text)
        if data.get("count") == 1:  # ambiguous (0 or >1) does NOT verify
            self.verified_customer_id = data["matches"][0]["id"]

    async def _tool_schemas(self) -> list[dict]:
        tools = await self.client.list_tools()
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.inputSchema,
            }
            for t in tools
        ]

    async def _run_tools(self, response: Message) -> list[dict]:
        """Execute every tool_use block the model emitted; return tool_result blocks."""
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            print(f"tool_use: {block.name}({json.dumps(block.input)})")

            blocked = self._gate(block.name)
            if blocked is not None:
                print(f"⛔ gated: {block.name} (no verified customer)")
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(blocked),
                        "is_error": True,
                    }
                )
                continue

            output = await self.client.call_tool(block.name, block.input)
            text = output.content[0].text if output and output.content else "{}"

            self._latch_verification(block.name, text)
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": text,
                    "is_error": self._is_error_envelope(text),
                }
            )

        return results

    @staticmethod
    def _is_error_envelope(text: str) -> bool:
        """True if a tool returned the isError envelope (so the API marks the result as an error.)"""
        try:
            return bool(json.loads(text).get("isError"))
        except (ValueError, AttributeError):
            return False

    async def run(self, user_text: str, max_steps: int = 8) -> str:
        self.messages.append({"role": "user", "content": user_text})
        tools = await self._tool_schemas()

        for _ in range(max_steps):  # runaway guard, NOT the stop condition
            response = self.claude.chat(
                messages=self.messages, system=SYSTEM, tools=tools
            )
            self.messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "tool_use":  # the real driver
                tool_results = await self._run_tools(response)
                self.messages.append({"role": "user", "content": tool_results})
                continue

            # stop_reason == "end_turn" (or any non-tool stop) -> we're done
            return self.claude.text_from_message(response)
        return "Stopped after too many steps - please rephrase or contact support."
