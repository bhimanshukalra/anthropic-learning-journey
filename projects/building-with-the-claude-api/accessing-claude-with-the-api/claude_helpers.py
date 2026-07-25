from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()
CLAUDE_MODEL = "claude-sonnet-4-0"
MAX_TOKENS = 1000


def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)


def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)


def chat(messages, system=None, stop_sequences=None):
    params = {
        "model": CLAUDE_MODEL,
        "max_tokens": MAX_TOKENS,
        "messages": messages,
    }
    if system:
        params["system"] = system
    if stop_sequences:
        params["stop_sequences"] = stop_sequences
    message = client.messages.create(**params)
    return message.content[0].text
