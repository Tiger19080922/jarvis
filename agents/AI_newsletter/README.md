# AI India Digest

**A newsletter that refuses to tell you what to think.**

Most newsletters — including earlier versions of this one — hand you a finished conclusion: a narrative, an essay, a "here's what this means for you" section. That's comfortable to read and useless to practice with. This agent does the opposite: it surfaces raw material about one funded Indian AI startup a day, and makes you produce the reasoning yourself.

---

## Why This Exists

If you're prepping for VC interviews, "informing" you isn't the gap. The gap is defending a startup pick under adversarial follow-up questions — why this company, why now, why doesn't the obvious competitor kill it, why might the cited investor's thesis be wrong. You don't build that skill by reading someone else's argument. You build it by being forced to make your own, out loud, against a skeptical interviewer, every day.

So this agent stopped writing the argument for you. It hands you the facts and the questions, and nothing else.

---

## What This Is

Every morning, the digest sends you three things about one funded Indian AI startup:

### 1. Raw Facts
What the company does. Who funded it, how much, at what stage. What the historical Indian-market comparison looks like. No "why it matters," no "the implication is," no sentence that draws a conclusion for you. If a sentence in the draft tells the reader what to think about a fact instead of stating the fact, it gets deleted before you see it — there's a banned-phrase filter (`this means`, `the implication is`, `what this signals`, and similar) applied to the model's output as a safety net, not just a prompt instruction.

### 2. A VC Thesis Excerpt
A short, verbatim quote (under 15 words, cited) from a recent thesis post by a Tier 1 Indian VC firm — Peak XV Partners or Nexus Venture Partners, currently — picked because it's thematically relevant to that day's startup. The model grounds this via search against the firm's real writing. It will not fabricate a quote: if nothing verifiably relevant is found, the section is simply omitted.

### 3. Interrogation Questions
Every email ends with 3 to 5 follow-up questions, written the way a skeptical VC partner would ask them in an interview: what's the actual moat if a funded competitor copies this in six months, why might the cited investor's thesis be wrong, what specific event kills this company in 18 months. These are generated fresh each day from that day's specific company, numbers, and VC excerpt — never a fixed template — and they come with no answers and no hints.

**What you do with it:** read the facts, read the excerpt, then answer the questions yourself — out loud if you can, in writing if that's what's available — before you look anything else up. Log your answers with `respond.py` (see below) so you have a record to review your reasoning against, later, when you actually are in an interview.

---

## Logging Your Answers

```
cd agents/AI_newsletter
python respond.py            # answer the oldest pending question set
python respond.py --list     # see recent entries and how many questions are answered
python respond.py --status   # summary: total entries, how many fully answered
```

Each day's run seeds `responses.json` with that day's questions and no answers. `respond.py` walks you through the ones you haven't answered yet, one at a time, and saves after every answer so nothing is lost if you stop partway through. History is kept for 90 days and is not pruned the way the 14-day story-dedup memory is — this is meant to be a record you can look back over, not a rolling cache.

There is no email-reply parsing. You run this from the terminal, not from your inbox.

---

## VC Blog Sourcing

`VC_BLOGS` in `config.py` currently includes two firms, chosen because they're the only Tier 1 Indian VCs (of eight checked) that expose material this pipeline can reliably ingest:

| Firm | Method | Why |
|------|--------|-----|
| **Peak XV Partners** | Scrape `/insights` listing | Server-rendered HTML with title, date, and link all present in the raw page — no JS execution needed. |
| **Nexus Venture Partners** | RSS (`nexusvp.com/in/feed/`) | Valid, dated RSS feed. |

**Dropped, and why:**

