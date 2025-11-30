import json
import logging
import os
import uuid
from typing import List, Optional, Dict, Any

logger = logging.getLogger("commerce")

# --- Data Models (Dictionaries for simplicity) ---

# Product Schema:
# {
#     "id": str,
#     "name": str,
#     "description": str,
#     "price": float,
#     "currency": str,
#     "category": str,
#     "attributes": dict (optional)
# }

# Order Schema:
# {
#     "id": str,
#     "items": List[dict],  # [{"product_id": str, "quantity": int, "price": float}]
#     "total": float,
#     "currency": str,
#     "created_at": str (ISO timestamp)
# }

# --- Mock Catalog ---

PRODUCTS = [
    {
        "id": "mug-001",
        "name": "Stoneware Coffee Mug",
        "description": "A durable, hand-crafted stoneware mug, perfect for your morning brew.",
        "price": 800,
        "currency": "INR",
        "category": "mug",
        "attributes": {"color": "white", "capacity": "350ml"},
    },
    {
        "id": "mug-002",
        "name": "Travel Tumbler",
        "description": "Insulated stainless steel tumbler to keep your drinks hot or cold.",
        "price": 1200,
        "currency": "INR",
        "category": "mug",
        "attributes": {"color": "black", "capacity": "500ml"},
    },
    {
        "id": "tee-001",
        "name": "Classic Cotton T-Shirt",
        "description": "Soft, breathable 100% cotton t-shirt for everyday wear.",
        "price": 600,
        "currency": "INR",
        "category": "clothing",
        "attributes": {"color": "navy", "size": "M"},
    },
    {
        "id": "hoodie-001",
        "name": "Cozy Fleece Hoodie",
        "description": "Warm and comfortable fleece hoodie with a kangaroo pocket.",
        "price": 2500,
        "currency": "INR",
        "category": "clothing",
        "attributes": {"color": "grey", "size": "L"},
    },
    {
        "id": "hoodie-002",
        "name": "Zip-Up Hoodie",
        "description": "Versatile zip-up hoodie, great for layering.",
        "price": 2800,
        "currency": "INR",
        "category": "clothing",
        "attributes": {"color": "black", "size": "M"},
    },
]

ORDERS_FILE = "orders.json"

# --- Persistence Helpers ---

def _load_orders() -> List[Dict[str, Any]]:
    if not os.path.exists(ORDERS_FILE):
        return []
    try:
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.error(f"Failed to decode {ORDERS_FILE}, returning empty list.")
        return []
    except Exception as e:
        logger.error(f"Error loading orders: {e}")
        return []

def _save_order(order: Dict[str, Any]):
    orders = _load_orders()
    orders.append(order)
    try:
        with open(ORDERS_FILE, "w") as f:
            json.dump(orders, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving order: {e}")

# --- Public Functions (Tools) ---

def list_products(search_query: str = "", category: str = "", max_price: float = 0.0) -> str:
    """
    Searches and filters the product catalog.
    Returns a JSON string representation of the matching products.
    """
    results = []
    for p in PRODUCTS:
        # Filter by category
        if category and category.lower() not in p["category"].lower():
            continue
        
        # Filter by max_price
        if max_price > 0 and p["price"] > max_price:
            continue
            
        # Filter by search query (name or description)
        if search_query:
            query = search_query.lower()
            if query not in p["name"].lower() and query not in p["description"].lower():
                continue
        
        results.append(p)
    
    return json.dumps(results, indent=2)

def create_order(product_id: str, quantity: int = 1) -> str:
    """
    Creates a new order for a specific product.
    Returns a JSON string representation of the created order.
    """
    # Find product
    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        return json.dumps({"error": f"Product with ID {product_id} not found."})

    # Create order object
    total_price = product["price"] * quantity
    
    import datetime
    
    order = {
        "id": str(uuid.uuid4()),
        "items": [
            {
                "product_id": product["id"],
                "name": product["name"],
                "quantity": quantity,
                "unit_price": product["price"]
            }
        ],
        "total": total_price,
        "currency": product["currency"],
        "created_at": datetime.datetime.now().isoformat()
    }
    
    # Save to file
    _save_order(order)
    
    return json.dumps(order, indent=2)

def get_last_order() -> str:
    """
    Retrieves the most recent order placed.
    Returns a JSON string representation of the order, or a message if no orders exist.
    """
    orders = _load_orders()
    if not orders:
        return json.dumps({"message": "No orders found."})
    
    return json.dumps(orders[-1], indent=2)
