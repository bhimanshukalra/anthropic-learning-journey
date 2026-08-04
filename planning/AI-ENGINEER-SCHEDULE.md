# AI Engineer Daily Schedule

**Roadmap source:** `planning/AI-ENGINEER-ROADMAP.md`
**Start date:** Monday, 27 July 2026
**End date:** Sunday, 18 October 2026
**Time budget assumed:** 5h Monday-Friday + 10h Saturday + 10h Sunday = 45h/week.

**Naming convention:** Portfolio projects are **Project 1-Project 4** and may be abbreviated **P1-P4**. Python fluency study units are **Python Batch 1-Python Batch 12**.

## Roadmap Verdict

The roadmap is directionally strong for the goal: becoming hireable as an application-layer AI Engineer. At 45h/week, a 12-week calendar is more appropriate than the earlier 16-week version, but it only works if each project has hard scope gates and eval/report quality wins over feature completeness.

The main risk is producing four half-polished systems instead of strong proof. Keep Project 1-Project 4 frozen, ship each minimum viable evidence bar first, and use Sundays to cut anything that does not improve hireability evidence.

## Daily Operating Rules

- Every project week must produce something visible: code, eval results, a README section, a demo, or a written trade-off note.
- Theory is pulled by the current build task. Do not stockpile courses.
- Weekend days are 10-hour deep-work days: first block for building/evals, second block for docs, debugging, polish, review, or buffer.
- Every Sunday second block is a named recovery block: fix integration bugs, cut scope, update evals/docs, or recover slipped work.
- For risk tasks, if the task is not working after 6 focused hours, reduce scope and preserve eval/report quality.
- Every Sunday: update roadmap checkboxes, write a 5-10 line weekly review, cut scope if needed, and plan the next week.
- From Week 8 onward, apply to at least 5 roles/week while continuing Project 4 and interview prep.

## Week 1 - Foundations Close-Out + Project 1 Setup

| Date | Hours | Tasks |
|---|---:|---|
| Mon 27 Jul | 5 | Finish Python Batch 3: data structures/idioms; do the drill; choose the Project 1 document domain. |
| Tue 28 Jul | 5 | Finish Python Batch 4: functions and Python Batch 5: OOP; write tiny examples using dataclasses and callbacks. |
| Wed 29 Jul | 5 | Finish Python Batch 6: type hints and Python Batch 7: errors/resources; implement retry/backoff around a fake API. |
| Thu 30 Jul | 5 | Complete `AI-FOUNDATIONS.md` Batch 4; explain training vs. fine-tuning vs. RLHF aloud without notes. |
| Fri 31 Jul | 5 | Complete `AI-FOUNDATIONS.md` Batch 5; collect 20 target job posts and extract recurring requirements to tune Project 2-Project 4 choices. |
| Sat 1 Aug | 10 | Finish Python Batch 8: streaming and Python Batch 9: async; scaffold Project 1 with uv, Ruff, pytest, config, logging, and README outline. |
| Sun 2 Aug | 10 | Finish Python Batch 10-12: Pydantic, pytest, outside-world; take the Python exit test; weekly review, Project 1 scope lock, and recovery block. |

## Week 2 - Project 1: Multimodal Structured Documents

| Date | Hours | Tasks |
|---|---:|---|
| Mon 3 Aug | 5 | Work through Claude API basics: messages, stop reasons, temperature, max tokens, token counting. |
| Tue 4 Aug | 5 | Implement Project 1 API client wrapper, config loading, token/cost estimator, and mocked tests. |
| Wed 5 Aug | 5 | Collect 20-30 seed documents from one document family; define one schema family, golden-data format, nullable fields, and abstention rules. |
| Thu 6 Aug | 5 | Implement text/PDF/image loading with metadata preservation and progress events. |
| Fri 7 Aug | 5 | Implement Claude multimodal calls and structured-output parsing into Pydantic models. |
| Sat 8 Aug | 10 | Add validation errors, targeted retry-on-invalid, streaming progress, JSONL outputs, cost/latency logging, and fixtures. |
| Sun 9 Aug | 10 | Run first Project 1 eval; add per-field accuracy, hallucination rate, cost, latency; fix top failures; identify 5-10 possible Project 4 users/problems; weekly review and recovery block. |

## Week 3 - Project 1 Finish + Project 2 Retrieval Foundation

| Date | Hours | Tasks |
|---|---:|---|
| Mon 10 Aug | 5 | Finish Project 1 eval report, README quickstart, architecture diagram, and demo script. |
| Tue 11 Aug | 5 | Freeze Project 1 scope; choose Project 2 corpus and product question scope. |
| Wed 12 Aug | 5 | Set up Postgres/pgvector and ingestion versioning; document local setup. |
| Thu 13 Aug | 5 | Implement text/PDF ingestion preserving page, section, layout, and source metadata. |
| Fri 14 Aug | 5 | Implement structure-aware chunking, chunk IDs, metadata, and source spans. |
| Sat 15 Aug | 10 | Add embeddings, vector search, BM25 keyword search, metadata filters, and a retrieval debugging CLI. |
| Sun 16 Aug | 10 | Draft 40-50 eval questions including unanswerables; run early retrieval checks; send 2-3 Project 4 discovery messages; weekly review and recovery block. |

