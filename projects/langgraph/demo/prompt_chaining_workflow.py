from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

model = ChatGroq(model="qwen/qwen3.6-27b", reasoning_format="hidden")


class BlogState(TypedDict):
    title: str
    outline: str
    content: str


def create_outline(state: BlogState) -> BlogState:
    title = state["title"]
    prompt = f"Generate a detailed outline for a blog on the topic: {title}"
    outline = model.invoke(prompt).content
    state["outline"] = outline

    return state


def create_blog(state: BlogState) -> BlogState:
    title = state["title"]
    outline = state["outline"]
    prompt = f"Write a detailed blog on the title: {title}, using the following outline:\n{outline}"
    content = model.invoke(prompt).content
    state["content"] = content

    return state


def main():
    graph = StateGraph(BlogState)

    graph.add_node("create_outline", create_outline)
    graph.add_node("create_blog", create_blog)

    graph.add_edge(START, "create_outline")
    graph.add_edge("create_outline", "create_blog")
    graph.add_edge("create_blog", END)

    workflow = graph.compile()

    initial_state = {"title": "Rise of AI in India"}
    final_state = workflow.invoke(initial_state)
    print("title:\n", final_state["title"])
    print("\n\noutline:\n", final_state["outline"])
    print("\n\ncontent:\n", final_state["content"])


if __name__ == "__main__":
    main()
