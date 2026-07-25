from claude_helpers import add_user_message, client, CLAUDE_MODEL, MAX_TOKENS


def main():
    messages = []

    add_user_message(messages, "Write a 1 sentence description of a fake database")
    with client.messages.stream(
        model=CLAUDE_MODEL,
        max_tokens=MAX_TOKENS,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            # print(text, end="")
            pass
    stream.get_final_message()


if __name__ == "__main__":
    main()
