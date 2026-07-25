# Accessing Claude with the API

Small Python exercises from the "Building with the Claude API" course. The
examples show how to send messages, use system prompts, continue a conversation,
stream responses, and nudge Claude toward structured output.

The goal of this folder is not just to keep course demos. Each script should
become a small API-learning artifact: something you can run, inspect, and use to
explain one Anthropic Messages API concept clearly.

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

| File | What it teaches | Current status |
| --- | --- | --- |
| `claude_helpers.py` | Shared Anthropic client setup, environment variable loading, `messages.create`, response text extraction, token usage metadata, and a compatibility `chat()` wrapper. | Upgraded learning artifact |
| `math_tutor.py` | Using a `system` prompt to define Claude's role and behavior, plus `max_tokens`, `temperature`, and response metadata. | Upgraded learning artifact |
| `user_assistant_flow.py` | Preserving conversation history by sending prior `user` and `assistant` turns back to the API. | Upgraded learning artifact |
| `prompt_input_provide_response.py` | Manual chat loop, repeated API calls, growing message history, clean exits, and per-turn metadata. | Upgraded learning artifact |
| `structured_data.py` | Assistant prefill and stop sequences for JSON-shaped output. | Course demo |
| `structured_data_exercise.py` | Stop sequences with a fenced bash response. | Course demo |
| `streaming.py` | Streaming text chunks as they arrive, then reading the final message for stop reason and token usage metadata. | Upgraded learning artifact |
| `streaming_server.py` | FastAPI endpoint that keeps the Anthropic API key on the backend and forwards Claude chunks as Server-Sent Events. | Upgraded learning artifact |
| `streaming_client.py` | HTTP client that consumes the local streaming endpoint and prints chunks as they arrive. | Upgraded learning artifact |
| `STREAMING-END-TO-END.md` | Step-by-step guide for completing server-to-client streaming. | Learning guide |
| `main.py` | Placeholder script created by the project scaffold. | Not part of the learning path |

## Run an Exercise

Run scripts from this folder so local imports resolve cleanly:

```bash
uv run python prompt_input_provide_response.py
uv run python user_assistant_flow.py
uv run python math_tutor.py
uv run python structured_data.py
uv run python streaming.py
```

Run the end-to-end streaming example with two terminals.

Terminal 1:

```bash
uv run uvicorn streaming_server:app --reload
```

Terminal 2:

```bash
uv run python streaming_client.py
```

If `uv` is not available in the current shell, activate the virtual environment
or run the scripts with the Python interpreter that has the project dependencies
installed.

## API Concepts to Know

After finishing the API overview and primer, you should be able to explain these
points from memory:

- `ANTHROPIC_API_KEY` authenticates requests and should live in `.env` or your
  shell environment, not in source code.
- The Anthropic SDK creates a client with `Anthropic(...)`, then sends requests
  with `client.messages.create(...)`.
- `model` selects which Claude model handles the request.
- `messages` is the conversation history. Each item has a `role` and `content`.
- `system` is separate from `messages` and is used for high-level behavior
  instructions.
- `max_tokens` controls the maximum response length.
- `temperature` controls how deterministic or varied the response is.
- A response can contain multiple content blocks, so helper code should extract
  text blocks instead of assuming a raw string response.
- `stop_reason` explains why Claude stopped generating.
- `usage.input_tokens` and `usage.output_tokens` help you understand cost and
  prompt size.
- Stop sequences can end generation at a delimiter, which is useful for shaped
  output experiments.
- Streaming returns text incrementally, which is useful for responsive apps.
- `stream.text_stream` is for live text chunks; `stream.get_final_message()` is
  for the completed message object and metadata after the stream finishes.
- End-to-end streaming usually flows from Claude to your backend, then from your
  backend to the client, so the API key and product controls stay server-side.
- Server-Sent Events send `data:` lines over a long-lived HTTP response.

## Completion Notes

This folder is complete for the "Accessing Claude with the API" checkpoint when:

- You can run the upgraded scripts from this folder.
- You can point to where the API key, model, messages, system prompt, max tokens,
  temperature, stop reason, and token usage are handled.
- You understand why `user_assistant_flow.py` manually appends the assistant's
  previous answer before asking the next question.
- You understand why `structured_data.py` uses assistant prefill and a stop
  sequence even though it is still a course demo.
- You can explain the difference between a normal response and a streamed
  response.
- You can explain why streaming code prints chunks as they arrive but waits until
  the end to inspect stop reason and token usage.
- You can run `streaming_server.py` and `streaming_client.py` together and
  explain the Claude -> backend -> client streaming path.
