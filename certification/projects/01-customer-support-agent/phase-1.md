# Project 01 · Phase 1 — Implementation Guide: *Runnable Agent*

> **Companion to:** [`overview.md`](overview.md) (the overview).
> **This file is the in-depth walkthrough for Phase 1 only.** Build it yourself — every snippet here
> is a *reference* to compare against, not code to paste blindly. The learning is in typing it and
> watching it behave.

**Phase 1 covers build steps 1–2** (Domains 2.1 + 1.1).
**Milestone:** ask *"check my order #12345"* → the agent routes to `lookup_order` (not `get_customer`),
calls it, and replies — with the loop terminating purely on `stop_reason == "end_turn"`.

**Phase 1 Definition of done**
- [ ] Two deliberately-similar tools (`get_customer`, `lookup_order`) reliably selected via descriptions alone — no routing layer.
- [ ] Loop driven purely by `stop_reason`; no NL-parsing / iteration-cap / text-content stop.

What Phase 1 deliberately leaves out (don't build these yet): structured error categories, the
verification gate, hooks, escalation calibration. Those are Phases 2–4. Resist the urge to add them
now — the point of Phase 1 is to *see a clean loop work* before you complicate it.

---

## 0. Mental model before you type

You are building three pieces that talk over stdio:

```
┌────────────┐   user text    ┌──────────────────┐   tool_use blocks   ┌────────────────┐
│  CLI / you │ ─────────────▶ │  Agentic loop    │ ───────────────────▶ │ MCP server     │
│            │ ◀───────────── │  (core/agent.py) │ ◀─────────────────── │ (mock backend) │
└────────────┘  final reply   └──────────────────┘   tool_result blocks └────────────────┘
                                       │
                                       ▼
                              Anthropic Messages API
                              (decides which tool, when to stop)
```

The model never executes anything. It *emits* `tool_use` blocks; **your loop** runs them and feeds
results back. The model signals "I'm finished" via `stop_reason`, not via prose. Internalising that
split is literally Domain 1.1.

---

## 1. Scaffold the project

Mirror your existing course projects so the muscle memory carries over. Suggested location:
`projects/cert-01-customer-support-agent/` (prefix `cert-` so it doesn't clash with course `01`/`02`).

```bash
cd ~/Development/anthropic-learning-journey/projects
uv init cert-01-customer-support-agent
cd cert-01-customer-support-agent
uv add "anthropic>=0.51.0" "mcp[cli]>=1.8.0" "prompt-toolkit>=3.0.51" "python-dotenv>=1.1.0"
```

Target layout for Phase 1 (you'll add files in later phases):

```text
cert-01-customer-support-agent/
  .env                  # ANTHROPIC_API_KEY + CLAUDE_MODEL
  mock_backend.py       # in-memory fake data (no real DB)
  mcp_server.py         # the 4 tools, exposed over stdio
  mcp_client.py         # stdio client wrapper (reuse from course project 01)
  core/
    __init__.py
    claude.py           # thin Anthropic wrapper (reuse from course project 01)
    agent.py            # ← the agentic loop you write this phase
  main.py               # CLI entry point
```

`.env`:

```bash
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-opus-4-8     # latest Opus; claude-sonnet-4-6 is the cheaper option
```

> Reuse, don't reinvent: copy `mcp_client.py` and `core/claude.py` verbatim from
> `projects/01-introduction-to-model-context-protocol/`. They already implement the stdio client and
> the `messages.create` wrapper correctly. Phase 1's *new* thinking goes into the tools and the loop.

---

## 2. The mock backend (`mock_backend.py`)

Keep the data tiny and in-memory. Two customers, a couple of orders. The mock is where you encode the
*one* edge case Phase 1 cares about: a phone number that matches **two** customers (you'll exploit
that in Phase 4, but seed it now so you don't reshape data later).

```python
# mock_backend.py — a fake CRM/OMS. No network, no DB. Pure dicts.

CUSTOMERS = {
    "C001": {"id": "C001", "name": "Ada Lovelace",  "email": "ada@example.com",  "phone": "555-0100"},
    "C002": {"id": "C002", "name": "Alan Turing",   "email": "alan@example.com", "phone": "555-0199"},
    # Same phone as C001 on purpose — sets up the "multiple matches" case for Phase 4.
    "C003": {"id": "C003", "name": "Ada B.",        "email": "adab@example.com", "phone": "555-0100"},
}

ORDERS = {
    "12345": {"order_id": "12345", "customer_id": "C001", "status": 2,
              "total": 49.99, "placed_at": 1717200000},          # Unix ts on purpose (Phase 3)
    "67890": {"order_id": "67890", "customer_id": "C002", "status": 4,
              "total": 620.00, "placed_at": "2026-05-30T10:00:00Z"},  # ISO on purpose (Phase 3)
}

def find_customer(query: str) -> list[dict]:
    """Match by id, email, or phone. Returns 0, 1, or many."""
    q = query.strip().lower()
    return [c for c in CUSTOMERS.values()
            if q in (c["id"].lower(), c["email"].lower(), c["phone"])]

def get_order(order_id: str) -> dict | None:
    return ORDERS.get(order_id.lstrip("#").strip())
```

> Note the mixed `status` (int) and `placed_at` (Unix vs ISO) shapes — that inconsistency is
> intentional bait for the Phase 3 normalization hook. Leave it ugly for now.

---

## 3. The four tools with *differentiating* descriptions (Step 1 ⭐)

This is the highest-leverage idea in Phase 1, and it's exam Q2: **two similar tools must be
disambiguated by their descriptions alone.** A weak description is the root cause of misrouting —
and the fix is *descriptions first*, before few-shot, routing layers, or merging tools.

Use `FastMCP`. The docstring / `description` is what the model sees, so write it like API docs:
purpose, accepted inputs, example queries, edge cases, and **"use this vs. the other tool."**

```python
# mcp_server.py
from mcp.server.fastmcp import FastMCP
import mock_backend as db

mcp = FastMCP("support")

@mcp.tool()
def get_customer(identifier: str) -> dict:
    """Look up a CUSTOMER ACCOUNT by who they are — NOT by their orders.

    Use when you have a customer identifier: a customer ID (e.g. "C001"), an email
    ("ada@example.com"), or a phone number ("555-0100"). Returns the account record(s).

    Example queries that should route HERE:
      - "my email is ada@example.com"
      - "look up customer C001"
      - "I'm calling from 555-0100"

    Edge cases: a phone/email may match MORE THAN ONE account — the result can contain several.
    Do NOT use this to look up an order. If the user gives an ORDER number, use `lookup_order`.
    """
    matches = db.find_customer(identifier)
    return {"matches": matches, "count": len(matches)}

@mcp.tool()
def lookup_order(order_id: str) -> dict:
    """Look up a single ORDER by its ORDER NUMBER — NOT a customer.

    Use when the user references a specific order/purchase, e.g. "#12345", "order 12345",
    "where's my package for 12345". Input is the order number (with or without a leading '#').

    Example queries that should route HERE:
      - "check my order #12345"
      - "what's the status of 12345"
      - "track order 67890"

    Edge cases: returns an empty result if no such order exists (that is a VALID empty result,
    not an error). Do NOT use this for emails/phones/customer IDs — use `get_customer` for those.
    """
    order = db.get_order(order_id)
    return {"order": order, "found": order is not None}

@mcp.tool()
def process_refund(order_id: str, amount: float) -> dict:
    """Issue a refund against an order. (Phase 1: returns a stub success. Gating comes in Phase 2.)"""
    return {"refunded": True, "order_id": order_id, "amount": amount}

@mcp.tool()
def escalate_to_human(reason: str, summary: str) -> dict:
    """Hand the case to a human agent. Terminal action. (Phase 1: stub. Calibration comes in Phase 4.)"""
    return {"escalated": True, "reason": reason}

if __name__ == "__main__":
    mcp.run()
```

> **The contrast is the lesson.** Read the two top descriptions back-to-back: each names the *other*
> tool and says when to defer to it. That single sentence ("if the user gives an order number, use
> `lookup_order`") is usually what flips a misroute to a correct route. When you test, if routing is
> wrong, **fix the words here first** — don't reach for a classifier.

---

## 4. The agentic loop (`core/agent.py`) — Step 2 ⭐

Your course `core/chat.py` already has the canonical shape. For this project, write it fresh so you
*feel* the contract. The whole rule: **loop while `tool_use`, stop on `end_turn`.**

```python
# core/agent.py
import json
from anthropic.types import Message
from core.claude import Claude
from mcp_client import MCPClient

SYSTEM = (
    "You are a customer-support resolution agent. Use the tools to look up customers and orders "
    "and answer the user. Pick the single most appropriate tool for each step."
)

class SupportAgent:
    def __init__(self, claude: Claude, client: MCPClient):
        self.claude = claude
        self.client = client
        self.messages: list = []

    async def _tool_schemas(self) -> list[dict]:
        tools = await self.client.list_tools()
        return [{"name": t.name, "description": t.description, "input_schema": t.inputSchema}
                for t in tools]

    async def _run_tools(self, response: Message) -> list[dict]:
        """Execute every tool_use block the model emitted; return tool_result blocks."""
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            print(f"  ↳ tool_use: {block.name}({json.dumps(block.input)})")   # observe routing
            out = await self.client.call_tool(block.name, block.input)
            text = out.content[0].text if out and out.content else "{}"
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": text,
            })
        return results

    async def run(self, user_text: str) -> str:
        self.messages.append({"role": "user", "content": user_text})
        tools = await self._tool_schemas()

        while True:                                            # ← the agentic loop
            response = self.claude.chat(messages=self.messages, system=SYSTEM, tools=tools)
            self.messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "tool_use":             # model wants a tool → run it, loop
                tool_results = await self._run_tools(response)
                self.messages.append({"role": "user", "content": tool_results})
                continue

            # stop_reason == "end_turn" (or any non-tool stop) → we're done
            return self.claude.text_from_message(response)
```

### The anti-patterns — write them down so you can name them on the exam
Phase 1 is your chance to *prove* these are wrong by deliberately not doing them:

| ❌ Anti-pattern | Why it breaks |
|----------------|---------------|
| Parsing the model's text for "done"/"I'll help you" | Prose is not a control signal; it's brittle and locale-dependent. |
| Using an iteration cap as the *primary* stop | A cap is a safety net, not a terminator — it cuts off valid multi-step work. |
| Treating any assistant *text* as completion | The model often narrates *then* calls a tool in the same turn. |

The **only** correct terminator is `stop_reason == "end_turn"`. (Keep a high iteration cap as a
runaway guard if you like — just don't let it be the thing that normally ends the loop.)

---

## 5. Wire up the CLI (`main.py`)

```python
import asyncio, os, sys
from dotenv import load_dotenv
from mcp_client import MCPClient
from core.claude import Claude
from core.agent import SupportAgent

load_dotenv()

async def main():
    claude = Claude(model=os.environ["CLAUDE_MODEL"])
    command, args = (("uv", ["run", "mcp_server.py"])
                     if os.getenv("USE_UV", "1") == "1"
                     else ("python", ["mcp_server.py"]))

    async with MCPClient(command=command, args=args) as client:
        agent = SupportAgent(claude, client)
        print("Support agent ready. Type a message (Ctrl-C to quit).\n")
        while True:
            try:
                user_text = input("you> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not user_text:
                continue
            reply = await agent.run(user_text)
            print(f"agent> {reply}\n")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
```

---

## 6. Run it and *observe* (the milestone)

```bash
uv run main.py
```

Run these three probes and watch the `↳ tool_use:` lines:

1. **Disambiguation (the milestone):**
   `you> check my order #12345`
   ✅ Expect `↳ tool_use: lookup_order({"order_id": "#12345"})` → agent reports status/total.
   ❌ If it calls `get_customer`, your *descriptions* are too weak — go back to §3 and sharpen the
   "use this vs. that" lines. Do **not** add code to fix this.

2. **The other side of the pair:**
   `you> look up customer ada@example.com`
   ✅ Expect `get_customer`, returning Ada's record.

3. **Clean termination & valid-empty:**
   `you> what's the status of order 99999`
   ✅ Expect `lookup_order` → `{"found": false}` → the agent *explains there's no such order* and the
   loop ends on `end_turn` (one tool call, then a normal reply — not an error, not an infinite loop).

If all three behave, Phase 1 is done.

### Quick self-check while observing
- Did the loop ever stop because of text rather than `stop_reason`? (It shouldn't — you didn't write
  that path.)
- Did a multi-step query (e.g. "find customer C001 then their order 12345") loop correctly, appending
  each tool_result before the next model call?

---

## 7. Close out the phase

- [ ] Tick the two Phase 1 boxes in [`overview.md`](overview.md).
- [ ] Jot a one-liner for your notes: *"misrouting → fix descriptions first (Q2); loop terminator is
  `stop_reason`, never prose (1.1)."*
- [ ] Commit it (this repo commits straight to `main`):
  ```bash
  git add projects/cert-01-customer-support-agent certification/projects/overview.md
  git commit -m "Project 01 Phase 1: runnable support agent with disambiguated tools"
  ```
- [ ] Run `/log` for the day.

### What Phase 2 will add (preview)
You'll make the tools return the structured `isError` envelope (transient vs business vs validation
vs permission) and add the **deterministic prerequisite gate** — `lookup_order`/`process_refund`
refuse to run until `get_customer` has returned a verified ID, enforced in code, not in the prompt.
That's the single most-tested idea in the whole project. The clean loop you built here is what makes
that gate easy to drop in.
```
