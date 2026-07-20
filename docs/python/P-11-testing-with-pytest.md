# Batch P-11 — Testing with pytest

> Reference notes for [`docs/PYTHON-FLUENCY.md`](../PYTHON-FLUENCY.md) · Batch P-11.
> Drill: pending — complete after the lesson and quiz.

*pytest keeps tests close to ordinary Python: arrange values, call behaviour, and assert the
observable result. Fluency comes from knowing when fixtures clarify dependencies, when
parametrisation replaces repetition, and where to patch an external boundary so an LLM API
never makes a unit test slow, expensive, or nondeterministic.*

---

## 1. pytest basics

A test is normally a function whose name begins with `test_` and whose failures use plain
`assert`:

```python
# tests/test_scoring.py
from app.scoring import normalise_score


def test_normalise_score_clamps_values_above_one() -> None:
    result = normalise_score(1.4)

    assert result == 1.0
```

pytest rewrites assertions while importing test modules, so a failure displays the values
and expression involved. Use one meaningful assertion or several closely related assertions;
there is no need for special methods such as `assertEqual`.

### Discovery and layout

With the usual project shape:

```text
project/
├── pyproject.toml
├── src/
│   └── app/
│       └── scoring.py
└── tests/
    ├── conftest.py
    └── test_scoring.py
```

pytest discovers files such as `test_*.py` and `*_test.py`, classes named `Test...`, and
functions/methods named `test_...`. Test classes do not need to inherit from anything and
should generally have no custom `__init__`.

Common commands are:

```bash
uv run pytest
uv run pytest tests/test_scoring.py
uv run pytest tests/test_scoring.py::test_normalise_score_clamps_values_above_one
uv run pytest -k "normalise and not empty"
uv run pytest -q
uv run pytest -x
```

`-k` selects by name expression, `-q` reduces output, and `-x` stops after the first failure.
Run a focused node ID while iterating and the whole suite before considering work complete.

### Test behaviour, not implementation

A useful test expresses a contract:

```python
def test_build_prompt_includes_document_and_instruction() -> None:
    prompt = build_prompt("The quarterly revenue rose.")

    assert "quarterly revenue" in prompt
    assert "Summarise" in prompt
```

A brittle test inspects private helper call order or duplicates the production algorithm.
Refactoring should not break tests when observable behaviour is unchanged. Patch external
boundaries—network, clock, randomness, filesystem when appropriate—not every internal
function merely to make the test pass.

### Testing expected exceptions

Use `pytest.raises` as a context manager and inspect the captured exception when its message
is part of the contract:

```python
import pytest


def test_temperature_rejects_values_above_two() -> None:
    with pytest.raises(ValueError, match="between 0 and 2") as captured:
        validate_temperature(2.5)

    assert captured.value.args[0] == "temperature must be between 0 and 2"
```

Keep only the operation expected to fail inside the block. If setup also raises `ValueError`,
a large block could let the test pass for the wrong reason. `match` is a regular expression,
so escape punctuation when a message contains regex metacharacters.

### Useful temporary-path and output helpers

pytest includes fixtures for common boundaries:

```python
from pathlib import Path


def test_save_result_writes_json(tmp_path: Path) -> None:
    destination = tmp_path / "result.json"

    save_result(destination, {"text": "hello"})

    assert destination.read_text(encoding="utf-8") == '{"text": "hello"}'


def test_report_prints_model_name(capsys: pytest.CaptureFixture[str]) -> None:
    report("sonnet")

    captured = capsys.readouterr()
    assert captured.out == "model: sonnet\n"
```

`tmp_path` gives each test an isolated temporary `Path`; `capsys` captures stdout and stderr.
Prefer these over manually chosen global paths or permanently redirecting output.

---

## 2. Fixtures — explicit test dependencies

A fixture is a function pytest calls to provide a named dependency. A test requests it by
parameter name:

```python
import pytest


@pytest.fixture
def sample_rows() -> list[dict[str, object]]:
    return [
        {"model": "haiku", "score": 0.82},
        {"model": "sonnet", "score": 0.94},
    ]


def test_best_row_uses_highest_score(
    sample_rows: list[dict[str, object]],
) -> None:
    assert best_row(sample_rows)["model"] == "sonnet"
```

This is dependency injection managed by pytest, not a function call hidden in the test.
Fixtures may depend on other fixtures, and pytest resolves the graph.

Use a fixture when setup is reused, has a lifecycle, or represents a meaningful test
dependency. Do not turn every literal into a fixture; local values often make a test easier
to read because its complete scenario is visible in one place.

### Setup and teardown with `yield`

Code before `yield` sets up the resource; code after it tears down the resource even when the
test fails:

