from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB
from tonesoul.memory.write_gateway import (
    MemoryWriteGateway,
    MemoryWriteRejectedError,
    MemoryWriteResult,
    _has_evidence,
    _has_provenance,
    _has_strong_promotion_gate,
    _intentional_forgetting_gate,
)


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


# ── _has_evidence ─────────────────────────────────────────────────────────────


def test_has_evidence_from_evidence_ids() -> None:
    assert _has_evidence({"evidence_ids": ["id_1"]}) is True
    assert _has_evidence({"evidence_ids": ["  "]}) is False
    assert _has_evidence({"evidence_ids": []}) is False


def test_has_evidence_from_evidence_list() -> None:
    assert _has_evidence({"evidence": ["artifact"]}) is True
    assert _has_evidence({"evidence": []}) is False


def test_has_evidence_from_transcript_contract_records() -> None:
    payload = {"transcript": {"multi_agent_contract": {"records": [{"evidence": ["trace://one"]}]}}}
    assert _has_evidence(payload) is True


def test_has_evidence_returns_false_for_empty_payload() -> None:
    assert _has_evidence({}) is False


# ── _has_provenance ───────────────────────────────────────────────────────────


def test_has_provenance_from_intent_id() -> None:
    assert _has_provenance({"intent_id": "abc"}) is True
    assert _has_provenance({"intent_id": "  "}) is False


def test_has_provenance_from_genesis_dict() -> None:
    assert _has_provenance({"genesis": {"source": "test"}}) is True
    assert _has_provenance({"genesis": {}}) is False


def test_has_provenance_from_transcript() -> None:
    payload = {"transcript": {"intent_id": "tx-1"}}
    assert _has_provenance(payload) is True


def test_has_provenance_returns_false_for_empty() -> None:
    assert _has_provenance({}) is False


# ── _intentional_forgetting_gate ──────────────────────────────────────────────


def test_forgetting_gate_bypasses_handoff_types() -> None:
    for t in ("handoff", "crystal", "audit", "governance_retro"):
        keep, reasons = _intentional_forgetting_gate({"type": t, "content": ""})
        assert keep is True
        assert reasons == []


def test_forgetting_gate_rejects_short_content() -> None:
    keep, reasons = _intentional_forgetting_gate({"content": "hi"})
    assert keep is False
    assert "content_too_short" in reasons


def test_forgetting_gate_rejects_ephemeral_tag() -> None:
    keep, reasons = _intentional_forgetting_gate(
        {
            "content": "sufficient content to pass length check",
            "tags": ["ephemeral"],
        }
    )
    assert keep is False
    assert "ephemeral_tag" in reasons


def test_forgetting_gate_rejects_passive_noise() -> None:
    keep, reasons = _intentional_forgetting_gate(
        {
            "content": "sufficient content to pass length check",
            "observation_mode": "passive_noise",
        }
    )
    assert keep is False
    assert "passive_noise" in reasons


def test_forgetting_gate_passes_normal_content() -> None:
    keep, reasons = _intentional_forgetting_gate({"content": "sufficient content here"})
    assert keep is True
    assert reasons == []


# ── _has_strong_promotion_gate ────────────────────────────────────────────────


def test_strong_promotion_gate_string_reviewed() -> None:
    assert _has_strong_promotion_gate({"promotion_gate": "approved"}) is True
    assert _has_strong_promotion_gate({"promotion_gate": "pending"}) is False


def test_strong_promotion_gate_dict_with_status_and_basis() -> None:
    gate = {"status": "reviewed", "review_basis": "consolidation confirmed"}
    assert _has_strong_promotion_gate({"promotion_gate": gate}) is True


def test_strong_promotion_gate_dict_without_basis_fails() -> None:
    gate = {"status": "reviewed"}
    assert _has_strong_promotion_gate({"promotion_gate": gate}) is False


def test_strong_promotion_gate_reviewed_by_list() -> None:
    gate = {"reviewed_by": ["alice", "bob"], "review_basis": "manual check"}
    assert _has_strong_promotion_gate({"promotion_gate": gate}) is True


# ── MemoryWriteRejectedError ──────────────────────────────────────────────────


def test_memory_write_rejected_error_formats_message() -> None:
    exc = MemoryWriteRejectedError(["missing_evidence", "missing_provenance"])
    assert exc.reasons == ["missing_evidence", "missing_provenance"]
    assert "missing_evidence" in str(exc)


def test_memory_write_rejected_error_empty_reasons() -> None:
    exc = MemoryWriteRejectedError([])
    assert exc.reasons == []
    assert str(exc) == "memory write rejected"


# ── MemoryWriteResult ─────────────────────────────────────────────────────────


def test_memory_write_result_defaults() -> None:
    result = MemoryWriteResult()
    assert result.written == 0
    assert result.skipped == 0
    assert result.rejected == 0
    assert result.record_ids == []
    assert result.reject_reasons == []


# ── MemoryWriteGateway._merge_tags ───────────────────────────────────────────


def test_merge_tags_deduplicates_and_always_includes_defaults(tmp_path: Path) -> None:
    gw = MemoryWriteGateway(SqliteSoulDB(db_path=tmp_path / "soul.db"))
    tags = gw._merge_tags(["alpha", "environment", "alpha"], observation_mode="feed")
    assert "environment" in tags
    assert "perception" in tags
    assert "observation:feed" in tags
    assert tags.count("alpha") == 1


def test_merge_tags_empty_input_adds_defaults(tmp_path: Path) -> None:
    gw = MemoryWriteGateway(SqliteSoulDB(db_path=tmp_path / "soul.db"))
    tags = gw._merge_tags(None)
    assert "environment" in tags
    assert "perception" in tags


# ── MemoryWriteGateway.write_payload type guard ───────────────────────────────


def test_write_payload_raises_type_error_for_non_dict(tmp_path: Path) -> None:
    gw = MemoryWriteGateway(SqliteSoulDB(db_path=tmp_path / "soul.db"))
    with pytest.raises(TypeError):
        gw.write_payload(MemorySource.CUSTOM, "not a dict")  # type: ignore[arg-type]
