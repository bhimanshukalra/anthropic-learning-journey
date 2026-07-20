# Batch P-5 — OOP the Python Way

> Reference notes for [`docs/PYTHON-FLUENCY.md`](../PYTHON-FLUENCY.md) · Batch P-5.
> Drill: pending — complete after the lesson and quiz.

*Python supports familiar object-oriented ideas, but its style is deliberately light. Classes
are ordinary objects, conventions replace access-control ceremony, data classes remove
boilerplate, and small behavioural interfaces matter more than elaborate inheritance trees.*

---

## 1. Classes without ceremony

A class statement creates a new class object. Calling that class normally allocates an
instance and then passes it to `__init__` for initialisation:

```python
class ModelClient:
    provider = "anthropic"             # class attribute

    def __init__(self, model: str, timeout: float = 30.0) -> None:
        self.model = model              # instance attribute
        self.timeout = timeout

    def describe(self) -> str:
        return f"{self.provider}/{self.model} ({self.timeout}s)"


client = ModelClient("sonnet", timeout=10.0)
print(client.describe())
```

`self` is the instance on which a method was called. It is explicit in the definition but
supplied automatically at the call site:

```python
client.describe()
ModelClient.describe(client)            # equivalent, but rarely written
```

`self` is a convention rather than a reserved word, but departing from it only makes code
harder to read. Unlike Java or Kotlin, fields do not need a separate declaration: assigning
`self.name` creates or replaces an instance attribute.

`__init__` initialises an already-created object; it is not the constructor in the strict
sense and must return `None`. Custom allocation through `__new__` exists, but ordinary
application classes almost never need it.

### Class attributes versus instance attributes

Attribute lookup on `client.provider` first checks the instance, then its class and base
classes. This makes class attributes suitable for shared constants and defaults:

```python
first = ModelClient("haiku")
second = ModelClient("sonnet")

first.provider = "local"               # creates an attribute on first only
print(first.provider)                   # local
print(second.provider)                  # anthropic
print(ModelClient.provider)             # anthropic
```

The mutable class-attribute trap is the object-oriented cousin of a mutable default argument:

```python
class BadQueue:
    jobs: list[str] = []                # one list shared by every instance


class Queue:
    def __init__(self) -> None:
        self.jobs: list[str] = []       # a new list per instance
```

Use class attributes for genuinely shared state. Put per-instance mutable state on `self`, or
use a dataclass `default_factory` as shown later.

### Python has conventions, not enforced privacy

```python
class ApiClient:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
```

A leading underscore means "internal implementation detail." It asks callers not to depend
on the attribute, but does not prevent access. This is social encapsulation supported by
documentation, IDEs, and linters.

Double-leading underscores trigger name mangling:

```python
class Parent:
    def __init__(self) -> None:
        self.__state = "parent"         # stored approximately as _Parent__state
```

Name mangling mainly avoids accidental collisions in subclasses; it is not a security or
privacy boundary. Do not use it merely to imitate `private`. Public attributes are normal in
Python, and a property can preserve the public API if validation is needed later.

### Class methods and static methods

Although not the core of this batch, these forms are common when reading class APIs:

```python
class Endpoint:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    @classmethod
    def parse(cls, value: str) -> "Endpoint":
        host, port = value.rsplit(":", maxsplit=1)
        return cls(host, int(port))

    @staticmethod
    def is_valid_port(port: int) -> bool:
        return 0 < port < 65_536
```

A class method receives `cls` and is useful for alternative constructors because subclasses
can produce their own type. A static method receives neither `self` nor `cls`; use one only
when a function belongs conceptually in the class namespace. Otherwise, a module-level
function is simpler.

---

## 2. Dunder methods — joining Python's object protocols

"Dunder" means double underscore. Methods such as `__len__` are hooks used by Python syntax
and built-ins. Implementing the relevant protocol lets a class behave like the rest of the
language instead of exposing Java-style methods such as `getLength()`.

