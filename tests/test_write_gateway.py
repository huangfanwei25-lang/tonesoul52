from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB
from tonesoul.memory.write_gateway import MemoryWriteGateway, MemoryWriteRejectedError


def test_write_payload_rejects_missing_provenance(tmp_path: Path) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    gateway = MemoryWriteGateway(db)

    with pytest.raises(MemoryWriteRejectedError) as excinfo:
        gateway.write_payload(
            MemorySource.CUSTOM,
            {
                "type": "handoff",
                "summary": "Imported handoff without provenance should fail.",
                "evidence": ["artifact excerpt"],
            },
        )

    assert excinfo.value.reasons == ["missing_provenance"]


def test_write_payload_rejects_missing_evidence(tmp_path: Path) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    gateway = MemoryWriteGateway(db)

    with pytest.raises(MemoryWriteRejectedError) as excinfo:
        gateway.write_payload(
            MemorySource.CUSTOM,
            {
                "type": "handoff",
                "summary": "Missing evidence should fail.",
                "provenance": {"source_file": "handoff.json"},
            },
        )

    assert excinfo.value.reasons == ["missing_evidence"]


def test_gateway_persists_provenance_into_sqlite_schema(tmp_path: Path) -> None:
    db_path = tmp_path / "soul.db"
    db = SqliteSoulDB(db_path=db_path)
    gateway = MemoryWriteGateway(db)

    record_id = gateway.write_payload(
        MemorySource.CUSTOM,
        {
            "type": "handoff",
            "summary": "Imported via gateway.",
            "evidence": ["Imported via gateway."],
            "provenance": {"source_file": "handoff.json", "kind": "handoff_json"},
        },
    )

    conn = sqlite3.connect(db_path)
    columns = {str(row[1]) for row in conn.execute("PRAGMA table_info(memories)")}
    row = conn.execute("SELECT provenance FROM memories WHERE id = ?", (record_id,)).fetchone()
    conn.close()

    assert "provenance" in columns
    assert row is not None
    assert json.loads(str(row[0])) == {"source_file": "handoff.json", "kind": "handoff_json"}

    records = list(db.stream(MemorySource.CUSTOM))
    assert records[0].payload["provenance"] == {
        "source_file": "handoff.json",
        "kind": "handoff_json",
    }
