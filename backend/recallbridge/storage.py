from __future__ import annotations

import json
import os
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path

from .models import RecallCategory, RecallRecord, RecallSource

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE = PACKAGE_ROOT / "data" / "recalls.db"
SEED_FILE = PACKAGE_ROOT / "data" / "seed_recalls.json"


def database_path() -> Path:
    return Path(os.environ.get("RECALLBRIDGE_DB", DEFAULT_DATABASE))


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode = WAL")
    db.execute("PRAGMA foreign_keys = ON")
    try:
        yield db
        db.commit()
    finally:
        db.close()


def initialize_database() -> None:
    with connection() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS recalls (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                source_id TEXT NOT NULL,
                source_url TEXT NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                product_description TEXT NOT NULL,
                hazard TEXT NOT NULL,
                remedy TEXT NOT NULL,
                recall_date TEXT NOT NULL,
                status TEXT NOT NULL,
                severity TEXT NOT NULL,
                manufacturer TEXT NOT NULL,
                affected_units TEXT NOT NULL,
                identifiers TEXT NOT NULL,
                images TEXT NOT NULL,
                synced_at TEXT NOT NULL,
                is_demo INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        db.execute("CREATE INDEX IF NOT EXISTS recalls_date_idx ON recalls(recall_date DESC)")
        db.execute("CREATE INDEX IF NOT EXISTS recalls_source_idx ON recalls(source)")
        count = db.execute("SELECT COUNT(*) FROM recalls").fetchone()[0]
    if count == 0 and SEED_FILE.exists():
        seed_records = [
            RecallRecord.model_validate(item)
            for item in json.loads(SEED_FILE.read_text())
        ]
        upsert_recalls(seed_records)


def upsert_recalls(records: list[RecallRecord]) -> int:
    if not records:
        return 0
    rows = [
        (
            record.id,
            record.source.value,
            record.source_id,
            record.source_url,
            record.title,
            record.category.value,
            record.product_description,
            record.hazard,
            record.remedy,
            record.recall_date.isoformat(),
            record.status,
            record.severity,
            record.manufacturer,
            record.affected_units,
            json.dumps([item.model_dump() for item in record.identifiers]),
            json.dumps([item.model_dump() for item in record.images]),
            record.synced_at.isoformat(),
            int(record.is_demo),
        )
        for record in records
    ]
    with connection() as db:
        db.executemany(
            """
            INSERT INTO recalls (
                id, source, source_id, source_url, title, category,
                product_description, hazard, remedy, recall_date, status,
                severity, manufacturer, affected_units, identifiers, images,
                synced_at, is_demo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                source_url=excluded.source_url,
                title=excluded.title,
                product_description=excluded.product_description,
                hazard=excluded.hazard,
                remedy=excluded.remedy,
                recall_date=excluded.recall_date,
                status=excluded.status,
                severity=excluded.severity,
                manufacturer=excluded.manufacturer,
                affected_units=excluded.affected_units,
                identifiers=excluded.identifiers,
                images=excluded.images,
                synced_at=excluded.synced_at,
                is_demo=excluded.is_demo
            """,
            rows,
        )
    return len(rows)


def delete_demo_records() -> int:
    with connection() as db:
        cursor = db.execute("DELETE FROM recalls WHERE is_demo = 1")
    return cursor.rowcount


def _to_record(row: sqlite3.Row) -> RecallRecord:
    return RecallRecord.model_validate(
        {
            **dict(row),
            "identifiers": json.loads(row["identifiers"]),
            "images": json.loads(row["images"]),
            "is_demo": bool(row["is_demo"]),
        }
    )


def search_recalls(
    query: str = "",
    category: RecallCategory | None = None,
    source: RecallSource | None = None,
    limit: int = 50,
) -> tuple[list[RecallRecord], int]:
    clauses: list[str] = []
    values: list[object] = []
    if query.strip():
        escaped_query = (
            query.strip().lower().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        )
        pattern = f"%{escaped_query}%"
        clauses.append(
            "LOWER(title || ' ' || product_description || ' ' || manufacturer "
            "|| ' ' || hazard || ' ' || identifiers) LIKE ? ESCAPE '\\'"
        )
        values.append(pattern)
    if category:
        clauses.append("category = ?")
        values.append(category.value)
    if source:
        clauses.append("source = ?")
        values.append(source.value)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    with connection() as db:
        total = db.execute(f"SELECT COUNT(*) FROM recalls {where}", values).fetchone()[0]
        rows = db.execute(
            f"SELECT * FROM recalls {where} ORDER BY recall_date DESC, title LIMIT ?",
            [*values, limit],
        ).fetchall()
    return [_to_record(row) for row in rows], total


def get_recall(recall_id: str) -> RecallRecord | None:
    with connection() as db:
        row = db.execute("SELECT * FROM recalls WHERE id = ?", (recall_id,)).fetchone()
    return _to_record(row) if row else None


def all_recalls() -> list[RecallRecord]:
    with connection() as db:
        rows = db.execute("SELECT * FROM recalls ORDER BY recall_date DESC").fetchall()
    return [_to_record(row) for row in rows]


def recall_stats() -> dict[str, object]:
    with connection() as db:
        total, active, latest, demo_count = db.execute(
            """
            SELECT COUNT(*),
                   SUM(CASE WHEN LOWER(status) NOT IN (
                       'completed', 'terminated', 'closed'
                   ) THEN 1 ELSE 0 END),
                   MAX(recall_date),
                   SUM(is_demo)
            FROM recalls
            """
        ).fetchone()
        sources = db.execute(
            "SELECT source, COUNT(*) AS count FROM recalls GROUP BY source ORDER BY count DESC"
        ).fetchall()
    return {
        "total": total,
        "active": active or 0,
        "latest_date": date.fromisoformat(latest) if latest else None,
        "demo_mode": bool(total and demo_count == total),
        "by_source": [dict(row) for row in sources],
    }
