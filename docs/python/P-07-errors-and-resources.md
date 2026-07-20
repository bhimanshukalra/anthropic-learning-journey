# Batch P-7 — Errors & Resources

> Reference notes for [`docs/PYTHON-FLUENCY.md`](../PYTHON-FLUENCY.md) · Batch P-7.
> Drill: pending — complete after the lesson and quiz.

*Failures are part of a program's interface. Fluent Python code distinguishes expected
failure from programmer error, adds useful context without erasing the cause, and releases
resources on every path. This batch turns those principles into exception, context-manager,
and retry patterns suitable for files, databases, locks, and flaky APIs.*

---

## 1. Exception idioms

An exception interrupts normal control flow and searches outward for a matching handler.
Catch an exception only where the program can recover, translate it into a more meaningful
domain error, or add operational context. Otherwise, let it propagate.

### `try`, `except`, `else`, and `finally`

Each clause has a distinct job:

```python
def load_port(path: str) -> int:
    try:
        text = open(path, encoding="utf-8").read()
        port = int(text)
    except FileNotFoundError:
        return 8080
    except ValueError as error:
        raise ValueError(f"invalid port in {path!r}") from error
    else:
        print(f"loaded port from {path}")
        return port
    finally:
        print("configuration attempt finished")
```

- `try` contains operations expected to raise the handled exceptions.
- `except` handles a matching failure.
- `else` runs only when the `try` suite completes without an exception.
- `finally` runs whether the suite succeeds, raises, or returns.

The example deliberately previews a resource bug: `open(...).read()` does not make ownership
or closure clear. The context-manager section fixes it. In normal code, keep the `try` suite
small so it is obvious which operation a handler belongs to:

```python
try:
    value = int(raw_value)
except ValueError:
    value = default
else:
    save(value)  # a failure here should not be mistaken for invalid input
```

Putting `save(value)` inside the `try` could accidentally send one of its `ValueError`s down
the wrong recovery path. `else` narrows the handler's jurisdiction.

`finally` is for unavoidable cleanup or bookkeeping, not for hiding outcomes. A `return` in
`finally` overrides both an earlier return and a pending exception, so almost never write one:

```python
def broken() -> int:
    try:
        raise RuntimeError("lost")
    finally:
        return 0  # suppresses the RuntimeError
```

### Catch narrowly

Catch the most specific exception that represents the failure you understand:

```python
try:
    timeout = float(config["timeout"])
except KeyError:
    timeout = 30.0
except (TypeError, ValueError) as error:
    raise ValueError("timeout must be numeric") from error
```

These cases have different meanings: a missing key gets a default, while a present but
malformed value is rejected. Avoid a bare `except:`; it also catches `KeyboardInterrupt` and
`SystemExit`, making programs difficult to stop. `except Exception` is less dangerous but
still too broad for ordinary recovery because it can mask unrelated programming bugs.

A broad boundary can be appropriate when it logs and re-raises, isolates one background job,
or converts all failures into a protocol-level response:

```python
try:
    process_job(job)
except Exception:
    logger.exception("job %s failed", job.id)
    raise
```

Bare `raise` inside a handler re-raises the active exception with its traceback intact. Do not
write `raise error` merely to propagate it; that changes the visible traceback location.

### Exception chaining and translation

Low-level exceptions often expose implementation details. Translate them at a useful
abstraction boundary and preserve the cause explicitly:

```python
class ConfigurationError(Exception):
    """Raised when application configuration cannot be loaded."""


def parse_timeout(raw_value: str) -> float:
    try:
        return float(raw_value)
    except ValueError as error:
        raise ConfigurationError(
            f"invalid timeout value: {raw_value!r}"
        ) from error
```

`raise NewError(...) from error` sets `__cause__` and produces a traceback that says the new
error was the direct consequence of the original. Callers can work at the domain level while
logs retain the diagnostic detail.

Use `raise ... from None` only when the original failure is expected noise that adds no useful
information to the user. It suppresses display of the context; it should not become a way to
erase evidence during debugging.

### Custom exceptions

Create a custom exception when callers need to distinguish a domain failure from built-in
mechanics:

```python
class ModelClientError(Exception):
    """Base class for model-client failures."""


class RateLimitError(ModelClientError):
    """The service rejected a request because its limit was exceeded."""


class InvalidResponseError(ModelClientError):
    """The service returned a response the client could not accept."""
```

The small hierarchy lets a caller catch `RateLimitError` to retry or `ModelClientError` to
handle any client-domain failure. Subclass `Exception`, not `BaseException`. Prefer names
ending in `Error`, useful messages, and a shallow hierarchy. A new class pays rent when its
type changes control flow; do not create dozens of types that callers treat identically.

