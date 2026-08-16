from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import asyncio
import os


async def main():
    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": ["math_server.py"],
                "transport": "stdio",
            },
            "weather": {
                "url": "http://localhost:8000/mcp",
                "transport": "streamable_http",
            },
        }
    )

    tools = await client.get_tools()
    model = ChatGroq(model="qwen-qwq-32b")
    agent = create_agent(model, tools)

    math_response = await agent.invoke(
        {"messages": [{"role": "user", "content": "What's (3+5) x 12?"}]}
    )

    print("math_response: ", math_response["messages"][-1].content)


asyncio.run(main())
