from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

model = ChatGroq(model="qwen/qwen3.6-27b")


class WorkflowState(TypedDict):
    question: str
    answer: str


def llm_qa(state: WorkflowState) -> WorkflowState:
    question = state["question"]
    prompt = f"Answer the following question: {question}"
    answer = model.invoke(prompt).content
    state["answer"] = answer

    return state


def main():
    graph = StateGraph(WorkflowState)

    graph.add_node("llm_qa", llm_qa)

    graph.add_edge(START, "llm_qa")
    graph.add_edge("llm_qa", END)

    workflow = graph.compile()

    initial_state = {"question": "Who is the creator of Python"}
    final_state = workflow.invoke(initial_state)
    print("final_state", final_state["answer"])


if __name__ == "__main__":
    main()
