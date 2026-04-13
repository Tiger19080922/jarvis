"""
essay_memory.py — Rolling 90-day essay history.

Tracks which angle was covered each day and the key arguments made,
so the writer never repeats the same angle or arguments within a topic week.

Stored in essay_memory.json alongside memory.json.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List

from config import MEMORY_FILE

ESSAY_MEMORY_FILE = os.path.join(os.path.dirname(MEMORY_FILE), "essay_memory.json")
ESSAY_MEMORY_DAYS = 90   # keep the full curriculum history


def _load() -> Dict:
    if not os.path.exists(ESSAY_MEMORY_FILE):
        return {"essays": []}
    with open(ESSAY_MEMORY_FILE, "r") as f:
        return json.load(f)


def _save(data: Dict) -> None:
    with open(ESSAY_MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def get_recent_essays(topic: str, days: int = 7) -> List[Dict]:
    """
    Return essays written on the same topic in the last N days.
    Used to build the 'prior coverage' context passed to the writer.
    """
    data   = _load()
    cutoff = datetime.now() - timedelta(days=days)
    return [
        e for e in data["essays"]
        if e.get("topic") == topic
        and datetime.fromisoformat(e["date"]) > cutoff
    ]


def build_prior_coverage_block(topic: str) -> str:
    """
    Returns a formatted string describing what has already been covered
    on this topic in the past 7 days. Empty string if nothing yet.
    Injected into the essay write prompt so the writer avoids repetition.
    """
    recent = get_recent_essays(topic, days=7)
    if not recent:
        return ""

    lines = ["PRIOR COVERAGE THIS WEEK (do NOT repeat these angles or arguments):"]
    for e in recent:
        lines.append(f"\nDay {e.get('day_number', '?')} — Angle: {e.get('angle', 'unknown')}")
        args = e.get("key_arguments", [])
        if args:
            for arg in args:
                lines.append(f"  - {arg}")

    lines.append(
        "\nYour essay today must take a DIFFERENT angle and make DIFFERENT arguments. "
        "If sources overlap, interpret them from a fresh perspective."
    )
    return "\n".join(lines)


def save_essay(
    day_number:     int,
    topic:          str,
    angle:          str,
    key_arguments:  List[str],
) -> None:
    """
    Save today's essay metadata to memory after writing.

    key_arguments: 3-5 short strings summarising the main points made.
    These are extracted by the writer after the essay is complete.
    """
    data = _load()
    data["essays"].append({
        "date":          datetime.now().isoformat(),
        "day_number":    day_number,
        "topic":         topic,
        "angle":         angle,
        "key_arguments": key_arguments,
    })

    # Prune entries older than ESSAY_MEMORY_DAYS
    cutoff = (datetime.now() - timedelta(days=ESSAY_MEMORY_DAYS)).isoformat()
    data["essays"] = [e for e in data["essays"] if e["date"] >= cutoff]
    _save(data)
    print(f"[essay_memory] saved day {day_number} — {topic}: {angle}")
