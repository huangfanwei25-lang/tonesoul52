"""Tests for tonesoul.memory.subjectivity_triage pure helper functions."""

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
    _source_url,
    _stimulus_lineage,
)

# ── _normalize_text ───────────────────────────────────────────────────────────


class TestNormalizeText:
    def test_string_stripped(self):
        assert _normalize_text("  hello  ") == "hello"

    def test_none_gives_empty(self):
        assert _normalize_text(None) == ""

    def test_number_converted(self):
        assert _normalize_text(42) == "42"

    def test_empty_string_stays_empty(self):
        assert _normalize_text("") == ""


# ── _normalize_string_list ────────────────────────────────────────────────────


class TestNormalizeStringList:
    def test_list_of_strings(self):
        result = _normalize_string_list(["a", "b", " c "])
        assert result == ["a", "b", "c"]

    def test_filters_empty_strings(self):
        result = _normalize_string_list(["", "  ", "x"])
        assert result == ["x"]

    def test_single_string_becomes_list(self):
        result = _normalize_string_list("hello")
        assert result == ["hello"]

    def test_empty_string_gives_empty_list(self):
        result = _normalize_string_list("")
        assert result == []

    def test_none_gives_empty_list(self):
        result = _normalize_string_list(None)
        assert result == []

    def test_filters_none_items(self):
        result = _normalize_string_list([None, "valid"])
        assert result == ["valid"]


# ── _normalize_topic ──────────────────────────────────────────────────────────


class TestNormalizeTopic:
    def test_uses_topic_key(self):
        result = _normalize_topic({"topic": "governance drift"}, {})
        assert result == "governance drift"

    def test_uses_title_key_fallback(self):
        result = _normalize_topic({"title": "my title"}, {})
        assert result == "my title"

    def test_uses_summary_key_fallback(self):
        result = _normalize_topic({"summary": "session summary"}, {})
        assert result == "session summary"

    def test_strips_dream_collision_prefix(self):
        result = _normalize_topic({"topic": "Dream collision: governance"}, {})
        assert result == "governance"

    def test_strips_dream_collision_examined_format(self):
        text = "Dream collision examined 'boundary check'. Friction=0.4 something"
        result = _normalize_topic({"summary": text}, {})
        assert result == "boundary check"

    def test_fallback_to_row_summary(self):
        result = _normalize_topic({}, {"summary": "row topic"})
        assert result == "row topic"

    def test_no_keys_gives_unknown(self):
        result = _normalize_topic({}, {})
        assert result == "<unknown>"


# ── _extract_friction_score ───────────────────────────────────────────────────


class TestExtractFrictionScore:
    def test_friction_score_key(self):
        assert _extract_friction_score({"friction_score": 0.4}, {}) == pytest.approx(0.4)

    def test_tension_key_fallback(self):
        assert _extract_friction_score({"tension": 0.6}, {}) == pytest.approx(0.6)

    def test_tension_score_key_fallback(self):
        assert _extract_friction_score({"tension_score": 0.3}, {}) == pytest.approx(0.3)

    def test_friction_score_key_takes_priority(self):
        result = _extract_friction_score({"friction_score": 0.2, "tension": 0.9}, {})
        assert result == pytest.approx(0.2)

    def test_summary_marker_extraction(self):
        row = {"summary": "Dream collision examined 'x'. Friction=0.55 something"}
        result = _extract_friction_score({}, row)
        assert result == pytest.approx(0.55)

    def test_invalid_value_gives_zero(self):
        assert _extract_friction_score({"friction_score": "not_a_number"}, {}) == 0.0

    def test_none_gives_zero(self):
        assert _extract_friction_score({}, {}) == 0.0


# ── _friction_band ────────────────────────────────────────────────────────────


class TestFrictionBand:
    def test_zero_is_low(self):
        assert _friction_band(0.0) == "low"

    def test_below_threshold_is_low(self):
        assert _friction_band(0.29) == "low"

    def test_at_low_max_is_low(self):
        # < 0.30 → low, so 0.30 is NOT low (it's medium because ≤ 0.50)
        assert _friction_band(0.30) == "medium"

    def test_medium_range(self):
        assert _friction_band(0.40) == "medium"

    def test_at_medium_max_is_medium(self):
        assert _friction_band(0.50) == "medium"

    def test_above_medium_max_is_high(self):
        assert _friction_band(0.51) == "high"

    def test_one_is_high(self):
        assert _friction_band(1.0) == "high"


