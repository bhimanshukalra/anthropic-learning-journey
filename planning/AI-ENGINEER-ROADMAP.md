# AI Engineer Roadmap — Source of Truth

**Goal:** Be hireable as an industry-standard AI Engineer in ~12 weeks at 45 hrs/week.
**Profile:** Software engineer → AI Engineer (app layer, building on foundation models). Python-first. Anthropic cert = the foundation, not the destination.

**How to use this file:** Work top to bottom, tick items only when the "done means" bar is met. Projects are the spine — theory items exist to serve them. This file is the single source of truth; review it weekly and re-plan.

**Naming convention:** Portfolio projects are named **Project 1–Project 4** and may be abbreviated **P1–P4**. Python fluency study units are named **Python Batch 1–Python Batch 12**; avoid the old `P-1`/`P-4` shorthand so Python batches are not confused with portfolio projects.

**Sources (📚):** free-first; exactly one book is worth paying for (Phase 4). Prefer official docs over courses-about-docs. If a link has moved, search the title.

**What "industry standard" actually means (the bar hiring managers apply):**
you can take a fuzzy product ask, turn it into a working LLM feature, *prove* it works with evals, ship it behind an API, monitor its cost/quality in production, and explain every design trade-off you made. Not "knows about AI" — *ships reliable AI*.

**12-week execution rule:** eval/report quality beats feature completeness. Every project has a minimum viable evidence bar and a stretch bar; ship the minimum first, then add stretch features only if the evidence is already strong.

---

## Phase 0 — Prerequisites (Week 1, alongside Phase 1)

- [x] **Python working fluency** — comfortable with venvs/uv, type hints, dataclasses/Pydantic, async/await, pytest. *Done means: you write idiomatic Python without translating from another language in your head.*
- [x] **HTTP + API muscle memory** — requests, streaming responses (SSE), retries with backoff, rate-limit handling. Primary reference: `../docs/HTTP-API-MUSCLE-MEMORY.md`. *Done means: you can consume a streaming API with proper error handling from scratch.*
- [x] **Git hygiene for a public portfolio** — clean commits, README discipline, one repo per project.

📚 **Sources:** primary = **`../docs/PYTHON-FLUENCY.md`** — 12-batch tutor-then-quiz study plan worked through with Claude, with per-batch local drills and an exit test. Treat those as **Python Batch 1–Python Batch 12**, not portfolio project labels. Supplement = **Exercism Python track** (free, idiom-focused feedback) for extra reps. Reference docs pulled as needed: Pydantic, uv, pytest, official tutorial. Cap dedicated Python study at ~10h of teaching time — Project 1 teaches the rest.

## Phase 1 — Foundations (mostly in progress)

- [x] **Anthropic certification passed** (Architect Foundations) — ✅ 13 Jul 2026, 781/1000
- [x] **`../certification/AI-FOUNDATIONS.md` complete** — all batches taught AND quizzed
- [x] **3Blue1Brown Neural Networks ch. 1–8** watched
- [x] **Karpathy "Deep Dive into LLMs"** watched
- [ ] Can explain, cold, no notes: tokens → embeddings → attention → probability table → sampling; training vs. inference; why hallucination is structural. *Done means: you could teach it to another engineer for 30 minutes.*

📚 **Sources:** already curated in `../certification/AI-FOUNDATIONS.md` → Recommended Resources (3Blue1Brown, Karpathy, Jay Alammar, Anthropic Academy).

## Phase 2 — Core AI Engineering Skills

### 2.1 LLM APIs in depth (Claude API as primary)

- [x] Messages API: system prompts, multi-turn, temperature/max_tokens/stop reasons in real code
- [x] **Streaming** end-to-end (server → client)
- [x] **Structured output** — JSON mode / schema-enforced responses with Pydantic validation + retry-on-invalid
- [x] **Tool use / function calling** — define tools, handle tool-call loops, parallel tool calls
- [x] **Multimodal input** — images plus native PDF/document blocks; understand visual-token cost, page limits, Files API reuse, tables/charts, and when OCR/preprocessing is still needed
- [x] **Prompt caching** — what it caches, cache breakpoints, cost math
- [x] Batch API for offline workloads
- [x] Token counting + cost estimation utility you wrote yourself
- *Done means: you can build any API-level feature without reading examples.*

