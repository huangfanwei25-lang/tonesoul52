from __future__ import annotations

from types import SimpleNamespace

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
        {"pending_paths": ["tonesoul/runtime_adapter.py", "spec/governance/r_memory_packet_v1.schema.json"]},
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


def test_build_project_memory_summary_aggregates_focus_and_pending_paths() -> None:
    posture = SimpleNamespace(tension_history=[{"topic": "fallback", "severity": 0.4}])
    summary = build_project_memory_summary(
        posture=posture,
        recent_traces=[
            {"agent": "codex", "topics": ["runtime", "risk"]},
            {"agent": "claude", "topics": ["risk", "packet"]},
        ],
        claims=[
            {"task_id": "risk-r", "agent": "codex", "paths": ["tonesoul/runtime_adapter.py"]},
        ],
        compactions=[
            {
                "pending_paths": ["tonesoul/diagnose.py"],
                "carry_forward": ["keep packet readable"],
                "next_action": "wire project memory summary into diagnose",
            }
        ],
    )

    assert summary["focus_topics"][0] == "risk"
    assert "codex" in summary["recent_agents"]
    assert "tonesoul/runtime_adapter.py" in summary["pending_paths"]
    assert summary["carry_forward"] == ["keep packet readable"]
    assert "近期焦點" in summary["summary_text"]
