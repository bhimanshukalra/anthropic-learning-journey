import asyncio, os, sys
from dotenv import load_dotenv
from mcp_client import MCPClient
from core.claude import Claude
from core.agent import SupportAgent

load_dotenv()

async def main():
    claude = Claude(model=os.environ["CLAUDE_MODEL"])
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
            reply = await agent.run(user_text)
            print(f"agent> {reply}\n")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())