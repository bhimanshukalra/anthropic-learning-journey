from mcp.server.fastmcp import FastMCP
import mock_backend as db

mcp = FastMCP("support")


@mcp.tool()
def get_customer(identifier: str) -> dict:
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
def lookup_order(order_id: str) -> dict:
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
    if order_id.strip().upper() == "TIMEOUT":  # simulate the backend being unreachable
        return db.err("transient", True, "Order service timed out, safe to retry.")
    order = db.get_order(order_id)

    # found:false is a VALID empty result, NOT an error
    return {"order": order, "found": order is not None}


@mcp.tool()
def process_refund(order_id: str, amount: float) -> dict:
    """Issue a refund against an order. Fails (business) if the refund window has closed."""
    order = db.get_order(order_id)
    if order is None:
        return db.err("validation", False, f"No order '{order_id}' exists to refund.")
    if not order["refund_window_open"]:
        return db.err(
            "business",
            False,
            f"The refund window has expired for order {order['order_id']}; "
            f"it can no longer be refunded automatically.",
        )
    return {"refunded": True, "order_id": order_id, "amount": amount}


@mcp.tool()
def escalate_to_human(
    customer_id: str,
    root_cause: str,
    recommended_action: str,
    refund_amount: float | None = None,
) -> dict:
    """Hand the case to a human agent with a SELF-CONTAINED handoff (the human cannot see the chat). Provide: who(customer_id), WHY (root_cause), what to do (recommended_action), and any amount."""
    return {
        "escalated": True,
        "handoff": {
            "customer_id": customer_id,
            "root_cause": root_cause,
            "recommended_action": recommended_action,
            "refund_amount": refund_amount,
        },
    }


if __name__ == "__main__":
    mcp.run()
