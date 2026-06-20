"""
Minimal MCP server for the developer-productivity-explorer project.

MCP (Model Context Protocol) lets Claude Code talk to external tools and data sources.
This server is spawned as a subprocess by Claude Code and communicates via stdin/stdout
using JSON-RPC 2.0 — one JSON message per line in, one JSON response per line out.

Exposes:
  RESOURCE  project://catalog          — phase/domain/DoD map (no exploratory calls needed)
  TOOL      search_phases(query)       — keyword search across phase markdown files
  TOOL      get_phase(phase_id)        — return one phase file's full text

Run:  python server.py
Protocol: MCP stdio (JSON-RPC 2.0)
"""

import json
import sys
import os
from pathlib import Path

# ROOT points to the cert-06 project folder where the phase-*.md files live.
ROOT = Path(__file__).parent.parent.parent / "certification/projects/06-developer-productivity-explorer"
# CATALOG_PATH points to catalog.json sitting alongside this file.
CATALOG_PATH = Path(__file__).parent / "catalog.json"

# ---------------------------------------------------------------------------
# Helpers — pure file operations, no MCP logic
# ---------------------------------------------------------------------------

def _read_catalog() -> dict:
    # Reads and parses catalog.json — the structured map of all project phases.
    return json.loads(CATALOG_PATH.read_text())

def _read_phase(phase_id: str) -> str:
    # Opens a phase file by ID (e.g. "phase-3" → phase-3.md) and returns its full text.
    path = ROOT / f"{phase_id}.md"
    if not path.exists():
        return f"Phase file not found: {phase_id}.md"
    return path.read_text()

def _search_phases(query: str) -> list[dict]:
    # Case-insensitive substring search across all phase-*.md files.
    # Returns up to 5 matching lines per file, with the filename for attribution.
    q = query.lower()
    results = []
    for md in sorted(ROOT.glob("phase-*.md")):
        text = md.read_text()
        lines = [ln for ln in text.splitlines() if q in ln.lower()]
        if lines:
            results.append({"file": md.name, "matches": lines[:5]})
    return results

# ---------------------------------------------------------------------------
# MCP message handlers — one function per JSON-RPC method Claude Code sends
# ---------------------------------------------------------------------------

def handle_initialize(msg: dict) -> dict:
    # Handshake: Claude Code sends "initialize" first. We respond with our name,
    # protocol version, and the capabilities we support (tools and resources).
    return {
        "jsonrpc": "2.0",
        "id": msg["id"],
        "result": {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "dev-productivity-explorer", "version": "1.0.0"},
            "capabilities": {"tools": {}, "resources": {}},
        },
    }

def handle_tools_list(msg: dict) -> dict:
    # Claude Code asks "what tools do you have?" before deciding whether to use one.
    # The description field is critical — it's the instruction Claude reads to decide
    # WHEN to prefer this tool over a built-in like Grep.
    return {
        "jsonrpc": "2.0",
        "id": msg["id"],
        "result": {
            "tools": [
                {
                    "name": "search_phases",
                    "description": (
                        "Search the text of all phase guides for a keyword or concept. "
                        "Prefer this over Grep when you want semantic matches across the "
                        "structured phase documents — it returns only the relevant lines "
                        "with file attribution, avoiding a raw grep across markdown files."
                    ),
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Keyword or phrase to search for"}
                        },
                        "required": ["query"],
                    },
                },
                {
                    "name": "get_phase",
                    "description": (
                        "Return the full text of a specific phase guide (e.g. 'phase-3'). "
                        "Use when you already know which phase to read and want its complete content. "
                        "Prefer search_phases first to locate the right phase."
                    ),
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "phase_id": {
                                "type": "string",
                                "description": "Phase identifier, e.g. 'phase-1', 'phase-3'",
                            }
                        },
                        "required": ["phase_id"],
                    },
                },
            ]
        },
    }

def handle_tools_call(msg: dict) -> dict:
    # Claude Code sends "tools/call" when it wants to execute a tool.
    # We route to the right helper based on the tool name and return the result as text.
    params = msg.get("params", {})
    name = params.get("name")
    args = params.get("arguments", {})
    if name == "search_phases":
        results = _search_phases(args.get("query", ""))
        content = json.dumps(results, indent=2)
    elif name == "get_phase":
        content = _read_phase(args.get("phase_id", ""))
    else:
        content = f"Unknown tool: {name}"
    return {
        "jsonrpc": "2.0",
        "id": msg["id"],
        "result": {"content": [{"type": "text", "text": content}]},
    }

def handle_resources_list(msg: dict) -> dict:
    # Claude Code asks "what resources do you have?" Resources are content catalogs
    # Claude can read directly — unlike tools, they don't require a call to execute.
    # The description steers Claude to read this FIRST before making exploratory calls.
    return {
        "jsonrpc": "2.0",
        "id": msg["id"],
        "result": {
            "resources": [
                {
                    "uri": "project://catalog",
                    "name": "Project phase catalog",
                    "description": (
                        "Structured map of every phase: title, domains covered, build steps, "
                        "milestone, and definition-of-done checklist. Read this resource first "
                        "to understand project structure WITHOUT making exploratory tool calls."
                    ),
                    "mimeType": "application/json",
                }
            ]
        },
    }

def handle_resources_read(msg: dict) -> dict:
    # Claude Code sends "resources/read" with a URI when it wants the resource content.
    # We return the full catalog.json text for the project://catalog URI.
    uri = msg.get("params", {}).get("uri", "")
    if uri == "project://catalog":
        text = json.dumps(_read_catalog(), indent=2)
    else:
        text = f"Unknown resource: {uri}"
    return {
        "jsonrpc": "2.0",
        "id": msg["id"],
        "result": {"contents": [{"uri": uri, "mimeType": "application/json", "text": text}]},
    }

# ---------------------------------------------------------------------------
# Stdio loop — the MCP transport layer
# ---------------------------------------------------------------------------

# Maps each JSON-RPC method name to its handler function.
HANDLERS = {
    "initialize": handle_initialize,
    "tools/list": handle_tools_list,
    "tools/call": handle_tools_call,
    "resources/list": handle_resources_list,
    "resources/read": handle_resources_read,
}

def main():
    # Read one JSON message per line from stdin, dispatch to the right handler,
    # and write the JSON response back to stdout. Claude Code keeps this process
    # alive for the duration of the session.
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        method = msg.get("method", "")
        handler = HANDLERS.get(method)
        if handler:
            response = handler(msg)
        else:
            # Return a standard JSON-RPC error for any method we don't recognise.
            response = {
                "jsonrpc": "2.0",
                "id": msg.get("id"),
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }
        print(json.dumps(response), flush=True)

if __name__ == "__main__":
    main()
