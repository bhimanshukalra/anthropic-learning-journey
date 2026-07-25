# End-to-End Streaming Guide

Use this guide to complete the roadmap checkbox:

```md
[ ] Streaming end-to-end (server -> client)
```

You already completed the Claude SDK streaming piece in `streaming.py`. This
guide adds the missing production-shaped path: Claude streams to your backend,
and your backend streams chunks to a client.

## Goal

By the end, you should have:

- `streaming_server.py` exposing a streaming API endpoint.
- `streaming_client.py` consuming that endpoint incrementally.
- README notes explaining how to run both.
- A clear mental model of Claude stream -> server generator -> HTTP stream ->
  client output.

## Why This Matters

In a real product, the browser or frontend usually should not call Claude
directly. The backend owns API keys, auth, logging, rate limits, safety checks,
and cost controls. Streaming end-to-end means the user sees tokens quickly while
the backend still stays in control.

## Step 1: Add Dependencies

From this folder, add the backend and client dependencies:

```bash
uv add fastapi uvicorn httpx
```

What each package is for:

- `fastapi`: creates the backend API.
- `uvicorn`: runs the FastAPI server locally.
- `httpx`: lets the client consume the streaming endpoint.

## Step 2: Create `streaming_server.py`

Create a FastAPI app with:

- `POST /stream`
- request body containing `prompt`
- empty prompt validation
- `StreamingResponse`
- `media_type="text/event-stream"` for Server-Sent Events

Recommended shape:

```python
from collections.abc import Iterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from claude_helpers import CLAUDE_MODEL, DEFAULT_TEMPERATURE, add_user_message, client

app = FastAPI()


class StreamRequest(BaseModel):
    prompt: str


def claude_text_events(prompt: str) -> Iterator[str]:
    messages = []
    add_user_message(messages, prompt)

    with client.messages.stream(
        model=CLAUDE_MODEL,
        max_tokens=500,
        messages=messages,
        temperature=DEFAULT_TEMPERATURE,
    ) as stream:
        for text in stream.text_stream:
            yield f"data: {text}\n\n"

        final_message = stream.get_final_message()
        yield f"event: done\ndata: {final_message.stop_reason}\n\n"


@app.post("/stream")
def stream_response(request: StreamRequest):
    prompt = request.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    return StreamingResponse(
        claude_text_events(prompt),
        media_type="text/event-stream",
    )
```

Important things to notice:

- The API key stays on the server.
- `stream.text_stream` yields only text chunks.
- `StreamingResponse` forwards chunks as they are produced.
- The final message is only available after Claude finishes streaming.
- The `done` event gives the client a clean terminal signal.

## Step 3: Create `streaming_client.py`

Create a small client that calls your local server and prints chunks as they
arrive:

```python
import httpx


STREAM_URL = "http://127.0.0.1:8000/stream"


def main():
    payload = {
        "prompt": "Write a 4 sentence explanation of why streaming improves chat UX."
    }

    with httpx.stream("POST", STREAM_URL, json=payload, timeout=60) as response:
        response.raise_for_status()

        print("Streaming from server:")
        for line in response.iter_lines():
            if not line:
                continue

            if line.startswith("data: "):
                print(line.removeprefix("data: "), end="", flush=True)
            elif line.startswith("event: done"):
                print()

        print()


if __name__ == "__main__":
    main()
```

This client intentionally stays simple. Its job is to prove that the backend is
streaming chunks across HTTP instead of waiting for Claude's full answer before
returning.

## Step 4: Run the Server

In one terminal:

```bash
uv run uvicorn streaming_server:app --reload
```

Expected result:

- Server starts on `http://127.0.0.1:8000`.
- It keeps running and waits for requests.

## Step 5: Run the Client

In a second terminal:

```bash
uv run python streaming_client.py
```

Expected result:

- The client prints text gradually.
- It should feel different from waiting for a full response.
- The server terminal should show the request.

## Step 6: Test the Edge Case

Temporarily change the client payload to:

```python
payload = {"prompt": ""}
```

Run the client again.

Expected result:

- Server returns HTTP `400`.
- Client raises an HTTP error.
- You can explain why validation belongs on the server.

After testing, restore a real prompt.

## Step 7: Update README

Update `README.md`:

- Add `streaming_server.py` and `streaming_client.py` to the file table.
- Mention that `streaming.py` is SDK-only streaming.
- Mention that `streaming_server.py` plus `streaming_client.py` is end-to-end
  server-to-client streaming.
- Add run commands for server and client.

## Step 8: Verify

Run syntax checks:

```bash
uv run python -m py_compile \
  claude_helpers.py \
  streaming.py \
  streaming_server.py \
  streaming_client.py
```

Then manually verify:

- `uv run uvicorn streaming_server:app --reload` starts successfully.
- `uv run python streaming_client.py` prints chunks gradually.
- Empty prompt returns `400`.

## Step 9: Update the Roadmap

Once the server and client work, update:

```md
- [x] **Streaming** end-to-end (server -> client)
```

Add a progress note with:

- date completed
- files created
- what you learned
- commit hash after committing

## Self-Check

You are done when you can answer these without notes:

- Why should the frontend usually not call Claude directly?
- What does `stream.text_stream` yield?
- What does `StreamingResponse` do?
- Why does the server use a generator?
- What is Server-Sent Events?
- Why is `stream.get_final_message()` only available after streaming ends?
- Where would you add auth, rate limiting, tracing, and cost logging in a real
  product?

## Minimum Done Bar

Do not tick the roadmap checkbox until all of this is true:

- The server streams Claude output.
- The client receives and prints chunks incrementally.
- Empty prompts fail cleanly.
- README documents how to run the flow.
- You can explain the path from Claude -> backend -> client.
