from __future__ import annotations

import json
from pathlib import Path

import pytest

from tonesoul.error_event import ErrorLedger
from tonesoul.escalation import (
    decide_escalation,
    decision_mode_from_context,
    load_drift_metrics,
    record_escalation,
)


def test_decision_mode_from_context_defaults_normal() -> None:
    assert decision_mode_from_context({}) == "normal"
    assert decision_mode_from_context({"time_island": {}}) == "normal"


def test_decision_mode_from_context_extracts_kairos_mode() -> None:
    context = {"time_island": {"kairos": {"decision_mode": "lockdown"}}}

    assert decision_mode_from_context(context) == "lockdown"


def test_load_drift_metrics_returns_defaults_for_missing_path(tmp_path: Path) -> None:
    metrics = load_drift_metrics(str(tmp_path / "missing.json"))

    assert metrics == {
        "available": False,
        "count": 0,
        "max_delta_norm": None,
        "avg_delta_norm": None,
    }


def test_load_drift_metrics_computes_summary(tmp_path: Path) -> None:
    path = tmp_path / "nodes.json"
    path.write_text(
        json.dumps(
            {
                "nodes": [
                    {"drift": {"delta_norm": 0.4}},
                    {"drift": {"delta_norm": 0.8}},
                    {"drift": {}},
                ]
            }
        ),
        encoding="utf-8",
    )

    metrics = load_drift_metrics(str(path))

    assert metrics["available"] is True
    assert metrics["count"] == 2
    assert metrics["max_delta_norm"] == 0.8
    assert metrics["avg_delta_norm"] == pytest.approx(0.6)


def test_decide_escalation_quarantines_on_poav_breach() -> None:
    result = decide_escalation(0.4, 0.5, None, 0.7, "normal")

    assert result["decision"] == "quarantine"
    assert "poav_below_threshold" in result["reasons"]


def test_decide_escalation_jumps_on_drift_without_lockdown() -> None:
    result = decide_escalation(0.8, 0.5, 0.9, 0.7, "normal")

    assert result["decision"] == "jump"
    assert result["reasons"] == ["drift_above_threshold"]


def test_decide_escalation_returns_none_when_clean() -> None:
    result = decide_escalation(0.8, 0.5, 0.2, 0.7, "normal")

    assert result == {"decision": "none", "reasons": []}


def test_record_escalation_returns_none_for_non_action(tmp_path: Path) -> None:
    assert (
        record_escalation(
            "none",
            [],
            {"poav": 0.9},
            str(tmp_path / "ledger.jsonl"),
            "normal",
            "run-001",
        )
        is None
    )
    assert record_escalation("jump", ["reason"], {"poav": 0.3}, None, "normal", "run-001") is None


def test_record_escalation_writes_error_ledger(tmp_path: Path) -> None:
    ledger_path = tmp_path / "logs" / "escalation.jsonl"

    event_id = record_escalation(
        "jump",
        ["drift_above_threshold"],
        {"max_delta_norm": 0.9},
        str(ledger_path),
        "normal",
        "run-002",
    )
    ledger = ErrorLedger(str(ledger_path))

    assert event_id is not None
    assert ledger_path.exists()
    assert len(ledger.events) == 1
    assert ledger.events[0].behavior == "Escalation: jump"
    assert ledger.events[0].mode_at_time == "normal"
