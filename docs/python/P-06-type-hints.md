# Batch P-6 — Type Hints

> Reference notes for [`docs/PYTHON-FLUENCY.md`](../PYTHON-FLUENCY.md) · Batch P-6.
> Drill: pending — complete after the lesson and quiz.

*Python remains dynamically typed, but modern Python code communicates its intended shapes
with type hints. Hints make interfaces easier to read, let editors and checkers catch mistakes
before execution, and give frameworks enough metadata to build schemas—without changing what
the interpreter normally accepts at runtime.*

---

## 1. Core annotation syntax

Annotate parameters after their names and a return type after `->`:

```python
def token_cost(input_tokens: int, output_tokens: int, rate: float) -> float:
    return (input_tokens + output_tokens) * rate
```

The annotation is a contract for callers and tooling: `input_tokens` should be an `int`, and
the function promises a `float`. It is not a cast and does not automatically validate data.

Local variables can be annotated too:

```python
model: str = "sonnet"
attempts: int = 0
scores: list[float] = [0.82, 0.91]
usage: dict[str, int] = {"input": 120, "output": 40}
```

Since Python 3.9, built-in collections are generic: prefer `list[str]`, `dict[str, int]`,
`set[str]`, and `tuple[int, int]` over the older `typing.List`, `typing.Dict`, and friends.
A fixed tuple describes each position; a variable-length homogeneous tuple uses an ellipsis:

```python
coordinate: tuple[float, float] = (12.5, 7.0)
samples: tuple[float, ...] = (0.4, 0.6, 0.9)
```

Annotate boundaries and public interfaces first. Obvious locals such as `attempts = 0` are
usually inferred, so annotating every name adds noise rather than safety.

### Prefer abstract input types when the implementation is flexible

If a function only iterates, it need not demand a list:

```python
from collections.abc import Iterable, Mapping, Sequence


def total_tokens(counts: Iterable[int]) -> int:
    return sum(counts)


def first_prompt(prompts: Sequence[str]) -> str:
    return prompts[0]


def timeout(config: Mapping[str, float]) -> float:
    return config.get("timeout", 30.0)
```

`Iterable` promises iteration, `Sequence` also promises indexing and length, and `Mapping`
promises mapping-style reads. Use the smallest capability the function needs. Returning a
concrete `list[T]` is often helpful because it tells callers exactly what they receive.

`Any` disables useful checking for a value and lets it flow unchecked:

```python
from typing import Any

payload: Any = load_unknown_data()
payload.made_up.method()  # a checker permits this
```

Use `Any` at genuinely untyped boundaries, then validate or narrow it promptly. `object` is
safer when the value may be anything but code must inspect it before using type-specific
operations.

---

## 2. Optional values and unions

The `|` operator describes alternatives:

```python
def parse_identifier(value: str | int) -> str:
    return str(value)
```

`str | None` means the value is either a string or exactly `None`:

```python
def display_name(name: str | None) -> str:
    if name is None:
        return "anonymous"
    return name.strip()
```

After the `None` check, a type checker narrows `name` to `str`. The older spelling
`Optional[str]` means exactly `str | None`; it does **not** mean the argument itself may be
omitted. Defaults control omission:

```python
def greet(name: str | None) -> str: ...          # required argument; None is valid
def greet(name: str = "world") -> str: ...      # optional argument; None is invalid
def greet(name: str | None = None) -> str: ...   # optional argument; None is valid
```

Treat optionality as a contract, not an invitation to add `None` everywhere. Every union
creates branches that downstream code must handle. If absence is invalid, keep the narrower
type and reject missing data at the boundary.

Prefer explicit narrowing to assertions that merely silence the checker:

```python
model: str | None = read_model()

if model is None:
    raise ValueError("model is required")

send(model)  # narrowed to str
```

For larger unions, `isinstance` narrows by runtime type. A long chain of type tests can signal
that the data needs a shared protocol or a tagged representation instead.

---

