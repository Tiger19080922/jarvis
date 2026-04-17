"""
essay_writer.py — Daily pivot essay pipeline.

Step 1 (Gemini Flash + Google Search): Source discovery — find best real articles.
Step 2 (Gemini Flash):                 Write 2000-word essay from source material.
Step 3 (Gemini Flash):                 Write role-specific pivot lens (150-200 words).
Step 4 (Gemini Flash):                 Extract key arguments for essay memory.
"""

import json
import time
from typing import Dict, List

from google import genai
from google.genai import types

from config import FLASH, PRO, GOOGLE_API_KEY
from curriculum import get_today_topic
from essay_memory import build_prior_coverage_block, save_essay
from essay_prompts import (
    ESSAY_SEARCH_SYSTEM, ESSAY_SEARCH_USER,
    ESSAY_WRITE_SYSTEM, ESSAY_WRITE_USER,
    PIVOT_LENS_SYSTEM, PIVOT_LENS_USER,
    EXTRACT_ARGS_SYSTEM, EXTRACT_ARGS_USER,
)

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=GOOGLE_API_KEY)
    return _client

SEARCH_TOOL = types.Tool(google_search=types.GoogleSearch())

PAUSE = 10  # seconds between steps


# ── STEP 1: SOURCE DISCOVERY ──────────────────────────────────────────────────

def _search_sources(entry: Dict) -> str:
    """Gemini Flash + Google Search: find the best real source material for today's angle."""
    print(f"[essay] step 1 — searching sources: {entry['topic']} / {entry['angle']}")

    user = ESSAY_SEARCH_USER.format(
        topic        = entry["topic"],
        focus        = entry["focus"],
        search_query = entry["search_query"],
        day_number   = entry["day_number"],
        phase        = entry["phase"],
    )

    response = _get_client().models.generate_content(
        model=FLASH,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=ESSAY_SEARCH_SYSTEM,
            max_output_tokens=2000,
            tools=[SEARCH_TOOL],
        ),
    )

    brief = response.text or ""
    print(f"[essay] research brief: {len(brief)} chars")
    return brief


# ── STEP 2: ESSAY WRITING ─────────────────────────────────────────────────────

def _write_essay(entry: Dict, research_brief: str, prior_coverage: str) -> str:
    """Write the 2000-word essay for today's specific angle."""
    print(f"[essay] step 2 — writing essay (angle: {entry['angle']})...")

    user = ESSAY_WRITE_USER.format(
        topic          = entry["topic"],
        angle          = entry["angle"],
        phase          = entry["phase"],
        day_number     = entry["day_number"],
        day_in_week    = entry["day_in_week"],
        days_remaining = entry["days_remaining"],
        focus          = entry["focus"],
        prior_coverage = prior_coverage,
        research_brief = research_brief,
    )

    response = _get_client().models.generate_content(
        model=PRO,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=ESSAY_WRITE_SYSTEM,
            max_output_tokens=4000,
            temperature=0.4,
        ),
    )

    essay = response.text or ""
    word_count = len(essay.split())
    print(f"[essay] essay: {word_count} words")
    return essay


# ── STEP 3: PIVOT LENS ────────────────────────────────────────────────────────

def _write_pivot_lens(entry: Dict, essay: str) -> str:
    """Write the role-specific pivot lens (150-200 words)."""
    print(f"[essay] step 3 — writing pivot lens (role: {entry['role_lens']})...")

    essay_opening = essay[:1000] + "..." if len(essay) > 1000 else essay

    user = PIVOT_LENS_USER.format(
        topic                = entry["topic"],
        role_lens            = entry["role_lens"],
        role_lens_description= entry["role_lens_description"],
        essay_opening        = essay_opening,
    )

    response = _get_client().models.generate_content(
        model=FLASH,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=PIVOT_LENS_SYSTEM,
            max_output_tokens=500,
            temperature=0.3,
        ),
    )

    pivot_lens = response.text or ""
    print(f"[essay] pivot lens: {len(pivot_lens.split())} words")
    return pivot_lens


# ── STEP 4: ARGUMENT EXTRACTION ───────────────────────────────────────────────

def _extract_arguments(essay: str) -> List[str]:
    """Extract 3-5 key arguments from the essay for memory storage."""
    print(f"[essay] step 4 — extracting key arguments for memory...")

    user = EXTRACT_ARGS_USER.format(essay_text=essay[:3000])

    response = _get_client().models.generate_content(
        model=FLASH,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=EXTRACT_ARGS_SYSTEM,
            max_output_tokens=300,
            temperature=0.1,
        ),
    )

    raw = (response.text or "").strip()

    try:
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        bracket = raw.find("[")
        if bracket >= 0:
            raw = raw[bracket:]
        args = json.loads(raw)
        if isinstance(args, list):
            print(f"[essay] extracted {len(args)} key arguments")
            return [str(a) for a in args[:5]]
    except Exception as e:
        print(f"[essay] argument extraction parse error: {e}")

    return []


# ── FULL PIPELINE ─────────────────────────────────────────────────────────────

def generate_essay() -> Dict:
    """
    Run the full four-step essay pipeline.

    Returns a dict ready for emailer.build_html():
      day_number, days_remaining, phase, week, topic, angle,
      role_lens, essay_text, pivot_lens
    """
    entry = get_today_topic()

    print(f"\n[essay] Day {entry['day_number']}/90 | {entry['phase']} | "
          f"{entry['topic']} | Day {entry['day_in_week']}/7")
    print(f"[essay] Angle:     {entry['angle']}")
    print(f"[essay] Role lens: {entry['role_lens']}")

    prior_coverage = build_prior_coverage_block(entry["topic"])
    if prior_coverage:
        print(f"[essay] Prior coverage block: {len(prior_coverage)} chars")
    else:
        print(f"[essay] No prior coverage for this topic yet")

    # Step 1: Search
    research_brief = _search_sources(entry)

    print(f"[essay] pausing {PAUSE}s...")
    time.sleep(PAUSE)

    # Step 2: Write
    essay_text = _write_essay(entry, research_brief, prior_coverage)

    print(f"[essay] pausing {PAUSE}s...")
    time.sleep(PAUSE)

    # Step 3: Pivot lens
    pivot_lens = _write_pivot_lens(entry, essay_text)

    print(f"[essay] pausing {PAUSE}s...")
    time.sleep(PAUSE)

    # Step 4: Extract arguments and save to memory
    key_arguments = _extract_arguments(essay_text)
    save_essay(
        day_number    = entry["day_number"],
        topic         = entry["topic"],
        angle         = entry["angle"],
        key_arguments = key_arguments,
    )

    return {
        "day_number":     entry["day_number"],
        "day_in_week":    entry["day_in_week"],
        "days_remaining": entry["days_remaining"],
        "phase":          entry["phase"],
        "week":           entry["week"],
        "topic":          entry["topic"],
        "angle":          entry["angle"],
        "role_lens":      entry["role_lens"],
        "essay_text":     essay_text,
        "pivot_lens":     pivot_lens,
    }
