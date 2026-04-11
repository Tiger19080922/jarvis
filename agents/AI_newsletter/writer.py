"""
writer.py — Four-step prompt chain.

Step 1: Haiku + web_search → research brief
Step 2: Sonnet → story plan (consulting structure)
Step 3: Sonnet → narrative (execute the plan)
Step 4: Sonnet → structure extraction (four HTML sections)
+ Subject line: Haiku
"""

import anthropic
import json
import time
from typing import Dict

from config import HAIKU, SONNET, ANTHROPIC_API_KEY
from prompts import (
    RESEARCH_SYSTEM, RESEARCH_USER,
    PLANNING_SYSTEM, PLANNING_USER,
    NARRATIVE_SYSTEM, NARRATIVE_USER,
    EXTRACT_SYSTEM, EXTRACT_USER,
    SUBJECT_SYSTEM, SUBJECT_USER,
)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SEARCH_TOOL = {
    "type": "web_search_20250305",
    "name": "web_search",
}

PAUSE = 20  # seconds between steps to avoid rate limits


def _extract_text(response) -> str:
    return "".join(
        block.text for block in response.content
        if hasattr(block, "text")
    ).strip()


def _extract_json(text: str) -> dict:
    """Extract JSON object, robust to preamble and trailing text."""
    # Find the opening brace
    brace = text.find("{")
    if brace > 0:
        text = text[brace:]
    # Strip markdown fences
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()
    # Find matching closing brace to trim trailing garbage
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
    """Single Claude call with logging."""
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = _extract_text(response)
    if trace:
        trace.span(name=step_name,
                   input={"chars": len(user)},
                   output={"chars": len(text)})
    return text


# ─── STEP 1: RESEARCH ────────────────────────────────────────────────────────

def research(item: Dict, trace=None) -> str:
    """Haiku + web_search: build rich research brief."""
    print(f"[writer] step 1 — researching: {item['title'][:60]}")

    user = RESEARCH_USER.format(
        title=item["title"],
        summary=item["summary"],
        source=item["source"],
    )

    response = client.messages.create(
        model=HAIKU,
        max_tokens=2500,
        system=RESEARCH_SYSTEM,
        tools=[SEARCH_TOOL],
        messages=[{"role": "user", "content": user}],
    )

    brief = _extract_text(response)
    print(f"[writer] research brief: {len(brief)} chars")

    if trace:
        trace.span(name="research", output={"chars": len(brief)})
    return brief


# ─── STEP 2: PLANNING ────────────────────────────────────────────────────────

def plan(item: Dict, research_brief: str, trace=None) -> str:
    """
    Sonnet: build the story plan before writing.
    Consultant thinking: central argument, question sequence, analogy choices,
    emotional arc, what to include, what to leave out, the conclusion.
    """
    print(f"[writer] step 2 — planning narrative structure...")

    user = PLANNING_USER.format(
        research_brief=research_brief,
        title=item["title"],
    )

    story_plan = _call(
        model=SONNET,
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
    """
    Sonnet: execute the plan as flowing narrative journalism.
    600-900 words. Plain English after every stat. Analogies throughout.
    """
    print(f"[writer] step 3 — writing narrative...")

    user = NARRATIVE_USER.format(
        story_plan=story_plan,
        research_brief=research_brief,
        title=item["title"],
        source=item["source"],
        url=item.get("url", ""),
    )

    narrative = _call(
        model=SONNET,
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
    """
    Sonnet: extract the four email sections from the narrative.
    Uses Sonnet (not Haiku) to handle the full token length reliably.
    """
    print(f"[writer] step 4 — extracting structure...")

    user = EXTRACT_USER.format(
        narrative=narrative,
        source=item["source"],
        url=item.get("url", ""),
    )

    text = _call(
        model=SONNET,
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
        # Fallback: split narrative into sections manually
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
    """
    Run the full four-step chain with pauses between each step
    to avoid hitting the token rate limit.
    """
    # Step 1: Research
    brief = research(item, trace=trace)

    print(f"[writer] pausing {PAUSE}s...")
    time.sleep(PAUSE)

    # Step 2: Plan
    story_plan = plan(item, brief, trace=trace)

    print(f"[writer] pausing {PAUSE}s...")
    time.sleep(PAUSE)

    # Step 3: Write
    narrative = write_narrative(item, brief, story_plan, trace=trace)

    print(f"[writer] pausing {PAUSE}s...")
    time.sleep(PAUSE)

    # Step 4: Extract
    story = extract_structure(narrative, item, trace=trace)

    return story


# ─── SUBJECT LINE ─────────────────────────────────────────────────────────────

def write_subject_line(story: Dict, trace=None) -> str:
    """Haiku writes the subject line."""
    hook = story.get("what_happened", "")[:200]

    user = SUBJECT_USER.format(
        headline=story["headline"],
        stat_number=story.get("stat_number", ""),
        stat_label=story.get("stat_label", ""),
        hook=hook,
    )

    response = client.messages.create(
        model=HAIKU,
        max_tokens=40,
        system=SUBJECT_SYSTEM,
        messages=[{"role": "user", "content": user}],
    )

    return _extract_text(response).strip('"\'')
