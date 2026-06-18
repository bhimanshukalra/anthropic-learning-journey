# mock_backend.py — a fake CRM/OMS. No network, no DB. Pure dicts.

CUSTOMERS = {
    "C001": {"id": "C001", "name": "Ada Lovelace", "email": "ada@example.com", "phone": "555-0100"},
    "C002": {"id": "C002", "name": "Alan Turing", "email": "alan@example.com", "phone": "555-0199"},
    # Same phone as C001 on purpose — sets up the "multiple matches" case.
    "C003": {"id": "C003", "name": "Ada B.", "email": "adab@example.com", "phone": "555-0100"},
}

ORDERS = {
    "12345": {"order_id": "12345", "customer_id": "C001", "status": 2,
              "total": 49.99, "placed_at": 1717200000, "refund_window_open": True},          # Unix ts on purpose
    "67890": {"order_id": "67890", "customer_id": "C002", "status": 4,
              "total": 620.00, "placed_at": "2026-05-30T10:00:00Z", "refund_window_open": False},  # ISO on purpose
}

def find_customer(query:str) -> list[dict]:
    """Match by id, email, or phone. Returns 0, 1 or many."""
    q = query.strip().lower()
    return [c for c in CUSTOMERS.values() if q in (c["id"].lower(), c["email"].lower(), c["phone"].lower())]

def get_order(order_id:str) -> dict | None:
    """Return order by id, or None if not found. Accepts leading # and whitespace."""
    return ORDERS.get(order_id.lstrip("#").strip())

def err(category: str, retryable: bool, message: str) -> dict:
    return {"isError": True, "errorCategory": category, "isRetryable": retryable, "message": message}