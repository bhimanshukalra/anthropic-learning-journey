# Batch P-12 — Working with the Outside World

> Reference notes for [`docs/PYTHON-FLUENCY.md`](../PYTHON-FLUENCY.md) · Batch P-12.
> Drill: pending — complete after the lesson and quiz.

*Programs become useful at their boundaries: files, wire formats, HTTP services,
configuration, and operational evidence. Python has compact tools for each, but reliable
boundary code must make encoding, failure, cleanup, secrecy, and observability explicit.*

---

## 1. `pathlib` — paths as values

`pathlib.Path` models a filesystem path and composes it without manual slash handling:

```python
from pathlib import Path


project = Path.cwd()
data_dir = project / "data"
input_path = data_dir / "prompts.jsonl"

print(input_path.name)                 # prompts.jsonl
print(input_path.stem)                 # prompts
print(input_path.suffix)               # .jsonl
print(input_path.parent)               # .../data
```

The `/` operator joins path components; it does not access the filesystem. A relative `Path`
is interpreted against the process's current working directory, which may differ between a
terminal, IDE, test runner, and service. Accept important paths as configuration or anchor
them deliberately rather than assuming where the process was launched.

### Reading and writing text or bytes

```python
text = input_path.read_text(encoding="utf-8")
input_path.write_text("one line\n", encoding="utf-8")

payload_path = data_dir / "image.bin"
payload = payload_path.read_bytes()
payload_path.write_bytes(payload)
```

Specify the text encoding at system boundaries. Relying on the platform default can make
code behave differently across machines. `read_text` and `read_bytes` load the whole file;
for large or streaming data, open the file and iterate:

```python
with input_path.open("r", encoding="utf-8") as source:
    for line in source:
        process(line)
```

Opening with `"w"` or calling `write_text` replaces an existing file. Use `"a"` to append,
and treat overwrite decisions as part of the API rather than an incidental default.

Create directories explicitly:

```python
data_dir.mkdir(parents=True, exist_ok=True)
```

`exist_ok=True` tolerates an existing directory; it does not make an existing regular file
valid. Filesystem operations can still fail because of permissions, races, full disks, or
invalid paths—an earlier `.exists()` check cannot guarantee the later operation succeeds.

### Discovering files

```python
markdown_files = sorted(project.glob("docs/**/*.md"))
json_files = sorted(data_dir.rglob("*.json"))
```

`glob` returns an iterator of `Path` objects. Filesystem order is not a stable contract, so
sort when deterministic processing matters. A match can disappear before it is opened;
handle errors at the operation that matters.

Useful methods include `.exists()`, `.is_file()`, `.is_dir()`, `.resolve()`, `.rename()`, and
`.unlink()`. Avoid converting to `str` unless an older library requires it; modern Python APIs
usually accept path-like objects directly.

Do not confuse path manipulation with security validation. Checking that a user-provided path
"looks" contained under a directory is subtle around `..`, symlinks, and races. Use a proven
containment policy for untrusted paths.

---

## 2. JSON and JSONL — explicit interchange formats

The standard `json` module converts between JSON text and ordinary Python values:

```python
import json


record = {
    "prompt": "Explain generators",
    "score": 0.92,
    "passed": True,
    "tags": ["python", "streaming"],
    "notes": None,
}

encoded = json.dumps(record, ensure_ascii=False)
decoded = json.loads(encoded)
```

`dumps` and `loads` operate on strings. `dump` and `load` operate on open file objects:

```python
path = Path("result.json")

with path.open("w", encoding="utf-8") as destination:
    json.dump(record, destination, indent=2, ensure_ascii=False)

with path.open("r", encoding="utf-8") as source:
    loaded = json.load(source)
```

The similar names follow a useful rule: the trailing `s` means string.

JSON has a deliberately small type system:

| JSON | Python after `loads` |
|---|---|
| object | `dict` |
| array | `list` |
| string | `str` |
| number | `int` or `float` |
| `true` / `false` | `True` / `False` |
| `null` | `None` |

