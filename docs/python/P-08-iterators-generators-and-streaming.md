# Batch P-8 — Iterators, Generators & Streaming

> Reference notes for [`docs/PYTHON-FLUENCY.md`](../PYTHON-FLUENCY.md) · Batch P-8.
> Drill: pending — complete after the lesson and quiz.

*Python's iteration model lets a consumer ask for one value at a time without knowing whether
those values come from memory, a file, a computation, or a network stream. Understanding that
pull-based contract makes generators unsurprising and provides the right mental model for
processing streamed LLM output.*

---

## 1. The iteration protocol

An **iterable** is an object that can produce an iterator. An **iterator** is a stateful object
that produces its next value and eventually signals exhaustion.

```python
models = ["haiku", "sonnet", "opus"]  # iterable
iterator = iter(models)                # ask for an iterator

next(iterator)                         # "haiku"
next(iterator)                         # "sonnet"
next(iterator)                         # "opus"
next(iterator)                         # raises StopIteration
```

The protocol consists of:

- `iter(value)`, which calls `value.__iter__()`;
- `next(iterator)`, which calls `iterator.__next__()`;
- `StopIteration`, which means there are no more values.

A `for` loop handles that protocol for you. Conceptually:

```python
iterator = iter(models)
while True:
    try:
        model = next(iterator)
    except StopIteration:
        break
    print(model)
```

Do not write this expansion in normal application code; its purpose is to remove the magic
from `for`. Python iteration asks for values, not indexes, which is why lists, sets, files,
dict views, generators, and custom objects all work with the same loop syntax.

### Iterable versus iterator

A list is reusable: each call to `iter(list_value)` creates a fresh iterator. Most iterators
are single-use and return themselves from `iter(iterator)`:

```python
numbers = [1, 2, 3]

for number in numbers:
    pass
for number in numbers:                 # starts from 1 again
    pass

iterator = iter(numbers)
list(iterator)                         # [1, 2, 3]
list(iterator)                         # [] — already exhausted
```

This distinction matters in function signatures. `Iterable[str]` promises that a caller may
obtain an iterator, but it does not promise indexing, length, or repeated traversal. If an
algorithm requires two passes, accept a reusable `Sequence`, or deliberately materialise once:

```python
from collections.abc import Iterable


def compare_ends(values: Iterable[int]) -> tuple[int, int]:
    materialised = list(values)
    return materialised[0], materialised[-1]
```

Materialisation costs memory proportional to the input. Make that tradeoff explicit rather
than accidentally consuming an iterator once and finding it empty later.

### Laziness

A lazy iterator computes or retrieves a value only when the consumer requests it. This can:

- keep memory bounded;
- begin producing output before all input exists;
- avoid work when a consumer stops early;
- represent unbounded sequences.

Laziness also delays failures and side effects. Opening or parsing may not happen when the
iterator is created; an exception may appear during iteration instead. Document this when it
affects resource lifetime or error handling.

---

## 2. Generator functions and `yield`

Any function containing `yield` is a **generator function**. Calling it creates a generator
object; the body does not begin running until iteration requests the first value:

```python
from collections.abc import Iterator


def countdown(start: int) -> Iterator[int]:
    current = start
    while current > 0:
        yield current
        current -= 1


values = countdown(3)  # body has not run yet
next(values)            # 3
next(values)            # 2
list(values)            # [1]
```

At `yield`, the function returns one value temporarily and suspends. Its instruction position
and local variables remain alive. The next request resumes immediately after that `yield`.
Falling off the function ends iteration by raising `StopIteration` internally.

A generator's return annotation is normally `Iterator[T]` or `Generator[YieldType, SendType,
ReturnType]`. Use `Iterator[T]` unless callers genuinely use advanced `send()` or generator
return values.

### Memory behaviour

This generator does not build all rows first:

```python
from collections.abc import Iterator


def successful(lines: Iterator[str]) -> Iterator[str]:
    for line in lines:
        if '"status": "ok"' in line:
            yield line
```

Its working memory stays roughly constant as input grows, assuming the source is lazy too.
Writing a generator around an already materialised million-item list does not recover the
memory used by that list; the entire pipeline must preserve laziness for the benefit to hold.

### `yield from` delegates iteration

```python
from collections.abc import Iterable, Iterator


def flatten(groups: Iterable[Iterable[str]]) -> Iterator[str]:
    for group in groups:
        yield from group
