"""
curriculum.py — 90-day learning curriculum for AI product/strategy pivot.

Goal: Break into AI PM / Strategy / VC roles at 50 LPA in 3-6 months.
Start date: April 11, 2026.

Phase 1 (Days  1–28): Foundation — technical vocabulary + AI PM frameworks
Phase 2 (Days 29–56): Market     — India AI ecosystem + VC mental models
Phase 3 (Days 57–84): Application — global case studies + synthesis
Days 85–90:           Buffer      — revisit technical depth (hardest gaps)
"""

from datetime import date

START_DATE = date(2026, 4, 11)

# 13 weekly entries × 7 days = 91 days (days 1–90 used; week 13 = buffer)
WEEKLY_CURRICULUM = [

    # ── PHASE 1: FOUNDATION ──────────────────────────────────────────────────

    {
        "week": 1,
        "phase": "Foundation",
        "topic": "How Large Language Models Work",
        "focus": (
            "Tokens, context windows, attention mechanisms, transformer architecture, "
            "why models hallucinate, inference cost and latency, what prompting actually "
            "does at a mechanical level. Goal: make product trade-offs with engineers "
            "without being lost."
        ),
        "search_query": (
            "how large language models work explained product manager tokens context "
            "window attention transformer architecture hallucination inference 2025"
        ),
        "role_lens": None,
    },

    {
        "week": 2,
        "phase": "Foundation",
        "topic": "RAG, Embeddings, and Retrieval",
        "focus": (
            "What RAG (Retrieval-Augmented Generation) is and why it exists, "
            "vector embeddings and semantic search, chunking strategies, "
            "when RAG beats fine-tuning and when it does not, "
            "latency and cost trade-offs. Real product examples."
        ),
        "search_query": (
            "RAG retrieval augmented generation explained product manager embeddings "
            "vector search chunking fine-tuning comparison 2025"
        ),
        "role_lens": None,
    },

    {
        "week": 3,
        "phase": "Foundation",
        "topic": "AI Agents and Orchestration",
        "focus": (
            "What AI agents are, how tool use and function calling work, "
            "planning and reasoning loops, multi-agent systems, "
            "when agents fail and why, LangGraph / CrewAI / Claude agent patterns. "
            "Why an agent-builder has a structural advantage in PM/Strategy roles."
        ),
        "search_query": (
            "AI agents orchestration tool use planning loops LangGraph multi-agent "
            "failure modes product manager perspective 2025"
        ),
        "role_lens": None,
    },

    {
        "week": 4,
        "phase": "Foundation",
        "topic": "AI Product Management Frameworks",
        "focus": (
            "How to write an AI product spec, designing evaluation loops, "
            "trust and safety in AI products, human-in-the-loop design, "
            "AI product metrics beyond accuracy, the PM's role in model selection "
            "and prompt engineering, feedback loop design."
        ),
        "search_query": (
            "AI product management frameworks spec writing evaluation loops "
            "trust safety human-in-the-loop AI metrics PM role 2025"
        ),
        "role_lens": None,
    },

    # ── PHASE 2: MARKET ──────────────────────────────────────────────────────

    {
        "week": 5,
        "phase": "Market",
        "topic": "India AI Ecosystem: Startups and Founders",
        "focus": (
            "The top funded Indian AI startups — Sarvam AI, Krutrim, Mad Street Den, "
            "Haptik, Yellow.ai, Observe.AI, Gnani.ai — their founding stories, "
            "customers, business models, and competitive moats. "
            "Who is winning and why."
        ),
        "search_query": (
            "India AI startups Sarvam Krutrim top funded 2025 ecosystem founders "
            "product strategy competitive advantage analysis"
        ),
        "role_lens": None,
    },

    {
        "week": 6,
        "phase": "Market",
        "topic": "India AI Policy, Infrastructure, and Capital",
        "focus": (
            "IndiaAI Mission (INR 10,372 crore), MeitY AI policy framework, "
            "GPU access and compute infrastructure, top AI-focused VCs "
            "(Blume, Accel, Lightspeed, Peak XV, Stellaris), "
            "talent landscape, where the funding is going and why now."
        ),
        "search_query": (
            "IndiaAI mission MeitY compute infrastructure VC funding AI India "
            "2025 analysis Blume Accel Peak XV GPU"
        ),
        "role_lens": None,
    },

    {
        "week": 7,
        "phase": "Market",
        "topic": "VC Mental Models for AI Investing",
        "focus": (
            "How top VCs evaluate AI companies: defensibility frameworks, "
            "types of moats in AI (data network effects, workflow lock-in, distribution), "
            "why most AI wrappers fail, what 'AI-native' means to investors, "
            "Sequoia's AI market map, a16z's AI thesis, NFX on network effects in AI."
        ),
        "search_query": (
            "VC mental models AI investing defensibility moats data network effects "
            "workflow lock-in AI wrapper thesis Sequoia a16z 2025"
        ),
        "role_lens": None,
    },

    {
        "week": 8,
        "phase": "Market",
        "topic": "AI Business Models and Unit Economics",
        "focus": (
            "How AI companies price — per seat vs per token vs outcome-based, "
            "why AI unit economics differ from SaaS (inference cost scales with usage), "
            "gross margin challenges, consumption vs subscription models, "
            "how enterprise AI sales works, why pilots stall."
        ),
        "search_query": (
            "AI business models pricing unit economics gross margin inference cost "
            "enterprise AI sales consumption subscription SaaS comparison 2025"
        ),
        "role_lens": None,
    },

    # ── PHASE 3: APPLICATION ─────────────────────────────────────────────────

    {
        "week": 9,
        "phase": "Application",
        "topic": "Global Product Case Studies I: Cursor, Perplexity, Harvey",
        "focus": (
            "Cursor: how they won developer trust, pricing evolution, why IDE "
            "integration is a distribution moat. "
            "Perplexity: the answer engine bet vs Google, publisher conflict, "
            "business model. "
            "Harvey: legal AI, why vertical-specific AI wins, enterprise sales."
        ),
        "search_query": (
            "Cursor AI product strategy case study Perplexity answer engine "
            "Harvey legal AI product decisions growth 2025"
        ),
        "role_lens": None,
    },

    {
        "week": 10,
        "phase": "Application",
        "topic": "Global Product Case Studies II: Glean, Notion AI, Midjourney",
        "focus": (
            "Glean: enterprise knowledge graph, why search is the Trojan horse for "
            "enterprise AI. "
            "Notion AI: integrating AI into an existing product, feature vs platform. "
            "Midjourney: no app, Discord-only, community as distribution — "
            "what this reveals about AI product strategy."
        ),
        "search_query": (
            "Glean enterprise AI knowledge graph Notion AI product integration "
            "Midjourney Discord strategy product decisions case study 2025"
        ),
        "role_lens": None,
    },

    # ── SYNTHESIS (Weeks 11–12, Day-level rotation: PM → Strategy → VC) ──────

    {
        "week": 11,
        "phase": "Synthesis",
        "topic": "Synthesis: Connecting AI Product, Strategy, and Investment",
        "focus": (
            "Connect frameworks from all prior phases. How does technical depth "
            "change product decisions? How do VC mental models inform startup strategy? "
            "How does India's context reshape global playbooks? "
            "Essays rotate daily across PM, Strategy, and VC role lenses."
        ),
        "search_query": (
            "AI product strategy investment synthesis India PM VC analyst "
            "decision framework connecting technical strategy 2025"
        ),
        "role_lens": "synthesis",
    },

    {
        "week": 12,
        "phase": "Synthesis",
        "topic": "Synthesis: Interview-Ready Perspectives",
        "focus": (
            "The questions you will be asked in PM, Strategy, and VC interviews. "
            "How to frame agent-building experience as a strategic asset. "
            "What a 30-60-90 day plan looks like for each role. "
            "Essays rotate daily across PM, Strategy, and VC role lenses."
        ),
        "search_query": (
            "AI PM interview questions strategy VC analyst AI startup "
            "30-60-90 day plan product strategy pivot 2025"
        ),
        "role_lens": "synthesis",
    },

    # ── BUFFER (Days 85–90) ──────────────────────────────────────────────────

    {
        "week": 13,
        "phase": "Buffer",
        "topic": "Deep Dive: AI Technical Concepts Revisited",
        "focus": (
            "Fine-tuning vs RAG vs prompting — when each wins and why. "
            "Evals: how AI teams measure quality in production. "
            "Latency, cost, and quality trade-offs a PM must own. "
            "How to talk about these trade-offs in an interview without overclaiming."
        ),
        "search_query": (
            "AI fine-tuning RAG prompting comparison evals production quality "
            "latency cost AI PM technical decision making 2025"
        ),
        "role_lens": None,
    },
]