---

## 2. EAFP vs LBYL

Python commonly follows **EAFP**: *easier to ask forgiveness than permission*. Attempt the
operation and catch its expected failure. **LBYL** means *look before you leap*: check a
condition first, then operate.

```python
# LBYL
if "timeout" in config:
    timeout = config["timeout"]
else:
    timeout = 30

# EAFP
try:
    timeout = config["timeout"]
except KeyError:
    timeout = 30
```

EAFP is often a good fit because it expresses the operation directly, avoids duplicate
lookups, and works naturally with duck typing. It can also avoid a time-of-check/time-of-use
race:

```python
# Racy: the file may disappear after this check.
if path.exists():
    text = path.read_text()

# The operation itself is authoritative.
try:
    text = path.read_text()
except FileNotFoundError:
    text = ""
```

EAFP does **not** mean "catch everything." The attempted operation should be small, the
expected exception specific, and the recovery meaningful.

LBYL remains clearer when a check communicates an ordinary branch, prevents an expensive or
irreversible attempt, or supplies a better validation error:

```python
if temperature < 0 or temperature > 2:
    raise ValueError("temperature must be between 0 and 2")
```

The distinction is about semantics, not ideology. Use normal conditions for expected states;
use exceptions for operations whose failure is exceptional at that level. Never rely on LBYL
alone for external state that can change between checking and use.

---

## 3. Context managers — deterministic resource lifetimes

A context manager defines setup and teardown around a block. `with` guarantees the exit step
runs when the block finishes normally, returns early, or raises:

```python
from pathlib import Path


def first_line(path: Path) -> str:
    with path.open(encoding="utf-8") as file:
        return file.readline().rstrip("\n")
```

The file is closed before `first_line` returns. There is no reachable path that forgets
cleanup, and ownership is visible from indentation.

Conceptually, a context manager implements `__enter__` and `__exit__`:

```python
manager = path.open(encoding="utf-8")
file = manager.__enter__()
try:
    text = file.read()
except BaseException as error:
    suppress = manager.__exit__(type(error), error, error.__traceback__)
    if not suppress:
        raise
else:
    manager.__exit__(None, None, None)
```

Do not write this expansion yourself; it illustrates why `with` is reliable. If `__exit__`
returns a truthy value, it suppresses the exception. Most resource managers return a falsey
value so failures propagate.

Use context managers for any acquire/use/release lifecycle:

```python
with database.transaction():
    update_account()

with lock:
    shared_state.append(item)

with client.stream("GET", url) as response:
    for chunk in response.iter_bytes():
        consume(chunk)
```

Manual `close()` at the bottom is fragile because an exception or early return can skip it.
`try/finally` can be correct, but `with` is the standard, composable spelling.

### Writing one with `@contextmanager`

For simple cases, `contextlib.contextmanager` turns a one-yield generator into a context
manager:

```python
from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter


@contextmanager
def timed(label: str) -> Iterator[None]:
    started = perf_counter()
    try:
        yield
    finally:
        elapsed = perf_counter() - started
        print(f"{label}: {elapsed:.3f}s")


with timed("request"):
    call_service()
```

Code before `yield` is setup, the yielded value becomes the target after `as`, and code after
`yield` is teardown. There must be exactly one yield. Put cleanup in `finally` so an exception
thrown into the generator still releases the resource.

A manager can yield an acquired object:

```python
from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def managed_client() -> Iterator[Client]:
    client = Client()
    try:
        yield client
    finally:
        client.close()


with managed_client() as client:
    client.send("hello")
```

Prefer an existing object's native context-manager API when it has one. Write a custom
manager when you own a repeated lifecycle or need to adapt an API that lacks one.

---

## 4. Retry patterns for flaky calls

Retries are appropriate for **transient** failures: rate limits, temporary unavailability,
connection resets, and some timeouts. They are not a cure for invalid input, authentication
failure, programming bugs, or every HTTP error.

A useful retry loop is bounded, selective, delayed, observable, and preserves the final
failure:

```python
import random
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


class TransientAPIError(Exception):
    pass


def call_with_retry(
    operation: Callable[[], T],
    *,
    attempts: int = 4,
    base_delay: float = 0.5,
) -> T:
    if attempts < 1:
        raise ValueError("attempts must be at least 1")

    for attempt in range(attempts):
        try:
            return operation()
        except TransientAPIError:
            if attempt == attempts - 1:
                raise

            delay = base_delay * (2**attempt)
            jitter = random.uniform(0, delay * 0.25)
            time.sleep(delay + jitter)

    raise AssertionError("unreachable")
```

