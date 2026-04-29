"""Tests for pure helper functions in tonesoul/memory/subjectivity_reporting.py"""

from __future__ import annotations

from datetime import datetime, timezone

from tonesoul.memory.subjectivity_reporting import (
    _extract_promotion_status,
    _is_unresolved_tension,
    _normalize_memory_layer,
    _normalize_subjectivity_layer,
    _normalize_text,
    _parse_timestamp,
    _record_excerpt,
)

# ---------------------------------------------------------------------------
# TestNormalizeText
# ---------------------------------------------------------------------------


class TestNormalizeText:
    def test_strips_leading_trailing_whitespace(self):
        assert _normalize_text("  hello  ") == "hello"

    def test_none_returns_empty_string(self):
        assert _normalize_text(None) == ""

    def test_non_string_coerced(self):
        assert _normalize_text(42) == "42"

    def test_already_clean_string_unchanged(self):
        assert _normalize_text("clean") == "clean"

    def test_empty_string_unchanged(self):
        assert _normalize_text("") == ""

    def test_only_whitespace_returns_empty(self):
        assert _normalize_text("   ") == ""

    def test_list_coerced(self):
        result = _normalize_text([1, 2])
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# TestNormalizeSubjectivityLayer
# ---------------------------------------------------------------------------


class TestNormalizeSubjectivityLayer:
    def test_tension(self):
        assert _normalize_subjectivity_layer("tension") == "tension"

    def test_vow(self):
        assert _normalize_subjectivity_layer("vow") == "vow"

    def test_event(self):
        assert _normalize_subjectivity_layer("event") == "event"

    def test_meaning(self):
        assert _normalize_subjectivity_layer("meaning") == "meaning"

    def test_identity(self):
        assert _normalize_subjectivity_layer("identity") == "identity"

    def test_unknown_returns_unclassified(self):
        assert _normalize_subjectivity_layer("bogus_layer") == "unclassified"

    def test_none_returns_unclassified(self):
        assert _normalize_subjectivity_layer(None) == "unclassified"

    def test_uppercase_normalized_to_lower(self):
        # The function lowercases before checking, so "TENSION" → "tension" → valid
        assert _normalize_subjectivity_layer("TENSION") == "tension"

    def test_empty_string_returns_unclassified(self):
        assert _normalize_subjectivity_layer("") == "unclassified"


# ---------------------------------------------------------------------------
# TestNormalizeMemoryLayer
# ---------------------------------------------------------------------------


class TestNormalizeMemoryLayer:
    def test_working_layer(self):
        assert _normalize_memory_layer("working") == "working"

    def test_none_returns_experiential(self):
        assert _normalize_memory_layer(None) == "experiential"

    def test_empty_string_returns_experiential(self):
        assert _normalize_memory_layer("") == "experiential"

    def test_whitespace_only_returns_experiential(self):
        assert _normalize_memory_layer("   ") == "experiential"

    def test_factual_layer(self):
        assert _normalize_memory_layer("factual") == "factual"

    def test_uppercase_lowercased(self):
        assert _normalize_memory_layer("WORKING") == "working"


# ---------------------------------------------------------------------------
# TestExtractPromotionStatus
# ---------------------------------------------------------------------------


class TestExtractPromotionStatus:
    def test_string_gate_reviewed(self):
        assert _extract_promotion_status({"promotion_gate": "reviewed"}) == "reviewed"

    def test_dict_gate_with_status_approved(self):
        assert _extract_promotion_status({"promotion_gate": {"status": "approved"}}) == "approved"

    def test_dict_gate_with_decision_reviewed(self):
        assert _extract_promotion_status({"promotion_gate": {"decision": "reviewed"}}) == "reviewed"

    def test_no_gate_returns_none(self):
        assert _extract_promotion_status({}) == "none"

    def test_none_gate_returns_none(self):
        assert _extract_promotion_status({"promotion_gate": None}) == "none"

    def test_dict_gate_no_recognized_key_returns_none(self):
        assert _extract_promotion_status({"promotion_gate": {"unknown_key": "value"}}) == "none"

    def test_dict_gate_status_takes_priority(self):
        result = _extract_promotion_status(
            {"promotion_gate": {"status": "candidate", "decision": "approved"}}
        )
        assert result == "candidate"

    def test_string_gate_stripped_and_lowercased(self):
        assert _extract_promotion_status({"promotion_gate": "  REVIEWED  "}) == "reviewed"

    def test_empty_string_gate_returns_none(self):
        assert _extract_promotion_status({"promotion_gate": ""}) == "none"


# ---------------------------------------------------------------------------
# TestParseTimestamp
# ---------------------------------------------------------------------------