Tuples become arrays and decode as lists. Sets, `Path`, `datetime`, `Decimal`, bytes, enums,
and arbitrary classes are not JSON values. Convert them deliberately or provide a narrowly
defined encoder. `default=str` is convenient but often hides schema mistakes by silently
turning unsupported values into lossy strings.

JSON parsing proves only that input is syntactically valid JSON. It does not prove that
required keys exist or values have the expected shape. Validate external data after parsing;
Pydantic from P-10 is a natural fit.

### JSONL — one JSON value per line

JSON Lines is useful for logs, evaluation datasets, and streaming pipelines because each line
is an independent record:

```python
def read_jsonl(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid JSON on line {line_number}") from error
            if not isinstance(value, dict):
                raise ValueError(f"expected object on line {line_number}")
            records.append(value)
    return records
```

For large data, make the function a generator and yield one record at a time instead of
building a list. Preserve the line number in errors; "invalid JSON" alone is painful in a
million-line dataset.

Writing JSONL means serialising each record independently and terminating it with a newline:

```python
with Path("results.jsonl").open("w", encoding="utf-8") as destination:
    for result in results:
        destination.write(json.dumps(result, ensure_ascii=False) + "\n")
```

JSONL is not one top-level JSON array, so `json.load()` cannot read the entire file as a
single document. Its record independence enables append-only and chunk-by-chunk processing.

---

## 3. `httpx` — HTTP with explicit policy

`httpx` offers closely aligned synchronous and asynchronous APIs. It is a third-party
dependency, so add and lock it through the project's package manager rather than assuming it
is installed.

### Reuse a client

```python
import httpx


timeout = httpx.Timeout(10.0, connect=3.0)

with httpx.Client(
    base_url="https://api.example.com",
    timeout=timeout,
    headers={"Accept": "application/json"},
) as client:
    response = client.get("/models", params={"limit": 20})
    response.raise_for_status()
    models = response.json()
```

A client reuses connection pools and centralises base URLs, headers, authentication, and
timeouts. Top-level helpers such as `httpx.get(...)` are fine for one-off calls but waste
connections in repeated workflows. A client is a context manager because its resources must
be closed.

`params=` builds an encoded query string. Use `json=` for a JSON request body:

```python
response = client.post(
    "/generate",
    json={"prompt": "Explain context managers", "max_tokens": 200},
)
```

Do not use `data=` when the server expects JSON; it represents form or raw request data.
Likewise, prefer `response.json()` over manually decoding `response.text`, but remember that a
successful parse does not validate the response schema.

### Timeouts and status failures

Network calls need finite timeouts. `httpx` distinguishes connect, read, write, and pool
timeouts, allowing policy to reflect the operation. Catch exceptions narrowly:

```python
try:
    response = client.get("/models")
    response.raise_for_status()
except httpx.TimeoutException as error:
    raise RuntimeError("model service timed out") from error
except httpx.HTTPStatusError as error:
    status = error.response.status_code
    raise RuntimeError(f"model service returned {status}") from error
except httpx.RequestError as error:
    raise RuntimeError("model service request failed") from error
```

`raise_for_status()` converts 4xx/5xx responses into `HTTPStatusError`. Without it, an error
response is still a normal `Response` and code may mistake its body for success data.

Do not blindly retry every failure. Timeouts, connection failures, `429`, and some `5xx`
responses may be transient; most `4xx` failures are caller errors. Retrying a non-idempotent
request can duplicate effects unless the API supports idempotency keys. Retry policy belongs
around the request, as covered in P-7.

Avoid putting API keys or response bodies containing sensitive data in exception messages or
logs.

### Async requests

```python
import asyncio
import httpx


async def fetch_models() -> object:
    async with httpx.AsyncClient(
        base_url="https://api.example.com",
        timeout=10.0,
    ) as client:
        response = await client.get("/models")
        response.raise_for_status()
        return response.json()


models = asyncio.run(fetch_models())
```

