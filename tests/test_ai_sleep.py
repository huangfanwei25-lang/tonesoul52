"""Test AI Sleep memory consolidation."""

from __future__ import annotations

from tonesoul.memory.consolidator import SleepResult, _classify_for_promotion, sleep_consolidate
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


def test_sleep_consolidate_promotes_commitment(tmp_path):
    db, source = _build_db(tmp_path)
    db.append(
        source,
        {
            "text": "I promise to listen more",
            "layer": "working",
        },
    )

    result = sleep_consolidate(db, source=source)
    factual_records = list(db.query(source, layer="factual"))
    working_records = list(db.query(source, layer="working"))

    assert result.promoted_count == 1
    assert len(factual_records) == 1
    assert len(working_records) == 1


def test_sleep_result_has_layer_summary(tmp_path):
    db, source = _build_db(tmp_path)
    db.append(source, {"text": "test", "layer": "experiential"})
    result = sleep_consolidate(db, source=source)
    assert "experiential" in result.layer_summary
    assert isinstance(result.layer_summary["experiential"], int)
