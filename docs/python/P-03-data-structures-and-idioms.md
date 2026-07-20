# Batch P-3 — Data Structures & Idioms

> Reference notes for [`docs/PYTHON-FLUENCY.md`](../PYTHON-FLUENCY.md) · Batch P-3.
> Drill: pending — complete after the lesson and quiz.

*Python code becomes fluent when the shape of the data drives the choice of container and
the loop says what it means. This batch replaces index-heavy, ceremony-heavy code with the
small vocabulary Python programmers use every day.*

---

## 1. The big four — list, tuple, dict, set

All four containers can hold mixed types at runtime, though production code normally keeps a
consistent shape and documents it with type hints.

| Type | Meaning | Ordered? | Mutable? | Typical lookup |
|---|---|---:|---:|---:|
| `list[T]` | Ordered sequence that may change | Yes | Yes | Index: O(1), value: O(n) |
| `tuple[...]` | Fixed record or immutable sequence | Yes | No | Index: O(1), value: O(n) |
| `dict[K, V]` | Key → value mapping | In insertion order | Yes | Key: O(1) average |
| `set[T]` | Unique values / membership index | No useful order | Yes | Member: O(1) average |

Big-O describes normal CPython behaviour, not a hard real-time guarantee. Dict and set
operations can degrade under pathological hash collisions; that rarely changes application
design.

### Lists — the default sequence

```python
models = ["haiku", "sonnet"]
models.append("opus")                 # mutate in place
first = models[0]                      # O(1)
has_opus = "opus" in models            # O(n)
last = models.pop()                    # remove and return the end, O(1) amortized
```

Use a list when order matters, duplicates are valid, or items will be added/removed. Appending
and popping at the end are cheap; inserting/removing at the front shifts every later element
and is O(n). For a real queue, use `collections.deque`, not `list.pop(0)`.

### Tuples — fixed shape, not merely "an immutable list"

```python
point = (12.5, 7.0)
x, y = point

def dimensions() -> tuple[int, int]:
    return 1920, 1080                  # parentheses are optional when packing
```

Use tuples for a small, fixed-position record or a return value with a stable arity. Prefer a
`NamedTuple` or dataclass once positions become hard to remember. A one-item tuple needs a
comma: `(42,)`; `(42)` is just an `int` in parentheses.

"Immutable tuple" means its slots cannot be rebound. A tuple may still contain mutable
objects, and those objects may change:

```python
record = ("job-1", ["queued"])
record[1].append("running")            # legal: the tuple is unchanged; its list mutated
```

### Dicts — Python's workhorse

```python
usage = {"input_tokens": 120, "output_tokens": 45}
usage["cached_tokens"] = 20

input_tokens = usage["input_tokens"]  # KeyError if the key is absent
cache_hits = usage.get("cache_hits", 0)

for name, count in usage.items():
    print(name, count)
```

Use `mapping[key]` when absence is an error; use `mapping.get(key, default)` when absence is
expected. Avoid `if key in d: value = d[key]` when a single `get` or `try/except KeyError`
states the policy more clearly.

Dict iteration is over **keys** by default. Use `.keys()` when explicitness helps, `.values()`
for values, and `.items()` for key/value pairs. Since Python 3.7, insertion order is a language
guarantee, but a dict still communicates *mapping*, not sorted collection.

Merging creates a new dict; update mutates the left one:

```python
defaults = {"timeout": 30, "retries": 2}
overrides = {"timeout": 60}
config = defaults | overrides           # right-hand value wins; defaults unchanged
defaults.update(overrides)              # defaults is mutated
```

### Sets — uniqueness and fast membership

```python
requested = {"read", "write"}
allowed = {"read", "list"}

requested & allowed                    # intersection: {'read'}
requested | allowed                    # union
requested - allowed                    # difference: {'write'}
requested <= allowed                   # subset test
```

Use a set for deduplication, membership checks, and set algebra. Elements must be hashable, so
strings, numbers, and suitable tuples work; lists and dicts do not. `{}` is an empty **dict**;
the empty set is `set()`.

Converting a list with `list(set(items))` removes duplicates but loses useful ordering. To
deduplicate while preserving first appearance:

```python
unique_in_order = list(dict.fromkeys(items))
```

---

## 2. Slicing — selecting a range without index bookkeeping

The general form is `sequence[start:stop:step]`: start is inclusive, stop is exclusive, and
each part is optional.

```python
values = [0, 1, 2, 3, 4, 5]

values[1:4]       # [1, 2, 3]
values[:3]        # [0, 1, 2]
values[3:]        # [3, 4, 5]
values[-1]        # 5 — last item
values[-3:]       # [3, 4, 5]
values[::2]       # [0, 2, 4]
values[::-1]      # [5, 4, 3, 2, 1, 0]
```

