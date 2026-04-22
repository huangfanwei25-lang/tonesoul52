"""Tests for tonesoul.memory.subjectivity_triage — pure helpers (no SoulDB)."""
from __future__ import annotations

import pytest

from tonesoul.memory.subjectivity_triage import (
    _build_multi_direction_topics,
    _dream_cycle_id,
    _duplicate_pressure_profile,
    _extract_friction_score,
    _friction_band,
    _handoff_shape,
    _infer_direction,
    _lineage_density_profile,
    _lineage_density_snapshot,
    _lineage_group_key,
    _normalize_string_list,
    _normalize_text,
    _normalize_topic,
    _recommend_semantic_group,
    _semantic_group_key,
    _semantic_group_shape,
    _semantic_group_status_line,
    _source_url,
    _stimulus_lineage,
)


# ── _normalize_text ───────────────────────────────────────────────────────────

class TestNormalizeText:
    def test_strips_whitespace(self):
        assert _normalize_text("  hello  ") == "hello"

    def test_none_returns_empty(self):
        assert _normalize_text(None) == ""

    def test_converts_non_string(self):
        assert _normalize_text(42) == "42"

    def test_empty_string(self):
        assert _normalize_text("") == ""


# ── _normalize_string_list ────────────────────────────────────────────────────

class TestNormalizeStringList:
    def test_list_of_strings(self):
        result = _normalize_string_list(["a", "b"])
        assert result == ["a", "b"]

    def test_filters_empty(self):
        result = _normalize_string_list(["", "  ", "x"])
        assert result == ["x"]

    def test_single_string_wrapped(self):
        result = _normalize_string_list("hello")
        assert result == ["hello"]

    def test_none_returns_empty(self):
        assert _normalize_string_list(None) == []


# ── _normalize_topic ──────────────────────────────────────────────────────────

class TestNormalizeTopic:
    def test_uses_topic_key(self):
        result = _normalize_topic({"topic": "ethics"}, {})
        assert result == "ethics"

    def test_strips_dream_collision_prefix(self):
        result = _normalize_topic({"topic": "Dream collision: ethics"}, {})
        assert result == "ethics"

    def test_extracts_from_examined_format(self):
        payload = {"topic": "Dream collision examined 'safety'. Friction=0.8 other"}
        result = _normalize_topic(payload, {})
        assert result == "safety"

    def test_falls_back_to_title(self):
        result = _normalize_topic({"title": "governance"}, {})
        assert result == "governance"

    def test_falls_back_to_summary_key(self):
        result = _normalize_topic({"summary": "about resource use"}, {})
        assert result == "about resource use"

    def test_falls_back_to_row_summary(self):
        result = _normalize_topic({}, {"summary": "row summary"})
        assert result == "row summary"

    def test_unknown_when_all_empty(self):
        result = _normalize_topic({}, {})
        assert result == "<unknown>"


# ── _extract_friction_score ───────────────────────────────────────────────────

class TestExtractFrictionScore:
    def test_from_friction_score_key(self):
        assert _extract_friction_score({"friction_score": 0.7}, {}) == pytest.approx(0.7)

    def test_from_tension_key(self):
        assert _extract_friction_score({"tension": 0.5}, {}) == pytest.approx(0.5)

    def test_from_tension_score_key(self):
        assert _extract_friction_score({"tension_score": 0.3}, {}) == pytest.approx(0.3)

    def test_from_row_summary_marker(self):
        row = {"summary": "Dream collision. Friction=0.65 detected"}
        assert _extract_friction_score({}, row) == pytest.approx(0.65)

    def test_missing_returns_zero(self):
        assert _extract_friction_score({}, {}) == pytest.approx(0.0)


# ── _friction_band ────────────────────────────────────────────────────────────

class TestFrictionBand:
    def test_low_below_0_3(self):
        assert _friction_band(0.1) == "low"

    def test_low_just_below_0_3(self):
        assert _friction_band(0.29) == "low"

    def test_medium_at_0_3(self):
        assert _friction_band(0.30) == "medium"

    def test_medium_at_0_5(self):
        assert _friction_band(0.50) == "medium"

    def test_high_above_0_5(self):
        assert _friction_band(0.51) == "high"

    def test_high_at_1(self):
        assert _friction_band(1.0) == "high"


