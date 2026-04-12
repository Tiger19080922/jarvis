# AI India Digest

**A next-generation newsletter that knows who you are, what you need to learn, and why it matters to you — personally.**

Most newsletters are written for everyone. This one is written for you.

---

## The Problem with Newsletters Today

Every newsletter you subscribe to was written for a fictional average reader. The founder who gets *your* issue gets the same one as the student, the VC, and the journalist. The signal-to-noise ratio for any individual reader is low by design.

The result: you skim, you archive, you unsubscribe.

---

## What This Is

AI India Digest is a self-hosted, AI-powered newsletter agent that delivers two things to your inbox every morning:

### 1. The Daily Digest
A single, deeply reported story from the Indian AI ecosystem, written the way a consulting analyst would brief a senior partner. Not a summary. A narrative with context, history, analogies, and a clear implication for what you should do next.

Built on a four-step pipeline:
- **Research** — Claude searches the web and builds a full briefing on the story
- **Plan** — structures the argument before writing a word (consultant-style)
- **Write** — 600 to 900 words of narrative journalism, plain English throughout
- **Extract** — carves the narrative into clean email sections

### 2. The Daily Learning Essay
A 2,000-word original essay on a topic chosen from your personal 90-day curriculum, sourced from the best real articles published on that topic and synthesised by Claude into something worth reading slowly.

Every essay ends with a **Pivot Lens**: a 150 to 200 word section that connects the topic directly to your specific career goals, current role, and unique differentiator.

This is the part that makes it next-generation. The essay does not just inform you. It builds you.

---

## The 90-Day Curriculum

When you set up your instance, you define who you are and where you are going. The agent maps a 90-day learning path across five domains:

| Phase | Weeks | Topics |
|-------|-------|--------|
| Foundation | 1 to 4 | How LLMs work · RAG and retrieval · AI agents · AI PM frameworks |
| Market | 5 to 8 | India AI ecosystem · Policy and capital · VC mental models · AI business models |
| Application | 9 to 12 | Global product case studies · Synthesis across roles |
| Buffer | 13 | Revisit weakest area |

Each day's essay advances you through this map. By day 90, you have read 90 deeply researched essays on exactly the topics your target role requires, and a Pivot Lens that connected every single one back to your specific situation.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DAILY RUN  (GitHub Actions, 07:00 IST)    │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┴───────────────────┐
          ▼                                       ▼
   ┌─────────────┐                       ┌──────────────────┐
   │  DIGEST     │                       │  ESSAY           │
   │  PIPELINE   │                       │  PIPELINE        │
   └─────────────┘                       └──────────────────┘
          │                                       │
   ┌──────▼──────┐                    ┌───────────▼──────────┐
   │ RSS + Web   │                    │ Curriculum: today's  │
   │ Search      │                    │ topic (day N of 90)  │
   └──────┬──────┘                    └───────────┬──────────┘
          │                                       │
   ┌──────▼──────┐                    ┌───────────▼──────────┐
   │ Score and   │                    │ Haiku + web_search   │
   │ Filter      │                    │ finds best sources   │
   └──────┬──────┘                    └───────────┬──────────┘
          │                                       │
   ┌──────▼──────┐                    ┌───────────▼──────────┐
   │ 4-step      │                    │ Sonnet writes 2,000  │
   │ narrative   │                    │ word original essay  │
   │ chain       │                    └───────────┬──────────┘
   └──────┬──────┘                               │
          │                           ┌───────────▼──────────┐
          │                           │ Haiku writes Pivot   │
          │                           │ Lens (role-specific) │
          │                           └───────────┬──────────┘
          └───────────────┬───────────────────────┘
                          ▼
               ┌─────────────────────┐
               │  Single HTML email  │
               │  sent via Gmail     │
               └─────────────────────┘
