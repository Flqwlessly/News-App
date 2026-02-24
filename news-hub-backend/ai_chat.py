from __future__ import annotations

import json
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL

genai.configure(api_key=GEMINI_API_KEY)
_model = genai.GenerativeModel(GEMINI_MODEL)


async def select_and_process_articles(raw_articles: list[dict], count: int = 10) -> list[dict]:
    """
    Given a batch of raw NewsAPI articles, use Gemini to:
      1. Pick the `count` most relevant AI / Tech news
      2. Generate quickSummary, detailedSummary, whyItMatters for each
    Returns a list of processed article dicts ready for MongoDB.
    """
    condensed = []
    for i, a in enumerate(raw_articles):
        condensed.append({
            "index": i,
            "title": a.get("title", ""),
            "description": a.get("description", ""),
            "content": (a.get("content") or "")[:500],
            "source": a.get("source", {}).get("name", ""),
            "url": a.get("url", ""),
        })

    prompt = f"""You are a tech news editor. Below is a JSON array of {len(condensed)} articles from top tech publishers.

Your tasks:
1. Select the {count} BEST and MOST RELEVANT articles about AI, Technology, Startups, Funding, or Machine Learning.
2. For each selected article, produce:
   - "index": the original index from the input
   - "category": one of ["AI", "Technology", "Startups", "Funding", "Machine Learning"]
   - "quickSummary": a compelling 1-2 sentence summary for a news card (max 30 words)
   - "detailedSummary": a well-written 2-paragraph journalistic summary (150-200 words)
   - "whyItMatters": a concise paragraph on why this matters for the tech industry (50-80 words)

Return ONLY a valid JSON array of {count} objects. No markdown, no explanation.

Articles:
{json.dumps(condensed, ensure_ascii=False)}"""

    response = await _model.generate_content_async(prompt)
    text = response.text.strip()

    # Strip markdown fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]

    selected = json.loads(text)

    results = []
    for item in selected:
        idx = item["index"]
        raw = raw_articles[idx]
        source = raw.get("source", {})
        logo_letter = (source.get("name") or "N")[0].upper()

        results.append({
            "title": raw.get("title", ""),
            "coverImage": raw.get("urlToImage") or "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&h=400&fit=crop",
            "publisherName": source.get("name") or "Unknown",
            "publisherLogo": f"https://img.icons8.com/color/48/{logo_letter.lower()}.png",
            "authorName": raw.get("author") or "Unknown",
            "sourceUrl": raw.get("url") or "#",
            "originalContent": raw.get("content") or raw.get("description") or "",
            "category": item.get("category", "Technology"),
            "quickSummary": item.get("quickSummary", ""),
            "detailedSummary": item.get("detailedSummary", ""),
            "whyItMatters": item.get("whyItMatters", ""),
        })

    return results


async def chat_about_article(
    article_title: str,
    article_summary: str,
    article_content: str,
    conversation_history: list[dict],
    user_message: str,
) -> str:
    """
    Chat about a specific article with full context loaded.
    """
    system_prompt = (
        "You are a knowledgeable AI news assistant. The user is reading the article below. "
        "Answer their questions in depth using the article context. "
        "Be insightful and add relevant analysis. Keep responses under 200 words.\n\n"
        f"Title: {article_title}\n"
        f"Summary: {article_summary}\n"
        f"Full Content: {article_content}\n"
    )

    history = []
    for msg in conversation_history:
        role = "user" if msg.get("isUser") else "model"
        history.append({"role": role, "parts": [msg["text"]]})

    chat = _model.start_chat(history=history)
    response = await chat.send_message_async(
        f"{system_prompt}\n\nUser question: {user_message}"
    )
    return response.text
