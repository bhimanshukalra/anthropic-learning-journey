# Python Working Fluency — Study Plan

**Goal:** Idiomatic, working Python fluency for AI engineering — the Phase 0 prerequisite of `../planning/AI-ENGINEER-ROADMAP.md`. Calibrated for an experienced software engineer: we skip programming fundamentals entirely and focus on (a) what's *different* about Python, (b) what's *idiomatic* (the fluency gap), and (c) what P1–P4 will actually use.

**Method:** tutor-then-quiz per batch (same format as `../certification/TOPIC-DEFINITIONS.md`). Ask to be taught a batch, get quizzed, tick it. Every batch ends with a tiny hands-on drill to run locally — fluency comes from fingers, not eyes.

**Done means (whole file):** you can write P1 without translating from another language in your head, and your code would pass an idiom-focused code review.

---

## Batch P-1 — Setup & Tooling *(get productive in one sitting)*

- [x] **uv + virtual environments** — why Python isolates deps per project; `uv init`, `uv add`, `uv run`; what `pyproject.toml` is
- [x] **Running code** — scripts vs. modules (`python file.py` vs `python -m pkg`), the REPL, `if __name__ == "__main__":` and why it exists
- [x] **Project layout** — the standard shape of a small Python project (src layout, tests/, pyproject.toml) so P1 looks professional from day one
- [x] **Ruff + formatting** — one linter/formatter, zero config debates
- [x] **How imports actually work** — modules, packages, `__init__.py`, absolute vs relative imports, the "why can't Python find my module" class of errors

## Batch P-2 — Core Language Differences *(where other-language habits break)*

- [ ] **Dynamic typing & everything-is-an-object** — variables are labels on objects, not boxes; `id()`, `is` vs `==`
- [ ] **Mutability & references** — lists/dicts are mutable and shared by reference; the classic aliasing bugs; `copy` vs `deepcopy`
- [ ] **The mutable default argument trap** — `def f(items=[])` and why it's the most famous Python gotcha
- [ ] **Truthiness & None** — what counts as falsy; `if not x:` idioms; `None` checks with `is`; Optional-shaped thinking
- [ ] **f-strings & string handling** — formatting, multiline, raw strings; strings are immutable

## Batch P-3 — Data Structures & Idioms *(the fluency core — the biggest batch on purpose)*

- [ ] **The big four** — list, tuple, dict, set: when each, performance characteristics, dict as Python's workhorse
- [ ] **Slicing** — `[start:stop:step]` on strings and lists, negative indices, `[::-1]`
- [ ] **Comprehensions** — list/dict/set comprehensions, conditions, nested; when a comprehension becomes unreadable and a loop is better
- [ ] **Iteration idioms** — `enumerate`, `zip`, unpacking (`a, b = pair`, star-unpacking), never `range(len(x))`
- [ ] **Sorting & key functions** — `sorted(items, key=...)`, `lambda` vs `operator.itemgetter`, reverse, stable sort
- [ ] **collections module** — `defaultdict`, `Counter`, `namedtuple`/`NamedTuple` — the three that pay rent

## Batch P-4 — Functions, Properly

- [ ] **Arguments in full** — positional/keyword, defaults, `*args`/`**kwargs`, keyword-only args (`*,`), unpacking calls with `*`/`**`
- [ ] **First-class functions & closures** — passing functions around, functions returning functions
- [ ] **Lambdas** — where they're idiomatic (keys, callbacks) and where they're not
- [ ] **Decorators** — what `@decorator` actually does (function wrapping), writing one, `functools.wraps`; reading them fluently (pytest, FastAPI, retry libraries all speak decorator)
- [ ] **Scope rules** — LEGB, why assignment inside a function creates a local, `global`/`nonlocal` (and why you rarely want them)

## Batch P-5 — OOP the Python Way *(different from Java/Kotlin/Swift OOP)*

- [ ] **Classes without ceremony** — `__init__`, `self`, class vs instance attributes, no private (the `_underscore` convention)
- [ ] **Dunder methods** — `__repr__`, `__eq__`, `__len__`, `__getitem__`: how Python's operators and builtins hook into your objects
- [ ] **@dataclass** — 90% of your classes should be this; fields, defaults, `frozen=True`
- [ ] **Properties** — `@property` instead of getters/setters
- [ ] **Duck typing & Protocols** — "if it quacks" as a design philosophy; `Protocol` for structural typing; why Python favours composition and small interfaces over inheritance trees

## Batch P-6 — Type Hints *(modern Python is typed Python)*

