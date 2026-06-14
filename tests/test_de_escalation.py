"""Axiom 7 (reframed) — high tension raises a de-escalation directive.

Pins that high_tension_threshold is now a live consumer for the damping axis:
a high-tension trace carries a de_escalation directive, and the marker enters the
immutable committed trace. (Applying the directive to live output is a separate
referenced->partial step, intentionally not covered here.)
"""

from __future__ import annotations

import json
from pathlib import Path

from tonesoul.governance.de_escalation import evaluate_de_escalation
from tonesoul.soul_config import SOUL


def test_high_tension_raises_directive() -> None:
    out = evaluate_de_escalation({"tension_events": [{"severity": 0.9}]})
    assert out["de_escalation_required"] is True
    assert out["directive"]  # non-empty concrete move
    assert out["axiom"] == 7


def test_low_tension_no_directive() -> None:
    out = evaluate_de_escalation({"tension_events": [{"severity": 0.5}]})
    assert out["de_escalation_required"] is False
    assert out["directive"] == ""


def test_threshold_is_high_tension_threshold_by_default() -> None:
    th = SOUL.tension.high_tension_threshold
    assert evaluate_de_escalation({"tension_events": [{"severity": th + 0.05}]})[
        "de_escalation_required"
    ]
    assert not evaluate_de_escalation({"tension_events": [{"severity": th - 0.05}]})[
        "de_escalation_required"
    ]


def test_threshold_override() -> None:
    out = evaluate_de_escalation({"tension_events": [{"severity": 0.6}]}, threshold=0.5)
    assert out["de_escalation_required"] is True
    assert out["threshold"] == 0.5


def test_empty_trace_no_directive() -> None:
    out = evaluate_de_escalation({})
    assert out["de_escalation_required"] is False
    assert out["peak_tension"] == 0.0


def test_commit_stamps_de_escalation_into_the_chain(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("TONESOUL_MEMORY_EMBEDDER", "hash")
    from tonesoul.runtime_adapter import SessionTrace, commit

    trace = SessionTrace(
        agent="claude-opus-4-8",
        topics=["a7-test"],
        tension_events=[{"severity": 0.9, "type": "high_tension"}],
    )
    traces_path = tmp_path / "session_traces.jsonl"
    commit(trace, state_path=tmp_path / "governance_state.json", traces_path=traces_path)

    rows = [
        json.loads(line) for line in traces_path.read_text(encoding="utf-8").splitlines() if line
    ]
    mine = [r for r in rows if r.get("session_id") == trace.session_id]
    assert mine, "committed trace not found"
    marker = mine[0].get("de_escalation")
    assert marker is not None
    assert marker["de_escalation_required"] is True
    assert marker["axiom"] == 7
    assert "_chain" in mine[0]  # inside the immutable chain