### `__repr__` — a developer-facing representation

```python
class Run:
    def __init__(self, run_id: str, tokens: int) -> None:
        self.run_id = run_id
        self.tokens = tokens

    def __repr__(self) -> str:
        return f"Run(run_id={self.run_id!r}, tokens={self.tokens!r})"
```

`repr(run)` and the `!r` f-string conversion call `__repr__`. Aim for an unambiguous,
information-rich representation, ideally resembling valid construction syntax. Never include
secrets. `__str__`, when present, is the friendlier user-facing form; otherwise `str()` falls
back to `__repr__`.

### `__eq__` — value equality

```python
class Label:
    def __init__(self, value: str) -> None:
        self.value = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Label):
            return NotImplemented
        return self.value == other.value
```

Returning `NotImplemented` for an unsupported type lets Python try the reflected comparison
or conclude the values are unequal. It is different from raising `NotImplementedError`.
Remember P-2: `==` asks for value equality via this protocol; `is` asks whether two names
refer to the same object.

Defining equality affects hashing. Mutable value objects generally should not be dictionary
keys or set members because changing equality-relevant state would invalidate a hash table.
Frozen dataclasses provide a convenient value-object design.

### `__len__` and truthiness

```python
class Batch:
    def __init__(self, prompts: list[str]) -> None:
        self._prompts = prompts

    def __len__(self) -> int:
        return len(self._prompts)
```

Now `len(batch)` calls `batch.__len__()`. If no `__bool__` exists, a zero length also makes
the object falsy. Keep `__len__` cheap and return a non-negative integer; callers expect it
to describe a collection, not perform expensive work.

### `__getitem__` — indexing and slicing

```python
class Batch:
    def __init__(self, prompts: list[str]) -> None:
        self._prompts = prompts

    def __len__(self) -> int:
        return len(self._prompts)

    def __getitem__(self, index: int | slice) -> str | list[str]:
        return self._prompts[index]
```

`batch[0]` passes `0`; `batch[1:3]` passes a `slice` object. Delegating to a list preserves
its familiar `IndexError`, negative-index, and slice semantics. Python can also iterate an
object using successive integer `__getitem__` calls, although implementing `__iter__`
directly is clearer for a true iterable (covered in P-8).

Dunder methods are protocol hooks, not a menu to implement pre-emptively. Add one when the
corresponding operation is natural and unsurprising. Calling `obj.__len__()` directly or
inventing names like `__validate__` works against the protocol model; call `len(obj)` and use
an ordinary method such as `validate`.

---

## 3. Dataclasses — value-oriented classes without boilerplate

Most application classes primarily hold data. `@dataclass` generates methods such as
`__init__`, `__repr__`, and `__eq__` from annotated fields:

```python
from dataclasses import dataclass


@dataclass
class Usage:
    input_tokens: int
    output_tokens: int
    model: str = "sonnet"


usage = Usage(input_tokens=120, output_tokens=45)
print(usage)                            # Usage(input_tokens=120, ...)
```

Annotations identify dataclass fields; they do not enforce types at runtime. `Usage("many",
45)` still constructs unless application validation or another library rejects it. Pydantic,
covered in P-10, is the right tool when untrusted external data needs runtime validation.

Fields without defaults must precede fields with defaults, for the same reason function
parameters follow that ordering.

### Mutable defaults need `default_factory`

```python
from dataclasses import dataclass, field


@dataclass
class Evaluation:
    prompt: str
    tags: list[str] = field(default_factory=list)
```

`default_factory=list` calls `list()` for each new instance. `field(default=[])` would imply
shared mutable state and dataclasses reject common mutable defaults. Factories also support
non-container defaults that must be computed per instance.

### Derived state with `__post_init__`

```python
@dataclass
class Temperature:
    celsius: float

    def __post_init__(self) -> None:
        if self.celsius < -273.15:
            raise ValueError("temperature is below absolute zero")
```

