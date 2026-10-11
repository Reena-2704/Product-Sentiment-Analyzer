import os
from datetime import datetime, timezone
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
MONGODB_URI = os.getenv("MONGODB_URI", "").strip()
DB_NAME = os.getenv("MONGODB_DATABASE", "product_sentiment")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION", "reviews")
_client = None
_collection = None

if MONGODB_URI:
    try:
        from pymongo import MongoClient
        _client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
        _client.admin.command("ping")
        _collection = _client[DB_NAME][COLLECTION_NAME]
    except Exception:
        _client = None
        _collection = None

_memory = []


def database_status():
    return "MongoDB connected" if _collection is not None else "Demo/local mode"


def save_reviews(items):
    stamped = []
    for item in items:
        record = dict(item)
        record["created_at"] = datetime.now(timezone.utc).isoformat()
        stamped.append(record)

    if _collection is not None and stamped:
        _collection.insert_many(stamped)
    else:
        _memory.extend(stamped)

    return stamped


def get_reviews(product=None):
    if _collection is not None:
        query = {}
        if product:
            query["product"] = {"$regex": product, "$options": "i"}
        return list(_collection.find(query, {"_id": 0}).sort("created_at", -1).limit(500))

    if product:
        product_l = product.lower()
        return [x for x in reversed(_memory) if product_l in str(x.get("product", "")).lower()]

    return list(reversed(_memory))
