# CI Review Standards (Project 05)

Project context loaded by CI-invoked Claude. Keep reviews **actionable with few false positives.**

## What to report
- Real **bugs** (crashes, wrong results, unhandled edge cases) and **security** issues.
- A comment/docstring **only when its claimed behavior contradicts the code** — not mere "could be clearer".

## What to skip
- Minor style, formatting, naming preferences.
- Locally-consistent patterns (matches the surrounding file's conventions).
- Speculative "might be nice" suggestions.

## Severity (with concrete examples)
- **high** — can crash or produce wrong output. e.g. `sum(xs)/len(xs)` with no empty-list guard.
- **medium** — correctness/robustness risk that isn't an immediate crash. e.g. a docstring that says
  "returns a copy" while returning the live reference.
- **low** — minor but real (e.g. a misleading error message).

> Do NOT use vague instructions like "be conservative" — apply the categorical rules above.
> If one rule (`detected_pattern`) is noisy, disable that rule rather than letting it poison trust.

## Test generation standards
- Framework: `pytest`. Tests live under `tests/`, named `test_*.py`.
- A valuable test covers an **uncovered** behavior — check the existing tests passed in context and do
  not duplicate scenarios already covered. Prioritize edge cases (empty input, boundaries, errors).
