# Batch P-4 — Functions, Properly

> Reference notes for [`docs/PYTHON-FLUENCY.md`](../PYTHON-FLUENCY.md) · Batch P-4.
> Drill: pending — complete after the lesson and quiz.

*Defining a basic function is easy. Python fluency comes from understanding its argument
model, treating functions as ordinary values, reading decorators without magic, and knowing
exactly which scope a name belongs to.*

---

## 1. Arguments in full

Python supports positional arguments, keyword arguments, defaults, variadic arguments, and
explicit positional-only or keyword-only boundaries. A well-designed signature makes invalid
calls difficult and documents intent before a docstring is opened.

### Positional and keyword arguments

```python
def generate(prompt: str, model: str, temperature: float = 0.0) -> str:
    return f"{model}: {prompt} ({temperature=})"


generate("Summarise this", "sonnet")
generate("Summarise this", model="sonnet", temperature=0.2)
generate(prompt="Summarise this", model="sonnet")
```

Positional arguments are matched left to right. Keyword arguments are matched by parameter
name and improve readability when a value's meaning is not obvious. Once a call uses a
keyword argument, ordinary positional arguments cannot follow it.

Defaults are evaluated **once**, when the `def` statement executes—not on each call. P-2's
mutable-default rule therefore still applies:

```python
def collect(value: str, items: list[str] | None = None) -> list[str]:
    if items is None:
        items = []
    items.append(value)
    return items
```

Required parameters must normally come before parameters with defaults. Keyword-only
parameters are the useful exception because their order does not make calls ambiguous.

### Keyword-only arguments with `*`

Place a bare `*` in the signature to require all later arguments by name:

```python
def call_model(
    prompt: str,
    *,
    timeout: float = 30.0,
    retries: int = 2,
    stream: bool = False,
) -> str:
    ...


call_model("Explain generators", timeout=10, stream=True)  # clear
call_model("Explain generators", 10, 2, True)              # TypeError
```

Use keyword-only parameters for options, booleans, and multiple same-typed values. The call
`call_model(prompt, 10, 2, True)` is legal-looking but unreadable; the signature can forbid it.

If a function already accepts `*args`, parameters after `*args` are automatically
keyword-only:

```python
def log_many(*messages: str, level: str = "INFO") -> None:
    ...
```

### Positional-only arguments with `/`

Parameters before `/` cannot be passed by name:

```python
def ratio(numerator: float, denominator: float, /) -> float:
    return numerator / denominator


ratio(10, 4)                              # valid
ratio(numerator=10, denominator=4)        # TypeError
```

Positional-only parameters are common in built-ins and useful when parameter names are an
implementation detail, or when any keyword must be accepted by `**kwargs` without collision.
Application code uses `/` less often than `*`, but you must be able to read it.

The complete ordering is:

```python
def example(pos_only, /, positional_or_keyword, *args, keyword_only, **kwargs):
    ...
```

### `*args` and `**kwargs`

```python
def record(event: str, *tags: str, **metadata: object) -> dict[str, object]:
    return {
        "event": event,
        "tags": tags,
        "metadata": metadata,
    }


record("request", "llm", "production", model="sonnet", tokens=450)
```

Inside the function:

- `args` is a tuple of extra positional arguments.
- `kwargs` is a dict of extra keyword arguments.
- The names are conventional; the `*` and `**` create the behaviour.

Do not add variadic arguments "for flexibility" without a concrete reason. An explicit
signature is easier for callers, IDEs, type checkers, and future maintainers. Variadics pay
rent in adapters, decorators, forwarding functions, and APIs whose cardinality is genuinely
variable.

### Unpacking calls with `*` and `**`

At a call site, the same symbols unpack containers into arguments:

```python
def create_job(prompt: str, model: str, *, timeout: float = 30.0) -> None:
    ...


identity = ("Summarise this", "sonnet")
options = {"timeout": 10.0}
create_job(*identity, **options)
```

This is conceptually:

```python
create_job("Summarise this", "sonnet", timeout=10.0)
```

Duplicate values are errors. `create_job("x", *identity)` may supply `prompt` twice, and
`create_job(*identity, timeout=5, **options)` supplies `timeout` twice. Python raises
`TypeError` rather than choosing a winner.

---

## 2. Functions are first-class objects

A Python function is an ordinary object. It can be assigned to a name, stored in a container,
passed as an argument, returned from another function, and inspected at runtime.

```python
def normalise(text: str) -> str:
    return text.strip().lower()


operation = normalise                 # no parentheses: store the function itself
result = operation("  Hello  ")       # parentheses: call it

pipeline = [str.strip, str.lower]
value = "  Hello  "
for transform in pipeline:
    value = transform(value)
```

The difference between `normalise` and `normalise()` is fundamental: the first is the
function object; the second is the result of calling it.

### Functions as arguments

```python
from collections.abc import Callable, Iterable


def transform_all(
    values: Iterable[str],
    transform: Callable[[str], str],
) -> list[str]:
    return [transform(value) for value in values]


cleaned = transform_all([" A ", " B "], str.strip)
```

