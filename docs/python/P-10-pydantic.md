# Batch P-10 — Pydantic

> Reference notes for [`docs/PYTHON-FLUENCY.md`](../PYTHON-FLUENCY.md) · Batch P-10.
> Drill: pending — complete after the lesson and quiz.

*Type hints describe an intended shape to static tools. Pydantic turns those hints into a
runtime boundary: it parses untrusted input, validates constraints, reports structured errors,
serializes trusted models, and emits JSON Schema. Those are exactly the operations needed
between an application and an LLM's structured output.*

---

## 1. `BaseModel` basics

Declare a model by subclassing `BaseModel` and annotating its fields:

```python
from pydantic import BaseModel


class Usage(BaseModel):
    input_tokens: int
    output_tokens: int
    cached_tokens: int = 0


usage = Usage(input_tokens=120, output_tokens=45)

usage.input_tokens                  # 120
usage.cached_tokens                 # 0
```

Pydantic reads the annotations at runtime. Required fields have no default; `cached_tokens`
is optional to supply because it has a default, though its value is never `None`.

By default, Pydantic performs useful coercion where it can:

```python
usage = Usage(input_tokens="120", output_tokens=45)
usage.input_tokens                  # 120, an int
```

That is **parsing**, not merely checking. It is convenient at JSON, CLI, and environment
boundaries, but coercion can conceal a producer bug. Enable strictness where the distinction
matters:

```python
from pydantic import BaseModel, ConfigDict


class StrictUsage(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    input_tokens: int
    output_tokens: int
```

Now the string `"120"` is rejected, and `extra="forbid"` rejects unknown input keys. The
defaults are more permissive: extra keys are ignored. At contracts such as LLM outputs,
forbidding extras often exposes schema drift instead of silently discarding it.

### The validation direction

Use `model_validate` for Python objects and `model_validate_json` for JSON text or bytes:

```python
raw = {"input_tokens": 120, "output_tokens": 45}
usage = Usage.model_validate(raw)

payload = '{"input_tokens": 120, "output_tokens": 45}'
usage_from_json = Usage.model_validate_json(payload)
```

Think of these as moving **untrusted input → validated model**. Constructing with
`Usage(...)` also validates, but the explicit methods make a boundary's direction obvious.

Do not use `model_construct()` for normal parsing. It creates a model without validation and
exists for narrow trusted-data or advanced performance cases. Measure before assuming it is
needed.

### The serialization direction

Move **model → plain representation** with the v2 serialization methods:

```python
usage.model_dump()
# {'input_tokens': 120, 'output_tokens': 45, 'cached_tokens': 0}

usage.model_dump(exclude_defaults=True)
# {'input_tokens': 120, 'output_tokens': 45}

usage.model_dump_json()
# JSON text
```

`model_dump()` defaults to Python-mode values. `model_dump(mode="json")` produces only
JSON-compatible representations for supported types—for example, turning a `datetime` into a
string—while still returning a Python dict. `model_dump_json()` encodes directly to JSON text.

Pydantic v1 names such as `.dict()`, `.json()`, `parse_obj`, and `parse_raw` are legacy APIs.
In new v2 code, use `model_dump`, `model_dump_json`, `model_validate`, and
`model_validate_json`.

---

## 2. Field constraints and validators

Types provide broad categories; `Field` captures domain constraints and schema metadata:

```python
from typing import Annotated

from pydantic import BaseModel, Field

Probability = Annotated[float, Field(ge=0.0, le=1.0)]


class Evaluation(BaseModel):
    label: str = Field(min_length=1, max_length=80)
    confidence: Probability
    notes: str = Field(default="", max_length=500)
```

`ge` and `le` mean greater-than-or-equal and less-than-or-equal. Other useful constraints
include `gt`, `lt`, `min_length`, `max_length`, `pattern`, and collection length constraints.
The `Annotated` form makes a reusable constrained type without hiding its base type.

`Field` also controls aliases, descriptions, examples, exclusion, and serialization details.
Descriptions flow into generated JSON Schema, so write them as instructions a schema consumer
can act on:

```python
class SearchQuery(BaseModel):
    query: str = Field(
        min_length=1,
        description="A concise search query without explanatory prose.",
    )
```

### Field validators

Use `@field_validator` for a rule that cannot be expressed clearly as a built-in constraint:

```python
from pydantic import BaseModel, field_validator


class TagSet(BaseModel):
    tags: list[str]

    @field_validator("tags")
    @classmethod
    def normalise_tags(cls, value: list[str]) -> list[str]:
        cleaned = [tag.strip().lower() for tag in value if tag.strip()]
        if len(cleaned) != len(set(cleaned)):
            raise ValueError("tags must be unique after normalisation")
        return cleaned
```

