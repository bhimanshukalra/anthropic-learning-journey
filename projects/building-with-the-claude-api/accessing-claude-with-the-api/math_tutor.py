from claude_helpers import add_user_message, chat

MATH_TUTOR_SYSTEM_PROMPT = """
You are a patient math tutor.
Do not directly answer a student's questions.
Guide them to a solution step by step.
"""
CONCISE_CODE_SYSTEM_PROMPT = "You are a Python engineer who writes very concise code."
# Low temperature = More deterministic output
# High temperature = More random output


def main():
    messages = []

    add_user_message(messages, "How do I solve 5x+3=2 for x?")
    answer = chat(messages, system=MATH_TUTOR_SYSTEM_PROMPT)
    print("Response: ", answer)


if __name__ == "__main__":
    main()