The first retry waits roughly `base_delay`, then twice that, then four times that: exponential
backoff reduces pressure on a struggling service. Jitter prevents many clients from retrying
in lockstep. The loop counts total **attempts**, including the first call; naming this clearly
avoids the common off-by-one ambiguity around a `retries` parameter.

Production retry policy also needs:

- a per-attempt timeout and often an overall deadline;
- server guidance such as `Retry-After` when available;
- logging/metrics with attempt number and delay;
- cancellation support in async code;
- idempotency analysis before repeating writes.

A retry can duplicate an operation if the server completed it but the response was lost.
Reads are usually safe; charges, messages, and record creation may not be. Use an idempotency
key or an API guarantee before retrying side effects.

Do not sleep while holding an unrelated lock, transaction, file, or streaming response. Keep
each attempt's resources scoped inside the attempt so they are released before backoff.
Libraries such as Tenacity can encode mature policies, but understanding this loop is
essential for configuring and reviewing them correctly.

---

## 5. Putting the pieces together

This client reads a response through a context manager, translates low-level failures into
domain exceptions, and retries only the transient one:

```python
import json
import random
import time
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


class ModelClientError(Exception):
    pass


class TransientModelError(ModelClientError):
    pass


class InvalidModelResponse(ModelClientError):
    pass


def fetch_result(client: Any, prompt: str) -> dict[str, object]:
    try:
        with client.request(prompt, timeout=10.0) as response:
            if response.status_code in {429, 502, 503, 504}:
                raise TransientModelError(
                    f"temporary API failure: {response.status_code}"
                )
            response.raise_for_status()
            raw_body = response.read()
    except TimeoutError as error:
        raise TransientModelError("model request timed out") from error

    try:
        payload = json.loads(raw_body)
        text = payload["text"]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise InvalidModelResponse("response has no valid text field") from error
    else:
        return {"text": str(text)}


def retry_transient(
    operation: Callable[[], T],
    *,
    attempts: int = 4,
    base_delay: float = 0.5,
) -> T:
    for attempt in range(attempts):
        try:
            return operation()
        except TransientModelError:
            if attempt == attempts - 1:
                raise
            delay = base_delay * (2**attempt)
            time.sleep(delay + random.uniform(0, delay * 0.25))

    raise AssertionError("unreachable")


result = retry_transient(
    lambda: fetch_result(client, "Summarise this"),
    attempts=4,
)
```

The `with` block releases the response after every attempt. Network conditions become a
retryable domain error, malformed successful responses become a non-retryable domain error,
and unexpected bugs propagate untouched. The retry layer knows policy but not HTTP details;
the fetch layer knows one attempt but not scheduling. That separation keeps both testable.

---

## Quick self-check (cold recall)

1. What runs in `else` and `finally` after a `try`? Why should a `try` suite usually be small?
2. Why is a bare `except:` dangerous? Give one legitimate use of a broad
   `except Exception` boundary.
3. Contrast bare `raise`, `raise error`, and `raise DomainError(...) from error`.
4. When does a custom exception type pay rent, and why should it inherit from `Exception`
   rather than `BaseException`?
5. Explain EAFP and LBYL. Why can checking that a file exists before opening it still fail?
6. What guarantee does `with` provide on return and exception paths? What does a truthy
   `__exit__` return mean?
7. In an `@contextmanager` function, what happens before, at, and after `yield`? Why should
   cleanup normally be in `finally`?
8. Which failures should be retried? Explain exponential backoff, jitter, attempt limits, and
   the idempotency risk of retrying a write.

---

## Suggested 15-minute drill

Build a fake model call that consumes a predefined sequence of outcomes such as two
`TransientAPIError`s followed by a valid JSON response:

1. Define a small custom exception hierarchy with transient and invalid-response errors.
2. Write `@contextmanager` `open_fake_response(...)` that prints `open` and `close`, with
   cleanup in `finally`.
3. Parse the response, translating `json.JSONDecodeError` with `raise ... from`.
4. Retry only the transient exception, with three total attempts and tiny exponential delays
   such as `0.01`, `0.02`, and no sleep after the final failure.
5. Confirm the response closes after every success or failure.
6. Run a permanent invalid-JSON case and prove it is attempted exactly once.
7. Run an all-transient case and inspect the preserved final traceback.

Keep delays tiny because the goal is control flow, not waiting. Explain which failures cross
each abstraction boundary and why. Mark P-7 complete in the fluency plan only after the quiz
and drill both pass.
