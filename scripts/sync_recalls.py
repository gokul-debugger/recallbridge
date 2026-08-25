from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from recallbridge.syncing import sync_official_recalls  # noqa: E402


async def sync(days: int, limit: int) -> None:
    stored_by_source = await sync_official_recalls(days, limit)
    for source, stored in stored_by_source.items():
        print(f"{source}: stored {stored} records")


def main() -> None:
    parser = argparse.ArgumentParser(description="Synchronize recent official recall data")
    parser.add_argument("--days", type=int, default=365, help="Lookback window")
    parser.add_argument("--limit", type=int, default=100, help="Maximum records per source")
    args = parser.parse_args()
    asyncio.run(sync(args.days, args.limit))


if __name__ == "__main__":
    main()
