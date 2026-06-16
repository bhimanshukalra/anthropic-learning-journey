import json
from anthropic.types import Message
from core.claude import Claude
from mcp_client import MCPClient

SYSTEM = """You are a customer-support resolution agent. Use the tools to look up customers and orders and answer the user. Pick the single most appropriate tool for each step."""

class SupportAgent:
    def __init__(self, claude: Claude, client: MCPClient):
        self.claude = claude
        self.client = client
        self.messages: list = []

    async def _tool_schemas(self) -> list[dict]:
        tools = await self.client.list_tools()
        return [{"name": t.name, "description": t.description, "input_schema": t.inputSchema } for t in tools]
    
    async def _run_tools(self, response: Message) -> list[dict]:
        """Execute every tool_use block the model emitted; return tool_result blocks."""
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            print(f"tool_use: {block.name}({json.dumps(block.input)})")
            output = await self.client.call_tool(block.name, block.input)
            text = output.content[0].text if output and output.content else "{}"
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": text})

        return results
    
    async def run(self, user_text: str) -> str:
        self.messages.append({"role": "user", "content": user_text})
        tools = await self._tool_schemas()

        while True:
            response = self.claude.chat(messages=self.messages, system = SYSTEM, tools = tools)
            self.messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "tool_use":
                tool_results = await self._run_tools(response)
                self.messages.append({"role": "user", "content": tool_results})
                continue

            # stop_reason == "end_turn" (or any non-tool stop) -> we're done
            return self.claude.text_from_message(response)