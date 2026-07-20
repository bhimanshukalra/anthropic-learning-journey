# Batch P-9 — Async Python

> Reference notes for [`docs/PYTHON-FLUENCY.md`](../PYTHON-FLUENCY.md) · Batch P-9.
> Drill: pending — complete after the lesson and quiz.

*Async Python is not "make this function faster" syntax. It is a way for one thread to keep
many I/O operations in flight by switching tasks at explicit suspension points. The payoff
for AI engineering is direct: concurrent model calls, responsive streaming, and timeouts that
do not require one thread per request.*

---

## 1. The mental model

An asyncio program normally has one **event loop** running many **tasks**. Each task executes
ordinary Python until it reaches an operation that cannot complete yet and awaits it. At that
point, the task cooperatively yields control so the loop can run another ready task.

```python
import asyncio


async def fetch(name: str, delay: float) -> str:
    print(f"start {name}")
    await asyncio.sleep(delay)  # task pauses; the thread is free to run another task
    print(f"finish {name}")
    return name


async def main() -> None:
    first = asyncio.create_task(fetch("first", 0.2))
    second = asyncio.create_task(fetch("second", 0.1))
    results = await asyncio.gather(first, second)
    print(results)


asyncio.run(main())
```

Both waits overlap, so elapsed time is roughly the slower `0.2` seconds rather than their
`0.3`-second sum. `gather` returns results in input order (`first`, then `second`), even though
the second task finishes first.

### Concurrency is not parallelism

These terms answer different questions:

- **Async concurrency:** tasks take turns on an event-loop thread and overlap waiting.
- **Threads:** the operating system schedules multiple threads; useful for blocking I/O and
  libraries without async APIs, but shared state requires care.
- **Processes:** separate interpreters can execute Python on multiple CPU cores; useful for
  CPU-heavy work, with higher startup and communication cost.

Async wins when work spends substantial time waiting for network, database, subprocess, or
other async-aware I/O. Model API calls are a near-ideal case. It does not make Python loops,
JSON transformations, image processing, or model inference CPU work execute in parallel.

### Cooperative means blocking code blocks everyone

The event loop can switch tasks only when the running task yields control. This blocks the
entire loop:

```python
import time


async def wrong() -> None:
    time.sleep(2)  # blocks the event-loop thread
```

Use an async operation when available:

```python
async def right() -> None:
    await asyncio.sleep(2)
```

For an unavoidable blocking function, move it to a worker thread:

```python
result = await asyncio.to_thread(blocking_client.call, prompt)
```

`to_thread` keeps the loop responsive; it does not turn CPU-heavy Python into scalable
parallel work. Prefer the library's native async API when it exists.

---

## 2. Coroutines and `async`/`await`

`async def` defines a **coroutine function**. Calling it creates a coroutine object; it does
not immediately run the body:

```python
async def generate(prompt: str) -> str:
    return prompt.upper()


coroutine = generate("hello")  # body has not run; result is not a str
result = await coroutine        # schedules execution and receives "HELLO"
```

`await` may be used inside `async def`. It suspends the current coroutine until the awaitable
finishes and then evaluates to its result. Coroutines, tasks, and futures are awaitable;
ordinary values are not.

### Entering async code with `asyncio.run`

A normal script needs one synchronous entry point:

```python
import asyncio


async def main() -> None:
    result = await generate("hello")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
```

`asyncio.run` creates an event loop, runs the top-level coroutine, finalises async generators,
and closes the loop. Call it once near the edge of a CLI program, not throughout application
logic. Frameworks such as FastAPI, pytest async plugins, and notebooks already own a loop;
inside them, use `await` rather than nesting `asyncio.run`, which raises `RuntimeError`.

### The forgotten-`await` bug

```python
async def handle() -> str:
    response = generate("hello")
    return response  # wrong: returning a coroutine where str is promised
```

Python often warns that a coroutine "was never awaited," but the mistake can travel before
the warning appears. Type checking catches many cases. If an async call's result is needed
now, `await` it. If it should run concurrently, deliberately turn it into a task and retain
or supervise that task.

