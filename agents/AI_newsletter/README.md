# Agent 02: AI India Digest

Daily newsletter for founders, investors, and operators in the Indian AI ecosystem.

**Format:** One Story of the Day (250 words, full depth) + section bullets + The Thread.  
**Read time:** ~3 minutes.  
**Editorial filter:** AI developments in India that change what founders, investors, and operators should do next.

---

## Setup

### 1. Add to your existing .env

```bash
# Already present from Agent 01:
ANTHROPIC_API_KEY=
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=

# New for Agent 02:
GMAIL_ADDRESS=your.gmail@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx   # Gmail App Password, NOT your login password
GMAIL_RECIPIENT=your.gmail@gmail.com     # Who receives the digest (defaults to sender)
```

**Gmail App Password setup:**  
1. Enable 2FA on your Google account  
2. Go to myaccount.google.com/apppasswords  
3. Create a password for "Mail"  
4. Use that 16-character password as GMAIL_APP_PASSWORD

### 2. Install dependencies

```bash
cd agent_02_digest
pip install -r requirements.txt
```

### 3. Run direnv

```bash
cd ..   # back to project root
direnv allow
```

---

## Usage

```bash
# Dry run — builds email, saves to /tmp, does not send
python run.py --dry-run

# Full run — sends email
python run.py

# Check memory status
python run.py --memory
```

---

## Ratchet Rule

**Complete 10 supervised manual runs before scheduling automatically.**

Log each run:

| Run | Date | Items found | SOTD | Sent? | Notes |
|-----|------|-------------|------|-------|-------|
| 1   |      |             |      |       |       |
| 2   |      |             |      |       |       |
| 3   |      |             |      |       |       |
| 4   |      |             |      |       |       |
| 5   |      |             |      |       |       |
| 6   |      |             |      |       |       |
| 7   |      |             |      |       |       |
| 8   |      |             |      |       |       |
| 9   |      |             |      |       |       |
| 10  |      |             |      |       |       |

Only after 10 clean runs: schedule with `cron` or GitHub Actions at 6:30 AM IST.

```cron
30 1 * * * cd /path/to/project && direnv exec . python agent_02_digest/run.py >> logs/agent_02.log 2>&1
```

---

## File Structure

```
agent_02_digest/
├── config.py       — all constants, feeds, models, thresholds
├── feeds.py        — RSS fetching and filtering
├── search.py       — Claude web search gap queries
├── memory.py       — 14-day story memory and deduplication
├── scorer.py       — Haiku batch scoring
├── prompts.py      — all editorial prompts
├── writer.py       — Haiku bullets + Sonnet SOTD + Sonnet Thread
├── emailer.py      — HTML template + Gmail SMTP
├── agent.py        — pipeline orchestrator
├── run.py          — entry point and CLI
├── memory.json     — auto-created, gitignored
└── requirements.txt
```

---

## Cost estimate

~$0.02 per run · ~$0.60/month  
(Anthropic API only — RSS is free, Claude web search uses your existing key)

---

## Tuning

All editorial prompts are in `prompts.py`. Adjust voice, length, and rules there.  
All thresholds (relevance score, max items per section) are in `config.py`.  
Add or remove RSS feeds in `config.py` under `RSS_FEEDS`.
