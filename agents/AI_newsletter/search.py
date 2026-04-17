"""
search.py — Gemini Google Search tool for gap filling.

Runs targeted queries for content RSS cannot reach.
Uses Gemini's built-in Google Search grounding.
"""

from google import genai
from google.genai import types
import json
from datetime import datetime
from typing import List, Dict

from config import FLASH, SEARCH_QUERIES, GOOGLE_API_KEY

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=GOOGLE_API_KEY)
    return _client

SEARCH_TOOL = types.Tool(google_search=types.GoogleSearch())

SEARCH_SYSTEM = (
    f"Today is {datetime.now().strftime('%B %d, %Y')}. "
    "You are a news researcher for an AI India newsletter. "
    "Search for the query and extract distinct news items from the last 48 hours only. "
    "For each item found return a JSON array. Each element: "
    '{"title": str, "summary": str (max 150 words), "url": str, "source": str, "date": str}. '
    "Start your response directly with [ and return ONLY the JSON array. "
    "No preamble, no explanation, no markdown. "
    "If nothing relevant found in last 48 hours, return []."
)


def _extract_items(text: str) -> List[Dict]:
    """Parse Gemini's response into a list of story dicts."""
    if not text:
        return []

    text = text.strip()
    bracket = text.find("[")
    if bracket < 0:
        return []
    text = text[bracket:]

    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]

    # Find the matching closing bracket to strip any grounding citations appended after
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

    try:
        items = json.loads(text.strip())
        if not isinstance(items, list):
            return []
        result = []
        for item in items:
            if not item.get("title"):
                continue
            result.append({
                "title":         item.get("title", "").strip(),
                "summary":       item.get("summary", "").strip()[:500],
                "url":           item.get("url", ""),
                "source":        item.get("source", "Web"),
                "date":          item.get("date", datetime.now().strftime("%b %d")),
                "category_hint": "general",
                "origin":        "search",
            })
        return result
    except (json.JSONDecodeError, Exception) as e:
        print(f"[search] JSON parse error: {e}")
        print(f"[search] raw text snippet: {text[:200]}")
        return []


def fetch_gaps(trace=None) -> List[Dict]:
    """Run all gap queries and return combined results."""
    all_items = []
    seen_urls = set()

    for i, query in enumerate(SEARCH_QUERIES):
        print(f"[search] query {i+1}/{len(SEARCH_QUERIES)}: {query[:60]}...")
        try:
            response = _get_client().models.generate_content(
                model=FLASH,
                contents=query,
                config=types.GenerateContentConfig(
                    system_instruction=SEARCH_SYSTEM,
                    max_output_tokens=1500,
                    tools=[SEARCH_TOOL],
                ),
            )

            if trace:
                trace.span(name=f"web_search_{i+1}", input={"query": query})

            items = _extract_items(response.text or "")
            for item in items:
                if item["url"] not in seen_urls:
                    seen_urls.add(item["url"])
                    all_items.append(item)

            print(f"[search] query {i+1} returned {len(items)} items")

            # Short pause between queries
            if i < len(SEARCH_QUERIES) - 1:
                import time; time.sleep(5)

        except Exception as e:
            print(f"[search] ERROR on query {i+1}: {e}")
            continue

    print(f"[search] total items from web search: {len(all_items)}")
    return all_items
