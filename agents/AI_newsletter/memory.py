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


def is_duplicate(title: str, threshold: float = 0.6) -> bool:
    """
    Return True if title is too similar to a recently seen story.
    Uses simple token overlap — no external library needed.
    threshold: fraction of words that must overlap to be called duplicate.
    """
    candidate = set(_normalise(title).split())
    if not candidate:
        return False
    for seen in get_recent_titles():
        seen_words = set(seen.split())
        if not seen_words:
            continue
        overlap = len(candidate & seen_words) / len(candidate | seen_words)
        if overlap >= threshold:
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
