# Session prompt — Project 06 codebase exploration

Use this prompt at the start of every session (fresh or resumed).

---

## Starting a fresh session

```
We are exploring the Project 06 cert codebase at:
  certification/projects/06-developer-productivity-explorer/

Ground rules for this session:
1. After completing each phase, write your key findings to
   .scratch/findings.md under a heading for that phase.
   Record specific facts: exact file paths, function names,
   decisions made — not vague summaries.

2. At the end of each phase, update .scratch/manifest.json:
   - Set phase_completed and phase_in_progress
   - Update key_files with any important paths you found
   - Append to decisions_made if a choice was settled
   - Refresh resume_prompt to reflect current state

3. Before starting a new phase, re-read .scratch/findings.md
   to restore context from prior phases.

4. If I ask about something you found earlier, check
   .scratch/findings.md before answering — don't rely on
   conversation memory.

Start with Phase 1: read overview.md, then begin.
```

---

## Resuming after a crash

```
Load .scratch/manifest.json and read the resume_prompt field.
Then read .scratch/findings.md to restore all prior findings.

Do not re-explore phases already marked as completed in the manifest.
Pick up from phase_in_progress and continue from where we left off.
```

---

## Mid-session context recovery (when drift is detected)

If Claude starts saying "typically" or "usually" instead of citing
specific files or functions, run this:

```
Re-read .scratch/findings.md now and answer my last question
again using only the specific facts recorded there.
```