**Current progress (25 Jul 2026):** Completed the "Accessing Claude with the API" section plus the API overview and API usage primer. Upgraded the course demos in `../projects/building-with-the-claude-api/accessing-claude-with-the-api/` into learning artifacts for basic messages, system prompts, multi-turn message history, response text extraction, metadata, `max_tokens`, `temperature`, and clean interactive use. Commit: `2227e9d` (`Upgrade Claude API learning artifacts`).

**Current progress (26 Jul 2026):** Completed the Claude SDK streaming docs pass and upgraded `streaming.py` into a learning artifact using `stream.text_stream` for live chunks and `stream.get_final_message()` for final text, stop reason, and token usage metadata. Commit: `dcf2ecf` (`Upgrade Claude streaming artifact`). Also added `streaming_server.py` and `streaming_client.py` for end-to-end Claude → backend → client streaming over Server-Sent Events, plus `STREAMING-END-TO-END.md` as the implementation guide.

**Current progress (26 Jul 2026):** Implemented the structured-output learning artifact in `structured_data.py`: JSON schema via `output_config.format`, Pydantic validation, retry-on-invalid, deliberate invalid payload repair, attempt counting, and response metadata. Commit: `ac1180a` (`Upgrade Claude structured output artifact`). Verified with syntax and installed-SDK checks; live API run is deferred until an Anthropic API key is available.

**Current progress (26 Jul 2026):** Implemented `tool_use.py` for tool definitions, Pydantic-validated tool inputs, `tool_use` block detection, local function execution, matching `tool_result` blocks, loop limits, multiple tool results per turn, and tool-call metadata. Verified with syntax checks and local fake-key tool execution checks; live Claude run is deferred until an Anthropic API key is available.

**Current progress (26 Jul 2026):** Implemented `multimodal_input.py` for image URL/base64 inputs, PDF URL/base64 document blocks, Files API upload/reuse, and visual-token estimation using `ceil(width / 28) * ceil(height / 28)`. Verified with syntax checks, local fake-key import checks, and visual-token examples; live Claude run is deferred until an Anthropic API key is available.

**Current progress (26 Jul 2026):** Completed prompt-caching docs plus the two Anthropic prompt-caching blog posts. Implemented `prompt_caching.py` for automatic caching, explicit `cache_control` breakpoints, 5m vs 1h TTL selection, cache prewarming with `max_tokens=0`, and cache write/read usage metadata. Verified with syntax checks and installed-SDK/fake-key checks; live Claude run is deferred until an Anthropic API key is available.

**Current progress (26 Jul 2026):** Completed token-counting and batch-processing docs. Implemented `token_counting.py` for `messages.count_tokens`, system/tool/image request sizing, context-budget warnings, and simple cost estimation. Implemented `batch_processing.py` for batch creation, status retrieval, polling, and per-`custom_id` result handling. Verified with syntax checks and installed-SDK/fake-key checks; live Claude runs are deferred until an Anthropic API key is available.

**Phase 2.1 status (26 Jul 2026):** Complete under the current no-API-key constraint. All API-level learning artifacts are implemented and locally verified; once the Anthropic API key is available, run the scripts against the live API as a final smoke test.

📚 **Sources and study flow:** use the official course as the spine, docs while coding, and cookbook examples only after you have tried the implementation yourself.

- **Primary course:** Anthropic Academy / Claude resources — **"Building with the Claude API"** (`https://claude.com/resources/courses`). Watch one section, then immediately build the matching script.
- **Core docs while coding:**
  - API overview: `https://platform.claude.com/docs/en/api/overview`
  - API usage primer: `https://platform.claude.com/docs/en/claude_api_primer`
  - Streaming messages: `https://platform.claude.com/docs/en/build-with-claude/streaming`
  - Structured outputs: `https://platform.claude.com/docs/en/build-with-claude/structured-outputs`
  - Tool use: `https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview`
  - PDF support: `https://platform.claude.com/docs/en/build-with-claude/pdf-support`
  - Files API: `https://platform.claude.com/docs/en/build-with-claude/files`
  - Token counting: `https://platform.claude.com/docs/en/build-with-claude/token-counting`
  - Batch processing: `https://platform.claude.com/docs/en/build-with-claude/batch-processing`
- **Prompt caching:** docs/blog plus the practical Claude Code writeup:
  - `https://claude.com/blog/prompt-caching`
  - `https://claude.com/blog/lessons-from-building-claude-code-prompt-caching-is-everything`