### Awaiting sequentially vs scheduling concurrently

This code is asynchronous but still sequential:

```python
first = await fetch("first", 0.2)
second = await fetch("second", 0.1)
```

The second call is not started until the first finishes. Concurrency requires both operations
to be scheduled before waiting for all results:

```python
first, second = await asyncio.gather(
    fetch("first", 0.2),
    fetch("second", 0.1),
)
```

Async syntax creates the possibility of concurrency; the structure of the awaits determines
whether operations actually overlap.

---

## 3. Concurrency in practice

### `asyncio.gather` for a known group of independent calls

```python
import asyncio
from collections.abc import Sequence


async def generate_all(
    client: AsyncModelClient,
    prompts: Sequence[str],
) -> list[str]:
    results = await asyncio.gather(
        *(client.generate(prompt) for prompt in prompts)
    )
    return list(results)
```

`gather` schedules the awaitables concurrently and returns their results in the same order.
By default, the first propagated exception makes the awaiting caller fail. Do not reflexively
use `return_exceptions=True`: it mixes exception objects with successful values and makes it
easy to forget a failure. Use it only when partial results are an explicit part of the API
and every item is inspected.

Unbounded fan-out can overwhelm a service, consume connections, and trigger rate limits. A
semaphore bounds operations in flight:

```python
async def generate_bounded(
    client: AsyncModelClient,
    prompts: Sequence[str],
    *,
    concurrency: int = 5,
) -> list[str]:
    semaphore = asyncio.Semaphore(concurrency)

    async def one(prompt: str) -> str:
        async with semaphore:
            return await client.generate(prompt)

    return list(await asyncio.gather(*(one(prompt) for prompt in prompts)))
```

`async with` is the asynchronous context-manager form. Acquiring a busy semaphore can await;
release is guaranteed when the block exits, including on exceptions.

### `TaskGroup` for structured concurrency

Python 3.11 introduced `asyncio.TaskGroup`:

```python
async def generate_pair(client: AsyncModelClient) -> tuple[str, str]:
    async with asyncio.TaskGroup() as group:
        summary_task = group.create_task(client.generate("Summarise"))
        title_task = group.create_task(client.generate("Write a title"))

    return summary_task.result(), title_task.result()
```

Leaving the block waits for every task. If one task fails with a non-cancellation exception,
the group cancels its remaining tasks and raises an `ExceptionGroup` containing failures.
This is **structured concurrency**: child tasks have a visible lifetime nested inside the
parent scope, so work cannot silently outlive its owner.

Use `gather` when a collection of results and input-order preservation is the natural shape.
Prefer `TaskGroup` when tasks form one operation and sibling cancellation on failure is the
desired policy. Neither choice removes the need to decide limits, timeouts, and error policy.

### Timeouts with `asyncio.wait_for`

```python
try:
    response = await asyncio.wait_for(
        client.generate(prompt),
        timeout=10.0,
    )
except TimeoutError:
    raise ModelTimeoutError(f"request exceeded 10s: {prompt!r}")
```

When the timeout expires, `wait_for` cancels the wrapped operation and raises `TimeoutError`.
Cancellation is cooperative: the coroutine receives `asyncio.CancelledError` at a suspension
point and runs its `finally` blocks while unwinding. Total wall time can therefore exceed the
nominal timeout if cleanup takes time or code suppresses cancellation.

Modern Python also offers `asyncio.timeout` for a timeout around a block:

```python
async with asyncio.timeout(10.0):
    response = await client.generate(prompt)
    await save(response)
```

Use `wait_for` for one awaitable and `asyncio.timeout` when several awaits share a deadline.
A timeout should normally be translated at the boundary where its domain meaning is known.

### Cancellation is control flow, not an ordinary failure

Cancellation lets parents, timeouts, and shutdown logic ask work to stop. Cleanup belongs in
`finally`:

```python
async def consume(stream: AsyncStream) -> None:
    try:
        async for chunk in stream:
            await persist(chunk)
    finally:
        await stream.aclose()
```

