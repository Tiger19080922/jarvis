"""
curriculum.py — 90-day learning curriculum for AI product/strategy pivot.

Goal: Break into AI PM / Strategy / VC roles at 50 LPA in 3-6 months.
Start date: configured via CURRICULUM_START_DATE env var.

Structure:
  - 13 weekly topics, each with 7 distinct daily sub-angles
  - No two days in the same week have the same search query or focus
  - Day 1 = fundamentals, Day 2 = practitioner use, Day 3 = failure modes,
    Day 4 = India angle, Day 5 = case study, Day 6 = frontier, Day 7 = synthesis

Phase 1 (Days  1-28): Foundation
Phase 2 (Days 29-56): Market
Phase 3 (Days 57-84): Application
Days 85-90:           Buffer
"""

from datetime import date
from config import CURRICULUM_START_DATE, USER_CURRENT_ROLE, USER_TARGET_ROLES

START_DATE = CURRICULUM_START_DATE

# Each week has:
#   topic       — the umbrella theme
#   phase       — Foundation / Market / Application / Buffer / Synthesis
#   role_lens   — None (auto-assigned General) or "synthesis"
#   days        — list of 7 dicts, one per day, each with: angle, focus, search_query

WEEKLY_CURRICULUM = [

    # ── WEEK 1: How Large Language Models Work ───────────────────────────────
    {
        "week": 1,
        "phase": "Foundation",
        "topic": "How Large Language Models Work",
        "role_lens": None,
        "days": [
            {
                "angle": "The mechanics: tokens, attention, and transformers",
                "focus": (
                    "What a token is and why it matters for cost and speed. "
                    "How the attention mechanism lets the model weigh context. "
                    "The transformer architecture at a conceptual level. "
                    "Why this is the foundation for every product decision involving LLMs."
                ),
                "search_query": "how transformer attention mechanism works tokens explained product manager 2025",
            },
            {
                "angle": "Why models hallucinate and what PMs can do about it",
                "focus": (
                    "The probabilistic nature of LLM output. Why hallucination is not a bug. "
                    "How temperature and sampling affect outputs. "
                    "Evals as the PM's tool for managing hallucination in production. "
                    "Real examples of hallucination causing product failures."
                ),
                "search_query": "LLM hallucination causes product manager eval strategies mitigation 2025",
            },
            {
                "angle": "Context windows: the constraint that shapes every AI product",
                "focus": (
                    "What a context window is, how it has grown (4K to 1M+ tokens). "
                    "Why larger windows do not solve everything — cost, latency, lost-in-the-middle. "
                    "How PMs decide what goes in the context and what does not. "
                    "Practical chunking and retrieval strategies when content exceeds the window."
                ),
                "search_query": "LLM context window limitations product decisions chunking retrieval 2025",
            },
            {
                "angle": "Inference cost and latency — the economics every PM must own",
                "focus": (
                    "How inference pricing works (per token, per request, per second). "
                    "The latency vs quality trade-off: why Haiku vs Sonnet vs Opus is a product decision. "
                    "Caching, batching, and streaming as cost levers. "
                    "How Indian AI startups manage inference costs differently from US peers."
                ),
                "search_query": "LLM inference cost latency trade-offs product pricing haiku sonnet optimization 2025",
            },
            {
                "angle": "Prompting as product design — what it actually does mechanically",
                "focus": (
                    "System prompts vs user prompts vs few-shot examples. "
                    "Why prompt engineering is temporary and eval design is permanent. "
                    "Chain-of-thought and why it improves accuracy. "
                    "What a PM needs to know about prompting to work effectively with engineers."
                ),
                "search_query": "prompt engineering product manager system prompt chain of thought few-shot 2025",
            },
            {
                "angle": "Model selection: how to choose between foundation models",
                "focus": (
                    "GPT-4o vs Claude vs Gemini vs Llama — the real differences that matter to a PM. "
                    "Benchmarks vs vibes: why leaderboards mislead product decisions. "
                    "When to use a proprietary model vs open-source. "
                    "How Indian AI companies (Sarvam, Krutrim) are building on top of and competing with foundation models."
                ),
                "search_query": "foundation model selection product manager GPT Claude Gemini Sarvam comparison 2025",
            },
            {
                "angle": "Week synthesis: connecting LLM mechanics to your first PM interview answer",
                "focus": (
                    "Consolidate the week: tokens, attention, hallucination, context, cost, prompting, model selection. "
                    "How to explain LLM trade-offs confidently to an engineering team. "
                    "The one technical concept most PM candidates get wrong in AI interviews. "
                    "Frame your agent-building experience using the week's vocabulary."
                ),
                "search_query": "AI product manager interview technical questions LLM knowledge expected 2025",
            },
        ],
    },

    # ── WEEK 2: RAG, Embeddings, and Retrieval ───────────────────────────────
    {
        "week": 2,
        "phase": "Foundation",
        "topic": "RAG, Embeddings, and Retrieval",
        "role_lens": None,
        "days": [
            {
                "angle": "What RAG is and why it exists",
                "focus": (
                    "The core problem RAG solves: LLMs have a knowledge cutoff and no memory. "
                    "The retrieve-then-generate loop explained simply. "
                    "Why RAG beat fine-tuning as the default enterprise AI pattern. "
                    "Real products built on RAG: Notion AI, Glean, Perplexity."
                ),
                "search_query": "RAG retrieval augmented generation explained why it exists enterprise products 2025",
            },
            {
                "angle": "Vector embeddings and semantic search from first principles",
                "focus": (
                    "What an embedding is: turning text into numbers that capture meaning. "
                    "How semantic search differs from keyword search. "
                    "Vector databases (Pinecone, Weaviate, Chroma) and what they actually do. "
                    "Why similarity search is fast and why it sometimes fails."
                ),
                "search_query": "vector embeddings semantic search explained product manager vector database 2025",
            },
            {
                "angle": "Chunking strategies: the unglamorous decision that determines RAG quality",
                "focus": (
                    "Why chunking strategy is the single biggest lever on RAG quality. "
                    "Fixed-size vs semantic vs hierarchical chunking. "
                    "The chunk size trade-off: precision vs recall. "
                    "How enterprise AI teams tune chunking — and what PMs need to know."
                ),
                "search_query": "RAG chunking strategies quality fixed semantic hierarchical product 2025",
            },
            {
                "angle": "RAG vs fine-tuning: the decision framework",
                "focus": (
                    "When RAG wins: dynamic data, citability, low upfront cost. "
                    "When fine-tuning wins: style/tone, consistent format, domain vocabulary. "
                    "The hybrid approach: fine-tune for behavior, RAG for knowledge. "
                    "Cost and latency implications of each choice."
                ),
                "search_query": "RAG vs fine-tuning when to use decision framework cost latency 2025",
            },
            {
                "angle": "RAG in India: enterprise knowledge management use cases",
                "focus": (
                    "How Indian enterprises are using RAG — BFSI, healthcare, legal. "
                    "Indian-language RAG: the chunking and embedding challenges in Hindi, Tamil, Marathi. "
                    "Companies building RAG infrastructure for Indian enterprises. "
                    "Why Indian document complexity (multilingual, scanned PDFs) creates a harder RAG problem."
                ),
                "search_query": "RAG enterprise India BFSI healthcare multilingual Hindi knowledge management 2025",
            },
            {
                "angle": "Retrieval failure modes: why RAG systems break in production",
                "focus": (
                    "The five ways RAG fails: bad retrieval, bad chunks, bad embeddings, context overflow, and hallucination on top. "
                    "Evaluation metrics for RAG: RAGAS, precision, recall, faithfulness. "
                    "How PMs build feedback loops to improve retrieval quality over time. "
                    "The monitoring stack a PM should demand from an engineering team."
                ),
                "search_query": "RAG failure modes production evaluation metrics RAGAS faithfulness 2025",
            },
            {
                "angle": "Week synthesis: RAG as a product architecture decision",
                "focus": (
                    "Consolidate the week: what RAG is, embeddings, chunking, RAG vs fine-tuning, India angle, failure modes. "
                    "How to spec a RAG-based feature in a product document. "
                    "What questions to ask engineering when reviewing a RAG architecture. "
                    "How your agent-building work already demonstrates RAG thinking."
                ),
                "search_query": "RAG product specification architecture decision PM engineering 2025",
            },
        ],
    },

    # ── WEEK 3: AI Agents and Orchestration ──────────────────────────────────
    {
        "week": 3,
        "phase": "Foundation",
        "topic": "AI Agents and Orchestration",
        "role_lens": None,
        "days": [
            {
                "angle": "What AI agents actually are — beyond the hype",
                "focus": (
                    "The precise definition: an agent perceives, reasons, and acts in a loop. "
                    "How tool use and function calling work mechanically. "
                    "The difference between a chatbot, an assistant, and an agent. "
                    "Why 2024-2026 is the inflection point for agents in production."
                ),
                "search_query": "AI agents definition tool use function calling production 2025 explained",
            },
            {
                "angle": "Planning and reasoning loops: how agents decide what to do",
                "focus": (
                    "ReAct, chain-of-thought, and tree-of-thought patterns. "
                    "How an agent breaks a task into steps and recovers from failures. "
                    "Why planning is hard: the horizon problem in multi-step tasks. "
                    "When to use a single powerful call vs an agent loop."
                ),
                "search_query": "AI agent planning reasoning ReAct chain of thought multi-step tasks 2025",
            },
            {
                "angle": "Multi-agent systems: when one agent is not enough",
                "focus": (
                    "Orchestrator vs subagent patterns. "
                    "Why multi-agent parallelism speeds up complex workflows. "
                    "Failure propagation: how one agent's mistake breaks the chain. "
                    "Real multi-agent products: Devin, AutoGPT lessons, Claude agent SDK."
                ),
                "search_query": "multi-agent systems orchestrator subagent patterns production failures 2025",
            },
            {
                "angle": "Agent failure modes: why agents break and how PMs design around them",
                "focus": (
                    "The five failure modes: hallucinated tool calls, infinite loops, context overflow, irreversible actions, cost blowouts. "
                    "Human-in-the-loop design: when to pause and ask. "
                    "Guardrails, sandboxing, and reversibility as PM requirements. "
                    "Why an agent that costs $0.50 per run can bankrupt you at scale."
                ),
                "search_query": "AI agent failure modes guardrails human in loop cost production PM 2025",
            },
            {
                "angle": "Agent frameworks: LangGraph, CrewAI, Claude agent SDK",
                "focus": (
                    "What LangGraph adds over raw API calls: state management and cycles. "
                    "CrewAI for role-based multi-agent workflows. "
                    "Claude agent SDK and the hooks/tools pattern. "
                    "How to pick a framework as a PM evaluating a team's architecture."
                ),
                "search_query": "LangGraph CrewAI Claude agent SDK comparison frameworks 2025",
            },
            {
                "angle": "Agents in India: what is being built and what is hype",
                "focus": (
                    "Indian enterprise agent use cases: document processing, customer support, compliance. "
                    "Why agents for Indian workflows face unique challenges: multilingual input, low-trust data. "
                    "Startups building agent infrastructure in India. "
                    "Where Indian enterprises are in the agent adoption curve."
                ),
                "search_query": "AI agents India enterprise startups adoption document processing 2026",
            },
            {
                "angle": "Week synthesis: your agent-building experience as a PM signal",
                "focus": (
                    "Consolidate the week: what agents are, planning loops, multi-agent, failure modes, frameworks, India. "
                    "How to frame building the Jarvis newsletter agent as a PM portfolio piece. "
                    "The specific language to use when describing your agent work in interviews. "
                    "What a hiring manager at an AI startup actually wants to hear about your agents."
                ),
                "search_query": "AI PM portfolio agent building interview signal product manager 2025",
            },
        ],
    },

    # ── WEEK 4: AI Product Management Frameworks ──────────────────────────────
    {
        "week": 4,
        "phase": "Foundation",
        "topic": "AI Product Management Frameworks",
        "role_lens": None,
        "days": [
            {
                "angle": "How to write an AI product spec",
                "focus": (
                    "What makes an AI spec different from a traditional PRD. "
                    "The five sections every AI spec needs: problem, model selection rationale, eval criteria, edge cases, fallback behavior. "
                    "How to specify what good looks like before building. "
                    "Real AI spec examples from Notion, Linear, and Intercom."
                ),
                "search_query": "AI product spec PRD writing guide examples 2025 PM",
            },
            {
                "angle": "Evaluation design: the PM's most important AI skill",
                "focus": (
                    "Why evals are the PM's job, not the engineer's. "
                    "How to build an eval set: golden examples, adversarial cases, regression tests. "
                    "Automated evals vs human evals: when to use each. "
                    "The eval-driven development loop: spec, build, eval, iterate."
                ),
                "search_query": "AI evaluation design product manager eval set automated human evals 2025",
            },
            {
                "angle": "Trust, safety, and the PM's accountability",
                "focus": (
                    "Why trust and safety is a PM problem, not a legal problem. "
                    "The taxonomy of AI harms: factual errors, bias, privacy, misuse. "
                    "Red-teaming as a product practice. "
                    "How Anthropic, OpenAI, and Google approach responsible AI at the product layer."
                ),
                "search_query": "AI trust safety product manager red teaming responsible AI 2025",
            },
            {
                "angle": "AI product metrics: beyond accuracy",
                "focus": (
                    "Why accuracy is the wrong primary metric for most AI products. "
                    "The metrics that matter: task completion rate, fallback rate, user correction rate, trust score. "
                    "How to instrument an AI feature to measure what users actually experience. "
                    "Leading vs lagging indicators in AI product quality."
                ),
                "search_query": "AI product metrics beyond accuracy task completion trust PM measurement 2025",
            },
            {
                "angle": "Human-in-the-loop design patterns",
                "focus": (
                    "When to automate fully vs keep a human in the loop. "
                    "The three HITL patterns: approve-before-act, review-after-act, exception-only. "
                    "How HITL design changes as the model gets better. "
                    "Real examples: Harvey (legal), Glean (enterprise search), Github Copilot."
                ),
                "search_query": "human in the loop AI design patterns approve review exception PM 2025",
            },
            {
                "angle": "Feedback loops: how AI products get better over time",
                "focus": (
                    "The flywheel: user feedback improves the model improves the product. "
                    "Implicit signals (clicks, corrections, abandonment) vs explicit ratings. "
                    "How to design feedback capture into the product without annoying users. "
                    "Why Indian AI products have a data advantage if they build the right feedback loops."
                ),
                "search_query": "AI product feedback loop implicit signals flywheel data PM design 2025",
            },
            {
                "angle": "Week synthesis: the AI PM skill stack",
                "focus": (
                    "Consolidate the week: spec writing, evals, trust/safety, metrics, HITL, feedback loops. "
                    "What separates a great AI PM from a traditional PM who learned some AI. "
                    "How to demonstrate these skills in a portfolio project or interview. "
                    "The one thing most AI PM candidates are missing."
                ),
                "search_query": "AI product manager skills what makes great PM interview portfolio 2025",
            },
        ],
    },

    # ── WEEK 5: India AI Ecosystem — Startups and Founders ───────────────────
    {
        "week": 5,
        "phase": "Market",
        "topic": "India AI Ecosystem: Startups and Founders",
        "role_lens": None,
        "days": [
            {
                "angle": "Sarvam AI: building India's sovereign model",
                "focus": (
                    "Sarvam's founding story and why Pratyush Kumar and Vivek Raghavan left academia. "
                    "What Sarvam actually builds: Indic LLMs, speech models, enterprise APIs. "
                    "The $300M+ funding round and what it signals about India's model ambitions. "
                    "Why sovereign AI matters to the Indian government."
                ),
                "search_query": "Sarvam AI funding founding story sovereign model India Pratyush Kumar 2025 2026",
            },
            {
                "angle": "Krutrim: Ola's AI bet and the conglomerate play",
                "focus": (
                    "How Bhavish Aggarwal is building Krutrim as India's full-stack AI company. "
                    "The chip ambition: why Krutrim is designing its own AI processor. "
                    "Enterprise product strategy: what Krutrim is selling today. "
                    "Whether a mobility company can credibly build foundational AI."
                ),
                "search_query": "Krutrim AI Bhavish Aggarwal chip strategy enterprise product 2025 2026",
            },
            {
                "angle": "The conversational AI cohort: Haptik, Yellow.ai, Gnani",
                "focus": (
                    "How Haptik, Yellow.ai, and Gnani.ai built before the LLM wave and are rebuilding now. "
                    "The pivot challenge: from rule-based to LLM-powered without losing enterprise clients. "
                    "Revenue models in Indian conversational AI. "
                    "Who is winning in enterprise chatbot/voice AI in India today."
                ),
                "search_query": "Haptik Yellow.ai Gnani conversational AI India enterprise revenue 2025",
            },
            {
                "angle": "AI in Indian enterprise: BFSI, healthcare, and retail",
                "focus": (
                    "The three verticals where Indian enterprise AI spending is concentrating. "
                    "BFSI use cases: fraud detection, underwriting, customer service. "
                    "Healthcare: diagnostic AI, EHR automation, drug discovery. "
                    "Which Indian AI startups are winning in each vertical and why."
                ),
                "search_query": "AI enterprise India BFSI healthcare retail startups use cases 2025 2026",
            },
            {
                "angle": "AI4Bharat and the research-to-product pipeline",
                "focus": (
                    "What AI4Bharat is, how it operates, and why its Indic models matter. "
                    "The gap between Indian AI research and Indian AI products. "
                    "How startups are commercialising IIT/IISc research. "
                    "The talent pipeline: where India's AI researchers are going."
                ),
                "search_query": "AI4Bharat Indic models research product pipeline IIT IISc talent 2025",
            },
            {
                "angle": "Competitive moats in Indian AI: what actually defends a position",
                "focus": (
                    "Why Indian-language data is the scarcest and most defensible asset. "
                    "Distribution moat: why the company with the largest enterprise sales force wins. "
                    "The API commodity trap: building on top of GPT-4 in India is not a moat. "
                    "What Sarvam and Krutrim understand about moats that most Indian AI startups do not."
                ),
                "search_query": "India AI startup moat defensibility language data distribution 2025",
            },
            {
                "angle": "Week synthesis: your India AI market map",
                "focus": (
                    "Consolidate the week: Sarvam, Krutrim, conversational AI, enterprise verticals, research pipeline, moats. "
                    "How to walk a VC or hiring manager through the India AI landscape in 3 minutes. "
                    "The three bets you would make in India AI if you had capital today. "
                    "What gaps exist that a new startup could fill."
                ),
                "search_query": "India AI market map landscape gaps opportunities 2026 analysis",
            },
        ],
    },

    # ── WEEK 6: India AI Policy, Infrastructure, and Capital ─────────────────
    {
        "week": 6,
        "phase": "Market",
        "topic": "India AI Policy, Infrastructure, and Capital",
        "role_lens": None,
        "days": [
            {
                "angle": "IndiaAI Mission: the Rs 10,372 crore bet",
                "focus": (
                    "What the IndiaAI Mission actually funds: compute, datasets, skilling, startups. "
                    "How India's AI compute allocation compares to US, China, and EU. "
                    "What MeitY and the IndiaAI team are doing operationally. "
                    "Which startups and institutions have benefited so far."
                ),
                "search_query": "IndiaAI Mission MeitY 10372 crore compute datasets startups 2025 2026",
            },
            {
                "angle": "GPU access in India: the infrastructure gap",
                "focus": (
                    "Why GPU availability is the binding constraint on Indian AI development. "
                    "The government compute initiative: who gets access, how, and at what cost. "
                    "Hyperscaler presence: AWS, Azure, GCP data centers in India. "
                    "How Indian startups train models without owning GPUs."
                ),
                "search_query": "GPU access India AI compute infrastructure government hyperscaler 2025 2026",
            },
            {
                "angle": "India's AI regulatory approach: principles-based vs rules-based",
                "focus": (
                    "How India's approach to AI regulation differs from the EU AI Act. "
                    "The DPDP Act and its implications for AI companies using personal data. "
                    "Sectoral regulators: RBI on AI in BFSI, IRDA, SEBI. "
                    "What the regulatory environment means for AI product decisions."
                ),
                "search_query": "India AI regulation DPDP Act RBI AI policy principles-based 2025 2026",
            },
            {
                "angle": "VC funding flows: who is investing in Indian AI and why",
                "focus": (
                    "The top AI-focused funds active in India: Blume, Accel, Lightspeed, Peak XV, Stellaris. "
                    "How Indian AI funding in 2025-26 compares to 2022-23 and 2019-20 cycles. "
                    "Where the capital is going: infrastructure vs application vs tooling. "
                    "Why global funds are opening India offices specifically for AI."
                ),
                "search_query": "India AI VC funding 2025 2026 Blume Accel Lightspeed Peak XV trends",
            },
            {
                "angle": "India's AI talent economy",
                "focus": (
                    "Where India's AI talent comes from and where it is going. "
                    "The IIT/IISc-to-startup pipeline vs the IIT-to-US pipeline. "
                    "Compensation benchmarks: what AI PMs, engineers, and researchers earn in India. "
                    "Why India produces more AI talent than it retains — and whether that is changing."
                ),
                "search_query": "India AI talent compensation PM engineer researcher IIT startup 2025 2026",
            },
            {
                "angle": "Public digital infrastructure as an AI moat",
                "focus": (
                    "How UPI, Aadhaar, ONDC, and Account Aggregator create a unique foundation for Indian AI. "
                    "Why India's DPI stack is the envy of AI investors globally. "
                    "Which AI companies are building directly on DPI and why it creates defensibility. "
                    "The financial inclusion AI opportunity that only exists because of DPI."
                ),
                "search_query": "India DPI UPI Aadhaar ONDC Account Aggregator AI moat opportunity 2025",
            },
            {
                "angle": "Week synthesis: India's AI position in 2026",
                "focus": (
                    "Consolidate the week: IndiaAI Mission, GPU access, regulation, VC flows, talent, DPI. "
                    "India's structural advantages and disadvantages vs US and China in AI. "
                    "The 3-year view: what India AI looks like in 2029 if current trends hold. "
                    "How to use this market map in a VC or strategy role interview."
                ),
                "search_query": "India AI position 2026 advantages disadvantages forecast analysis",
            },
        ],
    },

    # ── WEEK 7: VC Mental Models for AI Investing ─────────────────────────────
    {
        "week": 7,
        "phase": "Market",
        "topic": "VC Mental Models for AI Investing",
        "role_lens": None,
        "days": [
            {
                "angle": "Why most AI wrappers fail: the defensibility problem",
                "focus": (
                    "What an AI wrapper is and why it is not a business. "
                    "The three questions every VC asks: what happens when the underlying model gets better? "
                    "Why distribution, not the model, is what VCs are actually buying. "
                    "Which AI companies are wrappers and which are not."
                ),
                "search_query": "AI wrapper defensibility VC investing why fail distribution moat 2025",
            },
            {
                "angle": "The three moats in AI: data, workflow, and distribution",
                "focus": (
                    "Data moat: proprietary training data that competitors cannot replicate. "
                    "Workflow moat: so deeply embedded in operations that switching costs are prohibitive. "
                    "Distribution moat: the sales motion and brand that gets you into the enterprise. "
                    "Real examples of each moat in AI companies."
                ),
                "search_query": "AI company moats data workflow distribution VC framework examples 2025",
            },
            {
                "angle": "How top VCs evaluate AI founding teams",
                "focus": (
                    "What Sequoia, a16z, and Lightspeed look for in AI founders specifically. "
                    "Technical depth vs GTM strength: the balance that matters at different stages. "
                    "Why research-to-product founders are valued differently from repeat entrepreneurs. "
                    "Red flags in AI founding teams that experienced VCs identify quickly."
                ),
                "search_query": "VC evaluate AI founding team technical depth GTM Sequoia a16z criteria 2025",
            },
            {
                "angle": "AI market sizing: why TAM analysis is different for AI",
                "focus": (
                    "Why AI compresses software costs and can shrink TAM while growing revenue. "
                    "The services-to-software conversion: how AI is replacing outsourcing. "
                    "How to size an AI market without double-counting. "
                    "Sequoia's AI market size framework."
                ),
                "search_query": "AI market sizing TAM services software conversion Sequoia framework 2025",
            },
            {
                "angle": "Pricing and monetisation models in AI",
                "focus": (
                    "Per seat vs per token vs outcome-based pricing. "
                    "Why outcome-based pricing is the most defensible but hardest to implement. "
                    "The gross margin challenge: inference cost eats AI company margins. "
                    "How AI companies like Harvey and Cursor have evolved their pricing."
                ),
                "search_query": "AI pricing models per seat token outcome gross margin Harvey Cursor 2025",
            },
            {
                "angle": "The a16z and NFX AI theses: what they believe and why",
                "focus": (
                    "a16z's view on AI infrastructure vs application layer investing. "
                    "NFX on network effects in AI: which AI products get stronger with more users. "
                    "First Round's thesis on AI-native vs AI-enabled companies. "
                    "Where these theses agree and where they diverge."
                ),
                "search_query": "a16z NFX First Round AI thesis infrastructure application network effects 2025",
            },
            {
                "angle": "Week synthesis: how to think like an AI investor",
                "focus": (
                    "Consolidate the week: wrappers, moats, team evaluation, TAM, pricing, theses. "
                    "How to evaluate any AI startup using this week's frameworks in 10 minutes. "
                    "The investment memo structure a VC analyst would write on Sarvam AI today. "
                    "What you would say in a VC interview when asked: what AI company would you invest in and why?"
                ),
                "search_query": "AI investment memo analysis framework VC analyst interview 2025",
            },
        ],
    },

    # ── WEEK 8: AI Business Models and Unit Economics ─────────────────────────
    {
        "week": 8,
        "phase": "Market",
        "topic": "AI Business Models and Unit Economics",
        "role_lens": None,
        "days": [
            {
                "angle": "How AI changes the economics of software",
                "focus": (
                    "Why AI collapses the cost of certain software categories to near-zero. "
                    "The SaaS disruption thesis: which SaaS companies are being unbundled by AI. "
                    "Why AI companies can have high revenue with smaller teams. "
                    "What Andreessen's 'software is eating the world' looks like in the AI era."
                ),
                "search_query": "AI software economics SaaS disruption unbundling revenue per employee 2025",
            },
            {
                "angle": "Consumption vs subscription: the pricing model battle",
                "focus": (
                    "Why AI-native products lean toward consumption pricing. "
                    "The CFO problem: consumption pricing creates unpredictable spend. "
                    "How companies like Anthropic and OpenAI balance consumption and subscription. "
                    "Which model wins for enterprise vs developer vs consumer AI."
                ),
                "search_query": "AI consumption subscription pricing enterprise developer Anthropic OpenAI 2025",
            },
            {
                "angle": "Gross margins in AI: the inference cost problem",
                "focus": (
                    "Why AI companies have lower gross margins than SaaS companies. "
                    "How inference cost as a percentage of revenue changes at scale. "
                    "The model distillation and caching strategies that protect margins. "
                    "What investors accept as a normal gross margin for an AI company."
                ),
                "search_query": "AI gross margin inference cost SaaS comparison distillation 2025",
            },
            {
                "angle": "Enterprise AI sales: why pilots stall",
                "focus": (
                    "The enterprise AI sales cycle and where deals die. "
                    "Why procurement, security, and legal kill AI deals more than technical failure. "
                    "How the best AI companies accelerate from pilot to contract. "
                    "What a PM at an AI startup needs to know about the enterprise sales process."
                ),
                "search_query": "enterprise AI sales cycle pilot stall procurement security PM 2025",
            },
            {
                "angle": "AI in the services industry: replacing outsourcing",
                "focus": (
                    "How AI is compressing India's IT services TAM. "
                    "Which outsourcing categories are being automated and on what timeline. "
                    "How TCS, Infosys, and Wipro are responding to the AI threat. "
                    "The opportunity for AI-native players to take outsourcing revenue."
                ),
                "search_query": "AI replacing IT outsourcing India TCS Infosys Wipro threat 2025 2026",
            },
            {
                "angle": "Unit economics deep dive: CAC, LTV, and payback in AI",
                "focus": (
                    "How customer acquisition cost works differently for AI products with viral loops. "
                    "LTV calculation when the product improves and churn decreases over time. "
                    "Payback period benchmarks for enterprise AI vs consumer AI. "
                    "The unit economics of a successful Indian AI startup."
                ),
                "search_query": "AI startup unit economics CAC LTV payback enterprise consumer 2025",
            },
            {
                "angle": "Week synthesis: business model analysis as an AI PM skill",
                "focus": (
                    "Consolidate the week: software economics, consumption vs subscription, margins, enterprise sales, outsourcing, unit economics. "
                    "How to do a quick business model teardown of any AI company. "
                    "What a strategy hire at an AI startup is expected to know on day one. "
                    "The business model question you would be asked in a PM or strategy interview."
                ),
                "search_query": "AI business model analysis teardown PM strategy interview 2025",
            },
        ],
    },

    # ── WEEK 9: Global Product Case Studies I ────────────────────────────────
    {
        "week": 9,
        "phase": "Application",
        "topic": "Global Product Case Studies I: Cursor, Perplexity, Harvey",
        "role_lens": None,
        "days": [
            {
                "angle": "Cursor: how trust became a distribution moat",
                "focus": (
                    "How Cursor won developer trust when GitHub Copilot had the head start. "
                    "The product decisions that differentiated Cursor: multi-file context, agent mode, codebase indexing. "
                    "Pricing evolution: from free to $20 to enterprise. "
                    "Why IDE integration is a stronger moat than a standalone tool."
                ),
                "search_query": "Cursor AI product strategy trust developer IDE moat pricing 2025 2026",
            },
            {
                "angle": "Perplexity: the answer engine bet against Google",
                "focus": (
                    "What Perplexity is betting: people want answers, not links. "
                    "How Perplexity's product differs from Google and ChatGPT. "
                    "The publisher conflict and why it matters for the business model. "
                    "Whether the answer engine can become a platform."
                ),
                "search_query": "Perplexity answer engine vs Google product strategy publisher conflict 2025",
            },
            {
                "angle": "Harvey: vertical AI and why lawyers pay premium prices",
                "focus": (
                    "How Harvey built specifically for legal work and why general AI tools failed lawyers. "
                    "The enterprise sales strategy: partner with AmLaw 100, use logos to sell down-market. "
                    "Why legal is the perfect first vertical: high-value, document-heavy, risk-averse. "
                    "What other verticals can apply the Harvey playbook."
                ),
                "search_query": "Harvey AI legal vertical enterprise sales playbook premium pricing 2025",
            },
            {
                "angle": "The developer tool AI wave: lessons from Cursor, Copilot, Tabnine",
                "focus": (
                    "What the developer tool wars teach about AI product competition. "
                    "Why the best AI product does not always win. "
                    "The role of trust, latency, and workflow fit in developer AI. "
                    "How Cursor overtook Copilot despite Microsoft's distribution advantage."
                ),
                "search_query": "developer AI tools Cursor Copilot Tabnine competition trust latency 2025",
            },
            {
                "angle": "How these companies made their hardest product decisions",
                "focus": (
                    "Cursor's decision to go agent-first before most users were ready. "
                    "Perplexity's decision to show sources despite the copyright risk. "
                    "Harvey's decision to refuse consumer use cases and stay enterprise. "
                    "The decision-making frameworks behind each of these choices."
                ),
                "search_query": "Cursor Perplexity Harvey product decision making case study 2025",
            },
            {
                "angle": "India lens: can these playbooks work in the Indian market",
                "focus": (
                    "Whether an Indian Cursor (developer tools) is viable given the talent base. "
                    "What an Indian Perplexity would look like: regional language answer engine. "
                    "Harvey for Indian legal: why it is harder (unstructured case law) but potentially bigger. "
                    "Which global AI product playbooks transfer to India and which do not."
                ),
                "search_query": "India AI product playbook Cursor Perplexity Harvey India adaptation 2025 2026",
            },
            {
                "angle": "Week synthesis: reverse-engineering AI product decisions",
                "focus": (
                    "Consolidate the week: Cursor, Perplexity, Harvey and the patterns across them. "
                    "The reverse-engineering framework: what problem, what bet, what moat, what decision. "
                    "How to use this framework to answer a PM case study in an interview. "
                    "The one product decision from this week you would have made differently and why."
                ),
                "search_query": "AI product case study reverse engineering framework PM interview 2025",
            },
        ],
    },

    # ── WEEK 10: Global Product Case Studies II ───────────────────────────────
    {
        "week": 10,
        "phase": "Application",
        "topic": "Global Product Case Studies II: Glean, Notion AI, Midjourney",
        "role_lens": None,
        "days": [
            {
                "angle": "Glean: enterprise search as the Trojan horse for AI",
                "focus": (
                    "How Glean turned enterprise search into a knowledge graph play. "
                    "Why search is the highest-leverage AI entry point in large enterprises. "
                    "Glean's expansion from search to AI assistant to workflow automation. "
                    "The data moat: why Glean gets better with every query."
                ),
                "search_query": "Glean enterprise AI search knowledge graph expansion strategy 2025",
            },
            {
                "angle": "Notion AI: integrating AI into a beloved product without breaking it",
                "focus": (
                    "The product challenge: adding AI to Notion without alienating power users. "
                    "How Notion decided which features to build vs which to buy. "
                    "The feature vs platform decision: when does an AI add-on become a product layer. "
                    "What Notion AI teaches about AI integration in existing products."
                ),
                "search_query": "Notion AI product integration strategy feature platform user trust 2025",
            },
            {
                "angle": "Midjourney: community as distribution and Discord as the product",
                "focus": (
                    "Why Midjourney launched on Discord and never built a standalone app. "
                    "How community-driven product development worked: users taught each other prompting. "
                    "The revenue model without a sales team. "
                    "What Midjourney's strategy reveals about AI consumer product distribution."
                ),
                "search_query": "Midjourney Discord strategy community distribution revenue model 2025",
            },
            {
                "angle": "The enterprise AI platform battle: who wins the knowledge layer",
                "focus": (
                    "Microsoft Copilot vs Google Workspace AI vs Glean vs Notion. "
                    "Why the knowledge layer is the most fought-over surface in enterprise AI. "
                    "The integration tax: why it is hard to displace tools already in enterprise workflows. "
                    "Where the enterprise AI platform battle stands in 2026."
                ),
                "search_query": "enterprise AI platform Microsoft Copilot Google Glean Notion battle 2025 2026",
            },
            {
                "angle": "Consumer AI products: why most fail and what the winners share",
                "focus": (
                    "The consumer AI graveyard: products that launched with hype and died quietly. "
                    "What the surviving consumer AI products share: habit, delight, and irreplaceability. "
                    "Why consumer AI is harder than enterprise AI despite lower sales costs. "
                    "The consumer AI opportunities that remain wide open."
                ),
                "search_query": "consumer AI product success failure habit delight what works 2025",
            },
            {
                "angle": "India lens: what Glean, Notion, Midjourney teach Indian builders",
                "focus": (
                    "Whether enterprise search AI works in Indian enterprises with fragmented data. "
                    "Why Notion's gentle AI integration strategy is a model for Indian SaaS. "
                    "What a Midjourney-style community-first launch looks like in India. "
                    "The Indian products that have used these strategies successfully."
                ),
                "search_query": "India enterprise AI Glean Notion Midjourney lessons SaaS 2025 2026",
            },
            {
                "angle": "Week synthesis: the AI product pattern library",
                "focus": (
                    "Consolidate weeks 9 and 10: six case studies, six product strategies. "
                    "The five reusable patterns: trust-first, vertical focus, Trojan horse, community distribution, gentle integration. "
                    "How to apply these patterns to evaluate or design a new AI product. "
                    "Which pattern fits the Indian AI context best and why."
                ),
                "search_query": "AI product strategy patterns case studies framework PM 2025",
            },
        ],
    },

    # ── WEEK 11: Synthesis I ──────────────────────────────────────────────────
    {
        "week": 11,
        "phase": "Synthesis",
        "topic": "Synthesis: Connecting AI Product, Strategy, and Investment",
        "role_lens": "synthesis",
        "days": [
            {
                "angle": "How technical depth changes your product decisions",
                "focus": (
                    "Revisit weeks 1-4: tokens, RAG, agents, AI PM frameworks. "
                    "The specific product decisions that become obvious once you understand the mechanics. "
                    "How to use technical depth as a PM without crossing into engineering territory. "
                    "The questions you can now ask that you could not ask 10 weeks ago."
                ),
                "search_query": "AI PM technical depth product decisions practical impact 2025",
            },
            {
                "angle": "How market knowledge sharpens your investment thesis",
                "focus": (
                    "Revisit weeks 5-8: India ecosystem, policy, VC mental models, business models. "
                    "Building a defensible point of view on the Indian AI market. "
                    "How to connect market structure to investment thesis. "
                    "The two or three bets in India AI you would make today and why."
                ),
                "search_query": "India AI investment thesis market structure 2026 analysis",
            },
            {
                "angle": "How product case studies inform strategy",
                "focus": (
                    "Revisit weeks 9-10: Cursor, Perplexity, Harvey, Glean, Notion, Midjourney. "
                    "Applying case study patterns to evaluate Indian AI companies. "
                    "What a strategy hire at an Indian AI startup should know about global competitors. "
                    "The competitive analysis framework using the case study library."
                ),
                "search_query": "AI product case studies strategy India competitive analysis 2025 2026",
            },
            {
                "angle": "The PM, Strategy, and VC views of the same problem",
                "focus": (
                    "How a PM, a strategy consultant, and a VC analyst would look at the same AI startup differently. "
                    "What each role sees that the others miss. "
                    "How to code-switch between these perspectives in interviews. "
                    "The superpower of having all three lenses simultaneously."
                ),
                "search_query": "AI startup PM strategy VC perspective analysis different views 2025",
            },
            {
                "angle": "Your agent-building differentiator: how to talk about it",
                "focus": (
                    "How to frame the Jarvis newsletter agent and MoM Maker as PM portfolio evidence. "
                    "The specific language that signals product thinking (not just coding). "
                    "What a PM hiring manager at Sarvam or Krutrim would find compelling about your work. "
                    "How to connect building agents to the AI PM frameworks from week 4."
                ),
                "search_query": "AI PM portfolio agent building differentiator interview narrative 2025",
            },
            {
                "angle": "Gaps and blind spots: what you still do not know",
                "focus": (
                    "The areas the 90-day curriculum does not fully cover. "
                    "What an actual PM or VC at a top Indian AI company knows that you do not yet. "
                    "The fastest ways to close the remaining gaps. "
                    "How to be honest about gaps in an interview without losing the opportunity."
                ),
                "search_query": "AI PM knowledge gaps blind spots interview honest approach 2025",
            },
            {
                "angle": "Week synthesis: your integrated point of view on AI",
                "focus": (
                    "What is your actual view on the most important thing happening in AI right now? "
                    "Not what you have read but what you believe and why. "
                    "How to articulate a genuine, defensible, specific opinion about AI in India. "
                    "The opinion that would make a founder or VC want to keep talking to you."
                ),
                "search_query": "India AI 2026 perspective opinion what matters most analysis",
            },
        ],
    },

    # ── WEEK 12: Synthesis II — Interview Ready ───────────────────────────────
    {
        "week": 12,
        "phase": "Synthesis",
        "topic": "Synthesis: Interview-Ready Perspectives",
        "role_lens": "synthesis",
        "days": [
            {
                "angle": "PM interview prep: the questions you will be asked",
                "focus": (
                    "The 10 AI PM interview questions asked most frequently in 2025-26. "
                    "How to answer: design an AI feature, evaluate model quality, handle hallucination in production. "
                    "The portfolio project walk-through: how to present the newsletter agent. "
                    "What Sarvam, Krutrim, and scaling AI companies specifically test for."
                ),
                "search_query": "AI PM interview questions 2025 design feature model quality production",
            },
            {
                "angle": "Strategy interview prep: the frameworks expected",
                "focus": (
                    "What a strategy role at an AI startup actually does day-to-day. "
                    "The frameworks expected: market sizing, competitive analysis, go-to-market. "
                    "How consulting experience translates — and where it does not. "
                    "The case study format most AI startups use in strategy interviews."
                ),
                "search_query": "AI startup strategy role interview frameworks consulting translation 2025",
            },
            {
                "angle": "VC analyst interview prep: the investment thesis exercise",
                "focus": (
                    "What a VC analyst interview at Blume or Accel India looks like. "
                    "The pitch exercise: evaluate this company in 48 hours. "
                    "How to structure an investment memo on an Indian AI company. "
                    "What partners are actually testing for when they ask about AI."
                ),
                "search_query": "VC analyst interview India AI fund investment memo Blume Accel 2025",
            },
            {
                "angle": "Your 30-60-90 day plan: PM version",
                "focus": (
                    "What a PM at Sarvam or Krutrim should achieve in the first 30, 60, and 90 days. "
                    "How to frame your consulting background as a speed advantage. "
                    "The first product decision you would want to make and why. "
                    "How to make the 30-60-90 feel specific to the company, not generic."
                ),
                "search_query": "AI PM 30 60 90 day plan Sarvam Krutrim first 90 days 2025",
            },
            {
                "angle": "Your 30-60-90 day plan: strategy version",
                "focus": (
                    "What a strategy hire at an early-stage AI startup should do in the first quarter. "
                    "Where consulting skills are immediately useful vs where they slow you down. "
                    "The market research, competitive intelligence, and GTM work of day one. "
                    "How to show you understand the startup pace difference from NRI."
                ),
                "search_query": "AI startup strategy hire first 90 days consulting transition pace 2025",
            },
            {
                "angle": "Compensation negotiation: the 50 LPA path",
                "focus": (
                    "What AI PM and strategy roles pay at Series B+ Indian AI companies. "
                    "How to frame 50 LPA as a target without anchoring too low or too high. "
                    "The components of an AI startup offer: base, ESOP, bonus, joining. "
                    "What leverage you have and how to use it."
                ),
                "search_query": "India AI PM strategy compensation 2025 2026 salary ESOP negotiation",
            },
            {
                "angle": "Week synthesis: your 90-day transformation in words",
                "focus": (
                    "How would you describe what you know today vs what you knew on day 1? "
                    "The one insight from the 90 days that changed how you think about AI. "
                    "What you will continue learning after day 90 and how. "
                    "The narrative you tell in every interview: who you are, what you built, where you are going."
                ),
                "search_query": "AI career pivot narrative transformation learning 2025 2026",
            },
        ],
    },

    # ── WEEK 13: BUFFER ───────────────────────────────────────────────────────
    {
        "week": 13,
        "phase": "Buffer",
        "topic": "Deep Dive: AI Technical Concepts Revisited",
        "role_lens": None,
        "days": [
            {
                "angle": "Fine-tuning revisited: when it is worth the cost",
                "focus": (
                    "Fine-tuning mechanics: supervised fine-tuning, RLHF, DPO. "
                    "The cost matrix: compute, data labeling, maintenance. "
                    "The exact scenarios where fine-tuning beats prompting + RAG. "
                    "How Indian AI companies are using fine-tuning for Indic languages."
                ),
                "search_query": "fine-tuning LLM SFT RLHF DPO when worth cost Indic language 2025",
            },
            {
                "angle": "Evals in production: how AI teams measure quality at scale",
                "focus": (
                    "How Anthropic, OpenAI, and Google run evals in production. "
                    "The eval stack: unit tests, integration evals, A/B tests, red teaming. "
                    "How a PM designs an eval framework without an ML background. "
                    "What eval failures look like and how to catch them before users do."
                ),
                "search_query": "AI evals production PM framework red teaming A/B test quality 2025",
            },
            {
                "angle": "Latency and quality trade-offs: the decisions a PM must own",
                "focus": (
                    "The latency budget: how much delay users tolerate for different task types. "
                    "Streaming vs batch: the UX implications of each. "
                    "Model cascade: using a fast cheap model first, escalating to expensive only when needed. "
                    "How to spec latency requirements in a product document."
                ),
                "search_query": "AI latency quality trade-off streaming batch cascade PM spec 2025",
            },
            {
                "angle": "Multimodal AI: what changes when the model can see and hear",
                "focus": (
                    "What multimodal means: text, image, audio, video in a single model. "
                    "Product opportunities that only exist because of multimodal. "
                    "The quality gaps that still exist in multimodal AI in 2026. "
                    "Indian-language multimodal: where it is and where it is going."
                ),
                "search_query": "multimodal AI product opportunities gaps Indian language 2025 2026",
            },
            {
                "angle": "AI infrastructure for PMs: what you need to understand about the stack",
                "focus": (
                    "The AI stack from GPU to API: what each layer does and who owns it. "
                    "Why PMs at AI companies need a working knowledge of inference infrastructure. "
                    "The vocabulary to use with infrastructure engineers without overstepping. "
                    "How infrastructure decisions constrain product decisions."
                ),
                "search_query": "AI infrastructure stack GPU inference PM knowledge vocabulary 2025",
            },
            {
                "angle": "On-device AI: the shift from cloud to edge",
                "focus": (
                    "Why AI is moving from cloud inference to on-device models. "
                    "Apple Intelligence, Qualcomm AI chips, and what they mean for product. "
                    "Privacy-preserving AI as a product differentiator. "
                    "Indian device market implications: offline-first AI for low-connectivity contexts."
                ),
                "search_query": "on-device AI edge inference Apple Intelligence Qualcomm privacy India 2025 2026",
            },
            {
                "angle": "Buffer synthesis: what you will keep learning",
                "focus": (
                    "The areas of AI that are moving fastest and require continuous learning. "
                    "How to stay current without spending 4 hours a day reading papers. "
                    "The three sources that give you 80 percent of the signal for 20 percent of the effort. "
                    "Your learning system for the next 90 days after this curriculum ends."
                ),
                "search_query": "AI staying current learning system efficient sources PM strategy 2025",
            },
        ],
    },
]