# ── _infer_direction ──────────────────────────────────────────────────────────


class TestInferDirection:
    def test_provenance_term_detected(self):
        result = _infer_direction({"topic": "provenance tracking"}, {})
        assert result == "provenance_discipline"

    def test_boundary_term_detected(self):
        result = _infer_direction({"summary": "boundary enforcement"}, {})
        assert result == "boundary_discipline"

    def test_safety_term_detected(self):
        result = _infer_direction({"council_reason": "safety check failed"}, {})
        assert result == "safety_boundary"

    def test_resource_term_detected(self):
        result = _infer_direction({"summary": "compute budget exceeded"}, {})
        assert result == "resource_discipline"

    def test_governance_term_detected(self):
        result = _infer_direction({"topic": "governance threshold breach"}, {})
        assert result == "governance_escalation"

    def test_no_keywords_gives_undifferentiated(self):
        result = _infer_direction({}, {})
        assert result == "undifferentiated_tension"

    def test_row_summary_also_checked(self):
        result = _infer_direction({}, {"summary": "audit trail needed"})
        assert result == "provenance_discipline"


# ── _dream_cycle_id ───────────────────────────────────────────────────────────


class TestDreamCycleId:
    def test_direct_field(self):
        assert _dream_cycle_id({"dream_cycle_id": "dc-1"}) == "dc-1"

    def test_provenance_dict_fallback(self):
        result = _dream_cycle_id({"provenance": {"dream_cycle_id": "dc-2"}})
        assert result == "dc-2"

    def test_no_field_gives_empty(self):
        assert _dream_cycle_id({}) == ""


# ── _source_url ───────────────────────────────────────────────────────────────


class TestSourceUrl:
    def test_direct_field(self):
        assert _source_url({"source_url": "https://example.com"}) == "https://example.com"

    def test_provenance_dict_fallback(self):
        result = _source_url({"provenance": {"source_url": "https://prov.example.com"}})
        assert result == "https://prov.example.com"

    def test_no_field_gives_empty(self):
        assert _source_url({}) == ""


# ── _stimulus_lineage ─────────────────────────────────────────────────────────


class TestStimulusLineage:
    def test_stimulus_record_id_used(self):
        result = _stimulus_lineage({"stimulus_record_id": "rec-1"}, {})
        assert result == "rec-1"

    def test_source_record_ids_joined(self):
        result = _stimulus_lineage({"source_record_ids": ["a", "b"]}, {})
        assert result == "a + b"

    def test_row_source_record_ids_fallback(self):
        result = _stimulus_lineage({}, {"source_record_ids": ["x", "y"]})
        assert result == "x + y"

    def test_row_record_id_last_fallback(self):
        result = _stimulus_lineage({}, {"record_id": "row-r"})
        assert result == "row-r"

    def test_empty_gives_empty(self):
        assert _stimulus_lineage({}, {}) == ""


# ── _semantic_group_key ───────────────────────────────────────────────────────


class TestSemanticGroupKey:
    def test_returns_topic_direction_band(self):
        row = {"topic": "t", "direction": "safety_boundary", "friction_band": "high"}
        key = _semantic_group_key(row)
        assert key == ("t", "safety_boundary", "high")

    def test_missing_keys_use_defaults(self):
        key = _semantic_group_key({})
        assert key[0] == "<unknown>"
        assert key[1] == "undifferentiated_tension"
        assert key[2] == "low"


# ── _lineage_group_key ────────────────────────────────────────────────────────


class TestLineageGroupKey:
    def test_returns_stimulus_and_topic(self):
        row = {"stimulus_lineage": "lin-1", "topic": "topic A"}
        key = _lineage_group_key(row)
        assert key == ("lin-1", "topic A")

    def test_missing_gives_empty_defaults(self):
        key = _lineage_group_key({})
        assert key[0] == ""
        assert key[1] == "<unknown>"


# ── _recommend_semantic_group ─────────────────────────────────────────────────


