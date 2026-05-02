"""Tests for tonesoul.memory.subjectivity_review_batch — pure helpers (no SoulDB)."""

from __future__ import annotations

from collections import Counter

from tonesoul.memory.subjectivity_review_batch import (
    _carry_forward_annotation,
    _default_review_status,
    _density_compaction_followup,
    _handoff_shape,
    _history_density_summary,
    _latest_prior_status,
    _latest_review_context,
    _lineage_density_snapshot,
    _matches_group_signature,
    _operator_lens_summary,
    _operator_status_line,
    _parse_timestamp,
    _queue_posture,
    _review_basis_template,
    _revisit_readiness,
    _revisit_trigger,
    _revisit_trigger_code,
)

# ── _default_review_status ────────────────────────────────────────────────────


class TestDefaultReviewStatus:
    def test_candidate(self):
        assert _default_review_status("candidate_for_manual_review") == "manual_review_required"

    def test_reject(self):
        assert _default_review_status("reject_review") == "rejected"

    def test_defer(self):
        assert _default_review_status("defer_review") == "deferred"

    def test_unknown(self):
        assert _default_review_status("unknown_recommendation") == "manual_review_required"


# ── _parse_timestamp ──────────────────────────────────────────────────────────


class TestParseTimestamp:
    def test_z_suffix(self):
        from datetime import timezone

        result = _parse_timestamp("2026-01-01T00:00:00Z")
        assert result.tzinfo == timezone.utc

    def test_empty_returns_min(self):
        from datetime import datetime, timezone

        result = _parse_timestamp("")
        assert result == datetime.min.replace(tzinfo=timezone.utc)

    def test_none_returns_min(self):
        from datetime import datetime, timezone

        result = _parse_timestamp(None)
        assert result == datetime.min.replace(tzinfo=timezone.utc)

    def test_invalid_returns_min(self):
        from datetime import datetime, timezone

        result = _parse_timestamp("not-a-date")
        assert result == datetime.min.replace(tzinfo=timezone.utc)


# ── _revisit_readiness ────────────────────────────────────────────────────────


class TestRevisitReadiness:
    def test_non_deferred_na(self):
        result = _revisit_readiness(
            default_review_status="manual_review_required",
            pending_status_counts=Counter(),
            latest_review_timestamp="",
            latest_row_timestamp="",
        )
        assert result == "n/a"

    def test_deferred_no_review_timestamp(self):
        result = _revisit_readiness(
            default_review_status="deferred",
            pending_status_counts=Counter(),
            latest_review_timestamp="",
            latest_row_timestamp="",
        )
        assert result == "ready_for_first_deferred_write"

    def test_deferred_non_deferred_status_needs_revisit(self):
        result = _revisit_readiness(
            default_review_status="deferred",
            pending_status_counts=Counter({"approved": 1}),
            latest_review_timestamp="2026-01-01T00:00:00Z",
            latest_row_timestamp="2026-01-01T00:00:00Z",
        )
        assert result == "needs_revisit"

    def test_deferred_holding(self):
        result = _revisit_readiness(
            default_review_status="deferred",
            pending_status_counts=Counter({"deferred": 2}),
            latest_review_timestamp="2026-06-01T00:00:00Z",
            latest_row_timestamp="2026-01-01T00:00:00Z",
        )
        assert result == "holding_deferred"

    def test_new_row_after_review_needs_revisit(self):
        result = _revisit_readiness(
            default_review_status="deferred",
            pending_status_counts=Counter({"deferred": 1}),
            latest_review_timestamp="2026-01-01T00:00:00Z",
            latest_row_timestamp="2026-06-01T00:00:00Z",
        )
        assert result == "needs_revisit"


# ── _carry_forward_annotation ─────────────────────────────────────────────────


