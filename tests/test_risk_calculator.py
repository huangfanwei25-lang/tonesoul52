from __future__ import annotations

from types import SimpleNamespace

import pytest

import tonesoul.risk_calculator as risk_calculator
from tonesoul.risk_calculator import build_project_memory_summary, compute_runtime_risk


def test_compute_runtime_risk_surfaces_high_pressure_factors() -> None:
    posture = SimpleNamespace(
        tension_history=[
            {"topic": "governance", "severity": 0.82},
            {"topic": "runtime", "severity": 0.74},
        ],
        aegis_vetoes=[{"type": "memory_poisoning"}],
    )
    recent_traces = [
        {"agent": "codex", "topics": ["governance"], "tension_count": 3},
        {"agent": "claude", "topics": ["runtime"], "tension_count": 2},
    ]
    claims = [
        {"task_id": "risk-r", "agent": "codex"},
        {"task_id": "packet-summary", "agent": "claude"},
    ]
    compactions = [
        {
            "pending_paths": [
                "tonesoul/runtime_adapter.py",
                "spec/governance/r_memory_packet_v1.schema.json",
            ]
        },
        {"pending_paths": ["tonesoul/diagnose.py", "tests/test_runtime_adapter.py"]},
    ]

    risk = compute_runtime_risk(
        posture=posture,
        recent_traces=recent_traces,
        claims=claims,
        compactions=compactions,
    )

    assert risk["score"] > 0.5
    assert risk["level"] in {"caution", "high", "critical"}
    assert "high_recent_tension" in risk["factors"]
    assert "recent_aegis_vetoes" in risk["factors"]


def test_build_project_memory_summary_aggregates_focus_pending_and_repo_progress() -> None:
    posture = SimpleNamespace(tension_history=[{"topic": "fallback", "severity": 0.4}])
    original_repo_snapshot = risk_calculator._build_repo_progress_snapshot
    risk_calculator._build_repo_progress_snapshot = lambda repo_root=None: {
        "available": True,
        "branch": "feature/r-memory",
        "head": "abc1234",
        "staged_count": 1,
        "modified_count": 2,
        "untracked_count": 3,
        "dirty_count": 6,
        "path_preview": ["tonesoul/runtime_adapter.py"],
    }
    try:
        summary = build_project_memory_summary(
            posture=posture,
            recent_traces=[
                {"agent": "codex", "topics": ["runtime", "risk"]},
                {"agent": "claude", "topics": ["risk", "packet"]},
            ],
            claims=[
                {
                    "task_id": "risk-r",
                    "agent": "codex",
                    "paths": ["tonesoul/runtime_adapter.py"],
                },
            ],
            compactions=[
                {
                    "pending_paths": ["tonesoul/diagnose.py"],
                    "carry_forward": ["keep packet readable"],
                    "next_action": "leave compaction before release once diagnose catches up",
                }
            ],
            subject_snapshots=[
                {
                    "summary": "Stay packet-first and keep theory out of runtime truth.",
                    "stable_vows": ["do not smuggle theory into runtime"],
                    "durable_boundaries": ["protected files stay human-managed"],
                    "decision_preferences": ["prefer packet before broad repo scan"],
                    "verified_routines": ["leave compaction before release"],
                    "active_threads": ["subject-snapshot rollout"],
                }
            ],
            routing_summary={
                "summary_text": "router=writes=1 previews=0 overrides=0 overlap=0 misroute_signals=0 top=checkpoint",
                "recent_events": [
                    {
                        "summary": "checkpoint before release remains the default handoff rhythm",
                    }
                ],
            },
        )
    finally:
        risk_calculator._build_repo_progress_snapshot = original_repo_snapshot

    assert summary["focus_topics"][0] == "risk"
    assert "codex" in summary["recent_agents"]
    assert "tonesoul/runtime_adapter.py" in summary["pending_paths"]
    assert summary["carry_forward"] == ["keep packet readable"]
    assert summary["subject_anchor"]["summary"].startswith("Stay packet-first")
    assert summary["working_style_anchor"]["summary"].startswith(
        "prefs=prefer packet before broad repo scan"
    )
    assert summary["working_style_anchor"]["decision_preferences"] == [
        "prefer packet before broad repo scan"
    ]
    assert summary["working_style_anchor"]["verified_routines"] == [
        "leave compaction before release"
    ]
    assert summary["working_style_anchor"]["guardrail_boundaries"] == [
        "protected files stay human-managed"
    ]
    assert summary["working_style_anchor"]["receiver_posture"] == "advisory_apply_not_promote"
    assert "render-layer noise" in summary["working_style_anchor"]["render_caveat"]
    assert summary["working_style_observability"]["status"] == "reinforced"
    assert summary["working_style_observability"]["drift_risk"] == "low"
    assert summary["working_style_observability"]["reinforced_item_count"] == 2
    assert (
        "decision_preferences: prefer packet before broad repo scan"
        in summary["working_style_observability"]["reinforced_items"]
    )
    assert (
        "verified_routines: leave compaction before release"
        in summary["working_style_observability"]["reinforced_items"]
    )
    assert summary["working_style_import_limits"]["apply_posture"] == "bounded_default"
    assert any(
        item.startswith("scan_order:")
        for item in summary["working_style_import_limits"]["safe_apply"]
    )
    assert any(
        item.startswith("canonical_governance_truth:")
        for item in summary["working_style_import_limits"]["must_not_import"]
    )
    assert summary["repo_progress"]["branch"] == "feature/r-memory"
    assert "focus=risk, runtime" in summary["summary_text"]
    assert (
        "subject=Stay packet-first and keep theory out of runtime truth." in summary["summary_text"]
    )
    assert "repo=feature/r-memory@abc1234 dirty=6" in summary["summary_text"]


