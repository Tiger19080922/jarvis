"""
feeds.py — RSS fetching and parsing.

Pulls from all configured feeds, filters by recency and AI relevance,
returns clean dicts ready for scoring.
"""

import feedparser
from datetime import datetime, timedelta
from typing import List, Dict
import time

from config import RSS_FEEDS, RSS_LOOKBACK_HOURS

# Keywords that must appear (case-insensitive) for an item to be kept.
# Broad enough to catch all relevant stories, tight enough to drop noise.
AI_KEYWORDS = [
    "artificial intelligence", "ai ", " ai", "machine learning", "deep learning",
    "llm", "large language model", "generative ai", "gen ai",
    "chatgpt", "claude", "gemini", "gpt",
    "sarvam", "krutrim", "ai4bharat", "nymble",
    "automation", "neural", "nlp", "computer vision",
    "data science", "foundation model", "startup", "funding",
    # Keep policy/enterprise even without explicit AI mention if from right source
    "meity", "nasscom", "digital india",
]


def _is_ai_relevant(title: str, summary: str) -> bool:
    text = (title + " " + summary).lower()
    return any(kw in text for kw in AI_KEYWORDS)


def _parse_date(entry) -> datetime:
    """Best-effort date parsing from feedparser entry."""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6])
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        return datetime(*entry.updated_parsed[:6])
    return datetime.now()  # fallback: treat as fresh


def fetch_all() -> List[Dict]:
    """
    Fetch all RSS feeds and return a flat list of recent AI-relevant items.
    Each item: {title, summary, url, source, date, category_hint}
    """
    cutoff = datetime.now() - timedelta(hours=RSS_LOOKBACK_HOURS)
    items = []
    seen_urls = set()

    for feed_config in RSS_FEEDS:
        url  = feed_config["url"]
        name = feed_config["name"]
        cat  = feed_config["category"]

        try:
            feed = feedparser.parse(url, agent="AIIndiaDigest/1.0")
            print(f"[feeds] {name}: {len(feed.entries)} entries fetched")

            for entry in feed.entries:
                pub_date = _parse_date(entry)
                if pub_date < cutoff:
                    continue  # too old

                link    = getattr(entry, "link", "")
                title   = getattr(entry, "title", "").strip()
                summary = getattr(entry, "summary", "")[:600].strip()

                if not title or not link:
                    continue
                if link in seen_urls:
                    continue  # cross-posted duplicate

                if not _is_ai_relevant(title, summary):
                    continue  # not AI related

                seen_urls.add(link)
                items.append({
                    "title":         title,
                    "summary":       summary,
                    "url":           link,
                    "source":        name,
                    "date":          pub_date.strftime("%b %d"),
                    "category_hint": cat,
                    "origin":        "rss",
                })

            time.sleep(0.3)  # polite delay between feed fetches

        except Exception as e:
            print(f"[feeds] ERROR fetching {name}: {e}")
            continue

    print(f"[feeds] total items after RSS filter: {len(items)}")
    return items