class TestCarryForwardAnnotation:
    def test_no_prior_fresh_group(self):
        result = _carry_forward_annotation(
            prior_decision_status_counts=Counter(),
            revisit_readiness="n/a",
        )
        assert result == "fresh_group"

    def test_all_approved(self):
        result = _carry_forward_annotation(
            prior_decision_status_counts=Counter({"approved": 2}),
            revisit_readiness="n/a",
        )
        assert result == "prior_approved_match"

    def test_all_rejected(self):
        result = _carry_forward_annotation(
            prior_decision_status_counts=Counter({"rejected": 1}),
            revisit_readiness="n/a",
        )
        assert result == "prior_reject_match"

    def test_deferred_needs_revisit(self):
        result = _carry_forward_annotation(
            prior_decision_status_counts=Counter({"deferred": 1}),
            revisit_readiness="needs_revisit",
        )
        assert result == "prior_deferred_match_needs_revisit"

    def test_deferred_holding(self):
        result = _carry_forward_annotation(
            prior_decision_status_counts=Counter({"deferred": 1}),
            revisit_readiness="holding_deferred",
        )
        assert result == "prior_deferred_match"

    def test_mixed_statuses(self):
        result = _carry_forward_annotation(
            prior_decision_status_counts=Counter({"approved": 1, "rejected": 1}),
            revisit_readiness="n/a",
        )
        assert result == "mixed_prior_decisions"


# ── _matches_group_signature ──────────────────────────────────────────────────


class TestMatchesGroupSignature:
    def test_matching_topic_and_source(self):
        row = {
            "topic": "safety",
            "direction": "safety_boundary",
            "source_url": "https://x.com",
            "stimulus_lineage": "",
        }
        result = _matches_group_signature(
            row,
            topic="safety",
            direction="safety_boundary",
            source_urls={"https://x.com"},
            stimulus_lineages=set(),
        )
        assert result is True

    def test_wrong_topic(self):
        row = {
            "topic": "other",
            "direction": "safety_boundary",
            "source_url": "https://x.com",
            "stimulus_lineage": "",
        }
        result = _matches_group_signature(
            row,
            topic="safety",
            direction="safety_boundary",
            source_urls={"https://x.com"},
            stimulus_lineages=set(),
        )
        assert result is False

    def test_matching_lineage(self):
        row = {"topic": "t1", "direction": "d1", "source_url": "", "stimulus_lineage": "lineage-a"}
        result = _matches_group_signature(
            row,
            topic="t1",
            direction="d1",
            source_urls=set(),
            stimulus_lineages={"lineage-a"},
        )
        assert result is True

    def test_no_overlap_when_filters_set(self):
        row = {
            "topic": "t1",
            "direction": "d1",
            "source_url": "https://other.com",
            "stimulus_lineage": "unrelated",
        }
        result = _matches_group_signature(
            row,
            topic="t1",
            direction="d1",
            source_urls={"https://x.com"},
            stimulus_lineages={"lineage-b"},
        )
        assert result is False


# ── _latest_prior_status ──────────────────────────────────────────────────────


class TestLatestPriorStatus:
    def test_empty_rows(self):
        assert _latest_prior_status([]) == ""

    def test_single_row(self):
        rows = [{"review_timestamp": "2026-01-01T00:00:00Z", "review_status": "approved"}]
        assert _latest_prior_status(rows) == "approved"

    def test_latest_by_timestamp(self):
        rows = [
            {"review_timestamp": "2026-01-01T00:00:00Z", "review_status": "rejected"},
            {"review_timestamp": "2026-06-01T00:00:00Z", "review_status": "approved"},
        ]
        assert _latest_prior_status(rows) == "approved"


# ── _latest_review_context ────────────────────────────────────────────────────


class TestLatestReviewContext:
    def test_empty_rows(self):
        result = _latest_review_context([])
        assert result["latest_review_status"] == ""

    def test_extracts_latest(self):
        rows = [
            {
                "review_timestamp": "2026-06-01T00:00:00Z",
                "review_status": "approved",
                "review_basis": "reason",
                "review_notes": "ok",
                "review_actor_id": "actor1",
                "review_actor_type": "human",
                "review_actor_display_name": "Alice",
            }
        ]
        result = _latest_review_context(rows)
        assert result["latest_review_status"] == "approved"
        assert result["latest_review_basis"] == "reason"
        assert result["latest_review_actor_id"] == "actor1"


# ── _review_basis_template ────────────────────────────────────────────────────