The generated `__init__` calls `__post_init__` after assigning fields. Use it for small
invariants or derived attributes. If construction requires complex parsing, I/O, or many
conditional modes, prefer a named class method or separate factory.

### `frozen=True` — value-object intent

```python
@dataclass(frozen=True)
class ModelId:
    provider: str
    name: str
```

Assignment such as `model.name = "opus"` now raises `FrozenInstanceError`, equality is based
on field values, and instances are normally hashable when their fields are hashable. Frozen
is useful for configuration, identifiers, and dictionary keys.

It is shallow immutability: a frozen dataclass containing a list still contains a mutable
list. Prefer immutable field types such as tuples when the whole value must be stable.

Other useful options include `slots=True`, which prevents arbitrary new attributes and can
reduce memory for many instances, and `kw_only=True`, which makes generated constructor
parameters keyword-only. Use them when their constraint or benefit is real, not as ritual.

Not every class should be a dataclass. A service object whose identity and behaviour matter
more than its fields, or one maintaining a complex internal invariant, often deserves a
purpose-built class. "90%" is a direction toward less ceremony, not a literal quota.

---

## 4. Properties — attribute syntax with controlled behaviour

Python callers normally read attributes directly. A property preserves that natural syntax
when access later needs validation or computation:

```python
class SamplingConfig:
    def __init__(self, temperature: float = 0.0) -> None:
        self.temperature = temperature

    @property
    def temperature(self) -> float:
        return self._temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        if not 0.0 <= value <= 2.0:
            raise ValueError("temperature must be between 0 and 2")
        self._temperature = value
```

Callers still write `config.temperature`, not `config.get_temperature()`, and assignment
passes through the setter. A read-only computed property needs only the getter:

```python
@dataclass(frozen=True)
class TokenUsage:
    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens
```

Do not write trivial properties that merely return `_name`; a public `name` attribute is
simpler. Properties should also behave like attributes: fast, unsurprising, and free of
visible side effects. A network request, expensive computation, or state transition belongs
in an explicitly named method.

Changing a public attribute into a property is usually backward-compatible at the call site.
That freedom is why Python code does not add getters and setters "just in case."

---

## 5. Duck typing and protocols

Duck typing asks what an object can do, not what inheritance declaration it carries: if an
object supplies the operations a function uses, it is acceptable.

```python
def render_upper(source: object) -> str:
    return str(source).upper()
```

More realistically, many unrelated objects have a `.read()` method. Code can accept that
behaviour without forcing every implementation under one base class. Tests can then provide
a tiny fake with the same behaviour.

Dynamic duck typing is flexible, but a type checker needs a way to describe the expected
shape. `Protocol` provides structural typing:

```python
from typing import Protocol


class TextGenerator(Protocol):
    def generate(self, prompt: str, *, max_tokens: int) -> str:
        ...


class LocalGenerator:
    def generate(self, prompt: str, *, max_tokens: int) -> str:
        return prompt[:max_tokens]


def summarise(client: TextGenerator, document: str) -> str:
    return client.generate(
        f"Summarise: {document}",
        max_tokens=200,
    )


summarise(LocalGenerator(), "A long document")
```

`LocalGenerator` never inherits from `TextGenerator` or registers itself. It satisfies the
protocol because its method has the required compatible signature. This is static structural
typing: by default, `Protocol` does not add runtime enforcement.

Use `@runtime_checkable` only when an `isinstance` check is genuinely required, and remember
that runtime protocol checks mainly verify attribute presence, not full type signatures.

### Prefer small capabilities and composition

Inheritance is useful for a true subtype relationship and for frameworks designed around it,
but deep hierarchies couple subclasses to parent implementation details. Composition keeps
policies independent:

