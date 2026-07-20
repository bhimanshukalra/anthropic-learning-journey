# Batch P-1 — Setup & Tooling

> Reference notes for [`docs/PYTHON-FLUENCY.md`](../PYTHON-FLUENCY.md) · Batch P-1 (completed 2026-07-13).
> Drill: scaffolded Portfolio Project P1 as a standalone uv project (src layout, tests, Ruff, locked deps).

---

## 1. uv + virtual environments

**Why Python isolates deps per project.** Python installs packages into a single
`site-packages` directory per interpreter — there is no per-project resolution built into the
language (unlike Gradle/Maven/SPM, where the build tool resolves per project by design). Two
projects needing different versions of the same library would collide in a shared interpreter.
A **virtual environment** (venv) fixes this: a lightweight copy of the interpreter with its own
`site-packages`, one per project.

**uv** is the modern tool that manages all of it — venv creation, dependency resolution,
lockfiles, and Python versions — replacing the old `pip` + `venv` + `pip-tools` stack, and fast
enough that you never think about it.

| Command | What it does |
|---|---|
| `uv init` | Scaffold a project: `pyproject.toml`, `.python-version`, sample module |
| `uv add httpx` | Add a dependency: updates `pyproject.toml`, resolves, writes `uv.lock`, installs into `.venv` |
| `uv add --dev pytest` | Add a dev-only dependency (test/lint tools — not shipped) |
| `uv run python main.py` | Run inside the project's venv — no manual activation needed |
| `uv run pytest` | Same for any installed tool |
| `uv sync` | Recreate `.venv` exactly from `uv.lock` (what a fresh clone runs) |

**`pyproject.toml`** is the single project manifest (think `build.gradle.kts` /
`Package.swift`): name, version, Python requirement, dependencies, plus config sections for
tools (`[tool.ruff]`, `[tool.pytest.ini_options]`). `uv.lock` is the exact resolved snapshot —
**commit both**, never commit `.venv`.

**Habit:** `uv run <cmd>` beats activating the venv manually (`source .venv/bin/activate`).
It always uses the right environment, works in scripts and CI, and there's nothing to forget
to deactivate.

---

## 2. Running code — scripts vs. modules

Two ways to execute Python, and the difference matters:

```bash
python main.py          # run a FILE as a script
python -m pkg.tool      # run a MODULE by its import path
```

- `python file.py` — runs the file; `sys.path[0]` is the **file's directory**.
- `python -m pkg.tool` — imports and runs `pkg/tool.py`; `sys.path[0]` is the **current
  working directory**, so package-internal imports resolve properly. This is why tools run as
  `python -m pytest`, and why running a file buried inside a package often breaks its imports
  (see §5).

**`if __name__ == "__main__":`** — the guard exists because *importing a module executes all
of its top-level code*. Every module has a `__name__`: it's `"__main__"` when the file is the
entry point, and the module's import path when imported. The guard means "only run this when
executed directly, not on import":

```python
def main() -> None: ...

if __name__ == "__main__":
    main()
```

Without it, `import mymodule` from a test would trigger the whole program. Kotlin/Java's
`main()` is only an entry point; Python's top level is *live code* — the guard is how you get
entry-point semantics back.

**The REPL** (`uv run python`) — quick experiments; `_` holds the last result;
`help(obj)` / `dir(obj)` for introspection. Reach for it the way you'd reach for a Kotlin
scratch file.

---

## 3. Project layout — the src layout

The professional default shape for a small Python project:

```text
my-project/
├── pyproject.toml        # manifest + tool config
├── uv.lock               # exact resolved deps (committed)
├── README.md
├── .python-version       # interpreter pin for uv
├── src/
│   └── my_project/       # the actual package (import name: my_project)
│       ├── __init__.py
│       └── cli.py
└── tests/
    └── test_cli.py
```

**Why `src/` instead of the package at repo root:** with the package at the root, `python`
run from the repo can import your code from the *working directory* rather than the
*installed* package — tests then pass locally but the shipped package is broken (missing
files, wrong metadata). The `src/` layout forces everything through a real install
(`uv sync` installs the project in editable mode), so tests exercise what users get.

Notes:
- Repo/dist name may use hyphens (`my-project`); the **import name uses underscores**
  (`my_project`) — hyphens aren't valid in Python identifiers.
- `tests/` lives *outside* `src/` — tests aren't part of the shipped package.

---

## 4. Ruff — one linter/formatter, zero debates

**Ruff** replaced the old zoo (flake8 + isort + black + pylint…) as a single, extremely fast
tool that both lints and formats:

```bash
uv add --dev ruff
uv run ruff check .          # lint (add --fix to auto-fix)
uv run ruff format .         # format (the black-style formatter)
```

Config lives in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]   # errors, pyflakes, import-sort, modernize, bugbear
```

The point is the same as ktlint/SwiftFormat: adopt the community formatter, configure almost
nothing, never discuss style in review again. Run both commands before every commit (or wire
them into pre-commit/CI later — roadmap §2.5 territory).

---

## 5. How imports actually work

The mental model that dissolves the entire "why can't Python find my module" class of errors:

- A **module** is just a `.py` file. A **package** is just a directory containing modules.
- **`__init__.py`** marks a directory as a package and runs on first import of anything in
  it. Usually empty; sometimes used to re-export a public API
  (`from .cli import main`).
- **Import resolution is a path search**: Python walks `sys.path` (script's directory or
  CWD first — see §2, then installed `site-packages`) and takes the first match. There is
  no classpath magic, no build-tool resolution — just that list.

**Absolute vs relative imports:**

```python
from my_project.services import claude     # absolute — default choice, always clear
from . import config                        # relative — siblings within the same package
from .config import Settings                # relative — fine for intra-package wiring
```

Absolute imports are the default recommendation; relative imports are acceptable *within* a
package for internal wiring. Never use relative imports across package boundaries.

**The `ModuleNotFoundError` diagnosis table:**

| Symptom | Cause | Fix |
|---|---|---|
| Works in IDE, fails in terminal | IDE injected the project root into `sys.path`; terminal didn't | src layout + `uv sync` (installs the package), then `uv run` |
| `python src/my_project/cli.py` fails on package imports | Ran a package-internal file as a script — `sys.path[0]` is the file's dir, package parent invisible | `uv run python -m my_project.cli` |
| `attempted relative import with no known parent package` | Relative import in a file executed directly | Same fix — run as a module (`-m`), not a file |
| Import works but it's the wrong code | A same-named file/dir earlier on `sys.path` shadows the real one (e.g. a local `json.py`) | Never name files after stdlib/installed packages |
| Fresh clone can't import anything | No venv yet | `uv sync` |

**Rule that prevents 90% of it:** use the src layout, let uv install the package, and always
run through `uv run` (with `-m` for package entry points). Then `sys.path` is always right and
imports behave like a compiled language's.

---

## Quick self-check (cold recall)

1. What two files fully define a project's dependencies, and which is exact?
2. Why does `python src/pkg/cli.py` break imports that `python -m pkg.cli` resolves?
3. What executes when you `import` a module, and what does the `__main__` guard change?
4. Why does the src layout exist — what failure mode does it prevent?
5. A file imports fine in PyCharm but not from the terminal — what's the first hypothesis?
