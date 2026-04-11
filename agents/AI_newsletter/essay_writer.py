"""
essay_writer.py — Daily pivot essay pipeline.

Step 1 (Haiku + web_search): Source discovery — find best real articles.
Step 2 (Sonnet):             Write 2000-word essay from source material.
Step 3 (Haiku):              Write role-specific pivot lens (150-200 words).
"""

import time
from typing import Dict

import anthropic

from config import HAIKU, SONNET, ANTHROPIC_API_KEY
from curriculum import get_today_topic
from essay_prompts import (
    ESSAY_SEARCH_SYSTEM, ESSAY_SEARCH_USER,
    ESSAY_WRITE_SYSTEM, ESSAY_WRITE_USER,
    PIVOT_LENS_SYSTEM, PIVOT_LENS_USER,
)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SEARCH_TOOL = {
    "type": "web_search_20250305",
    "name": "web_search",
}

PAUSE = 15  # seconds between steps to avoid rate limit bursts


def _extract_text(response) -> str:
    return "".join(
        block.text for block in response.content
        if hasattr(block, "text")
    ).strip()


# ── STEP 1: SOURCE DISCOVERY ──────────────────────────────────────────────────

def _search_sources(entry: Dict) -> str:
    """Haiku + web_search: find the best real source material for today's topic."""
    print(f"[essay] step 1 — searching sources: {entry['topic']}")

    user = ESSAY_SEARCH_USER.format(
        topic=entry["topic"],
        focus=entry["focus"],
        search_query=entry["search_query"],
        day_number=entry["day_number"],
        phase=entry["phase"],
    )

    response = client.messages.create(
        model=HAIKU,
        max_tokens=3000,
        system=ESSAY_SEARCH_SYSTEM,
        tools=[SEARCH_TOOL],
        messages=[{"role": "user", "content": user}],
    )

    brief = _extract_text(response)
    print(f"[essay] research brief: {len(brief)} chars")
    return brief


# ── STEP 2: ESSAY WRITING ─────────────────────────────────────────────────────

def _write_essay(entry: Dict, research_brief: str) -> str:
    """Sonnet: write the 2000-word essay."""
    print(f"[essay] step 2 — writing essay...")

    user = ESSAY_WRITE_USER.format(
        topic=entry["topic"],
        phase=entry["phase"],
        day_number=entry["day_number"],
        days_remaining=entry["days_remaining"],
        focus=entry["focus"],
        research_brief=research_brief,
    )

    response = client.messages.create(
        model=SONNET,
        max_tokens=4000,
        system=ESSAY_WRITE_SYSTEM,
        messages=[{"role": "user", "content": user}],
    )

    essay = _extract_text(response)
    word_count = len(essay.split())
    print(f"[essay] essay: {word_count} words")
    return essay


# ── STEP 3: PIVOT LENS ────────────────────────────────────────────────────────

def _write_pivot_lens(entry: Dict, essay: str) -> str:
    """Haiku: write the role-specific pivot lens (150-200 words)."""
    print(f"[essay] step 3 — writing pivot lens (role: {entry['role_lens']})...")

    # Pass the opening of the essay so Haiku can make the lens specific
    essay_opening = essay[:1000] + "..." if len(essay) > 1000 else essay

    user = PIVOT_LENS_USER.format(
        topic=entry["topic"],
        role_lens=entry["role_lens"],
        role_lens_description=entry["role_lens_description"],
        essay_opening=essay_opening,
    )

    response = client.messages.create(
        model=HAIKU,
        max_tokens=500,
        system=PIVOT_LENS_SYSTEM,
        messages=[{"role": "user", "content": user}],
    )

    pivot_lens = _extract_text(response)
    print(f"[essay] pivot lens: {len(pivot_lens.split())} words")
    return pivot_lens


# ── FULL PIPELINE ─────────────────────────────────────────────────────────────

def generate_essay() -> Dict:
    """
    Run the full three-step essay pipeline.

    Returns a dict ready for emailer.build_html():
      day_number, days_remaining, phase, week, topic,
      role_lens, essay_text, pivot_lens
    """
    entry = get_today_topic()

    print(f"\n[essay] ── Day {entry['day_number']}/90 | {entry['phase']} | {entry['topic']}")
    print(f"[essay]    Role lens: {entry['role_lens']}")

    # Step 1
    research_brief = _search_sources(entry)

    print(f"[essay] pausing {PAUSE}s...")
    time.sleep(PAUSE)

    # Step 2
    essay_text = _write_essay(entry, research_brief)

    print(f"[essay] pausing {PAUSE}s...")
    time.sleep(PAUSE)

    # Step 3
    pivot_lens = _write_pivot_lens(entry, essay_text)

    return {
        "day_number":     entry["day_number"],
        "days_remaining": entry["days_remaining"],
        "phase":          entry["phase"],
        "week":           entry["week"],
        "topic":          entry["topic"],
        "role_lens":      entry["role_lens"],
        "essay_text":     essay_text,
        "pivot_lens":     pivot_lens,
    }
