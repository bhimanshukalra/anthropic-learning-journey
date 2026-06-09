# MCP Chat

MCP Chat is a command-line interface application that enables interactive chat capabilities with AI models through the Anthropic API. The application supports document retrieval, command-based prompts, and extensible tool integrations via the MCP (Model Control Protocol) architecture.

## Prerequisites

- Python 3.9+
- Anthropic API Key

## Setup

### Step 1: Configure the environment variables

1. Create or edit the `.env` file in the project root and verify that the following variables are set correctly:

```
ANTHROPIC_API_KEY=""  # Enter your Anthropic API secret key
```

### Step 2: Install dependencies

#### Option 1: Setup with uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

1. Install uv, if not already installed:

```bash
pip install uv
```

2. Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
uv pip install -e .
```

4. Run the project

```bash
uv run main.py
```

#### Option 2: Setup without uv

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install anthropic python-dotenv prompt-toolkit "mcp[cli]==1.8.0"
```

3. Run the project

```bash
python main.py
```

## Usage

### Basic Interaction

Simply type your message and press Enter to chat with the model.

### Document Retrieval

Use the @ symbol followed by a document ID to include document content in your query:

```
> Tell me about @deposition.md
```

### Commands

Use the / prefix to execute commands defined in the MCP server:

```
> /summarize deposition.md
```

Commands will auto-complete when you press Tab.

## MCP Concepts

The Model Context Protocol (MCP) lets a server expose capabilities to an AI client through three core primitives: **Tools**, **Resources**, and **Prompts**. Understanding the difference helps you decide where new functionality belongs in `mcp_server.py`.

### Tools

**Definition:** Functions the model can call to perform an action or computation. Each tool has a name, a description, and a typed input schema.

**Why:** Tools give the model the ability to *do* things — fetch live data, run logic, or change state — instead of relying only on what it already knows.

**How:** Decorate a function with `@mcp.tool(...)` and describe each argument with `Field(...)`. The model decides when to call a tool based on its description, and is *model-controlled* (the AI chooses to invoke it).

```python
@mcp.tool(name="read_doc_contents", description="Read the contents of a document and return it as a string.")
def read_document(doc_id: str = Field(description="The ID of the document to read.")) -> str:
    ...
```

This project exposes `read_doc_contents` and `edit_doc_contents`.

### Resources

**Definition:** Read-only data the server makes available, identified by a URI (e.g. `docs://documents` or `docs://documents/report.pdf`).

**Why:** Resources expose context — files, records, config — that the application can load *into* a conversation. Unlike tools, they don't perform actions or have side effects; they just return data.

**How:** Register a function with `@mcp.resource(...)` and give it a URI. Resources are typically *application-controlled* — the client app (not the model) decides when to read them, such as when a user references `@deposition.md`.

```python
@mcp.resource("docs://documents", mime_type="application/json")
def list_docs() -> list[str]:
    return list(docs.keys())
```

### Prompts

**Definition:** Reusable, parameterized message templates the server offers to the user.

**Why:** Prompts package a well-crafted instruction (e.g. "summarize this document") so users can trigger high-quality, consistent workflows without rewriting the wording each time.

**How:** Decorate a function with `@mcp.prompt(...)`; it returns a list of messages that get inserted into the conversation. Prompts are *user-controlled* — surfaced as slash commands (e.g. `/summarize`) that the user explicitly invokes.

```python
@mcp.prompt(name="summarize", description="Summarize the contents of a document.")
def summarize_prompt(doc_id: str = Field(description="The document to summarize.")) -> list[base.Message]:
    ...
```

| Primitive  | What it is            | Controlled by | Side effects | Example in this app          |
| ---------- | --------------------- | ------------- | ------------ | ---------------------------- |
| Tool       | Callable function     | Model         | Yes          | `read_doc_contents`          |
| Resource   | Read-only data by URI | Application   | No           | `docs://documents`           |
| Prompt     | Message template      | User          | No           | `/summarize`                 |

## Development

### Adding New Documents

Edit the `mcp_server.py` file to add new documents to the `docs` dictionary.

### Implementing MCP Features

To fully implement the MCP features:

1. Complete the TODOs in `mcp_server.py`
2. Implement the missing functionality in `mcp_client.py`

### Inspecting the MCP Server

You can run the MCP server in isolation using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector), a web-based debugging tool. This lets you explore the server's tools, resources, and prompts and call them interactively without running the full chat client.

```bash
uv run mcp dev mcp_server.py
```

This launches the Inspector and prints a local URL (e.g. `http://localhost:6274`) with a session token. Open it in your browser, click **Connect**, then use the **Tools** tab to invoke `read_doc_contents` and `edit_doc_contents` directly.

> **Note:** The Inspector requires [Node.js](https://nodejs.org/) (it runs via `npx`).

### Linting and Typing Check

There are no lint or type checks implemented.
