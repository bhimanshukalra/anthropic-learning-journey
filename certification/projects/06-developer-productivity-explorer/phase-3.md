# Project 06 · Phase 3 — Long-session context ⭐

> **Companion to:** [`overview.md`](overview.md). Phases: [1](phase-1.md) · [2](phase-2.md) ·
> [3](phase-3.md) · [4](phase-4.md) · [5](phase-5.md). Build it yourself; the snippets are a reference.

**Phase 3 covers build step 4** (Domain **5.4** — large-codebase context). This is the heart of the
project: extended exploration **degrades** the model's grip on specifics, and you fight that with
external memory and delegation.

**Milestone:** a long session stays coherent (no "typical patterns" drift) via scratchpad + delegation
+ `/compact`, and crash recovery via a manifest works on resume.

**Phase 3 Definition of done**
- [ ] Scratchpad + subagent delegation + `/compact` keep a long session coherent.
- [ ] Crash recovery via a manifest works on resume.

---

## 0. Mental model — the tell-tale symptom

```
  long session → context fills with verbose discovery → model loses the specifics
  SYMPTOM: it starts citing "typical patterns" instead of the actual classes it found earlier
  FIX: move memory OUT of the context (scratchpads, manifests) + delegate + compact
```

The failure mode to recognize: when an agent that *had* found `RefundService.process()` starts
hand-waving about "a typical refund handler," its context has degraded. The fixes all share one idea —
**don't rely on the conversation as memory.**

---

## 1. Step 4 — Large-codebase context management (Domain 5.4) ⭐

- **Scratchpad files:** have the agent **write key findings to a file** and re-read them later. The
  durable file, not the chat history, is the source of truth — counteracts context degradation.
- **Subagent delegation:** spawn subagents for **narrow questions** ("find all test files," "trace the
  refund-flow dependencies") so the verbose work happens in *their* context; the main agent keeps only
  high-level coordination.
- **Summarize-before-next-phase:** condense phase-1 findings and inject that summary into phase-2's
  initial context, instead of carrying the whole transcript forward.
- **`/compact`:** reduce context when it fills with verbose discovery.
- **Crash recovery via manifests:** each agent **exports structured state** to a known location; on
  resume, the coordinator **loads the manifest and injects it** into prompts — so a crash doesn't lose
  the investigation.

```text
  .scratch/findings.md      ← agent writes specifics here, re-reads on demand
  .scratch/manifest.json    ← structured state for crash recovery / resume
```

---

## 2. Run & observe

- **Reproduce the drift:** run a long exploration without scratchpads and watch it shift from specific
  class names to vague "typical patterns" — that's the degradation symptom.
- **Fix it:** have the agent record findings to a scratchpad, delegate narrow lookups to subagents, and
  `/compact` periodically; confirm it keeps citing the *real* classes.
- **Crash recovery:** export a manifest mid-investigation, start a fresh session, load the manifest, and
  confirm the agent resumes from the recorded state instead of re-exploring.

---

## 3. Exam mapping

- **Large-codebase context** (EXAM-PREP §5.4): extended sessions degrade (the "typical patterns" tell);
  use **scratchpad files**, **subagent delegation** for verbose discovery, **structured state
  exports/manifests** for crash recovery, **summarize-before-next-phase**, and **`/compact`**.
- A bigger context window does **not** fix this — externalized, structured state does.

## 4. Close out the phase

- [ ] Tick the two Phase 3 boxes in [`overview.md`](overview.md).
- [ ] Notes one-liner: *"Long sessions degrade ('typical patterns' tell); fix with scratchpad files,
  subagent delegation, summarize-before-next-phase, `/compact`, and manifests for crash recovery."*
- [ ] Commit; run `/log`.

### What Phase 4 will add (preview)
Continuing and branching the work: `--resume` a named investigation, `fork_session` to explore two
approaches, resume-vs-fresh judgment, and the interview pattern for iterative refinement.
