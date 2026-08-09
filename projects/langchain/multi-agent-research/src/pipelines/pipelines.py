from src.agents.agents import (
    build_search_agent,
    build_reader_agent,
    writer_chain,
    critic_chain,
)
from rich import print


def run_research_pipeline(topic: str) -> dict:
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

    state["search_results"] = search_result["messages"][-1].content
    print("Search result: \n", state["search_results"])

    # Reader agent

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke(
        {
            "messages": [
                (
                    "user",
                    f"Based on the following search results about '{topic}', pick the most relevant URL and scrape it for deeper content.\n\nSearch results:\n{state['search_results'][:800]}",
                )
            ]
        }
    )

    state["scraped_content"] = reader_result["messages"][-1].content

    print("\n\nScraped content: \n", state["scraped_content"])

    # Writer chain

    research_combined = f"SEARCH RESULTS: \n{state['search_results']} \n\n DETAILED SCRAPED CONTENT: \n {state['scraped_content']}"

    state["report"] = writer_chain.invoke(
        {"topic": topic, "research": research_combined}
    )

    print("Final report", state["report"])

    # Critic report

    state["feedback"] = critic_chain.invoke({"report": state["report"]})

    print("Critic report", state["feedback"])

    return state
