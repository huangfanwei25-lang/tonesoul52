"""Tests for tonesoul.shared_edit_preflight helper functions and main API."""

from __future__ import annotations

from tonesoul.shared_edit_preflight import (
    _build_working_style_consumer,
    _candidate_path_gaps,
    _candidate_paths_covered,
    _claim_command,
    _claim_overlap_records,
    _clean_paths,
    _flatten_overlap_paths,
    _normalize_repo_path,
    _path_key,
    _paths_overlap,
    build_shared_edit_preflight,
)

# ── _normalize_repo_path ──────────────────────────────────────────────────────


class TestNormalizeRepoPath:
    def test_strips_leading_dot_slash(self):
        assert _normalize_repo_path("./tonesoul/foo.py") == "tonesoul/foo.py"

    def test_strips_multiple_leading_dot_slash(self):
        assert _normalize_repo_path("././tonesoul/foo.py") == "tonesoul/foo.py"

    def test_strips_leading_slash(self):
        assert _normalize_repo_path("/tonesoul/foo.py") == "tonesoul/foo.py"

    def test_normalizes_backslash(self):
        assert _normalize_repo_path("tonesoul\\foo.py") == "tonesoul/foo.py"

    def test_empty_gives_empty(self):
        assert _normalize_repo_path("") == ""

    def test_none_gives_empty(self):
        assert _normalize_repo_path(None) == ""

    def test_strips_trailing_slash(self):
        assert _normalize_repo_path("tonesoul/") == "tonesoul"

    def test_simple_path_unchanged(self):
        assert _normalize_repo_path("tonesoul/foo.py") == "tonesoul/foo.py"


# ── _path_key ─────────────────────────────────────────────────────────────────


class TestPathKey:
    def test_casefolds(self):
        assert _path_key("ToNeSoul/FOO.py") == "tonesoul/foo.py"

    def test_strips_and_casefolds(self):
        assert _path_key("./ToNeSoul/Foo.py") == "tonesoul/foo.py"


# ── _paths_overlap ────────────────────────────────────────────────────────────


class TestPathsOverlap:
    def test_identical_paths_overlap(self):
        assert _paths_overlap("a/b.py", "a/b.py") is True

    def test_case_insensitive_overlap(self):
        assert _paths_overlap("A/B.py", "a/b.py") is True

    def test_left_is_prefix_of_right(self):
        assert _paths_overlap("tonesoul", "tonesoul/foo.py") is True

    def test_right_is_prefix_of_left(self):
        assert _paths_overlap("tonesoul/foo.py", "tonesoul") is True

    def test_no_overlap_different_paths(self):
        assert _paths_overlap("a/b.py", "c/d.py") is False

    def test_empty_left_no_overlap(self):
        assert _paths_overlap("", "a/b.py") is False

    def test_empty_right_no_overlap(self):
        assert _paths_overlap("a/b.py", "") is False

    def test_partial_name_no_overlap(self):
        assert _paths_overlap("tonesoul/foo.py", "tonesoul/foobar.py") is False


# ── _clean_paths ─────────────────────────────────────────────────────────────


class TestCleanPaths:
    def test_normalizes_paths(self):
        result = _clean_paths(["./a/b.py"])
        assert result == ["a/b.py"]

    def test_deduplicates(self):
        result = _clean_paths(["a/b.py", "a/b.py"])
        assert result == ["a/b.py"]

    def test_filters_empty(self):
        result = _clean_paths(["", None, "a/b.py"])
        assert result == ["a/b.py"]

    def test_none_input_gives_empty_list(self):
        result = _clean_paths(None)
        assert result == []

    def test_empty_list_gives_empty_list(self):
        result = _clean_paths([])
        assert result == []

    def test_preserves_order(self):
        result = _clean_paths(["z/a.py", "a/b.py"])
        assert result == ["z/a.py", "a/b.py"]


# ── _claim_overlap_records ────────────────────────────────────────────────────


