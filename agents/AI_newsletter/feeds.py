"""
feeds.py — RSS fetching and parsing.

Pulls from all configured feeds, filters by recency and AI relevance,
returns clean dicts ready for scoring.
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict
import time

from config import RSS_FEEDS, RSS_LOOKBACK_HOURS, VC_BLOGS, VC_LOOKBACK_DAYS, MAX_VC_POSTS

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


# ── VC BLOG THESES ────────────────────────────────────────────────────────────
# Surfaces recent Tier 1 Indian VC blog posts as raw candidate material.
# writer.py grounds the actual excerpt quote via Gemini + google_search over
# this pool, rather than scraping full article bodies here — see README.md
# "VC blog sourcing" for why (Nexus RSS <link> URLs 404; most VC sites are
# client-rendered SPAs with no server-side article text to scrape reliably).

def _fetch_vc_rss(source: Dict, cutoff: datetime) -> List[Dict]:
    """RSS-based VC blog (currently: Nexus Venture Partners)."""
    posts = []
    try:
        feed = feedparser.parse(source["url"], agent="AIIndiaDigest/1.0")
        print(f"[feeds] {source['name']}: {len(feed.entries)} entries fetched")
        for entry in feed.entries:
            pub_date = _parse_date(entry)
            if pub_date < cutoff:
                continue
            title = getattr(entry, "title", "").strip()
            link  = getattr(entry, "link", "")
            if not title:
                continue
            posts.append({
                "title":  title,
                "url":    link,
                "source": source["name"],
                "date":   pub_date.strftime("%b %d, %Y"),
            })
    except Exception as e:
        print(f"[feeds] ERROR fetching VC RSS {source['name']}: {e}")
    return posts


def _fetch_vc_scrape(source: Dict, cutoff: datetime) -> List[Dict]:
    """Scrape a server-rendered VC blog listing page (currently: Peak XV Partners)."""
    posts = []
    try:
        resp = requests.get(
            source["url"],
            headers={"User-Agent": "Mozilla/5.0 (compatible; AIIndiaDigest/1.0)"},
            timeout=15,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Peak XV markup: <a class="insights_link-in" href="/insight/...">
        #   <h3 class="resource_heading">Title</h3>
        #   ... <div fs-list-field="date">July 23, 2026</div>
        cards = soup.select("a.insights_link-in")
        seen_urls = set()
        for card in cards:
            heading = card.select_one(".resource_heading")
            date_el = card.select_one('[fs-list-field="date"]')
            if not heading or not date_el:
                continue

            href = card.get("href", "")
            url = href if href.startswith("http") else f"https://www.peakxv.com{href}"
            if url in seen_urls:
                continue  # listing page renders each card twice (grid + list view)

            title = heading.get_text(strip=True)
            date_text = date_el.get_text(strip=True)
            try:
                pub_date = datetime.strptime(date_text, "%B %d, %Y")
            except ValueError:
                continue
            if pub_date < cutoff:
                continue

            seen_urls.add(url)
            posts.append({
                "title":  title,
                "url":    url,
                "source": source["name"],
                "date":   pub_date.strftime("%b %d, %Y"),
            })
    except Exception as e:
        print(f"[feeds] ERROR scraping VC blog {source['name']}: {e}")
    return posts


def fetch_vc_theses() -> List[Dict]:
    """
    Fetch recent Tier 1 Indian VC blog posts across VC_BLOGS.
    Each item: {title, url, source, date}
    Returns at most MAX_VC_POSTS items, most recent first.
    """
    cutoff = datetime.now() - timedelta(days=VC_LOOKBACK_DAYS)
    posts: List[Dict] = []

    for vc in VC_BLOGS:
        if vc["type"] == "rss":
            posts.extend(_fetch_vc_rss(vc, cutoff))
        elif vc["type"] == "scrape":
            posts.extend(_fetch_vc_scrape(vc, cutoff))
        time.sleep(0.3)

    posts.sort(key=lambda p: datetime.strptime(p["date"], "%b %d, %Y"), reverse=True)
    posts = posts[:MAX_VC_POSTS]

    print(f"[feeds] VC theses: {len(posts)} candidate posts from {len(VC_BLOGS)} firms")
    return posts
