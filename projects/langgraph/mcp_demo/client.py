import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()


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
    model = ChatGroq(model="qwen/qwen3.6-27b", reasoning_format="hidden")
    agent = create_agent(model, tools)

    math_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "What's (3+5) x 12?"}]}
    )

    print("math_response: ", math_response["messages"][-1].content)

    weather_response = await agent.ainvoke(
        {
            "messages": [
                {"role": "user", "content": "What is the weather in California?"}
            ]
        }
    )

    print("weather_response: ", weather_response["message"][-1].content)


asyncio.run(main())