class TestClaimOverlapRecords:
    def _make_claim(self, task_id, agent, paths):
        return {"task_id": task_id, "agent": agent, "summary": "task", "paths": paths}

    def test_self_claim_classified_as_self(self):
        claims = [self._make_claim("t1", "agent-a", ["tonesoul/foo.py"])]
        self_recs, other_recs = _claim_overlap_records(
            agent_id="agent-a",
            candidate_paths=["tonesoul/foo.py"],
            claims=claims,
        )
        assert len(self_recs) == 1
        assert self_recs[0]["ownership"] == "self"
        assert len(other_recs) == 0

    def test_other_agent_claim_classified_as_other(self):
        claims = [self._make_claim("t1", "agent-b", ["tonesoul/foo.py"])]
        self_recs, other_recs = _claim_overlap_records(
            agent_id="agent-a",
            candidate_paths=["tonesoul/foo.py"],
            claims=claims,
        )
        assert len(other_recs) == 1
        assert other_recs[0]["ownership"] == "other"

    def test_non_overlapping_claim_excluded(self):
        claims = [self._make_claim("t1", "agent-b", ["unrelated/bar.py"])]
        self_recs, other_recs = _claim_overlap_records(
            agent_id="agent-a",
            candidate_paths=["tonesoul/foo.py"],
            claims=claims,
        )
        assert len(self_recs) == 0
        assert len(other_recs) == 0

    def test_overlap_paths_populated(self):
        claims = [self._make_claim("t1", "agent-b", ["tonesoul/foo.py"])]
        _, other_recs = _claim_overlap_records(
            agent_id="agent-a",
            candidate_paths=["tonesoul/foo.py"],
            claims=claims,
        )
        assert "tonesoul/foo.py" in other_recs[0]["overlap_paths"]

    def test_directory_overlap_detected(self):
        claims = [self._make_claim("t1", "agent-b", ["tonesoul"])]
        _, other_recs = _claim_overlap_records(
            agent_id="agent-a",
            candidate_paths=["tonesoul/foo.py"],
            claims=claims,
        )
        assert len(other_recs) == 1

    def test_empty_claims_gives_empty_results(self):
        self_recs, other_recs = _claim_overlap_records(
            agent_id="agent-a",
            candidate_paths=["tonesoul/foo.py"],
            claims=[],
        )
        assert self_recs == []
        assert other_recs == []


# ── _candidate_paths_covered ─────────────────────────────────────────────────


class TestCandidatePathsCovered:
    def test_all_covered(self):
        records = [{"overlap_paths": ["a/b.py", "c/d.py"]}]
        assert (
            _candidate_paths_covered(candidate_paths=["a/b.py", "c/d.py"], records=records) is True
        )

    def test_partial_covered_is_false(self):
        records = [{"overlap_paths": ["a/b.py"]}]
        assert (
            _candidate_paths_covered(candidate_paths=["a/b.py", "c/d.py"], records=records) is False
        )

    def test_empty_paths_is_vacuously_true(self):
        assert _candidate_paths_covered(candidate_paths=[], records=[]) is True

    def test_no_records_with_paths_is_false(self):
        assert _candidate_paths_covered(candidate_paths=["a/b.py"], records=[]) is False


# ── _candidate_path_gaps ─────────────────────────────────────────────────────


class TestCandidatePathGaps:
    def test_uncovered_path_is_gap(self):
        gaps = _candidate_path_gaps(
            candidate_paths=["a/b.py", "c/d.py"],
            records=[{"overlap_paths": ["a/b.py"]}],
        )
        assert "c/d.py" in gaps
        assert "a/b.py" not in gaps

    def test_all_covered_gives_empty_gaps(self):
        gaps = _candidate_path_gaps(
            candidate_paths=["a/b.py"],
            records=[{"overlap_paths": ["a/b.py"]}],
        )
        assert gaps == []

    def test_empty_paths_gives_empty_gaps(self):
        gaps = _candidate_path_gaps(candidate_paths=[], records=[])
        assert gaps == []


# ── _flatten_overlap_paths ────────────────────────────────────────────────────


class TestFlattenOverlapPaths:
    def test_collects_all_paths(self):
        records = [
            {"overlap_paths": ["a/b.py"]},
            {"overlap_paths": ["c/d.py"]},
        ]
        result = _flatten_overlap_paths(records)
        assert "a/b.py" in result
        assert "c/d.py" in result

    def test_deduplicates(self):
        records = [
            {"overlap_paths": ["a/b.py"]},
            {"overlap_paths": ["a/b.py"]},
        ]
        result = _flatten_overlap_paths(records)
        assert result.count("a/b.py") == 1

    def test_empty_records_gives_empty(self):
        assert _flatten_overlap_paths([]) == []


# ── _claim_command ────────────────────────────────────────────────────────────


class TestClaimCommand:
    def test_contains_agent_id(self):
        cmd = _claim_command("my-agent", ["tonesoul/foo.py"])
        assert "my-agent" in cmd

    def test_contains_path(self):
        cmd = _claim_command("agent", ["tonesoul/foo.py"])
        assert "tonesoul/foo.py" in cmd

    def test_contains_run_task_claim(self):
        cmd = _claim_command("agent", ["x.py"])
        assert "run_task_claim.py" in cmd


# ── _build_working_style_consumer ────────────────────────────────────────────


