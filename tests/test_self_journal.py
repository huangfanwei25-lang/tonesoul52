from __future__ import annotations

import uuid
from pathlib import Path
from types import SimpleNamespace

from tonesoul.council import PreOutputCouncil
from tonesoul.council.self_journal import (
    _compute_intent_match,
    _compute_risk_level,
    _label_for_verdict,
    load_recent_memory,
    record_self_memory,
)


def _journal_path() -> Path:
    base = Path("temp") / "pytest-self-journal"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"journal-{uuid.uuid4().hex}.jsonl"


def test_record_self_memory_writes_entry():
    council = PreOutputCouncil()
    verdict = council.validate("The weather is nice today.", context={})

    journal_path = _journal_path()
    entry = record_self_memory(
        verdict,
        context={"self_identity": "ToneSoul", "language": "en"},
        path=journal_path,
    )

    assert entry["identity"] == "ToneSoul"
    assert entry["verdict"] == verdict.verdict.value
    assert "self_statement" in entry and entry["self_statement"]

    entries = load_recent_memory(limit=1, path=journal_path)
    assert len(entries) == 1
    assert entries[0]["identity"] == "ToneSoul"


def test_load_recent_memory_returns_latest():
    journal_path = _journal_path()
    journal_path.write_text(
        '{"identity": "A", "verdict": "approve"}\n{"identity": "B", "verdict": "block"}\n',
        encoding="utf-8",
    )

    entries = load_recent_memory(limit=1, path=journal_path)
    assert entries[0]["identity"] == "B"


# ─────────────────────────────────────────────
# Extended coverage — pure helper functions
# ─────────────────────────────────────────────


class TestLabelForVerdict:
    def test_approve_english(self):
        assert _label_for_verdict("approve", "en") == "approved"

    def test_approve_chinese(self):
        label = _label_for_verdict("approve", "zh")
        assert label == "通過"

    def test_refine_english(self):
        assert _label_for_verdict("refine", "en") == "needs refinement"

    def test_block_english(self):
        assert _label_for_verdict("block", "en") == "blocked"

    def test_unknown_verdict_returns_value_unchanged(self):
        assert _label_for_verdict("some_unknown_verdict", "en") == "some_unknown_verdict"


class TestComputeRiskLevel:
    def _verdict(self, verdict_name: str = "APPROVE"):
        verdict_ns = SimpleNamespace(name=verdict_name)
        return SimpleNamespace(verdict=verdict_ns)

    def test_contradiction_flag_is_critical(self):
        level = _compute_risk_level(self._verdict(), {"is_contradiction": True})
        assert level == "critical"

    def test_block_verdict_is_high(self):
        level = _compute_risk_level(self._verdict("BLOCK"), {})
        assert level == "high"

    def test_high_tension_is_high(self):
        level = _compute_risk_level(self._verdict(), {"tension": 0.9})
        assert level == "high"

    def test_medium_tension_is_medium(self):
        level = _compute_risk_level(self._verdict(), {"tension": 0.5})
        assert level == "medium"

    def test_low_tension_is_low(self):
        level = _compute_risk_level(self._verdict(), {"tension": 0.1})
        assert level == "low"

    def test_invalid_tension_treated_as_zero(self):
        level = _compute_risk_level(self._verdict(), {"tension": "bad"})
        assert level == "low"

    def test_no_tension_is_low(self):
        level = _compute_risk_level(self._verdict(), {})
        assert level == "low"


class TestComputeIntentMatch:
    def _verdict(self, verdict_name: str = "APPROVE"):
        verdict_ns = SimpleNamespace(name=verdict_name)
        return SimpleNamespace(verdict=verdict_ns)

    def test_no_intent_is_matched(self):
        assert _compute_intent_match({}, self._verdict()) is True

    def test_approve_with_intent_is_matched(self):
        assert _compute_intent_match({"user_intent": "Do X"}, self._verdict("APPROVE")) is True

    def test_block_verdict_with_intent_is_not_matched(self):
        assert _compute_intent_match({"user_intent": "Do X"}, self._verdict("BLOCK")) is False

    def test_declare_stance_with_intent_is_not_matched(self):
        assert (
            _compute_intent_match({"user_intent": "Do X"}, self._verdict("DECLARE_STANCE")) is False
        )


class TestLoadRecentMemoryEdgeCases:
    def test_zero_limit_returns_empty(self, tmp_path):
        path = tmp_path / "journal.jsonl"
        path.write_text('{"identity": "X"}\n', encoding="utf-8")
        assert load_recent_memory(limit=0, path=path) == []

    def test_negative_limit_returns_empty(self, tmp_path):
        path = tmp_path / "journal.jsonl"
        path.write_text('{"identity": "X"}\n', encoding="utf-8")
        assert load_recent_memory(limit=-1, path=path) == []
