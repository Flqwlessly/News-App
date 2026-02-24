from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

import db_handler
import news_fetcher
import ai_chat

app = FastAPI(title="NewsHub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Sync: Fetch → AI process → Store
# ---------------------------------------------------------------------------

@app.post("/api/sync")
async def sync_articles(count: int = Query(10, ge=1, le=20)):
    """
    Full pipeline: fetch from top tech publishers, let AI select the best
    articles and generate summaries, then store in MongoDB.
    """
    raw = await news_fetcher.fetch_tech_articles(page_size=40)
    if not raw:
        return {"message": "No articles fetched from NewsAPI.", "fetched": 0, "new": 0}

    processed = await ai_chat.select_and_process_articles(raw, count=count)
    upserted = await db_handler.upsert_articles(processed)

    return {
        "fetched_from_api": len(raw),
        "ai_selected": len(processed),
        "new_in_db": upserted,
        "message": f"Synced {len(processed)} AI-curated articles ({upserted} new).",
    }


# ---------------------------------------------------------------------------
# Articles
# ---------------------------------------------------------------------------

@app.get("/api/articles")
async def list_articles(
    category: str = Query("", description="Filter by category"),
    limit: int = Query(30, ge=1, le=100),
):
    """Return articles from MongoDB for the homepage."""
    articles = await db_handler.get_all_articles(limit=limit)
    if category:
        articles = [a for a in articles if category.lower() in a.get("category", "").lower()]
    return {"articles": articles, "total": len(articles)}


@app.get("/api/articles/{article_id}")
async def get_article(article_id: str):
    """Return a single article with full content for the detail page."""
    article = await db_handler.get_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


# ---------------------------------------------------------------------------
# AI Chat
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    articleId: str
    articleTitle: str = ""
    articleSummary: str = ""
    articleContent: str = ""
    history: List[dict] = []
    message: str


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """
    Chat with Gemini about an article.
    The frontend sends the article context so the AI has full knowledge.
    """
    reply = await ai_chat.chat_about_article(
        article_title=req.articleTitle,
        article_summary=req.articleSummary,
        article_content=req.articleContent,
        conversation_history=req.history,
        user_message=req.message,
    )
    return {"reply": reply}


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health():
    return {"status": "ok"}
