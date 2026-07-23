"""
agent.py — Simplified single-story pipeline.

1.  Fetch RSS feeds
2.  Fetch web search gaps
3.  Fetch recent Tier 1 Indian VC blog theses (Peak XV, Nexus)
4.  Pause 20s (rate limit reset)
5.  Score + deduplicate with Haiku
6.  Pick the single highest-scoring item
7.  Write raw facts with Gemini (JSON: headline, stat, what happened,
    funding facts, India lens)
8.  Ground a VC thesis excerpt via search over the VC theses pool
9.  Write interrogation questions
10. Write subject line with Haiku
11. Build HTML email (raw facts, VC excerpt, interrogation questions)
12. Send or dry run
13. Save to memory + seed today's questions in responses.json
"""

import time
from datetime import datetime
from typing import Dict

from config import validate
import feeds
import search as web_search
import memory as mem
import responses as resp
import scorer
import writer
import emailer


def run(dry_run: bool = False, trace=None) -> Dict:
    start = datetime.now()
    print(f"\n{'='*60}")
    print(f"AI India Digest — Run started: {start.strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")

    # 1. Fetch RSS
    rss_items = feeds.fetch_all()

    # 2. Fetch web search gaps
    search_items = web_search.fetch_gaps(trace=trace)

    # 3. Fetch VC blog theses (Peak XV, Nexus) — candidate pool for the excerpt
    vc_posts = feeds.fetch_vc_theses()

    # 4. Merge
    all_items = rss_items + search_items
    print(f"\n[agent] total raw items: {len(all_items)}")

    if not all_items:
        print("[agent] no items found. Exiting.")
        return {"status": "no_items"}

    # 5. Pause before scoring
    print("[agent] pausing 20s before scoring to reset rate limit window...")
    time.sleep(20)

    # 6. Score + filter + dedup
    scored = scorer.score_and_filter(all_items, trace=trace)

    if not scored:
        print("[agent] no items passed scoring threshold. Exiting.")
        return {"status": "no_scored_items"}

    print(f"\n[agent] {len(scored)} items passed scoring")

    # 7. Pick the single best story
    best = scored[0]
    print(f"\n[agent] Story of the Day: {best['title'][:70]}")
    print(f"        Score: {best['score']} | Category: {best['category']}")

    # 8. Write raw facts
    story = writer.write_story(best, trace=trace)

    # 9. Ground a VC thesis excerpt against the fetched VC theses pool
    vc_excerpt = writer.write_vc_excerpt(story, vc_posts, trace=trace)
    story["vc_excerpt"]            = vc_excerpt["excerpt"]
    story["vc_excerpt_firm"]       = vc_excerpt["firm"]
    story["vc_excerpt_post_title"] = vc_excerpt["post_title"]
    story["vc_excerpt_post_url"]  = vc_excerpt["post_url"]

    # 10. Write interrogation questions
    questions = writer.write_interrogation_questions(story, vc_excerpt, trace=trace)
    story["interrogation_questions"] = questions

    # 11. Write subject line with Haiku
    subject_words = writer.write_subject_line(story, trace=trace)
    date_prefix   = datetime.now().strftime("%b %d")
    subject        = f"{date_prefix} — {subject_words}"
    print(f"\n[agent] Subject: {subject}")

    # 12. Build HTML
    date_str = datetime.now().strftime("%B %-d, %Y")
    html = emailer.build_html(story=story, date_str=date_str)

    # 13. Send or dry run
    if dry_run:
        output_path = f"/tmp/digest_{start.strftime('%Y%m%d_%H%M')}.html"
        with open(output_path, "w") as f:
            f.write(html)
        print(f"\n[agent] DRY RUN — email saved to {output_path}")
        sent = False
    else:
        sent = emailer.send(subject=subject, html=html)

    # 14. Save ALL scored items to memory (not just the winner)
    # This prevents the same stories from re-surfacing tomorrow
    mem.save_stories(scored)

    # 15. Seed today's interrogation questions in responses.json for respond.py
    if questions:
        resp.add_entry(
            headline=story["headline"],
            source_url=story.get("source_url", ""),
            questions=questions,
        )

    elapsed = (datetime.now() - start).total_seconds()
    result = {
        "status":     "sent" if sent else ("dry_run" if dry_run else "send_failed"),
        "subject":    subject,
        "story":      story["headline"],
        "score":      best["score"],
        "questions":  len(questions),
        "elapsed":    round(elapsed, 1),
    }

    print(f"\n{'='*60}")
    print(f"Run complete in {elapsed:.1f}s")
    print(f"Status:      {result['status']}")
    print(f"Story:       {result['story'][:70]}")
    print(f"Questions:   {result['questions']}")
    print(f"Memory:      {mem.status()}")
    print(f"Responses:   {resp.status()}")
    print(f"{'='*60}\n")

    return result
