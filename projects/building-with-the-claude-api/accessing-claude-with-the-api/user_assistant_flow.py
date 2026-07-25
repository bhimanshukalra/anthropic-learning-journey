from claude_helpers import add_assistant_message, add_user_message, chat


def main():
    messages = []

    add_user_message(messages, "Define quantum computing in one sentence")
    answer = chat(messages)
    print("First response from model: ", answer)
    add_assistant_message(messages, answer)
    add_user_message(messages, "Write another sentence")
    answer = chat(messages)
    print("Second response from model: ", answer)


if __name__ == "__main__":
    main()
