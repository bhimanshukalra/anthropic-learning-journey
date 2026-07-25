from claude_helpers import (
    add_user_message,
    client,
    CLAUDE_MODEL,
    DEFAULT_TEMPERATURE,
    extract_text,
    print_message_metadata,
)

STREAMING_PROMPT = "Write a 3 sentence description of a fake database."
MAX_STREAM_TOKENS = 500


def stream_response(prompt: str) -> None:
    if not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    messages = []
    add_user_message(messages, prompt)

    print("Prompt:")
    print(prompt)
    print()
    print("Streaming response:")

    with client.messages.stream(
        model=CLAUDE_MODEL,
        max_tokens=MAX_STREAM_TOKENS,
        messages=messages,
        temperature=DEFAULT_TEMPERATURE,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

        final_message = stream.get_final_message()

    print()
    print_message_metadata(final_message)

    print()
    print("Final message text:")
    print(extract_text(final_message))


def main():
    try:
        stream_response(STREAMING_PROMPT)
    except KeyboardInterrupt:
        print("\nStream interrupted by user.")
    except ValueError as error:
        print(f"Invalid input: {error}")


if __name__ == "__main__":
    main()
