"""
scorer.py — Haiku batch scoring with rate limit handling.
"""

import anthropic
import json
import time
from typing import List, Dict

from config import HAIKU, RELEVANCE_THRESHOLD, EDITORIAL_FILTER, ANTHROPIC_API_KEY
import memory as mem

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

BATCH_SIZE  = 15   # smaller batches
BATCH_PAUSE = 30   # 30s between batches — lets the token window reset

SCORE_SYSTEM = f"""
You are a senior editor at an AI India newsletter.

Editorial filter: {EDITORIAL_FILTER}

Score each article for relevance to professional founders, investors,
and operators in the Indian AI ecosystem.

Scoring rubric:
10 = Major AI development that changes decisions immediately
8-9 = Significant AI news, clearly relevant to the ecosystem
6-7 = Relevant AI story but not urgent
4-5 = Marginally relevant
1-3 = Not AI-related, noise, or too generic

Articles about IPOs, general business, finance, hardware, satellites, or
non-AI topics MUST score 1-3 regardless of the company or investor involved.
A story about a consumer brand founder raising money is NOT an AI story.
A story about satellite imaging is NOT an AI story unless it explicitly uses AI/ML.
Only stories where AI, machine learning, or automation is the PRIMARY subject score above 5.
If in doubt, score 3.

Also assign a category from: FUNDING, POLICY, RESEARCH, ENTERPRISE, OTHER

Return ONLY a JSON array. Each element:
{{"id": <int>, "score": <int 1-10>, "category": <str>, "reason": <str max 10 words>}}

Start your response with [ and nothing else.
"""


def _extract_json(text: str) -> list:
    text = text.strip()
    # Find first [ bracket
    bracket = text.find("[")
    if bracket > 0:
        text = text[bracket:]
    # Strip markdown fences
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()
    # Find matching ] to handle extra data after the array
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


def _score_batch_with_retry(batch: list, b_idx: int, trace=None) -> dict:
    """Score one batch, retry once after 20s on rate limit."""
    for attempt in range(2):
        try:
            response = client.messages.create(
                model=HAIKU,
                max_tokens=600,
                system=SCORE_SYSTEM,
                messages=[{
                    "role": "user",
                    "content": f"Score these {len(batch)} articles:\n\n"
                               + json.dumps(batch, ensure_ascii=False)
                }],
            )
            if trace:
                trace.span(name=f"batch_score_{b_idx}", input={"item_count": len(batch)})

            text = "".join(
                block.text for block in response.content
                if hasattr(block, "text")
            )
            batch_scores = _extract_json(text)
            return {s["id"]: s for s in batch_scores}

        except anthropic.RateLimitError:
            if attempt == 0:
                print(f"[scorer] rate limit hit on batch {b_idx+1}, waiting 30s...")
                time.sleep(30)
            else:
                print(f"[scorer] rate limit persists on batch {b_idx+1}, skipping")
                return {item["id"]: {"id": item["id"], "score": 3,
                                     "category": "OTHER", "reason": "rate limit"}
                        for item in batch}
        except Exception as e:
            print(f"[scorer] ERROR on batch {b_idx+1}: {e}")
            return {item["id"]: {"id": item["id"], "score": 3,
                                 "category": "OTHER", "reason": "error"}
                    for item in batch}


def score_and_filter(items: List[Dict], trace=None) -> List[Dict]:
    # Dedup
    before = len(items)
    items = [i for i in items if not mem.is_duplicate(i["title"])]
    print(f"[scorer] dedup removed {before - len(items)} items. {len(items)} remain.")

    if not items:
        return []

    # Trim to save tokens
    numbered = [
        {"id": idx, "title": item["title"], "summary": item["summary"][:100]}
        for idx, item in enumerate(items)
    ]

    # Batch score
    score_map = {}
    batches = [numbered[i:i+BATCH_SIZE] for i in range(0, len(numbered), BATCH_SIZE)]

    for b_idx, batch in enumerate(batches):
        if b_idx > 0:
            print(f"[scorer] pausing {BATCH_PAUSE}s before next batch...")
            time.sleep(BATCH_PAUSE)

        print(f"[scorer] scoring batch {b_idx+1}/{len(batches)} ({len(batch)} items)...")
        result = _score_batch_with_retry(batch, b_idx, trace)
        score_map.update(result)

    # Filter and sort
    enriched = []
    for idx, item in enumerate(items):
        s = score_map.get(idx, {"score": 3, "category": "OTHER", "reason": ""})
        score = s.get("score", 3)
        if score < RELEVANCE_THRESHOLD:
            continue
        item["score"]    = score
        item["category"] = s.get("category", "OTHER")
        item["reason"]   = s.get("reason", "")
        enriched.append(item)

    enriched.sort(key=lambda x: x["score"], reverse=True)

    print(f"[scorer] {len(enriched)} items passed threshold (min {RELEVANCE_THRESHOLD})")
    cats = {}
    for item in enriched:
        cats[item["category"]] = cats.get(item["category"], 0) + 1
    print(f"[scorer] breakdown: {cats}")

    return enriched
