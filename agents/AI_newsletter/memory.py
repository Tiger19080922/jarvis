"""
memory.py — Rolling 14-day story memory.

Stores story titles, URLs, and key entities from every run.
Deduplication runs against this before any item goes to the writer.

Dedup strategy (three passes):
  Pass 1 — Token overlap >= 0.45 (catches near-identical titles)
  Pass 2 — Entity + category within N days (catches "Sarvam $300M" vs "Sarvam $350M")
            Window: FUNDING=7 days, POLICY=5 days, others=3 days
  Pass 3 — Topic fingerprint: (entity, event_type) within 7 days
            Catches the same funding round / policy event across multiple outlets

Within-run dedup is handled by dedup_batch() — call this BEFORE is_duplicate()
to remove same-run duplicates that haven't hit memory yet.
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict

from config import MEMORY_FILE, MEMORY_DAYS


# ── Entity + event-type taxonomy ─────────────────────────────────────────────

_KNOWN_ENTITIES = [
    "sarvam", "krutrim", "anthropic", "openai", "google", "microsoft",
    "meity", "nasscom", "infosys", "tcs", "wipro", "reliance", "jio",
    "flipkart", "razorpay", "zerodha", "zomato", "swiggy", "paytm",
    "ai4bharat", "indiaai", "blume", "accel", "lightspeed", "stellaris",
    "haptik", "yellowai", "gnani", "observe", "workongrid", "satleo",
    "zoho", "freshworks", "browserstack", "postman", "unacademy", "byju",
    "ola", "nykaa", "meesho", "cred", "groww", "zepto", "blinkit",
]

# Pass 2 (entity+category window) only applies to these closely-tracked entities.
# For large global players (OpenAI, Google, Microsoft) Pass 2 would be too broad —
# they publish genuinely different stories in the same category every day.
# For them, rely on Pass 1 (title overlap) and Pass 3 (fingerprint) only.
_PASS2_ENTITIES = {
    "sarvam", "krutrim", "ai4bharat", "indiaai", "meity", "nasscom",
    "workongrid", "satleo", "haptik", "yellowai", "gnani",
}

# Keywords that identify the *type* of event — used to build topic fingerprints
_FUNDING_KEYWORDS   = {"funding", "raises", "raised", "raise", "round", "valuation",
                       "investment", "invested", "invest", "mn", "cr", "million",
                       "billion", "series", "seed", "pre-seed"}
_POLICY_KEYWORDS    = {"governance", "regulation", "guidelines", "policy", "framework",
                       "ministry", "meity", "nasscom", "indiaai", "rules", "compliance",
                       "advisory", "government", "govt", "panel", "committee"}
_LAUNCH_KEYWORDS    = {"launches", "launch", "launched", "releases", "released",
                       "release", "introduces", "announced", "unveils", "unveil",
                       "debuts", "debut"}
_SHUTDOWN_KEYWORDS  = {"shuts", "shutdown", "offline", "closes", "closed", "discontinues"}


# ── Entity window by category ─────────────────────────────────────────────────
# How many days to block a story with the same entity + category
_ENTITY_WINDOW = {
    "FUNDING":    7,
    "POLICY":     5,
    "RESEARCH":   3,
    "ENTERPRISE": 3,
    "OTHER":      2,
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _normalise(text: str) -> str:
    """Lowercase + strip punctuation for fuzzy matching."""
    return re.sub(r"[^a-z0-9 ]", "", text.lower()).strip()


def _extract_entities(text: str) -> set:
    """Return known named entities found in text."""
    words = set(text.lower().split())
    return {e for e in _KNOWN_ENTITIES if e in words}


def _event_type(text: str) -> str:
    """
    Classify the *type* of event described in the title.
    Returns one of: funding | policy | launch | shutdown | general
    """
    words = set(_normalise(text).split())
    if words & _FUNDING_KEYWORDS:
        return "funding"
    if words & _POLICY_KEYWORDS:
        return "policy"
    if words & _SHUTDOWN_KEYWORDS:
        return "shutdown"
    if words & _LAUNCH_KEYWORDS:
        return "launch"
    return "general"


def _topic_fingerprints(title: str) -> set:
    """
    Return a set of (entity, event_type) tuples for a title.
    A story with fingerprint ("sarvam", "funding") blocks any future story
    with the same fingerprint for FINGERPRINT_WINDOW days.
    """
    entities = _extract_entities(title)
    event    = _event_type(title)
    if not entities or event == "general":
        return set()
    return {(e, event) for e in entities}


FINGERPRINT_WINDOW = 7  # days — topic fingerprint blocking horizon


# ── Storage ───────────────────────────────────────────────────────────────────

def _load() -> Dict:
    if not os.path.exists(MEMORY_FILE):
        return {"stories": []}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def _save(data: Dict) -> None:
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


# ── Public read helpers ───────────────────────────────────────────────────────

def get_recent_titles() -> List[str]:
    """Return normalised titles from the last MEMORY_DAYS days."""
    data   = _load()
    cutoff = datetime.now() - timedelta(days=MEMORY_DAYS)
    return [
        _normalise(s["title"])
        for s in data["stories"]
        if datetime.fromisoformat(s["date"]) > cutoff
    ]


def get_recent_entries(days: int = 14) -> list:
    """Return full story entries from the last N days."""
    data   = _load()
    cutoff = datetime.now() - timedelta(days=days)
    return [
        s for s in data["stories"]
        if datetime.fromisoformat(s["date"]) > cutoff
    ]


# ── Core dedup ────────────────────────────────────────────────────────────────

def is_duplicate(title: str, category: str = "", threshold: float = 0.45) -> bool:
    """
    Return True if title is too similar to a recently seen story.

    Three-pass check:
    1. Token overlap >= threshold
    2. Entity + category within category-specific window
    3. Topic fingerprint (entity + event_type) within FINGERPRINT_WINDOW days
    """
    norm_title     = _normalise(title)
    candidate      = set(norm_title.split())
    candidate_ents = _extract_entities(norm_title)
    candidate_fps  = _topic_fingerprints(norm_title)

    if not candidate:
        return False

    entity_window = _ENTITY_WINDOW.get(category.upper(), 3)
    recent        = get_recent_entries(days=max(MEMORY_DAYS, FINGERPRINT_WINDOW))

    for entry in recent:
        seen_norm  = _normalise(entry.get("title", ""))
        seen_words = set(seen_norm.split())
        seen_date  = datetime.fromisoformat(entry["date"])
        days_ago   = (datetime.now() - seen_date).days

        if not seen_words:
            continue

        # Pass 1: token overlap
        overlap = len(candidate & seen_words) / len(candidate | seen_words)
        if overlap >= threshold:
            return True

        # Pass 2: entity + category within window (tracked entities only)
        if candidate_ents and category:
            tracked_candidate = candidate_ents & _PASS2_ENTITIES
            if tracked_candidate:
                seen_ents = _extract_entities(seen_norm)
                if (tracked_candidate & seen_ents
                        and entry.get("cat", "") == category.upper()
                        and days_ago <= entity_window):
                    return True

        # Pass 3: topic fingerprint
        if candidate_fps:
            seen_fps = _topic_fingerprints(seen_norm)
            if candidate_fps & seen_fps and days_ago <= FINGERPRINT_WINDOW:
                return True

    return False


def dedup_batch(items: List[Dict]) -> List[Dict]:
    """
    Remove within-run duplicates BEFORE checking against memory.
    Keeps the first occurrence of each (entity, event_type) fingerprint
    and title-overlap cluster within the same batch.

    Call this in score_and_filter() before is_duplicate().
    """
    seen_fps:    set = set()
    seen_titles: list = []  # list of normalised word-sets
    kept:        list = []

    for item in items:
        title     = item.get("title", "")
        norm      = _normalise(title)
        words     = set(norm.split())
        fps       = _topic_fingerprints(norm)
        category  = item.get("category", "")

        # Within-batch token overlap check
        is_dup = False
        for seen_words in seen_titles:
            if not seen_words:
                continue
            overlap = len(words & seen_words) / len(words | seen_words) if (words | seen_words) else 0
            if overlap >= 0.45:
                is_dup = True
                break

        # Within-batch fingerprint check
        if not is_dup and fps:
            if fps & seen_fps:
                is_dup = True

        if not is_dup:
            kept.append(item)
            seen_titles.append(words)
            seen_fps.update(fps)

    removed = len(items) - len(kept)
    if removed:
        print(f"[memory] within-run dedup removed {removed} items.")
    return kept


# ── Write ─────────────────────────────────────────────────────────────────────

def save_stories(stories: List[Dict]) -> None:
    """
    Persist today's published stories to memory.
    Each story dict must have: title, url, category.
    """
    data  = _load()
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
    """Return a summary of the current memory state."""
    data = _load()
    return {
        "total_stories": len(data["stories"]),
        "oldest": data["stories"][0]["date"]  if data["stories"] else None,
        "newest": data["stories"][-1]["date"] if data["stories"] else None,
    }