| Firm | Reason dropped |
|------|-----------------|
| **Accel India** | `accel.com/news` is a client-rendered Next.js app — the raw HTML has essentially no article content, only app shell. Would need a headless browser to scrape reliably. |
| **Elevation Capital** | `/perspectives` is Next.js with Framer Motion animation; raw HTML headings are UI chrome ("Perspectives", "Opening Bell"), not article titles. The real data lives in an embedded `__NEXT_DATA__` JSON blob, but that's an undocumented internal structure that can change on any redeploy without notice — too fragile to depend on. |
| **Blume Ventures** | `/commentaries` listing has the right HTML tags (`<h3>`) but they're empty until client-side JS hydrates them. No Medium publication either (`medium.com/feed/blume-ventures` 404s). |
| **3one4 Capital** | `/blog` and `/feed` both return no scrapeable article content — a client-rendered SPA with nothing server-side to parse. |
| **Kalaari Capital** | `/alpha-archives` has server-rendered titles, but zero dates and no discoverable per-article links in the raw HTML (populated by client-side JS). Without a date, we can't tell if a post is recent; without a link, we can't cite it. |
| **Lightspeed India** | No dedicated India-specific site exists (`lightspeedindia.com` / `lightspeedindiapartners.com` don't resolve). The global `lsvp.com/feed` is blocked by Cloudflare's bot challenge — it returned an "Attention Required" interstitial instead of RSS content when tested, which means it can't be trusted for unattended daily automation. |

**Why the excerpt isn't scraped from full article bodies:** even for the two included firms, per-article HTML scraping proved unreliable in testing — Nexus's own RSS `<link>` URLs 404 on the live site, and Peak XV's listing page gives title/date/link but no body text. Rather than build a third fragile scraper, `writer.py`'s VC-excerpt step hands the model the candidate title/date/link pool and lets it ground a real, verbatim quote via Gemini's search tool — the same mechanism the research step already uses elsewhere in this pipeline. If it can't verify a quote, it returns nothing rather than paraphrasing or fabricating one.

If any of the dropped firms later launch a real RSS feed or a server-rendered blog, add an entry to `VC_BLOGS` in `config.py` — `feeds.py` already supports both `"rss"` and `"scrape"` source types.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DAILY RUN  (GitHub Actions)                │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
 ┌─────────────┐      ┌──────────────┐      ┌──────────────────┐
 │  RSS + Web  │      │  VC Blog     │      │  Score + Dedup    │
 │  Search     │      │  Theses      │      │  (Flash)          │
 │ (Inc42,     │      │ (Peak XV,    │      └─────────┬─────────┘
 │  Entrackr,  │      │  Nexus)      │                │
 │  YourStory) │      └──────┬───────┘                ▼
 └──────┬──────┘             │              ┌──────────────────┐
        │                    │              │  Research → Plan  │
        │                    │              │  → Write → Extract│
        │                    │              │  (raw facts only) │
        │                    │              └─────────┬─────────┘
        │                    │                        │
        │                    └───────────┬────────────┘
        │                                ▼
        │                     ┌──────────────────────┐
        │                     │  VC excerpt grounding │
        │                     │  (search over pool)   │
        │                     └───────────┬───────────┘
        │                                 ▼
        │                     ┌──────────────────────┐
        │                     │  Interrogation        │
        │                     │  questions            │
        │                     └───────────┬───────────┘
        │                                 ▼
        │                     ┌──────────────────────┐
        └────────────────────▶│  HTML email → Gmail   │
                              └──────────┬───────────┘
                                         ▼
                              ┌──────────────────────┐
                              │  responses.json seeded│
                              │  → you answer via     │
                              │    respond.py          │
                              └──────────────────────┘
```

**Models:** Gemini 2.5 Flash-Lite (scoring, search gaps, interrogation questions, subject line) · Gemini 2.5 Flash (research, planning, writing, extraction, VC excerpt grounding)

---

## What Makes This Different

| Traditional Newsletter | This Version | The Earlier Version of This Agent |
|---|---|---|
| Written for the average reader | Written to make you argue, not just read | Written to inform and connect to your career |
| Tells you the conclusion | Gives you facts and questions, no conclusion | Told you the conclusion (the "Pivot Lens") |
| Ends when you read it | Ends when you've answered the questions yourself | Ended when you'd read the essay |

---

## Setup: Fork and Run in 15 Minutes

### Step 1. Fork this repo

### Step 2. Add required secrets

`Settings → Secrets and variables → Actions → New repository secret`

| Secret | Description |
|--------|-------------|
| `GOOGLE_API_KEY` | [Get one at aistudio.google.com](https://aistudio.google.com/apikey) |
| `GMAIL_ADDRESS` | Gmail account to send from |
| `GMAIL_APP_PASSWORD` | [Create a Gmail App Password](https://myaccount.google.com/apppasswords) — not your login password |
| `GMAIL_RECIPIENT` | Email address to deliver to (can be same as sender) |

No persona or curriculum secrets are needed — this version doesn't personalise a career narrative, so there's nothing to configure beyond delivery.

### Step 3. Trigger manually to test

Go to `Actions` tab → `AI India Digest — Daily` → `Run workflow`

Watch the logs. Check your inbox.

### Step 4. Scheduled delivery

The workflow runs daily via cron (see `.github/workflows/daily_digest.yml` for the schedule). GitHub Actions free tier introduces some scheduling variance.

### Step 5. Answer the questions

After each day's email arrives, run:

```
cd agents/AI_newsletter
python respond.py
```

and answer that day's interrogation questions before you move on.

---

## File Structure

```
AI_newsletter/
├── run.py              — entry point and CLI
├── agent.py            — pipeline orchestrator
├── config.py           — all constants and env var config (incl. VC_BLOGS)
├── feeds.py            — RSS fetching/filtering + VC blog theses (scrape/RSS)
├── search.py           — Gemini web search gap queries
├── scorer.py           — Gemini batch scoring
├── prompts.py          — raw-facts, VC-excerpt, and interrogation prompts
├── writer.py           — research → plan → write → extract → VC excerpt → questions
├── emailer.py           — HTML template + Gmail SMTP
├── memory.py           — 14-day story deduplication
├── memory.json         — auto-updated by the workflow
├── responses.py        — 90-day interrogation-response log
├── respond.py          — CLI to log your own answers
├── responses.json      — auto-updated by respond.py and by the workflow
├── requirements.txt
└── .github/
    └── workflows/
        └── daily_digest.yml
```

---

## Tuning

- Raw-facts, VC-excerpt, and interrogation prompts: `prompts.py`
- Scoring thresholds, RSS feeds, and `VC_BLOGS`: `config.py`
- Banned synthesis phrases (the safety-net filter): `BANNED_SYNTHESIS_PHRASES` in `prompts.py`

---

## Built With

- [Google Gemini](https://ai.google.dev) — 2.5 Flash and Flash-Lite, with Google Search grounding
- [GitHub Actions](https://github.com/features/actions) — scheduling and hosting (free tier)
- Gmail SMTP — delivery
- RSS feeds, `requests` + `BeautifulSoup`, and Gemini web search — source ingestion

---

*Built by [@Tiger19080922](https://github.com/Tiger19080922)*