class TestRecommendSemanticGroup:
    def test_undifferentiated_gives_reject(self):
        rec, _ = _recommend_semantic_group(
            {
                "direction": "undifferentiated_tension",
                "source_url_count": 3,
                "lineage_count": 3,
                "cycle_count": 3,
            }
        )
        assert rec == "reject_review"

    def test_governance_single_source_gives_reject(self):
        rec, _ = _recommend_semantic_group(
            {
                "direction": "governance_escalation",
                "source_url_count": 1,
                "lineage_count": 1,
                "cycle_count": 2,
            }
        )
        assert rec == "reject_review"

    def test_governance_single_url_multi_lineage_gives_defer(self):
        rec, _ = _recommend_semantic_group(
            {
                "direction": "governance_escalation",
                "source_url_count": 1,
                "lineage_count": 3,
                "cycle_count": 2,
            }
        )
        assert rec == "defer_review"

    def test_boundary_multi_source_gives_candidate(self):
        rec, _ = _recommend_semantic_group(
            {
                "direction": "boundary_discipline",
                "source_url_count": 2,
                "lineage_count": 2,
                "cycle_count": 2,
            }
        )
        assert rec == "candidate_for_manual_review"

    def test_safety_multi_source_gives_candidate(self):
        rec, _ = _recommend_semantic_group(
            {
                "direction": "safety_boundary",
                "source_url_count": 3,
                "lineage_count": 3,
                "cycle_count": 3,
            }
        )
        assert rec == "candidate_for_manual_review"


# ── _duplicate_pressure_profile ──────────────────────────────────────────────


class TestDuplicatePressureProfile:
    def test_diverse_sources_low_pressure(self):
        result = _duplicate_pressure_profile(
            {"source_url_count": 3, "record_count": 5, "lineage_count": 5, "cycle_count": 5}
        )
        assert result["duplicate_pressure"] == "low"

    def test_same_source_high_pressure(self):
        result = _duplicate_pressure_profile(
            {"source_url_count": 1, "record_count": 8, "lineage_count": 2, "cycle_count": 5}
        )
        assert result["duplicate_pressure"] == "high"
        assert result["same_source_loop"] is True

    def test_same_source_medium_pressure(self):
        result = _duplicate_pressure_profile(
            {"source_url_count": 1, "record_count": 3, "lineage_count": 2, "cycle_count": 2}
        )
        assert result["duplicate_pressure"] == "medium"

    def test_rows_per_lineage_computed(self):
        result = _duplicate_pressure_profile(
            {"source_url_count": 2, "record_count": 10, "lineage_count": 5, "cycle_count": 2}
        )
        assert result["rows_per_lineage"] == pytest.approx(2.0)


# ── _lineage_density_profile ──────────────────────────────────────────────────


class TestLineageDensityProfile:
    def test_empty_groups(self):
        result = _lineage_density_profile([])
        assert result["max_lineage_record_count"] == 0

    def test_repeated_count(self):
        groups = [
            {"record_count": 3},
            {"record_count": 1},
            {"record_count": 3},
        ]
        result = _lineage_density_profile(groups)
        assert result["repeated_lineage_count"] == 2  # 3 >= 2

    def test_dense_count(self):
        groups = [{"record_count": 3}, {"record_count": 2}]
        result = _lineage_density_profile(groups)
        assert result["dense_lineage_count"] == 1  # only 3 >= 3

    def test_singleton_count(self):
        groups = [{"record_count": 1}, {"record_count": 1}, {"record_count": 4}]
        result = _lineage_density_profile(groups)
        assert result["singleton_lineage_count"] == 2


# ── _lineage_density_snapshot ─────────────────────────────────────────────────


class TestLineageDensitySnapshot:
    def test_empty_gives_empty(self):
        assert _lineage_density_snapshot({}) == ""

    def test_formats_entries_descending(self):
        result = _lineage_density_snapshot({"1": 5, "3": 2})
        assert result.startswith("3r")  # highest count first

    def test_single_entry(self):
        result = _lineage_density_snapshot({"2": 4})
        assert "2r" in result
        assert "x4" in result


# ── _semantic_group_shape ─────────────────────────────────────────────────────


