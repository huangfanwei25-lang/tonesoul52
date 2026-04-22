"""Tests for tonesoul.memory.pipeline — pure functions and orchestrator error handling."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from tonesoul.memory.pipeline import (
    CONSOLIDATION_INTERVAL,
    WISDOM_BETA,
    PipelineResult,
    _adapt_patterns,
    _count_rediscoveries,
    _digest_to_text,
    classify_lane,
    run_session_end_pipeline,
)


# ── PipelineResult ────────────────────────────────────────────────────────────

class TestPipelineResult:
    def test_default_digest_written_false(self):
        r = PipelineResult()
        assert r.digest_written is False

    def test_default_consolidation_ran_false(self):
        r = PipelineResult()
        assert r.consolidation_ran is False

    def test_default_crystals_zero(self):
        r = PipelineResult()
        assert r.crystals_generated == 0

    def test_default_rag_ingested_zero(self):
        r = PipelineResult()
        assert r.rag_ingested == 0

    def test_default_wisdom_delta_zero(self):
        r = PipelineResult()
        assert r.wisdom_delta == 0.0

    def test_default_errors_empty_list(self):
        r = PipelineResult()
        assert r.errors == []

    def test_errors_list_independent_per_instance(self):
        r1 = PipelineResult()
        r2 = PipelineResult()
        r1.errors.append("err")
        assert r2.errors == []


# ── classify_lane ─────────────────────────────────────────────────────────────

class TestClassifyLane:
    def test_vow_keyword_gives_governance(self):
        assert classify_lane(["vow maintenance"], []) == "governance"

    def test_axiom_keyword_gives_governance(self):
        assert classify_lane([], ["axiom 3 tension"]) == "governance"

    def test_drift_keyword_gives_governance(self):
        assert classify_lane(["drift detection"], []) == "governance"

    def test_council_keyword_gives_governance(self):
        assert classify_lane([], ["council deliberation"]) == "governance"

    def test_aegis_keyword_gives_governance(self):
        assert classify_lane(["aegis shield"], []) == "governance"

    def test_handoff_keyword_gives_continuity(self):
        assert classify_lane(["handoff notes"], []) == "continuity"

    def test_checkpoint_keyword_gives_continuity(self):
        assert classify_lane([], ["checkpoint saved"]) == "continuity"

    def test_compaction_keyword_gives_continuity(self):
        assert classify_lane(["compaction done"], []) == "continuity"

    def test_session_keyword_gives_continuity(self):
        assert classify_lane([], ["session end"]) == "continuity"

    def test_learning_when_no_keywords(self):
        assert classify_lane(["random topic"], ["some learning"]) == "learning"

    def test_empty_lists_gives_learning(self):
        assert classify_lane([], []) == "learning"

    def test_governance_wins_over_continuity(self):
        # governance keywords should win because they're checked first
        result = classify_lane(["governance"], ["handoff"])
        assert result == "governance"

    def test_chinese_governance_keyword(self):
        assert classify_lane(["治理策略"], []) == "governance"

    def test_chinese_continuity_keyword(self):
        assert classify_lane(["交接文件"], []) == "continuity"


# ── _count_rediscoveries ──────────────────────────────────────────────────────

class TestCountRediscoveries:
    def test_empty_events_returns_zero(self):
        assert _count_rediscoveries([], []) == 0

    def test_empty_crystals_returns_zero(self):
        events = [{"topic": "drift tracking", "severity": 0.5}]
        assert _count_rediscoveries(events, []) == 0

    def test_no_overlap_returns_zero(self):
        crystal = MagicMock()
        crystal.rule = "boundary discipline constraint"
        events = [{"topic": "vow creation", "severity": 0.2}]
        assert _count_rediscoveries(events, [crystal]) == 0

    def test_matching_topic_counts(self):
        crystal = MagicMock()
        crystal.rule = "boundary enforcement"
        events = [{"topic": "boundary issue detected", "severity": 0.4}]
        count = _count_rediscoveries(events, [crystal])
        assert count >= 1

    def test_short_words_in_rule_ignored(self):
        # Words ≤4 chars should be skipped as keywords
        crystal = MagicMock()
        crystal.rule = "use the for"  # all short words
        events = [{"topic": "the use for that", "severity": 0.1}]
        count = _count_rediscoveries(events, [crystal])
        assert count == 0

    def test_multiple_events_multiple_matches(self):
        crystal = MagicMock()
        crystal.rule = "safety boundary enforcement"
        events = [
            {"topic": "safety check failed", "severity": 0.5},
            {"topic": "boundary exceeded", "severity": 0.4},
        ]
        count = _count_rediscoveries(events, [crystal])
        assert count == 2

    def test_crystal_without_rule_attr(self):
        crystal = MagicMock()
        crystal.rule = None
        events = [{"topic": "anything", "severity": 0.3}]
        assert _count_rediscoveries(events, [crystal]) == 0


# ── _digest_to_text ───────────────────────────────────────────────────────────

class TestDigestToText:
    def test_includes_session_id(self):
        digest = {"session_id": "sess-abc", "topics": [], "learnings": []}
        text = _digest_to_text(digest)
        assert "sess-abc" in text

    def test_includes_topics(self):
        digest = {"session_id": "s", "topics": ["governance", "drift"], "learnings": []}
        text = _digest_to_text(digest)
        assert "governance" in text
        assert "drift" in text

    def test_includes_learnings(self):
        digest = {"session_id": "s", "topics": [], "learnings": ["pattern A observed"]}
        text = _digest_to_text(digest)
        assert "pattern A observed" in text

    def test_includes_unresolved_topics(self):
        digest = {
            "session_id": "s",
            "topics": [],
            "learnings": [],
            "tension_summary": {"unresolved_topics": ["topic X"]},
        }
        text = _digest_to_text(digest)
        assert "topic X" in text

    def test_includes_stance_shift(self):
        digest = {
            "session_id": "s",
            "topics": [],
            "learnings": [],
            "stance_shift": {"from": "caution", "to": "innovation"},
        }
        text = _digest_to_text(digest)
        assert "caution" in text
        assert "innovation" in text

    def test_no_stance_shift_no_stance_line(self):
        digest = {"session_id": "s", "topics": [], "learnings": []}
        text = _digest_to_text(digest)
        assert "Stance" not in text

    def test_missing_session_id_gives_unknown(self):
        digest = {"topics": [], "learnings": []}
        text = _digest_to_text(digest)
        assert "unknown" in text

    def test_returns_string(self):
        assert isinstance(_digest_to_text({}), str)


# ── _adapt_patterns ───────────────────────────────────────────────────────────

class TestAdaptPatterns:
    def _make_consolidation(self, patterns):
        result = MagicMock()
        result.patterns = patterns
        return result

    def test_verdict_counts_propagated(self):
        consolidation = self._make_consolidation({"verdict_counts": {"approve": 5, "reject": 2}})
        adapted = _adapt_patterns(consolidation)
        assert adapted["verdicts"]["approve"] == 5

    def test_low_tension_approvals_counted(self):
        consolidation = self._make_consolidation(
            {"verdict_counts": {"approve": 4}, "average_weighted_tension": 0.2}
        )
        adapted = _adapt_patterns(consolidation)
        assert adapted["low_tension_approvals"] == 4

    def test_high_tension_approvals_not_counted(self):
        consolidation = self._make_consolidation(
            {"verdict_counts": {"approve": 4}, "average_weighted_tension": 0.5}
        )
        adapted = _adapt_patterns(consolidation)
        assert adapted["low_tension_approvals"] == 0

    def test_autonomous_high_delta_from_genesis(self):
        consolidation = self._make_consolidation(
            {"verdict_counts": {}, "genesis_counts": {"autonomous": 3}}
        )
        adapted = _adapt_patterns(consolidation)
        assert adapted["autonomous_high_delta"] == 3

    def test_resonance_convergences_always_zero(self):
        consolidation = self._make_consolidation({"verdict_counts": {}})
        adapted = _adapt_patterns(consolidation)
        assert adapted["resonance_convergences"] == 0


# ── run_session_end_pipeline — error accumulation ─────────────────────────────

class TestRunSessionEndPipeline:
    def test_returns_pipeline_result(self):
        with (
            patch("tonesoul.memory.pipeline._write_digest", side_effect=Exception("db error")),
            patch("tonesoul.memory.pipeline._maybe_consolidate", side_effect=Exception("no db")),
            patch("tonesoul.memory.pipeline._compute_wisdom_delta", side_effect=Exception("no crystals")),
            patch("tonesoul.memory.pipeline._ingest_to_rag", side_effect=Exception("no faiss")),
        ):
            result = run_session_end_pipeline({"session_id": "s"}, session_count=1)
        assert isinstance(result, PipelineResult)

    def test_digest_failure_captured_in_errors(self):
        with (
            patch("tonesoul.memory.pipeline._write_digest", side_effect=Exception("no db")),
            patch("tonesoul.memory.pipeline._maybe_consolidate", side_effect=Exception("no db")),
            patch("tonesoul.memory.pipeline._compute_wisdom_delta", side_effect=Exception("no cr")),
            patch("tonesoul.memory.pipeline._ingest_to_rag", side_effect=Exception("no faiss")),
        ):
            result = run_session_end_pipeline({}, session_count=1)
        assert any("digest" in e for e in result.errors)

    def test_errors_never_propagate(self):
        with (
            patch("tonesoul.memory.pipeline._write_digest", side_effect=RuntimeError("BOOM")),
            patch("tonesoul.memory.pipeline._maybe_consolidate", side_effect=RuntimeError("BOOM")),
            patch("tonesoul.memory.pipeline._compute_wisdom_delta", side_effect=RuntimeError("BOOM")),
            patch("tonesoul.memory.pipeline._ingest_to_rag", side_effect=RuntimeError("BOOM")),
        ):
            result = run_session_end_pipeline({}, session_count=1)
        assert len(result.errors) >= 3  # digest + consolidation + wisdom

    def test_digest_written_true_on_success(self):
        with (
            patch("tonesoul.memory.pipeline._write_digest", return_value={"session_id": "s"}),
            patch("tonesoul.memory.pipeline._maybe_consolidate", side_effect=Exception("skip")),
            patch("tonesoul.memory.pipeline._compute_wisdom_delta", return_value=0.5),
            patch("tonesoul.memory.pipeline._ingest_to_rag", return_value=1),
        ):
            result = run_session_end_pipeline({}, session_count=1)
        assert result.digest_written is True

    def test_wisdom_delta_set_on_success(self):
        with (
            patch("tonesoul.memory.pipeline._write_digest", return_value={}),
            patch("tonesoul.memory.pipeline._maybe_consolidate", return_value=None),
            patch("tonesoul.memory.pipeline._compute_wisdom_delta", return_value=0.42),
            patch("tonesoul.memory.pipeline._ingest_to_rag", return_value=0),
        ):
            result = run_session_end_pipeline({}, session_count=1)
        assert result.wisdom_delta == pytest.approx(0.42)

    def test_rag_ingested_count_set(self):
        with (
            patch("tonesoul.memory.pipeline._write_digest", return_value={"session_id": "s"}),
            patch("tonesoul.memory.pipeline._maybe_consolidate", return_value=None),
            patch("tonesoul.memory.pipeline._compute_wisdom_delta", return_value=0.3),
            patch("tonesoul.memory.pipeline._ingest_to_rag", return_value=2),
        ):
            result = run_session_end_pipeline({}, session_count=1)
        assert result.rag_ingested == 2

    def test_force_consolidate_flag(self):
        mock_consolidation = MagicMock()
        mock_consolidation.patterns = {"verdict_counts": {}, "average_weighted_tension": 0.1}
        with (
            patch("tonesoul.memory.pipeline._write_digest", return_value={}),
            patch("tonesoul.memory.pipeline._maybe_consolidate", return_value=mock_consolidation) as mock_mc,
            patch("tonesoul.memory.pipeline._crystallize", return_value=[]) as mock_crys,
            patch("tonesoul.memory.pipeline._compute_wisdom_delta", return_value=0.1),
            patch("tonesoul.memory.pipeline._ingest_to_rag", return_value=0),
            patch("tonesoul.memory.pipeline.export_crystal_index", return_value={}),
        ):
            run_session_end_pipeline({}, session_count=2, force_consolidate=True)
            _, kwargs = mock_mc.call_args
            assert kwargs.get("force") is True


# ── Constants ─────────────────────────────────────────────────────────────────

class TestConstants:
    def test_consolidation_interval_positive(self):
        assert CONSOLIDATION_INTERVAL > 0

    def test_wisdom_beta_between_zero_and_one(self):
        assert 0.0 < WISDOM_BETA < 1.0