# ── _infer_direction ──────────────────────────────────────────────────────────

class TestInferDirection:
    def test_provenance_discipline(self):
        direction = _infer_direction({"summary": "traceable audit"}, {})
        assert direction == "provenance_discipline"

    def test_boundary_discipline(self):
        direction = _infer_direction({"summary": "guardrail constraint"}, {})
        assert direction == "boundary_discipline"

    def test_safety_boundary(self):
        direction = _infer_direction({"summary": "safety risk fail-closed"}, {})
        assert direction == "safety_boundary"

    def test_resource_discipline(self):
        direction = _infer_direction({"summary": "compute budget cost"}, {})
        assert direction == "resource_discipline"

    def test_governance_escalation(self):
        direction = _infer_direction({"summary": "governance council threshold"}, {})
        assert direction == "governance_escalation"

    def test_undifferentiated_default(self):
        direction = _infer_direction({"summary": "something random"}, {})
        assert direction == "undifferentiated_tension"


# ── _dream_cycle_id ───────────────────────────────────────────────────────────

class TestDreamCycleId:
    def test_direct_field(self):
        assert _dream_cycle_id({"dream_cycle_id": "d123"}) == "d123"

    def test_from_provenance(self):
        payload = {"provenance": {"dream_cycle_id": "d456"}}
        assert _dream_cycle_id(payload) == "d456"

    def test_missing_returns_empty(self):
        assert _dream_cycle_id({}) == ""


# ── _source_url ───────────────────────────────────────────────────────────────

class TestSourceUrl:
    def test_direct_field(self):
        assert _source_url({"source_url": "https://x.com"}) == "https://x.com"

    def test_from_provenance(self):
        payload = {"provenance": {"source_url": "https://y.com"}}
        assert _source_url(payload) == "https://y.com"

    def test_missing_returns_empty(self):
        assert _source_url({}) == ""


# ── _stimulus_lineage ──────────────────────────────────────────────────────────

class TestStimulusLineage:
    def test_stimulus_record_id_direct(self):
        assert _stimulus_lineage({"stimulus_record_id": "s1"}, {}) == "s1"

    def test_source_record_ids_joined(self):
        result = _stimulus_lineage({"source_record_ids": ["a", "b"]}, {})
        assert "a" in result and "b" in result

    def test_row_source_record_ids(self):
        result = _stimulus_lineage({}, {"source_record_ids": ["c", "d"]})
        assert "c" in result

    def test_row_record_id_fallback(self):
        result = _stimulus_lineage({}, {"record_id": "r1"})
        assert result == "r1"

    def test_empty_all_returns_empty(self):
        result = _stimulus_lineage({}, {})
        assert result == ""


# ── _semantic_group_key ───────────────────────────────────────────────────────

class TestSemanticGroupKey:
    def test_returns_tuple(self):
        row = {"topic": "t", "direction": "d", "friction_band": "low"}
        key = _semantic_group_key(row)
        assert isinstance(key, tuple)
        assert len(key) == 3

    def test_values_in_key(self):
        row = {"topic": "safety", "direction": "safety_boundary", "friction_band": "high"}
        key = _semantic_group_key(row)
        assert key == ("safety", "safety_boundary", "high")


# ── _lineage_group_key ─────────────────────────────────────────────────────────

class TestLineageGroupKey:
    def test_returns_tuple_of_two(self):
        row = {"stimulus_lineage": "s1", "topic": "t1"}
        key = _lineage_group_key(row)
        assert len(key) == 2
        assert key == ("s1", "t1")


# ── _recommend_semantic_group ─────────────────────────────────────────────────