## 3. `TypedDict`, `Literal`, and `Enum`

These tools describe closed shapes and choices—especially useful for JSON payloads and LLM
tool schemas.

### `TypedDict` — a typed dictionary shape

```python
from typing import NotRequired, TypedDict


class Message(TypedDict):
    role: str
    content: str
    name: NotRequired[str]


message: Message = {"role": "user", "content": "Explain generators"}
```

At runtime, `message` is an ordinary dict, not a `Message` instance. `TypedDict` helps a
checker verify required keys and value types; it does not validate incoming JSON.
`NotRequired` marks an individual key as omittable. For a shape where most keys are optional,
`TypedDict(..., total=False)` is available, though explicit requiredness is often clearer.

Use `TypedDict` when the runtime representation must remain dict-shaped—for example an API
payload. Prefer a dataclass or validated model when behaviour, defaults, invariants, or
runtime parsing matter.

### `Literal` — exact permitted values

```python
from typing import Literal

Role = Literal["system", "user", "assistant"]


def add_message(role: Role, content: str) -> None:
    ...
```

A checker rejects `add_message("admin", "...")`. The runtime still receives a normal string.
`Literal` is excellent for a small, local set of wire-format values and for overloads whose
return type depends on an exact argument.

### `Enum` — named runtime values

```python
from enum import StrEnum


class FinishReason(StrEnum):
    STOP = "stop"
    MAX_TOKENS = "max_tokens"


def handle_finish(reason: FinishReason) -> None:
    if reason is FinishReason.MAX_TOKENS:
        ...
```

An enum creates a real runtime type with named members, iteration, identity, and a central
namespace. `StrEnum` members also behave like strings, which is convenient at JSON boundaries.
Use `Literal` for lightweight static restrictions; use `Enum` when the choices deserve
runtime identity, behaviour, discoverability, or reuse across many interfaces. Neither
automatically converts an arbitrary incoming string—parse or validate it first.

---

## 4. Generics lite — preserving relationships between types

A generic says that types in different positions are related. `TypeVar` names the unknown
type so a checker can preserve it:

```python
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def first(items: Sequence[T]) -> T:
    return items[0]


name = first(["haiku", "sonnet"])  # inferred as str
score = first([0.8, 0.9])           # inferred as float
```

Writing `object` would lose that relationship: it would say the return value may be any
object, rather than "the same element type as the input." A type variable is useful when the
same unknown type appears more than once in a signature.

A type variable can be constrained or bounded:

```python
from typing import TypeVar

Number = TypeVar("Number", int, float)  # one of these exact alternatives


def clamp(value: Number, low: Number, high: Number) -> Number:
    return min(max(value, low), high)
```

A bound such as `TypeVar("T", bound=SupportsClose)` means any subtype satisfying that upper
limit. Constraints select from listed alternatives. Do not reach for generics to make every
helper maximally abstract; write them when they preserve information a caller actually uses.

In modern Python you may also encounter the Python 3.12 type-parameter syntax:

```python
def first[T](items: Sequence[T]) -> T:
    return items[0]
```

It expresses the same central idea. You will read generic library types far more often than
write them: `list[T]`, `Iterable[T]`, `Callable[[T], R]`, and classes such as `Repository[T]`.

---

## 5. The checker and the runtime are different systems

Annotations are stored as metadata and consumed by editors, static checkers, documentation
tools, and frameworks. Ordinary Python execution does not enforce them:

```python
def double(value: int) -> int:
    return value * 2


double("ha")  # runs and returns "haha", despite the incorrect call
```

A checker catches the call before deployment:

```text
pyright src tests
mypy src tests
```

Use the checker configured by the project rather than adding a second one casually. Run it in
CI so annotations remain trustworthy. Strictness settings matter: the same codebase may
produce different diagnostics under different configurations.

Type checking is static analysis, not input validation. Data from JSON, environment variables,
files, users, or APIs remains untrusted at runtime. Validate it before claiming a narrow type;
Pydantic in P-10 is one common boundary tool.