class TestParseTimestamp:
    def test_valid_iso_with_z_returns_utc(self):
        result = _parse_timestamp("2026-03-10T01:00:00Z")
        assert result.tzinfo is not None
        assert result == datetime(2026, 3, 10, 1, 0, 0, tzinfo=timezone.utc)

    def test_invalid_text_returns_datetime_min(self):
        result = _parse_timestamp("not-a-date")
        assert result == datetime.min.replace(tzinfo=timezone.utc)

    def test_empty_string_returns_datetime_min(self):
        result = _parse_timestamp("")
        assert result == datetime.min.replace(tzinfo=timezone.utc)

    def test_none_returns_datetime_min(self):
        result = _parse_timestamp(None)
        assert result == datetime.min.replace(tzinfo=timezone.utc)

    def test_naive_iso_string_gets_utc(self):
        result = _parse_timestamp("2026-01-15T12:30:00")
        assert result.tzinfo is not None
        assert result.tzinfo == timezone.utc

    def test_result_always_has_timezone(self):
        result = _parse_timestamp("2026-05-01T00:00:00")
        assert result.tzinfo is not None


# ---------------------------------------------------------------------------
# TestRecordExcerpt
# ---------------------------------------------------------------------------


class TestRecordExcerpt:
    def test_prefers_summary(self):
        payload = {"summary": "The summary text.", "title": "The title"}
        assert _record_excerpt(payload) == "The summary text."

    def test_falls_back_to_title(self):
        payload = {"title": "The title only"}
        assert _record_excerpt(payload) == "The title only"

    def test_empty_dict_returns_empty_string(self):
        assert _record_excerpt({}) == ""

    def test_truncates_to_160_chars(self):
        long_text = "x" * 200
        result = _record_excerpt({"summary": long_text})
        assert len(result) == 160

    def test_short_text_not_truncated(self):
        text = "Short text."
        assert _record_excerpt({"summary": text}) == text

    def test_falls_back_to_text_key(self):
        payload = {"text": "Some raw text content."}
        assert _record_excerpt(payload) == "Some raw text content."

    def test_summary_takes_priority_over_text(self):
        payload = {"summary": "summary value", "text": "text value"}
        assert _record_excerpt(payload) == "summary value"


# ---------------------------------------------------------------------------
# TestIsUnresolvedTension
# ---------------------------------------------------------------------------


class TestIsUnresolvedTension:
    def test_non_tension_payload_returns_false(self):
        payload = {"subjectivity_layer": "vow"}
        assert _is_unresolved_tension(payload) is False

    def test_tension_without_promotion_returns_true(self):
        payload = {"subjectivity_layer": "tension"}
        assert _is_unresolved_tension(payload) is True

    def test_tension_with_reviewed_promotion_returns_false(self):
        payload = {
            "subjectivity_layer": "tension",
            "promotion_gate": {"status": "reviewed"},
        }
        assert _is_unresolved_tension(payload) is False

    def test_tension_with_approved_promotion_returns_false(self):
        payload = {
            "subjectivity_layer": "tension",
            "promotion_gate": {"status": "approved"},
        }
        assert _is_unresolved_tension(payload) is False

    def test_tension_with_candidate_promotion_returns_true(self):
        payload = {
            "subjectivity_layer": "tension",
            "promotion_gate": {"status": "candidate"},
        }
        assert _is_unresolved_tension(payload) is True

    def test_tension_with_settled_review_status_returns_false(self):
        payload = {"subjectivity_layer": "tension"}
        review_status = {
            "rec-1": {"settled": True},
        }
        assert (
            _is_unresolved_tension(
                payload, record_id="rec-1", review_status_by_record_id=review_status
            )
            is False
        )

    def test_tension_with_unsettled_review_status_returns_true(self):
        payload = {"subjectivity_layer": "tension"}
        review_status = {
            "rec-1": {"settled": False},
        }
        assert (
            _is_unresolved_tension(
                payload, record_id="rec-1", review_status_by_record_id=review_status
            )
            is True
        )

    def test_event_layer_not_unresolved_tension(self):
        payload = {"subjectivity_layer": "event"}
        assert _is_unresolved_tension(payload) is False

    def test_unknown_layer_not_unresolved_tension(self):
        payload = {"subjectivity_layer": "unknown"}
        assert _is_unresolved_tension(payload) is False

    def test_tension_no_record_id_ignores_review_status(self):
        payload = {"subjectivity_layer": "tension"}
        review_status = {"some-other-id": {"settled": True}}
        # No record_id provided → review_status_by_record_id not consulted
        assert (
            _is_unresolved_tension(
                payload, record_id=None, review_status_by_record_id=review_status
            )
            is True
        )