def test_repo_progress_snapshot_parses_git_status(monkeypatch) -> None:
    class _Completed:
        def __init__(self, stdout: str, returncode: int = 0) -> None:
            self.stdout = stdout
            self.returncode = returncode

    responses = {
        ("git", "rev-parse", "--abbrev-ref", "HEAD"): _Completed("feature/r-memory\n"),
        ("git", "rev-parse", "--short", "HEAD"): _Completed("abc1234\n"),
        ("git", "status", "--short"): _Completed(
            " M CLAUDE.md\n"
            "M  tonesoul/runtime_adapter.py\n"
            " M tonesoul/diagnose.py\n"
            "?? docs/status/new_snapshot.md\n"
        ),
    }

    def _fake_run(command, **kwargs):
        return responses[tuple(command)]

    monkeypatch.setattr(risk_calculator.subprocess, "run", _fake_run)

    snapshot = risk_calculator._build_repo_progress_snapshot(repo_root=".")

    assert snapshot["available"] is True
    assert snapshot["branch"] == "feature/r-memory"
    assert snapshot["head"] == "abc1234"
    assert snapshot["staged_count"] == 1
    assert snapshot["modified_count"] == 2
    assert snapshot["untracked_count"] == 1
    assert snapshot["dirty_count"] == 4
    assert snapshot["path_preview"][0] == "CLAUDE.md"
    assert snapshot["path_preview"][1] == "tonesoul/runtime_adapter.py"


# ── _coerce_unit ──────────────────────────────────────────────────────────────

class TestCoerceUnit:
    def test_normal_float(self):
        assert risk_calculator._coerce_unit(0.5) == pytest.approx(0.5)

    def test_clamps_above_one(self):
        assert risk_calculator._coerce_unit(1.5) == pytest.approx(1.0)

    def test_clamps_below_zero(self):
        assert risk_calculator._coerce_unit(-0.5) == pytest.approx(0.0)

    def test_none_returns_zero(self):
        assert risk_calculator._coerce_unit(None) == 0.0

    def test_string_number(self):
        assert risk_calculator._coerce_unit("0.75") == pytest.approx(0.75)

    def test_invalid_string_returns_zero(self):
        assert risk_calculator._coerce_unit("bad") == 0.0

    def test_integer_one(self):
        assert risk_calculator._coerce_unit(1) == pytest.approx(1.0)

    def test_integer_zero(self):
        assert risk_calculator._coerce_unit(0) == pytest.approx(0.0)