```python
from dataclasses import dataclass
from typing import Protocol


class Generator(Protocol):
    def generate(self, prompt: str) -> str:
        ...


class Recorder(Protocol):
    def record(self, prompt: str, response: str) -> None:
        ...


@dataclass
class Evaluator:
    generator: Generator
    recorder: Recorder

    def run(self, prompt: str) -> str:
        response = self.generator.generate(prompt)
        self.recorder.record(prompt, response)
        return response
```

`Evaluator` is assembled from two narrow capabilities. Either can be replaced independently,
including with an in-memory test double. Compare that with an `Evaluator` inheriting logging,
API transport, retry, and storage behaviour through multiple layers.

Abstract base classes (`abc.ABC`) remain appropriate when shared runtime behaviour or
nominal membership is important. A protocol is usually the lighter choice when consumers
only need a small interface. Start from the caller's required behaviour, not from a taxonomy
of every implementation.

---

## 6. Putting the pieces together

This example combines a frozen data value, a small protocol, composition, a property, and
natural dunder behaviour:

```python
from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class Request:
    prompt: str
    model: str = "sonnet"


@dataclass(frozen=True)
class Response:
    text: str
    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class Model(Protocol):
    def complete(self, request: Request) -> Response:
        ...


class FakeModel:
    def complete(self, request: Request) -> Response:
        text = f"Echo: {request.prompt}"
        return Response(text, len(request.prompt.split()), len(text.split()))


@dataclass
class Session:
    model: Model
    _responses: list[Response] = field(default_factory=list, repr=False)

    def submit(self, request: Request) -> Response:
        response = self.model.complete(request)
        self._responses.append(response)
        return response

    def __len__(self) -> int:
        return len(self._responses)

    def __getitem__(self, index: int | slice) -> Response | list[Response]:
        return self._responses[index]


session = Session(FakeModel())
response = session.submit(Request("Explain duck typing"))

print(response.total_tokens)
print(len(session))
print(session[0])
```

The data objects compare by value and cannot be casually rebound. `FakeModel` satisfies the
interface without inheritance. `Session` owns orchestration through composition, hides its
mutable list by convention, and implements only the collection operations callers naturally
need. None of this requires a framework or a hierarchy.

---

## Quick self-check (cold recall)

1. What is `self`, and why does `client.run()` not pass it explicitly? What is `__init__`
   responsible for?
2. Explain attribute lookup when both a class and one instance have an attribute named
   `provider`. Why is a mutable class attribute dangerous?
3. What promise does one leading underscore make? Why does double-underscore name mangling
   not provide privacy?
4. Which operations invoke `__repr__`, `__eq__`, `__len__`, and `__getitem__`? Why should an
   unsupported `__eq__` comparison return `NotImplemented`?
5. Which methods does a basic dataclass generate? Why must a list field use
   `field(default_factory=list)`?
6. What does `frozen=True` prevent, and why is that guarantee only shallow?
7. When is a property better than a public attribute? What kinds of work should not be hidden
   behind property access?
8. How can a class satisfy a `Protocol` without inheriting from it? Contrast a protocol with
   an abstract base class.
9. Why do small interfaces plus composition usually age better than a deep inheritance tree?

---

## Suggested 15-minute drill

Build a tiny in-memory prompt history:

1. Create frozen `Prompt` and `Reply` dataclasses; give `Reply` a computed `total_tokens`
   property.
2. Define a three-line `Generator` protocol and implement an `EchoGenerator` without
   inheriting from it.
3. Create a `Conversation` dataclass containing the generator and a private-by-convention
   reply list created with `default_factory`.
4. Implement `submit`, `__len__`, `__getitem__`, and a safe `__repr__` that never exposes a
   secret.
5. Prove that two equal frozen values compare equal and work as dictionary keys.
6. Create two conversations and prove their reply lists are not shared.

Run it, then explain which parts use convention, which are enforced at runtime, and which are
checked only by a static type checker. Mark P-5 complete in the fluency plan only after the
quiz and drill both pass.