## Week 4 - Project 2: Hybrid RAG + Evals

| Date | Hours | Tasks |
|---|---:|---|
| Mon 17 Aug | 5 | Implement hybrid BM25 + vector retrieval, top-k controls, and retrieval logs. |
| Tue 18 Aug | 5 | Add reranking and measure quality, cost, and latency impact on sample queries. |
| Wed 19 Aug | 5 | Implement answer generation with page-level citations and abstention behavior. |
| Thu 20 Aug | 5 | Add contextual chunking experiment and cache expensive preprocessing. |
| Fri 21 Aug | 5 | Implement retrieval metrics: recall@k, MRR/nDCG where useful, groundedness, citation accuracy. |
| Sat 22 Aug | 10 | Expand eval set to 75-100 questions; run chunk-size and top-k experiments first; add contextualization/reranking only after baseline metrics are stable. |
| Sun 23 Aug | 10 | Risk task: build agentic-RAG ablation; if not working after 6h, reduce to one query class; compare fixed vs. agentic paths; send 2 discovery messages; weekly review and recovery block. |

## Week 5 - Project 2 Finish + Project 3 Bare Agent Loop

| Date | Hours | Tasks |
|---|---:|---|
| Mon 24 Aug | 5 | Wire Project 2 evals into CI using promptfoo or a small reproducible harness. |
| Tue 25 Aug | 5 | Write Project 2 eval report with clear recommendation, experiment tables, and trade-offs. |
| Wed 26 Aug | 5 | Polish Project 2 README/demo; freeze scope; choose Project 3 use case. |
| Thu 27 Aug | 5 | Define Project 3 task domain, fixed-workflow baseline, loop contract, and success metrics. |
| Fri 28 Aug | 5 | Implement bare loop: trigger, load state, select action, call tool, observe, decide next step. |
| Sat 29 Aug | 10 | Risk task: add three scoped tools with typed schemas, permission boundaries, idempotency, durable state, traces, and terminal states; if not working after 6h, ship one tool fully and stub the rest. |
| Sun 30 Aug | 10 | Build one MCP server, connect it to the agent, run 10 manual scenarios, refine loop contract, analyze 3 target roles, send 2 informational messages; weekly review and recovery block. |

## Week 6 - Project 3: Safety, Tracing, Agent Evals

| Date | Hours | Tasks |
|---|---:|---|
| Mon 31 Aug | 5 | Add context compaction/memory files and recovery from interrupted runs. |
| Tue 1 Sep | 5 | Add structured failure recovery: retry, re-plan, escalate, and stop. |
| Wed 2 Sep | 5 | Add prompt-injection defenses, tool-permission checks, and approval gates. |
| Thu 3 Sep | 5 | Add independent verifier for final environment state where it earns its cost. |
| Fri 4 Sep | 5 | Add tracing for inputs, outputs, tokens, latency, cost, tool calls, and state transitions. |
| Sat 5 Sep | 10 | Build 30-50 scenario eval tasks with injected failures, expected terminal states, and trace fixtures; if behind, ship 30 high-quality scenarios instead of 50 thin ones. |
| Sun 6 Sep | 10 | Run multi-trial eval; measure task success, policy violations, escalation precision/recall, steps, cost, latency; validate top Project 4 problem candidates; weekly review and recovery block. |

## Week 7 - Project 3 Finish + Project 4 Discovery

| Date | Hours | Tasks |
|---|---:|---|
| Mon 7 Sep | 5 | Add tool-selection and argument-correctness graders; compare against single-call/fixed-workflow baseline. |
| Tue 8 Sep | 5 | Try one framework held loosely; document what it helps and what it hides. |
| Wed 9 Sep | 5 | Finalize Project 3 README, architecture diagram, demo flow, trace viewer/readme notes, and eval report. |
| Thu 10 Sep | 5 | Interview or message potential Project 4 users; choose one narrow valuable problem. |
| Fri 11 Sep | 5 | Define Project 4 success metrics, user workflow, risks, v1 scope, and must-have AI capability. |
| Sat 12 Sep | 10 | Scaffold FastAPI backend, auth/per-user isolation plan, config, logging, tests, and minimal frontend. |
| Sun 13 Sep | 10 | Implement mocked end-to-end Project 4 workflow, streaming UX, core API route, and user validation plan; confirm first 2-3 test users; weekly review and recovery block. |

## Week 8 - Project 4 MVP + Applications Start

