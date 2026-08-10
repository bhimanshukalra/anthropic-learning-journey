from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage

from dotenv import load_dotenv
from rich import print
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(model="qwen/qwen3.6-27b", reasoning_format="hidden")


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState):
    messages = state["messages"]

    response = llm.invoke(messages)

    return {"messages": [response]}


graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile()

initial_state = {
    "messages": [HumanMessage(content="What is Object oriented programming?")]
}

response = chatbot.invoke(initial_state)

print(response["messages"][-1].content)