Do not swallow `asyncio.CancelledError`. If cleanup code catches it, perform cleanup and
re-raise. Also avoid broad exception handling that accidentally converts cancellation into a
retry. Cancellation means the caller no longer wants the work.

---

## 4. Async iteration and generators

Synchronous `for` assumes obtaining the next item does not need to await. An **async iterable**
supports item arrival over time, and `async for` awaits each step:

```python
async def print_stream(stream: AsyncTokenStream) -> None:
    async for token in stream:
        print(token, end="", flush=True)
```

Conceptually, `async for` calls `aiter(stream)`, then repeatedly awaits `anext(iterator)` until
`StopAsyncIteration`. You normally use the syntax rather than those protocol functions.

An **async generator** combines `async def` and `yield`:

```python
from collections.abc import AsyncIterator


async def words(text: str) -> AsyncIterator[str]:
    for word in text.split():
        await asyncio.sleep(0.05)
        yield word


async def main() -> None:
    async for word in words("tokens arrive gradually"):
        print(word)
```

Like a synchronous generator, it is lazy and retains its local state between yields. Unlike
one, it may await between items. This is the natural shape for LLM response events, database
cursors, message queues, and chunked HTTP bodies.

### Streaming is useful only if the pipeline stays streaming

```python
# Collects everything before processing: loses early-result and memory benefits.
chunks = [chunk async for chunk in stream]
await consume("".join(chunks))

# Processes incrementally.
async for chunk in stream:
    await consume(chunk)
```

Incremental consumption reduces time to first output and can bound memory. The consumer also
creates **backpressure**: because the generator advances only after the loop body finishes, a
slow consumer naturally slows production—assuming the underlying client does not buffer the
entire response itself.

An async comprehension is concise when collecting is intentional:

```python
non_empty = [chunk async for chunk in stream if chunk]
```

Do not use it merely because it is available; for large or endless streams, collection
defeats the point.

Async generators should release their resources if iteration ends early. Prefer an async
context manager supplied by the client, and place generator cleanup in `finally`:

```python
from collections.abc import AsyncIterator


async def response_chunks(client: AsyncHTTPClient, url: str) -> AsyncIterator[bytes]:
    async with client.stream("GET", url) as response:
        response.raise_for_status()
        async for chunk in response.aiter_bytes():
            yield chunk
```

The response remains open while values are yielded and closes when iteration finishes or the
generator is closed.

---

## 5. The coloring problem

Async functions and synchronous functions do not compose symmetrically:

- sync code can call an async entry point only by running an event loop;
- async code must `await` async functions;
- a synchronous callback cannot simply `await`;
- a blocking sync function called from async code blocks the event loop.

This property is often called **function coloring**: once an operation must await, its callers
usually become async all the way to a top-level boundary.

```python
# Async core: honest about awaiting network I/O.
async def build_report(client: AsyncModelClient, prompt: str) -> str:
    response = await client.generate(prompt)
    return format_report(response)


# One sync boundary for a CLI.
def cli() -> None:
    report = asyncio.run(build_report(AsyncModelClient(), "Summarise"))
    print(report)
```

Do not hide `asyncio.run` inside reusable library functions. It prevents composition in
applications whose event loop is already running. Expose an async API when the work is
fundamentally async, and let the outermost application choose how to run it.

If a package genuinely serves both worlds, it may provide separate `Client` and `AsyncClient`
interfaces. Avoid a single function that sometimes returns a value and sometimes a coroutine;
that makes every caller branch on execution mode and defeats type checking.

### Keep pure logic synchronous

Not every caller in an async program must be async. Pure transformations that do not await
should remain ordinary functions:

```python
def build_prompt(document: str) -> str:
    return f"Summarise:\n\n{document.strip()}"


async def summarise(client: AsyncModelClient, document: str) -> str:
    prompt = build_prompt(document)
    return await client.generate(prompt)
```

This confines the async color to I/O orchestration and keeps domain logic easy to test. The
boundary is not "make the entire codebase async"; it is "make the call chain that waits on
async I/O async."

---

## 6. Putting the pieces together