The same syntax works for strings, tuples, and other sequence types. Slicing built-in
sequences creates a **shallow copy**; it is O(k) in the slice length. `items[:]` therefore
copies the outer list but still shares nested objects (the P-2 rule).

Slice assignment mutates a list and may even change its length:

```python
values[1:3] = [10, 20, 30]
```

Negative-step slices are easiest to reason about as "walk backwards." With an explicit
negative step, defaults also reverse direction; dense expressions such as `xs[8:1:-2]` are
valid but often clearer as named intermediate data or a loop.

Do not use `[::-1]` when all you need is reverse iteration: `reversed(items)` is lazy and
doesn't copy the sequence.

---

## 3. Comprehensions — build a collection from an iterable

A comprehension expresses **mapping**, optionally followed by **filtering**:

```python
prices = [10, 25, 40]
with_tax = [price * 1.18 for price in prices]
large_with_tax = [price * 1.18 for price in prices if price >= 25]

length_by_name = {name: len(name) for name in ["haiku", "sonnet"]}
initials = {name[0] for name in ["haiku", "sonnet", "opus"]}
```

Read the list form as: "`price * 1.18` for every `price` in `prices`, if the condition holds."
The output expression comes first because it is the main result.

### Nested comprehensions

The `for` clauses have the same order as equivalent nested loops:

```python
pairs = [(x, y) for x in range(3) for y in range(2)]

# Equivalent:
pairs = []
for x in range(3):
    for y in range(2):
        pairs.append((x, y))
```

This is fine for a simple Cartesian product or flattening one level:

```python
flat = [item for group in groups for item in group]
```

Once there are multiple transformations, multiple conditions, side effects, or a reader must
decode the expression, use an ordinary loop. Comprehensions are for constructing values, not
for doing work:

```python
# Don't: creates a throwaway list solely for side effects.
[send(item) for item in items]

# Do:
for item in items:
    send(item)
```

Parentheses produce a **generator expression**, not a tuple comprehension:

```python
total = sum(price * 1.18 for price in prices)  # lazy; no intermediate list
```

Generators are covered fully in P-8. For now, prefer one when immediately feeding a single
consumer such as `sum`, `any`, `all`, `min`, or `max`.

---

## 4. Iteration and unpacking idioms

Python loops iterate over values directly. Reach for indices only when the index is genuinely
part of the problem.

```python
# Values only
for model in models:
    print(model)

# Position and value
for position, model in enumerate(models, start=1):
    print(position, model)

# Corresponding values from multiple iterables
for prompt, response in zip(prompts, responses, strict=True):
    evaluate(prompt, response)
```

`range(len(items))` is usually a translation smell. Use `enumerate(items)` when you need the
position. Use `zip` for parallel iteration. Plain `zip` stops at the shortest iterable,
potentially hiding missing data; `strict=True` raises `ValueError` when lengths differ and is
the safer choice when equal length is an invariant.

### Packing and unpacking

```python
name, score = ("sonnet", 0.94)
first, *middle, last = [1, 2, 3, 4, 5]

head = [1, 2]
tail = [3, 4]
all_items = [*head, *tail]

base = {"timeout": 30, "retries": 2}
config = {**base, "timeout": 60}       # later key wins
```

Unpacking makes the expected shape executable: `a, b = pair` raises `ValueError` unless there
are exactly two values. A starred target collects the remainder into a list. `_` conventionally
means "intentionally unused":

```python
job_id, _, status = row
```

Swapping needs no temporary variable because the right side is packed before the left side is
assigned:

```python
left, right = right, left
```

Unpacking in a call is related but distinct: `f(*args)` supplies positional arguments and
`f(**kwargs)` supplies keyword arguments. P-4 covers the function side in detail.

---

## 5. Sorting and key functions

`sorted(iterable)` returns a **new list** and accepts any iterable. `list.sort()` mutates a
list in place and returns `None`.

```python
scores = [0.72, 0.95, 0.81]
descending = sorted(scores, reverse=True)

records = [
    {"name": "opus", "latency_ms": 430},
    {"name": "haiku", "latency_ms": 120},
]
by_latency = sorted(records, key=lambda row: row["latency_ms"])
```

The `key` function is called once per item to compute its comparison value. Use a small lambda
when the extraction/transformation is local and obvious. For direct field access,
`operator.itemgetter` and `operator.attrgetter` are concise, reusable alternatives:

```python
from operator import attrgetter, itemgetter

by_name = sorted(records, key=itemgetter("name"))
by_created_at = sorted(jobs, key=attrgetter("created_at"))
```

For multiple criteria, return a tuple; tuple comparison proceeds left to right:

