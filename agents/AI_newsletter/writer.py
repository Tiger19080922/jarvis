"""
writer.py — Four-step prompt chain.

Step 1: Gemini Flash + Google Search → research brief
Step 2: Gemini Flash → story plan (consulting structure)
Step 3: Gemini Flash → narrative (execute the plan)
Step 4: Gemini Flash → structure extraction (four HTML sections)
+ Subject line: Gemini Flash
"""

from google import genai
from google.genai import types
import json
import time
from typing import Dict

from config import FLASH, PRO, GOOGLE_API_KEY
from prompts import (
    RESEARCH_SYSTEM, RESEARCH_USER,
    PLANNING_SYSTEM, PLANNING_USER,
    NARRATIVE_SYSTEM, NARRATIVE_USER,
    EXTRACT_SYSTEM, EXTRACT_USER,
    SUBJECT_SYSTEM, SUBJECT_USER,
)

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=GOOGLE_API_KEY)
    return _client

SEARCH_TOOL = types.Tool(google_search=types.GoogleSearch())

PAUSE = 10  # seconds between steps (Gemini has more generous rate limits)


def _extract_json(text: str) -> dict:
    """Extract JSON object, robust to preamble and trailing text."""
    brace = text.find("{")
    if brace > 0:
        text = text[brace:]
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()
    depth = 0
    end = 0
    in_string = False
    escape = False
    for i, ch in enumerate(text):
        if escape:
            escape = False
            continue
        if ch == '\\' and in_string:
            escape = True
            continue
        if ch == '"' and not escape:
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end:
        text = text[:end]
    return json.loads(text)


def _call(model: str, system: str, user: str, max_tokens: int,
          step_name: str, trace=None) -> str:
    """Single Gemini call with logging. Retries once on 503."""
    for attempt in range(3):
        try:
            response = _get_client().models.generate_content(
                model=model,
                contents=user,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    max_output_tokens=max_tokens,
                    temperature=0.3,
                ),
            )
            text = response.text or ""
            if trace:
                trace.span(name=step_name,
                           input={"chars": len(user)},
                           output={"chars": len(text)})
            return text
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                wait = 30 * (attempt + 1)
                print(f"[writer] 503 on {step_name}, retrying in {wait}s... (attempt {attempt+1})")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError(f"[writer] {step_name} failed after 3 attempts")


# ─── STEP 1: RESEARCH ────────────────────────────────────────────────────────

def research(item: Dict, trace=None) -> str:
    """Gemini Flash + Google Search: build rich research brief."""
    print(f"[writer] step 1 — researching: {item['title'][:60]}")

    user = RESEARCH_USER.format(
        title=item["title"],
        summary=item["summary"],
        source=item["source"],
    )

    response = _get_client().models.generate_content(
        model=FLASH,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=RESEARCH_SYSTEM,
            max_output_tokens=2500,
            tools=[SEARCH_TOOL],
        ),
    )

    brief = response.text or ""
    print(f"[writer] research brief: {len(brief)} chars")

    if trace:
        trace.span(name="research", output={"chars": len(brief)})
    return brief


# ─── STEP 2: PLANNING ────────────────────────────────────────────────────────

def plan(item: Dict, research_brief: str, trace=None) -> str:
    """Build the story plan before writing."""
    print(f"[writer] step 2 — planning narrative structure...")

    user = PLANNING_USER.format(
        research_brief=research_brief,
        title=item["title"],
    )

    story_plan = _call(
        model=PRO,
        system=PLANNING_SYSTEM,
        user=user,
        max_tokens=1500,
        step_name="plan",
        trace=trace,
    )

    print(f"[writer] story plan: {len(story_plan)} chars")
    return story_plan


# ─── STEP 3: NARRATIVE WRITING ───────────────────────────────────────────────

def write_narrative(item: Dict, research_brief: str,
                    story_plan: str, trace=None) -> str:
    """Execute the plan as flowing narrative journalism. 600-900 words."""
    print(f"[writer] step 3 — writing narrative...")

    user = NARRATIVE_USER.format(
        story_plan=story_plan,
        research_brief=research_brief,
        title=item["title"],
        source=item["source"],
        url=item.get("url", ""),
    )

    narrative = _call(
        model=PRO,
        system=NARRATIVE_SYSTEM,
        user=user,
        max_tokens=2000,
        step_name="narrative",
        trace=trace,
    )

    word_count = len(narrative.split())
    print(f"[writer] narrative: {word_count} words")
    return narrative


# ─── STEP 4: STRUCTURE EXTRACTION ────────────────────────────────────────────

def extract_structure(narrative: str, item: Dict, trace=None) -> Dict:
    """Extract the four email sections from the narrative."""
    print(f"[writer] step 4 — extracting structure...")

    user = EXTRACT_USER.format(
        narrative=narrative,
        source=item["source"],
        url=item.get("url", ""),
    )

    text = _call(
        model=PRO,
        system=EXTRACT_SYSTEM,
        user=user,
        max_tokens=2000,
        step_name="extract",
        trace=trace,
    )

    try:
        story = _extract_json(text)
        return {
            "headline":       story.get("headline", item["title"]),
            "stat_number":    story.get("stat_number", ""),
            "stat_label":     story.get("stat_label", ""),
            "what_happened":  story.get("what_happened", ""),
            "why_it_matters": story.get("why_it_matters", ""),
            "india_lens":     story.get("india_lens", ""),
            "implication":    story.get("implication", ""),
            "source_name":    story.get("source_name", item["source"]),
            "source_url":     story.get("source_url", item.get("url", "")),
        }
    except Exception as e:
        print(f"[writer] JSON extraction error: {e}")
        print(f"[writer] raw text: {text[:300]}")
        half = len(narrative) // 2
        return {
            "headline":       item["title"],
            "stat_number":    "",
            "stat_label":     "",
            "what_happened":  narrative[:half],
            "why_it_matters": narrative[half:],
            "india_lens":     "",
            "implication":    "",
            "source_name":    item["source"],
            "source_url":     item.get("url", ""),
        }


# ─── FULL CHAIN ───────────────────────────────────────────────────────────────

def write_story(item: Dict, trace=None) -> Dict:
    """Run the full four-step chain."""
    brief = research(item, trace=trace)

    print(f"[writer] pausing {PAUSE}s...")
    time.sleep(PAUSE)

    story_plan = plan(item, brief, trace=trace)

    print(f"[writer] pausing {PAUSE}s...")
    time.sleep(PAUSE)

    narrative = write_narrative(item, brief, story_plan, trace=trace)

    print(f"[writer] pausing {PAUSE}s...")
    time.sleep(PAUSE)

    story = extract_structure(narrative, item, trace=trace)

    return story


# ─── SUBJECT LINE ─────────────────────────────────────────────────────────────

def write_subject_line(story: Dict, trace=None) -> str:
    """Write the email subject line."""
    hook = story.get("what_happened", "")[:200]

    user = SUBJECT_USER.format(
        headline=story["headline"],
        stat_number=story.get("stat_number", ""),
        stat_label=story.get("stat_label", ""),
        hook=hook,
    )

    response = _get_client().models.generate_content(
        model=FLASH,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=SUBJECT_SYSTEM,
            max_output_tokens=40,
            temperature=0.1,
        ),
    )

    return (response.text or "").strip('"\'').strip()
