# Project 05 · Phase 1 — Headless invocation & structured output ⭐

> **Companion to:** [`overview.md`](overview.md). Phases: [1](phase-1.md) · [2](phase-2.md) ·
> [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). Build it yourself; the snippets are a reference.

**Phase 1 covers build steps 1–2** (Domains **3.6** CLI in CI, **4.3** structured output). Goal: get
Claude Code running inside a pipeline **without hanging**, emitting **machine-parseable** findings you
can turn into inline PR comments.

**Milestone:** the CI job runs `claude -p ...` to completion (no hang) and produces schema-valid JSON
that posts as inline PR comments.

**Phase 1 Definition of done**
- [ ] Pipeline runs Claude Code with `-p` and doesn't hang.
- [ ] JSON-schema output posts as structured inline PR comments.

---

## 0. Mental model — CI has no human and no TTY

```
  interactive Claude Code        CI Claude Code
  ─────────────────────────      ─────────────────────────
  waits for your input    →      NOTHING types back → HANGS
  prints prose to a human →      a script must PARSE it → needs JSON
```

Two problems, two fixes:
- **No human** to answer prompts → run **headless** with `-p`/`--print` (process prompt, print, exit).
- **A script, not a person, reads the output** → emit **structured JSON** (`--output-format json` +
  `--json-schema`) so CI can post each finding as a comment.

---

## 1. Step 1 — Non-interactive invocation (Domain 3.6) ⭐

```bash
claude -p "Review the staged diff for security issues" \
  --output-format json --json-schema ./schema.json
```

`-p` / `--print` makes Claude Code **process the prompt, print to stdout, and exit** — it never waits
for interactive input, so the job can't hang.

> **Exam point (Q10):** a CI job that hangs is fixed by **`-p`/`--print`**. The distractors are wrong:
> - `CLAUDE_HEADLESS=1` — not a real env var;
> - `--batch` — not the flag (and "batch" ≠ the Message Batches API);
> - `< /dev/null` — closing stdin doesn't put the CLI in print mode; it still runs interactively.

## 2. Step 2 — Structured, machine-parseable findings (Domain 3.6 / 4.3)

`--output-format json` makes the result a JSON document; `--json-schema` constrains it to *your* shape
so CI can rely on the fields. One finding per issue:

```json
// schema.json — array of findings
{
  "type": "object",
  "properties": {
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "location": {"type": "string"},        // "src/auth.py:42"
          "issue": {"type": "string"},
          "severity": {"type": "string", "enum": ["low", "medium", "high"]},
          "suggested_fix": {"type": "string"},
          "detected_pattern": {"type": "string"} // enables false-positive analysis later
        },
        "required": ["location", "issue", "severity"],
        "additionalProperties": false
      }
    }
  },
  "required": ["findings"],
  "additionalProperties": false
}
```

CI then parses the JSON and posts each `finding` at its `location` as an inline PR comment. The
`detected_pattern` field is what lets you later measure which rule produced false positives (Phase 2).

---

## 3. Run & observe

- **No hang:** run the command in the pipeline (or locally piping no input) and confirm it **exits**
  on its own. Deliberately drop `-p` once to *see* it wait — that's the failure Q10 describes.
- **Valid JSON:** pipe the output to `jq '.findings[]'` and confirm every finding has
  `location`/`issue`/`severity`. A schema violation means the prompt or schema needs tightening.
- **Comments land:** wire the parsed findings into your PR-comment step and confirm they appear at the
  right `file:line`.

**Scaffold:** `projects/cert-05-claude-code-cicd/` has this wired up — `review.sh` runs `claude -p` with
`schema.json`, and `ci/claude-review.yml` is the GitHub Actions template. Run `./review.sh` with no API
key to watch the parse-and-render path on canned findings.

---

## 4. Exam mapping

- **CLI in CI** (EXAM-PREP §3.6 / Cheatsheet): `-p`/`--print` = non-interactive (prevents hangs);
  `--output-format json` + `--json-schema` = machine-parseable findings for inline PR comments.
- **Structured output** (§4.3): a JSON schema guarantees the *shape* CI depends on (it doesn't fix
  *semantic* quality — that's Phase 2).
- Q10 → `-p`/`--print`.

## 5. Close out the phase

- [ ] Tick the two Phase 1 boxes in [`overview.md`](overview.md).
- [ ] Notes one-liner: *"CI hang → `-p`/`--print` (not CLAUDE_HEADLESS/--batch/`</dev/null`);
  `--output-format json` + `--json-schema` → parseable findings for inline PR comments."*
- [ ] Commit; run `/log`.

### What Phase 2 will add (preview)
The output is now *structured* but not yet *trustworthy*: explicit categorical review criteria and
few-shot examples to cut false positives, so the comments are worth reading.