Use `AsyncClient` inside an async application, especially when many independent network
requests must overlap. Do not call the synchronous client from the event-loop thread for
ordinary request work; it blocks all other tasks. Also do not create a new async client for
every call—reuse one at an appropriate application lifetime to retain pooling benefits.

Async improves I/O concurrency, not the speed of a single server or CPU-bound work. Bound
concurrency when issuing many calls so the client does not overwhelm the remote service.

### Streaming responses

Stream when the response is large or useful incrementally:

```python
with httpx.Client(timeout=30.0) as client:
    with client.stream("GET", "https://api.example.com/events") as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                handle(line)
```

The async form uses both async context management and async iteration:

```python
async with httpx.AsyncClient(timeout=30.0) as client:
    async with client.stream("GET", url) as response:
        response.raise_for_status()
        async for line in response.aiter_lines():
            if line:
                await handle(line)
```

The response context must remain open while its body is consumed. `response.text` or
`response.content` materialises the full body, defeating the memory advantage of streaming.
HTTP chunk boundaries are transport details and may not correspond to application messages;
use the service's framing protocol, such as complete lines or server-sent events.

---

## 4. Environment variables and secrets

Process configuration commonly enters through `os.environ`:

```python
import os


api_key = os.environ["MODEL_API_KEY"]  # KeyError when required config is absent
region = os.environ.get("REGION", "us-east")
```

Use indexing for required variables so startup fails clearly. Use `.get` only when a real
default or absence policy exists. Environment values are always strings; parse and validate
them rather than relying on truthiness:

```python
timeout_seconds = float(os.environ.get("TIMEOUT_SECONDS", "30"))
debug = os.environ.get("DEBUG", "false").lower() in {"1", "true", "yes"}
```

A `.env` file is a developer convenience, not a Python feature and not a secret vault. A
loader such as `python-dotenv` or Pydantic settings can copy its entries into configuration.
Keep `.env` out of version control, commit a `.env.example` containing names and harmless
placeholders, and use the deployment platform's secret manager in production.

Never hard-code or commit credentials. Also avoid leaking them through:

- logs, tracebacks, screenshots, and shell history;
- URLs, where proxies and access logs may record query strings;
- dataclass or model `repr` output;
- copied production configuration in fixtures.

Pass secrets in an authorization header, redact sensitive metadata, and rotate a credential
immediately if it is exposed. Reading configuration once into a validated settings object at
startup is usually easier to reason about than consulting `os.environ` throughout the code.

---

## 5. Logging — minimal useful operational evidence

Libraries and modules create named loggers; an application entry point configures handlers
and formatting once:

```python
import logging


logger = logging.getLogger(__name__)


def configure_logging(*, verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
```

Levels communicate actionability:

- `DEBUG`: diagnostic detail useful while investigating;
- `INFO`: normal lifecycle milestones;
- `WARNING`: unexpected or degraded behaviour the program can continue through;
- `ERROR`: an operation failed;
- `CRITICAL`: the process or system may be unable to continue safely.

Log data separately from its message template:

```python
logger.info("processed batch batch_id=%s records=%d", batch_id, count)
```

This defers formatting when the level is disabled and works well with logging backends.
Avoid f-strings in hot debug logs because they format eagerly.

When handling an exception, `logger.exception` includes the active traceback:

```python
try:
    process_batch(path)
except ValueError:
    logger.exception("batch failed path=%s", path)
    raise
```

Log an exception at the layer that can add useful context or decide its fate. Logging and
re-raising at every layer creates duplicate noise. Do not use a bare `except Exception` only
to log and continue; swallowing failure can corrupt the workflow.

`print` is appropriate for intentional command output consumed by a person or pipeline.
Logging is for timestamped, levelled, configurable operational evidence, usually sent to
standard error or a logging service. Never call `basicConfig` from a reusable library, because
the host application owns global logging policy.

---

## 6. Putting the boundary pieces together

This synchronous example reads a JSONL work queue, calls an HTTP service, streams results to
disk, and logs progress without exposing its key:

