# cert-05 — Claude Code in CI/CD (minimal pipeline)

A tiny, runnable scaffold for **Project 05 / Scenario 5**: wiring Claude Code into CI to review PRs.
The "app under review" is deliberately trivial — the learning is in the **review job**, which is
language/framework-agnostic (that's why this is a few Python files, not a React Native app).

## Layout
```
app/calculator.py          # tiny module with 2 intentional bugs (the code being reviewed)
tests/test_calculator.py   # existing test (passed into context so gen doesn't duplicate it)
CLAUDE.md                  # CI review standards (categorical criteria + severities) — Phase 2/4
schema.json                # findings schema for --json-schema — Phase 1
review.sh                  # runs `claude -p`, parses JSON, renders findings — Phases 1/4
sample_findings.json       # canned findings so review.sh runs WITHOUT an API key
ci/claude-review.yml       # GitHub Actions workflow template — Phase 1/4
```

## Primary files

The engine is three files; everything else is the trigger or fixtures.

| File | Why it's primary |
|------|------------------|
| **`review.sh`** | The review step itself — builds the prompt, runs `claude -p`, parses the JSON, renders/posts findings. |
| **`schema.json`** | The output contract `--json-schema` enforces, so findings are machine-parseable. |
| **`CLAUDE.md`** | The review standards/criteria (categorical rules + severities) Claude reviews against. |

Secondary: `ci/claude-review.yml` is just the **trigger** (it calls `review.sh` on PRs — and only runs
from the repo root, not here); `sample_findings.json` is a fixture for credit-free runs; `app/` and
`tests/` are the disposable "code under review." Swap GitHub Actions for another CI system and only the
trigger changes — the three primary files stay the same.

## Run it (credit-free)
```bash
cd projects/cert-05-claude-code-cicd
./review.sh
```
With **no `ANTHROPIC_API_KEY`**, `review.sh` uses `sample_findings.json` so you can see the whole
parse-and-render path. Expected: 2 findings (a `high` ZeroDivisionError, a `medium` comment-contradicts-code).

## Run it live (needs API credits)
```bash
export ANTHROPIC_API_KEY=...          # you don't have this yet — build now, run later
npm install -g @anthropic-ai/claude-code
./review.sh origin/main               # diffs against main, calls `claude -p`
```

## How it maps to the phases ([overview](../../certification/projects/05-claude-code-cicd/overview.md))
- **Phase 1** — `review.sh` uses `claude -p` (non-interactive) + `--output-format json --json-schema`.
- **Phase 2** — `CLAUDE.md` holds categorical criteria + per-severity examples (not "be conservative").
- **Phase 3** — the review runs as its **own** `claude -p` (independent of whatever wrote the code);
  for a big PR you'd loop `review.sh` per file + a final cross-file pass.
- **Phase 4** — `CLAUDE.md` = CI context; the workflow's `synchronize` trigger is where re-run hygiene
  (pass prior findings, report only new) lives; the pre-merge job is **sync**, the overnight report is a
  separate **Batches** job.

## To actually deploy in a repo
1. Copy `ci/claude-review.yml` to the **repo root** `.github/workflows/` (GitHub ignores workflows
   under `projects/`).
2. Add `ANTHROPIC_API_KEY` to repo secrets.
3. Extend `review.sh`'s comment-posting step (`gh api .../pulls/$PR/comments`) to post each finding
   inline.

## Known caveat
The live `claude -p --output-format json` result is a JSON **envelope**; `review.sh` has a TODO to
extract the `result` field before parsing. The credit-free path reads the schema shape directly.