# ── SYNTHESIS ROTATION ────────────────────────────────────────────────────────
# Day-of-week index (0–6) cycles through PM → Strategy → VC
SYNTHESIS_ROLES = ["PM", "Strategy", "VC"]

ROLE_LENS_DESCRIPTIONS = {
    "PM": (
        "You are targeting a PM role at a scaling AI company (Series B+, e.g. Sarvam, "
        "Krutrim, or a global AI co with India presence). Frame the pivot lens around: "
        "product spec decisions, feature prioritisation, eval design, working with ML "
        "engineers, and how to demonstrate AI product instincts in an interview."
    ),
    "Strategy": (
        "You are targeting a Strategy or BD role at an early-stage AI startup. "
        "Frame the pivot lens around: go-to-market decisions, partnership strategy, "
        "competitive positioning, and how NRI consulting skills translate directly "
        "into an AI-native strategy context."
    ),
    "VC": (
        "You are targeting a VC Analyst or Associate role at an AI-focused fund "
        "(Blume Ventures, Accel, Lightspeed, or a global fund with India exposure). "
        "Frame the pivot lens around: building an investment thesis, due diligence "
        "frameworks, evaluating founding teams, and spotting defensible AI business models."
    ),
    "General": (
        "You are building toward AI PM, Strategy, and VC analyst roles simultaneously. "
        "Frame the pivot lens around what this topic means for someone pivoting from "
        "strategy consulting into AI. How does mastering this topic change how you speak "
        "in interviews? What signal does it send to a hiring manager or investor?"
    ),
}


def get_today_topic() -> dict:
    """
    Returns the curriculum entry for today.
    Day 1 = April 11, 2026. Capped at day 90.
    Synthesis weeks resolve to a specific role lens based on day-of-week.
    """
    today = date.today()
    days_elapsed = (today - START_DATE).days  # 0 on day 1
    day_number = max(1, days_elapsed + 1)
    day_number = min(day_number, 90)

    week_index = min((day_number - 1) // 7, len(WEEKLY_CURRICULUM) - 1)
    entry = WEEKLY_CURRICULUM[week_index].copy()
    entry["day_number"] = day_number
    entry["days_remaining"] = max(0, 90 - day_number)

    if entry["role_lens"] == "synthesis":
        role = SYNTHESIS_ROLES[(day_number - 1) % 3]
        entry["role_lens"] = role
    elif entry["role_lens"] is None:
        entry["role_lens"] = "General"

    entry["role_lens_description"] = ROLE_LENS_DESCRIPTIONS[entry["role_lens"]]
    return entry
