"""
Agent 02: AI India Digest
Configuration — all constants live here, nothing is hardcoded elsewhere.
"""

import os
from datetime import datetime

# ── MODELS ────────────────────────────────────────────────────────────────────
HAIKU  = "claude-haiku-4-5-20251001"   # scoring, bullets, subject line
SONNET = "claude-sonnet-4-6"           # Story of the Day, The Thread

# ── PIPELINE THRESHOLDS ───────────────────────────────────────────────────────
RELEVANCE_THRESHOLD   = 6      # min score (1-10) to pass scoring filter
MAX_ITEMS_PER_SECTION = 3      # max bullets per category section
STORY_OF_DAY_WORDS    = 250    # target word count for SOTD
THREAD_WORDS          = 120    # target word count for The Thread
RSS_LOOKBACK_HOURS    = 48     # how far back to pull RSS items
MEMORY_DAYS           = 14     # how many days of stories to keep in memory

# ── EDITORIAL FILTER ─────────────────────────────────────────────────────────
EDITORIAL_FILTER = (
    "We cover AI developments in India that change what founders, "
    "investors, and operators should do next. If a story does not "
    "change what a professional in the Indian AI ecosystem should "
    "think or do, it does not make the digest."
)

AUDIENCE = (
    "Primary: founders, VCs, operators, and product leaders in the "
    "Indian tech and AI ecosystem. They are time-constrained, "
    "technically literate, and want signal not noise. "
    "Secondary: senior professionals at non-tech companies who are "
    "intelligent but not technical — every story must be "
    "understandable without jargon."
)

# ── RSS FEEDS ─────────────────────────────────────────────────────────────────
RSS_FEEDS = [
    {"url": "https://inc42.com/feed/",                               "name": "Inc42",              "category": "general"},
    {"url": "https://yourstory.com/feed",                            "name": "YourStory",          "category": "general"},
    {"url": "https://entrackr.com/feed/",                            "name": "Entrackr",           "category": "funding"},
    {"url": "https://medianama.com/feed/",                           "name": "MediaNama",          "category": "policy"},
    {"url": "https://analyticsindiamag.com/feed/",                   "name": "Analytics India",    "category": "research"},
    {"url": "https://economictimes.indiatimes.com/tech/rss.cms",     "name": "Economic Times Tech","category": "general"},
    {"url": "https://theprint.in/category/india/science/feed/",      "name": "The Print Science",  "category": "research"},
    {"url": "https://indianexpress.com/section/technology/feed/",    "name": "Indian Express Tech","category": "general"},
    {"url": "https://www.livemint.com/rss/technology",               "name": "Mint Tech",          "category": "general"},
    {"url": "https://thenextweb.com/feed/",                          "name": "TNW",                "category": "global"},
]

# ── WEB SEARCH GAP QUERIES ────────────────────────────────────────────────────
# Claude's built-in web_search tool fills what RSS misses:
# government press releases, research papers, niche announcements.
SEARCH_QUERIES = [
    f"India AI government policy MeitY NASSCOM announcement last 48 hours site:pib.gov.in OR site:nasscom.in OR site:meity.gov.in",
    f"Sarvam AI Krutrim AI4Bharat Indian AI startup news funding last 48 hours",
    f"India artificial intelligence enterprise adoption BFSI healthcare automotive last 48 hours",
    f"Indian AI research paper arxiv IIT IISc announcement last 48 hours",
]

# ── CATEGORIES ────────────────────────────────────────────────────────────────
CATEGORIES = {
    "FUNDING":    {"emoji": "💰", "label": "FUNDING"},
    "POLICY":     {"emoji": "🏛", "label": "POLICY & REGULATION"},
    "RESEARCH":   {"emoji": "🔬", "label": "RESEARCH"},
    "ENTERPRISE": {"emoji": "🏢", "label": "ENTERPRISE & PRODUCTS"},
    "OTHER":      {"emoji": "📌", "label": "OTHER"},
}

# ── EMAIL ─────────────────────────────────────────────────────────────────────
EMAIL_SENDER    = os.getenv("GMAIL_ADDRESS", "")
EMAIL_RECIPIENT = os.getenv("GMAIL_RECIPIENT", EMAIL_SENDER)  # defaults to self
SMTP_PASSWORD   = os.getenv("GMAIL_APP_PASSWORD", "")

# ── LANGFUSE ──────────────────────────────────────────────────────────────────
LANGFUSE_PUBLIC_KEY  = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY  = os.getenv("LANGFUSE_SECRET_KEY", "")
LANGFUSE_ENABLED     = bool(LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY)

# ── MEMORY ────────────────────────────────────────────────────────────────────
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory.json")

# ── ANTHROPIC ─────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ── USER PERSONA ──────────────────────────────────────────────────────────────
# Set these as GitHub Secrets (or env vars) to personalise the daily essay.
# Each person who forks this repo sets their own values — nothing is hardcoded.
USER_CURRENT_ROLE    = os.getenv("USER_CURRENT_ROLE",    "a strategy consultant")
USER_TARGET_ROLES    = os.getenv("USER_TARGET_ROLES",    "AI PM, Strategy at an AI startup, VC Analyst")
USER_GOAL            = os.getenv("USER_GOAL",            "break into AI product and strategy roles")
USER_DIFFERENTIATOR  = os.getenv("USER_DIFFERENTIATOR",  "building AI agents for productivity")

# ── CURRICULUM ────────────────────────────────────────────────────────────────
# Set CURRICULUM_START_DATE to the date you forked / started your 90-day run.
# Format: YYYY-MM-DD.  Defaults to today so day 1 = the first time you run it.
_raw_start = os.getenv("CURRICULUM_START_DATE", "")
if _raw_start:
    from datetime import date as _date
    CURRICULUM_START_DATE = _date.fromisoformat(_raw_start)
else:
    from datetime import date as _date
    CURRICULUM_START_DATE = _date.today()

def validate():
    """Called at startup. Fails loudly if required config is missing."""
    missing = []
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    if not EMAIL_SENDER:
        missing.append("GMAIL_ADDRESS")
    if not SMTP_PASSWORD:
        missing.append("GMAIL_APP_PASSWORD")
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Add them to your .env file and run: direnv allow"
        )
    return True