# ── _unique_ordered ───────────────────────────────────────────────────────────

class TestUniqueOrdered:
    def test_preserves_order(self):
        result = risk_calculator._unique_ordered(["c", "a", "b"])
        assert result == ["c", "a", "b"]

    def test_deduplicates(self):
        result = risk_calculator._unique_ordered(["a", "b", "a"])
        assert result == ["a", "b"]

    def test_filters_empty_strings(self):
        result = risk_calculator._unique_ordered(["a", "", "  ", "b"])
        assert result == ["a", "b"]

    def test_none_values_filtered(self):
        result = risk_calculator._unique_ordered([None, "a", None])
        assert result == ["a"]

    def test_strips_whitespace(self):
        result = risk_calculator._unique_ordered(["  x  ", "y"])
        assert result == ["x", "y"]

    def test_empty_input(self):
        assert risk_calculator._unique_ordered([]) == []


# ── _slice_strings ────────────────────────────────────────────────────────────

class TestSliceStrings:
    def test_limits_results(self):
        result = risk_calculator._slice_strings(["a", "b", "c", "d"], 2)
        assert result == ["a", "b"]

    def test_limit_zero_returns_empty(self):
        result = risk_calculator._slice_strings(["a", "b"], 0)
        assert result == []

    def test_none_input_returns_empty(self):
        result = risk_calculator._slice_strings(None, 3)
        assert result == []

    def test_deduplication_applies(self):
        result = risk_calculator._slice_strings(["a", "a", "b"], 10)
        assert result == ["a", "b"]


# ── RiskAssessment.to_dict ────────────────────────────────────────────────────

class TestRiskAssessmentToDict:
    def test_fields_present(self):
        from tonesoul.risk_calculator import RiskAssessment
        ra = RiskAssessment(
            score=0.72,
            level="high",
            factors=["high_recent_tension"],
            recommended_action="review_before_commit",
            inputs={"tension_pressure": 0.5},
        )
        d = ra.to_dict()
        assert d["score"] == pytest.approx(0.72)
        assert d["level"] == "high"
        assert d["factors"] == ["high_recent_tension"]
        assert d["recommended_action"] == "review_before_commit"
        assert d["inputs"]["tension_pressure"] == pytest.approx(0.5)

    def test_score_rounded(self):
        from tonesoul.risk_calculator import RiskAssessment
        ra = RiskAssessment(
            score=0.123456789,
            level="stable",
            factors=[],
            recommended_action="normal_operation",
            inputs={},
        )
        assert ra.to_dict()["score"] == pytest.approx(0.1235, abs=1e-4)


# ── compute_runtime_risk — level bands ───────────────────────────────────────

