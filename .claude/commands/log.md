---
description: Record end-of-day cert-study progress — write the evening log and tick completed boxes.
argument-hint: "<how the day went / what you completed / confidence 1-5>"
allowed-tools: Read, Edit
---

You are recording the user's end-of-day progress for the certification study plan. The user's
reflection / what they completed is in `$ARGUMENTS`. **Only edit `certification/STUDY-PLAN.md`** —
do not touch any other file.

## Step 1 — Find the day to log
- Read `certification/STUDY-PLAN.md`.
- The day to log = the current day = the **earliest day block with unchecked morning-checklist
  boxes** (the one being worked today). If the user named a specific day in `$ARGUMENTS`, use that.

## Step 2 — Update that day block (use Edit; preserve everything else exactly)
- **Tick completed tasks:** based on `$ARGUMENTS`, change `- [ ]` to `- [x]` for the tasks the user
  reports done. If they say "done"/"finished everything", tick all of that day's morning boxes. If
  it's unclear which tasks were completed, ask **one** brief clarifying question before editing.
- **Write the evening log:** replace that day's `🌙 **Evening log:** _..._` placeholder line with the
  user's actual entry. Capture **confidence (1–5)**, **what clicked**, and **what to revisit**. If the
  user didn't give a 1–5 confidence, ask for it once, then write it. Keep it to one line.
- **Weekly checkpoint:** if this day's tasks are now all ticked *and* it is the last study day of a
  week, also tick that week's **Weekly checkpoint** box and fill its "Weakest: ___" from the revisit notes.

## Step 3 — Confirm
- Briefly confirm what you ticked and the evening log you wrote.
- If the log flags something to revisit, note that it will resurface in tomorrow's `/today` warm-up
  and in the Phase 3 weak-area work.
- If the user is behind the calendar, gently *offer* to adjust the plan (don't change it unprompted).
