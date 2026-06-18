# Project 01 · Phase 3 — Implementation Guide: *Hooks* ⭐

> **Companion to:** [`overview.md`](overview.md) (overview),
> [`phase-1.md`](phase-1.md) (the runnable agent),
> and [`phase-2.md`](phase-2.md) (structured
> errors + the deterministic gate). This file is the in-depth walkthrough for **Phase 3 only** —
> build it yourself; the snippets are a reference to compare against.

**Phase 3 covers build step 5** (Domain 1.5 — Hooks). Phase 2's `_gate` and `_latch_verification`
were *hard-coded* interception points. Phase 3 turns that idea into a **reusable mechanism**: a small
pipeline of **PreToolUse** hooks (run *before* a tool, can block or redirect) and **PostToolUse**
hooks (run *after* a tool, can rewrite the result before the model sees it).

**Milestone:** a **$600 refund is intercepted and escalated** (never executed), and **tool outputs
reach the model in one consistent date/status shape** regardless of which tool produced them.

**Phase 3 Definition of done**
- [ ] Refund > $500 is **blocked and redirected** by a hook (not by the prompt).
- [ ] Mixed date/status formats are **normalized by a PostToolUse hook** before the model reads them.

What Phase 3 deliberately leaves out (don't build these yet): escalation *calibration* with few-shot
(explicit-request / policy-gap / no-progress), multi-concern decomposition, the structured handoff
summary, and the persistent **"case facts"** block — all of that is **Phase 4**. Phase 3 is hooks and
nothing more.

---

## 0. Mental model — two interception points around every tool call

Phase 2 wired *two specific* behaviors into `_run_tools`: a gate before the call and a verification
latch after it. Phase 3 keeps those exact behaviors but **re-homes them as entries in a hook
pipeline**, then adds one more hook to each side:

```
        ┌────────────────────────────────────────────────────────────────┐
        │  for each tool_use block the model emitted:                      │
        │                                                                  │
        │   ─ PreToolUse hooks ─ (run in order, first decision wins)       │
        │      • verify_gate    → block if no verified customer  (Phase 2) │
        │      • refund_cap     → redirect refund > $500 to escalate  ⭐   │  ← NEW
        │                                                                  │
        │   ── CALL ── run the (possibly redirected) tool                  │
        │                                                                  │
        │   ─ PostToolUse hooks ─ (run in order, each rewrites result)     │
        │      • latch_verify   → latch id on get_customer count==1 (Ph.2) │
        │      • normalize      → unify placed_at + status shapes     ⭐   │  ← NEW
        └────────────────────────────────────────────────────────────────┘
```

Two ideas, same two homes as Phase 2:

- **PreToolUse = enforcement** (lives in the **harness**, in code). It runs *before* the tool and can
  **block** (short-circuit with an error envelope) or **redirect** (swap the call for another tool).
  The model cannot talk past it — that is the whole point of using a hook for a rule that *must* hold.
- **PostToolUse = normalization** (also in the harness). It runs *after* the tool and **rewrites the
  result** so the model always sees one clean shape, never raw Unix timestamps or numeric status codes.

> **Why hooks, not prompt instructions?** Same reason as the Phase 2 gate (§4.1 determinism): a
> "$500 limit" enforced in the prompt fails some non-zero fraction of the time. A hook is a hard
> invariant. **Use a hook whenever compliance must be guaranteed** — that exact phrasing is what the
> exam tests in Domain 1.5.

---

## 1. Step 5a — Generalize the gate/latch into a hook pipeline

Define two tiny hook contracts and register them once. A **PreToolUse** hook returns a *decision*
(or `None` to allow); a **PostToolUse** hook returns a (possibly rewritten) result dict.

```python
# core/agent.py — hook contracts

# A PreToolUse hook inspects (tool_name, tool_input, agent) and returns one of:
#   None                                  → allow the call unchanged
#   {"block":    <error-envelope dict>}   → skip the tool, return the envelope as the result
#   {"redirect": (tool_name, tool_input)} → call a DIFFERENT tool instead

# A PostToolUse hook inspects (tool_name, result, agent) and returns a result dict
#   (it may rewrite the result or return it untouched).
```

Phase 2's two behaviors become the first hook on each side — *identical logic, new packaging*:

```python
def hook_verify_gate(tool_name: str, tool_input: dict, agent) -> dict | None:
    """PreToolUse: block gated tools until a single customer is verified. (was _gate)"""
    if tool_name in GATED_TOOLS and agent.verified_customer_id is None:
        return {"block": {
            "isError": True, "errorCategory": "permission", "isRetryable": False,
            "message": ("Identity not verified. Call get_customer and confirm a SINGLE "
                        "matching customer before looking up orders or issuing refunds."),
        }}
    return None

def hook_latch_verification(tool_name: str, result: dict, agent) -> dict:
    """PostToolUse: latch the id when get_customer returns exactly one match. (was _latch_verification)"""
    if tool_name == "get_customer" and result.get("count") == 1:
        agent.verified_customer_id = result["matches"][0]["id"]
    return result
```

> Note the post-hook now works on the **parsed dict**, not the raw text — see §4 for where the JSON
> parse moves to. That keeps every hook dealing in plain dicts.

---

## 2. Step 5b — Tool-call interception: block refund > $500, redirect to escalation ⭐ (Domain 1.5)

This is the headline of Phase 3 (and exam §1.5 / the distractor-trap in §4.1). A refund above the
auto-approve limit **must not execute** — instead the call is **redirected** to `escalate_to_human`,
so a person decides. The threshold lives in code; no prompt wording can override it.

```python
REFUND_LIMIT = 500.0

def hook_refund_cap(tool_name: str, tool_input: dict, agent) -> dict | None:
    """PreToolUse: a refund over $500 is never auto-issued — redirect it to a human."""
    if tool_name == "process_refund" and float(tool_input.get("amount", 0)) > REFUND_LIMIT:
        return {"redirect": ("escalate_to_human", {
            "reason": "refund_over_limit",
            "summary": (f"Refund of ${tool_input.get('amount')} on order "
                        f"{tool_input.get('order_id')} exceeds the ${REFUND_LIMIT:.0f} "
                        f"auto-approve limit; routing to a human for approval."),
        })}
    return None
```

Register both pre-hooks — **order matters**: verify identity first, then apply the cap.

```python
PRE_HOOKS  = [hook_verify_gate, hook_refund_cap]   # first decision wins
POST_HOOKS = [hook_latch_verification, hook_normalize_order]   # hook_normalize_order: §3
```

> **Block vs redirect — the subtlety.** A *blocked* call returns an error envelope under the model's
> original `tool_use_id`, and the model reacts (e.g. calls `get_customer`). A *redirected* call
> executes a different tool but still answers the original `tool_use_id` — so the model asked for a
> refund and gets back an "escalated" result. Both keep the `tool_use`/`tool_result` pairing balanced,
> which the API requires. (We intercept rather than refuse so the conversation stays well-formed.)

---

## 3. Step 5c — PostToolUse normalization: one shape for dates + status (Domain 1.5)

Your mock data is heterogeneous **on purpose** (see Phase 1 seed data): order `12345` stores
`placed_at` as a **Unix timestamp** `1717200000` and `status` as `2`; order `67890` stores `placed_at`
as **ISO 8601** `"2026-05-30T10:00:00Z"` and `status` as `4`. If the raw values reach the model it has
to reason about two formats *and* decode numeric status codes — exactly the kind of avoidable
ambiguity a `PostToolUse` hook removes.

```python
from datetime import datetime, timezone

STATUS_LABELS = {0: "pending", 1: "processing", 2: "shipped",
                 3: "out_for_delivery", 4: "delivered", 5: "cancelled"}

def _to_iso(value) -> str:
    """Unix epoch (int/float) OR an ISO-ish string → a single canonical ISO-8601 UTC string."""
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()
    return str(value).replace("Z", "+00:00")   # already a string; normalize the Z suffix

def hook_normalize_order(tool_name: str, result: dict, agent) -> dict:
    """PostToolUse: rewrite an order payload into one consistent date/status shape."""
    order = result.get("order")
    if isinstance(order, dict):
        if "placed_at" in order:
            order["placed_at"] = _to_iso(order["placed_at"])
        if isinstance(order.get("status"), int):
            order["status"] = STATUS_LABELS.get(order["status"], f"unknown({order['status']})")
    return result
```

> **Don't do the date math in the tool.** Phase 2 deliberately deferred this so the *tools* stay dumb
> data sources and the *normalization* is a single, reusable cross-cutting concern. One hook fixes
> every tool that returns an order, instead of N copies of the conversion sprinkled through the server.

---

## 4. Wire the pipeline into `_run_tools`

The pre/post-hook loops replace Phase 2's inline `_gate` / `_latch_verification` calls. Parse the tool
output **once** into a dict, run the post-hooks on it, then serialize back for the `tool_result`.

```python
    def _run_pre_hooks(self, tool_name, tool_input):
        for hook in PRE_HOOKS:
            decision = hook(tool_name, tool_input, self)
            if decision is not None:
                return decision          # first decision wins
        return None

    def _run_post_hooks(self, tool_name, result: dict) -> dict:
        for hook in POST_HOOKS:
            result = hook(tool_name, result, self)
        return result

    async def _run_tools(self, response: Message) -> list[dict]:
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            name, args = block.name, block.input
            print(f"tool_use: {name}({json.dumps(args)})")

            decision = self._run_pre_hooks(name, args)            # ── PreToolUse ──
            if decision and "block" in decision:
                print(f"  ⛔ blocked: {name}")
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": json.dumps(decision["block"]), "is_error": True})
                continue
            if decision and "redirect" in decision:
                name, args = decision["redirect"]                 # swap the call
                print(f"  ↪ redirected to: {name}({json.dumps(args)})")

            output = await self.client.call_tool(name, args)      # ── CALL ──
            text = output.content[0].text if output and output.content else "{}"
            try:
                result = json.loads(text)
            except (ValueError, TypeError):
                result = {}

            result = self._run_post_hooks(name, result)           # ── PostToolUse ──
            results.append({"type": "tool_result", "tool_use_id": block.id,
                            "content": json.dumps(result),
                            "is_error": bool(result.get("isError"))})
        return results
```

Notice the `is_error` flag now comes straight from the parsed dict (`result.get("isError")`) — the
Phase 2 `_is_error_envelope` text-parsing helper is no longer needed once the loop parses once.

---

## 5. Run & observe — most of this needs **no API credits**

Like Phase 2, the hooks are deterministic code, so you can verify the headline behavior without the
model.

### 5a. Pre-hook test (pure — no server, no model)
```python
# test_hooks.py — run with: uv run python test_hooks.py
from core.agent import SupportAgent
a = SupportAgent(claude=None, client=None)
a.verified_customer_id = "C001"                      # pretend already verified

# refund within limit → allowed (no decision)
assert a._run_pre_hooks("process_refund", {"order_id": "12345", "amount": 50}) is None

# refund over $500 → redirected to escalate_to_human, NOT executed
d = a._run_pre_hooks("process_refund", {"order_id": "67890", "amount": 600})
assert d and d["redirect"][0] == "escalate_to_human", d

# gate still fires when unverified
b = SupportAgent(claude=None, client=None)
assert "block" in b._run_pre_hooks("process_refund", {"order_id": "12345", "amount": 50})
print("PRE-HOOK TESTS OK")
```

### 5b. Post-hook normalization test (pure)
```python
unix = a._run_post_hooks("lookup_order",
        {"order": {"order_id": "12345", "status": 2, "placed_at": 1717200000}, "found": True})
iso  = a._run_post_hooks("lookup_order",
        {"order": {"order_id": "67890", "status": 4, "placed_at": "2026-05-30T10:00:00Z"}, "found": True})

# both now carry an ISO-8601 string date and a human status label — ONE shape
assert unix["order"]["status"] == "shipped"   and "T" in unix["order"]["placed_at"]
assert iso["order"]["status"]  == "delivered" and iso["order"]["placed_at"].endswith("+00:00")
print("POST-HOOK TESTS OK")
```

### 5c. Model-level behavior (when you have auth/credits)
With `uv run main.py`, after verifying a customer:
- `"refund order 67890 for $600"` → the refund **never runs**; the hook redirects to
  `escalate_to_human`, and the agent tells the customer it's been routed for approval.
- `"refund order 12345 for $20"` → under the limit → proceeds normally (subject to the Phase 2
  business/validation checks).
- `"what's the status of order 12345"` → the model sees `status: "shipped"` and an ISO date, never
  `2` / `1717200000`.

---

## 6. How this maps to *real* Claude Code / Agent SDK hooks (exam) ⭐

You built the hook mechanism by hand so you can *see* it — but in production you'd use Claude Code's
(and the Agent SDK's) **built-in hook system**, and the exam tests the real feature names and what
each event can actually do. The good news: the two hooks you wrote map **one-to-one** onto real
events, capabilities and all.

### 6.1 The two events that matter here

| Your hand-built hook | Real event | Fires | Can it… |
|---|---|---|---|
| `hook_verify_gate` / `hook_refund_cap` | **`PreToolUse`** | *before* a tool runs | **deny** the call, **modify the input**, or auto-allow |
| `hook_latch_verification` / `hook_normalize_order` | **`PostToolUse`** | *after* a tool succeeds | **rewrite the output the model sees**, add context — but **cannot block** (the tool already ran) |

This is the whole Domain 1.5 idea in one line: **`PreToolUse` = enforcement/interception**,
**`PostToolUse` = normalization of heterogeneous tool data before the model reads it**.

### 6.2 `PreToolUse` — block or redirect (your refund cap)

A `PreToolUse` hook returns a decision under `hookSpecificOutput`. The key fields:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Refund exceeds the $500 auto-approve limit; routing to a human.",
    "updatedInput": null
  }
}
```

- **`permissionDecision`** is one of **`"allow"`** (auto-approve, skip the permission prompt),
  **`"deny"`** (block the call — the `Reason` is sent back to Claude), or **`"ask"`** (surface a
  confirmation to the user).
- **`updatedInput`** lets the hook **rewrite the tool's arguments** before it runs (e.g. clamp,
  sanitize, or redirect a path).
- A command hook can equivalently signal a block with **exit code 2** (stderr is fed back to Claude).

> **Mapping to your code:** your `{"block": <envelope>}` is a `permissionDecision: "deny"` with the
> envelope text as the reason. Your `{"redirect": (...)}` has no single built-in equivalent — the
> closest real patterns are **`deny` + a reason that tells the model to call `escalate_to_human`**, or
> **`updatedInput`** to mutate the *same* tool's args. True "call a different tool instead" is a
> harness-level convenience you built; on the exam, "intercept the refund and **deny** it, redirecting
> to escalation" is the expected phrasing.

### 6.3 `PostToolUse` — normalize the output (your date/status hook)

A `PostToolUse` hook fires after the tool succeeds and **can replace what the model receives**:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "updatedToolOutput": "{\"order\": {\"status\": \"shipped\", \"placed_at\": \"2024-06-01T00:00:00+00:00\"}}",
    "additionalContext": "Dates normalized to ISO-8601 UTC; status codes mapped to labels."
  }
}
```

