from __future__ import annotations

from datetime import UTC, date, datetime
from enum import StrEnum
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator


def validate_http_url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("URL must use HTTP or HTTPS")
    return value


class RecallCategory(StrEnum):
    CONSUMER_PRODUCT = "consumer_product"
    FOOD = "food"
    MEDICAL_DEVICE = "medical_device"


class RecallSource(StrEnum):
    CPSC = "cpsc"
    OPENFDA_FOOD = "openfda_food"
    OPENFDA_DEVICE = "openfda_device"


class ProductIdentifier(BaseModel):
    kind: str
    value: str


class RecallImage(BaseModel):
    url: str
    caption: str = ""

    _validate_url = field_validator("url")(validate_http_url)


class RecallRecord(BaseModel):
    id: str
    source: RecallSource
    source_id: str
    source_url: str
    title: str
    category: RecallCategory
    product_description: str
    hazard: str
    remedy: str
    recall_date: date
    status: str = "Open"
    severity: str = "Not classified"
    manufacturer: str = ""
    affected_units: str = ""
    identifiers: list[ProductIdentifier] = Field(default_factory=list)
    images: list[RecallImage] = Field(default_factory=list)
    synced_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )
    is_demo: bool = False

    _validate_source_url = field_validator("source_url")(validate_http_url)


class RecallSearchResponse(BaseModel):
    items: list[RecallRecord]
    total: int
    query: str


class MatchRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    product_name: str = Field(default="", max_length=160)
    brand: str = Field(default="", max_length=120)
    model: str = Field(default="", max_length=100)
    upc: str = Field(default="", max_length=50)
    lot: str = Field(default="", max_length=100)
    category: RecallCategory | None = None


class RecallMatch(BaseModel):
    recall: RecallRecord
    confidence: str
    score: int
    reasons: list[str]


class MatchResponse(BaseModel):
    matches: list[RecallMatch]
    checked: int
    exact_identifier_match: bool


class SourceStat(BaseModel):
    source: RecallSource
    count: int


class RecallStats(BaseModel):
    total: int
    active: int
    latest_date: date | None
    demo_mode: bool
    by_source: list[SourceStat]
