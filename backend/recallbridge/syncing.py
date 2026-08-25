from __future__ import annotations

import asyncio
import logging
from datetime import date, timedelta

import httpx

from .connectors import fetch_cpsc_recalls, fetch_openfda_device, fetch_openfda_food
from .storage import delete_demo_records, initialize_database, upsert_recalls

logger = logging.getLogger(__name__)


async def sync_official_recalls(days: int = 365, limit: int = 100) -> dict[str, int]:
    """Fetch recent official records and return stored counts by source."""
    start_date = date.today() - timedelta(days=max(1, days))
    request_limit = max(1, min(limit, 1000))
    headers = {"User-Agent": "RecallBridge/0.1 (open-source recall index)"}

    async with httpx.AsyncClient(
        timeout=40,
        follow_redirects=True,
        headers=headers,
    ) as client:
        jobs = {
            "CPSC": fetch_cpsc_recalls(client, start_date, request_limit),
            "openFDA food": fetch_openfda_food(client, start_date, request_limit),
            "openFDA device": fetch_openfda_device(client, start_date, request_limit),
        }
        results = await asyncio.gather(*jobs.values(), return_exceptions=True)

    initialize_database()
    successful_records = [
        result for result in results if not isinstance(result, BaseException) and result
    ]
    if successful_records:
        delete_demo_records()

    stored_by_source: dict[str, int] = {}
    for source, result in zip(jobs, results, strict=True):
        if isinstance(result, BaseException):
            logger.warning("%s recall sync failed: %s", source, result)
            stored_by_source[source] = 0
            continue
        stored_by_source[source] = upsert_recalls(result)

    if not any(stored_by_source.values()):
        raise RuntimeError("No official recall source returned records")

    return stored_by_source
