# Investigation findings scratchpad

<!-- Agent writes specific findings here as it explores. Re-reads this file at the start of
     each new phase instead of relying on conversation history. -->

## Phase 1 — Tool selection & MCP
- Built-in tool mental model confirmed: Grep=contents, Glob=paths, Edit=unique anchor else Read+Write
- MCP server lives at: projects/cert-06-developer-productivity-explorer/server.py
- Resource: project://catalog — answers structure questions without exploratory calls
- Tools: search_phases(query), get_phase(phase_id)
- Server registered in: .claude/settings.json (project-level)

## Phase 2 — Exploration workflow
- Plan mode used for multi-file restructure task (phases/ subfolder exercise)
- Explore subagent mapped all cross-references before any edits — returned digest, not raw files
- Reverted the restructure after demonstrating the pattern

## Phase 3 — Long-session context (in progress)
- [ ] Scratchpad pattern demonstrated (this file)
- [ ] Manifest pattern demonstrated
- [ ] Subagent delegation exercise run