class TestReviewBasisTemplate:
    def _group(self, recommendation="candidate_for_manual_review"):
        return {
            "topic": "safety",
            "record_count": 5,
            "lineage_count": 3,
            "cycle_count": 2,
            "source_url_count": 2,
            "direction": "safety_boundary",
            "triage_recommendation": recommendation,
        }

    def test_reject_template(self):
        result = _review_basis_template(self._group("reject_review"))
        assert "repeated" in result.lower()

    def test_defer_template(self):
        result = _review_basis_template(self._group("defer_review"))
        assert "recurred" in result.lower()

    def test_candidate_template(self):
        result = _review_basis_template(self._group("candidate_for_manual_review"))
        assert "direction" in result.lower()


# ── _density_compaction_followup ──────────────────────────────────────────────


class TestDensityCompactionFollowup:
    def test_candidate_when_all_conditions_met(self):
        result = _density_compaction_followup(
            carry_forward_annotation="prior_deferred_match",
            revisit_readiness="holding_deferred",
            duplicate_pressure="high",
            same_source_loop=True,
            record_count=10,
            lineage_count=3,
            repeated_lineage_count=3,
            dense_lineage_count=2,
            max_lineage_record_count=5,
        )
        assert result["density_compaction_candidate"] is True

    def test_not_candidate_when_not_deferred(self):
        result = _density_compaction_followup(
            carry_forward_annotation="fresh_group",
            revisit_readiness="n/a",
            duplicate_pressure="high",
            same_source_loop=True,
            record_count=10,
            lineage_count=3,
            repeated_lineage_count=3,
            dense_lineage_count=2,
            max_lineage_record_count=5,
        )
        assert result["density_compaction_candidate"] is False

    def test_keys_present(self):
        result = _density_compaction_followup(
            carry_forward_annotation="fresh_group",
            revisit_readiness="n/a",
            duplicate_pressure="low",
            same_source_loop=False,
            record_count=2,
            lineage_count=1,
            repeated_lineage_count=0,
            dense_lineage_count=0,
            max_lineage_record_count=1,
        )
        for k in ("density_compaction_candidate", "density_compaction_reason", "operator_followup"):
            assert k in result


# ── _history_density_summary ──────────────────────────────────────────────────


class TestHistoryDensitySummary:
    def test_basic_summary(self):
        result = _history_density_summary(
            record_count=5,
            cycle_count=3,
            lineage_count=2,
            first_seen="2026-01-01",
            last_seen="2026-06-01",
            same_source_loop=False,
            latest_review_timestamp="",
            rows_after_latest_review=0,
        )
        assert "5" in result

    def test_same_source_loop_mentioned(self):
        result = _history_density_summary(
            record_count=5,
            cycle_count=3,
            lineage_count=2,
            first_seen="2026-01-01",
            last_seen="2026-06-01",
            same_source_loop=True,
            latest_review_timestamp="",
            rows_after_latest_review=0,
        )
        assert "same-source loop" in result

    def test_new_rows_mentioned(self):
        result = _history_density_summary(
            record_count=5,
            cycle_count=3,
            lineage_count=2,
            first_seen="2026-01-01",
            last_seen="2026-06-01",
            same_source_loop=False,
            latest_review_timestamp="2026-03-01",
            rows_after_latest_review=2,
        )
        assert "2 row(s) added since" in result


# ── _lineage_density_snapshot ─────────────────────────────────────────────────


class TestLineageDensitySnapshot:
    def test_empty_returns_empty(self):
        assert _lineage_density_snapshot({}) == ""

    def test_sorted_descending(self):
        result = _lineage_density_snapshot({"1": 3, "5": 1})
        assert result.index("5r") < result.index("1r")


# ── _queue_posture ────────────────────────────────────────────────────────────


class TestQueuePosture:
    def test_stable_deferred_history(self):
        result = _queue_posture(
            default_review_status="deferred",
            carry_forward_annotation="prior_deferred_match",
            revisit_readiness="holding_deferred",
        )
        assert result == "stable_deferred_history"

    def test_deferred_revisit_queue(self):
        result = _queue_posture(
            default_review_status="deferred",
            carry_forward_annotation="prior_deferred_match_needs_revisit",
            revisit_readiness="needs_revisit",
        )
        assert result == "deferred_revisit_queue"

    def test_active_manual_review(self):
        result = _queue_posture(
            default_review_status="manual_review_required",
            carry_forward_annotation="fresh_group",
            revisit_readiness="n/a",
        )
        assert result == "active_manual_review_queue"

    def test_rejected_reentry_watch(self):
        result = _queue_posture(
            default_review_status="rejected",
            carry_forward_annotation="prior_reject_match",
            revisit_readiness="n/a",
        )
        assert result == "rejected_reentry_watch"


