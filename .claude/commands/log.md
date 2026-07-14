---
description: Record end-of-day roadmap progress — tick completed boxes and write the evening log.
allowed-tools: Read, Edit, Write
---

You are recording the user's end-of-day progress on the **AI Engineer roadmap**. This is a
zero-argument workflow by default: derive the log from `planning/TODAY.md` without asking the user
for a summary, confidence score, explanation, or other metadata. If `$ARGUMENTS` is supplied
voluntarily, treat it only as a correction or additional reflection. You may edit only these files:
`planning/AI-ENGINEER-ROADMAP.md`, `docs/PYTHON-FLUENCY.md`, `planning/DAILY-LOG.md`, and `planning/TODAY.md`.

## Step 0 — Read planning/TODAY.md first
- If `planning/TODAY.md` exists and isn't already stamped `> logged ✅`, its ticked boxes and Notes
  section are the authoritative record of what was done today; voluntary `$ARGUMENTS` wins on any
  conflict.
- After Steps 1–2 are done, stamp it by appending `> logged ✅ YYYY-MM-DD` at the end of the file
  so tomorrow's `/today` knows it can be overwritten.
- If the file doesn't exist, use voluntary `$ARGUMENTS` if present; otherwise report that there is
  no daily brief to log. Do not ask the user to reconstruct the day.

## Step 1 — Tick completed boxes (use Edit; preserve everything else exactly)
- **`docs/PYTHON-FLUENCY.md`** — if the day included Python study, tick the batch topics the user
  reports done and fill that batch's row in the Drills ledger if a drill was completed.
- **`planning/AI-ENGINEER-ROADMAP.md`** — tick a roadmap item **only when its "done means" bar is
  met**, not merely started. If the user reports work toward an item (e.g. "made progress on P1"),
  leave the box unticked — progress lives in the daily log, ticks are for completion.
- Infer completion only from checked boxes, explicit Notes, and already-verifiable completion
  evidence. If evidence is ambiguous, leave the source checkbox unchanged and record the work as
  progress. Do not ask a clarifying question merely to make the log more detailed.

## Step 2 — Write the evening log
- Append today's entry to **`planning/DAILY-LOG.md`** (create the file with a `# Daily Log` heading if
  it doesn't exist; newest entry at the top, under the heading).
- Entry format, one line per day:
  `- **YYYY-MM-DD (Day)** · Phase/focus · Did: … · Clicked: … · Revisit: …`
- Derive **Phase/focus** from the summary table and project spine; **Did** from checked tasks and
  Notes; **Clicked** from source-of-truth boxes actually propagated; and **Revisit** from quiz
  misses, blockers, explicit Notes, or important incomplete follow-through. Use `none noted` when
  there is no supported revisit item. Do not invent subjective reflections.
- Convert relative dates to absolute. Keep it to one line — this file is a ledger, not a diary.

## Step 3 — Confirm
- Briefly confirm what you ticked and the log line you wrote.
- Anything flagged "revisit" will resurface in tomorrow's `/today` warm-up — say so.
- If a whole roadmap subsection or Python batch just completed, note what the next one is
  (one line, no planning session).
- If progress has stalled against the weekly cadence table, gently *offer* to re-plan during the
  weekly review (don't change the roadmap unprompted).