- **`updatedToolOutput`** *replaces* the raw tool result the model sees — this is the real mechanism
  behind "normalize Unix vs ISO dates and numeric status codes **before the model reads them**." It is
  **not just feedback**; it actually changes the content. That's precisely what your
  `hook_normalize_order` does.
- **`additionalContext`** *appends* extra info alongside the result (without replacing it).
- **It cannot block** — the tool has already executed. Enforcement belongs in `PreToolUse`.

### 6.4 Where hooks are configured (`settings.json`) — ties into Domain 3

In Claude Code, hooks live in a **`hooks`** block in settings, keyed by event, with a **`matcher`** on
the tool name:

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "process_refund",
        "hooks": [{ "type": "command", "command": ".claude/hooks/refund_cap.sh" }] }
    ],
    "PostToolUse": [
      { "matcher": "lookup_order",
        "hooks": [{ "type": "command", "command": ".claude/hooks/normalize_order.sh" }] }
    ]
  }
}
```

- `matcher` is an exact name or `A|B` alternation (and matches MCP tools as `mcp__<server>__<tool>`);
  omit it to match every tool.
- **Scope follows the Domain 3 hierarchy:** **`.claude/settings.json`** (project, **committed/shared**
  with the team) vs **`~/.claude/settings.json`** (user, machine-local) vs
  **`.claude/settings.local.json`** (project but **git-ignored**, personal overrides). A team-wide
  compliance hook belongs in **project** `.claude/settings.json`.

### 6.5 The same hooks in the Agent SDK (Python)

Since this project is built on the Agent SDK, the production form of your pipeline is a `hooks` option
of callbacks registered with `HookMatcher`:

```python
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

