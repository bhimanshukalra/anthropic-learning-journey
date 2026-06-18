# Project 01 · Phase 4 — Implementation Guide: *Judgment & context* ⭐

> **Companion to:** [`overview.md`](overview.md) (overview),
> [`-phase-1.md`](phase-1.md) (runnable agent),
> [`-phase-2.md`](phase-2.md) (structured errors + the gate), and
> [`-phase-3.md`](phase-3.md) (hooks). This is the in-depth walkthrough for
> **Phase 4 only** — build it yourself; the snippets are a reference to compare against.

**Phase 4 covers build steps 6–7** (Domains **5.2** Escalation, **1.4** Decomposition/Handoff, **5.1**
Context preservation). It's the **last *build* phase** — after this, Phase 5 is just writing up the
four "Be able to answer" questions.

The mental shift from Phases 2–3: those were about things you can **guarantee in code** (gates,
hooks). Phase 4 is about the things you **can't** hard-code — *when to escalate* is a judgment call,
so it's done with **explicit criteria + few-shot** in the prompt. But the two *outputs* of that
judgment — the **handoff summary** and the **case-facts block** — are structured data you control.

**Milestone:** a multi-issue message is decomposed and synthesized into one reply; an escalation emits
a **self-contained structured handoff**; and the key numbers survive a long, summarized conversation.

**Phase 4 Definition of done**
- [ ] Escalation happens on **request / policy-gap / no-progress** only; a **multi-match asks for an
  identifier** (never guesses).
- [ ] Escalation produces a **structured handoff** summary (customer ID, root cause, amount, action).
- [ ] A persistent **"case facts"** block survives long multi-turn conversations.

There's nothing Phase 4 defers — it's the final build phase. (Phase 5 = write up the answers.)

---

## 0. Mental model — judgment in the prompt, state in the harness

```
        ┌──────────────────────────────────────────────────────────────┐
        │  SYSTEM prompt  =  role  +  escalation CRITERIA + few-shot     │  ← step 6 (judgment)
        │                                                                │
        │  every turn:  system = SYSTEM + CASE-FACTS block (at the top)  │  ← step 7c (context)
        │                          ▲                                     │
        │                          │ updated after each tool result      │
        │  tool loop ── decompose multi-concern → handle each → synth ── │  ← step 7a
        │                                                                │
        │  escalate_to_human(customer_id, root_cause, action, amount)    │  ← step 7b (handoff)
        └──────────────────────────────────────────────────────────────┘
```

Three ideas, three homes:

- **Escalation calibration (6)** → lives in the **system prompt** (criteria + few-shot). It's a
  *probabilistic* judgment, so it belongs in the prompt — the opposite of the Phase 2 gate. (Don't
  confuse the two: the $500 refund cap is a hard rule → hook; "is this worth escalating?" is judgment
  → prompt.)
- **Decomposition + handoff (7a/7b)** → the **loop** already lets the model handle several concerns;
  the **handoff tool** carries structured fields because the human **can't see the transcript**.
- **Case facts (7c)** → **harness state** injected into every prompt so progressive summarization
  can't lose the numbers.

---

## 1. Step 6 — Escalation calibration ⭐ (Domain 5.2)

The exam's favorite escalation traps: agents that escalate because a case is **"complex"**, because the
customer **"sounds angry"** (sentiment), or because the model's **self-reported confidence** is low.
All three are wrong. Encode the *real* triggers as **explicit criteria with few-shot examples** in the
system prompt.

```python
# core/agent.py — replace the one-line SYSTEM with calibrated criteria + few-shot
SYSTEM = """You are a customer-support resolution agent. Use the tools to look up customers and
orders and resolve the request. Pick the single most appropriate tool for each step.

ESCALATE TO A HUMAN only when one of these is true:
  1. The customer EXPLICITLY asks for a human — escalate immediately, do NOT investigate first.
  2. POLICY GAP / SILENCE — the policy does not cover the situation (e.g. a competitor price-match
     when policy only addresses our own pricing). Don't invent a policy.
  3. INABILITY TO PROGRESS — you are blocked and no tool or question can move the case forward.

Do NOT escalate because a case seems COMPLEX, because the customer sounds FRUSTRATED, or because you
feel UNSURE — none of those mean a human is needed. Resolve what you can.

If get_customer returns MORE THAN ONE match, do NOT guess — ASK the customer for another identifier
(order number, full name) to disambiguate.

When you do escalate, call escalate_to_human with a SELF-CONTAINED summary — the human cannot see this
conversation.

Examples:
- "This is broken and I want my money back, here's a photo" → damage replacement is covered → RESOLVE
  (process the return/refund); do NOT escalate.
- "Just connect me to a person." → explicit request → ESCALATE immediately.
- "Will you match Acme's lower price?" and policy only covers our own pricing → POLICY GAP → ESCALATE.
- "I'm furious this took so long!" with an otherwise normal refund → frustration is NOT a trigger →
  RESOLVE the refund.
"""
```