`Callable[[str], str]` means "a callable accepting one string and returning a string." It
describes functions, bound methods, and callable objects without caring which one was passed.

Callbacks appear throughout Python: `sorted(..., key=...)`, web route handlers, retry hooks,
event listeners, and test parametrisation.

### Closures — functions that retain surrounding state

A nested function can reference names from the enclosing function even after the outer call
has returned:

```python
from collections.abc import Callable


def make_threshold(minimum: float) -> Callable[[float], bool]:
    def passes(score: float) -> bool:
        return score >= minimum

    return passes


is_good = make_threshold(0.8)
is_good(0.91)                         # True
is_good(0.72)                         # False
```

`passes` closes over the `minimum` binding. The returned function carries that environment
with it; no class is required merely to retain one piece of configuration.

Closures capture **names**, not frozen snapshots of their values. This causes the late-binding
trap when functions are created in a loop:

```python
checks = [lambda: threshold for threshold in (0.5, 0.7, 0.9)]
[check() for check in checks]         # [0.9, 0.9, 0.9]
```

Each lambda looks up the same final `threshold` when called. Bind the current value through a
default argument:

```python
checks = [lambda threshold=threshold: threshold for threshold in (0.5, 0.7, 0.9)]
```

This works because defaults are evaluated when each lambda is created—the same rule that
causes the mutable-default trap, used deliberately.

---

## 3. Lambdas — small anonymous functions

A lambda is a function restricted to one expression:

```python
lambda row: row["score"]
```

It is roughly equivalent to:

```python
def get_score(row):
    return row["score"]
```

Lambdas are idiomatic when the behaviour is tiny, local, and disposable:

```python
ranked = sorted(rows, key=lambda row: (-row["score"], row["latency_ms"]))
```

Prefer `def` when the function:

- deserves a meaningful name;
- is reused;
- needs annotations, a docstring, or multiple expressions;
- contains enough logic to require explanation or testing.

Do not contort statements, nested conditionals, or exception handling into a lambda. The
one-expression restriction is a readability boundary, not a puzzle.

Sometimes a standard tool states intent better than a lambda:

```python
from operator import attrgetter, itemgetter


sorted(rows, key=itemgetter("score"))
sorted(jobs, key=attrgetter("created_at"))
```

---

## 4. Decorators — function transformation with `@` syntax

A decorator accepts a function and returns a replacement function. This:

```python
@trace
def generate(prompt: str) -> str:
    ...
```

is syntax sugar for:

```python
def generate(prompt: str) -> str:
    ...


generate = trace(generate)
```

The decoration happens when the `def` statement executes—normally during module import—not
each time `generate` is called. The returned wrapper is what later calls invoke.

### Writing a basic decorator

```python
from collections.abc import Callable
from functools import wraps
from typing import Any


def trace(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"finished {func.__name__}")
        return result

    return wrapper
```

`wrapper` accepts and forwards arbitrary arguments so the decorator can wrap different
signatures. It is also a closure: it retains `func` after `trace` returns.

### Why `functools.wraps` matters

Without `@wraps(func)`, the decorated function appears to be named `wrapper`; its docstring,
annotations, and introspection metadata are obscured. That breaks debugging, documentation,
test tools, and frameworks that inspect callables.

`@wraps` copies important metadata and sets `__wrapped__`, allowing inspection tools to reach
the original. Treat it as mandatory for ordinary wrapper decorators.

### Decorators with configuration

A decorator called with arguments adds one more function layer:

```python
import time
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def retry(attempts: int, *, delay: float = 0.0):
    def decorate(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_error: Exception | None = None
            for attempt in range(attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as error:
                    last_error = error
                    if attempt < attempts - 1:
                        time.sleep(delay)
            assert last_error is not None
            raise last_error

        return wrapper

    return decorate
```

Usage:

```python
@retry(3, delay=0.25)
def fetch() -> str:
    ...
```

Read it inside out:

1. `retry(3, delay=0.25)` runs first and returns `decorate`.
2. `decorate(fetch)` runs and returns `wrapper`.
3. The name `fetch` is rebound to `wrapper`.
4. Each later `fetch()` call runs the retry loop.

The example demonstrates structure, not a production retry policy: real retry code should
catch narrow transient exceptions and define backoff, jitter, logging, and cancellation
behaviour. P-7 covers that policy.

### Stacked decorators

```python
@authorise
@trace
def generate(prompt: str) -> str:
    ...
```

is equivalent to:

```python
generate = authorise(trace(generate))
```

The decorator closest to the function is applied first. At call time, the outer wrapper
(`authorise`) runs before the inner wrapper (`trace`). Order can therefore change behaviour.

### Registration decorators may not wrap

Not every decorator replaces behaviour. Framework decorators often register the original
function and return it unchanged:

```python
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

Pytest fixtures, FastAPI routes, CLI commands, dataclasses, and caching APIs all use decorator
syntax. The reliable mental model remains: evaluate the decorator expression, pass it the
defined object, bind the returned object to the original name.

---

## 5. Scope — LEGB name resolution

When Python reads a name, it searches outward in this order:

1. **Local** — the current function.
2. **Enclosing** — outer functions, if nested.
3. **Global** — the current module.
4. **Built-in** — names such as `len`, `str`, and `Exception`.

```python
label = "global"


def outer() -> None:
    label = "enclosing"

    def inner() -> None:
        label = "local"
        print(label)

    inner()
```

`inner` prints `"local"`. Remove its assignment and it finds `"enclosing"`; remove that and it
finds `"global"`.

### Assignment makes a name local

If a function assigns to a name anywhere in its body, Python treats that name as local
throughout the function unless declared otherwise:

```python
count = 10


def increment() -> int:
    print(count)       # UnboundLocalError
    count = count + 1
    return count
```

Python knows `count` is local because of the assignment, but the local value does not exist
when `print` runs. This is determined when the function is compiled, not dynamically line by
line.

Reading a global needs no declaration. Rebinding one requires `global`:

```python
count = 10


def increment() -> int:
    global count
    count += 1
    return count
```

This is legal but usually poor design: hidden shared mutation makes functions harder to test
and reason about. Prefer returning the new value, passing state explicitly, or encapsulating
state in an object.

### `nonlocal` rebinds an enclosing function's name

```python
from collections.abc import Callable


def make_counter() -> Callable[[], int]:
    count = 0

    def increment() -> int:
        nonlocal count
        count += 1
        return count

    return increment
```

`nonlocal` searches enclosing function scopes—not module globals—and allows rebinding their
names. Without it, `count += 1` would make `count` local to `increment` and cause
`UnboundLocalError`.

Mutation does not require rebinding the name:

```python
def make_collector() -> Callable[[str], list[str]]:
    items: list[str] = []

    def collect(item: str) -> list[str]:
        items.append(item)             # mutates the object; does not rebind `items`
        return items.copy()

    return collect
```

No `nonlocal` is needed because `items` continues to refer to the same list. This is the same
binding-versus-mutation distinction from P-2.

### Avoid shadowing useful names

```python
list = [1, 2, 3]       # shadows built-in list()
id = "job-123"         # shadows built-in id()
```

Python permits shadowing, but calling `list(...)` later now fails because `list` refers to an
object rather than the built-in type. Use names such as `items`, `job_id`, `format_name`, and
`input_text`; do not repurpose built-ins or imported module names.

---

## 6. Putting the pieces together

This example combines a keyword-only API, a closure, a first-class callback, and a decorator:

```python
from collections.abc import Callable, Iterable
from functools import wraps
from time import perf_counter
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def timed(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        started = perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            print(f"{func.__name__}: {perf_counter() - started:.3f}s")

    return wrapper


def make_passes(minimum: float) -> Callable[[float], bool]:
    return lambda score: score >= minimum


@timed
def select_scores(
    scores: Iterable[float],
    predicate: Callable[[float], bool],
    *,
    descending: bool = True,
) -> list[float]:
    selected = [score for score in scores if predicate(score)]
    return sorted(selected, reverse=descending)


passing = select_scores(
    [0.72, 0.94, 0.81],
    make_passes(0.8),
    descending=True,
)
```

The public call reads like a specification. `select_scores` does not know how passing is
defined, the closure retains that policy, the keyword-only flag makes the boolean legible,
and `@timed` adds an orthogonal concern without contaminating the selection logic.

---

## Quick self-check (cold recall)

1. In `def f(a, /, b, *, c)`, how may each parameter be passed? Why would an API use `/` or
   `*`?
2. What are the runtime types of `args` and `kwargs`? When is an explicit signature better?
3. Explain the difference between passing `normalise` and `normalise()` to another function.
4. Why do three lambdas created in a loop often observe the same final value? Show the
   default-argument fix.
5. Expand `@retry(3)` into ordinary assignment syntax. At what time does decoration happen?
6. Why is `@wraps` important, and in what order are stacked decorators applied?
7. Explain LEGB and derive the `UnboundLocalError` caused by reading a name before assigning
   it in the same function.
8. Contrast `nonlocal` rebinding with mutating a captured list. Why does only one require a
   declaration?

---

## Suggested 15-minute drill

Write a small in-memory evaluation pipeline:

1. Define `select(rows, predicate, *, limit=None)` with `limit` keyword-only.
2. Pass a predicate created by `make_min_score(minimum)`, which returns a closure.
3. Add a `@timed` decorator that preserves metadata with `@wraps`.
4. Add `apply_all(value, *transforms)` and forward the transforms in order.
5. Verify `select.__name__ == "select"` after decoration.
6. Create three threshold predicates in a loop, first reproducing late binding and then fixing
   it with a default argument.

Run the script and explain every `*`, `**`, closure, and wrapper from memory. Mark P-4 complete
in the fluency plan only after the quiz and drill both pass.
