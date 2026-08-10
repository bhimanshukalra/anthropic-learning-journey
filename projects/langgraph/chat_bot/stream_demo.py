from langchain_core.messages import HumanMessage

from chatbot_workflow import chatbot, CONFIG

for message_chunk, metadat in chatbot.stream(
    {"messages": [HumanMessage("Generate a blog about ML")]},
    config=CONFIG,
    stream_mode="messages",
):
    if message_chunk.content:
        print(message_chunk.content, end="", flush=True)
