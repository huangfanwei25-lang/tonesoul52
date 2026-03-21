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


def test_write_payload_normalizes_subjectivity_fields(tmp_path: Path) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    gateway = MemoryWriteGateway(db)

    record_id = gateway.write_payload(
        MemorySource.CUSTOM,
        {
            "type": "dream_collision",
            "summary": "Unresolved collision should stay as tension candidate.",
            "evidence": ["collision excerpt"],
            "provenance": {"source": "dream_engine"},
            "subjectivity_layer": " TENSION ",
            "confidence": 0.73,
            "source_record_ids": [" stim-1 ", "", "stim-2"],
            "decay_policy": "adaptive",
        },
    )

    records = list(db.stream(MemorySource.CUSTOM))

    assert record_id
    assert len(records) == 1
    assert records[0].payload["subjectivity_layer"] == "tension"
    assert records[0].payload["confidence"] == 0.73
    assert records[0].payload["source_record_ids"] == ["stim-1", "stim-2"]
    assert records[0].payload["decay_policy"] == {"policy": "adaptive"}


def test_write_payload_rejects_vow_without_review_gate(tmp_path: Path) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    gateway = MemoryWriteGateway(db)

    with pytest.raises(MemoryWriteRejectedError) as excinfo:
        gateway.write_payload(
            MemorySource.CUSTOM,
            {
                "type": "memory_promotion",
                "summary": "A single cycle should not write vows directly.",
                "evidence": ["cycle excerpt"],
                "provenance": {"source": "dream_engine"},
                "subjectivity_layer": "vow",
            },
        )

    assert excinfo.value.reasons == ["subjectivity_requires_review"]


def test_write_payload_allows_vow_with_review_gate(tmp_path: Path) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    gateway = MemoryWriteGateway(db)

    gateway.write_payload(
        MemorySource.CUSTOM,
        {
            "type": "memory_promotion",
            "summary": "Reviewed promotion into vow is allowed.",
            "evidence": ["review excerpt"],
            "provenance": {"source": "consolidator"},
            "subjectivity_layer": "vow",
            "promotion_gate": {
                "status": "reviewed",
                "reviewed_by": "sleep_consolidator",
                "review_basis": "Repeated tension across consolidation windows.",
            },
        },
    )

    records = list(db.stream(MemorySource.CUSTOM))

    assert len(records) == 1
    assert records[0].payload["subjectivity_layer"] == "vow"
    assert records[0].payload["promotion_gate"] == {
        "status": "reviewed",
        "reviewed_by": "sleep_consolidator",
        "review_basis": "Repeated tension across consolidation windows.",
    }


def test_write_payload_rejects_invalid_subjectivity_layer(tmp_path: Path) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    gateway = MemoryWriteGateway(db)

    with pytest.raises(MemoryWriteRejectedError) as excinfo:
        gateway.write_payload(
            MemorySource.CUSTOM,
            {
                "type": "handoff",
                "summary": "Invalid subjectivity layer should fail closed.",
                "evidence": ["artifact excerpt"],
                "provenance": {"source_file": "handoff.json"},
                "subjectivity_layer": "myth",
            },
        )

    assert excinfo.value.reasons == ["invalid_subjectivity_layer"]


def test_write_payload_rejects_vow_review_gate_without_review_basis(tmp_path: Path) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    gateway = MemoryWriteGateway(db)

    with pytest.raises(MemoryWriteRejectedError) as excinfo:
        gateway.write_payload(
            MemorySource.CUSTOM,
            {
                "type": "memory_promotion",
                "summary": "Review basis is required for auditability.",
                "evidence": ["review excerpt"],
                "provenance": {"source": "manual_review"},
                "subjectivity_layer": "vow",
                "promotion_gate": {
                    "status": "reviewed",
                    "reviewed_by": "operator",
                },
            },
        )

    assert excinfo.value.reasons == ["subjectivity_requires_review"]
