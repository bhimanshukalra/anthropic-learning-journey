from chatbot_workflow import chatbot, config
from langchain_core.messages import BaseMessage, HumanMessage

response = chatbot.invoke(
    {"messages": [HumanMessage("What is Python?")]}, config=config
)

print(response["messages"][-1].content)
