"""Test AI Sleep memory consolidation."""

from __future__ import annotations

from tonesoul.memory.consolidator import (
    SleepResult,
    _classify_for_promotion,
    build_reviewed_vow_payload,
    promote_reviewed_tension_to_vow,
    sleep_consolidate,
)
from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource


def _build_db(tmp_path):
    source = MemorySource.SELF_JOURNAL
    db = JsonlSoulDB(source_map={source: tmp_path / "self_journal.jsonl"})
    return db, source


def test_classify_commitment_as_factual():
    payload = {"text": "I commit to being honest"}
    assert _classify_for_promotion(payload) == "factual"


def test_classify_emotion_as_experiential():
    payload = {"text": "I feel conflicted about this"}
    assert _classify_for_promotion(payload) == "experiential"


def test_classify_generic_stays_working():
    payload = {"text": "random unrelated text"}
    assert _classify_for_promotion(payload) == "working"


def test_classify_chinese_keywords():
    assert _classify_for_promotion({"text": "我承諾不再犯"}) == "factual"
    assert _classify_for_promotion({"text": "心裡感覺很衝突"}) == "experiential"


def test_sleep_consolidate_empty_db(tmp_path):
    db, _ = _build_db(tmp_path)
    result = sleep_consolidate(db)
    assert isinstance(result, SleepResult)
    assert result.promoted_count == 0
    assert result.cleared_count == 0
    assert result.gated_count == 0


def test_sleep_consolidate_promotes_commitment(tmp_path):
    db, source = _build_db(tmp_path)
    db.append(
        source,
        {
            "text": "I promise to listen more",
            "layer": "working",
            "evidence_ids": ["ev-001"],
            "intent_id": "intent-001",
        },
    )

    result = sleep_consolidate(db, source=source)
    factual_records = list(db.query(source, layer="factual"))
    working_records = list(db.query(source, layer="working"))
    factual_payload = factual_records[0].payload

    assert result.promoted_count == 1
    assert result.gated_count == 0
    assert len(factual_records) == 1
    assert len(working_records) == 1
    assert factual_payload["subjectivity_layer"] == "event"
    assert factual_payload["promotion_gate"] == {
        "status": "candidate",
        "source": "sleep_consolidate",
    }
    assert factual_payload["source_record_ids"]


def test_sleep_result_has_layer_summary(tmp_path):
    db, source = _build_db(tmp_path)
    db.append(source, {"text": "test", "layer": "experiential"})
    result = sleep_consolidate(db, source=source)
    assert "experiential" in result.layer_summary
    assert isinstance(result.layer_summary["experiential"], int)


def test_sleep_result_includes_subjectivity_summary(tmp_path):
    db, source = _build_db(tmp_path)
    db.append(
        source,
        {
            "text": "I promise to keep provenance explicit",
            "layer": "working",
            "evidence_ids": ["ev-100"],
            "intent_id": "intent-100",
        },
    )

    result = sleep_consolidate(db, source=source)

    assert result.subjectivity_summary["total_records"] == 2
    assert result.subjectivity_summary["by_memory_layer"] == {"working": 1, "factual": 1}
    assert result.subjectivity_summary["by_subjectivity_layer"]["event"] == 1
    assert result.subjectivity_summary["by_subjectivity_layer"]["unclassified"] == 1
    assert result.subjectivity_summary["by_source"] == {"self_journal": 2}


def test_sleep_consolidate_blocks_promotion_without_evidence(tmp_path):
    db, source = _build_db(tmp_path)
    db.append(
        source,
        {
            "text": "I promise to keep this commitment",
            "layer": "working",
            "intent_id": "intent-002",
        },
    )

    result = sleep_consolidate(db, source=source)
    factual_records = list(db.query(source, layer="factual"))
    assert result.promoted_count == 0
    assert result.gated_count == 1
    assert result.gate_failures.get("missing_evidence") == 1
    assert len(factual_records) == 0


def test_sleep_consolidate_blocks_promotion_without_provenance(tmp_path):
    db, source = _build_db(tmp_path)
    db.append(
        source,
        {
            "text": "I promise to keep this commitment",
            "layer": "working",
            "evidence_ids": ["ev-002"],
        },
    )

    result = sleep_consolidate(db, source=source)
    factual_records = list(db.query(source, layer="factual"))
    assert result.promoted_count == 0
    assert result.gated_count == 1
    assert result.gate_failures.get("missing_provenance") == 1
    assert len(factual_records) == 0


def test_sleep_consolidate_preserves_existing_subjectivity_layer(tmp_path):
    db, source = _build_db(tmp_path)
    db.append(
        source,
        {
            "text": "I feel conflict tension around this decision",
            "layer": "working",
            "evidence_ids": ["ev-003"],
            "intent_id": "intent-003",
            "subjectivity_layer": "tension",
        },
    )

    result = sleep_consolidate(db, source=source)
    experiential_records = list(db.query(source, layer="experiential"))

    assert result.promoted_count == 1
    assert len(experiential_records) == 1
    assert experiential_records[0].payload["subjectivity_layer"] == "tension"


def test_build_reviewed_vow_payload_promotes_tension_candidate() -> None:
    payload = build_reviewed_vow_payload(
        {
            "summary": "Persistent unresolved governance conflict.",
            "evidence": ["cycle-1", "cycle-2"],
            "provenance": {"source": "dream_engine"},
            "subjectivity_layer": "tension",
            "layer": "working",
            "source_record_ids": ["stim-001"],
        },
        reviewed_by="operator",
        review_basis="Repeated tension across two reviewed cycles.",
    )

    assert payload["layer"] == "factual"
    assert payload["subjectivity_layer"] == "vow"
    assert payload["review_basis"] == "Repeated tension across two reviewed cycles."
    assert payload["source_record_ids"] == ["stim-001"]
    assert payload["promotion_gate"]["status"] == "reviewed"
    assert payload["promotion_gate"]["reviewed_by"] == "operator"
    assert (
        payload["promotion_gate"]["review_basis"] == "Repeated tension across two reviewed cycles."
    )


def test_build_reviewed_vow_payload_rejects_non_tension_source() -> None:
    import pytest

    with pytest.raises(ValueError, match="tension candidate"):
        build_reviewed_vow_payload(
            {
                "summary": "Plain event should not jump straight to vow.",
                "evidence": ["artifact"],
                "provenance": {"source": "handoff"},
                "subjectivity_layer": "event",
            },
            reviewed_by="operator",
            review_basis="Not enough unresolved tension.",
        )


def test_promote_reviewed_tension_to_vow_persists_via_gateway(tmp_path) -> None:
    db, source = _build_db(tmp_path)

    record_id = promote_reviewed_tension_to_vow(
        db,
        source=source,
        payload={
            "summary": "Persistent unresolved governance conflict.",
            "layer": "working",
            "subjectivity_layer": "tension",
            "evidence": ["cycle-1", "cycle-2"],
            "provenance": {"source": "dream_engine"},
            "source_record_ids": ["stim-001"],
        },
        reviewed_by="operator",
        review_basis="Repeated tension across reviewed cycles.",
    )

    factual_records = list(db.query(source, layer="factual"))

    assert record_id
    assert len(factual_records) == 1
    assert factual_records[0].payload["subjectivity_layer"] == "vow"
    assert factual_records[0].payload["promotion_gate"]["review_basis"] == (
        "Repeated tension across reviewed cycles."
    )
