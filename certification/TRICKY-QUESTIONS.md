# ⚠️ Tricky Questions — the ones people usually get wrong

> 25 questions (5 per domain) built around the exam's known trap patterns: every distractor
> here is "technically valid but wrong" in the house style — over-engineered, symptom-not-root-cause,
> prompt-where-determinism-needed, or disproportionate-first-step.
>
> **Do them closed-book, all 25, before scrolling to the answer key at the bottom.**
> Target: ≥22/25. Any miss → add it to the Weak List in `EXAM-WEEK-CHECKLIST.md`.

---

## Set 1 — Agentic Architecture & Orchestration (D1)

**Q1.** A developer's agent loop decides to stop when the assistant's reply contains the phrase
"task complete." Sometimes it loops forever; sometimes it stops mid-task. Most reliable fix?

- A. Add a maximum-iteration cap of 10 as the stop condition
- B. Prompt the model to always end its final reply with "TASK COMPLETE"
- C. Loop while `stop_reason == "tool_use"`; exit when it is `"end_turn"`
- D. Stop whenever the response contains a text block instead of a tool call

**Q2.** A coordinator spawns three research subagents one after another, and total latency is
too high. The subtasks are independent. How do you run them in parallel?

- A. Have the coordinator emit multiple `Task` tool calls in a single assistant turn
- B. Spawn each subagent from a separate coordinator turn with an async flag
- C. Set `parallel: true` in each subagent's `AgentDefinition`
- D. Run three coordinator instances, one per subtask

**Q3.** A subagent returns generic, unhelpful results even though the coordinator has all the
customer's details in its conversation. Most likely cause?

- A. The subagent is running on a smaller model tier
- B. The subagent's `allowedTools` list is empty
- C. The `Task` tool truncated the payload
- D. Subagents have isolated context — the coordinator never passed the details explicitly in the prompt

**Q4.** Policy: refunds over $500 must never be executed by the agent and must go to a human.
How do you guarantee this?

- A. State the rule prominently in the system prompt with few-shot examples
- B. A tool-call interception hook that blocks `process_refund` over $500 and redirects to escalation
- C. Set temperature to 0 so the model follows instructions deterministically
- D. A nightly audit job that flags any violations for review

**Q5.** A multi-agent research system produces reports that consistently miss whole sub-topics.
Queried directly, each search agent performs well. What should you fix?

- A. Give the search agents broader search tools
- B. Increase the synthesis agent's context budget
- C. The coordinator's decomposition — it splits topics too narrowly, leaving coverage gaps
- D. Add a second synthesis pass to catch what the first one missed

---

## Set 2 — Tool Design & MCP Integration (D2)

**Q6.** The agent keeps calling `search_knowledge_base` when it should call `search_tickets`;
the two descriptions are similar. Best **first** step?

- A. Build a keyword-based router that picks the tool before the LLM runs
- B. Rewrite both descriptions to differentiate them: when to use each, input formats, boundaries
- C. Consolidate both into a single tool with a `source` parameter
- D. Force `tool_choice` to `search_tickets` for support queries

**Q7.** A search tool executes successfully but finds no matches for a valid query. What should
the tool return?

- A. `isError: true` with the message "search unavailable"
- B. An empty string so the model moves on
- C. A retryable error so the agent tries a different query
- D. A success result explicitly indicating zero matches — an empty result is not an error

**Q8.** One agent has 18 tools and frequently picks the wrong one. Best fix?

- A. Split responsibilities into role-scoped agents with 4–5 tools each
- B. Move to a larger model with better reasoning
- C. Make all 18 descriptions longer and more detailed
- D. Set `tool_choice: "any"` so it always calls something

**Q9.** A team MCP server needs an API token. The config must be shared via git. How?

- A. Commit the token inside `.mcp.json` and restrict repository access
- B. Project `.mcp.json` referencing `${API_TOKEN}` via environment-variable expansion
- C. Have each developer add the server to their own `~/.claude.json`
- D. Encrypt `.mcp.json` and share the key out-of-band

**Q10.** Every document must be processed by `extract_metadata` before any other tool runs.
How do you guarantee the first call?

- A. `tool_choice: "any"` on the first request
- B. Prompt instruction: "always call extract_metadata first"
- C. `tool_choice: {"type": "tool", "name": "extract_metadata"}` on the first request
- D. List `extract_metadata` first in the tools array

---

## Set 3 — Claude Code Configuration & Workflows (D3)