```python
import json
import logging
import os
from collections.abc import Iterator
from pathlib import Path

import httpx


logger = logging.getLogger(__name__)


def read_prompts(path: Path) -> Iterator[tuple[int, str]]:
    with path.open("r", encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                prompt = record["prompt"]
            except (json.JSONDecodeError, KeyError, TypeError) as error:
                raise ValueError(f"invalid prompt on line {line_number}") from error
            if not isinstance(prompt, str):
                raise ValueError(f"prompt must be text on line {line_number}")
            yield line_number, prompt


def run(input_path: Path, output_path: Path) -> None:
    api_key = os.environ["MODEL_API_KEY"]
    output_path.parent.mkdir(parents=True, exist_ok=True)

    headers = {"Authorization": f"Bearer {api_key}"}
    timeout = httpx.Timeout(30.0, connect=5.0)

    with (
        httpx.Client(
            base_url="https://api.example.com",
            headers=headers,
            timeout=timeout,
        ) as client,
        output_path.open("w", encoding="utf-8") as destination,
    ):
        for line_number, prompt in read_prompts(input_path):
            try:
                response = client.post("/generate", json={"prompt": prompt})
                response.raise_for_status()
                result = response.json()
            except (httpx.RequestError, httpx.HTTPStatusError) as error:
                logger.error(
                    "request failed input_line=%d error_type=%s",
                    line_number,
                    type(error).__name__,
                )
                raise

            destination.write(json.dumps(result, ensure_ascii=False) + "\n")
            logger.info("generated result input_line=%d", line_number)
```

The boundaries have explicit policies: UTF-8 text, line-aware parse errors, required startup
configuration, finite timeouts, status checking, client reuse, deterministic resource
cleanup, record-by-record output, and metadata-only logs. Production code would additionally
validate response schemas, choose a retry/idempotency policy, and consider atomic output when
a partially written file is unacceptable.

---

## Quick self-check (cold recall)

1. Why is `Path` preferable to manual string concatenation? When should you use `.open()`
   instead of `.read_text()`?
2. What does `encoding="utf-8"` make explicit, and why can `.exists()` not eliminate
   filesystem errors?
3. Contrast `json.load`, `json.loads`, `json.dump`, and `json.dumps`. Which Python values do
   not have a direct JSON representation?
4. Why is JSONL useful for evaluation datasets? How would you report one malformed record
   without loading the whole file?
5. Why reuse an `httpx.Client`, set a timeout, and call `raise_for_status()`? Which failures
   might be retried, and what makes retries unsafe?
6. Show the sync and async shapes of an HTTP request. Why must a streamed response be consumed
   inside its context manager?
7. When should environment configuration use `os.environ[name]` rather than `.get()`? Why is
   a `.env` file not a production secret manager?
8. Distinguish `DEBUG`, `INFO`, `WARNING`, and `ERROR`. Why prefer logging placeholders over an
   f-string, and when is `logger.exception` appropriate?
9. Name three ways secrets can leak even when they are not committed to source control.

---

## Suggested 15-minute drill

Build a small JSONL enrichment command:

1. Read an input and output path with `Path`; stream UTF-8 input one line at a time.
2. Parse each non-blank line as an object containing `id` and `prompt`, reporting malformed
   data with its line number.
3. Read a required API key and an optional timeout from environment variables without ever
   printing either value.
4. Reuse one `httpx.Client`, send JSON, enforce the timeout, and call `raise_for_status()`.
   Point it at a fake or mocked service rather than spending real API credit.
5. Write each successful response immediately as one JSONL record.
6. Configure one useful log format at the entry point and log record IDs, counts, and failure
   types—never prompt contents, response bodies, or credentials.
7. Explain how you would convert the request loop to `AsyncClient` with bounded concurrency
   and how streaming would change response consumption.

Run it against valid input, malformed JSON, a simulated timeout, and an HTTP error. Mark P-12
complete in the fluency plan only after the quiz and drill both pass.
