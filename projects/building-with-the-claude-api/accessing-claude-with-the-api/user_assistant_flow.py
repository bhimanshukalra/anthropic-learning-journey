from claude_helpers import add_assistant_message, add_user_message, create_message, extract_text, print_message_metadata


def main():
    messages = []

    add_user_message(messages, "Define quantum computing in one sentence")
    first_message = create_message(messages, max_tokens=250, temperature=0.2)
    first_answer = extract_text(first_message)
    print("First response from model:")
    print(first_answer)
    print_message_metadata(first_message)

    add_assistant_message(messages, first_answer)
    add_user_message(messages, "Write another sentence that builds on your previous answer")
    second_message = create_message(messages, max_tokens=250, temperature=0.2)
    second_answer = extract_text(second_message)
    print()
    print("Second response from model:")
    print(second_answer)
    print_message_metadata(second_message)

    print()
    print("Messages sent in second request:")
    for index, message in enumerate(messages, start=1):
        print(f"{index}. {message['role']}: {message['content']}")


if __name__ == "__main__":
    main()
