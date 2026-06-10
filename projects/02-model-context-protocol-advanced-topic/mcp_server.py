import asyncio

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.fastmcp.prompts import base
from pydantic import Field

from core.logging import configure_logging, get_logger


# Server logs must be configured before tools/resources start handling requests.
configure_logging()
logger = get_logger(__name__)

# FastMCP's own log level controls framework-level messages from the server.
mcp = FastMCP("DocumentMCP", log_level="INFO")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}


async def _pause_for_demo() -> None:
    # A tiny pause makes progress notifications visible when testing locally.
    await asyncio.sleep(0.2)


@mcp.tool(name="read_doc_contents", description="Read the contents of a document and return it as string.")
def read_document(doc_id: str = Field(description="The ID of the document to read.")) -> str:
    # Log the operation before doing the lookup so failures are traceable too.
    logger.info("Reading document '%s'", doc_id)
    if doc_id not in docs:
        logger.warning("Document '%s' was not found", doc_id)
        raise ValueError(f"Document with ID '{doc_id}' not found.")
    return docs.get(doc_id)


@mcp.tool(name="edit_doc_contents", description="Edit the contents of a document by replacing the existing content with new content.")
def edit_document(doc_id: str = Field(description="The ID of the document to edit."), old_str: str = Field(description="The text to replace. Must match exactly, including whitespace."), new_str: str = Field(description="The new text to insert in place of the old text.")):
    # Edits change server state, so they get both start and finish log lines.
    logger.info("Editing document '%s'", doc_id)
    if doc_id not in docs:
        logger.warning("Document '%s' was not found", doc_id)
        raise ValueError(f"Document with ID '{doc_id}' not found.")
    
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)
    logger.info("Edited document '%s'", doc_id)


@mcp.tool(
    name="analyze_doc_structure",
    description="Analyze a document and report progress through MCP notifications.",
)
async def analyze_doc_structure(
    doc_id: str = Field(description="The ID of the document to analyze."),
    ctx: Context | None = None,
) -> str:
    # Context gives tools access to MCP protocol features like notifications.
    logger.info("Analyzing document structure for '%s'", doc_id)
    if ctx is None:
        raise RuntimeError("MCP Context is required for progress notifications.")

    if doc_id not in docs:
        logger.warning("Document '%s' was not found", doc_id)
        raise ValueError(f"Document with ID '{doc_id}' not found.")

    await ctx.log("info", f"Starting document analysis for {doc_id}")
    await ctx.report_progress(0, 4, "starting analysis")
    await _pause_for_demo()

    content = docs[doc_id]
    await ctx.report_progress(1, 4, "counting characters")
    await _pause_for_demo()

    words = content.split()
    await ctx.report_progress(2, 4, "counting words")
    await _pause_for_demo()

    sentences = [part for part in content.split(".") if part.strip()]
    await ctx.report_progress(3, 4, "counting sentences")
    await _pause_for_demo()

    await ctx.report_progress(4, 4, "analysis complete")
    await ctx.log("info", f"Finished document analysis for {doc_id}")

    return (
        f"Analysis for {doc_id}: "
        f"{len(content)} characters, {len(words)} words, "
        f"{len(sentences)} sentences."
    )

@mcp.resource("docs://documents", mime_type="application/json")
def list_docs() -> list[str]:
    # Resource logs help show what the client loads during autocomplete setup.
    logger.info("Listing %d documents", len(docs))
    return list(docs.keys())

# TODO: Write a resource to return the contents of a particular doc
@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")
def fetch_doc(doc_id: str) -> str:
    # This runs when the client resolves a docs://documents/{doc_id} resource URI.
    logger.info("Fetching document resource '%s'", doc_id)
    if doc_id not in docs:
        logger.warning("Document resource '%s' was not found", doc_id)
        raise ValueError(f"Document with ID '{doc_id}' not found.")
    return docs[doc_id]


@mcp.prompt(name="format", description = "Rewrites the contents of the document in markdown format.")
def format_doc(doc_id: str = Field(description="The ID of the document to format.")) -> list[base.Message]:
    # Prompt logs are useful when debugging slash commands from the CLI.
    logger.info("Building format prompt for document '%s'", doc_id)
    prompt = f"""
Your goal is to reformat a document to be written with markdown syntax.

The id of the document you need to reformat is:
<document_id>
{doc_id}
</document_id>

Add in headers, bullet points, tables, etc as necessary. Feel free to add in structure.
Use the 'edit_document' tool to edit the document. After the document has been reformatted...
"""
    
    return [base.UserMessage(prompt)]

# TODO: Write a prompt to summarize a doc


if __name__ == "__main__":
    mcp.run(transport="stdio")
