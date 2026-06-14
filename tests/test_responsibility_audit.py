"""Axiom 2 (Responsibility Threshold) — audit_log_threshold is now a live consumer.

Pins that high-stakes traces carry an explicit ``responsibility_audit`` marker
(risk > audit_log_threshold, or an integrity event), and that the marker enters
the immutable committed trace — so A2's "risk > 0.4 -> immutable audit" is
explicit and queryable, not dead config.
"""

from __future__ import annotations

import json
from pathlib import Path

from tonesoul.governance.responsibility_audit import evaluate_responsibility_audit

# ── pure evaluator ────────────────────────────────────────────────────────────


def test_high_responsibility_risk_requires_audit() -> None:
    out = evaluate_responsibility_audit({"tension_events": [{"severity": 0.7}]})
    assert out["audit_required"] is True
    assert out["responsibility_risk"] == 0.7
    assert any("responsibility_risk" in r for r in out["reasons"])


def test_low_risk_does_not_require_audit() -> None:
    out = evaluate_responsibility_audit({"tension_events": [{"severity": 0.2}]})
    assert out["audit_required"] is False
    assert out["reasons"] == []


def test_threshold_is_read_from_config_by_default() -> None:
    # Default threshold is SOUL.risk.audit_log_threshold (0.4): 0.41 crosses, 0.39 does not.
    assert evaluate_responsibility_audit({"tension_events": [{"severity": 0.41}]})["audit_required"]
    assert not evaluate_responsibility_audit({"tension_events": [{"severity": 0.39}]})[
        "audit_required"
    ]


def test_threshold_override() -> None:
    out = evaluate_responsibility_audit({"tension_events": [{"severity": 0.5}]}, threshold=0.6)
    assert out["audit_required"] is False
    assert out["threshold"] == 0.6


def test_aegis_veto_forces_audit_regardless_of_tension() -> None:
    out = evaluate_responsibility_audit(
        {"tension_events": [{"severity": 0.1}], "aegis_vetoes": [{"type": "memory_poisoning"}]}
    )
    assert out["audit_required"] is True
    assert "aegis_veto_present" in out["reasons"]


def test_vow_violation_forces_audit() -> None:
    out = evaluate_responsibility_audit(
        {"tension_events": [], "vow_events": [{"status": "violation"}]}
    )
    assert out["audit_required"] is True
    assert "vow_violation_present" in out["reasons"]


def test_empty_trace_is_low_stakes() -> None:
    out = evaluate_responsibility_audit({})
    assert out["audit_required"] is False
    assert out["responsibility_risk"] == 0.0


# ── integration: the marker enters the immutable committed trace ───────────────


def test_commit_stamps_responsibility_audit_into_the_chain(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("TONESOUL_MEMORY_EMBEDDER", "hash")
    from tonesoul.runtime_adapter import SessionTrace, commit

    trace = SessionTrace(
        agent="claude-opus-4-8",
        topics=["a2-test"],
        tension_events=[{"severity": 0.8, "type": "high_stakes"}],
    )
    traces_path = tmp_path / "session_traces.jsonl"
    commit(trace, state_path=tmp_path / "governance_state.json", traces_path=traces_path)

    rows = [
        json.loads(line) for line in traces_path.read_text(encoding="utf-8").splitlines() if line
    ]
    mine = [r for r in rows if r.get("session_id") == trace.session_id]
    assert mine, "committed trace not found"
    marker = mine[0].get("responsibility_audit")
    assert marker is not None
    assert marker["audit_required"] is True
    assert marker["axiom"] == 2
    # The marker lives inside the hash-chained (immutable) trace.
    assert "_chain" in mine[0]
