"""
Create MongoDB collections with JSON Schema validation and indexes.
Collections: articles, chats
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, DESCENDING
from config import MONGODB_URI, MONGODB_DB

CATEGORY_ENUM = ["AI", "Technology", "Startups", "Funding", "Machine Learning"]

ARTICLES_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "title",
            "coverImage",
            "publisherName",
            "publisherLogo",
            "authorName",
            "datePosted",
            "quickSummary",
            "sourceUrl",
            "category",
        ],
        "properties": {
            # ── Core fields ──
            "title": {
                "bsonType": "string",
                "description": "Article headline",
            },
            "coverImage": {
                "bsonType": "string",
                "description": "URL of the cover / thumbnail image",
            },
            "publisherName": {
                "bsonType": "string",
                "description": "Name of the publishing outlet",
            },
            "publisherLogo": {
                "bsonType": "string",
                "description": "URL of the publisher logo",
            },
            "authorName": {
                "bsonType": "string",
                "description": "Author / byline",
            },
            "datePosted": {
                "bsonType": "date",
                "description": "Publication date",
            },

            # ── AI-processed content ──
            "quickSummary": {
                "bsonType": "string",
                "description": "Short AI-generated summary",
            },
            "detailedSummary": {
                "bsonType": "string",
                "description": "Longer AI-generated summary",
            },
            "whyItMatters": {
                "bsonType": "string",
                "description": "AI-generated significance blurb",
            },

            # ── Metadata ──
            "sourceUrl": {
                "bsonType": "string",
                "pattern": "^https?://",
                "description": "Original article URL (must be unique)",
            },
            "originalContent": {
                "bsonType": "string",
                "description": "Raw scraped / API content",
            },
            "category": {
                "bsonType": "string",
                "enum": CATEGORY_ENUM,
                "description": f"One of {CATEGORY_ENUM}",
            },
            "createdAt": {
                "bsonType": "date",
            },
            "updatedAt": {
                "bsonType": "date",
            },
        },
    }
}

CHATS_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["sessionId", "articleId", "messages", "articleTitle", "createdAt"],
        "properties": {
            "sessionId": {
                "bsonType": "string",
                "description": "Unique chat session identifier",
            },
            "articleId": {
                "bsonType": "string",
                "description": "Reference to the article being discussed",
            },
            "articleTitle": {
                "bsonType": "string",
                "description": "Denormalized article title for quick display",
            },
            "messages": {
                "bsonType": "array",
                "description": "Conversation history",
                "items": {
                    "bsonType": "object",
                    "required": ["id", "text", "isUser", "timestamp"],
                    "properties": {
                        "id": {
                            "bsonType": "string",
                            "description": "Unique message id",
                        },
                        "text": {
                            "bsonType": "string",
                            "description": "Message body",
                        },
                        "isUser": {
                            "bsonType": "bool",
                            "description": "True if sent by the user",
                        },
                        "timestamp": {
                            "bsonType": "date",
                            "description": "When the message was sent",
                        },
                    },
                },
            },
            "createdAt": {"bsonType": "date"},
            "updatedAt": {"bsonType": "date"},
        },
    }
}


async def setup():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[MONGODB_DB]

    existing = await db.list_collection_names()

    # ── Articles collection ──
    print("=" * 60)
    print("ARTICLES COLLECTION")
    print("=" * 60)

    if "articles" in existing:
        print("  Collection exists — dropping to recreate with new schema …")
        await db.drop_collection("articles")

    await db.create_collection("articles", validator=ARTICLES_VALIDATOR)
    print("  ✓ Created 'articles' with JSON Schema validation")

    articles_col = db["articles"]
    article_indexes = [
        IndexModel([("category", ASCENDING), ("datePosted", DESCENDING)], name="category_date"),
        IndexModel([("sourceUrl", ASCENDING)], name="sourceUrl_unique", unique=True),
        IndexModel([("datePosted", DESCENDING)], name="datePosted_desc"),
        IndexModel([("publisherName", ASCENDING)], name="publisherName_asc"),
    ]
    result = await articles_col.create_indexes(article_indexes)
    print(f"  ✓ Indexes created: {result}")

    # ── Chats collection ──
    print("\n" + "=" * 60)
    print("CHATS COLLECTION")
    print("=" * 60)

    if "chats" in existing:
        print("  Collection exists — dropping to recreate with new schema …")
        await db.drop_collection("chats")

    await db.create_collection("chats", validator=CHATS_VALIDATOR)
    print("  ✓ Created 'chats' with JSON Schema validation")

    chats_col = db["chats"]
    chat_indexes = [
        IndexModel([("sessionId", ASCENDING), ("createdAt", DESCENDING)], name="session_created"),
        IndexModel([("articleId", ASCENDING), ("createdAt", DESCENDING)], name="article_created"),
        IndexModel([("sessionId", ASCENDING)], name="sessionId_lookup"),
    ]
    result = await chats_col.create_indexes(chat_indexes)
    print(f"  ✓ Indexes created: {result}")

    # ── Verify ──
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)

    for name in ["articles", "chats"]:
        info = await db.command("listCollections", filter={"name": name})
        col_info = info["cursor"]["firstBatch"][0]
        validator = col_info.get("options", {}).get("validator", {})
        schema = validator.get("$jsonSchema", {})
        required = schema.get("required", [])
        props = list(schema.get("properties", {}).keys())
        print(f"\n  Collection: {name}")
        print(f"    Required fields: {required}")
        print(f"    All properties:  {props}")

        idx_cursor = db[name].list_indexes()
        idx_list = await idx_cursor.to_list(length=50)
        print(f"    Indexes:")
        for idx in idx_list:
            print(f"      - {idx['name']}: {dict(idx['key'])}" +
                  (" (unique)" if idx.get("unique") else ""))

    client.close()
    print("\n✓ Database setup complete!\n")


if __name__ == "__main__":
    asyncio.run(setup())