| Date | Hours | Tasks |
|---|---:|---|
| Mon 14 Sep | 5 | Integrate the first real AI capability: RAG, tool use, agent loop, or multimodal input as justified. |
| Tue 15 Sep | 5 | Implement per-user isolation and data model; add tests for access boundaries. |
| Wed 16 Sep | 5 | Add golden eval cases from product workflow and user examples. |
| Thu 17 Sep | 5 | Add offline eval runner in CI with cost, latency, and quality thresholds. |
| Fri 18 Sep | 5 | Create company target list and apply to first 5 roles using Project 1-3 evidence. |
| Sat 19 Sep | 10 | Conduct first live MVP test with 1-2 users; log friction; fix the highest-friction workflow issue. |
| Sun 20 Sep | 10 | Add feedback capture, convert user issues into eval cases, improve demo reliability, and weekly review/recovery block. |

## Week 9 - Project 4 Production Hardening + Deploy

| Date | Hours | Tasks |
|---|---:|---|
| Mon 21 Sep | 5 | Add rate-limit handling, retries, timeouts, fallback behavior, and graceful errors. |
| Tue 22 Sep | 5 | Add observability: traces, tokens, latency, cost, quality notes, and failure states. |
| Wed 23 Sep | 5 | Add cost controls: caching, routing, truncation budgets, and usage limits. |
| Thu 24 Sep | 5 | Add security checks: prompt injection tests, PII handling, output sanitization, approval gates. |
| Fri 25 Sep | 5 | Risk task: deploy to one platform and document rollback procedure; if deployment slips, cut nonessential frontend polish before cutting monitoring/evals; apply to 5 roles. |
| Sat 26 Sep | 10 | Run production smoke tests; test with 3-5 users; collect structured feedback and quality examples. |
| Sun 27 Sep | 10 | Fix production issues, update evals from feedback, write incident/postmortem if anything broke; weekly review/recovery block. |

## Week 10 - Project 4 Measurement + Portfolio Polish

| Date | Hours | Tasks |
|---|---:|---|
| Mon 28 Sep | 5 | Analyze user feedback and pick one measurable improvement to make. |
| Tue 29 Sep | 5 | Implement the improvement and add before/after eval cases. |
| Wed 30 Sep | 5 | Produce final Project 4 metrics: quality, latency, cost, failures, and user outcome. |
| Thu 1 Oct | 5 | Write Project 4 README, architecture diagram, eval report, production trade-offs, and demo script. |
| Fri 2 Oct | 5 | Apply to 5 roles; draft technical post 1 from a real project lesson. |
| Sat 3 Oct | 10 | Polish all four repo READMEs for a 3-minute hiring-manager scan; verify setup from a fresh clone. |
| Sun 4 Oct | 10 | Build/update one-page portfolio or GitHub profile README; rehearse capstone walkthrough; weekly review. |

## Week 11 - Job Readiness: CV, Writing, Interview Prep

| Date | Hours | Tasks |
|---|---:|---|
| Mon 5 Oct | 5 | Rewrite CV around shipped AI systems, eval numbers, latency/cost, and product outcomes. |
| Tue 6 Oct | 5 | Finish technical post 1 and outline technical post 2 or a strong project case study. |
| Wed 7 Oct | 5 | Make one small open-source touch: issue reproduction, docs fix, or focused PR. |
| Thu 8 Oct | 5 | Practice document Q&A/RAG system design: retrieval, evals, failure modes, cost, latency. |
| Fri 9 Oct | 5 | Apply to 5 roles; practice support agent/tool-use system design: permissions, state, escalation. |
| Sat 10 Oct | 10 | Mock interview day: one system design, one project deep dive, one behavioral session; revise weak answers. |
| Sun 11 Oct | 10 | Tighten behavioral stories, project trade-off stories, and portfolio evidence; weekly review. |

## Week 12 - Final Polish + Application Pipeline

| Date | Hours | Tasks |
|---|---:|---|
| Mon 12 Oct | 5 | Practice capstone deep dive: product choices, trade-offs, metrics, user feedback, what you would change. |
| Tue 13 Oct | 5 | Finish technical post 2 or replace it with a polished project case study. |
| Wed 14 Oct | 5 | Final portfolio QA: links, env examples, screenshots, demo scripts, eval reports, pinned repos. |
| Thu 15 Oct | 5 | Run fresh-clone setup checks for all showcase projects and patch any setup/documentation issues. |
| Fri 16 Oct | 5 | Apply to 5 roles; follow up on previous applications; refine target company list. |
| Sat 17 Oct | 10 | Full mock loop: resume screen, system design, Project 2 eval deep dive, Project 3 agent deep dive, Project 4 product demo. |
| Sun 18 Oct | 10 | Final roadmap review, portfolio freeze, application pipeline plan for the next 4 weeks, and recovery buffer for any unfinished critical item. |

## Weekly Review Template

Use this every Sunday at the end of the scheduled task.

```md
## Week __ Review

- Shipped:
- Measured:
- Biggest failure:
- Scope cut:
- Roadmap checkboxes changed:
- Next week's highest-risk task:
```
