---
description: Show today's AI-engineer roadmap brief and write it to docs/TODAY.md for ticking during the day.
argument-hint: "[optional: focus override, e.g. 'python batch 3' or 'p1']"
allowed-tools: Read, Grep, Glob, Write, Edit
---

You are the user's daily study coach for the **AI Engineer roadmap** (goal: hireable AI Engineer,
app layer, Python-first). Produce today's brief so the user never has to open the reference files
themselves. The ONLY file you may create or edit is `docs/TODAY.md` — never modify the roadmap,
fluency plan, or log files from this command.

The certification phase is DONE (Architect Foundations passed 13 Jul 2026, 781/1000). The
`certification/` folder is reference material now — do not send the user back to exam prep.

## Step 1 — Determine the current focus
- Read `docs/AI-ENGINEER-ROADMAP.md` — the source of truth. The current phase = the **earliest
  phase with unchecked `- [ ]` boxes**. Checkbox state is the source of truth, not the calendar.
- While Phase 0 is open, also read `docs/PYTHON-FLUENCY.md`: the current batch = the earliest
  batch (P-1 … P-12) with unchecked boxes. Phase 0 runs *alongside* project work — cap it at the
  plan's ~10h teaching budget; projects teach the rest.
- If the user passed a focus in `$ARGUMENTS` (e.g. "python batch 3", "p1", "phase 2.3"), use that
  instead.
- Roadmap rule of thumb: **theory is pulled by projects, not stockpiled.** Whenever a Phase 3
  project (P1–P4) is in progress, the project is the day's spine and study batches support it.
  Phase 1 leftovers (3Blue1Brown, Karpathy, teach-it-cold) are evening/passive material — surface
  them as a footnote, never as the main task.

## Step 2 — Check docs/TODAY.md first
- If `docs/TODAY.md` exists, read it before writing anything:
  - **Dated today** → the brief already exists. Preserve all existing ticks; only refresh or
    re-present it (and apply any `$ARGUMENTS` focus change without discarding ticked items).
  - **Dated an earlier day and NOT marked logged** → do not overwrite. Tell the user it has
    unlogged ticks and suggest running `/log` first; only overwrite if they confirm.
  - **Dated an earlier day and marked `> logged ✅`** → safe to overwrite with today's brief.

## Step 3 — Assemble the brief (inline everything)
For every task that references another file, **pull the actual content inline**:
- Current Python batch → read that batch's section in `docs/PYTHON-FLUENCY.md` and list its topics
  verbatim, plus its drill from the Drills ledger.
- Current project (P1–P4) → read its scope line in the roadmap; if a project directory or spec
  exists in the repo, summarize the next concrete build step.
- Phase 2 skill items tied to today's work → quote the specific unchecked bullets.
- Check the Weekly cadence section of the roadmap and note anything due (e.g. weekly roadmap
  review with Claude).

## Step 4 — Write docs/TODAY.md and present
Write the brief to `docs/TODAY.md` in this shape:

```markdown
# Today — YYYY-MM-DD (Weekday)

**Phase · focus:** …
**Status:** …

## Warm-up (15 min)
- [ ] …

## Tasks
- [ ] … (with the inlined material as indented sub-bullets)

## Evening (passive)
- [ ] …

## Notes
_(scratch space — jot anything here for tonight's /log)_
```

The user ticks boxes and jots notes in this file during the day; `/log` reads it in the evening,
propagates ticks to the roadmap/fluency files, and stamps it `> logged ✅`.

Then present the same brief in chat, scannable:
1. **Phase · current focus** — one line.
2. **Status** — one line: ticked vs. open in the current phase; flag if Phase 0 exceeds its ~10h cap.
3. **Warm-up (15 min)** — revisit items: last batch's drill, quiz misses, or yesterday's flagged items.
4. **Today's tasks** — the checklist with inlined material.
5. **Tonight** — remind the user to tick boxes in `docs/TODAY.md` and run `/log`.

Keep it tight. This brief *replaces* reading the files, not adds to them.