> **Why few-shot, not just rules?** Detailed instructions still leave ambiguous cases to chance;
> 2–4 examples that show *why one choice over the other* (especially the "frustrated but resolvable"
> and "explicit request" pair) are the most effective lever (EXAM-PREP §4.2). The frustration example
> is deliberately a near-miss so the model learns sentiment ≠ escalation.

The **multi-match → ask** rule pairs with the Phase 2 latch: `get_customer` with `count > 1` never
verifies (so the gate still blocks refunds), *and* the prompt tells the agent to ask for another
identifier rather than pick one.

---

## 2. Step 7a — Multi-concern decomposition (Domain 1.4)

One customer message often carries several issues ("my order's late **and** I was double-charged
**and** I want to update my email"). The agent should **split** them, handle each with the right
tool(s), and **synthesize one** coherent reply — not tackle only the first or send three fragmented
answers. Your agentic loop already supports this (multiple tool calls across turns); reinforce it in
the prompt:

```python
# append to SYSTEM
"""
When a message contains MULTIPLE concerns, address EACH one (use the right tool per concern) and then
combine the outcomes into a SINGLE clear reply. Do not drop a concern or answer only the first.
"""
```

You verify this behaviorally in §5 — there's no new code, it's a prompt + observation step.

---

## 3. Step 7b — Structured handoff (Domain 1.4)

Today's `escalate_to_human(reason, summary)` leans on a free-text blob. Because **the human can't see
the transcript**, make the handoff carry the facts they need as **structured fields**:

```python
# mcp_server.py — give escalate_to_human a structured, self-contained shape
@mcp.tool()
def escalate_to_human(customer_id: str, root_cause: str, recommended_action: str,
                      refund_amount: float | None = None) -> dict:
    """Hand the case to a human with a SELF-CONTAINED handoff (the human cannot see the chat).
    Provide: who (customer_id), WHY (root_cause), what to do (recommended_action), and any amount."""
    return {"escalated": True, "handoff": {
        "customer_id": customer_id,
        "root_cause": root_cause,
        "recommended_action": recommended_action,
        "refund_amount": refund_amount,
    }}
```

> ⚠️ **Cross-phase dependency.** Phase 3's `hook_refund_cap` *redirects* an over-limit refund to
> `escalate_to_human` — it currently passes `{"reason", "summary"}`. When you change the tool's
> signature here, **update that redirect** to emit the new fields (it has `agent` in scope, so it can
> read `agent.verified_customer_id`):
> ```python
> "redirect": ("escalate_to_human", {
>     "customer_id": agent.verified_customer_id,
>     "root_cause": "refund_over_limit",
>     "recommended_action": "Review and approve/deny the refund manually.",
>     "refund_amount": float(tool_input.get("amount", 0)),
> })
> ```
> If you forget, the redirected call will fail schema validation. Re-run `test_hooks.py` after the
> change (the §5a redirect assert still checks the target tool name).

---

## 4. Step 7c — The "case facts" block (Domain 5.1)

Over a long conversation, history gets summarized and **numbers/dates/IDs are exactly what
progressive summarization drops**. Defend them with a small **persistent facts block** the harness
maintains and **injects at the top of the system prompt every turn** (top, not middle —
lost-in-the-middle is real).

```python
# core/agent.py — capture facts as tools return them, then inject them each turn
class SupportAgent:
    def __init__(self, claude, client):
        ...
        self.case_facts: dict = {}            # durable numbers/IDs/dates

    def _capture_facts(self, tool_name: str, result: dict) -> None:
        """Pull the few fields worth keeping out of a (normalized) tool result."""
        if tool_name == "get_customer" and result.get("count") == 1:
            self.case_facts["customer_id"] = result["matches"][0]["id"]
        order = result.get("order")
        if isinstance(order, dict):                       # trim a verbose lookup to what matters
            self.case_facts["order"] = {k: order.get(k) for k in
                                        ("order_id", "status", "total", "placed_at")}
        if result.get("refunded"):
            self.case_facts["refund"] = {"order_id": result.get("order_id"),
                                         "amount": result.get("amount")}

    def _case_facts_block(self) -> str:
        if not self.case_facts:
            return ""
        return ("\n\n## CASE FACTS (authoritative — never contradict these)\n"
                + json.dumps(self.case_facts, indent=2))
```

Wire capture into the post-hook path and inject the block into the per-turn system prompt:

```python
    # in _run_tools, right after self._run_post_hooks(...):
    self._capture_facts(name, result)

    # in run(), build the system prompt fresh each turn so facts ride along:
    response = self.claude.chat(
        messages=self.messages,
        system=SYSTEM + self._case_facts_block(),   # facts pinned at the TOP
        tools=tools,
    )
```

> **Two §5.1 ideas in one move:** *trimming* the 4-field order down (not the whole 40-field record)
> keeps verbose tool output from accumulating, and *pinning* the facts at the top survives both
> summarization and lost-in-the-middle. The block is the durable source of truth the model can't lose.

---

## 5. Run & observe

### 5a. Structured handoff (server + client — no model)
```python
# reuse the mcp_client.py harness (like Phase 2 §4b)
h = await envelope("escalate_to_human", {
    "customer_id": "C001", "root_cause": "refund_over_limit",
    "recommended_action": "Approve manually", "refund_amount": 600})
assert h["escalated"] is True
for k in ("customer_id", "root_cause", "recommended_action", "refund_amount"):
    assert k in h["handoff"], h
print("HANDOFF TESTS OK")
```

### 5b. Case-facts assembly (pure — no model)
```python
a = SupportAgent(claude=None, client=None)
a._capture_facts("get_customer", {"matches": [{"id": "C001"}], "count": 1})
a._capture_facts("lookup_order", {"order": {"order_id": "12345", "status": "shipped",
                                            "total": 49.99, "placed_at": "2024-06-01T00:00:00+00:00",
                                            "customer_id": "C001"}, "found": True})
facts = a._case_facts_block()
assert "C001" in facts and "12345" in facts and "49.99" in facts
assert "customer_id" not in a.case_facts["order"]   # verbose field trimmed out
print("CASE-FACTS TESTS OK")
```

### 5c. Escalation calibration + decomposition (needs auth/credits)
With `uv run main.py`:
- *"This arrived broken, here's a photo, I want a replacement"* → **resolves** (no escalation).
- *"Just put me through to a person."* → **escalates immediately**, no investigation first.
- *"Will you match Acme's price?"* (policy silent) → **escalates** on the policy gap.
- *"I'm furious it's late!"* (normal refund) → **resolves**; frustration alone does not escalate.
- A phone number matching **two** customers → agent **asks for another identifier**, doesn't guess.
- A message with **three concerns** → all three handled, one synthesized reply.
- After a long chat, ask *"what was the order total again?"* → answered from the **case-facts block**,
  not a hallucination.

---

## 6. Exam mapping (where Phase 4 scores)

- **Escalation triggers** = explicit request / policy gap / no progress; **never** complexity,
  sentiment, or self-confidence (EXAM-PREP §4.4, §4.10; sample Q3). Honor explicit human requests
  *immediately*. Multiple matches → **ask**, don't heuristically pick (§4.10).
- **Structured handoff** = customer ID + root cause + amount + recommended action, because the human
  can't see the transcript (§1.4).
- **Case facts vs progressive summarization** = extract a persistent facts block, pin key info at the
  **start**, trim verbose tool outputs to relevant fields (§5.1). A bigger context window does **not**
  fix this — structured state does.
- **Few-shot** is the highest-leverage prompt technique for ambiguous judgment calls (§4.2).

---

## 7. Close out the phase

- [ ] Tick the three Phase 4 boxes in [`overview.md`](overview.md).
- [ ] Re-run `test_hooks.py` (handoff signature change touches the Phase 3 redirect) + add the
  §5a/§5b tests.
- [ ] Notes one-liner: *"Escalate on request/policy-gap/no-progress only (not complexity/sentiment/
  confidence); structured handoff because the human can't see the chat; pin a trimmed case-facts block
  at the top so summarization can't drop the numbers."*
- [ ] Commit (this repo commits straight to `main`):
  ```bash
  git add projects/cert-01-customer-support-agent certification/projects/overview.md
  git commit -m "Project 01 Phase 4: escalation calibration, structured handoff, case-facts block"
  ```
- [ ] Run `/log`.

### What's next — Phase 5 (the actual exam payload)
No more code. Answer the four **"Be able to answer"** questions from the overview in your own words and
put them in your notes:
1. Why is a prerequisite gate better than a strongly-worded system prompt for identity verification?
2. Why are sentiment and self-reported confidence bad escalation signals?
3. What's the difference between an access failure and a valid empty result, and why does it matter?
4. When would you choose a hook over prompt-based enforcement?
