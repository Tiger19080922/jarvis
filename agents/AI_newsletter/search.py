"""
search.py — Claude web search tool for gap filling.

Runs 4 targeted queries for content RSS cannot reach.
Uses Claude's built-in web_search_20250305 tool.
"""

import anthropic
import json
from datetime import datetime
from typing import List, Dict

from config import HAIKU, SEARCH_QUERIES, ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SEARCH_TOOL = {
    "type": "web_search_20250305",
    "name": "web_search",
}

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


def _extract_items(response) -> List[Dict]:
    """Parse Claude's response into a list of story dicts."""
    text = ""
    for block in response.content:
        if hasattr(block, "text"):
            text += block.text

    text = text.strip()
    if not text:
        return []

    # Find first [ — skip any preamble text
    bracket = text.find("[")
    if bracket < 0:
        return []
    text = text[bracket:]

    # Strip markdown fences
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]

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
            response = client.messages.create(
                model=HAIKU,
                max_tokens=1500,
                system=SEARCH_SYSTEM,
                tools=[SEARCH_TOOL],
                messages=[{"role": "user", "content": query}],
            )

            if trace:
                trace.span(name=f"web_search_{i+1}", input={"query": query})

            items = _extract_items(response)
            for item in items:
                if item["url"] not in seen_urls:
                    seen_urls.add(item["url"])
                    all_items.append(item)

            print(f"[search] query {i+1} returned {len(items)} items")

            # Pause between queries — each search burns ~10k tokens
            if i < len(SEARCH_QUERIES) - 1:
                import time; time.sleep(15)

        except Exception as e:
            print(f"[search] ERROR on query {i+1}: {e}")
            continue

    print(f"[search] total items from web search: {len(all_items)}")
    return all_items