class TestComputeRuntimeRiskLevels:
    def _posture(self, severities=None, vetoes=None):
        return SimpleNamespace(
            tension_history=[{"severity": s} for s in (severities or [])],
            aegis_vetoes=vetoes or [],
        )

    def test_stable_when_all_zero(self):
        risk = risk_calculator.compute_runtime_risk(posture=self._posture())
        assert risk["level"] == "stable"
        assert risk["score"] < 0.35

    def test_critical_with_max_pressure(self):
        posture = self._posture(
            severities=[1.0, 1.0, 1.0, 1.0, 1.0],
            vetoes=[{}, {}],
        )
        claims = [{} for _ in range(4)]
        compactions = [{"pending_paths": ["a", "b", "c", "d", "e", "f", "g", "h"]}]
        risk = risk_calculator.compute_runtime_risk(
            posture=posture,
            claims=claims,
            compactions=compactions,
            recent_traces=[{"tension_count": 8}],
        )
        assert risk["level"] == "critical"
        assert risk["score"] >= 0.85

    def test_caution_level(self):
        posture = self._posture(severities=[0.5, 0.5])
        risk = risk_calculator.compute_runtime_risk(posture=posture)
        assert risk["level"] in {"caution", "stable", "high"}

    def test_factors_multi_agent(self):
        posture = self._posture()
        claims = [{"agent": "codex"}, {"agent": "claude"}]
        risk = risk_calculator.compute_runtime_risk(posture=posture, claims=claims)
        assert "multi_agent_coordination" in risk["factors"]

    def test_factors_compaction_backlog(self):
        posture = self._posture()
        compactions = [{"pending_paths": ["a", "b", "c", "d"]}]
        risk = risk_calculator.compute_runtime_risk(posture=posture, compactions=compactions)
        assert "compaction_backlog" in risk["factors"]

    def test_factors_dense_trace_tension(self):
        posture = self._posture()
        traces = [{"tension_count": 4}]
        risk = risk_calculator.compute_runtime_risk(posture=posture, recent_traces=traces)
        assert "dense_recent_trace_tension" in risk["factors"]

    def test_inputs_dict_has_all_keys(self):
        posture = self._posture()
        risk = risk_calculator.compute_runtime_risk(posture=posture)
        assert set(risk["inputs"].keys()) == {
            "tension_pressure", "aegis_pressure", "coordination_pressure",
            "backlog_pressure", "trace_pressure",
        }

    def test_no_tension_history_attr(self):
        posture = SimpleNamespace()
        risk = risk_calculator.compute_runtime_risk(posture=posture)
        assert risk["level"] == "stable"


# ── _build_subject_anchor ─────────────────────────────────────────────────────

class TestBuildSubjectAnchor:
    def test_empty_snapshot_returns_empty(self):
        result = risk_calculator._build_subject_anchor({})
        assert result == {}

    def test_full_snapshot(self):
        snapshot = {
            "summary": "Stay focused",
            "stable_vows": ["vow1", "vow2"],
            "durable_boundaries": ["b1"],
            "decision_preferences": ["p1", "p2"],
            "verified_routines": ["r1"],
            "active_threads": ["t1"],
        }
        result = risk_calculator._build_subject_anchor(snapshot)
        assert result["summary"] == "Stay focused"
        assert result["stable_vows"] == ["vow1", "vow2"]
        assert result["active_threads"] == ["t1"]

    def test_limits_to_4_items(self):
        snapshot = {"stable_vows": ["a", "b", "c", "d", "e"]}
        result = risk_calculator._build_subject_anchor(snapshot)
        assert len(result["stable_vows"]) == 4


# ── _build_working_style_anchor ───────────────────────────────────────────────

class TestBuildWorkingStyleAnchor:
    def test_empty_snapshot_returns_empty(self):
        result = risk_calculator._build_working_style_anchor({})
        assert result == {}

    def test_with_decision_preferences(self):
        snapshot = {"decision_preferences": ["prefer-explicit", "avoid-guessing"]}
        result = risk_calculator._build_working_style_anchor(snapshot)
        assert result["decision_preferences"] == ["prefer-explicit", "avoid-guessing"]
        assert "prefs=" in result["summary"]

    def test_with_verified_routines(self):
        snapshot = {"verified_routines": ["run tests", "read file before edit"]}
        result = risk_calculator._build_working_style_anchor(snapshot)
        assert "routines=" in result["summary"]

    def test_prompt_defaults_present(self):
        snapshot = {"decision_preferences": ["x"]}
        result = risk_calculator._build_working_style_anchor(snapshot)
        assert isinstance(result["prompt_defaults"], list)
        assert len(result["prompt_defaults"]) > 0

    def test_receiver_posture_present(self):
        snapshot = {"verified_routines": ["x"]}
        result = risk_calculator._build_working_style_anchor(snapshot)
        assert result["receiver_posture"] == "advisory_apply_not_promote"

    def test_all_empty_fields_returns_empty(self):
        snapshot = {"summary": "", "decision_preferences": [], "verified_routines": []}
        result = risk_calculator._build_working_style_anchor(snapshot)
        assert result == {}

    def test_base_summary_fallback(self):
        snapshot = {"summary": "base summary"}
        result = risk_calculator._build_working_style_anchor(snapshot)
        assert result["summary"] == "base summary"


