from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
from rich import print

load_dotenv()

llm = ChatGroq(model="qwen/qwen3.6-27b", reasoning_format="hidden")


class JokeState(TypedDict):

    topic: str
    joke: str
    explanation: str


def generate_joke(state: JokeState):

    prompt = f'generate a joke on the topic {state["topic"]}'
    response = llm.invoke(prompt).content

    return {"joke": response}


def generate_explanation(state: JokeState):

    prompt = f'write an explanation for the joke - {state["joke"]}'
    response = llm.invoke(prompt).content

    return {"explanation": response}


graph = StateGraph(JokeState)

graph.add_node("generate_joke", generate_joke)
graph.add_node("generate_explanation", generate_explanation)

graph.add_edge(START, "generate_joke")
graph.add_edge("generate_joke", "generate_explanation")
graph.add_edge("generate_explanation", END)

checkpointer = InMemorySaver()

workflow = graph.compile(checkpointer=checkpointer)

config1 = {"configurable": {"thread_id": "1"}}
response = workflow.invoke({"topic": "Football"}, config=config1)

print("response", response)
print("get_state", workflow.get_state(config1))
print("get_state_history", list(workflow.get_state_history(config1)))

config2 = {"configurable": {"thread_id": "2"}}
response2 = workflow.invoke({"topic": "Cricket"}, config=config2)
print("response2", response2)

workflow.get_state(config2)
print("get_state", workflow.get_state(config2))

print("get_state_history", list(workflow.get_state_history(config2)))

# Time travel

workflow.get_state(
    {
        "configurable": {
            "thread_id": "2",
            "checkpoint_id": "1f15d969-8ed6-683c-8000-0c7a2f030ccd",
        }
    }
)

workflow.invoke(
    None,
    {
        "configurable": {
            "thread_id": "2",
            "checkpoint_id": "1f15d96a-02e6-69e6-8001-5bb2d5c6e2c1",
        }
    },
)

list(workflow.get_state_history(config2))

# Updating State

workflow.update_state(
    {
        "configurable": {
            "thread_id": "2",
            "checkpoint_id": "1f15d969-8ed6-683c-8000-0c7a2f030ccd",
            "checkpoint_ns": "",
        }
    },
    {"topic": "Tenis"},
)

list(workflow.get_state_history(config2))
