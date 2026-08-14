from datetime import date

import pytest
from pydantic import ValidationError
from recallbridge.models import RecallCategory, RecallRecord, RecallSource


def test_recall_rejects_non_http_source_urls() -> None:
    with pytest.raises(ValidationError, match="URL must use HTTP or HTTPS"):
        RecallRecord(
            id="test:unsafe",
            source=RecallSource.CPSC,
            source_id="unsafe",
            source_url="javascript:alert(1)",
            title="Unsafe source",
            category=RecallCategory.CONSUMER_PRODUCT,
            product_description="Example",
            hazard="Example",
            remedy="Example",
            recall_date=date(2026, 8, 15),
        )