# ── _build_evidence_readout_posture ───────────────────────────────────────────

class TestBuildEvidenceReadoutPosture:
    def test_has_required_keys(self):
        result = risk_calculator._build_evidence_readout_posture()
        assert "summary_text" in result
        assert "classification_counts" in result
        assert "lanes" in result
        assert "receiver_rule" in result

    def test_classification_counts_correct(self):
        result = risk_calculator._build_evidence_readout_posture()
        counts = result["classification_counts"]
        assert counts["tested"] == 2
        assert counts["runtime_present"] == 1
        assert counts["descriptive_only"] == 1
        assert counts["document_backed"] == 1

    def test_lanes_is_list_of_5(self):
        result = risk_calculator._build_evidence_readout_posture()
        assert len(result["lanes"]) == 5


# ── _run_git_command ──────────────────────────────────────────────────────────

class TestRunGitCommand:
    def test_successful_command(self, monkeypatch, tmp_path):
        class _Completed:
            returncode = 0
            stdout = "main\n"
        monkeypatch.setattr(risk_calculator.subprocess, "run", lambda cmd, **kw: _Completed())
        result = risk_calculator._run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=tmp_path)
        assert result == "main"

    def test_nonzero_exit_returns_none(self, monkeypatch, tmp_path):
        class _Completed:
            returncode = 1
            stdout = ""
        monkeypatch.setattr(risk_calculator.subprocess, "run", lambda cmd, **kw: _Completed())
        result = risk_calculator._run_git_command(["git", "status"], cwd=tmp_path)
        assert result is None

    def test_file_not_found_returns_none(self, monkeypatch, tmp_path):
        def _raise(*args, **kwargs):
            raise FileNotFoundError("git not found")
        monkeypatch.setattr(risk_calculator.subprocess, "run", _raise)
        result = risk_calculator._run_git_command(["git", "rev-parse", "HEAD"], cwd=tmp_path)
        assert result is None

    def test_os_error_returns_none(self, monkeypatch, tmp_path):
        def _raise(*args, **kwargs):
            raise OSError("permission denied")
        monkeypatch.setattr(risk_calculator.subprocess, "run", _raise)
        result = risk_calculator._run_git_command(["git", "log"], cwd=tmp_path)
        assert result is None

    def test_strips_trailing_newlines(self, monkeypatch, tmp_path):
        class _Completed:
            returncode = 0
            stdout = "abc1234\r\n"
        monkeypatch.setattr(risk_calculator.subprocess, "run", lambda cmd, **kw: _Completed())
        result = risk_calculator._run_git_command(["git", "rev-parse", "--short", "HEAD"], cwd=tmp_path)
        assert result == "abc1234"


# ── _build_repo_progress_snapshot ────────────────────────────────────────────