**Q11.** Testing conventions must apply to all `*.test.tsx` files, which are spread across the
entire repository. Where do the conventions go?

- A. A `.claude/rules/` file with `paths: ["**/*.test.tsx"]` glob frontmatter
- B. A CLAUDE.md in every directory that contains test files
- C. The root CLAUDE.md, trusting the model to infer when they apply
- D. A skill the developer invokes when writing tests

**Q12.** Claude follows your team standards on your machine, but ignores them entirely on a
teammate's machine using the same repo. Most likely cause?

- A. The teammate is on an older model version
- B. The teammate's context is full and needs `/compact`
- C. The teammate's Claude Code version doesn't support `.claude/rules/`
- D. The standards live in your user-scope `~/.claude/CLAUDE.md`, not in project scope

**Q13.** A CI pipeline invokes `claude` and the job hangs until it times out. Fix?

- A. Add a timeout wrapper to the CI job
- B. Run with `-p`/`--print` so it executes non-interactively
- C. Add `--output-format json`
- D. Shorten the prompt so it finishes faster

**Q14.** Task: migrate a 45-file module from the monolith to microservices, with several valid
architectural approaches. How do you start?

- A. Direct execution, switching to plan mode if it gets stuck
- B. Fork a session per file and migrate them independently
- C. Plan mode — the complexity is already known, so plan before touching code
- D. Direct execution one file at a time to keep changes small

**Q15.** You want to continue yesterday's session, but many files changed overnight. Best move?

- A. Start a fresh session with a structured summary plus the list of changed files — yesterday's tool results are stale
- B. `--resume` the session and keep going; the context is valuable
- C. `--resume` the session, then run `/compact` to clean it up
- D. `fork_session` so the original stays intact

---

## Set 4 — Prompt Engineering & Structured Output (D4)

**Q16.** An invoice-extraction pipeline fabricates values for fields missing from the document.
Best fix?

- A. Add a validation-retry loop with error feedback
- B. Add "never make up values" to the prompt
- C. Lower the temperature to reduce creativity
- D. Make the fields optional/nullable in the tool schema so the model can return null

**Q17.** A validation-retry loop (resend document + failed output + specific error). Which
failures can it actually fix?

- A. Missing information — retries give the model more chances to find it
- B. Format/structure errors — not information genuinely absent from the document
- C. All error types, given enough retries
- D. Semantic errors, like line items not summing to the stated total

**Q18.** Cost pressure: the team proposes moving both the blocking pre-merge review and the
weekly full-repo audit to the Message Batches API for the 50% saving. Best call?

- A. Move both — 50% savings on everything
- B. Move neither — batch reliability is too low for production
- C. Move the weekly audit to batch; keep pre-merge sync — batch has no SLA and up to 24h latency
- D. Move pre-merge to batch with a 1-hour polling loop

**Q19.** An automated reviewer flags far too many false positives for "misleading comments."
Best **first** fix?

- A. Explicit categorical criteria plus few-shot examples contrasting acceptable vs genuine issues
- B. Train a small classifier on labeled review data to filter findings
- C. Add "be conservative — only flag high-confidence issues" to the prompt
- D. Upgrade to a larger model for better judgment

**Q20.** A 3,000-document batch completes with 40 requests failed on validation errors. Next step?

- A. Resubmit the entire batch — simplest and everything gets a retry
- B. Retry the 40 synchronously one at a time as they're found
- C. Log the 40 and move on; 98.7% success is acceptable
- D. Fix the issue and resubmit only the failed `custom_id`s as a new batch

---

## Set 5 — Context Management & Reliability (D5)

**Q21.** In long support conversations, progressive summarization keeps losing order numbers
and dates. Fix?

- A. Extract a persistent structured "case facts" block and include it in every prompt
- B. Drop summarization and rely on a bigger context window
- C. Summarize more frequently so less is lost each time
- D. Instruct the summarizer to "keep all important details"

**Q22.** Mid-troubleshooting, the customer says "just let me talk to a human." The agent should:

- A. Finish the current diagnostic first so the handoff is more useful
- B. Escalate immediately, with a structured handoff (ID, issue, steps tried, recommendation)
- C. Ask why they want a human, in case it can resolve the concern
- D. Escalate only if sentiment analysis confirms the customer is frustrated

**Q23.** Two credible sources report conflicting statistics for the same metric. The synthesis
agent should:

