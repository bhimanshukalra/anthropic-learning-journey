from claude_helpers import add_assistant_message, add_user_message, chat


def main():
    messages = []

    while True:
        user_input = input("> ")
        print(">", user_input)
        add_user_message(messages, user_input)
        answer = chat(messages)
        add_assistant_message(messages, answer)
        print("Response from claude: ", answer)


if __name__ == "__main__":
    main()