The default validator mode is `"after"`: Pydantic first parses the annotated type, then the
validator receives a `list[str]`. Returning the value is mandatory; a validator transforms as
well as checks. Raise `ValueError` for a domain failure and make the message explain the
invariant, not the implementation.

A `mode="before"` validator receives raw input and is useful for carefully controlled
normalisation before type parsing. It also receives more possible shapes, so it is easier to
make unsafe assumptions. Prefer built-in parsing or an after validator when possible.

Validators should be deterministic and local to validation. Network calls, database writes,
and other side effects make model construction surprising, slow, and hard to test. Perform
those operations in an application service after validation.

### Reading validation errors

Invalid input raises `ValidationError`, whose entries include a location, error type, message,
and offending input:

```python
from pydantic import ValidationError

try:
    Evaluation(label="", confidence=1.5)
except ValidationError as error:
    for issue in error.errors():
        print(issue["loc"], issue["msg"], issue["type"])
```

Do not flatten every failure into "invalid response." Field locations such as
`('items', 2, 'confidence')` are valuable when diagnosing nested LLM output or producing a
targeted retry prompt. Avoid returning raw errors to untrusted clients without considering
whether their `input` values reveal sensitive data.

---

## 3. Nested models and collections

Model fields may contain other models and typed collections:

```python
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1)
    quote: str = Field(min_length=1, max_length=300)


class Claim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    verdict: Literal["supported", "unsupported", "uncertain"]
    citations: list[Citation] = Field(default_factory=list)


class Analysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str
    claims: list[Claim] = Field(min_length=1, max_length=20)
```

Pydantic recursively turns citation dictionaries into `Citation` instances and reports paths
through lists and models when something fails. This mirrors structured-output schemas: one
top-level object, nested records, arrays, and closed choices.

Use `default_factory=list`, not `[]`, to communicate that every model receives a new list.
Pydantic handles unhashable mutable defaults safely, but the factory remains explicit and
portable Python design.

### Models do not make mutable data immutable

Models and their collection fields are mutable by default:

```python
analysis.summary = "Revised"
analysis.claims.append(new_claim)
```

For value objects, configure `frozen=True`:

```python
class Citation(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    source_id: str
    quote: str
```

Freezing prevents field assignment but does not recursively freeze mutable objects nested
inside a model. Choose immutable field types too when deep immutability is required.

Keep models aligned with meaningful domain boundaries. One enormous model is hard for humans,
validators, and LLMs to satisfy. Conversely, wrapping every primitive in a model adds ceremony
without improving the contract.

---

## 4. Settings management

Pydantic v2 moved settings into the separate `pydantic-settings` package. Declare application
configuration with `BaseSettings`:

```python
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        extra="ignore",
    )

    anthropic_api_key: SecretStr
    model: str = "claude-sonnet"
    timeout_seconds: float = Field(default=30.0, gt=0)


settings = Settings()
```

With the prefix, fields read variables such as `APP_ANTHROPIC_API_KEY` and `APP_MODEL`.
Environment strings are parsed into their declared types. A `.env` file is a local convenience;
do not commit real secrets, and do not treat it as a production secret manager.

`SecretStr` masks its value in representations and logs:

```python
print(settings.anthropic_api_key)                    # **********
api_key = settings.anthropic_api_key.get_secret_value()
```

Masking reduces accidental disclosure; it does not encrypt the secret or stop deliberately
accessing it. Keep `get_secret_value()` close to the API client construction and never print
the result.

Instantiate settings once near the application's composition root and pass them to code that
needs them. Constructing settings at import time can make tests dependent on the developer's
environment and can cause imports to fail before a test can override configuration.

Source precedence and case sensitivity are configurable. Know which sources your project
enables—constructor arguments, environment, dotenv files, and secrets directories can provide
the same field. Hidden precedence bugs are especially confusing during deployment.

---

## 5. The LLM connection: model → schema → validated output

Pydantic generates JSON Schema from the same model used for validation:

```python
schema = Analysis.model_json_schema()
```

That schema can become a tool input or structured-output definition. The precise wrapper
differs across LLM providers and SDK versions, but the architecture is stable:

```text
Pydantic model
    → model_json_schema()
    → provider's tool / structured-output request
    → JSON-like model response
    → model_validate() or model_validate_json()
    → trusted application value
```

Generating a schema does not guarantee the remote model will obey it. Some provider features
constrain output strongly; others merely prompt the model. Your application should validate
the received value regardless.

### Validate and retry deliberately

A bounded retry can return validation feedback to the model:

```python
from collections.abc import Callable
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

ModelT = TypeVar("ModelT", bound=BaseModel)


def generate_validated(
    model_type: type[ModelT],
    call_llm: Callable[[dict[str, Any], str | None], str],
    *,
    attempts: int = 3,
) -> ModelT:
    feedback: str | None = None

    for attempt in range(1, attempts + 1):
        raw_json = call_llm(model_type.model_json_schema(), feedback)
        try:
            return model_type.model_validate_json(raw_json)
        except ValidationError as error:
            if attempt == attempts:
                raise
            feedback = error.json(include_input=False)

    raise AssertionError("loop always returns or raises")
```