class TestRecommendSemanticGroup:
    def _call(self, direction, source_url_count=0, lineage_count=0, cycle_count=0):
        return _recommend_semantic_group({
            "direction": direction,
            "source_url_count": source_url_count,
            "lineage_count": lineage_count,
            "cycle_count": cycle_count,
        })

    def test_undifferentiated_reject(self):
        rec, _ = self._call("undifferentiated_tension")
        assert rec == "reject_review"

    def test_governance_same_source_single_lineage_reject(self):
        rec, _ = self._call("governance_escalation", source_url_count=1, lineage_count=1)
        assert rec == "reject_review"

    def test_governance_same_source_multi_lineage_defer(self):
        rec, _ = self._call("governance_escalation", source_url_count=1, lineage_count=3)
        assert rec == "defer_review"

    def test_boundary_with_diversity_candidate(self):
        rec, _ = self._call("boundary_discipline",
                             source_url_count=2, lineage_count=2, cycle_count=2)
        assert rec == "candidate_for_manual_review"

    def test_boundary_insufficient_diversity_defer(self):
        rec, _ = self._call("boundary_discipline",
                             source_url_count=1, lineage_count=1, cycle_count=1)
        assert rec == "defer_review"


# ── _duplicate_pressure_profile ───────────────────────────────────────────────

class TestDuplicatePressureProfile:
    def _call(self, source_url_count=2, record_count=2, lineage_count=2, cycle_count=2):
        return _duplicate_pressure_profile({
            "source_url_count": source_url_count,
            "record_count": record_count,
            "lineage_count": lineage_count,
            "cycle_count": cycle_count,
        })

    def test_multi_source_low_pressure(self):
        result = self._call(source_url_count=3, record_count=4, lineage_count=3, cycle_count=3)
        assert result["duplicate_pressure"] == "low"

    def test_single_source_many_records_high_pressure(self):
        result = self._call(source_url_count=1, record_count=10, lineage_count=2, cycle_count=5)
        assert result["duplicate_pressure"] in ("high", "medium")

    def test_same_source_loop_flag(self):
        result = self._call(source_url_count=1)
        assert result["same_source_loop"] is True

    def test_multi_source_no_loop(self):
        result = self._call(source_url_count=3)
        assert result["same_source_loop"] is False

    def test_keys_present(self):
        result = self._call()
        for k in ("same_source_loop", "rows_per_lineage", "rows_per_cycle",
                  "duplicate_pressure", "duplicate_pressure_reason", "producer_followup"):
            assert k in result


# ── _lineage_density_profile ──────────────────────────────────────────────────

class TestLineageDensityProfile:
    def test_empty_groups(self):
        result = _lineage_density_profile([])
        assert result["max_lineage_record_count"] == 0

    def test_counts_repeated_lineages(self):
        groups = [
            {"record_count": 2},
            {"record_count": 3},
            {"record_count": 1},
        ]
        result = _lineage_density_profile(groups)
        assert result["repeated_lineage_count"] == 2
        assert result["dense_lineage_count"] == 1
        assert result["singleton_lineage_count"] == 1

    def test_histogram_keys_are_strings(self):
        groups = [{"record_count": 2}, {"record_count": 2}]
        result = _lineage_density_profile(groups)
        assert "2" in result["lineage_record_histogram"]


# ── _lineage_density_snapshot ─────────────────────────────────────────────────

class TestLineageDensitySnapshot:
    def test_empty_returns_empty(self):
        assert _lineage_density_snapshot({}) == ""

    def test_single_entry(self):
        result = _lineage_density_snapshot({"3": 2})
        assert "3r" in result
        assert "x2" in result

    def test_sorted_descending(self):
        result = _lineage_density_snapshot({"1": 3, "4": 1})
        assert result.index("4r") < result.index("1r")


# ── _semantic_group_shape ─────────────────────────────────────────────────────