Avoid `cast` as if it converted a value:

```python
from typing import cast

value = cast(str, external_value)  # tells the checker; performs no runtime conversion
value = str(external_value)        # actually constructs a string
```

Likewise, `# type: ignore` suppresses a diagnostic rather than solving it. When suppression is
necessary—often around an incomplete third-party library—make it narrow, include the error
code supported by the checker, and explain the boundary.

### Gradual typing is deliberate

A Python project can mix annotated and unannotated code. Add types where they produce the
most leverage:

- public functions and class methods;
- data crossing module or service boundaries;
- callback signatures and non-obvious return shapes;
- code where `None`, unions, or container element types otherwise stay implicit.

Annotations should clarify design. If a type becomes enormous, consider naming it with a
type alias, simplifying the data model, or replacing loosely shaped dictionaries with a
dedicated structure.

---

## 6. Putting the pieces together

This example types an LLM request while keeping static checking and runtime validation
separate:

```python
from enum import StrEnum
from typing import Literal, NotRequired, TypedDict, TypeVar


class Role(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ToolCall(TypedDict):
    name: str
    arguments: dict[str, object]


class Message(TypedDict):
    role: Role
    content: str
    tool_call: NotRequired[ToolCall]


Mode = Literal["fast", "accurate"]
T = TypeVar("T")


def require(value: T | None, *, field: str) -> T:
    if value is None:
        raise ValueError(f"{field} is required")
    return value


def build_request(
    messages: list[Message],
    model: str | None,
    *,
    mode: Mode = "accurate",
) -> dict[str, object]:
    checked_model = require(model, field="model")
    return {
        "model": checked_model,
        "messages": messages,
        "temperature": 0.0 if mode == "accurate" else 0.7,
    }


request = build_request(
    [{"role": Role.USER, "content": "Summarise this"}],
    model="sonnet",
    mode="fast",
)
```

`TypedDict` captures JSON-like shapes, the enum gives roles runtime identity, `Literal`
restricts a small configuration choice, and `require` uses a type variable to preserve the
non-`None` input type. The explicit check also enforces the invariant at runtime. The final
return type remains broad because different keys hold unrelated values; a dedicated
`TypedDict` would be the next step if callers need to inspect the request precisely.

---

## Quick self-check (cold recall)

1. What does `dict[str, list[int]]` describe? Does Python enforce it when the program runs?
2. Why might a parameter accept `Iterable[str]` while the function returns `list[str]`?
3. Contrast `str | None`, a parameter with a default, and `Optional[str]`.
4. How does an `if value is None` branch help both runtime correctness and static narrowing?
5. What is a `TypedDict` instance at runtime? When should it give way to a dataclass or a
   validated model?
6. Choose between `Literal` and `Enum` for a three-value option, and explain the tradeoff.
7. Why does `def first(items: Sequence[T]) -> T` preserve more information than returning
   `object`?
8. What do `cast` and `# type: ignore` change at runtime? Where must external input actually
   be validated?
9. Why can pyright or mypy reject `double("ha")` even though CPython executes it successfully?

---

## Suggested 15-minute drill

Create a typed tool-call request module:

1. Define `Role` as a `StrEnum` and `Mode` as a two-value `Literal`.
2. Define `ToolCall` and `Message` with `TypedDict`; make one message key optional.
3. Write `require(value: T | None, *, field: str) -> T` and prove the returned value is
   narrowed without using `cast`.
4. Write `build_request(messages, model, *, mode=...)` with complete parameter and return
   annotations.
5. Add one valid and three deliberately invalid calls: a missing dict key, a bad literal, and
   `None` where a string is required.
6. Run the project's pyright or mypy command, predict each diagnostic first, then fix the
   invalid calls.
7. Pass malformed runtime data once and explain why annotations alone do not reject it.

Explain every annotation from memory. Mark P-6 complete in the fluency plan only after the
quiz and drill both pass.
