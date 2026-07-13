---
description: Record end-of-day roadmap progress — tick completed boxes and write the evening log.
argument-hint: "<how the day went / what you completed / confidence 1-5>"
allowed-tools: Read, Edit, Write
---

You are recording the user's end-of-day progress on the **AI Engineer roadmap**. The user's
reflection / what they completed is in `$ARGUMENTS`. You may edit only these files:
`planning/AI-ENGINEER-ROADMAP.md`, `docs/PYTHON-FLUENCY.md`, `planning/DAILY-LOG.md`, and `planning/TODAY.md`.

## Step 0 — Read planning/TODAY.md first
- If `planning/TODAY.md` exists and isn't already stamped `> logged ✅`, its ticked boxes and Notes
  section are the primary record of what was done today; `$ARGUMENTS` adds color (confidence,
  reflections) and wins on any conflict.
- After Steps 1–2 are done, stamp it by appending `> logged ✅ YYYY-MM-DD` at the end of the file
  so tomorrow's `/today` knows it can be overwritten.
- If the file doesn't exist, work from `$ARGUMENTS` alone as before.

## Step 1 — Tick completed boxes (use Edit; preserve everything else exactly)
- **`docs/PYTHON-FLUENCY.md`** — if the day included Python study, tick the batch topics the user
  reports done and fill that batch's row in the Drills ledger if a drill was completed.
- **`planning/AI-ENGINEER-ROADMAP.md`** — tick a roadmap item **only when its "done means" bar is
  met**, not merely started. If the user reports work toward an item (e.g. "made progress on P1"),
  leave the box unticked — progress lives in the daily log, ticks are for completion.
- If it's unclear which items were completed, ask **one** brief clarifying question before editing.

## Step 2 — Write the evening log
- Append today's entry to **`planning/DAILY-LOG.md`** (create the file with a `# Daily Log` heading if
  it doesn't exist; newest entry at the top, under the heading).
- Entry format, one line per day:
  `- **YYYY-MM-DD (Day)** · Phase/focus · Confidence (1–5): N · Did: … · Clicked: … · Revisit: …`
- If the user didn't give a 1–5 confidence, ask for it once, then write it.
- Convert relative dates to absolute. Keep it to one line — this file is a ledger, not a diary.

## Step 3 — Confirm
- Briefly confirm what you ticked and the log line you wrote.
- Anything flagged "revisit" will resurface in tomorrow's `/today` warm-up — say so.
- If a whole roadmap subsection or Python batch just completed, note what the next one is
  (one line, no planning session).
- If progress has stalled against the weekly cadence table, gently *offer* to re-plan during the
  weekly review (don't change the roadmap unprompted).