async def refund_cap(input_data, tool_use_id, context):
    if input_data["tool_name"] == "process_refund" and input_data["tool_input"]["amount"] > 500:
        return {"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Refund over $500 — escalate to a human.",
        }}
    return {}

options = ClaudeAgentOptions(hooks={
    "PreToolUse":  [HookMatcher(matcher="process_refund", hooks=[refund_cap])],
    "PostToolUse": [HookMatcher(matcher="lookup_order",   hooks=[normalize_order])],
})
```

The callback receives `(input_data, tool_use_id, context)` and returns the **same
`hookSpecificOutput`** shape as the settings-file form.

### 6.6 The one-line exam takeaways

- **`PreToolUse` blocks/redirects; `PostToolUse` rewrites output. Only `PreToolUse` can stop a call.**
- **Use a hook when compliance or consistency must be *guaranteed*; use the prompt only for soft
  preferences** (the §4.1 determinism rule again).
- Team-shared hooks → **project `.claude/settings.json`** (Domain 3 hierarchy).

> **Scope note (don't over-study):** Claude Code defines many more hook events (`UserPromptSubmit`,
> `Stop`, `SubagentStop`, `SessionStart`/`SessionEnd`, `PreCompact`, `Notification`, and more). For
> **Foundations**, `PreToolUse` and `PostToolUse` are the ones that carry weight — recognize the
> others by name, but don't memorize their schemas.
>
> 📖 Official refs: Claude Code hooks — https://docs.claude.com/en/docs/claude-code/hooks ·
> Agent SDK hooks — https://docs.claude.com/en/api/agent-sdk/hooks

---

## 7. Close out the phase

- [ ] Tick the two Phase 3 boxes in [`overview.md`](overview.md).
- [ ] Notes one-liner: *"PreToolUse intercepts/redirects (refund>$500 → escalate); PostToolUse
  normalizes heterogeneous output (Unix/ISO dates, status codes) before the model reads it; hooks =
  guaranteed compliance, prompts = soft preference."*
- [ ] Commit (this repo commits straight to `main`):
  ```bash
  git add projects/cert-01-customer-support-agent certification/projects/overview.md
  git commit -m "Project 01 Phase 3: PreToolUse/PostToolUse hooks — refund cap + output normalization"
  ```
- [ ] Run `/log`.

### What Phase 4 will add (preview)
Phase 4 shifts from *enforcement* to *judgment*: **escalation calibration** with few-shot examples
(escalate on explicit request / policy gap / inability to progress — never on sentiment or
self-confidence), **multi-concern decomposition** with a single synthesized reply, the **structured
handoff** summary (customer ID + root cause + amount + recommended action, because the human can't see
the transcript), and a persistent **"case facts"** block injected each prompt so progressive
summarization never loses the numbers.
