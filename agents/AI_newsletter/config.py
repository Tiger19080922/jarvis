"""
Agent 02: AI India Digest
Configuration — all constants live here, nothing is hardcoded elsewhere.
"""

import os
from datetime import datetime

# ── MODELS ────────────────────────────────────────────────────────────────────
FLASH  = "gemini-2.5-flash-lite"  # cheapest: scoring, search, subject line, interrogation questions
PRO    = "gemini-2.5-flash"       # writing tasks: story facts, VC excerpt grounding

# ── PIPELINE THRESHOLDS ───────────────────────────────────────────────────────
RELEVANCE_THRESHOLD   = 6      # min score (1-10) to pass scoring filter
MAX_ITEMS_PER_SECTION = 3      # max bullets per category section
STORY_OF_DAY_WORDS    = 250    # target word count for SOTD
THREAD_WORDS          = 120    # target word count for The Thread
RSS_LOOKBACK_HOURS    = 48     # how far back to pull RSS items
MEMORY_DAYS           = 14     # how many days of stories to keep in memory
RESPONSE_LOG_DAYS     = 90     # how many days of interrogation responses to keep

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

# ── VC BLOGS (Tier 1 Indian VC theses) ────────────────────────────────────────
# Each entry is either a working RSS feed ("rss") or a server-rendered listing
# page we scrape directly ("scrape"). Verified by hand on 2026-07-23 — see
# agents/AI_newsletter/README.md "VC blog sourcing" section for what was
# dropped and why (Accel, Elevation, Blume, 3one4, Kalaari, Lightspeed India
# all lack a reliably parseable source).
VC_BLOGS = [
    {"name": "Peak XV Partners",      "type": "scrape", "url": "https://www.peakxv.com/insights"},
    {"name": "Nexus Venture Partners", "type": "rss",    "url": "https://nexusvp.com/in/feed/"},
]
VC_LOOKBACK_DAYS = 60   # VC firms post far less often than news outlets
MAX_VC_POSTS      = 15  # cap on how many candidate thesis posts to hand the model

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
EMAIL_RECIPIENT = os.getenv("GMAIL_RECIPIENT", "").strip() or EMAIL_SENDER  # empty → send to self
SMTP_PASSWORD   = os.getenv("GMAIL_APP_PASSWORD", "")

# ── LANGFUSE ──────────────────────────────────────────────────────────────────
LANGFUSE_PUBLIC_KEY  = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY  = os.getenv("LANGFUSE_SECRET_KEY", "")
LANGFUSE_ENABLED     = bool(LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY)

# ── MEMORY ────────────────────────────────────────────────────────────────────
MEMORY_FILE    = os.path.join(os.path.dirname(__file__), "memory.json")
RESPONSES_FILE = os.path.join(os.path.dirname(__file__), "responses.json")

# ── GOOGLE AI ─────────────────────────────────────────────────────────────────
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

def validate():
    """Called at startup. Fails loudly if required config is missing."""
    missing = []
    if not GOOGLE_API_KEY:
        missing.append("GOOGLE_API_KEY")
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
