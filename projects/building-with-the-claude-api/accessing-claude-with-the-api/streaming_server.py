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

    # This generator is the bridge between Claude's stream and the HTTP stream.
    # Each yielded string is flushed to the client by StreamingResponse.
    with client.messages.stream(
        model=CLAUDE_MODEL,
        max_tokens=500,
        messages=messages,
        temperature=DEFAULT_TEMPERATURE,
    ) as stream:
        for text in stream.text_stream:
            # SSE messages use "data:" lines separated by a blank line.
            yield f"data: {text}\n\n"

        # Token usage and stop reason are only available once the stream finishes.
        final_message = stream.get_final_message()
        yield f"event: done\ndata: {final_message.stop_reason}\n\n"


@app.post("/stream")
def stream_response(request: StreamRequest):
    prompt = request.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    # The server keeps the Anthropic API key private and forwards only streamed text.
    return StreamingResponse(claude_text_events(prompt), media_type="text/event-stream")
