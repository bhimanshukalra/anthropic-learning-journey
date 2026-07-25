# HTTP + API Muscle Memory

**Goal:** Be able to consume a real API, including a streaming API, with correct request construction, error handling, retries, rate-limit handling, timeouts, logging, and tests.

**Roadmap link:** Phase 0 prerequisite in `planning/AI-ENGINEER-ROADMAP.md`.

**Done means:** from scratch, you can call a JSON API and a streaming SSE API, validate the response shape, handle common failures, retry safely, respect rate limits, and leave enough logs to debug what happened.

This is not "learn every HTTP detail." For AI engineering, it means you are fluent at the boundary where your app talks to model APIs, embedding APIs, vector databases, auth providers, SaaS tools, and internal services.

---

## 1. The Mental Model

HTTP is a request-response protocol.

Your client sends:

- a method
- a URL
- headers
- optional query parameters
- optional body

The server returns:

- a status code
- headers
- optional body

Example:

```text
POST https://api.example.com/v1/messages
Authorization: Bearer <token>
Content-Type: application/json

{"message": "hello"}
```

Response:

```text
200 OK
Content-Type: application/json

{"id": "msg_123", "reply": "hi"}
```

The job of API client code is to make this boundary explicit and boring: construct requests consistently, parse responses carefully, handle failures predictably, and make behavior observable.

---

## 2. URLs, Query Parameters, and Bodies

Use query parameters for filtering, pagination, search, and simple modifiers:

```text
GET /documents?limit=20&cursor=abc
```

Use a request body for structured data, usually JSON:

```text
POST /messages
Content-Type: application/json

{"model": "claude-sonnet-4-5", "messages": [...]}
```

Rule of thumb:

- `GET`: retrieve data; parameters usually in the URL.
- `POST`: create/run something; data usually in JSON body.
- `PUT`/`PATCH`: update something.
- `DELETE`: delete something.

Do not hand-build query strings with string concatenation. Let the HTTP client encode parameters.

```python
import httpx

response = httpx.get(
    "https://api.example.com/documents",
    params={"limit": 20, "cursor": "abc"},
)
```

---

## 3. Headers

Headers carry metadata about the request or response.

Common request headers:

```text
Authorization: Bearer <api_key>
Content-Type: application/json
Accept: application/json
Idempotency-Key: <unique_operation_id>
```

Common response headers:

```text
Content-Type: application/json
Retry-After: 30
X-RateLimit-Remaining: 42
```

Important distinction:

- `Content-Type` says what you are sending.
- `Accept` says what you want back.
- `Authorization` proves who you are.
- `Retry-After` tells you when to retry after rate limiting or temporary overload.

Never log raw API keys or full authorization headers.

---

## 4. Status Codes You Must Know

You do not need to memorize every code. You do need the main buckets.

| Code | Meaning | Client behavior |
|---:|---|---|
| 200 | OK | Parse response. |
| 201 | Created | Parse response; resource was created. |
| 204 | No Content | Success, but no body to parse. |
| 400 | Bad Request | Your request is malformed; usually do not retry. |
| 401 | Unauthorized | Missing/invalid credentials; fix auth. |
| 403 | Forbidden | Authenticated but not allowed; fix permissions. |
| 404 | Not Found | Resource/path missing; check ID/URL. |
| 409 | Conflict | State conflict; may need idempotency or read-modify-write logic. |
| 422 | Validation error | Request shape/value invalid; fix payload. |
| 429 | Rate limited | Back off and retry after delay. |
| 500 | Server error | Retry with backoff if operation is safe. |
| 502/503/504 | Gateway/unavailable/timeout | Retry with backoff if operation is safe. |

Rule: retry temporary failures, not bad requests.

Usually retry:

- 429
- 500
- 502
- 503
- 504
- network timeouts/transient connection errors

Usually do not retry:

- 400
- 401
- 403
- 404
- 422

---

## 5. JSON APIs

Most AI APIs use JSON for request and response bodies.

Basic sync example:

```python
import httpx


def fetch_user(user_id: str, api_key: str) -> dict:
    response = httpx.get(
        f"https://api.example.com/users/{user_id}",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()
```

But raw `dict` is weak at boundaries. For serious code, validate response data.

```python
from pydantic import BaseModel


class User(BaseModel):
    id: str
    name: str
    email: str | None = None


def fetch_user(user_id: str, api_key: str) -> User:
    response = httpx.get(
        f"https://api.example.com/users/{user_id}",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=10.0,
    )
    response.raise_for_status()
    return User.model_validate(response.json())
```

Why this matters: API contracts drift, optional fields disappear, types change, and model output can be malformed. Validate at the boundary.

---

## 6. Timeouts

Every network call must have a timeout. No timeout means your program can hang forever.

Use explicit timeouts:

```python
timeout = httpx.Timeout(
    connect=5.0,
    read=30.0,
    write=10.0,
    pool=5.0,
)
```

Meaning:

- connect timeout: time allowed to establish a connection.
- read timeout: time waiting for response bytes.
- write timeout: time sending request bytes.
- pool timeout: time waiting for an available connection from the pool.