- A. Use the more recent source and drop the other
- B. Use the more authoritative source
- C. Present both figures with attribution and publication dates
- D. Average the two values and note the uncertainty

**Q24.** An extraction pipeline shows 97% aggregate accuracy on the validation set. Safe to
automate fully?

- A. Yes — 97% clears any reasonable threshold
- B. No — validate per document type and per field first; the aggregate can hide pockets of near-total failure
- C. Yes, with spot checks on low-confidence extractions only
- D. No — full automation needs 99.9%

**Q25.** Deep into a long refactoring session, the model starts citing "typical patterns" instead
of the actual classes it read earlier. Best response?

- A. Repeat the key filenames in every message
- B. Increase `max_tokens` so it can reason longer
- C. Tell it to re-read the files and be more careful
- D. Write findings to scratchpad files / structured state, then compact or restart the session from them

---
---

# 🔑 Answer key (don't scroll here until all 25 are done)

| Q | Ans | Why the tempting distractor fails | Heuristic |
|---|-----|-----------------------------------|-----------|
| 1 | **C** | Iteration caps (A) are a backstop, not a primary stop; text-parsing (B/D) is the original bug | §4.1 loop / anti-patterns |
| 2 | **A** | Parallel = multiple `Task` calls in ONE turn; there is no async flag or `parallel: true` | §4/D1.3 |
| 3 | **D** | Subagents inherit nothing — context must be explicit in the prompt | D1.3 |
| 4 | **B** | Prompts (A) are probabilistic; audits (D) catch violations after the money moved | §4.1 determinism |
| 5 | **C** | The search agents work — blaming them (A) or patching downstream (D) fixes a symptom | §4.2 root cause |
| 6 | **B** | Descriptions are the primary selection mechanism; a router (A) is over-engineered as a first step | §4.2/4.3 |
| 7 | **D** | Empty result ≠ access failure. Fake errors (A/C) trigger pointless retries | D2.2 |
| 8 | **A** | Too many tools degrades selection; longer descriptions (C) don't fix crowding | §4.5 least privilege |
| 9 | **B** | Committing secrets (A) is never right; user-scope (C) isn't shared/consistent | D2.4 `${ENV_VAR}` |
| 10 | **C** | `"any"` (A) = some tool, not that tool; prompts (B) and ordering (D) are suggestions | D2.3 forced tool_choice |
| 11 | **A** | Directory CLAUDE.md (B) can't follow scattered files; root file (C) relies on inference | §4.12 rules globs |
| 12 | **D** | Classic scope bug — user memory isn't in git, so teammates never see it | §4.12 / D3.1 |
| 13 | **B** | Without `-p` it waits for interactive input; a timeout (A) kills it without fixing it | D3.6 |
| 14 | **C** | "Start direct, switch later" (A) is the named trap when complexity is already known | §4.11 plan mode |
| 15 | **A** | Resuming (B/C) keeps stale tool results that actively mislead; fork (D) copies the staleness | D1.7 sessions |
| 16 | **D** | Prompts (B) reduce but can't prevent; retry loops (A) fix format, not fabrication incentive | D4.3 nullable |
| 17 | **B** | Retries can't conjure missing info (A) and don't fix semantics (D) | D4.4 |
| 18 | **C** | Batch ≠ blocking: no SLA, ≤24h. Polling (D) doesn't create an SLA | §4.9 latency match |
| 19 | **A** | "Be conservative" (C) is the named vague-instruction trap; a classifier (B) is over-engineered | §4.3 / D4.1 |
| 20 | **D** | Full resubmit (A) doubles cost; one-by-one sync (B) forfeits the batch discount | D4.5 `custom_id` |
| 21 | **A** | Bigger context (B) still has lost-in-the-middle; "keep everything" (D) is vague | D5.1 case facts |
| 22 | **B** | Explicit human request = escalate NOW; investigating first (A/C) is the trap | §4.10 |
| 23 | **C** | Picking either (A/B) loses information; averaging (D) invents a number nobody reported | D5.6 provenance |
| 24 | **B** | Aggregate hides per-type/per-field failure; low-confidence-only checks (C) miss confidently-wrong cases | D5.5 stratified |
| 25 | **D** | Long-session degradation isn't fixed by effort (C) or output budget (B) | D5.4 scratchpads |

**Scoring:** ≥22/25 → on track, add misses to the Weak List and re-test them once.
<19/25 → re-read EXAM-PREP §4 in full before anything else today.