# ── _revisit_trigger ──────────────────────────────────────────────────────────


class TestRevisitTrigger:
    def test_deferred_revisit_queue_trigger(self):
        result = _revisit_trigger(
            queue_posture="deferred_revisit_queue",
            rows_after_latest_review=3,
            latest_review_notes="",
            same_source_loop=False,
            default_review_status="deferred",
        )
        assert "3" in result

    def test_review_notes_used(self):
        result = _revisit_trigger(
            queue_posture="active_manual_review_queue",
            rows_after_latest_review=0,
            latest_review_notes="operator notes here",
            same_source_loop=False,
            default_review_status="manual_review_required",
        )
        assert "operator notes here" in result

    def test_manual_review_required(self):
        result = _revisit_trigger(
            queue_posture="active_manual_review_queue",
            rows_after_latest_review=0,
            latest_review_notes="",
            same_source_loop=False,
            default_review_status="manual_review_required",
        )
        assert "Review now" in result


# ── _revisit_trigger_code ─────────────────────────────────────────────────────


class TestRevisitTriggerCode:
    def test_stable_deferred(self):
        code = _revisit_trigger_code(
            queue_posture="stable_deferred_history",
            default_review_status="deferred",
        )
        assert code == "second_source_context_or_material_split"

    def test_manual_review(self):
        code = _revisit_trigger_code(
            queue_posture="active_manual_review_queue",
            default_review_status="manual_review_required",
        )
        assert code == "manual_review_required"


# ── _operator_lens_summary ────────────────────────────────────────────────────


class TestOperatorLensSummary:
    def test_basic_summary(self):
        result = _operator_lens_summary(
            queue_posture="active_manual_review_queue",
            record_count=3,
            lineage_count=2,
            cycle_count=1,
            lineage_density_snapshot="",
            rows_after_latest_review=0,
        )
        assert "3" in result
        assert "no new rows" in result

    def test_new_rows_mentioned(self):
        result = _operator_lens_summary(
            queue_posture="active_manual_review_queue",
            record_count=3,
            lineage_count=2,
            cycle_count=1,
            lineage_density_snapshot="3r x2",
            rows_after_latest_review=2,
        )
        assert "2 new row(s)" in result


# ── _operator_status_line ─────────────────────────────────────────────────────


class TestOperatorStatusLine:
    def test_basic_status_line(self):
        result = _operator_status_line(
            queue_posture="active_manual_review_queue",
            topic="safety",
            record_count=3,
            lineage_count=2,
            cycle_count=1,
            lineage_density_snapshot="",
            revisit_trigger_code="manual_review_required",
        )
        assert "safety" in result
        assert "manual_review_required" in result

    def test_density_included(self):
        result = _operator_status_line(
            queue_posture="active_manual_review_queue",
            topic="t1",
            record_count=5,
            lineage_count=3,
            cycle_count=2,
            lineage_density_snapshot="3r x2",
            revisit_trigger_code="code",
        )
        assert "density=3r x2" in result


# ── _handoff_shape ────────────────────────────────────────────────────────────


class TestHandoffShape:
    def test_empty(self):
        assert _handoff_shape([]) == "empty_queue"

    def test_stable_only(self):
        groups = [{"queue_posture": "stable_deferred_history"}]
        assert _handoff_shape(groups) == "stable_history_only"

    def test_action_required(self):
        groups = [{"queue_posture": "active_manual_review_queue"}]
        assert _handoff_shape(groups) == "action_required"

    def test_monitoring(self):
        groups = [{"queue_posture": "active_deferred_queue"}]
        assert _handoff_shape(groups) == "monitoring_queue"

    def test_mixed(self):
        # "mixed_queue" triggers when postures don't match any known category set
        groups = [
            {"queue_posture": "stable_deferred_history"},
            {"queue_posture": "unknown_custom_posture"},
        ]
        assert _handoff_shape(groups) == "mixed_queue"
