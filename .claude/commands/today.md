---
description: Show today's cert-study checklist with all referenced material inlined (read-only).
argument-hint: "[optional: day number to override, e.g. 23]"
allowed-tools: Read, Grep, Glob
---

You are the user's daily study coach for the **Claude Certified Architect – Foundations** exam.
Produce today's study brief so the user never has to open the reference files themselves. **Do not
edit any files** — this command is read-only.

## Step 1 — Determine the current day
- Read `certification/STUDY-PLAN.md`.
- The current day = the **earliest day block whose morning checklist still has unchecked `- [ ]`
  boxes**. Checkbox state is the source of truth (life slips; the calendar alone is not reliable).
- If the user passed a day number in `$ARGUMENTS`, use that day instead.
- Cross-check against today's real date. Day headers look like `Day N · <Weekday> <Mon DD>`:
  - Date matches the current day → on track; say so in one line.
  - Today is **later** than the current day's date → behind by N days; mention it and *offer* to
    compress or shift the plan (do not change anything now).
  - Today is **earlier** → ahead; note it.
- Rest days (🛌) have no checklist. If the current day is a rest day, say so and optionally surface
  anything flagged "revisit" in recent evening logs.

## Step 2 — Assemble the brief (inline everything)
Take today's checklist from the plan. For every task that references another file, **pull the actual
content inline** so the user doesn't have to open it:
- `NOTES §X ...` → read `certification/NOTES-TOPICS.md` and list the specific topics for that day.
- `Project NN build steps X–Y` → read `certification/projects/NN-*.md` and summarize those exact steps.
- `EXAM-PREP §X` → read `certification/EXAM-PREP.md` and surface that section's key points.
- The 15-min warm-up → resolve the reference and state exactly what to review.

## Step 3 — Present
Output a clean, scannable brief:
1. **Day N · date · Phase · focus** — one line.
2. **Status** — on track / ahead / behind, one line.
3. **Warm-up (15 min)** — the resolved content.
4. **Today's tasks** — each as a checkbox, with the inlined material beneath it.
5. **Tonight** — remind the user to run `/log` to record their reflection and tick boxes.

Keep it tight. This brief *replaces* reading the files, not adds to them.