For model APIs, read timeouts often need to be longer because generation can take time. For streaming responses, the read timeout is about time between chunks, not total response time.

---

## 7. Retries and Backoff

Retries handle transient failures. They are not a substitute for correct requests.

Use exponential backoff:

```text
try now
wait 1s
wait 2s
wait 4s
wait 8s
give up
```

Add jitter so many clients do not retry at the exact same time:

```text
wait = base_delay * 2^attempt + random small amount
```

Retry only when:

- the failure is likely temporary
- the operation is safe to retry
- you have a max attempt count
- you log the attempts

Simple async retry wrapper:

```python
import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


async def retry_with_backoff(
    operation: Callable[[], Awaitable[T]],
    *,
    max_attempts: int = 4,
    base_delay: float = 1.0,
) -> T:
    last_error: Exception | None = None

    for attempt in range(max_attempts):
        try:
            return await operation()
        except (httpx.TimeoutException, httpx.TransportError, httpx.HTTPStatusError) as error:
            last_error = error

            if isinstance(error, httpx.HTTPStatusError):
                status = error.response.status_code
                if status not in {429, 500, 502, 503, 504}:
                    raise

            if attempt == max_attempts - 1:
                raise

            delay = base_delay * (2**attempt) + random.uniform(0, 0.25)
            await asyncio.sleep(delay)

    raise RuntimeError("unreachable") from last_error
```

In production, prefer a tested retry library or a small local helper with tests.

---

## 8. Idempotency

Idempotency means repeating the same request has the same effect as doing it once.

Safe to retry by nature:

- `GET /users/123`
- `DELETE /cache/item` if deleting an already-deleted item is accepted

Dangerous to retry blindly:

- `POST /payments`
- `POST /tickets`
- `POST /orders`
- `POST /send-email`

If a POST creates something or causes a side effect, use an idempotency key when the API supports it:

```text
Idempotency-Key: create-ticket-user-123-2026-07-25T10:00:00Z
```

The server can use that key to recognize duplicate attempts and avoid creating duplicate resources.

AI relevance: if an agent retries a tool call that creates a ticket, sends an email, refunds an order, or modifies a database, idempotency is the difference between safe automation and expensive chaos.

---

## 9. Rate Limits

Rate limits protect services from overload and control usage.

Common signals:

- `429 Too Many Requests`
- `Retry-After` header
- provider-specific headers like remaining requests/tokens

Client behavior:

1. Read `Retry-After` if present.
2. Sleep at least that long.
3. Retry with backoff.
4. Stop after a max attempt count.
5. Surface a graceful error if still limited.

Do not solve rate limits by hammering harder. Use batching, caching, queueing, concurrency limits, and model routing.

AI relevance: model APIs often rate-limit by requests per minute and tokens per minute. A system can be under request limits but over token limits.

---

## 10. Streaming Responses and SSE

Streaming means the server sends partial output over time instead of waiting for the whole response.

LLM APIs often stream generated text token-by-token or event-by-event. This improves perceived latency and lets the UI show progress.

SSE means Server-Sent Events. It is a text-based streaming format where events look like this:

```text
event: message
data: {"text": "hello"}

event: message
data: {"text": " world"}

event: done
data: {}
```

Key details:

- Events are separated by blank lines.
- `data:` lines contain the payload.
- The connection stays open while events arrive.
- The client must handle partial lines/chunks.
- The stream can fail midway, so partial output is possible.

Basic async streaming shape:

```python
import httpx


async def stream_events(url: str, api_key: str) -> None:
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream(
            "POST",
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "text/event-stream",
            },
            json={"stream": True},
        ) as response:
            response.raise_for_status()

            async for line in response.aiter_lines():
                if not line:
                    continue
                if line.startswith("data: "):
                    print(line.removeprefix("data: "))
```

For real SSE parsing, preserve event boundaries and parse `event:` plus `data:` together. Do not assume every network chunk is a complete event.

---

## 11. Pagination

APIs rarely return everything at once.

Common pagination styles:

- page number: `?page=2`
- offset/limit: `?offset=100&limit=50`
- cursor: `?cursor=abc&limit=50`

Cursor pagination is common for changing datasets because it avoids skipping/duplicating records when new items appear.

Basic pattern:

```python
def fetch_all(api_key: str) -> list[dict]:
    cursor: str | None = None
    results: list[dict] = []

    while True:
        response = httpx.get(
            "https://api.example.com/items",
            headers={"Authorization": f"Bearer {api_key}"},
            params={"limit": 100, "cursor": cursor},
            timeout=10.0,
        )
        response.raise_for_status()
        payload = response.json()

        results.extend(payload["items"])
        cursor = payload.get("next_cursor")
        if cursor is None:
            return results
```

AI relevance: ingesting documents, tickets, messages, logs, or user feedback usually requires pagination.

---

## 12. Authentication and Secrets

Common API auth patterns:

- API key in `Authorization: Bearer ...`
- API key in a provider-specific header
- OAuth access token
- signed requests/webhooks

Rules:

- Read secrets from environment variables or a secret manager.
- Never commit `.env` files with real secrets.
- Never print API keys.
- Redact secrets in logs.
- Treat test keys as secrets too.

