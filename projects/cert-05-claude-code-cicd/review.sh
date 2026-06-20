#!/usr/bin/env bash
# Minimal "Claude Code in CI" review step (Project 05).
#
# Runs `claude -p` to review the diff and emit schema-valid JSON (Phase 1), then renders each
# finding (and shows how it'd post as a PR comment, Phase 1/4).
#
# CREDIT-FREE: with no ANTHROPIC_API_KEY set, it falls back to sample_findings.json so you can
# exercise the parse-and-render path without calling the API. Set the key (and run in a PR) to go live.
set -euo pipefail
cd "$(dirname "$0")"

BASE="${1:-HEAD}"   # base ref to diff against (CI passes origin/<base_branch>)

# What to review: the diff under app/ (fall back to the whole module if there's no diff locally).
CODE="$(git --no-pager diff "$BASE" -- app/ 2>/dev/null || true)"
[ -z "$CODE" ] && CODE="$(cat app/*.py)"

PROMPT="Review the code below against the criteria in CLAUDE.md. Report ONLY real bugs and security
issues, one finding per issue, matching the JSON schema. Code under review:
$CODE"

if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  echo "→ running claude -p (live)…"
  # --print: non-interactive (Phase 1). --output-format json + --json-schema: machine-parseable.
  # NOTE: live output is a JSON envelope; extract the result field before parsing (left as a TODO
  # so the credit-free path stays simple). For now we just capture it.
  claude -p "$PROMPT" --output-format json --json-schema ./schema.json > raw_output.json
  python3 -c "import json,sys; o=json.load(open('raw_output.json')); \
print(o.get('result', o) if isinstance(o,dict) else o)" > findings.json
else
  echo "→ no ANTHROPIC_API_KEY: using sample_findings.json (credit-free demo)"
  cp sample_findings.json findings.json
fi

# Render findings (python3 — no jq dependency). This is the parse step CI uses to post comments.
python3 - <<'PY'
import json
findings = json.load(open("findings.json"))["findings"]
print(f"\n{len(findings)} finding(s):\n")
for f in findings:
    print(f"  [{f['severity'].upper()}] {f['location']}")
    print(f"      {f['issue']}")
    if f.get("suggested_fix"):
        print(f"      fix: {f['suggested_fix']}")
    print()
PY

# In real CI you'd post each finding as an inline PR comment, e.g. (requires gh + a PR context):
#   gh api repos/$REPO/pulls/$PR/comments -f path=... -F line=... -f body="..."
echo "(in CI: post each finding as an inline PR comment via 'gh api' — see README)"
