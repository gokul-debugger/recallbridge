import sqlite3

from fastapi.testclient import TestClient
from recallbridge.app import app


def test_api_search_and_match(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("RECALLBRIDGE_DB", str(tmp_path / "recalls.db"))

    with TestClient(app) as client:
        health = client.get("/api/health")
        recalls = client.get("/api/recalls", params={"q": "QuickHeat"})
        match = client.post("/api/match", json={"model": "QH-220"})

    assert health.json()["status"] == "ok"
    assert recalls.json()["total"] == 1
    assert match.json()["exact_identifier_match"] is True
    assert match.json()["matches"][0]["confidence"] == "exact"


def test_empty_match_request_is_rejected(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("RECALLBRIDGE_DB", str(tmp_path / "recalls.db"))

    with TestClient(app) as client:
        response = client.post("/api/match", json={})

    assert response.status_code == 422


def test_match_request_rejects_oversized_or_unknown_fields(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("RECALLBRIDGE_DB", str(tmp_path / "recalls.db"))

    with TestClient(app) as client:
        oversized = client.post("/api/match", json={"product_name": "x" * 161})
        unknown = client.post("/api/match", json={"product_name": "toaster", "secret": "value"})

    assert oversized.status_code == 422
    assert unknown.status_code == 422


def test_search_treats_like_metacharacters_as_literals(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("RECALLBRIDGE_DB", str(tmp_path / "recalls.db"))

    with TestClient(app) as client:
        response = client.get("/api/recalls", params={"q": "%"})

    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_completed_recalls_are_not_counted_as_active(tmp_path, monkeypatch) -> None:
    database = tmp_path / "recalls.db"
    monkeypatch.setenv("RECALLBRIDGE_DB", str(database))

    with TestClient(app) as client:
        with sqlite3.connect(database) as connection:
            connection.execute(
                "UPDATE recalls SET status = 'Completed' WHERE id = 'demo:cpsc:toaster'"
            )
        response = client.get("/api/stats")

    assert response.status_code == 200
    assert response.json()["total"] == 6
    assert response.json()["active"] == 5
