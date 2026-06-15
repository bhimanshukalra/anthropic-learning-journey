from mcp.server.fastmcp import FastMCP
import mock_backend as db

mcp = FastMCP("support")

@mcp.tool()
def get_customer(identifier:str) -> dict:
    """Look up a CUSTOMER ACCOUNT by who they are - NOT by their order.
    
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
def lookup_order(order_id:str) -> dict:
    """Look up a single ORDER by its ORDER NUMBER - NOT a customer.

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
def process_refund(order_id:str, amount:float) -> dict:
    """Issue a refund against an order."""
    return {"refunded": True, "order_id": order_id, "amount": amount}

@mcp.tool()
def escalate_to_human(reason: str, summary:str) -> dict:
    """Hand the case to a human agent. Terminal action."""
    return {"escalated": True, "reason": reason}

if __name__ == "__main__":
    mcp.run()