- **Worked examples:** `anthropics/anthropic-cookbook` on GitHub (`https://github.com/anthropics/anthropic-cookbook`). Use it as a comparison/reference pass after your own scripts exist: check whether official examples handle edge cases, message shapes, retries, or result parsing differently, and copy only patterns you understand.
- **Script sequence:** current learning artifacts live in `../projects/building-with-the-claude-api/accessing-claude-with-the-api/`: `claude_helpers.py`, `math_tutor.py`, `user_assistant_flow.py`, `prompt_input_provide_response.py`, `streaming.py`, `streaming_server.py`, `streaming_client.py`, `structured_data.py`, `tool_use.py`, `multimodal_input.py`, `prompt_caching.py`, `token_counting.py`, and `batch_processing.py`. Keep each script as a small artifact with clean input, logged output/metadata where available, local validation or error handling, and one deliberate edge/failure case.

### 2.2 Prompt engineering (the real, unglamorous version)

- [x] System prompt design: role, constraints, output contract
- [x] Few-shot examples — when they help, how many, ordering effects
- [x] Chain-of-thought / extended thinking — when to pay the token cost
- [x] Structuring long prompts (XML tags, document placement, "lost in the middle" mitigation)
- [x] Defensive prompting: handling irrelevant/adversarial input
- [x] **Prompts as versioned artifacts** — stored in repo, diffed, tested like code
- *Done means: you iterate on prompts against an eval set, never by vibes.*

**Current progress (26 Jul 2026):** Completed Phase 2.2 study flow: Anthropic prompt-engineering interactive tutorial, matching Prompt Engineering docs, Console prompt improver pass on own prompts, before/after prompt review, and a small prompt test set with expected behavior and pass/fail notes.