The type variable preserves the relationship between the model class passed in and the model
instance returned. `include_input=False` avoids echoing potentially sensitive invalid content
into feedback, though an application must apply its own security policy.

Retries need a hard limit. They cost time and tokens, and repeated structural failure may mean
the schema is too complex, the model lacks capability, or the integration is wrong. Retry only
repairable validation errors; authentication, rate-limit, transport, and refusal handling are
separate policies.

Schema validation proves shape and declared constraints—not truth. A perfectly valid citation
may refer to a nonexistent source, and a confidence of `0.9` may be unjustified. Semantic
verification belongs in later application logic.

---

## 6. Putting the pieces together

This provider-neutral example defines an LLM fact-check result, generates its schema, validates
a response, and exposes useful feedback for a bounded retry:

```python
from collections.abc import Callable
from typing import Annotated, Any, Literal, TypeVar

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
)

Confidence = Annotated[float, Field(ge=0.0, le=1.0)]


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1)
    excerpt: str = Field(min_length=1, max_length=300)

    @field_validator("excerpt")
    @classmethod
    def collapse_whitespace(cls, value: str) -> str:
        return " ".join(value.split())


class Finding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim: str = Field(min_length=1)
    verdict: Literal["supported", "unsupported", "uncertain"]
    confidence: Confidence
    evidence: list[Evidence] = Field(default_factory=list, max_length=5)


class FactCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1, max_length=500)
    findings: list[Finding] = Field(min_length=1, max_length=20)


ResultT = TypeVar("ResultT", bound=BaseModel)


def request_structured(
    result_type: type[ResultT],
    generate: Callable[[dict[str, Any], str | None], str],
    *,
    max_attempts: int = 3,
) -> ResultT:
    feedback: str | None = None

    for attempt in range(max_attempts):
        raw = generate(result_type.model_json_schema(), feedback)
        try:
            return result_type.model_validate_json(raw)
        except ValidationError as error:
            if attempt + 1 == max_attempts:
                raise
            feedback = error.json(include_input=False)

    raise AssertionError("unreachable")


def fake_provider(schema: dict[str, Any], feedback: str | None) -> str:
    # A real adapter would place `schema` in the provider's structured-output API.
    return """{
      "summary": "One claim was checked.",
      "findings": [{
        "claim": "The service is available.",
        "verdict": "uncertain",
        "confidence": 0.55,
        "evidence": []
      }]
    }"""


result = request_structured(FactCheck, fake_provider)
payload = result.model_dump(mode="json")
```

One declaration now drives the schema sent outward, validation on the way inward, editor
types inside the application, and JSON-safe serialization afterward. The provider adapter is
kept separate because provider APIs change; the domain contract and retry policy remain
testable without a network call.

---

## Quick self-check (cold recall)

1. What is the difference between `model_validate`, `model_validate_json`, `model_dump`, and
   `model_dump_json`? State the direction of data flow for each.
2. Does `value: int` make Pydantic strict by default? When would coercion help or hurt?
3. Why might an external contract use `ConfigDict(extra="forbid")`?
4. When should a constraint live in `Field`, and when does it need a `field_validator`?
5. What does an after field validator receive, and what must it return?
6. How does Pydantic report a failure in the third item of a nested list?
7. Why use `default_factory=list`? Does a frozen model guarantee deep immutability?
8. Where does `BaseSettings` come from in Pydantic v2, and what protection does `SecretStr`
   provide—and not provide?
9. How does one Pydantic model support both an LLM schema and response validation?
10. Why are validation retries bounded, and what correctness properties remain unproven after
    a response validates?

---

## Suggested 15-minute drill

Build a provider-neutral structured-output boundary:

1. Define nested `Evidence`, `Finding`, and `FactCheck` models with forbidden extra fields.
2. Add numeric, string, and collection constraints with `Field`.
3. Add one after `field_validator` that normalises input and raises a useful `ValueError`.
4. Print `FactCheck.model_json_schema()` and identify where each constraint appears.
5. Validate one Python dict and one JSON string; serialize the results with both dump methods.
6. Feed three invalid responses—an extra key, a confidence above one, and a missing nested
   field—and predict each error location before running the code.
7. Implement a three-attempt validate-and-retry loop using a fake provider callback.
8. Define a `BaseSettings` model with one `SecretStr`, one default, and an environment prefix;
   verify that printing the secret does not reveal it.

Explain where parsing, validation, serialization, and schema generation happen. Mark P-10
complete in the fluency plan only after the quiz and drill both pass.
