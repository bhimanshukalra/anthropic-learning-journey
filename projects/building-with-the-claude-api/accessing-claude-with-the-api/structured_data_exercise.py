import json
from claude_helpers import add_assistant_message, add_user_message, chat


def main():
    messages = []

    add_user_message(
        messages,
        "Generate three different sample AWS CLI commands. Each should be very short.",
    )
    add_assistant_message(
        messages,
        "Here are all three commands in a single block without any comments:\n ```bash",
    )
    response = chat(messages, stop_sequences=["```"])
    print("response: ", response)


if __name__ == "__main__":
    main()