```python
ranked = sorted(records, key=lambda row: (-row["score"], row["name"]))
```

Here score is descending (negated) and name ascending. Avoid clever negation for non-numeric
values; use stable sorting instead.

Python's sort is **stable**: equal keys retain their original relative order. That permits
multi-pass sorting from the least important key to the most important:

```python
records.sort(key=itemgetter("name"))                 # secondary
records.sort(key=itemgetter("score"), reverse=True)  # primary
```

Never write `result = items.sort()` — `result` becomes `None`. Methods that mutate containers
usually return `None` precisely so mutation is visible in the code.

---

## 6. `collections` — specialised containers that pay rent

### `defaultdict` — construct missing values automatically

```python
from collections import defaultdict

scores_by_model: defaultdict[str, list[float]] = defaultdict(list)
for model, score in evaluations:
    scores_by_model[model].append(score)
```

On a missing key, `defaultdict` calls its factory (`list` here), stores the result, and returns
it. This replaces repeated `if key not in d` setup. Reading a missing key also inserts it, so
use a normal dict with `.get()` if lookup must not mutate state.

### `Counter` — a frequency map

```python
from collections import Counter

statuses = Counter(["ok", "error", "ok", "timeout", "ok"])
statuses["ok"]                    # 3
statuses["missing"]               # 0, not KeyError
statuses.most_common(2)            # [('ok', 3), ('error', 1)]
```

Counters support addition, subtraction, intersection, and union of counts. They are clearer
than hand-building `dict[T, int]` when the domain is explicitly frequencies or multisets.

### `namedtuple` and `NamedTuple` — lightweight immutable records

The older factory is useful to recognise in existing code:

```python
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
point = Point(3, 4)
```

For new typed code, prefer `typing.NamedTuple`:

```python
from typing import NamedTuple

class Usage(NamedTuple):
    input_tokens: int
    output_tokens: int

usage = Usage(input_tokens=120, output_tokens=45)
usage.input_tokens                         # named access
input_tokens, output_tokens = usage        # still tuple-compatible
```

Choose `NamedTuple` when tuple behaviour and immutability are useful—for example a small
internal return record. Choose a dataclass (P-5) for a domain object that may evolve, needs
methods/default factories, or should not expose positional tuple semantics.

Other useful `collections` types exist—especially `deque` for queues—but learn them when a
problem calls for them rather than memorising the module.

---

## 7. Putting the idioms together

Given model-evaluation rows, select passing models and rank them by score descending, then
latency ascending:

```python
from collections import Counter

rows = [
    {"model": "haiku", "score": 0.88, "latency_ms": 140, "status": "ok"},
    {"model": "sonnet", "score": 0.94, "latency_ms": 410, "status": "ok"},
    {"model": "opus", "score": 0.94, "latency_ms": 760, "status": "error"},
]

status_counts = Counter(row["status"] for row in rows)
passing = [row for row in rows if row["status"] == "ok" and row["score"] >= 0.8]
ranked = sorted(passing, key=lambda row: (-row["score"], row["latency_ms"]))

for rank, row in enumerate(ranked, start=1):
    print(f"{rank}. {row['model']}: {row['score']:.0%}")
```

Each construct has one job: `Counter` counts, the comprehension selects, `sorted` ranks, and
`enumerate` supplies display positions. That separation is more Pythonic—and easier to test—
than one large loop accumulating and mutating several pieces of state.

---

## Quick self-check (cold recall)

1. Choose among list, tuple, dict, and set for: an ordered event stream, an `(x, y)` return
   value, user lookup by ID, and checking whether a permission is allowed. Explain why.
2. What does `items[1:-1:2]` mean? Does slicing a list deep-copy nested values?
3. Rewrite an index loop using `enumerate`, and explain when `zip(..., strict=True)` is safer
   than plain `zip`.
4. When is a comprehension clearer than a loop, and what two signals mean it should become a
   loop?
5. Contrast `sorted(items)` with `items.sort()`. What does sort stability buy you?
6. When would you choose `defaultdict(list)`, `Counter`, and `NamedTuple` respectively—and
   what surprising mutation can `defaultdict` cause?

---

## Suggested 15-minute drill

Create a list of 10 evaluation dictionaries with `model`, `status`, `score`, and `latency_ms`,
then, without explicit indexing:

1. Count statuses with `Counter`.
2. Group scores by model with `defaultdict(list)`.
3. Select successful rows using one readable comprehension.
4. Rank them by score descending and latency ascending.
5. Print numbered results using `enumerate(start=1)`.
6. Zip the ranked models with a same-length list of reviewer names using `strict=True`.

Run it, deliberately shorten the reviewer list to observe the strict-zip failure, then restore
it. Mark P-3 complete in the fluency plan only after the quiz and this drill both pass.