class TestBuildRepoProgressSnapshot:
    def _fake_run(self, responses):
        class _Completed:
            def __init__(self, stdout, returncode=0):
                self.stdout = stdout
                self.returncode = returncode

        def _run(command, **kwargs):
            key = tuple(command)
            if key not in responses:
                return _Completed("", returncode=1)
            return _Completed(responses[key])

        return _run

    def test_unavailable_when_git_fails(self, monkeypatch, tmp_path):
        def _raise(*args, **kwargs):
            raise FileNotFoundError
        monkeypatch.setattr(risk_calculator.subprocess, "run", _raise)
        snap = risk_calculator._build_repo_progress_snapshot(repo_root=tmp_path)
        assert snap["available"] is False

    def test_available_with_clean_repo(self, monkeypatch, tmp_path):
        responses = {
            ("git", "rev-parse", "--abbrev-ref", "HEAD"): "main\n",
            ("git", "rev-parse", "--short", "HEAD"): "abc1234\n",
            ("git", "status", "--short"): "",
        }
        monkeypatch.setattr(risk_calculator.subprocess, "run", self._fake_run(responses))
        snap = risk_calculator._build_repo_progress_snapshot(repo_root=tmp_path)
        assert snap["available"] is True
        assert snap["dirty_count"] == 0
        assert snap["path_preview"] == []

    def test_limits_path_preview_to_5(self, monkeypatch, tmp_path):
        status = "\n".join(f" M file{i}.py" for i in range(10))
        responses = {
            ("git", "rev-parse", "--abbrev-ref", "HEAD"): "main\n",
            ("git", "rev-parse", "--short", "HEAD"): "abc\n",
            ("git", "status", "--short"): status,
        }
        monkeypatch.setattr(risk_calculator.subprocess, "run", self._fake_run(responses))
        snap = risk_calculator._build_repo_progress_snapshot(repo_root=tmp_path)
        assert len(snap["path_preview"]) <= 5


# ── build_project_memory_summary — edge cases ─────────────────────────────────

class TestBuildProjectMemorySummaryEdgeCases:
    def _posture(self):
        return SimpleNamespace(tension_history=[], aegis_vetoes=[])

    def _stub_repo(self, monkeypatch, available=False):
        monkeypatch.setattr(
            risk_calculator,
            "_build_repo_progress_snapshot",
            lambda repo_root=None: {"available": available, "branch": "", "head": "", "dirty_count": 0, "path_preview": []},
        )

    def test_empty_everything_has_evidence_readout_in_summary(self, monkeypatch):
        self._stub_repo(monkeypatch)
        summary = risk_calculator.build_project_memory_summary(posture=self._posture())
        # evidence_readout_posture always contributes a summary_text line
        assert "evidence=" in summary["summary_text"]

    def test_deduplicates_pending_paths_from_claims_and_compactions(self, monkeypatch):
        self._stub_repo(monkeypatch)
        summary = risk_calculator.build_project_memory_summary(
            posture=self._posture(),
            claims=[{"paths": ["tonesoul/foo.py"]}],
            compactions=[{"pending_paths": ["tonesoul/foo.py", "tonesoul/bar.py"]}],
        )
        assert summary["pending_paths"].count("tonesoul/foo.py") == 1

    def test_focus_topics_most_common_first(self, monkeypatch):
        self._stub_repo(monkeypatch)
        traces = [
            {"agent": "a", "topics": ["risk", "risk", "governance"]},
            {"agent": "b", "topics": ["risk"]},
        ]
        summary = risk_calculator.build_project_memory_summary(
            posture=self._posture(), recent_traces=traces
        )
        assert summary["focus_topics"][0] == "risk"

    def test_recent_agents_deduplicated(self, monkeypatch):
        self._stub_repo(monkeypatch)
        traces = [
            {"agent": "codex", "topics": []},
            {"agent": "codex", "topics": []},
            {"agent": "claude", "topics": []},
        ]
        summary = risk_calculator.build_project_memory_summary(
            posture=self._posture(), recent_traces=traces
        )
        assert summary["recent_agents"].count("codex") == 1

    def test_focus_topics_from_posture_when_no_traces(self, monkeypatch):
        self._stub_repo(monkeypatch)
        posture = SimpleNamespace(
            tension_history=[{"topic": "drift"}, {"topic": "axiom"}, {"topic": "council"}],
            aegis_vetoes=[],
        )
        summary = risk_calculator.build_project_memory_summary(posture=posture)
        assert "drift" in summary["focus_topics"]

    def test_routing_summary_appended_to_result(self, monkeypatch):
        self._stub_repo(monkeypatch)
        routing = {"total_events": 3, "summary_text": "routing_note"}
        summary = risk_calculator.build_project_memory_summary(
            posture=self._posture(), routing_summary=routing
        )
        assert summary.get("routing_summary") == routing
