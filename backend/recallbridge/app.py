from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager, suppress
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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
from .syncing import sync_official_recalls

logger = logging.getLogger(__name__)


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes"}


async def _refresh_recalls(interval_seconds: int) -> None:
    while True:
        try:
            stored = await sync_official_recalls()
            logger.info("Official recall sync completed: %s", stored)
        except Exception:
            logger.exception("Official recall sync failed; existing records remain available")
        await asyncio.sleep(interval_seconds)


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    refresh_task: asyncio.Task[None] | None = None
    if _env_flag("RECALLBRIDGE_AUTO_SYNC"):
        interval = max(900, int(os.environ.get("RECALLBRIDGE_SYNC_INTERVAL", "21600")))
        refresh_task = asyncio.create_task(_refresh_recalls(interval))
    try:
        yield
    finally:
        if refresh_task:
            refresh_task.cancel()
            with suppress(asyncio.CancelledError):
                await refresh_task


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


frontend_dir = os.environ.get("RECALLBRIDGE_FRONTEND_DIR")
if frontend_dir:
    frontend_path = Path(frontend_dir)
    if not frontend_path.is_dir():
        raise RuntimeError(f"Frontend directory does not exist: {frontend_path}")
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
