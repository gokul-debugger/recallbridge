from __future__ import annotations

import re
from datetime import UTC, date, datetime

import httpx

from ..models import (
    ProductIdentifier,
    RecallCategory,
    RecallImage,
    RecallRecord,
    RecallSource,
)

CPSC_ENDPOINT = "https://www.saferproducts.gov/RestWebServices/Recall"


def _first(items: list[dict], key: str) -> str:
    return str(items[0].get(key, "")) if items else ""


def _date(value: str) -> date:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).date()


def _description_models(description: str) -> list[str]:
    pattern = r"\bmodel(?:\s+(?:number|no\.?))?\s*[:#]?\s*[\"']?([A-Z0-9][A-Z0-9._/-]{2,})"
    return [
        value.rstrip(".,;:")
        for value in re.findall(pattern, description, flags=re.IGNORECASE)
    ]


def normalize_cpsc(item: dict) -> RecallRecord:
    source_id = str(item["RecallID"])
    products = item.get("Products") or []
    description = item.get("Description") or _first(products, "Description")
    identifiers: list[ProductIdentifier] = []
    for product in products:
        if product.get("Model"):
            identifiers.append(ProductIdentifier(kind="model", value=str(product["Model"])))
    for upc in item.get("ProductUPCs") or []:
        value = upc.get("UPC") or upc.get("Value") or upc.get("Name")
        if value:
            identifiers.append(ProductIdentifier(kind="upc", value=str(value)))
    identifiers.extend(
        ProductIdentifier(kind="model", value=value)
        for value in _description_models(description)
    )
    unique_identifiers = {
        (identifier.kind.lower(), identifier.value.lower()): identifier
        for identifier in identifiers
    }
    identifiers = list(
        unique_identifiers.values()
    )

    return RecallRecord(
        id=f"cpsc:{source_id}",
        source=RecallSource.CPSC,
        source_id=source_id,
        source_url=item.get("URL") or "https://www.cpsc.gov/Recalls",
        title=item.get("Title") or _first(products, "Name") or "CPSC recall",
        category=RecallCategory.CONSUMER_PRODUCT,
        product_description=description,
        hazard=" ".join(value.get("Name", "") for value in item.get("Hazards") or []).strip(),
        remedy=" ".join(value.get("Name", "") for value in item.get("Remedies") or []).strip(),
        recall_date=_date(item["RecallDate"]),
        status="Open",
        severity="Official safety recall",
        manufacturer=_first(item.get("Manufacturers") or [], "Name"),
        affected_units=_first(products, "NumberOfUnits"),
        identifiers=identifiers,
        images=[
            RecallImage(url=image["URL"], caption=image.get("Caption", ""))
            for image in item.get("Images") or []
            if image.get("URL")
        ][:6],
        synced_at=datetime.now(UTC),
    )


async def fetch_cpsc_recalls(
    client: httpx.AsyncClient,
    start_date: date,
    limit: int = 100,
) -> list[RecallRecord]:
    response = await client.get(
        CPSC_ENDPOINT,
        params={"format": "json", "RecallDateStart": start_date.isoformat()},
    )
    response.raise_for_status()
    payload = response.json()
    return [normalize_cpsc(item) for item in payload[:limit]]