class TestSemanticGroupShape:
    def test_candidate_for_manual_review(self):
        shape = _semantic_group_shape({"triage_recommendation": "candidate_for_manual_review"})
        assert shape == "manual_review_candidate"

    def test_high_duplicate_same_source(self):
        shape = _semantic_group_shape({
            "triage_recommendation": "defer_review",
            "same_source_loop": True,
            "duplicate_pressure": "high",
        })
        assert shape == "high_duplicate_same_source_loop"

    def test_same_source_monitor(self):
        shape = _semantic_group_shape({
            "same_source_loop": True,
            "duplicate_pressure": "low",
        })
        assert shape == "same_source_loop_monitor"

    def test_cross_context(self):
        shape = _semantic_group_shape({
            "source_url_count": 3,
            "lineage_count": 3,
        })
        assert shape == "cross_context_group"

    def test_unresolved_default(self):
        shape = _semantic_group_shape({})
        assert shape == "unresolved_group"


# ── _semantic_group_status_line ───────────────────────────────────────────────

class TestSemanticGroupStatusLine:
    def test_basic_status_line(self):
        group = {
            "group_shape": "unresolved_group",
            "topic": "safety",
            "triage_recommendation": "defer_review",
            "record_count": 3,
            "lineage_count": 2,
            "cycle_count": 1,
        }
        line = _semantic_group_status_line(group)
        assert "safety" in line
        assert "defer_review" in line

    def test_includes_density_when_present(self):
        group = {
            "group_shape": "unresolved_group",
            "topic": "test",
            "triage_recommendation": "defer_review",
            "record_count": 1,
            "lineage_count": 1,
            "cycle_count": 1,
            "lineage_record_histogram": {"2": 3},
        }
        line = _semantic_group_status_line(group)
        assert "density" in line


# ── _handoff_shape ────────────────────────────────────────────────────────────

class TestHandoffShape:
    def test_empty_queue(self):
        assert _handoff_shape(semantic_groups=[], multi_direction_topic_count=0) == "empty_queue"

    def test_action_required_when_candidate(self):
        groups = [{"triage_recommendation": "candidate_for_manual_review"}]
        assert _handoff_shape(semantic_groups=groups, multi_direction_topic_count=0) == "action_required"

    def test_action_required_when_multi_direction(self):
        groups = [{"triage_recommendation": "defer_review"}]
        assert _handoff_shape(semantic_groups=groups, multi_direction_topic_count=1) == "action_required"

    def test_monitoring_queue_single_same_source(self):
        groups = [{"triage_recommendation": "defer_review", "same_source_loop": True}]
        assert _handoff_shape(semantic_groups=groups, multi_direction_topic_count=0) == "monitoring_queue"

    def test_single_group(self):
        groups = [{"triage_recommendation": "defer_review", "same_source_loop": False}]
        assert _handoff_shape(semantic_groups=groups, multi_direction_topic_count=0) == "single_group"

    def test_multi_group(self):
        groups = [
            {"triage_recommendation": "defer_review"},
            {"triage_recommendation": "defer_review"},
        ]
        assert _handoff_shape(semantic_groups=groups, multi_direction_topic_count=0) == "multi_group"


# ── _build_multi_direction_topics ─────────────────────────────────────────────

class TestBuildMultiDirectionTopics:
    def test_single_direction_topic_not_included(self):
        groups = [
            {"topic": "safety", "direction": "safety_boundary"},
            {"topic": "safety", "direction": "safety_boundary"},
        ]
        result = _build_multi_direction_topics(groups)
        assert all(item["topic"] != "safety" for item in result)

    def test_multi_direction_topic_included(self):
        groups = [
            {"topic": "safety", "direction": "safety_boundary"},
            {"topic": "safety", "direction": "governance_escalation"},
        ]
        result = _build_multi_direction_topics(groups)
        assert len(result) == 1
        assert result[0]["direction_count"] == 2

    def test_sorted_by_direction_count(self):
        groups = [
            {"topic": "a", "direction": "d1"},
            {"topic": "a", "direction": "d2"},
            {"topic": "a", "direction": "d3"},
            {"topic": "b", "direction": "d1"},
            {"topic": "b", "direction": "d2"},
        ]
        result = _build_multi_direction_topics(groups)
        assert result[0]["topic"] == "a"  # 3 directions vs 2