# ── SYNTHESIS ROTATION ────────────────────────────────────────────────────────
# Days within synthesis weeks rotate PM → Strategy → VC based on day-within-week
SYNTHESIS_ROLES = ["PM", "Strategy", "VC"]

ROLE_LENS_DESCRIPTIONS = {
    "PM": (
        f"You are targeting a PM role at a scaling AI company. "
        f"The reader is currently {USER_CURRENT_ROLE}. "
        f"Frame the pivot lens around: product spec decisions, feature prioritisation, "
        f"eval design, working with ML engineers, and how to demonstrate AI product "
        f"instincts in an interview."
    ),
    "Strategy": (
        f"You are targeting a Strategy or BD role at an early-stage AI startup. "
        f"The reader is currently {USER_CURRENT_ROLE}. "
        f"Frame the pivot lens around: go-to-market decisions, partnership strategy, "
        f"competitive positioning, and how their consulting skills translate directly "
        f"into an AI-native strategy context."
    ),
    "VC": (
        f"You are targeting a VC Analyst or Associate role at an AI-focused fund. "
        f"The reader is currently {USER_CURRENT_ROLE}. "
        f"Frame the pivot lens around: building an investment thesis, due diligence "
        f"frameworks, evaluating founding teams, and spotting defensible AI business models."
    ),
    "General": (
        f"You are building toward these roles: {USER_TARGET_ROLES}. "
        f"The reader is currently {USER_CURRENT_ROLE}. "
        f"Frame the pivot lens around what this topic means for someone pivoting into AI. "
        f"How does mastering this topic change how they speak in interviews? "
        f"What signal does it send to a hiring manager or investor?"
    ),
}


