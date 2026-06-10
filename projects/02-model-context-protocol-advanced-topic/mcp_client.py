import sys
import asyncio
import json
from pydantic import AnyUrl
from typing import Optional, Any
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from mcp.types import LoggingMessageNotificationParams

from core.logging import configure_logging, get_logger
from core.progress import ProgressReporter


logger = get_logger(__name__)


class MCPClient:
    def __init__(
        self,
        command: str,
        args: list[str],
        env: Optional[dict] = None,
        name: Optional[str] = None,
        progress: Optional[ProgressReporter] = None,
    ):
        self._command = command
        self._args = args
        self._env = env
        self.name = name or command
        # Progress defaults to disabled for standalone use, so importing MCPClient is quiet.
        self.progress = progress or ProgressReporter(enabled=False)
        self._session: Optional[ClientSession] = None
        self._exit_stack: AsyncExitStack = AsyncExitStack()

    async def connect(self):
        logger.info(
            "Connecting MCP client '%s' with command: %s %s",
            self.name,
            self._command,
            " ".join(self._args),
        )
        # This progress line is for the CLI user; the logger line above is for debugging.
        self.progress.info(f"connecting MCP server '{self.name}'")
        server_params = StdioServerParameters(
            command=self._command,
            args=self._args,
            env=self._env,
        )
        stdio_transport = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        _stdio, _write = stdio_transport
        # The logging callback receives MCP notifications/message events from the server.
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(_stdio, _write, logging_callback=self._handle_server_log)
        )
        await self._session.initialize()
        logger.info("MCP client '%s' initialized", self.name)
        self.progress.info(f"MCP server '{self.name}' connected")

    async def _handle_server_log(
        self, params: LoggingMessageNotificationParams
    ) -> None:
        logger.info(
            "MCP server log from '%s' level=%s logger=%s data=%s",
            self.name,
            params.level,
            params.logger,
            params.data,
        )
        self.progress.server_log(self.name, params.level, params.data)

    async def _handle_tool_progress(
        self, tool_name: str, progress: float, total: float | None, message: str | None
    ) -> None:
        logger.info(
            "MCP progress notification for tool '%s' on client '%s': %s/%s %s",
            tool_name,
            self.name,
            progress,
            total,
            message,
        )
        self.progress.notification(f"{self.name}.{tool_name}", progress, total, message)

    def session(self) -> ClientSession:
        if self._session is None:
            raise ConnectionError(
                "Client session not initialized or cache not populated. Call connect_to_server first."
            )
        return self._session

    async def list_tools(self) -> list[types.Tool]:
        logger.debug("Listing tools for MCP client '%s'", self.name)
        # Wrap network/process calls in progress steps so slow MCP operations are visible.
        with self.progress.step(f"loading tools from '{self.name}'"):
            result = await self.session().list_tools()
        logger.info("MCP client '%s' exposed %d tools", self.name, len(result.tools))
        return result.tools

    async def call_tool(
        self, tool_name: str, tool_input: dict
    ) -> types.CallToolResult | None:
        logger.info("Calling MCP tool '%s' on client '%s'", tool_name, self.name)
        # Tool calls can take time, so show a start/end progress message around them.
        with self.progress.step(f"running tool '{tool_name}'"):
            # Passing progress_callback asks the SDK to attach a progressToken to
            # this request and route notifications/progress messages back here.
            result = await self.session().call_tool(
                tool_name,
                tool_input,
                progress_callback=lambda progress, total, message: self._handle_tool_progress(
                    tool_name, progress, total, message
                ),
            )
        logger.info(
            "MCP tool '%s' on client '%s' completed with isError=%s",
            tool_name,
            self.name,
            result.isError if result else None,
        )
        return result

    async def list_prompts(self) -> list[types.Prompt]:
        logger.debug("Listing prompts for MCP client '%s'", self.name)
        # Prompt discovery happens during CLI startup and completion refresh.
        with self.progress.step(f"loading prompts from '{self.name}'"):
            result = await self.session().list_prompts()
        logger.info(
            "MCP client '%s' exposed %d prompts", self.name, len(result.prompts)
        )
        return result.prompts

    async def get_prompt(self, prompt_name, args: dict[str, str]):
        logger.info("Fetching MCP prompt '%s' from client '%s'", prompt_name, self.name)
        # Slash commands fetch prompt templates from the MCP server.
        with self.progress.step(f"fetching prompt '{prompt_name}'"):
            result = await self.session().get_prompt(prompt_name, args)
        return result.messages

    async def read_resource(self, uri: str) -> Any:
        logger.info("Reading MCP resource '%s' from client '%s'", uri, self.name)
        # Resource reads power @document mentions and startup document discovery.
        with self.progress.step(f"reading resource '{uri}'"):
            result = await self.session().read_resource(AnyUrl(uri))
        resource = result.contents[0]
        if isinstance(resource, types.TextResourceContents):
            if resource.mime_type == "application/json":
                return json.loads(resource.text)

            return resource.text

    async def cleanup(self):
        # Closing the exit stack shuts down the MCP session and stdio process cleanly.
        logger.info("Cleaning up MCP client '%s'", self.name)
        await self._exit_stack.aclose()
        self._session = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()


# For testing
async def main():
    async with MCPClient(
        # If using Python without UV, update command to 'python' and remove "run" from args.
        command="uv",
        args=["run", "mcp_server.py"],
        name="documents",
    ) as _client:
        result = await _client.list_tools()
        print(result)


if __name__ == "__main__":
    configure_logging()
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
