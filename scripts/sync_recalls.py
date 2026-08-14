from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import date, timedelta
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from recallbridge.connectors import (  # noqa: E402
    fetch_cpsc_recalls,
    fetch_openfda_device,
    fetch_openfda_food,
)
from recallbridge.storage import (  # noqa: E402
    delete_demo_records,
    initialize_database,
    upsert_recalls,
)


async def sync(days: int, limit: int) -> None:
    start_date = date.today() - timedelta(days=days)
    headers = {"User-Agent": "RecallBridge/0.1 (open-source recall index)"}
    async with httpx.AsyncClient(timeout=40, follow_redirects=True, headers=headers) as client:
        jobs = {
            "CPSC": fetch_cpsc_recalls(client, start_date, limit),
            "openFDA food": fetch_openfda_food(client, start_date, limit),
            "openFDA device": fetch_openfda_device(client, start_date, limit),
        }
        results = await asyncio.gather(*jobs.values(), return_exceptions=True)

    initialize_database()
    if any(not isinstance(result, Exception) and result for result in results):
        delete_demo_records()
    stored_sources = 0
    for source, result in zip(jobs, results, strict=True):
        if isinstance(result, Exception):
            print(f"{source}: failed ({result})")
            continue
        stored = upsert_recalls(result)
        stored_sources += int(stored > 0)
        print(f"{source}: stored {stored} records")
    if stored_sources == 0:
        raise RuntimeError("No official recall source returned records")


def main() -> None:
    parser = argparse.ArgumentParser(description="Synchronize recent official recall data")
    parser.add_argument("--days", type=int, default=365, help="Lookback window")
    parser.add_argument("--limit", type=int, default=100, help="Maximum records per source")
    args = parser.parse_args()
    asyncio.run(sync(max(1, args.days), max(1, min(args.limit, 1000))))


if __name__ == "__main__":
    main()