```python
from collections.abc import Iterator


@pytest.fixture
def database() -> Iterator[TestDatabase]:
    db = TestDatabase()
    db.start()
    try:
        yield db
    finally:
        db.stop()
```

This mirrors `@contextmanager`. Prefer `try/finally` when teardown itself must happen even if
the fixture's post-yield assertions or other cleanup steps fail. For files and clients that
already implement context managers, use `with` inside the fixture.

### Fixture scopes

The default `scope="function"` creates a fresh value for every test. Other scopes include
`"class"`, `"module"`, `"package"`, and `"session"`:

```python
@pytest.fixture(scope="session")
def vocabulary() -> TokenVocabulary:
    return load_vocabulary()
```

Broader scopes can reduce expensive setup, but they also share state and weaken isolation. A
session-scoped mutable object can make tests order-dependent. Default to function scope and
broaden only for expensive, safely immutable or carefully reset resources.

A broader-scoped fixture cannot depend on a narrower-scoped one because the shorter-lived
value cannot safely serve the longer-lived fixture.

### `conftest.py` and fixture visibility

Put fixtures used by multiple test modules in the nearest common `conftest.py`. pytest loads
it automatically; tests do not import fixtures from it:

```python
# tests/conftest.py
import pytest


@pytest.fixture
def fake_config() -> AppConfig:
    return AppConfig(api_key="test-key", timeout=0.1)
```

A `conftest.py` applies to its directory and descendants. Keep local fixtures beside the test
that owns them; a giant root `conftest.py` becomes an implicit global dependency registry.

Avoid `autouse=True` unless the setup is truly universal and unsurprising. Explicit fixture
parameters tell the reader what a test needs.

---

## 3. Parametrisation — one contract, many cases

`@pytest.mark.parametrize` runs one test body for each data row:

```python
import pytest


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (" Hello ", "hello"),
        ("ALREADY", "already"),
        ("", ""),
    ],
)
def test_normalise_text(raw: str, expected: str) -> None:
    assert normalise_text(raw) == expected
```

Use parametrisation when the action and assertion are identical and only inputs/expected
outputs vary. It keeps edge cases visible and reports each row independently. Give opaque
cases useful IDs:

```python
@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({}, id="missing-text"),
        pytest.param({"text": 42}, id="non-string-text"),
    ],
)
def test_parse_response_rejects_invalid_payloads(payload: object) -> None:
    with pytest.raises(InvalidResponseError):
        parse_response(payload)
```

Do not force fundamentally different scenarios into one parametrised test with conditionals.
Separate tests communicate different behaviours better. Also avoid huge inline objects; use
a small factory helper or fixture when construction obscures the cases.

Parametrisation composes: stacking decorators produces the Cartesian product. That is useful
for small matrices but can silently create hundreds of tests, so count the combinations.

---

## 4. Mocking and monkeypatching

A unit test must not call a real LLM API. Real calls are slow, cost money, need secrets, may
fail with the network, and produce nondeterministic responses. Replace the boundary with a
controlled fake and assert how your code reacts.

### Prefer a small fake when behaviour matters

```python
class FakeModelClient:
    def __init__(self, response: str) -> None:
        self.response = response
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.response


def test_summarise_uses_client_and_returns_text() -> None:
    client = FakeModelClient("A short summary")

    result = summarise(client, "Long document")

    assert result == "A short summary"
    assert client.prompts == ["Summarise:\n\nLong document"]
```

Fakes are ordinary objects with working behaviour. They are easy to understand, type-check,
and evolve. Prefer dependency injection—passing a client into the code—because it makes the
external boundary explicit in production and tests.

### `monkeypatch` for process state and replacement

pytest's `monkeypatch` fixture safely restores changes after the test:

```python
def test_config_reads_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MODEL_API_KEY", "test-secret")

    config = load_config()

    assert config.api_key == "test-secret"


def test_config_rejects_missing_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MODEL_API_KEY", raising=False)

    with pytest.raises(ConfigurationError):
        load_config()
```

It can also set attributes, dictionary entries, current directories, and import paths. Use
`raising=True` (the default) for attributes so a misspelled target fails instead of silently
creating the wrong patch.

### Patch where the name is looked up

Suppose production code imports a function:

```python
# app/service.py
from vendor_sdk import generate


def summarise(document: str) -> str:
    return generate(f"Summarise:\n\n{document}")
```

The code looks up `generate` in `app.service`, so patch that name:

```python
def test_summarise_without_network(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_generate(prompt: str) -> str:
        calls.append(prompt)
        return "summary"

    monkeypatch.setattr("app.service.generate", fake_generate)

    assert summarise("document") == "summary"
    assert calls == ["Summarise:\n\ndocument"]
```

