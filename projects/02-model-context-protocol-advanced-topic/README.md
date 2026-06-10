# MCP Advanced: Logging and Progress

This project builds on `01-introduction-to-model-context-protocol` and focuses on
observability for a local MCP client/server application.

The app is still a command-line Claude chat client backed by a local document MCP
server, but this version adds:

- structured logging for MCP client, server, CLI, chat, resource, prompt, and tool flows
- user-facing progress messages while MCP servers connect and operations run
- beginner-friendly comments around the logging and progress code paths

## What This Project Demonstrates

MCP applications often have work happening across multiple places at once: the
CLI, the model call, the MCP client, and the MCP server process. Logging and
progress output make that work visible.

This project shows how to:

- configure Python logging once at app startup
- keep logs on `stderr` so MCP `stdio` protocol messages are not corrupted
- give each module a named logger with `get_logger(__name__)`
- wrap slow MCP operations in progress steps
- trace MCP tools, resources, and prompts without printing full document content

## Project Structure

```text
.
├── main.py              # CLI app entry point and shared progress setup
├── mcp_client.py        # MCP stdio client with logging and progress wrappers
├── mcp_server.py        # FastMCP document server with server-side logs
├── core/
│   ├── logging.py       # Shared logging configuration
│   ├── progress.py      # Lightweight stderr progress reporter
│   ├── chat.py          # Claude chat loop logging
│   ├── tools.py         # MCP tool discovery/execution logging
│   ├── cli.py           # CLI startup and autocomplete logging
│   └── cli_chat.py      # Document mention and slash-command logging
├── pyproject.toml
└── uv.lock
```

## Setup

Create a `.env` file in this folder:

```bash
ANTHROPIC_API_KEY="your-api-key"
CLAUDE_MODEL="claude-sonnet-4-5"
```

Install dependencies with `uv`:

```bash
uv sync
```

Run the app:

```bash
uv run main.py
```

If you are not using `uv`, create a virtual environment and install the project
dependencies from `pyproject.toml`.

## Logging

Logging is configured in `core/logging.py` and enabled by calling
`configure_logging()` from both `main.py` and `mcp_server.py`.

Logs are written to `stderr` because MCP's `stdio` transport uses stdout/stdin
for protocol messages. Printing logs to stdout from an MCP server can break the
client/server connection.

Set the log level with `MCP_LOG_LEVEL`:

```bash
MCP_LOG_LEVEL=DEBUG uv run main.py
```

Common levels:

- `INFO`: default, shows high-level application flow
- `DEBUG`: shows more detailed development traces
- `WARNING`: shows only warnings and errors
- `ERROR`: shows only errors

Example log coverage:

- MCP client connection startup and cleanup
- tool, resource, and prompt discovery
- Claude chat loop round trips
- model-requested tool execution
- server-side document reads and edits
- CLI resource and prompt refresh failures

## Progress

Progress output is handled by `core/progress.py`.

Progress messages are meant for the person using the CLI. They are shorter and
friendlier than logs:

```text
[progress] starting MCP chat application
[progress] connecting MCP server 'documents'
[progress] MCP server 'documents' connected
[progress] loading prompts from 'documents' done in 0.03s
```

Progress is enabled by default. Disable it with:

```bash
MCP_PROGRESS=0 uv run main.py
```

Progress currently wraps:

- MCP server connection
- tool loading
- prompt loading
- prompt fetching
- resource reads
- tool execution

## Usage

Start the app and type a message:

```text
> What documents are available?
```

Mention a document with `@` to include its contents in the chat context:

```text
> What does @deposition.md say?
```

Run a server-provided prompt with `/`:

```text
> /format deposition.md
```

The CLI autocomplete uses MCP resources and prompts, so startup logging/progress
will show those discovery calls.

## Inspecting the MCP Server

You can inspect the server directly with MCP Inspector:

```bash
uv run mcp dev mcp_server.py
```

Use the Inspector to call the document tools, list resources, and fetch prompts.
Server logs will still go to `stderr`.

## Notes

This project intentionally keeps the document server small. The goal is not to
add more MCP capabilities yet; the goal is to make the existing MCP flow easier
to observe while learning how client/server interactions move through the app.