Example:

```python
import os


api_key = os.environ["EXAMPLE_API_KEY"]
```

Use `.env.example` to document required variables without exposing values.

---

## 13. Errors as Product Behavior

An API failure is not just an exception; it is user experience.

Design for:

- timeout
- rate limit
- invalid input
- provider outage
- malformed response
- partial streaming response
- auth failure
- permission failure

Good client code should return or raise meaningful errors. A user-facing app should translate them into useful messages:

```text
The model provider is temporarily unavailable. Please try again in a minute.
```

not:

```text
HTTPStatusError: 503 Server Error
```

For internal logs, keep the technical detail. For users, keep it calm and actionable.

---

## 14. Logging and Observability

Log enough to debug, not enough to leak private data.

Useful fields:

- request ID
- endpoint name
- method
- status code
- latency
- retry count
- timeout vs HTTP error vs validation error
- token counts/cost for model APIs
- model name/version
- tool name and sanitized arguments

Avoid logging:

- API keys
- full auth headers
- raw personal data
- full prompts/documents unless explicitly allowed

AI relevance: if a model answer is bad, you need to know whether the failure was prompt, retrieval, tool call, provider, rate limit, timeout, or response parsing.

---

## 15. Testing API Client Code

Do not hit real APIs in unit tests.

Test:

- request method/path/body/headers
- successful response parsing
- validation failure
- timeout handling
- retry on 429/503
- no retry on 400/401/403/422
- streaming parser behavior
- secret redaction in logs

Use mocks/fakes for unit tests and a tiny number of real integration tests when needed.

Common Python tools:

- `pytest`
- `respx` for mocking `httpx`
- `pytest-httpx`
- `responses` for mocking `requests`

---

## 16. `requests` vs `httpx`

`requests` is the classic sync HTTP library. It is simple and still widely used.

`httpx` supports both sync and async, has a modern API, and fits AI engineering well because model calls, streaming, and concurrent API calls often benefit from async.

For this roadmap, prefer `httpx` unless a project already uses `requests`.

Sync:

```python
with httpx.Client(timeout=10.0) as client:
    response = client.get("https://api.example.com/health")
    response.raise_for_status()
```

Async:

```python
async with httpx.AsyncClient(timeout=10.0) as client:
    response = await client.get("https://api.example.com/health")
    response.raise_for_status()
```

Use a client object instead of one-off calls when making repeated requests. It reuses connections and centralizes headers/timeouts.

---

## 17. Minimal API Client Shape

A small but professional API client wraps details behind clear methods.

```python
from __future__ import annotations

import httpx
from pydantic import BaseModel


class MessageResponse(BaseModel):
    id: str
    text: str


class ExampleClient:
    def __init__(self, api_key: str, base_url: str = "https://api.example.com") -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0),
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def create_message(self, text: str) -> MessageResponse:
        response = await self._client.post("/messages", json={"text": text})
        response.raise_for_status()
        return MessageResponse.model_validate(response.json())
```

This centralizes:

- base URL
- auth
- timeouts
- response validation
- future retry/logging hooks

---

## 18. AI API Specifics

Model APIs add a few recurring concerns:

- output can be partial, malformed, or truncated
- streaming events need parsing
- rate limits may include tokens per minute
- costs depend on input tokens, output tokens, cache hits, and model choice
- tool calls require validation and loop control
- structured output still needs schema validation
- retries can duplicate side effects if tools are involved
- prompts may contain private user data

For every LLM call, know:

- model
- input tokens
- output tokens
- latency
- cost estimate
- stop reason
- retry count
- prompt/version used
- whether output passed validation

This is the foundation of evals and observability.

---

## 19. Common Failure Patterns

| Failure | Likely cause | Fix |
|---|---|---|
| Hangs forever | No timeout | Set explicit timeouts. |
| Works locally, fails in prod | Missing env var or different network/auth config | Validate config at startup. |
| Random 429s | Too much concurrency or token usage | Backoff, queue, lower concurrency, batch/cache. |
| Duplicate tickets/orders | Retried side-effecting POST without idempotency | Use idempotency keys and operation IDs. |
| JSON parse error | API returned HTML/error page or partial response | Check status and content type before parsing. |
| Model output invalid | Prompt/schema mismatch or model drift | Validate, retry selectively, add eval case. |
| Streaming UI freezes | Client waits for full response | Consume chunks/events incrementally. |
| Cannot debug bad answer | No trace of prompt/retrieval/tool/result | Add structured logs/traces. |

---

## 20. Exit Drill

Build a tiny API client with a fake/mocked service.

Requirements:

- Uses `httpx.AsyncClient`.
- Reads API key from environment.
- Has explicit timeouts.
- Sends a JSON POST request.
- Parses JSON into a Pydantic model.
- Retries 429 and 503 with exponential backoff.
- Does not retry 400 or 401.
- Supports a streaming endpoint that consumes SSE-style `data:` lines.
- Logs sanitized request ID, status, latency, and retry count.
- Has pytest tests for success, validation failure, retry, no-retry, timeout, and streaming parsing.

Done means you can rebuild this without looking up basic HTTP control flow.

