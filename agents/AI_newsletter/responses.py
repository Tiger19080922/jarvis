"""
responses.py — Rolling 90-day log of your own answers to the daily
interrogation questions.

Mirrors the memory.py pattern (load/save a JSON file next to this module),
but does NOT prune on every write the way memory.py's 14-day story memory
does — this keeps a full RESPONSE_LOG_DAYS (90-day) history so you can look
back at how your reasoning has developed.

agent.py calls add_entry() after each run to seed today's questions with
empty answers. You fill them in locally with respond.py — see that file
for the one-command CLI.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from config import RESPONSES_FILE, RESPONSE_LOG_DAYS


def _load() -> Dict:
    if not os.path.exists(RESPONSES_FILE):
        return {"responses": []}
    with open(RESPONSES_FILE, "r") as f:
        return json.load(f)


def _save(data: Dict) -> None:
    with open(RESPONSES_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def add_entry(headline: str, source_url: str, questions: List[str]) -> None:
    """
    Seed today's entry with the interrogation questions and no answers yet.
    Called once per run, right after the questions are written.
    """
    data = _load()
    data["responses"].append({
        "date":       datetime.now().isoformat(),
        "headline":   headline,
        "source_url": source_url,
        "questions":  questions,
        "answers":    [],
    })

    cutoff = (datetime.now() - timedelta(days=RESPONSE_LOG_DAYS)).isoformat()
    data["responses"] = [r for r in data["responses"] if r["date"] >= cutoff]
    _save(data)
    print(f"[responses] seeded {len(questions)} questions for: {headline[:60]}")


def get_latest_unanswered() -> Optional[Dict]:
    """
    Return the most recent entry that still has unanswered questions,
    or None if everything is answered (or there is no history yet).
    """
    data = _load()
    pending = [r for r in data["responses"] if len(r["answers"]) < len(r["questions"])]
    if not pending:
        return None
    return max(pending, key=lambda r: r["date"])


def record_answer(entry_date: str, answer_text: str) -> None:
    """Append one answer to the entry matching entry_date, in question order."""
    data = _load()
    for entry in data["responses"]:
        if entry["date"] == entry_date:
            entry["answers"].append(answer_text)
            break
    else:
        raise ValueError(f"No response entry found for date {entry_date}")
    _save(data)


def get_recent_entries(days: int = RESPONSE_LOG_DAYS) -> List[Dict]:
    """Return full entries from the last N days, most recent first."""
    data   = _load()
    cutoff = datetime.now() - timedelta(days=days)
    entries = [
        r for r in data["responses"]
        if datetime.fromisoformat(r["date"]) > cutoff
    ]
    return sorted(entries, key=lambda r: r["date"], reverse=True)


def status() -> Dict:
    """Return a summary of the current response log."""
    data = _load()
    entries = data["responses"]
    answered = sum(1 for r in entries if r["questions"] and len(r["answers"]) >= len(r["questions"]))
    return {
        "total_entries":    len(entries),
        "fully_answered":   answered,
        "oldest":           entries[0]["date"]  if entries else None,
        "newest":           entries[-1]["date"] if entries else None,
    }