- [ ] **The core syntax** — annotating variables, params, returns; `list[str]`, `dict[str, int]`
- [ ] **Optional & unions** — `str | None`, why Optional is a contract not a suggestion
- [ ] **TypedDict, Literal, Enum** — typing dict-shaped data and closed choices (constant in LLM tool schemas)
- [ ] **Generics lite** — `TypeVar` reading fluency (you'll read more than write)
- [ ] **The checker** — running pyright/mypy; hints are not enforced at runtime (and what that means)

## Batch P-7 — Errors & Resources

- [ ] **Exception idioms** — try/except/else/finally, catching narrow, exception chaining (`raise ... from`), custom exceptions
- [ ] **EAFP vs LBYL** — "easier to ask forgiveness" as the Python default, vs look-before-you-leap
- [ ] **Context managers** — `with` for files/connections/locks; writing one via `@contextmanager`; why you never manually `close()`
- [ ] **Retry patterns** — backoff loops around flaky calls (direct P1/2.1 prep: rate limits, API errors)

## Batch P-8 — Iterators, Generators & Streaming *(direct bridge to LLM streaming)*

- [ ] **The iteration protocol** — what `for` actually does; iterables vs iterators; laziness
- [ ] **Generator functions** — `yield`, pausing/resuming, why generators are memory-cheap
- [ ] **Generator expressions** — `sum(x*x for x in xs)`; when vs list comprehension
- [ ] **itertools essentials** — `chain`, `islice`, `batched` — just enough
- [ ] **Streaming mindset** — processing chunk-by-chunk vs collect-then-process; exactly how you'll consume Claude's streaming API in 2.1

## Batch P-9 — Async Python *(the one genuinely new-shaped thing)*

- [ ] **The mental model** — event loop, cooperative multitasking; async ≠ threads ≠ processes; when async wins (I/O-bound: API calls) and when it's pointless (CPU-bound)
- [ ] **async/await syntax** — coroutines, `asyncio.run`, the "forgot to await" bug
- [ ] **Concurrency in practice** — `asyncio.gather` for parallel LLM calls, `TaskGroup`, timeouts (`asyncio.wait_for`)
- [ ] **Async iteration** — `async for`, async generators — how streaming responses arrive
- [ ] **The coloring problem** — sync and async don't mix freely; structuring a codebase around that

## Batch P-10 — Pydantic *(the AI engineer's power tool)*

- [ ] **BaseModel basics** — declare, validate, `.model_dump()`/`.model_dump_json()`; validation vs serialization directions
- [ ] **Field constraints & validators** — `Field(ge=0, ...)`, `@field_validator`, good error messages
- [ ] **Nested models & collections** — models in models, lists of models — the shape of every structured-output schema
- [ ] **Settings management** — `pydantic-settings` for env vars/API keys (how P1 will hold its config)
- [ ] **The LLM connection** — Pydantic model → JSON Schema → tool/structured-output definition; validate-and-retry on model output (the heart of P1)

## Batch P-11 — Testing with pytest

- [ ] **pytest basics** — plain `assert`, test discovery, file/function naming, running subsets
- [ ] **Fixtures** — dependency injection for tests; scope; `conftest.py`
- [ ] **Parametrize** — one test, many cases (this is how eval-ish thinking starts)
- [ ] **Mocking & monkeypatch** — faking the LLM API in tests: `monkeypatch`, `unittest.mock`, why you never hit the real API in unit tests
- [ ] **Testing async code** — `pytest-asyncio` in one bite

## Batch P-12 — Working with the Outside World

- [ ] **pathlib** — modern file paths; read/write text and bytes; globbing
- [ ] **JSON** — `json.loads`/`dumps`, its type limits, JSONL (the eval-dataset format)
- [ ] **httpx** — sync and async HTTP, timeouts, raising for status, streaming responses
- [ ] **Env vars & secrets** — `os.environ`, `.env` files, never committing keys
- [ ] **logging** — the stdlib logging module in its minimal useful form (levels, one formatter, why not `print`)

---

## Drills ledger *(one per batch, ~15 min each — filled in as we go)*

Each batch's quiz is followed by a micro-drill you run locally; ticking a batch requires the drill. Example shape: after P-3, "solve 3 Exercism exercises using only comprehensions and unpacking"; after P-10, "define a nested Pydantic model for a receipt and validate malformed JSON against it."

---

**Exit test (all batches done):** build a tiny end-to-end script — read a JSONL file, validate rows with Pydantic, call a mock async API concurrently with retry + timeout, stream results to disk, with 5 pytest tests — without opening a search engine for language syntax. That's "working fluency," and it's also ~40% of P1.
