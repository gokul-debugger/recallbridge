from datetime import UTC, date, datetime

from recallbridge.matching import find_matches
from recallbridge.models import (
    MatchRequest,
    ProductIdentifier,
    RecallCategory,
    RecallRecord,
    RecallSource,
)


def recall() -> RecallRecord:
    return RecallRecord(
        id="test:1",
        source=RecallSource.CPSC,
        source_id="1",
        source_url="https://example.gov/recall/1",
        title="Northstar QuickHeat toaster recall",
        category=RecallCategory.CONSUMER_PRODUCT,
        product_description="Two-slice toaster model QH-220",
        hazard="Housing can overheat.",
        remedy="Stop using it.",
        recall_date=date(2026, 8, 1),
        manufacturer="Northstar Home",
        identifiers=[
            ProductIdentifier(kind="model", value="QH-220"),
            ProductIdentifier(kind="upc", value="012345678905"),
        ],
        synced_at=datetime.now(UTC),
    )


def test_exact_identifier_beats_text_similarity() -> None:
    matches = find_matches(MatchRequest(upc="0123 4567 8905"), [recall()])

    assert matches[0].confidence == "exact"
    assert matches[0].score == 100
    assert matches[0].reasons == ["Exact UPC match"]


def test_product_name_returns_explainable_possible_match() -> None:
    matches = find_matches(
        MatchRequest(product_name="QuickHeat two slice toaster", brand="Northstar"),
        [recall()],
    )

    assert matches
    assert matches[0].score >= 30
    assert "Product name resembles the recall description" in matches[0].reasons


def test_unrelated_product_is_not_returned() -> None:
    matches = find_matches(MatchRequest(product_name="garden hose"), [recall()])

    assert matches == []