```

For ordinary iteration, `yield from group` means "yield every value produced by `group`." It
also handles the full generator delegation protocol, but that machinery is rarely needed in
day-to-day data pipelines.

### Cleanup and early termination

A consumer may stop before exhaustion:

```python
for value in countdown(1_000_000):
    if value < 999_990:
        break
```

Therefore, do not assume code after the last `yield` will run promptly. Put essential cleanup
in `finally`, and prefer context managers when the iterator owns a file, connection, or stream.
Generator objects have `close()`, but making resource ownership obvious is safer than relying
on garbage collection timing.

Do not manually raise `StopIteration` inside a generator to end it; use `return` or let the
function finish. Python transforms an escaping manual `StopIteration` into `RuntimeError` to
prevent subtle bugs.

---

## 3. Generator expressions

A generator expression is the lazy counterpart of a comprehension:

```python
squares = (number * number for number in range(1_000_000))
total = sum(number * number for number in range(1_000_000))
```

Parentheses mean generator expression here, not tuple comprehension. The expression produces
each square only when requested and does not retain the entire output.

Choose based on how the result will be consumed:

```python
# Need all values, repeated traversal, indexing, or mutation:
squares_list = [number * number for number in range(10)]

# Feed one consumer once:
total = sum(number * number for number in range(10))

# Stop as soon as a match exists:
has_error = any(line.startswith("ERROR") for line in lines)
```

For a generator expression that is the sole function argument, its own parentheses may be
omitted, as in `sum(x * x for x in values)`. Add another argument and parentheses are needed.

Generators are not automatically faster. They reduce allocation and can avoid unused work,
but per-item iteration has overhead. For small collections, choose the form that communicates
ownership and reuse most clearly.

### The consumed-generator trap

```python
cleaned = (line.strip() for line in lines)

print(list(cleaned))
print(list(cleaned))  # []
```

Store a generator when single-pass behaviour is intentional. If callers might need to restart
the computation, store a generator **factory** instead:

```python
def cleaned():
    return (line.strip() for line in lines)


first_pass = list(cleaned())
second_pass = list(cleaned())
```

This only works if the underlying `lines` source is reusable too.

---

## 4. `itertools` essentials

`itertools` contains composable, lazy iterator building blocks. Three cover many practical
pipelines.

### `chain` — one sequence after another

```python
from itertools import chain

system_messages = ["Follow policy"]
user_messages = ["Hello", "Summarise this"]

for message in chain(system_messages, user_messages):
    process(message)
```

`chain` yields from each iterable in order without creating a combined list. For an iterable
of iterables, use `chain.from_iterable(groups)`.

### `islice` — lazy slicing

```python
from itertools import islice

first_five = list(islice(event_stream, 5))
page = list(islice(event_stream, 10, 20))
```

Unlike sequence slicing, `islice` does not require indexing and works on unbounded streams.
It consumes skipped values from the source. Negative indexes and negative steps are not
supported because a stream may have no known end.

### `batched` — fixed-size tuples

```python
from itertools import batched

for batch in batched(records, 100):
    upload(batch)
```

`batched` was added in Python 3.12. It lazily yields tuples of up to `n` items; the final batch
may be shorter. On Python versions supporting `strict=True`, strict mode raises when the final
batch is incomplete. Check the project's supported Python version before using newer options.

These tools share the state of their input iterator. If two consumers alternate over wrappers
around the same iterator, each advances that common source. Iterator pipelines should normally
have one clear owner and one direction of flow.

---

## 5. The streaming mindset

Collect-then-process waits for the producer to finish and stores everything:

```python
chunks = list(receive_chunks())
text = "".join(chunks)
render(text)
```

Stream processing handles each chunk as it arrives:

```python
parts: list[str] = []

for chunk in receive_chunks():
    render_delta(chunk)
    parts.append(chunk)

final_text = "".join(parts)
```

The second form reduces time to first output. It still retains chunks because the final value
is required. If only incremental effects or aggregates matter, avoid the list entirely.

Streaming changes the questions an implementation must answer:

- What exactly is a chunk: raw bytes, text delta, or structured event?
- Can a logical unit span chunk boundaries?
- What happens if the producer fails after partial output?
- Who owns cancellation and cleanup if the consumer stops?
- Is backpressure possible, or can production outrun consumption?

Network chunks are transport boundaries, not semantic boundaries. A JSON object, Unicode
character, word, or line may be split across chunks. Use the SDK's structured event layer or
an incremental decoder rather than assuming each chunk is independently parseable.

### Applying the model to an LLM stream

An LLM SDK commonly exposes a sync or async iterable of typed events. The exact API belongs
at the integration boundary, but the consumption pattern is stable:

```python
from collections.abc import Iterable, Iterator
from dataclasses import dataclass


