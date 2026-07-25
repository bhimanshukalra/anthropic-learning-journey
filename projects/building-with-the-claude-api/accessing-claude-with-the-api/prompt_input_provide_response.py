from claude_helpers import (
    add_assistant_message,
    add_user_message,
    create_message,
    extract_text,
    print_message_metadata,
)


def main():
    messages = []

    print("Interactive Claude chat. Type 'q' or 'quit' to exit.")

    try:
        while True:
            user_input = input("> ").strip()
            if user_input.lower() in {"q", "quit"}:
                print("Goodbye.")
                return
            if not user_input:
                continue

            add_user_message(messages, user_input)
            message = create_message(messages, max_tokens=500, temperature=0.2)
            answer = extract_text(message)
            add_assistant_message(messages, answer)

            print()
            print("Response from Claude:")
            print(answer)
            print_message_metadata(message)
            print()
    except KeyboardInterrupt:
        print("\nGoodbye.")


if __name__ == "__main__":
    main()
