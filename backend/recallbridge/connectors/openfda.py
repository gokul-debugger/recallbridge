from __future__ import annotations

import re
from datetime import UTC, date, datetime
from urllib.parse import urlencode

import httpx

from ..models import (
    ProductIdentifier,
    RecallCategory,
    RecallRecord,
    RecallSource,
)

FOOD_ENDPOINT = "https://api.fda.gov/food/enforcement.json"
DEVICE_ENDPOINT = "https://api.fda.gov/device/recall.json"


def _compact_date(value: str) -> date:
    return datetime.strptime(value, "%Y%m%d").date()


def _iso_date(value: str) -> date:
    return date.fromisoformat(value)


def _identifiers(
    code_info: str,
    extra: list[tuple[str, str]] | None = None,
) -> list[ProductIdentifier]:
    found: list[ProductIdentifier] = []
    patterns = {
        "upc": r"\bUPC(?:\s+(?:No\.?|Number))?\s*[:#]?\s*([0-9][0-9 -]{7,18})",
        "lot": r"\bLot(?:\s+(?:No\.?|Number))?\s*[:#]?\s*([A-Za-z0-9][A-Za-z0-9._/-]{2,})",
        "serial": r"\bserial(?:\s+(?:No\.?|Number))?\s*[:#]?\s*([A-Za-z0-9][A-Za-z0-9._/-]{2,})",
    }
    for kind, pattern in patterns.items():
        for value in re.findall(pattern, code_info, flags=re.IGNORECASE):
            cleaned = re.sub(r"\s+", "", value).rstrip(".,;")
            found.append(ProductIdentifier(kind=kind, value=cleaned))
    for kind, value in extra or []:
        if value:
            found.append(ProductIdentifier(kind=kind, value=value))
    deduped = {(item.kind.lower(), item.value.lower()): item for item in found}
    return list(deduped.values())


def normalize_food(item: dict) -> RecallRecord:
    source_id = str(item["recall_number"])
    source_url = f"{FOOD_ENDPOINT}?{urlencode({'search': f'recall_number:\"{source_id}\"'})}"
    code_info = " ".join([item.get("code_info", ""), item.get("more_code_info", "")])
    return RecallRecord(
        id=f"openfda_food:{source_id}",
        source=RecallSource.OPENFDA_FOOD,
        source_id=source_id,
        source_url=source_url,
        title=f"{item.get('recalling_firm', 'Food product')} recall",
        category=RecallCategory.FOOD,
        product_description=item.get("product_description", ""),
        hazard=item.get("reason_for_recall", ""),
        remedy="Follow the firm's recall instructions and consult the linked FDA record.",
        recall_date=_compact_date(item["report_date"]),
        status=item.get("status", "Unknown"),
        severity=item.get("classification", "Not classified"),
        manufacturer=item.get("recalling_firm", ""),
        affected_units=item.get("product_quantity", ""),
        identifiers=_identifiers(code_info),
        synced_at=datetime.now(UTC),
    )


def normalize_device(item: dict) -> RecallRecord:
    source_id = str(item["cfres_id"])
    source_url = f"{DEVICE_ENDPOINT}?{urlencode({'search': f'cfres_id:{source_id}'})}"
    extra = [("model", value) for value in item.get("k_numbers") or []]
    return RecallRecord(
        id=f"openfda_device:{source_id}",
        source=RecallSource.OPENFDA_DEVICE,
        source_id=source_id,
        source_url=source_url,
        title=f"{item.get('recalling_firm', 'Medical device')} recall",
        category=RecallCategory.MEDICAL_DEVICE,
        product_description=item.get("product_description", ""),
        hazard=item.get("reason_for_recall", ""),
        remedy=item.get("action", "Consult the linked FDA record for the firm's action."),
        recall_date=_iso_date(item["event_date_posted"]),
        status=item.get("recall_status", "Unknown"),
        severity=item.get("root_cause_description", "Not classified"),
        manufacturer=item.get("recalling_firm", ""),
        affected_units=item.get("product_quantity", ""),
        identifiers=_identifiers(item.get("code_info", ""), extra),
        synced_at=datetime.now(UTC),
    )


async def _fetch(
    client: httpx.AsyncClient,
    endpoint: str,
    search: str,
    sort: str,
    limit: int,
) -> list[dict]:
    response = await client.get(
        endpoint,
        params={"search": search, "sort": sort, "limit": min(limit, 1000)},
    )
    response.raise_for_status()
    return response.json().get("results", [])


async def fetch_openfda_food(
    client: httpx.AsyncClient,
    start_date: date,
    limit: int = 100,
) -> list[RecallRecord]:
    start = start_date.strftime("%Y%m%d")
    end = date.today().strftime("%Y%m%d")
    items = await _fetch(
        client,
        FOOD_ENDPOINT,
        f"report_date:[{start} TO {end}]",
        "report_date:desc",
        limit,
    )
    return [normalize_food(item) for item in items]


async def fetch_openfda_device(
    client: httpx.AsyncClient,
    start_date: date,
    limit: int = 100,
) -> list[RecallRecord]:
    items = await _fetch(
        client,
        DEVICE_ENDPOINT,
        f"event_date_posted:[{start_date.isoformat()} TO {date.today().isoformat()}]",
        "event_date_posted:desc",
        limit,
    )
    return [normalize_device(item) for item in items]