@dataclass(frozen=True)
class TextDelta:
    text: str


def text_chunks(events: Iterable[object]) -> Iterator[str]:
    for event in events:
        if isinstance(event, TextDelta):
            yield event.text


parts: list[str] = []
for text in text_chunks(stream_events):
    print(text, end="", flush=True)
    parts.append(text)

response = "".join(parts)
```

The adapter isolates event filtering from rendering and accumulation. Real SDK event types
should replace the illustrative dataclass. Async streams use `async for`, covered in P-9;
ordinary generators and async generators are related but implement different protocols.

Avoid repeated string concatenation such as `text += chunk` for large streams: strings are
immutable, so repeated rebuilding can become quadratic. Append parts and `"".join(parts)` once.

---

## 6. Putting the pieces together

This pipeline models streamed text, batches words for a downstream sink, and stops without
collecting the entire source:

```python
from collections.abc import Iterable, Iterator
from itertools import batched, chain, islice


def words(chunks: Iterable[str]) -> Iterator[str]:
    pending = ""

    for chunk in chunks:
        pending += chunk
        *complete, pending = pending.split(" ")
        yield from (word for word in complete if word)

    if pending:
        yield pending


def preview_batches(
    system_prefix: Iterable[str],
    streamed_chunks: Iterable[str],
    *,
    batch_size: int,
    limit: int,
) -> Iterator[tuple[str, ...]]:
    all_words = chain(system_prefix, words(streamed_chunks))
    limited = islice(all_words, limit)
    yield from batched(limited, batch_size)


chunks = iter(["Generators make ", "streaming ", "natural in Python"])

for batch in preview_batches(
    ["NOTICE:"],
    chunks,
    batch_size=3,
    limit=7,
):
    print(batch)
```

`words` retains only the unfinished word between chunks, including the important case where a
word crosses a chunk boundary. `chain` prepends metadata lazily, `islice` prevents unnecessary
upstream work after the limit, and `batched` gives the sink bounded groups. Every layer pulls
from the layer before it, so the original source advances only as demand reaches it.

The parser is intentionally simplified: splitting real text correctly may require handling
all whitespace and transport decoding. The design lesson is to keep incomplete boundary state
explicit rather than pretend chunks are complete records.

---

## Quick self-check (cold recall)

1. Distinguish iterable from iterator. Which one is normally reusable, and why?
2. Expand a `for` loop into `iter`, `next`, `try`, and `StopIteration` from memory.
3. When does a generator function body begin executing, and what state survives a `yield`?
4. Why can an iterator appear empty on its second use? When should you materialise it?
5. Choose between a list comprehension and generator expression for repeated indexing, for
   `sum`, and for `any`.
6. What do `chain`, `islice`, and `batched` each contribute? Which one consumes skipped input?
7. Why does a lazy pipeline save little memory if its source is already a giant list?
8. Why must network chunks not be treated as complete words or JSON objects?
9. Compare collect-then-process with chunk-by-chunk handling in latency, memory, partial
   failure, and cleanup.
10. Why are `parts.append(chunk)` and `"".join(parts)` preferable to repeated concatenation?

---

## Suggested 15-minute drill

Build a simulated LLM text stream:

1. Write `fake_stream(text, chunk_size) -> Iterator[str]` using `yield`.
2. Make chunks split at arbitrary character positions rather than word boundaries.
3. Write `words(chunks) -> Iterator[str]` that retains incomplete words between chunks.
4. Prepend one marker with `chain`, take only the first ten words with `islice`, and group
   them with `batched`.
5. Print each batch immediately, then optionally accumulate the final text with a list and
   `join`.
6. Demonstrate the consumed-generator trap by trying a second pass, then fix the design with
   a generator factory.
7. Add a `finally` block to the producer and stop consumption early to observe cleanup.

Explain where every value is stored and when every line executes. Mark P-8 complete in the
fluency plan only after the quiz and drill both pass.
