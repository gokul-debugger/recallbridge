import asyncio
from datetime import date

import pytest
from recallbridge import syncing
from recallbridge.models import RecallRecord


def _record(source_id: str = "123") -> RecallRecord:
    return RecallRecord.model_validate(
        {
            "id": f"cpsc:{source_id}",
            "source": "cpsc",
            "source_id": source_id,
            "source_url": "https://example.com/recall",
            "title": "Test recall",
            "category": "consumer_product",
            "product_description": "Test product",
            "hazard": "Test hazard",
            "remedy": "Stop use",
            "recall_date": date.today(),
            "status": "active",
            "severity": "warning",
            "manufacturer": "Test maker",
            "affected_units": "1",
            "identifiers": [],
            "images": [],
            "synced_at": date.today(),
            "is_demo": False,
        }
    )


def test_sync_keeps_successful_sources_when_another_source_fails(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("RECALLBRIDGE_DB", str(tmp_path / "recalls.db"))

    async def successful(*_args):
        return [_record()]

    async def empty(*_args):
        return []

    async def failing(*_args):
        raise RuntimeError("source unavailable")

    monkeypatch.setattr(syncing, "fetch_cpsc_recalls", successful)
    monkeypatch.setattr(syncing, "fetch_openfda_food", empty)
    monkeypatch.setattr(syncing, "fetch_openfda_device", failing)

    result = asyncio.run(syncing.sync_official_recalls())

    assert result == {"CPSC": 1, "openFDA food": 0, "openFDA device": 0}


def test_sync_fails_when_no_source_returns_records(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("RECALLBRIDGE_DB", str(tmp_path / "recalls.db"))

    async def empty(*_args):
        return []

    monkeypatch.setattr(syncing, "fetch_cpsc_recalls", empty)
    monkeypatch.setattr(syncing, "fetch_openfda_food", empty)
    monkeypatch.setattr(syncing, "fetch_openfda_device", empty)

    with pytest.raises(RuntimeError, match="No official recall source"):
        asyncio.run(syncing.sync_official_recalls())
