# Batch P-2 — Core Language Differences

> Reference notes for [`docs/PYTHON-FLUENCY.md`](../PYTHON-FLUENCY.md) · Batch P-2 (completed 2026-07-14).
> Drill: waived — 7/7 quiz covered identity, references, copying, mutable defaults, truthiness, and strings.

*This batch is where habits from Java/Kotlin/Swift silently break. Every topic here is a
class of real bug, not trivia.*

---

## 1. Dynamic typing — variables are labels, not boxes

In Java/Kotlin, a variable is a typed slot that holds a value (or a reference the compiler
tracks). In Python, **a variable is just a name bound to an object** — the name has no type,
only the object does:

```python
x = 42          # the name x is bound to an int object
x = "hello"     # rebind the SAME name to a str object — legal, no cast, no error
```

Everything is an object — ints, functions, classes, modules — and every object has an
identity (`id(obj)`, roughly its address), a type (`type(obj)`), and a value.

**`is` vs `==` — identity vs equality:**

```python
a = [1, 2, 3]
b = [1, 2, 3]
a == b    # True  — same VALUE (calls __eq__)
a is b    # False — different objects
c = a
c is a    # True  — same object, two labels
```

- Use `==` for value comparison — nearly always what you mean.
- Use `is` only for singletons: `is None`, `is True`, `is False`.
- Trap: small ints and short strings are *interned* (cached), so `x is y` can be `True` for
  `256` and `False` for `257`. Never use `is` for numbers/strings — the result is an
  implementation detail.

---

## 2. Mutability & references — the aliasing bugs

Assignment **never copies**. It binds another name to the same object. For mutable objects
(list, dict, set), mutation through one name is visible through all of them:

```python
team = ["ana", "raj"]
backup = team            # NOT a copy — an alias
team.append("li")
backup                   # ['ana', 'raj', 'li']  ← "backup" changed too
```

Same rule at function boundaries — arguments are passed by object reference, so a function
that mutates its parameter mutates the caller's data:

```python
def add_default(tags: list[str]) -> list[str]:
    tags.append("untagged")     # mutates the CALLER's list
    return tags
```

**Immutable types** (int, float, str, tuple, frozenset, bool) are safe to share — any
"change" produces a new object. Mutable types (list, dict, set, most custom classes) are
where aliasing bites.

**Copying, when you actually need it:**

```python
shallow = original.copy()        # or list(original), dict(original), original[:]
import copy
deep = copy.deepcopy(original)   # recursively copies nested structures
```

Shallow copy duplicates the outer container only — nested lists/dicts are still shared.
`deepcopy` severs everything. Reach for `deepcopy` rarely; needing it often signals the data
should be restructured or immutable.

---

## 3. The mutable default argument trap

The most famous Python gotcha. **Default values are evaluated once, at function definition —
not per call.** A mutable default is therefore *shared across every call*:

```python
def add_item(item: str, items: list[str] = []) -> list[str]:   # BUG
    items.append(item)
    return items

add_item("a")   # ['a']
add_item("b")   # ['a', 'b']  ← the SAME list, still growing
```

The idiom that fixes it — default to `None`, create inside:

```python
def add_item(item: str, items: list[str] | None = None) -> list[str]:
    if items is None:
        items = []
    items.append(item)
    return items
```

Same trap applies to `= {}`, `= set()`, and any mutable object (including
`= datetime.now()` — evaluated once at import, not per call). Ruff's bugbear rules (`B006`,
`B008`) catch these — another reason the `"B"` select from Batch P-1 is on.

---

## 4. Truthiness & None

Python conditions accept any object; these are **falsy**, everything else is truthy:

`False` · `None` · `0` / `0.0` · `""` · `[]` · `{}` · `()` · `set()` — i.e. zero, empty, or nothing.

Idiomatic checks lean on this:

```python
if not results:          # empty OR None — idiomatic for "nothing to do"
if results:              # "we have at least one"
```

**The distinction that matters:** `if not x:` treats `None`, `0`, and `""` identically. When
the difference is meaningful — "value absent" vs "value is legitimately zero/empty" — check
identity explicitly:

```python
if x is None:            # ONLY absent — 0 and "" pass through
```

Classic bug: `if not count:` treating a real count of `0` as "missing". API-response code
hits this constantly.

**Optional-shaped thinking:** Python's `None` plays Kotlin's `null`, but the compiler won't
force handling — type hints do. `def find_user(...) -> User | None:` is the Python spelling
of `User?`, and the type checker (Batch P-6) flags unguarded use of the result. The
`is None` / `is not None` guard is the Python equivalent of a Kotlin null check — there's no
`?.` operator; be explicit.

---

## 5. f-strings & string handling

**f-strings are the only formatting style worth using** (`%` and `.format()` are legacy):

```python
name, score = "Bhimanshu", 781
f"{name} scored {score}"            # interpolation
f"{score / 1000:.1%}"               # format spec → '78.1%'
f"{score=}"                         # debug shorthand → 'score=781'
f"{big_number:,}"                   # thousands separator → '1,000,000'
```

**Multiline & raw strings:**

```python
prompt = """You are a helpful assistant.
Answer in one sentence."""           # triple quotes — newlines preserved

pattern = r"\d+\.\d+"                # raw string — backslashes literal (regex, Windows paths)
```

**Strings are immutable.** Every "modification" returns a new string — methods like
`.upper()`, `.strip()`, `.replace()` never change the original:

```python
s = "hello"
s.upper()        # returns 'HELLO'; s is still 'hello'
s = s.upper()    # rebind to keep it
```

Consequence: building a string in a loop with `+=` creates a new object every iteration —
collect parts in a list and `"".join(parts)`, the standard idiom.

---

## Quick self-check (cold recall)

1. Why can `x is y` be `True` for two `256`s but `False` for two `257`s, and what rule does
   that imply about using `is`?
2. A function appends to its list parameter and the caller's data changes — what's the
   mechanism, and two ways to prevent it?
3. Explain *when* default argument values are evaluated, and derive the `None` idiom from it.
4. When is `if not x:` a bug where `if x is None:` is correct? Give a concrete example.
5. Why is `+=` string-building in a loop quadratic, and what's the idiomatic fix?