This pipeline runs model calls concurrently with a limit, gives each call a timeout, and
streams results as tasks finish:

```python
import asyncio
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class Completion:
    index: int
    text: str


class ModelTimeoutError(Exception):
    pass


async def complete_one(
    client: AsyncModelClient,
    prompt: str,
    index: int,
    semaphore: asyncio.Semaphore,
    *,
    timeout: float,
) -> Completion:
    async with semaphore:
        try:
            text = await asyncio.wait_for(
                client.generate(prompt),
                timeout=timeout,
            )
        except TimeoutError as error:
            raise ModelTimeoutError(f"prompt {index} timed out") from error

    return Completion(index=index, text=text)


async def completions_as_ready(
    client: AsyncModelClient,
    prompts: Sequence[str],
    *,
    concurrency: int = 5,
    timeout: float = 10.0,
) -> AsyncIterator[Completion]:
    semaphore = asyncio.Semaphore(concurrency)
    tasks = [
        asyncio.create_task(
            complete_one(
                client,
                prompt,
                index,
                semaphore,
                timeout=timeout,
            )
        )
        for index, prompt in enumerate(prompts)
    ]

    try:
        for completed in asyncio.as_completed(tasks):
            yield await completed
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


async def main() -> None:
    client = AsyncModelClient()
    async for completion in completions_as_ready(
        client,
        ["Summarise A", "Summarise B", "Summarise C"],
        concurrency=2,
    ):
        print(completion.index, completion.text)


if __name__ == "__main__":
    asyncio.run(main())
```

The semaphore limits pressure on the service, `wait_for` bounds each request, and
`as_completed` exposes early results instead of waiting for input order. The generator's
`finally` block cancels and awaits outstanding tasks if its consumer stops early, preventing
orphaned work and "Task exception was never retrieved" warnings. Real client construction
would normally also use its async context manager so network connections close cleanly.

Choose this more elaborate shape only when completion-order streaming is valuable. If all
results are required before the next step, bounded `gather` is simpler and should win.

---

## Quick self-check (cold recall)

1. What does the event loop do, and at exactly what kind of point can another task run? Why
   does `time.sleep` inside `async def` block unrelated tasks?
2. Contrast async concurrency, threads, and processes. Which one helps a CPU-heavy Python
   calculation use multiple cores?
3. What happens when an `async def` function is called? Contrast a coroutine object, a task,
   and the result obtained with `await`.
4. Why are two consecutive awaited calls still sequential? Show how to overlap them with
   `gather`.
5. Compare `gather` and `TaskGroup`, including result order and sibling-failure behaviour.
6. What does `wait_for` do on expiry? Why can real elapsed time exceed the timeout, and why
   should cancellation normally be re-raised?
7. Explain `async for` and an async generator in terms of awaiting and yielding. How does a
   streaming consumer provide backpressure?
8. What is the coloring problem? Where should `asyncio.run` live, and why should pure
   transformations remain synchronous?
9. Why can unbounded fan-out harm an API? What does an `asyncio.Semaphore` guarantee?

---

## Suggested 15-minute drill

Create a fake async model client whose `generate` method sleeps for a prompt-specific delay
and then returns the uppercased prompt:

1. Write a sequential version for five prompts and measure its elapsed time.
2. Rewrite it with `asyncio.gather` and show that result order remains input order.
3. Add a semaphore limiting concurrency to two; track and assert the maximum active count.
4. Give one prompt a delay beyond `asyncio.wait_for`'s timeout and translate `TimeoutError`
   into a custom `ModelTimeoutError` with exception chaining.
5. Write an async generator that yields successful results as tasks finish and consume it
   with `async for`.
6. Stop consumption after the first result; cancel and await remaining tasks in `finally`.
7. Deliberately replace one `await asyncio.sleep(...)` with `time.sleep(...)` and explain the
   timing change before restoring it.

Keep every delay below one second. From cold recall, explain where tasks are created, where
control can switch, and who owns cancellation. Mark P-9 complete in the fluency plan only
after the quiz and drill both pass.
