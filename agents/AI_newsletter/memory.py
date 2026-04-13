"""
memory.py — Rolling 14-day story memory.

Stores story titles, URLs, and key entities from every run.
Deduplication runs against this before any item goes to the writer.
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict

from config import MEMORY_FILE, MEMORY_DAYS


def _load() -> Dict:
    """Load memory from disk. Returns empty structure if file doesn't exist."""
    if not os.path.exists(MEMORY_FILE):
        return {"stories": []}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def _save(data: Dict) -> None:
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def _normalise(text: str) -> str:
    """Lowercase + strip punctuation for fuzzy matching."""
    import re
    return re.sub(r"[^a-z0-9 ]", "", text.lower()).strip()


def get_recent_titles() -> List[str]:
    """Return normalised titles from the last MEMORY_DAYS days."""
    data = _load()
    cutoff = datetime.now() - timedelta(days=MEMORY_DAYS)
    return [
        _normalise(s["title"])
        for s in data["stories"]
        if datetime.fromisoformat(s["date"]) > cutoff
    ]


# Named entities that trigger entity-level dedup when two stories share one
# and are in the same category within the last 3 days.
_KNOWN_ENTITIES = [
    "sarvam", "krutrim", "anthropic", "openai", "google", "microsoft",
    "meity", "nasscom", "infosys", "tcs", "wipro", "reliance", "jio",
    "flipkart", "razorpay", "zerodha", "zomato", "swiggy", "paytm",
    "ai4bharat", "indiaai", "blume", "accel", "lightspeed", "stellaris",
    "haptik", "yellowai", "gnani", "observe", "workongrid", "satleo",
]


def _extract_entities(text: str) -> set:
    """Return named entities found in text."""
    words = set(text.lower().split())
    return {e for e in _KNOWN_ENTITIES if e in words}


def get_recent_entries(days: int = 14) -> list:
    """Return full story entries from the last N days."""
    data = _load()
    cutoff = datetime.now() - timedelta(days=days)
    return [
        s for s in data["stories"]
        if datetime.fromisoformat(s["date"]) > cutoff
    ]


def is_duplicate(title: str, category: str = "", threshold: float = 0.45) -> bool:
    """
    Return True if title is too similar to a recently seen story.

    Two-pass check:
    1. Token overlap >= threshold (lowered from 0.6 to 0.45) — strict title match
    2. Entity-level: same named entity + same category within last 3 days
       catches "Sarvam raises $350M" vs "Sarvam in talks for $300M funding"
    """
    candidate       = set(_normalise(title).split())
    candidate_ents  = _extract_entities(_normalise(title))

    if not candidate:
        return False

    recent = get_recent_entries(days=14)

    for entry in recent:
        seen_title = _normalise(entry.get("title", ""))
        seen_words = set(seen_title.split())

        if not seen_words:
            continue

        # Pass 1: token overlap
        overlap = len(candidate & seen_words) / len(candidate | seen_words)
        if overlap >= threshold:
            return True

        # Pass 2: entity-level dedup (same entity + same category within 3 days)
        if candidate_ents and category:
            seen_ents = _extract_entities(seen_title)
            shared    = candidate_ents & seen_ents
            if shared:
                seen_cat  = entry.get("cat", "")
                seen_date = datetime.fromisoformat(entry["date"])
                if (seen_cat == category
                        and (datetime.now() - seen_date).days <= 3):
                    return True

    return False


def save_stories(stories: List[Dict]) -> None:
    """
    Persist today's published stories to memory.
    Each story dict must have: title, url, category.
    """
    data = _load()
    today = datetime.now().isoformat()
    for story in stories:
        data["stories"].append({
            "title": story.get("title", ""),
            "url":   story.get("url", ""),
            "cat":   story.get("category", "OTHER"),
            "date":  today,
        })
    # Prune entries older than MEMORY_DAYS
    cutoff = (datetime.now() - timedelta(days=MEMORY_DAYS)).isoformat()
    data["stories"] = [s for s in data["stories"] if s["date"] >= cutoff]
    _save(data)
    print(f"[memory] saved {len(stories)} stories. "
          f"Total in memory: {len(data['stories'])}")


def status() -> Dict:
    """Return a summary of the current memory state — useful for logging."""
    data = _load()
    return {
        "total_stories": len(data["stories"]),
        "oldest": data["stories"][0]["date"] if data["stories"] else None,
        "newest": data["stories"][-1]["date"] if data["stories"] else None,
    }
