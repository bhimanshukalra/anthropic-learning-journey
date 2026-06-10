from core.claude import Claude
from mcp_client import MCPClient
from core.tools import ToolManager
from anthropic.types import MessageParam
from core.logging import get_logger


logger = get_logger(__name__)


class Chat:
    def __init__(self, claude_service: Claude, clients: dict[str, MCPClient]):
        self.claude_service: Claude = claude_service
        self.clients: dict[str, MCPClient] = clients
        self.messages: list[MessageParam] = []

    async def _process_query(self, query: str):
        # Debug logs can include details useful during development but noisy for normal use.
        logger.debug("Adding user query with %d characters", len(query))
        self.messages.append({"role": "user", "content": query})

    async def run(
        self,
        query: str,
    ) -> str:
        final_text_response = ""

        await self._process_query(query)

        while True:
            # Each loop is one Claude round-trip; tool use may create additional loops.
            logger.info("Sending chat request with %d messages", len(self.messages))
            response = self.claude_service.chat(
                messages=self.messages,
                tools=await ToolManager.get_all_tools(self.clients),
            )
            logger.info("Claude response stop_reason=%s", response.stop_reason)

            self.claude_service.add_assistant_message(self.messages, response)

            if response.stop_reason == "tool_use":
                print(self.claude_service.text_from_message(response))
                # This marks the handoff from model reasoning to MCP tool execution.
                logger.info("Claude requested tool use")
                tool_result_parts = await ToolManager.execute_tool_requests(
                    self.clients, response
                )

                self.claude_service.add_user_message(
                    self.messages, tool_result_parts
                )
            else:
                final_text_response = self.claude_service.text_from_message(
                    response
                )
                break

        return final_text_response