def get_today_topic() -> dict:
    """
    Returns the curriculum entry for today.
    Day 1 = START_DATE. Capped at day 90.
    Each week has 7 distinct daily sub-angles — no two days repeat the same focus.
    Synthesis weeks rotate role lens: PM → Strategy → VC by day-within-week.
    """
    today = date.today()
    days_elapsed = (today - START_DATE).days   # 0 on day 1
    day_number   = max(1, days_elapsed + 1)
    day_number   = min(day_number, 90)

    week_index     = min((day_number - 1) // 7, len(WEEKLY_CURRICULUM) - 1)
    day_in_week    = (day_number - 1) % 7       # 0-6 within the week

    week_entry = WEEKLY_CURRICULUM[week_index]
    day_entry  = week_entry["days"][day_in_week]

    entry = {
        "week":           week_entry["week"],
        "phase":          week_entry["phase"],
        "topic":          week_entry["topic"],
        "angle":          day_entry["angle"],
        "focus":          day_entry["focus"],
        "search_query":   day_entry["search_query"],
        "day_number":     day_number,
        "day_in_week":    day_in_week + 1,        # 1-7 for display
        "days_remaining": max(0, 90 - day_number),
    }

    # Role lens
    role_lens = week_entry["role_lens"]
    if role_lens == "synthesis":
        role_lens = SYNTHESIS_ROLES[day_in_week % 3]
    elif role_lens is None:
        role_lens = "General"

    entry["role_lens"]             = role_lens
    entry["role_lens_description"] = ROLE_LENS_DESCRIPTIONS[role_lens]
    return entry