class TestSemanticGroupShape:
    def test_manual_review_candidate(self):
        result = _semantic_group_shape(
            {
                "triage_recommendation": "candidate_for_manual_review",
                "duplicate_pressure": "low",
                "same_source_loop": False,
                "source_url_count": 3,
                "lineage_count": 3,
            }
        )
        assert result == "manual_review_candidate"

    def test_high_duplicate_same_source(self):
        result = _semantic_group_shape(
            {
                "triage_recommendation": "defer_review",
                "duplicate_pressure": "high",
                "same_source_loop": True,
                "source_url_count": 1,
                "lineage_count": 2,
            }
        )
        assert result == "high_duplicate_same_source_loop"

    def test_same_source_monitor(self):
        result = _semantic_group_shape(
            {
                "triage_recommendation": "defer_review",
                "duplicate_pressure": "medium",
                "same_source_loop": True,
                "source_url_count": 1,
                "lineage_count": 2,
            }
        )
        assert result == "same_source_loop_monitor"

    def test_cross_context_group(self):
        result = _semantic_group_shape(
            {
                "triage_recommendation": "defer_review",
                "duplicate_pressure": "low",
                "same_source_loop": False,
                "source_url_count": 2,
                "lineage_count": 2,
            }
        )
        assert result == "cross_context_group"

    def test_unresolved_group_fallback(self):
        result = _semantic_group_shape(
            {
                "triage_recommendation": "defer_review",
                "duplicate_pressure": "low",
                "same_source_loop": False,
                "source_url_count": 1,
                "lineage_count": 1,
            }
        )
        assert result == "unresolved_group"


# ── _handoff_shape ────────────────────────────────────────────────────────────


class TestHandoffShape:
    def test_empty_groups_gives_empty_queue(self):
        result = _handoff_shape(semantic_groups=[], multi_direction_topic_count=0)
        assert result == "empty_queue"

    def test_manual_review_candidate_gives_action_required(self):
        groups = [{"triage_recommendation": "candidate_for_manual_review"}]
        result = _handoff_shape(semantic_groups=groups, multi_direction_topic_count=0)
        assert result == "action_required"

    def test_multi_direction_topic_gives_action_required(self):
        groups = [{"triage_recommendation": "defer_review"}]
        result = _handoff_shape(semantic_groups=groups, multi_direction_topic_count=1)
        assert result == "action_required"

    def test_single_same_source_loop_gives_monitoring(self):
        groups = [{"triage_recommendation": "defer_review", "same_source_loop": True}]
        result = _handoff_shape(semantic_groups=groups, multi_direction_topic_count=0)
        assert result == "monitoring_queue"

    def test_single_no_same_source_gives_single_group(self):
        groups = [{"triage_recommendation": "defer_review", "same_source_loop": False}]
        result = _handoff_shape(semantic_groups=groups, multi_direction_topic_count=0)
        assert result == "single_group"

    def test_multiple_groups_gives_multi_group(self):
        groups = [
            {"triage_recommendation": "defer_review", "same_source_loop": False},
            {"triage_recommendation": "defer_review", "same_source_loop": False},
        ]
        result = _handoff_shape(semantic_groups=groups, multi_direction_topic_count=0)
        assert result == "multi_group"


# ── _build_multi_direction_topics ─────────────────────────────────────────────


class TestBuildMultiDirectionTopics:
    def test_single_direction_per_topic_excluded(self):
        groups = [{"topic": "t1", "direction": "safety_boundary"}]
        result = _build_multi_direction_topics(groups)
        assert result == []

    def test_two_directions_for_same_topic(self):
        groups = [
            {"topic": "t1", "direction": "safety_boundary"},
            {"topic": "t1", "direction": "governance_escalation"},
        ]
        result = _build_multi_direction_topics(groups)
        assert len(result) == 1
        assert result[0]["topic"] == "t1"
        assert result[0]["direction_count"] == 2

    def test_sorted_by_direction_count_desc(self):
        groups = [
            {"topic": "t1", "direction": "a"},
            {"topic": "t1", "direction": "b"},
            {"topic": "t1", "direction": "c"},
            {"topic": "t2", "direction": "x"},
            {"topic": "t2", "direction": "y"},
        ]
        result = _build_multi_direction_topics(groups)
        assert result[0]["direction_count"] >= result[1]["direction_count"]
