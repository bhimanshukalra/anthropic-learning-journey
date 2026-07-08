"""Entry point: wires the LLM wrapper (core/claude.py), the agentic loop
(core/agent.py), and the MCP tool server (mcp_server.py) into a terminal chat."""

import asyncio, os, sys
from dotenv import load_dotenv
from mcp_client import MCPClient
from core.claude import Claude
from core.agent import SupportAgent

load_dotenv()  # pull the API key and CLAUDE_MODEL from .env

async def main():
    claude = Claude(model=os.environ["CLAUDE_MODEL"])
    # The MCP server runs as a separate subprocess, spoken to over stdio.
    command, args = (("uv", ["run", "mcp_server.py"]) if os.getenv("USE_UV") == "1" else ("python", ["mcp_server.py"]))

    async with MCPClient(command=command, args=args) as client:
        agent = SupportAgent(claude, client)
        print("Support agent ready. Type a message (Ctrl-C to quit).\n")
        while True:
            try:
                user_text = input("you> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not user_text:
                continue
            # One call = the whole agentic loop: tool calls, hooks, final reply.
            reply = await agent.run(user_text)
            print(f"agent> {reply}\n")

if __name__ == "__main__":
    # Windows needs the Proactor event loop to spawn subprocesses (our MCP server).
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
