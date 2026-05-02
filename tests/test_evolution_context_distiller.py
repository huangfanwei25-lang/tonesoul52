"""Tests for tonesoul.evolution.context_distiller — pure helpers and ContextDistiller."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tonesoul.evolution.context_distiller import (
    ContextDistiller,
    ContextPattern,
    DistillationResult,
    _normalize_string_list,
    _parse_timestamp,
    _to_float,
    _tone_score,
    _unique_preserve_order,
    _utc_now,
)

# ── _utc_now ──────────────────────────────────────────────────────────────────


class TestUtcNow:
    def test_returns_string(self):
        assert isinstance(_utc_now(), str)

    def test_ends_with_z(self):
        assert _utc_now().endswith("Z")


# ── _to_float ─────────────────────────────────────────────────────────────────


class TestToFloat:
    def test_integer_converted(self):
        assert _to_float(3) == pytest.approx(3.0)

    def test_float_passthrough(self):
        assert _to_float(0.5) == pytest.approx(0.5)

    def test_string_float_converted(self):
        assert _to_float("1.5") == pytest.approx(1.5)

    def test_none_returns_none(self):
        assert _to_float(None) is None

    def test_invalid_string_returns_none(self):
        assert _to_float("not-a-number") is None


# ── _parse_timestamp ──────────────────────────────────────────────────────────


class TestParseTimestamp:
    def test_z_suffix_parsed(self):
        result = _parse_timestamp("2026-01-01T00:00:00Z")
        assert isinstance(result, datetime)
        assert result.tzinfo is not None

    def test_none_returns_none(self):
        assert _parse_timestamp(None) is None

    def test_empty_string_returns_none(self):
        assert _parse_timestamp("") is None

    def test_invalid_returns_none(self):
        assert _parse_timestamp("not-a-date") is None

    def test_naive_gets_utc(self):
        result = _parse_timestamp("2026-01-01T00:00:00")
        assert result.tzinfo == timezone.utc

    def test_utc_normalized(self):
        result = _parse_timestamp("2026-06-01T12:00:00+05:00")
        assert result.tzinfo is not None


# ── _normalize_string_list ────────────────────────────────────────────────────


class TestNormalizeStringList:
    def test_list_of_strings(self):
        assert _normalize_string_list(["a", "b"]) == ["a", "b"]

    def test_filters_empty(self):
        assert _normalize_string_list(["", "  ", "c"]) == ["c"]

    def test_single_string_wrapped(self):
        assert _normalize_string_list("hello") == ["hello"]

    def test_other_types_empty(self):
        assert _normalize_string_list(None) == []
        assert _normalize_string_list(42) == []


# ── _unique_preserve_order ────────────────────────────────────────────────────


class TestUniquePreserveOrder:
    def test_deduplicates(self):
        assert _unique_preserve_order(["a", "b", "a"]) == ["a", "b"]

    def test_preserves_order(self):
        assert _unique_preserve_order(["c", "a", "b"]) == ["c", "a", "b"]

    def test_filters_empty(self):
        assert _unique_preserve_order(["", "  ", "x"]) == ["x"]

    def test_empty_list(self):
        assert _unique_preserve_order([]) == []


# ── _tone_score ───────────────────────────────────────────────────────────────


class TestToneScore:
    def test_positive_tokens_increase_score(self):
        score = _tone_score("Thank you this is great and helpful")
        assert score > 0

    def test_negative_tokens_decrease_score(self):
        score = _tone_score("I am frustrated and angry at this broken error")
        assert score < 0

    def test_neutral_text_zero(self):
        score = _tone_score("the quick brown fox jumps over the lazy dog")
        assert score == pytest.approx(0.0)

    def test_empty_text(self):
        assert _tone_score("") == pytest.approx(0.0)


# ── ContextPattern.to_dict ────────────────────────────────────────────────────


class TestContextPattern:
    def test_to_dict_keys(self):
        pattern = ContextPattern(
            pattern_type="decision",
            description="desc",
            evidence=["e1"],
            confidence=0.8,
            extracted_at="2026-01-01Z",
        )
        d = pattern.to_dict()
        for k in (
            "pattern_type",
            "description",
            "evidence",
            "confidence",
            "extracted_at",
            "metadata",
        ):
            assert k in d

    def test_confidence_as_float(self):
        pattern = ContextPattern("t", "d", [], 0.75, "ts")
        assert isinstance(pattern.to_dict()["confidence"], float)


# ── DistillationResult.to_dict ────────────────────────────────────────────────


class TestDistillationResult:
    def test_to_dict_keys(self):
        result = DistillationResult(
            patterns=[],
            conversations_analyzed=5,
            time_range=(None, None),
            summary="test",
        )
        d = result.to_dict()
        for k in ("patterns", "conversations_analyzed", "time_range", "summary", "distilled_at"):
            assert k in d

    def test_patterns_serialized(self):
        pattern = ContextPattern("decision", "d", [], 0.5, "ts")
        result = DistillationResult([pattern], 1, (None, None), "s")
        d = result.to_dict()
        assert len(d["patterns"]) == 1


# ── ContextDistiller helpers ──────────────────────────────────────────────────


class _FakePersistence:
    """Stub persistence that returns no data."""

    def list_conversations(self, limit, offset):
        return {"conversations": []}

    def get_conversation(self, id):
        return {}

    def list_audit_logs(self, limit, offset):
        return {"logs": []}


class TestContextDistillerInit:
    def test_no_cache_no_latest(self, tmp_path):
        distiller = ContextDistiller(_FakePersistence(), cache_path=tmp_path / "missing.json")
        assert distiller.get_latest_result() is None

    def test_corrupt_cache_ignored(self, tmp_path):
        cache = tmp_path / "cache.json"
        cache.write_text("not valid json")
        distiller = ContextDistiller(_FakePersistence(), cache_path=cache)
        assert distiller.get_latest_result() is None


class TestContextDistillerBuildSummary:
    def setup_method(self):
        self.distiller = ContextDistiller(_FakePersistence())

    def test_empty_patterns_summary(self):
        summary = self.distiller._build_summary([], 3)
        assert "No stable" in summary

    def test_summary_with_patterns(self):
        p = ContextPattern("decision", "d", [], 0.8, "ts")
        summary = self.distiller._build_summary([p], 5)
        assert "5" in summary
        assert "decision" in summary


class TestContextDistillerConversationRepairSignal:
    def setup_method(self):
        self.distiller = ContextDistiller(_FakePersistence())

    def _msgs(self, contents):
        return [{"role": "user", "content": c} for c in contents]

    def test_no_negative_no_repair(self):
        msgs = self._msgs(["thank you", "great help"])
        assert self.distiller._conversation_has_repair_signal(msgs) is False

    def test_negative_then_positive_repair(self):
        msgs = self._msgs(["I am frustrated and angry", "Thank you that is helpful"])
        assert self.distiller._conversation_has_repair_signal(msgs) is True

    def test_negative_without_recovery(self):
        msgs = self._msgs(["I am frustrated and angry at broken error", "still bad"])
        assert self.distiller._conversation_has_repair_signal(msgs) is False

    def test_empty_no_repair(self):
        assert self.distiller._conversation_has_repair_signal([]) is False


class TestExtractDecisionPatterns:
    def setup_method(self):
        self.distiller = ContextDistiller(_FakePersistence())

    def test_empty_logs_returns_empty(self):
        assert self.distiller.extract_decision_patterns([]) == []

    def test_single_decision_type_pattern(self):
        logs = [
            {"gate_decision": "approve", "conversation_id": "c1"},
            {"gate_decision": "approve", "conversation_id": "c2"},
        ]
        patterns = self.distiller.extract_decision_patterns(logs)
        assert any(p.pattern_type == "decision" for p in patterns)

    def test_high_tension_pattern_added(self):
        logs = [
            {"gate_decision": "block", "conversation_id": "c1", "delta_t": None},
        ]
        patterns = self.distiller.extract_decision_patterns(logs)
        high_tension = [p for p in patterns if "High-tension" in p.description]
        assert len(high_tension) >= 1

    def test_confidence_in_range(self):
        logs = [{"gate_decision": "approve", "conversation_id": "c1"}]
        patterns = self.distiller.extract_decision_patterns(logs)
        for p in patterns:
            assert 0.0 <= p.confidence <= 1.0


class TestExtractValueAccumulation:
    def setup_method(self):
        self.distiller = ContextDistiller(_FakePersistence())

    def test_no_conversations_empty(self):
        assert self.distiller.extract_value_accumulation([]) == []

    def test_commit_pattern_from_deliberation(self):
        conversations = [
            {
                "id": "c1",
                "messages": [
                    {
                        "role": "assistant",
                        "deliberation": {
                            "self_commits": ["I commit to honesty"],
                            "ruptures": [],
                            "emergent_values": ["honesty"],
                        },
                    }
                ],
            }
        ]
        patterns = self.distiller.extract_value_accumulation(conversations)
        assert any(p.pattern_type == "value" for p in patterns)


class TestExtractToneEvolution:
    def setup_method(self):
        self.distiller = ContextDistiller(_FakePersistence())

    def test_no_conversations_empty(self):
        assert self.distiller.extract_tone_evolution([]) == []

    def test_positive_shift_detected(self):
        conversations = [
            {
                "id": "c1",
                "messages": [
                    {"role": "user", "content": "I am frustrated and angry at this broken error"},
                    {"role": "user", "content": "Thank you this is great and helpful"},
                ],
            }
        ]
        patterns = self.distiller.extract_tone_evolution(conversations)
        descriptions = [p.description for p in patterns]
        assert any("improves" in d for d in descriptions)

    def test_negative_shift_detected(self):
        conversations = [
            {
                "id": "c1",
                "messages": [
                    {"role": "user", "content": "Thank you this is great and helpful"},
                    {"role": "user", "content": "I am frustrated and angry at this broken"},
                ],
            }
        ]
        patterns = self.distiller.extract_tone_evolution(conversations)
        descriptions = [p.description for p in patterns]
        assert any("frustration" in d for d in descriptions)


class TestExtractConflictResolutions:
    def setup_method(self):
        self.distiller = ContextDistiller(_FakePersistence())

    def test_no_conversations_empty(self):
        assert self.distiller.extract_conflict_resolutions([]) == []

    def test_resolved_conflict(self):
        conversations = [
            {
                "id": "c1",
                "messages": [
                    {"role": "user", "content": "I am frustrated and angry at this broken"},
                    {"role": "user", "content": "Thank you that is clear and helpful"},
                ],
            }
        ]
        patterns = self.distiller.extract_conflict_resolutions(conversations)
        descs = [p.description for p in patterns]
        assert any("recover" in d.lower() for d in descs)


class TestGetSummary:
    def test_no_result_defaults(self, tmp_path):
        distiller = ContextDistiller(_FakePersistence(), cache_path=tmp_path / "x.json")
        s = distiller.get_summary()
        assert s["total_patterns"] == 0
        assert "No distillation" in s["summary"]

    def test_after_distill_has_data(self, tmp_path):
        distiller = ContextDistiller(_FakePersistence(), cache_path=tmp_path / "cache.json")
        distiller.distill(limit=10)
        s = distiller.get_summary()
        assert "conversations_analyzed" in s
