from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .matching import find_matches
from .models import (
    MatchRequest,
    MatchResponse,
    RecallCategory,
    RecallRecord,
    RecallSearchResponse,
    RecallSource,
    RecallStats,
)
from .storage import (
    all_recalls,
    get_recall,
    initialize_database,
    recall_stats,
    search_recalls,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="RecallBridge API",
    description="Normalized search and explainable matching for official recall data.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "recallbridge"}


@app.get("/api/recalls", response_model=RecallSearchResponse)
def recalls(
    q: str = Query(default="", max_length=120),
    category: RecallCategory | None = None,
    source: RecallSource | None = None,
    limit: int = Query(default=50, ge=1, le=100),
) -> RecallSearchResponse:
    items, total = search_recalls(q, category, source, limit)
    return RecallSearchResponse(items=items, total=total, query=q)


@app.get("/api/recalls/{recall_id}", response_model=RecallRecord)
def recall(recall_id: str) -> RecallRecord:
    item = get_recall(recall_id)
    if not item:
        raise HTTPException(status_code=404, detail="Recall not found")
    return item


@app.post("/api/match", response_model=MatchResponse)
def match_product(request: MatchRequest) -> MatchResponse:
    if not any([request.product_name, request.brand, request.model, request.upc, request.lot]):
        raise HTTPException(status_code=422, detail="Provide a product name or identifier")
    candidates = all_recalls()
    matches = find_matches(request, candidates)
    return MatchResponse(
        matches=matches,
        checked=len(candidates),
        exact_identifier_match=any(match.confidence == "exact" for match in matches),
    )


@app.get("/api/stats", response_model=RecallStats)
def stats() -> RecallStats:
    return RecallStats.model_validate(recall_stats())