```

**Models:** Claude Haiku 4.5 (scoring, search, pivot lens) · Claude Sonnet 4.6 (planning, writing, extraction)

**Cost per run:** ~$0.05 to $0.08 · ~$1.50 to $2.50 per month

---

## What Makes This Different

| Traditional Newsletter | AI India Digest |
|----------------------|-----------------|
| Written for the average reader | Written for you, based on your role and goals |
| Informs | Informs and builds proficiency |
| Same for every subscriber | Unique to each fork |
| Curator decides what matters | Editorial filter tied to your trajectory |
| Ends when you read it | Ends when you have completed 90 days of structured learning |

---

## Setup: Fork and Run in 15 Minutes

### Step 1. Fork this repo

### Step 2. Add required secrets

`Settings → Secrets and variables → Actions → New repository secret`

| Secret | Description |
|--------|-------------|
| `ANTHROPIC_API_KEY` | [Get one at console.anthropic.com](https://console.anthropic.com) |
| `GMAIL_ADDRESS` | Gmail account to send from |
| `GMAIL_APP_PASSWORD` | [Create a Gmail App Password](https://myaccount.google.com/apppasswords) — not your login password |
| `GMAIL_RECIPIENT` | Email address to deliver to (can be same as sender) |

### Step 3. Personalise your instance

These secrets shape the essay and pivot lens to your specific situation. Optional but recommended.

| Secret | Example value |
|--------|--------------|
| `CURRICULUM_START_DATE` | `2026-04-11` (your day 1, in YYYY-MM-DD format) |
| `USER_CURRENT_ROLE` | `strategy consultant at a research firm` |
| `USER_TARGET_ROLES` | `AI PM, Strategy at an AI startup, VC Analyst` |
| `USER_GOAL` | `break into AI product roles in 6 months` |
| `USER_DIFFERENTIATOR` | `building AI agents to automate my current work` |

If you skip these, the agent uses sensible defaults and still works.

### Step 4. Trigger manually to test

Go to `Actions` tab → `AI India Digest — Daily` → `Run workflow`

Watch the logs. Check your inbox. The first run takes 4 to 6 minutes.

### Step 5. Scheduled delivery

The workflow runs daily at approximately 07:00 IST via cron. GitHub Actions free tier introduces some scheduling variance — the email typically arrives between 7 and 9 AM.

---

## File Structure

```
AI_newsletter/
├── run.py              — entry point and CLI
├── agent.py            — pipeline orchestrator
├── config.py           — all constants and env var config
├── feeds.py            — RSS fetching and filtering
├── search.py           — Claude web search gap queries
├── scorer.py           — Haiku batch scoring
├── prompts.py          — editorial prompts (digest pipeline)
├── writer.py           — 4-step narrative chain
├── emailer.py          — HTML template + Gmail SMTP
├── memory.py           — 14-day story deduplication
├── memory.json         — auto-updated by the workflow
├── curriculum.py       — 90-day learning schedule
├── essay_prompts.py    — essay and pivot lens prompts
├── essay_writer.py     — essay pipeline orchestrator
├── requirements.txt
└── .github/
    └── workflows/
        └── daily_digest.yml
```

---

## Customising the Curriculum

The default curriculum is designed for someone pivoting into AI product and strategy roles in the Indian ecosystem. To adapt it to your field:

1. Edit `WEEKLY_CURRICULUM` in `curriculum.py` — each entry takes a `topic`, `focus`, `search_query`, and optional `role_lens`
2. Edit `ROLE_LENS_DESCRIPTIONS` to match your target roles
3. Set `CURRICULUM_START_DATE` to today

The architecture is field-agnostic. The India AI focus is the default configuration, not a constraint.

---

## Tuning

- Editorial prompts for the digest: `prompts.py`
- Essay and pivot lens prompts: `essay_prompts.py`
- Scoring thresholds and RSS feeds: `config.py`
- Curriculum topics and rotation: `curriculum.py`

---

## The Bigger Vision

Newsletters have been personalised at the delivery layer for twenty years: your name in the subject line, your city in the weather widget. That is not personalisation. That is mail merge.

True personalisation means the content itself is shaped by who you are, what you already know, what you are trying to become, and where you are in that journey today. Every piece of information filtered through the question: does this matter to this specific person on this specific day?

That is what this agent does.

This is one implementation — India, AI, one person's career pivot. Fork it. Rebuild the curriculum for your field. Change the editorial filter. Point it at a different ecosystem. Make it yours.

---

## Built With

- [Anthropic Claude](https://www.anthropic.com) — Haiku 4.5 and Sonnet 4.6
- [GitHub Actions](https://github.com/features/actions) — scheduling and hosting (free tier)
- Gmail SMTP — delivery
- RSS feeds + Claude web search — source ingestion

---

*Built by [@Tiger19080922](https://github.com/Tiger19080922)*