Patching `vendor_sdk.generate` after `app.service` imported it does not replace the already
bound local name. "Patch where used, not where originally defined" prevents a large class of
false mocks.

### `unittest.mock` for interaction assertions

`Mock`, `MagicMock`, `AsyncMock`, and `patch` are in the standard library:

```python
from unittest.mock import Mock


def test_summarise_calls_model_once() -> None:
    client = Mock(spec=ModelClient)
    client.generate.return_value = "summary"

    result = summarise(client, "document")

    assert result == "summary"
    client.generate.assert_called_once_with("Summarise:\n\ndocument")
```

Using `spec` or `autospec=True` catches some nonexistent attributes and bad signatures.
Without a spec, mocks happily accept typos and can let an impossible interaction pass.

Mocks are powerful but can couple tests to implementation details. Assert interactions only
when the interaction is the contract—for example, a retry count, request parameters, or not
calling a provider after validation fails. Prefer result/state assertions for internal
collaboration.

### Mocking failures and sequences

`side_effect` can raise or provide successive outcomes:

```python
client = Mock(spec=ModelClient)
client.generate.side_effect = [RateLimitError("busy"), "summary"]

assert summarise_with_retry(client, "document") == "summary"
assert client.generate.call_count == 2
```

Patch sleeping in retry tests so they remain instant. Better yet, inject a sleep callable or
retry policy; time is an external dependency too.

---

## 5. Testing async code with pytest-asyncio

Install `pytest-asyncio`, mark coroutine tests, and await production code normally:

```python
import pytest


@pytest.mark.asyncio
async def test_async_summarise_returns_model_text() -> None:
    client = FakeAsyncModelClient("summary")

    result = await summarise_async(client, "document")

    assert result == "summary"
```

Do not call `asyncio.run` inside the test; pytest-asyncio manages the event loop. Explicit
markers work in strict mode and make async tests visible. A project may instead configure
automatic discovery in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

Auto mode runs `async def` tests without an explicit marker. Choose one convention for the
project. Explicit markers are less magical and coexist well when multiple async frameworks
are present.

### Async mocks

Use `AsyncMock` for awaited methods:

```python
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_async_summarise_calls_model_once() -> None:
    client = AsyncMock(spec=AsyncModelClient)
    client.generate.return_value = "summary"

    result = await summarise_async(client, "document")

    assert result == "summary"
    client.generate.assert_awaited_once_with("Summarise:\n\ndocument")
```

`assert_called_once_with` proves the mock was called, but
`assert_awaited_once_with` proves the returned coroutine was actually awaited—the contract
that matters in async code.

Async side effects work like synchronous ones:

```python
client.generate.side_effect = [RateLimitError("busy"), "summary"]
```

If production code awaits `asyncio.sleep`, monkeypatch it with an async function, not a normal
function returning `None`:

```python
async def no_sleep(delay: float) -> None:
    observed_delays.append(delay)


monkeypatch.setattr("app.service.asyncio.sleep", no_sleep)
```

### Async fixtures

Async fixtures use `pytest_asyncio.fixture` in strict mode:

```python
from collections.abc import AsyncIterator
import pytest_asyncio


@pytest_asyncio.fixture
async def async_client() -> AsyncIterator[TestAsyncClient]:
    client = TestAsyncClient()
    await client.start()
    try:
        yield client
    finally:
        await client.aclose()
```

Request the fixture from an async test like any other fixture. Keep function scope unless a
broader lifecycle is deliberately configured. Event-loop scope and fixture caching scope are
related but distinct in modern pytest-asyncio; avoid custom loop fixtures unless the project
genuinely needs them, and follow the installed version's configuration rather than copying
old `event_loop` recipes.

### Test concurrency without relying on fragile timing

Wall-clock assertions such as "this finished under 0.1 seconds" are flaky on loaded machines.
Use events or counters to prove overlap:

```python
import asyncio


@pytest.mark.asyncio
async def test_generate_all_starts_calls_concurrently() -> None:
    both_started = asyncio.Event()
    started = 0

    async def generate(prompt: str) -> str:
        nonlocal started
        started += 1
        if started == 2:
            both_started.set()
        await asyncio.wait_for(both_started.wait(), timeout=0.2)
        return prompt.upper()

    client = AsyncMock(spec=AsyncModelClient)
    client.generate.side_effect = generate

    assert await generate_all(client, ["a", "b"]) == ["A", "B"]
```

If calls were sequential, the first would wait for a second call that never starts and the
test would fail. The event tests coordination directly; the small timeout prevents a broken
test from hanging forever.

---

## 6. Putting the pieces together

Assume this service validates input, calls an async LLM client, and retries one rate limit:

