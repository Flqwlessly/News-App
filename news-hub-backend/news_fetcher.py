from __future__ import annotations

import httpx
from config import NEWS_API_KEY, NEWS_API_BASE

TOP_TECH_SOURCES = [
    "techcrunch",
    "the-verge",
    "wired",
    "ars-technica",
    "engadget",
    "the-next-web",
    "recode",
    "hacker-news",
    "techradar",
]


async def fetch_tech_articles(page_size: int = 40) -> list[dict]:
    """
    Fetch recent articles from top tech publishers using /top-headlines.
    Returns raw NewsAPI article dicts for AI to filter and process.
    """
    sources_param = ",".join(TOP_TECH_SOURCES)

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(
            f"{NEWS_API_BASE}/top-headlines",
            params={
                "sources": sources_param,
                "pageSize": page_size,
                "apiKey": NEWS_API_KEY,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    raw_articles = data.get("articles", [])
    # Filter out removed / empty articles
    return [
        a for a in raw_articles
        if a.get("title")
        and a["title"] != "[Removed]"
        and a.get("url")
    ]
