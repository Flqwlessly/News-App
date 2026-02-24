from __future__ import annotations

from datetime import datetime, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import DESCENDING
from config import MONGODB_URI, MONGODB_DB
import hashlib
from typing import Optional

_client: Optional[AsyncIOMotorClient] = None


def _get_db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGODB_URI)
    return _client[MONGODB_DB]


def _make_id(article: dict) -> str:
    """Deterministic ID from sourceUrl so upserts are idempotent."""
    key = article.get("sourceUrl") or article.get("title") or ""
    return hashlib.md5(key.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Articles
# ---------------------------------------------------------------------------

async def upsert_articles(articles: list[dict]) -> int:
    """Insert or update articles. Returns count of newly upserted docs."""
    if not articles:
        return 0
    col = _get_db()["articles"]
    now = datetime.now(timezone.utc)
    count = 0
    for article in articles:
        article_id = _make_id(article)
        article["updatedAt"] = now
        article.setdefault("createdAt", now)
        if isinstance(article.get("datePosted"), str):
            try:
                article["datePosted"] = datetime.fromisoformat(article["datePosted"].replace("Z", "+00:00"))
            except ValueError:
                article["datePosted"] = now
        elif not isinstance(article.get("datePosted"), datetime):
            article["datePosted"] = now

        result = await col.update_one(
            {"_id": article_id},
            {"$set": {**article, "_id": article_id}},
            upsert=True,
        )
        if result.upserted_id:
            count += 1
    return count


async def get_all_articles(limit: int = 30) -> list[dict]:
    """Return articles for the homepage listing."""
    col = _get_db()["articles"]
    cursor = col.find(
        {},
        {
            "_id": 1, "title": 1, "quickSummary": 1, "coverImage": 1,
            "publisherName": 1, "publisherLogo": 1, "authorName": 1,
            "datePosted": 1, "category": 1, "sourceUrl": 1,
        }
    ).sort("datePosted", DESCENDING).limit(limit)

    docs = await cursor.to_list(length=limit)
    for doc in docs:
        doc["id"] = str(doc.pop("_id"))
        _serialize_dates(doc)
    return docs


def _serialize_dates(doc: dict) -> None:
    """Convert datetime and ObjectId values to JSON-safe strings."""
    for key, val in doc.items():
        if isinstance(val, datetime):
            doc[key] = val.isoformat()
        elif isinstance(val, ObjectId):
            doc[key] = str(val)


async def get_article_by_id(article_id: str) -> Optional[dict]:
    """Return full article by ID (for the detail page)."""
    col = _get_db()["articles"]
    doc = await col.find_one({"_id": article_id})
    if not doc:
        return None
    doc["id"] = str(doc.pop("_id"))
    _serialize_dates(doc)
    return doc


# ---------------------------------------------------------------------------
# Chats
# ---------------------------------------------------------------------------

async def save_chat_message(session_id: str, article_id: str, article_title: str,
                            message: dict) -> None:
    """Push a message into a chat session (create session if needed)."""
    col = _get_db()["chats"]
    now = datetime.now(timezone.utc)
    await col.update_one(
        {"sessionId": session_id},
        {
            "$push": {"messages": message},
            "$set": {"updatedAt": now, "articleTitle": article_title, "articleId": article_id},
            "$setOnInsert": {"createdAt": now},
        },
        upsert=True,
    )


async def get_chat_history(session_id: str) -> list[dict]:
    """Get conversation history for a session."""
    col = _get_db()["chats"]
    doc = await col.find_one({"sessionId": session_id})
    if not doc:
        return []
    return doc.get("messages", [])