class TestBuildWorkingStyleConsumer:
    def test_absent_playbook_returns_not_present(self):
        result = _build_working_style_consumer(None)
        assert result["present"] is False

    def test_empty_playbook_returns_not_present(self):
        result = _build_working_style_consumer({})
        assert result["present"] is False

    def test_present_playbook_extracts_habits(self):
        playbook = {
            "present": True,
            "checklist": ["habit one", "habit two", "habit three"],
            "summary_text": "do this",
            "application_rule": "apply bounded",
            "non_promotion_rule": "no promotion",
        }
        result = _build_working_style_consumer(playbook)
        assert result["present"] is True
        assert len(result["selected_habits"]) == 2  # max 2 habits

    def test_missing_summary_uses_habits(self):
        playbook = {
            "present": True,
            "checklist": ["h1", "h2"],
        }
        result = _build_working_style_consumer(playbook)
        assert "h1" in result["summary_text"]

    def test_default_application_rule_filled(self):
        playbook = {"present": True, "checklist": ["h1"]}
        result = _build_working_style_consumer(playbook)
        assert result["application_rule"]

    def test_default_non_promotion_rule_filled(self):
        playbook = {"present": True, "checklist": ["h1"]}
        result = _build_working_style_consumer(playbook)
        assert result["non_promotion_rule"]


# ── build_shared_edit_preflight ───────────────────────────────────────────────


def _base_kwargs(**overrides):
    base = {
        "agent_id": "agent-x",
        "candidate_paths": ["tonesoul/foo.py"],
        "readiness": {"status": "ready"},
        "claims": [],
        "task_track_hint": {
            "claim_recommendation": "optional",
            "suggested_track": "feature_track",
        },
        "mutation_preflight": {"summary_text": "safe mutation"},
        "working_style_playbook": None,
    }
    base.update(overrides)
    return base


class TestBuildSharedEditPreflight:
    def test_no_paths_gives_insufficient_input(self):
        result = build_shared_edit_preflight(**_base_kwargs(candidate_paths=None))
        assert result["decision"] == "insufficient_input"

    def test_empty_paths_gives_insufficient_input(self):
        result = build_shared_edit_preflight(**_base_kwargs(candidate_paths=[]))
        assert result["decision"] == "insufficient_input"

    def test_blocked_readiness_gives_blocked(self):
        result = build_shared_edit_preflight(**_base_kwargs(readiness={"status": "blocked"}))
        assert result["decision"] == "blocked"

    def test_other_agent_overlap_gives_coordinate(self):
        claims = [
            {
                "task_id": "t1",
                "agent": "other-agent",
                "summary": "hold lane",
                "paths": ["tonesoul/foo.py"],
            }
        ]
        result = build_shared_edit_preflight(**_base_kwargs(claims=claims))
        assert result["decision"] == "coordinate"

    def test_missing_self_claim_gives_claim_first(self):
        result = build_shared_edit_preflight(
            **_base_kwargs(
                task_track_hint={
                    "claim_recommendation": "required",
                    "suggested_track": "feature_track",
                }
            )
        )
        assert result["decision"] == "claim_first"

    def test_clear_decision_when_no_conflicts(self):
        result = build_shared_edit_preflight(**_base_kwargs())
        assert result["decision"] == "clear"

    def test_present_is_true_with_paths(self):
        result = build_shared_edit_preflight(**_base_kwargs())
        assert result["present"] is True

    def test_normalized_candidate_paths(self):
        result = build_shared_edit_preflight(**_base_kwargs(candidate_paths=["./tonesoul/foo.py"]))
        assert "tonesoul/foo.py" in result["normalized_candidate_paths"]

    def test_task_track_propagated(self):
        result = build_shared_edit_preflight(**_base_kwargs())
        assert result["task_track"] == "feature_track"

    def test_summary_text_contains_decision(self):
        result = build_shared_edit_preflight(**_base_kwargs())
        assert "clear" in result["summary_text"]

    def test_overlap_count_zero_without_conflicts(self):
        result = build_shared_edit_preflight(**_base_kwargs())
        assert result["overlap_count"] == 0

    def test_other_overlap_paths_listed(self):
        claims = [
            {
                "task_id": "t1",
                "agent": "other-agent",
                "summary": "s",
                "paths": ["tonesoul/foo.py"],
            }
        ]
        result = build_shared_edit_preflight(**_base_kwargs(claims=claims))
        assert "tonesoul/foo.py" in result["other_overlap_paths"]

    def test_working_style_consumer_in_result(self):
        result = build_shared_edit_preflight(**_base_kwargs())
        assert "working_style_consumer" in result

    def test_self_claim_covers_all_false_without_claim(self):
        result = build_shared_edit_preflight(**_base_kwargs())
        assert result["self_claim_covers_all"] is False

    def test_self_claim_covers_all_true_with_own_claim(self):
        claims = [
            {
                "task_id": "t1",
                "agent": "agent-x",
                "summary": "my work",
                "paths": ["tonesoul/foo.py"],
            }
        ]
        result = build_shared_edit_preflight(**_base_kwargs(claims=claims))
        assert result["self_claim_covers_all"] is True

    def test_decision_basis_in_result(self):
        result = build_shared_edit_preflight(**_base_kwargs())
        assert "decision_basis" in result

    def test_receiver_rule_not_empty(self):
        result = build_shared_edit_preflight(**_base_kwargs())
        assert result["receiver_rule"]