📚 **Sources:** primary = **anthropics/prompt-eng-interactive-tutorial** (GitHub) — hands-on, 9 chapters, the single best prompt-engineering resource anywhere. Reference = Anthropic docs **Prompt Engineering** section (read every page once — it's short). Then use the **Claude Console prompt improver** on your own prompts and study what it changes.

### 2.3 RAG (retrieval-augmented generation)

- [ ] Embeddings for retrieval (similarity search — you already know the geometry)
- [ ] **Multimodal document ingestion** — text + scanned pages + tables/charts/images; preserve page, section, layout, and source metadata through the pipeline
- [ ] **Chunking strategies** — size/overlap trade-offs, structure-aware + contextual chunking; why naive splitting destroys meaning
- [ ] Vector DB hands-on (one of: pgvector, Qdrant, Chroma) — index, filter, hybrid queries
- [ ] **Hybrid search** — BM25 + vector, why keyword search still matters
- [ ] Reranking (cross-encoder / rerank API) and when it pays for itself
- [ ] Citations / grounding — making answers traceable to sources
- [ ] **Agentic retrieval, as an ablation** — compare fixed retrieve→answer against classify/rewrite/decompose→retrieve→inspect evidence→retrieve again; keep the agentic path only where evals justify its cost/latency
- [ ] **RAG evaluation** — retrieval metrics (recall@k plus MRR/nDCG where useful) separate from answer correctness, groundedness, citation accuracy, and abstention
- *Done means: you can diagnose "bad answer" into retrieval failure vs. generation failure in minutes.*

📚 **Sources:**

- **Multimodal/PDF input:** Anthropic docs — [Vision](https://platform.claude.com/docs/en/build-with-claude/vision) and [PDF support](https://docs.claude.com/en/docs/build-with-claude/pdf-support). Use these for image/document block shapes, PDF limits, Files API reuse, visual-token cost, and when PDF visual understanding matters.
- **Contextual retrieval:** Anthropic engineering — [Introducing Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval). Read this for contextual embeddings, contextual BM25, and why naive chunks lose retrieval-critical context.
- **Chunking strategies:** Greg Kamradt / Full Stack Retrieval — [5 Levels of Text Splitting notebook](https://github.com/FullStackRetrieval-com/RetrievalTutorials/blob/main/tutorials/LevelsOfTextSplitting/5_Levels_Of_Text_Splitting.ipynb) and [ChunkViz](https://www.chunkviz.com/). Use these to compare fixed-size, recursive, document-aware, semantic, and agentic chunking.
- **RAG overview and search concepts:** Pinecone Learning Center — [Retrieval-Augmented Generation](https://www.pinecone.io/learn/retrieval-augmented-generation/), [Semantic search](https://www.pinecone.io/learn/search-with-pinecone/), [Hybrid search intro](https://www.pinecone.io/learn/hybrid-search-intro/), and [Rerankers and two-stage retrieval](https://www.pinecone.io/learn/series/rag/rerankers/). Vendor-hosted, but useful for BM25 vs vector, hybrid retrieval, reranking, and retrieval architecture concepts.
- **Hybrid/rerank implementation reference:** Pinecone docs — [Hybrid search](https://docs.pinecone.io/guides/search/hybrid-search) and [Rerank results](https://docs.pinecone.io/guides/search/rerank-results). Use these as implementation references, not as a requirement to use Pinecone.
- **Vector DB hands-on:** [pgvector README](https://github.com/pgvector/pgvector/blob/master/README.md). Use pgvector because it keeps vector search inside Postgres, which matches your existing backend/SQL strengths.
- **Hands-on RAG/eval course:** DeepLearning.AI — [Building and Evaluating Advanced RAG](https://www.deeplearning.ai/courses/building-evaluating-advanced-rag). Use this for sentence-window retrieval, auto-merging retrieval, and the RAG triad: context relevance, groundedness, and answer relevance.
- **Corrective essays:** Jason Liu — [What is Retrieval-Augmented Generation?](https://jxnl.co/writing/2024/11/07/what-is-retrieval-augmented-generation/) and [Systematically Improving Your RAG](https://jxnl.github.io/blog/writing/2024/05/22/systematically-improving-your-rag/). Read these to avoid the common mistake of treating RAG as "just embedding search."

### 2.4 Agents & orchestration

- [ ] Anthropic's "Building Effective Agents" patterns: prompt chaining, routing, parallelisation, orchestrator-workers, evaluator-optimizer — and **when NOT to build an agent**
- [ ] Tool-using agent loop from scratch (no framework) — you must understand the bare loop first
- [ ] **MCP (Model Context Protocol)** — build one MCP server, connect it to Claude
- [ ] Context management for long-running agents (compaction, memory files)
- [ ] **Loop/harness engineering** — trigger → load goal/state → act → observe → verify → retry/re-plan/escalate → named terminal state; persist traces and durable state
- [ ] Bounded autonomy — scoped permissions, sandboxing, time/step/cost budgets, idempotent actions, and human approval gates for consequential operations
- [ ] Multi-agent patterns: subagents, handoffs — and their failure modes
- [ ] One framework, held loosely (e.g. Claude Agent SDK) — after the from-scratch version
- *Done means: you can argue, per use case, workflow vs. agent; build a bounded loop that proves completion from environment state rather than the model saying "done"; and defend the boring choice.*

📚 **Sources:**

- **Agent/workflow canon:** Anthropic engineering — [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents). Read this twice; it is the main source for prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer, and the workflow-vs-agent distinction.
- **Pattern implementations:** Anthropic Cookbook — [Agents patterns](https://github.com/anthropics/anthropic-cookbook/tree/main/patterns/agents) and the Claude Cookbook [Orchestrator-workers workflow](https://platform.claude.com/cookbook/patterns-agents-orchestrator-workers). Use these after reading the essay so you can map each pattern to runnable code.
- **Long-running agent harnesses:** Anthropic engineering — [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) and [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps). Use these for trigger/state/act/observe loops, compaction, handoff artifacts, verification, and long-horizon failure modes.
- **Context management:** Anthropic engineering — [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents). Read this for context curation, just-in-time loading, memory files, and why agent quality depends on what enters the context window.
- **MCP fundamentals:** Anthropic docs — [Model Context Protocol](https://docs.anthropic.com/en/docs/mcp) and official MCP docs — [Build an MCP server](https://modelcontextprotocol.io/docs/develop/build-server). Build the weather-server tutorial so MCP becomes concrete rather than just a protocol description.
- **MCP course:** Anthropic Academy — [Introduction to Model Context Protocol](https://www.classcentral.com/course/anthropic-academy-introduction-to-model-context-protocol-536163). Use this to reinforce server/client concepts, tools, resources, prompts, and inspector-driven testing.
- **Framework, only after the bare loop:** Claude Agent SDK docs — [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview) and [Quickstart](https://code.claude.com/docs/en/agent-sdk/quickstart). Use these after you have implemented a no-framework agent loop once.

### 2.5 Evals — the #1 differentiator on the job market

- [ ] Build a **golden dataset** (inputs + expected properties) for a real task
- [ ] Programmatic assertions (exact match, schema-valid, contains-citation, latency budget)
- [ ] **LLM-as-judge** — rubric design, its biases (position, verbosity, self-preference), calibrating against human labels
- [ ] Regression harness: every prompt/model change runs the eval suite (CI)
- [ ] A/B comparing models & prompts on cost/quality/latency — with a written recommendation
- [ ] **Agent evals** — scenario tasks, multiple trials, complete traces/trajectories, tool-behavior graders, and final environment-state grading (not self-reported success)
- *Done means: "how do you know it works?" always has a quantified answer. Most candidates fail here; this is your edge.*

📚 **Sources:**

- **Evaluation discipline:** Hamel Husain — [Your AI Product Needs Evals](https://hamel.dev/blog/posts/evals/index.html). Treat this as the main essay for building task-specific eval systems, looking at traces, debugging failures, and avoiding vibe-based iteration.
- **LLM-as-judge:** Hamel Husain — [Creating a LLM-as-a-Judge That Drives Business Results](https://hamel.dev/llm-judge/). Use this for rubric design, human alignment, critique shadowing, and judge error analysis.
- **Claude eval basics:** Anthropic docs — [Define success criteria and build evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests). Use this for measurable success criteria, exact/programmatic checks, LLM-based grading, and eval design principles.
- **Agent evals:** Anthropic engineering — [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents). Use this for multi-turn trajectories, environment-state grading, tool-behavior grading, and agent-specific failure modes.
- **Eval tooling:** promptfoo docs — [Intro](https://www.promptfoo.dev/docs/intro/). Use this for config-driven prompt/model regression tests that can run locally and in CI.

### 2.6 Production concerns

- [ ] **Observability** — tracing every LLM call (inputs, outputs, tokens, latency, cost); one tool hands-on (e.g. Langfuse)
- [ ] **LLMOps / AI production operations** — prompt/model/version tracking, eval datasets as regression assets, trace review, feedback-to-eval loops, release/rollback procedure, and quality/cost monitoring
- [ ] Cost engineering: caching, model routing (small model when possible), truncation budgets
- [ ] Latency engineering: streaming UX, parallel calls, speculative patterns
- [ ] Failure handling: retries, fallback models, graceful degradation, timeout budgets
- [ ] **Security:** prompt injection (direct + indirect), tool-permission scoping, PII handling, output sanitisation
- [ ] Rate limits & quotas at scale
- *Done means: your capstone survives a hostile demo — malicious input, API outage, cost audit — and you can explain how you would detect regressions after release.*

📚 **Sources:**

- **Observability:** Langfuse docs — [Get started with tracing](https://langfuse.com/docs/observability/get-started). Use this to instrument LLM calls, inspect traces, and track latency, tokens, cost, inputs, outputs, and metadata.
- **Self-hosting:** Langfuse docs — [Self-hosting](https://langfuse.com/self-hosting). Use this if you want a free/local-ish observability setup for P3/P4 instead of relying only on a hosted dashboard.
- **Cost engineering:** Anthropic docs — [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) and [Models overview](https://platform.claude.com/docs/en/about-claude/models/overview). Use these for caching breakpoints, model routing, context-window choices, latency/cost trade-offs, and your own routing math.
- **Security baseline:** Simon Willison — [Prompt injection writing](https://simonwillison.net/tags/prompt-injection/), especially [You can't solve AI security problems with more AI](https://simonwillison.net/2022/Sep/17/prompt-injection-more-ai/). Use this to understand direct and indirect prompt injection as a structural product risk.
- **Security checklist:** OWASP — [Top 10 for LLMs and Gen AI Apps](https://genai.owasp.org/llm-top-10/). Use this for interview-citable risk categories: prompt injection, sensitive information disclosure, supply chain, improper output handling, excessive agency, vector/embedding weaknesses, and unbounded consumption.

**Boundary:** learn LLMOps for shipped AI products. Do not detour into full training-centric MLOps unless a target job explicitly requires it; model registries, feature stores, distributed training pipelines, and data-labeling platforms are awareness topics for this track, not build requirements.

### 2.7 Fine-tuning awareness (breadth, not depth)

- [ ] When fine-tuning beats prompting/RAG (style, format, latency) and when it loses (knowledge injection — usually)
- [ ] What LoRA is conceptually; what an open-weights model is; run one locally once (Ollama)
- *Done means: you can kill a bad "let's fine-tune" proposal in a meeting with reasons.*

📚 **Sources:**

- **Fine-tuning/RLHF intuition:** Andrej Karpathy — [Deep Dive into LLMs like ChatGPT](https://www.youtube.com/watch?v=7xTGNNLPyMI). Rewatch the fine-tuning, supervised fine-tuning, preference tuning, and RLHF sections for awareness-level understanding.
- **Fine-tuning judgment:** Hamel Husain — [Is Fine-Tuning Still Valuable?](https://hamel.dev/blog/posts/fine-tuning/index.html). Use this to understand when fine-tuning is worth considering and why data/evals matter more than the training button.
- **Local model hands-on:** Ollama docs — [Quickstart](https://docs.ollama.com/quickstart). Spend ~30 minutes pulling a small model, chatting locally, and hitting the local API once.

---

## Phase 3 — Portfolio Projects (the spine)

> **This list is frozen at four portfolio projects.** Multimodal RAG, agentic RAG, and loop engineering are requirements/experiments inside these projects, not extra portfolio repos. Every project ships public with a 3-minute README, architecture diagram, reproducible setup, and written eval report; Project 3/Project 4 also get a live demo. Quality bar: a hiring manager sees a useful system, quantified evidence, and explicit trade-offs — not a collection of hot labels.

- [ ] **Project 1 (P1) — Multimodal structured-document processor** *(~1–2 weeks)*
  A CLI-first document-intelligence system that accepts text, scanned images, and PDFs (including tables/charts) and returns validated Pydantic models. Nullable fields + explicit abstention, targeted retry-on-invalid, streaming progress, token/latency/cost logging, and an optional thin FastAPI endpoint.
  **Eval bar:** golden set of 30–50 representative documents; schema-valid rate, per-field accuracy/precision/recall, missing-field hallucination rate, table/chart extraction accuracy, cost + latency per document; regression tests in CI.
  *Proves: multimodal API fundamentals, structured output, validation, measurement, engineering hygiene.*
  📚 **Sources:**

  - **Multimodal input:** Anthropic docs — [Vision](https://platform.claude.com/docs/en/build-with-claude/vision) and [PDF support](https://platform.claude.com/docs/en/build-with-claude/pdf-support). Use these for image/PDF inputs, page limits, visual-token cost, and document blocks.
  - **Structured extraction:** Anthropic docs — [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs). Use this for schema-enforced responses, JSON outputs, and validation-oriented extraction.
  - **Tooling patterns:** Anthropic docs — [Tool use overview](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview) and [Anthropic Cookbook](https://github.com/anthropics/claude-cookbooks). Use these for tool-call loops, local function execution, and multimodal examples you can compare against your own implementation.

- [ ] **Project 2 (P2) — Production multimodal RAG with a real eval harness** *(~2–3 weeks)*
  Q&A over a real, messy corpus containing text plus PDFs with tables/images. Preserve page/section/layout metadata; structure-aware + contextual chunking; pgvector, metadata filters, BM25 + vector hybrid retrieval, reranking, page-level citations, ingestion versioning, and caching.
  **Agentic-RAG ablation:** compare fixed retrieve→answer against classify/rewrite/decompose→retrieve→inspect evidence→retrieve again. Keep the agentic path only for query classes where measured quality gain justifies cost/latency.
  **Eval bar:** golden set ≥50–100 questions including unanswerables; retrieval recall@k (plus MRR/nDCG where useful), answer correctness, groundedness, citation accuracy, abstention, cost + latency. Publish chunk-size/contextualization, reranking, top-k, and agentic-vs-fixed experiments.
  *Proves: RAG depth + eval discipline — the highest-signal combination.*
  📚 **Sources:**

  - **Contextual retrieval:** Anthropic engineering — [Introducing Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval). Use this for contextual embeddings, contextual BM25, and the case against naive chunking.
  - **Vector DB:** pgvector — [README](https://github.com/pgvector/pgvector/blob/master/README.md). Use this for Postgres-native vector storage, indexing, similarity search, and filters.
  - **Eval harness:** promptfoo docs — [Intro](https://www.promptfoo.dev/docs/intro/). Use this for repeatable RAG regression tests and CI-friendly prompt/model comparison.
  - **Report model:** Hamel Husain — [Your AI Product Needs Evals](https://hamel.dev/blog/posts/evals/index.html) and [AI Evals notes](https://hamel.dev/notes/llm/evals/). Use these as the writing model for your eval report and failure-analysis workflow.

- [ ] **Project 3 (P3) — Bounded tool-using agent + loop-engineering system** *(~2–3 weeks)*
  An agent that performs real recurring multi-step work (support resolution, evidence-backed research, data-quality investigation, issue triage/maintenance). Build the bare loop first; ≥3 scoped tools, one MCP server, retrieval as an optional tool, explicit durable state, idempotent actions, context compaction/memory, full tracing, structured failure recovery, injection defences, and only then one framework held loosely.
  **Loop contract:** trigger → load goal/state → plan/select action → call tool → observe real environment → verify progress → retry/re-plan/escalate → named terminal state → persist trace/memory. Enforce time/step/cost budgets, sandbox/permissions, and human approval for consequential actions; use an independent verifier where it earns its cost.
  **Eval bar:** ≥30–50 scenario tasks with multiple trials; final environment-state/task success, tool selection + argument correctness, policy-violation rate, injected-failure recovery, escalation precision/recall, cost/latency/steps, and comparison with a single call or fixed workflow. CI regression suite.
  *Proves: agents, MCP, context/harness engineering, bounded autonomy, agent evals, production judgment.*
  📚 **Sources:**

  - **Agent/workflow canon:** Anthropic engineering — [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents). Use this to decide when a fixed workflow is enough and when agentic control flow is justified.
  - **Harness and context engineering:** Anthropic engineering — [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps), and [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents). Use these for durable state, compaction, traces, verification, and long-horizon reliability.
  - **Agent evals:** Anthropic engineering — [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents). Use this for trajectory grading, final-state grading, and repeated scenario trials.
  - **MCP:** Model Context Protocol docs — [Build an MCP server](https://modelcontextprotocol.io/docs/develop/build-server). Build one scoped MCP server for the project.
  - **Observability:** Langfuse docs — [Get started with tracing](https://langfuse.com/docs/observability/get-started). Use this for full traces of agent steps, tool calls, costs, and failures.

- [ ] **Project 4 (P4) — Capstone: deployed AI product with real users** *(~3–4 weeks)*
  Solve one narrow, valuable problem for ≥5 users. FastAPI backend + usable minimal frontend, auth/per-user isolation, streaming UX, and at least one justified multimodal capability. Compose RAG/tools/agents only where the product needs them — this is a judgment test, not a feature checklist.
  **Production bar:** offline evals in CI; traces + quality monitoring; user feedback becomes eval cases; cost/latency budgets, rate-limit handling, routing/fallback, injection tests, PII/audit handling, approval gates for consequential actions, deployment + rollback procedure, and one real incident postmortem. Show a measured improvement driven by users.
  *Proves: end-to-end product ownership — this is the interview centrepiece.*
  📚 **Sources:**

  - **API layer:** FastAPI docs — [FastAPI](https://fastapi.tiangolo.com/). Use this for backend routes, request/response models, auth integration points, streaming endpoints, and deployment shape.
  - **Deployment options:** [Railway FastAPI guide](https://docs.railway.com/guides/fastapi), [Render FastAPI guide](https://render.com/docs/deploy-fastapi), and [Fly.io FastAPI guide](https://fly.io/docs/python/frameworks/fastapi/). Pick one deploy target and go deep enough to handle env vars, logs, rollbacks, and production settings.
  - **Production AI stack:** Reuse Phase 2 sources for RAG, agents, evals, observability, security, cost routing, prompt caching, and multimodal inputs. P4 is about composing the pieces into a product, not adding new theory.

### Eval progression across the four projects

| Project | What the eval proves |
|---|---|
| P1 | Field/output correctness and abstention |
| P2 | Retrieval, grounding, citations, and answer correctness |
| P3 | Trajectory/tool behavior, safety, recovery, and final environment state |
| P4 | Product quality, online behavior, users, reliability, and economics |

### Topic boundary — required, conditional, or deliberately deferred

| Topic | Decision |
|---|---|
| Multimodal document processing | **Required in P1** |
| Multimodal document RAG | **Required in P2** |
| Agentic RAG | **Measured P2 ablation, not a project** |
| Context engineering + memory/compaction | **Required in P3** |
| Loop/harness engineering | **Required in P3, not a project** |
| Agent evals + trace grading | **Required in P3** |
| Human approval, MCP, tool security | **Required in P3/P4** |
| Routing, caching, cost control | **Required in P4** |
| Computer/browser use | Conditional — include only when the chosen use case needs UI interaction |
| Voice/realtime agents | Optional specialization — only if target roles demand it |
| GraphRAG/knowledge graphs | Conditional — only when corpus relationships make vector/hybrid retrieval inadequate |
| Fine-tuning/RFT | Awareness + at most one measured experiment; not a portfolio project |
| Local/open-weight model | One breadth exercise; not a portfolio project |
| Multi-agent swarms | Do not add; use multiple agents only when evals prove an advantage |
| Image/video generation | Outside the general application-layer target unless the product specifically needs it |

### Scope gates for 12-week execution

| Project | Minimum viable evidence bar | Stretch only after minimum is strong |
|---|---|---|
| Project 1 | One document family, one schema family, 30 representative documents, structured output, validation/retry, cost/latency logging, field-level eval report | More document families, broader table/chart coverage, FastAPI endpoint |
| Project 2 | Text/PDF RAG, metadata-preserving ingestion, hybrid retrieval, citations, 50+ question eval with unanswerables, retrieval vs. generation failure analysis | Full multimodal table/image handling, contextual chunking at scale, reranking sweeps, agentic-RAG ablation |
| Project 3 | Bare bounded loop, 3 scoped tools, one MCP server, durable state, traces, 30 scenario evals, final-state grading | Framework comparison, richer trace viewer, retrieval as an optional tool, independent verifier on more cases |
| Project 4 | One narrow user problem, 5 users contacted, usable deployed workflow, offline evals, monitoring, user-feedback-to-eval loop, measured improvement | More integrations, richer frontend, advanced routing/fallback, second product workflow |

---

## Phase 4 — Job Readiness (final 3–4 weeks, overlaps P4)

- [ ] **Portfolio polish** — 4 repos with excellent READMEs; pin them; one-page portfolio site or GitHub profile README
- [ ] **Write 2–3 technical posts** from real project pain (e.g. "what my RAG evals caught that vibes missed") — writing is the cheapest credibility multiplier
- [ ] **1–2 open-source touches** in the AI tooling you used (issue → small PR)
- [ ] **CV rewritten** around shipped AI work with numbers (recall@k improvements, cost reductions, latency budgets)
- [ ] **LLM system design interview prep** — practise aloud: "design a support bot / document Q&A / agent platform"; cost-quality-latency trade-offs, evals, failure modes
- [ ] **Behavioural stories** mapped to projects (debugging story, trade-off story, scope-cut story)
- [ ] **Pipeline discipline** — target list of companies, 5+ applications/week once P3 is live, don't wait for "ready"
- [ ] **Role targeting** — collect 20 target job posts, extract repeated requirements, and tune Project 2-Project 4 choices toward the roles you actually want. *Done means: your portfolio bullets map directly to recurring job-description language.*

📚 **Sources:**

- **System-design depth:** Chip Huyen — [AI Engineering](https://www.oreilly.com/library/view/ai-engineering/9781098166298/). This is the one paid book worth using during Phase 3/4; read it alongside the portfolio projects, not before them.
- **Field context:** swyx / Latent Space — [The Rise of the AI Engineer](https://www.latent.space/p/ai-engineer). Use this to understand the role boundary: application-layer AI engineering, product evals, and shipping with models you did not train.
- **Staying current:** Latent Space — [About](https://www.latent.space/about) and [Podcast](https://www.latent.space/podcast). Use this lightly for field awareness, not as a reason to delay building.
- **Writing model:** Simon Willison — [simonwillison.net](https://simonwillison.net/) and Hamel Husain — [hamel.dev](https://hamel.dev/). Study how they write concrete posts from real engineering work: problem, evidence, trade-offs, failures, and reproducible details.

---

## Weekly cadence (45 hrs)

| Hours | Activity |
|---|---|
| ~25 | Building (current project) |
| ~8 | Evals, debugging, and measurement |
| ~5 | Theory pulled by the project (just-in-time, not ahead of need) |
| ~4 | README/demo/writing/portfolio polish |
| ~3 | Review this file, tick, re-plan; from week 8: applications |

**Rough calendar:** Week 1 Phase 0/1 close-out + Project 1 setup · Weeks 2–3 Project 1 + Project 2 foundation · Weeks 4–5 Project 2 · Weeks 5–7 Project 3 · Weeks 7–10 Project 4 · Weeks 8–12 Phase 4/job readiness running in parallel.

**Daily schedule:** see `AI-ENGINEER-SCHEDULE.md` for the 12-week plan ending Sunday, 18 October 2026.

---

## Anti-goals (deliberately NOT on this list)

- Training models from scratch, hand-deriving backprop, CUDA — ML-engineer track, not yours
- Framework collecting (LangChain + LlamaIndex + CrewAI + ...) — one bare-loop understanding beats five wrappers
- Kaggle/classical-ML detours — different job
- Course hoarding — after Phase 1, theory is pulled by projects, never stockpiled
