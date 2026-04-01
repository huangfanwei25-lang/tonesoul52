from __future__ import annotations

from types import SimpleNamespace

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
