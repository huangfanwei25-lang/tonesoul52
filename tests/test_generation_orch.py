"""Tests for generation_orch execution report helpers."""

from __future__ import annotations

import json
from pathlib import Path

from tonesoul.generation_orch import build_execution_report, record_error_event


def _context() -> dict[str, object]:
    return {
        "context": {
            "task": "analyze runtime posture",
            "objective": "produce a concise execution summary",
        }
    }


def _frame_plan() -> dict[str, object]:
    return {
        "input_hash": "frame-hash",
        "selected_frames": [
            {
                "id": "analysis",
                "score": 4,
                "roles": ["Risk", "Recorder"],
                "governance_roles": ["guardian", "scribe"],
            }
        ],
        "rejected_frames": [
            {
                "id": "execution",
                "score": 0,
                "reason": "score=0",
            }
        ],
        "role_summary": {
            "operational_roles": ["Recorder", "Risk"],
            "governance_roles": ["guardian", "scribe"],
            "max_governance_level": 3,
        },
        "council_summary": {
            "decision": "review",
            "decision_mode": "normal",
            "weighted_score": 0.5,
            "dissent_ratio": 0.25,
            "signals": {
                "risk_roles": ["Risk"],
                "audit_roles": ["Recorder"],
            },
            "votes": [
                {
                    "governance_role": "guardian",
                    "weight": 3,
                    "stance": "review",
                    "score": 0.5,
                }
            ],
        },
    }


def test_build_execution_report_minimal(monkeypatch) -> None:
    monkeypatch.setattr("tonesoul.generation_orch.utc_now", lambda: "2026-03-19T00:00:00Z")
    monkeypatch.setattr("tonesoul.generation_orch.stable_hash", lambda _value: "ctx-hash")

    report = build_execution_report(_context(), frame_plan=None, constraints=None)

    assert "# Execution Report (M3)" in report
    assert "- Generated at: 2026-03-19T00:00:00Z" in report
    assert "- Context hash: ctx-hash" in report
    assert "- Task: analyze runtime posture" in report


def test_build_execution_report_with_frame_plan(monkeypatch) -> None:
    monkeypatch.setattr("tonesoul.generation_orch.utc_now", lambda: "2026-03-19T00:00:00Z")
    monkeypatch.setattr("tonesoul.generation_orch.stable_hash", lambda _value: "ctx-hash")

    report = build_execution_report(
        _context(),
        frame_plan=_frame_plan(),
        constraints="constraint A\nconstraint B",
    )

    assert "## Selected Frames" in report
    assert (
        "- analysis (score=4) roles=['Risk', 'Recorder'] gov_roles=['guardian', 'scribe']" in report
    )
    assert "## Rejected Frames" in report
    assert "## Role Summary" in report
    assert "## Council Summary" in report
    assert "## Constraint Stack Snapshot" in report


def test_build_execution_report_with_error_event(monkeypatch) -> None:
    monkeypatch.setattr("tonesoul.generation_orch.utc_now", lambda: "2026-03-19T00:00:00Z")
    monkeypatch.setattr("tonesoul.generation_orch.stable_hash", lambda _value: "ctx-hash")

    report = build_execution_report(
        _context(),
        frame_plan=None,
        constraints=None,
        error_event_id="err-123",
    )

    assert "- ErrorEvent recorded: err-123" in report


def test_build_execution_report_with_skills(monkeypatch) -> None:
    monkeypatch.setattr("tonesoul.generation_orch.utc_now", lambda: "2026-03-19T00:00:00Z")
    monkeypatch.setattr("tonesoul.generation_orch.stable_hash", lambda _value: "ctx-hash")

    report = build_execution_report(
        _context(),
        frame_plan=None,
        constraints=None,
        skills_applied=[
            {"skill_id": "playwright", "action": "inspect-ui"},
            {"skill_id": "pdf", "action": "summarize-artifact"},
        ],
    )

    assert "## Applied Skills" in report
    assert "- playwright -> inspect-ui" in report
    assert "- pdf -> summarize-artifact" in report


def test_record_error_event_creates_entry(tmp_path: Path) -> None:
    error_event_path = tmp_path / "error_event.json"
    ledger_path = tmp_path / "error_ledger.jsonl"
    error_event_path.write_text(
        json.dumps(
            {
                "behavior": "bad output",
                "context": "runtime confusion",
                "strategy": "tighten contract",
            }
        ),
        encoding="utf-8",
    )

    event_id = record_error_event(str(error_event_path), str(ledger_path))

    ledger_text = ledger_path.read_text(encoding="utf-8")
    assert event_id
    assert "bad output" in ledger_text
    assert "runtime confusion" in ledger_text
