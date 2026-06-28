"""
VOID — News Service
Tech news from Hacker News + Dev.to + optional NewsAPI
"""

import requests
from typing import List, Optional
from datetime import datetime
import config

# Cache to avoid rate limiting
_news_cache = {"data": None, "timestamp": 0}
CACHE_TTL = 1800  # 30 minutes


def get_tech_news(max_items: int = 5) -> List[str]:
    """Get top tech news headlines relevant to Karthik's interests."""
    global _news_cache

    now = datetime.now().timestamp()
    if _news_cache["data"] and (now - _news_cache["timestamp"]) < CACHE_TTL:
        return _news_cache["data"][:max_items]

    stories = []

    # Source 1: Hacker News (top 10 stories)
    try:
        resp = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10
        )
        resp.raise_for_status()
        top_ids = resp.json()[:10]
        for item_id in top_ids:
            try:
                item_resp = requests.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json",
                    timeout=5,
                )
                item = item_resp.json()
                title = item.get("title", "")
                url = item.get("url", f"https://news.ycombinator.com/item?id={item_id}")
                if title:
                    stories.append(f"🔗 {title}\n   {url}")
            except Exception:
                continue
    except Exception:
        pass

    # Source 2: Dev.to trending
    try:
        resp = requests.get(
            "https://dev.to/api/articles?top=5&per_page=5", timeout=10
        )
        resp.raise_for_status()
        for article in resp.json()[:5]:
            title = article.get("title", "")
            url = article.get("url", "")
            if title:
                stories.append(f"📝 {title}\n   {url}")
    except Exception:
        pass

    # Source 3: NewsAPI (if key available)
    if config.NEWSAPI_KEY:
        try:
            resp = requests.get(
                "https://newsapi.org/v2/top-headlines",
                params={
                    "q": "AI OR LLM OR machine learning OR developer",
                    "apiKey": config.NEWSAPI_KEY,
                    "pageSize": 5,
                    "language": "en",
                },
                timeout=10,
            )
            resp.raise_for_status()
            for article in resp.json().get("articles", [])[:5]:
                title = article.get("title", "")
                url = article.get("url", "")
                if title:
                    stories.append(f"📰 {title}\n   {url}")
        except Exception:
            pass

    # Deduplicate and limit
    seen = set()
    unique_stories = []
    for story in stories:
        key = story.split("\n")[0]
        if key not in seen:
            seen.add(key)
            unique_stories.append(story)

    result = unique_stories[:max_items] if unique_stories else [
        "No tech news fetched bro — check internet connection or API keys"
    ]

    _news_cache["data"] = result
    _news_cache["timestamp"] = now
    return result


def get_tech_news_formatted(max_items: int = 4) -> str:
    """Get tech news formatted for the daily brief."""
    news = get_tech_news(max_items)
    if not news or "No tech news" in news[0]:
        return "🌐 Tech news fetch avvaledhu"

    lines = ["🌐 **Tech News**"]
    for i, item in enumerate(news[:max_items], 1):
        lines.append(f"{i}. {item}")

    return "\n".join(lines)