```python
# src/app/service.py
import asyncio
from typing import Protocol


class RateLimitError(Exception):
    pass


class AsyncModelClient(Protocol):
    async def generate(self, prompt: str) -> str: ...


async def summarise(
    client: AsyncModelClient,
    document: str,
    *,
    attempts: int = 2,
) -> str:
    if not document.strip():
        raise ValueError("document must not be empty")

    prompt = f"Summarise:\n\n{document.strip()}"
    for attempt in range(attempts):
        try:
            return await client.generate(prompt)
        except RateLimitError:
            if attempt == attempts - 1:
                raise
            await asyncio.sleep(0.1 * (2**attempt))

    raise AssertionError("unreachable")
```

The tests replace both external dependencies—the LLM and time—while exercising real service
control flow:

```python
# tests/test_service.py
from unittest.mock import AsyncMock

import pytest

from app.service import AsyncModelClient, RateLimitError, summarise


@pytest.mark.asyncio
async def test_summarise_calls_llm_with_normalised_prompt() -> None:
    client = AsyncMock(spec=AsyncModelClient)
    client.generate.return_value = "short summary"

    result = await summarise(client, "  long document  ")

    assert result == "short summary"
    client.generate.assert_awaited_once_with("Summarise:\n\nlong document")


@pytest.mark.parametrize("document", ["", " ", "\n\t"])
@pytest.mark.asyncio
async def test_summarise_rejects_blank_input_without_calling_llm(
    document: str,
) -> None:
    client = AsyncMock(spec=AsyncModelClient)

    with pytest.raises(ValueError, match="must not be empty"):
        await summarise(client, document)

    client.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_summarise_retries_rate_limit_without_real_sleep(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = AsyncMock(spec=AsyncModelClient)
    client.generate.side_effect = [RateLimitError("busy"), "summary"]
    delays: list[float] = []

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    monkeypatch.setattr("app.service.asyncio.sleep", fake_sleep)

    result = await summarise(client, "document", attempts=2)

    assert result == "summary"
    assert client.generate.await_count == 2
    assert delays == [0.1]


@pytest.mark.asyncio
async def test_summarise_propagates_final_rate_limit() -> None:
    client = AsyncMock(spec=AsyncModelClient)
    client.generate.side_effect = RateLimitError("still busy")

    with pytest.raises(RateLimitError, match="still busy"):
        await summarise(client, "document", attempts=1)

    client.generate.assert_awaited_once()
```

No test needs a network connection, API key, billable request, or real backoff. The suite
checks output, validation, prompt construction, retry count, delay policy, final failure, and
the crucial guarantee that invalid input never reaches the provider.

---

## Quick self-check (cold recall)

1. Which files, classes, and functions does pytest discover by default? How do you run one
   exact test and how does plain `assert` produce useful diagnostics?
2. Why should only the expected failing operation live inside `pytest.raises`? What does its
   `match` argument interpret the string as?
3. When does a fixture improve a test, and when is a local value clearer? Explain fixture
   teardown with `yield`.
4. Contrast function and session fixture scopes. What state-sharing risk comes with a broader
   scope, and where does `conftest.py` expose its fixtures?
5. When should cases be parametrised, and when should they be separate tests? What do case IDs
   buy you?
6. Contrast a fake, `monkeypatch`, and `Mock`. Why should mocks usually have a spec?
7. Explain "patch where the name is looked up" using a function imported into another
   module.
8. Why must unit tests never call a real LLM API? Which interaction assertions are useful at
   that boundary, and which can make tests brittle?
9. How does pytest-asyncio run coroutine tests? Contrast `AsyncMock.assert_awaited...` with
   ordinary call assertions, and explain how to replace an awaited sleep.
10. Why are elapsed-time assertions weak evidence of concurrency? Name one synchronisation
    primitive that can test overlap deterministically.

---

## Suggested 15-minute drill

Create an async `classify(client, text, *, attempts=3)` function and a focused pytest suite:

1. Reject blank text before calling the client; parametrize at least three blank forms.
2. Return the label from a successful `await client.classify(prompt)` call.
3. Retry a custom `RateLimitError` with exponential async sleeps.
4. Use `AsyncMock(spec=...)` for the client and assert awaited calls precisely.
5. Use `monkeypatch` to replace `asyncio.sleep` where the service looks it up; record delays
   without waiting.
6. Test success, success-after-two-failures, and propagation after the final failure.
7. Add a fixture for a reusable valid request only if it makes multiple tests clearer.
8. Run one test by node ID, then run the complete suite with `uv run pytest -q`.

The suite must make zero network calls and require no API key. Explain which assertions test
behaviour and which test the external interaction contract. Mark P-11 complete in the fluency
plan only after the quiz and drill both pass.
