"""
respond.py — Log your own answers to today's interrogation questions.

Usage:
  python respond.py              → answer the oldest pending question set
  python respond.py --status     → show response log summary
  python respond.py --list       → list recent entries and their status

This is the CLI counterpart to responses.py. agent.py seeds each day's
questions with no answers; this script is the one command you run locally
to fill them in. No email reply parsing — you're doing this from the
terminal, not from your inbox.
"""

import sys
import argparse
import textwrap

import responses as resp


def _read_multiline(prompt: str) -> str:
    """Read one or more lines until a blank line. Joins into one paragraph."""
    print(prompt)
    print("(Type your answer — 3 to 5 sentences. Press Enter on an empty line to submit.)")
    lines = []
    while True:
        line = input("> ")
        if not line.strip():
            break
        lines.append(line.strip())
    return " ".join(lines)


def answer_next():
    entry = resp.get_latest_unanswered()
    if not entry:
        print("Nothing pending. Every logged question set already has an answer for each question.")
        return

    total     = len(entry["questions"])
    answered  = len(entry["answers"])
    remaining = entry["questions"][answered:]

    print(f"\n{'='*70}")
    print(f"Story: {entry['headline']}")
    if entry.get("source_url"):
        print(f"Source: {entry['source_url']}")
    print(f"Question {answered + 1} of {total}")
    print(f"{'='*70}\n")

    for i, question in enumerate(remaining):
        q_num = answered + i + 1
        print(f"\n[{q_num}/{total}] {textwrap.fill(question, width=78)}\n")
        answer = _read_multiline("Your answer:")
        if not answer:
            print("Empty answer — skipping for now. Run respond.py again to pick up where you left off.")
            return
        resp.record_answer(entry["date"], answer)
        print("Saved.")

    print(f"\nAll {total} questions for this entry are answered.")


def show_status():
    s = resp.status()
    print("Response log status:")
    print(f"  Total entries:    {s['total_entries']}")
    print(f"  Fully answered:   {s['fully_answered']}")
    print(f"  Oldest entry:     {s['oldest']}")
    print(f"  Newest entry:     {s['newest']}")


def show_list():
    entries = resp.get_recent_entries()
    if not entries:
        print("No entries yet.")
        return
    for e in entries:
        date = e["date"][:10]
        answered = len(e["answers"])
        total = len(e["questions"])
        marker = "done" if answered >= total else f"{answered}/{total}"
        print(f"  {date}  [{marker:>6}]  {e['headline'][:70]}")


def main():
    parser = argparse.ArgumentParser(description="Log answers to daily interrogation questions.")
    parser.add_argument("--status", action="store_true", help="Show response log summary.")
    parser.add_argument("--list",   action="store_true", help="List recent entries and their status.")
    args = parser.parse_args()

    if args.status:
        show_status()
        sys.exit(0)
    if args.list:
        show_list()
        sys.exit(0)

    answer_next()


if __name__ == "__main__":
    main()
