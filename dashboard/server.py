"""
dashboard/server.py  --  FastAPI backend for the Second Brain dashboard.

Run:  uvicorn dashboard.server:app --port 8501 --reload   (from jarvis/ root)
"""

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Optional

import chromadb
import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

def _find_jarvis_root() -> Path:
    """Walk up from this file to find the real jarvis root (contains second_brain/)."""
    candidate = Path(__file__).resolve().parent
    for _ in range(6):
        candidate = candidate.parent
        if (candidate / "second_brain").is_dir():
            return candidate
    return Path(__file__).resolve().parents[1]

ROOT = _find_jarvis_root()
sys.path.insert(0, str(ROOT / "agents" / "agent03"))
sys.path.insert(0, str(ROOT))

SECOND_BRAIN_ROOT = ROOT / "second_brain"
CHROMA_PATH       = str(ROOT / "data" / "chroma")
STATIC_DIR        = Path(__file__).parent / "static"

SOURCE_MAP: dict[str, str] = {
    "04_Work_Projects/Elevator_Business": "Elevator",
    "04_Work_Projects/Sustain_and_Co":    "Sustain & Co",
    "04_Work_Projects/NRI_Internship":    "Nomura",
    "04_Work_Projects/Solar_Energy":      "Solar",
    "04_Work_Projects/Aboli_JobSearch":   "Job Search",
    "05_AI_and_Tech":                     "AI & Tech",
    "03_Academic":                        "Academic",
    "07_Fonts":                           "Fonts",
    "02_MBA_Applications":                "MBA",
    "06_Media":                           "Media",
}

CAT_COLORS: dict[str, str] = {
    "Elevator":    "#a78bfa",
    "Sustain & Co":"#34d399",
    "Nomura":      "#60a5fa",
    "Solar":       "#fbbf24",
    "Job Search":  "#f472b6",
    "AI & Tech":   "#22d3ee",
    "Academic":    "#818cf8",
    "Fonts":       "#94a3b8",
    "MBA":         "#fb923c",
    "Media":       "#e879f9",
    "Other":       "#64748b",
}

TYPE_COLORS: dict[str, str] = {
    "analysis":     "#a78bfa",
    "observation":  "#34d399",
    "reference":    "#60a5fa",
    "fact":         "#fbbf24",
    "belief":       "#f472b6",
    "skill":        "#22d3ee",
    "event":        "#fb923c",
    "conversation": "#e879f9",
    "unknown":      "#64748b",
}

app = FastAPI(title="Second Brain")


# ── helpers ───────────────────────────────────────────────────────────────────

def _get_category(src: str) -> str:
    for key, label in SOURCE_MAP.items():
        if key in src:
            return label
    m = re.search(r"Documents/\d+_([^/]+)", src)
    return m.group(1).replace("_", " ") if m else "Other"


def _load_corpus() -> list[dict]:
    entries = []
    for f in sorted(SECOND_BRAIN_ROOT.rglob("*.md")):
        raw = f.read_text(errors="ignore")
        if not raw.startswith("---"):
            continue
        end = raw.find("---", 3)
        if end < 0:
            continue
        try:
            fm = yaml.safe_load(raw[3:end]) or {}
        except Exception:
            continue
        tags = fm.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]
        entries.append({
            "id":       str(fm.get("id", f.stem)),
            "file":     f.stem,
            "type":     fm.get("type", "unknown"),
            "category": _get_category(fm.get("source", "")),
            "tags":     [t.lower().strip() for t in tags if t],
            "summary":  fm.get("summary", ""),
            "date":     str(fm.get("date_created", ""))[:10],
            "source":   Path(fm.get("source", "")).name,
        })
    return entries


def _chunk_count() -> int:
    try:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        return client.get_collection("second_brain").count()
    except Exception:
        return 0


# ── API models ────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    query: str
    top_k: int = 5


# ── routes ────────────────────────────────────────────────────────────────────

@app.post("/api/chat")
async def chat(req: ChatRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="query is empty")

    try:
        from retriever import retrieve
        from query import _build_context, _synthesize, rewrite_query
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"Pipeline import failed: {e}")

    rewritten = rewrite_query(req.query)

    try:
        chunks = retrieve(query=rewritten, top_k=req.top_k)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    if not chunks:
        return {
            "answer": "I couldn't find anything relevant to that question in your second brain.",
            "sources": [],
        }

    context = _build_context(chunks)
    answer  = _synthesize(req.query, context)

    if not answer:
        raise HTTPException(status_code=500, detail="Synthesis failed")

    sources = []
    for chunk in chunks:
        meta = chunk["metadata"]
        fp   = meta.get("file_path") or meta.get("source") or ""
        sources.append({
            "name":    Path(fp).name or "unknown",
            "type":    meta.get("type", "unknown"),
            "tags":    meta.get("tags", ""),
            "snippet": chunk["text"][:120].replace("\n", " "),
        })

    return {"answer": answer, "sources": sources}


@app.get("/api/corpus")
async def corpus():
    entries = _load_corpus()
    chunks  = _chunk_count()

    all_tags   = [t for e in entries for t in e["tags"]]
    tag_counts = Counter(all_tags)
    top_tags   = [{"tag": t, "count": c} for t, c in tag_counts.most_common(20)]

    cat_counts  = Counter(e["category"] for e in entries)
    type_counts = Counter(e["type"] for e in entries)
    date_counts = Counter(e["date"] for e in entries if e["date"] and e["date"] != "None")

    top_domain = cat_counts.most_common(1)[0][0] if cat_counts else "—"

    return {
        "total":      len(entries),
        "chunks":     chunks,
        "unique_tags": len(tag_counts),
        "top_domain": top_domain,
        "categories": [
            {"label": k, "count": v, "color": CAT_COLORS.get(k, "#64748b")}
            for k, v in cat_counts.most_common()
        ],
        "types": [
            {"label": k, "count": v, "color": TYPE_COLORS.get(k, "#64748b")}
            for k, v in type_counts.most_common()
        ],
        "top_tags":  top_tags,
        "timeline":  [{"date": d, "count": c} for d, c in sorted(date_counts.items())],
    }


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


# Static files fallback (served after API routes)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
