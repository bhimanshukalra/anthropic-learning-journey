import json
from claude_helpers import add_user_message, chat, add_assistant_message


def main():
    messages = []

    add_user_message(messages, "Generate a very short event brde rule as json")
    add_assistant_message(messages, "```json")
    response = chat(messages, stop_sequences=["```"])
    clean_json = json.loads(response.strip())
    print("clean_json: ", clean_json)


if __name__ == "__main__":
    main()
