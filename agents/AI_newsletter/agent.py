"""
agent.py — Simplified single-story pipeline.

1.  Fetch RSS feeds
2.  Fetch web search gaps
3.  Pause 20s (rate limit reset)
4.  Score + deduplicate with Haiku
5.  Pick the single highest-scoring item
6.  Write full story with Sonnet (JSON: headline, stat, what happened,
    why it matters, India lens, implication)
7.  Write subject line with Haiku
8.  Build HTML email (briefing_preview_v4 design)
9.  Send or dry run
10. Save to memory
"""

import time
from datetime import datetime
from typing import Dict

from config import validate
import feeds
import search as web_search
import memory as mem
import scorer
import writer
import emailer
import essay_writer


def run(dry_run: bool = False, trace=None) -> Dict:
    start = datetime.now()
    print(f"\n{'='*60}")
    print(f"AI India Digest — Run started: {start.strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")

    # 1. Fetch RSS
    rss_items = feeds.fetch_all()

    # 2. Fetch web search gaps
    search_items = web_search.fetch_gaps(trace=trace)

    # 3. Merge
    all_items = rss_items + search_items
    print(f"\n[agent] total raw items: {len(all_items)}")

    if not all_items:
        print("[agent] no items found. Exiting.")
        return {"status": "no_items"}

    # 4. Pause before scoring
    print("[agent] pausing 20s before scoring to reset rate limit window...")
    time.sleep(20)

    # 5. Score + filter + dedup
    scored = scorer.score_and_filter(all_items, trace=trace)

    if not scored:
        print("[agent] no items passed scoring threshold. Exiting.")
        return {"status": "no_scored_items"}

    print(f"\n[agent] {len(scored)} items passed scoring")

    # 6. Pick the single best story
    best = scored[0]
    print(f"\n[agent] Story of the Day: {best['title'][:70]}")
    print(f"        Score: {best['score']} | Category: {best['category']}")

    # 7. Write full story with Sonnet
    story = writer.write_story(best, trace=trace)

    # 8. Write subject line with Haiku
    subject_words = writer.write_subject_line(story, trace=trace)
    date_prefix   = datetime.now().strftime("%b %d")
    subject        = f"{date_prefix} — {subject_words}"
    print(f"\n[agent] Subject: {subject}")

    # 9. Generate essay
    essay = None
    try:
        essay = essay_writer.generate_essay()
        print(f"\n[agent] Essay: Day {essay['day_number']}/90 — {essay['topic'][:60]}")
    except Exception as e:
        print(f"\n[agent] Essay generation failed (newsletter will still send): {e}")

    # 10. Build HTML
    date_str = datetime.now().strftime("%B %-d, %Y")
    html = emailer.build_html(story=story, date_str=date_str, essay=essay)

    # 11. Send or dry run
    if dry_run:
        output_path = f"/tmp/digest_{start.strftime('%Y%m%d_%H%M')}.html"
        with open(output_path, "w") as f:
            f.write(html)
        print(f"\n[agent] DRY RUN — email saved to {output_path}")
        sent = False
    else:
        sent = emailer.send(subject=subject, html=html)

    # 12. Save to memory
    mem.save_stories([best])

    elapsed = (datetime.now() - start).total_seconds()
    result = {
        "status":       "sent" if sent else ("dry_run" if dry_run else "send_failed"),
        "subject":      subject,
        "story":        story["headline"],
        "score":        best["score"],
        "essay_day":    essay["day_number"] if essay else None,
        "essay_topic":  essay["topic"] if essay else None,
        "elapsed":      round(elapsed, 1),
    }

    print(f"\n{'='*60}")
    print(f"Run complete in {elapsed:.1f}s")
    print(f"Status:  {result['status']}")
    print(f"Story:   {result['story'][:70]}")
    if result["essay_topic"]:
        print(f"Essay:   Day {result['essay_day']}/90 — {result['essay_topic'][:55]}")
    print(f"Memory:  {mem.status()}")
    print(f"{'='*60}\n")

    return result
