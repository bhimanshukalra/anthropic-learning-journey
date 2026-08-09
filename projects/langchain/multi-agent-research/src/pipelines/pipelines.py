import os

from src.agents.agents import (
    build_search_agent,
    build_reader_agent,
    writer_chain,
    critic_chain,
)
from rich import print


def _validate_environment() -> None:
    missing = [
        name for name in ("GROQ_API_KEY", "TAVILY_API_KEY") if not os.getenv(name)
    ]

    if missing:
        names = ", ".join(missing)
        raise RuntimeError(f"Missing required environment variable(s): {names}")


def _latest_message_content(result: dict) -> str:
    messages = result.get("messages", [])
    if not messages:
        return ""

    return getattr(messages[-1], "content", "")


def _latest_tool_content(result: dict) -> str:
    for message in reversed(result.get("messages", [])):
        if message.__class__.__name__ == "ToolMessage":
            return getattr(message, "content", "")

    return ""


def run_research_pipeline(topic: str) -> dict:
    _validate_environment()
    state = {}

    # Search agent
    search_agent = build_search_agent()
    search_result = search_agent.invoke(
        {
            "messages": [
                (
                    "user",
                    f"Find recent reliable and detailed information about: {topic}",
                )
            ]
        }
    )

    state["search_results"] = _latest_tool_content(
        search_result
    ) or _latest_message_content(search_result)
    print("Search result: \n", state["search_results"])

    # Reader agent

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke(
        {
            "messages": [
                (
                    "user",
                    f"Based on the following search results about '{topic}', pick the most relevant URL and scrape it for deeper content.\n\nSearch results:\n{state['search_results'][:4000]}",
                )
            ]
        }
    )

    state["scraped_content"] = _latest_tool_content(
        reader_result
    ) or _latest_message_content(reader_result)

    print("\n\nScraped content: \n", state["scraped_content"])

    # Writer chain

    research_combined = f"SEARCH RESULTS: \n{state['search_results']} \n\n DETAILED SCRAPED CONTENT: \n {state['scraped_content']}"

    state["report"] = writer_chain.invoke(
        {"topic": topic, "research": research_combined}
    )

    print("\n\nFinal report", state["report"])

    # Critic report

    state["feedback"] = critic_chain.invoke({"report": state["report"]})

    print("\n\nCritic report", state["feedback"])

    return state
