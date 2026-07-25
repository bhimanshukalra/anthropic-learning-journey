# Accessing Claude with the API

Small Python exercises from the "Building with the Claude API" course. The
examples show how to send messages, use system prompts, continue a conversation,
stream responses, and nudge Claude toward structured output.

## Setup

This project uses Python 3.11+ with `uv`.

```bash
uv sync
```

Create a `.env` file in this folder with your Anthropic API key:

```bash
ANTHROPIC_API_KEY=your_api_key_here
```

`.env` and `.venv/` are intentionally ignored by git.

## Files

- `claude_helpers.py` contains the shared Anthropic client, message helpers, and
  `chat()` wrapper.
- `prompt_input_provide_response.py` runs a simple interactive chat loop.
- `user_assistant_flow.py` demonstrates preserving conversation history.
- `math_tutor.py` demonstrates a system prompt.
- `structured_data.py` demonstrates assistant prefill and stop sequences for
  JSON-shaped output.
- `structured_data_exercise.py` practices stop sequences with a fenced bash
  response.
- `streaming.py` demonstrates streaming response text.

## Run an Exercise

Run scripts from this folder so local imports resolve cleanly:

```bash
uv run python math_tutor.py
uv run python structured_data.py
uv run python streaming.py
```
