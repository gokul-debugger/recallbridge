from recallbridge.connectors.cpsc import normalize_cpsc
from recallbridge.connectors.openfda import normalize_device, normalize_food


def test_cpsc_normalization_preserves_source_and_identifiers() -> None:
    record = normalize_cpsc(
        {
            "RecallID": 42,
            "RecallDate": "2026-07-23T00:00:00",
            "URL": "https://www.cpsc.gov/Recalls/example",
            "Title": "Example toaster recall",
            "Description": "Two-slice toaster.",
            "Products": [{"Name": "Toaster", "Model": "T-42", "NumberOfUnits": "100"}],
            "ProductUPCs": [{"UPC": "123456789012"}],
            "Hazards": [{"Name": "Can overheat."}],
            "Remedies": [{"Name": "Stop using it."}],
            "Manufacturers": [{"Name": "Example Co."}],
            "Images": [{"URL": "https://example.gov/image.jpg", "Caption": "Product"}],
        }
    )

    assert record.id == "cpsc:42"
    assert {item.kind for item in record.identifiers} == {"model", "upc"}
    assert record.hazard == "Can overheat."


def test_cpsc_normalization_extracts_models_from_description() -> None:
    record = normalize_cpsc(
        {
            "RecallID": 43,
            "RecallDate": "2026-08-13T00:00:00",
            "Title": "Pressure washer recall",
            "Description": 'Model number "HD14P-Z" is on the label. Also sold as model no. HX18.',
            "Products": [{"Name": "Pressure washer", "Model": ""}],
        }
    )

    assert [item.value for item in record.identifiers] == ["HD14P-Z", "HX18"]


def test_food_normalization_extracts_upc_and_lot() -> None:
    record = normalize_food(
        {
            "recall_number": "F-1000-2026",
            "report_date": "20260801",
            "recalling_firm": "Example Foods",
            "product_description": "Example granola",
            "reason_for_recall": "Undeclared allergen.",
            "status": "Ongoing",
            "classification": "Class I",
            "product_quantity": "200 bags",
            "code_info": "UPC No. 123456789012; Lot No. LOT-42",
            "more_code_info": "",
        }
    )

    assert record.id == "openfda_food:F-1000-2026"
    assert [(item.kind, item.value) for item in record.identifiers] == [
        ("upc", "123456789012"),
        ("lot", "LOT-42"),
    ]


def test_device_normalization_preserves_action() -> None:
    record = normalize_device(
        {
            "cfres_id": "30043",
            "event_date_posted": "2026-08-01",
            "recall_status": "Ongoing",
            "product_description": "Portable monitor",
            "code_info": "serial #ABC123",
            "k_numbers": ["K020436"],
            "recalling_firm": "Example Medical",
            "reason_for_recall": "Incorrect reading.",
            "root_cause_description": "Software Design",
            "action": "Install the correction.",
            "product_quantity": "50 units",
        }
    )

    assert record.remedy == "Install the correction."
    assert {item.kind for item in record.identifiers} == {"serial", "model"}
