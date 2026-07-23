"""
writer.py — Raw-facts prompt chain.

Step 1: Gemini Flash + Google Search → research brief
Step 2: Gemini Flash → fact plan (ordering, not argument-building)
Step 3: Gemini Flash → factual write-up (execute the plan)
Step 4: Gemini Flash → structure extraction (raw-facts fields)
Step 5: Gemini Pro + Google Search → VC thesis excerpt (grounded quote)
Step 6: Gemini Flash → interrogation questions
+ Subject line: Gemini Flash
"""

from google import genai
from google.genai import types
import json
import re
import time
from typing import Dict, List

from config import FLASH, PRO, GOOGLE_API_KEY
from prompts import (
    RESEARCH_SYSTEM, RESEARCH_USER,
    PLANNING_SYSTEM, PLANNING_USER,
    NARRATIVE_SYSTEM, NARRATIVE_USER,
    EXTRACT_SYSTEM, EXTRACT_USER,
    VC_EXCERPT_SYSTEM, VC_EXCERPT_USER,
    INTERROGATION_SYSTEM, INTERROGATION_USER,
    SUBJECT_SYSTEM, SUBJECT_USER,
    BANNED_SYNTHESIS_PHRASES,
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


def _extract_json_array(text: str) -> list:
    """Extract a JSON array, robust to preamble/markdown fences."""
    text = text.strip()
    bracket = text.find("[")
    if bracket > 0:
        text = text[bracket:]
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()
    depth = 0
    end = 0
    for i, ch in enumerate(text):
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end:
        text = text[:end]
    return json.loads(text)


_BANNED_SENTENCE_RE = re.compile(
    r"(?:(?<=^)|(?<=[.!?]\s))(" +
    "|".join(re.escape(p) for p in BANNED_SYNTHESIS_PHRASES) +
    r")[^.!?]*[.!?]",
    re.IGNORECASE,
)


def _strip_synthesis_language(text: str) -> str:
    """
    Safety net: delete any sentence starting with a banned synthesis phrase
    (e.g. "This means...", "The implication is..."). Applied to every
    extracted field so no field can sneak conclusion-for-the-reader language
    past the prompt-level instructions.
    """
    if not text:
        return text
    cleaned = _BANNED_SENTENCE_RE.sub("", text)
    return re.sub(r"\s{2,}", " ", cleaned).strip()


def _call(model: str, system: str, user: str, max_tokens: int,
          step_name: str, trace=None, thinking: bool = False) -> str:
    """Single Gemini call with logging. Retries once on 503.
    thinking=False disables the thinking budget to save tokens on structured steps."""
    for attempt in range(3):
        try:
            cfg = types.GenerateContentConfig(
                system_instruction=system,
                max_output_tokens=max_tokens,
                temperature=0.3,
            )
            if not thinking:
                cfg.thinking_config = types.ThinkingConfig(thinking_budget=0)
            response = _get_client().models.generate_content(
                model=model,
                contents=user,
                config=cfg,
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
        max_tokens=3000,
        step_name="narrative",
        trace=trace,
        thinking=True,   # narrative writing benefits from reasoning
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
        max_tokens=4000,    # needs room for full JSON — thinking disabled to not waste tokens
        step_name="extract",
        trace=trace,
    )

    try:
        story = _extract_json(text)
        fields = {
            "headline":      story.get("headline", item["title"]),
            "stat_number":   story.get("stat_number", ""),
            "stat_label":    story.get("stat_label", ""),
            "what_happened": story.get("what_happened", ""),
            "funding_facts": story.get("funding_facts", ""),
            "india_lens":    story.get("india_lens", ""),
            "source_name":   story.get("source_name", item["source"]),
            "source_url":    story.get("source_url", item.get("url", "")),
        }
    except Exception as e:
        print(f"[writer] JSON extraction error: {e}")
        print(f"[writer] raw text: {text[:300]}")
        half = len(narrative) // 2
        fields = {
            "headline":      item["title"],
            "stat_number":   "",
            "stat_label":    "",
            "what_happened": narrative[:half],
            "funding_facts": narrative[half:],
            "india_lens":    "",
            "source_name":   item["source"],
            "source_url":    item.get("url", ""),
        }

    # Safety net: strip any sentence that still opens with banned
    # synthesis language, in every text field.
    for field in ("headline", "what_happened", "funding_facts", "india_lens"):
        fields[field] = _strip_synthesis_language(fields[field])

    return fields


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


# ─── STEP 5: VC THESIS EXCERPT ────────────────────────────────────────────────

def write_vc_excerpt(story: Dict, vc_posts: List[Dict], trace=None) -> Dict:
    """
    Gemini Pro + Google Search: pick the most thematically relevant VC post
    from vc_posts and ground a real, verbatim excerpt from it via search.

    Returns {"excerpt": str, "firm": str, "post_title": str, "post_url": str}.
    All empty strings if no candidate posts or nothing verifiably relevant.
    """
    if not vc_posts:
        print("[writer] step 5 — no VC posts available, skipping excerpt")
        return {"excerpt": "", "firm": "", "post_title": "", "post_url": ""}

    print(f"[writer] step 5 — grounding VC thesis excerpt from {len(vc_posts)} candidates...")

    posts_block = "\n".join(
        f"- [{p['source']}] {p['title']} ({p['date']}) — {p['url']}"
        for p in vc_posts
    )

    user = VC_EXCERPT_USER.format(
        headline=story.get("headline", ""),
        what_happened=story.get("what_happened", "")[:500],
        vc_posts=posts_block,
    )

    try:
        response = _get_client().models.generate_content(
            model=PRO,
            contents=user,
            config=types.GenerateContentConfig(
                system_instruction=VC_EXCERPT_SYSTEM,
                max_output_tokens=800,
                temperature=0.2,
                tools=[SEARCH_TOOL],
            ),
        )
        if trace:
            trace.span(name="vc_excerpt", output={"chars": len(response.text or "")})

        result = _extract_json(response.text or "")
        excerpt = {
            "excerpt":    result.get("excerpt", ""),
            "firm":       result.get("firm", ""),
            "post_title": result.get("post_title", ""),
            "post_url":   result.get("post_url", ""),
        }
        if excerpt["excerpt"]:
            print(f"[writer] VC excerpt found: {excerpt['firm']} — \"{excerpt['excerpt'][:60]}\"")
        else:
            print("[writer] no verifiably relevant VC excerpt found")
        return excerpt
    except Exception as e:
        print(f"[writer] VC excerpt extraction error: {e}")
        return {"excerpt": "", "firm": "", "post_title": "", "post_url": ""}


# ─── STEP 6: INTERROGATION QUESTIONS ──────────────────────────────────────────

def write_interrogation_questions(story: Dict, vc_excerpt: Dict, trace=None) -> List[str]:
    """Gemini Flash: 3-5 hard, specific, VC-interviewer-style follow-up questions."""
    print("[writer] step 6 — writing interrogation questions...")

    user = INTERROGATION_USER.format(
        headline=story.get("headline", ""),
        what_happened=story.get("what_happened", ""),
        funding_facts=story.get("funding_facts", ""),
        vc_excerpt=vc_excerpt.get("excerpt", "") or "(none found)",
        vc_firm=vc_excerpt.get("firm", "") or "n/a",
    )

    response = _get_client().models.generate_content(
        model=FLASH,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=INTERROGATION_SYSTEM,
            max_output_tokens=500,
            temperature=0.6,
        ),
    )
    if trace:
        trace.span(name="interrogation_questions", output={"chars": len(response.text or "")})

    try:
        questions = _extract_json_array(response.text or "")
        questions = [str(q).strip() for q in questions if str(q).strip()][:5]
        print(f"[writer] {len(questions)} interrogation questions written")
        return questions
    except Exception as e:
        print(f"[writer] interrogation question parse error: {e}")
        return []


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
