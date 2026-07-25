import os
import sys
from typing import Any

from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5")
MAX_TOKENS = 1000
DEFAULT_TEMPERATURE = 0.2


def _require_api_key() -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Missing ANTHROPIC_API_KEY. Add it to .env or your shell environment.", file=sys.stderr)
        raise SystemExit(1)
    return api_key


client = Anthropic(api_key=_require_api_key())


def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)


def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)


def create_message(
    messages,
    *,
    system: str | None = None,
    stop_sequences: list[str] | None = None,
    max_tokens: int = MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
):
    params = {
        "model": CLAUDE_MODEL,
        "max_tokens": max_tokens,
        "messages": messages,
        "temperature": temperature,
    }
    if system:
        params["system"] = system
    if stop_sequences:
        params["stop_sequences"] = stop_sequences
    return client.messages.create(**params)


def extract_text(message: Any) -> str:
    text_blocks = []
    for block in message.content:
        if block.type == "text":
            text_blocks.append(block.text)
    return "\n".join(text_blocks)


def print_message_metadata(message: Any) -> None:
    print()
    print("Metadata:")
    print(f"- Model: {message.model}")
    print(f"- Stop reason: {message.stop_reason}")
    print(f"- Input tokens: {message.usage.input_tokens}")
    print(f"- Output tokens: {message.usage.output_tokens}")


def chat(
    messages,
    system=None,
    stop_sequences=None,
    max_tokens: int = MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
):
    message = create_message(
        messages,
        system=system,
        stop_sequences=stop_sequences,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return extract_text(message)
