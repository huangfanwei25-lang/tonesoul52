import json

import pytest

from tonesoul.error_event import ErrorEvent, ErrorLedger


def test_error_event_generates_event_id_and_delta_metrics():
    event = ErrorEvent(
        behavior="bad response",
        context="unsafe context",
        tension_before=0.1,
        tension_after=0.5,
        stability_before=0.8,
        stability_after=0.5,
        strategy="tighten validation",
    )

    assert len(event.event_id) == 12
    assert event.tension_delta() == pytest.approx(0.4)
    assert event.stability_delta() == pytest.approx(-0.3)
    assert event.was_harmful() is True


def test_error_event_to_dict_json_and_summary_preserve_content():
    event = ErrorEvent(
        behavior="hallucinated citation",
        context="citation path absent",
        strategy="require evidence",
        strategy_type="learn",
    )

    payload = event.to_dict()
    rendered = json.loads(event.to_json())
    summary = event.summary()

    assert payload["behavior"] == "hallucinated citation"
    assert rendered["strategy"] == "require evidence"
    assert event.event_id in summary
    assert "hallucinated citation"[:30] in summary


def test_error_ledger_record_reload_and_queries(tmp_path):
    ledger_path = tmp_path / "error_ledger.jsonl"
    ledger = ErrorLedger(str(ledger_path))
    harmful = ErrorEvent(
        behavior="harmful output",
        context="unsafe boundary",
        tension_before=0.1,
        tension_after=0.6,
        stability_before=0.9,
        stability_after=0.5,
        strategy="learn",
        strategy_type="learn",
    )
    benign = ErrorEvent(
        behavior="minor issue",
        context="formatting only",
        tension_before=0.2,
        tension_after=0.25,
        stability_before=0.9,
        stability_after=0.85,
        strategy="adjust",
        strategy_type="adjust",
    )

    ledger.record(harmful)
    ledger.record(benign)
    reloaded = ErrorLedger(str(ledger_path))

    assert len(reloaded.events) == 2
    assert [event.event_id for event in reloaded.find_by_strategy_type("learn")] == [
        harmful.event_id
    ]
    assert [event.event_id for event in reloaded.find_harmful()] == [harmful.event_id]


def test_error_ledger_pattern_analysis_reports_distributions_and_insight(tmp_path):
    ledger = ErrorLedger(str(tmp_path / "error_ledger.jsonl"))
    ledger.record(
        ErrorEvent(
            behavior="harmful output",
            context="unsafe risk escalation",
            behavior_type="response",
            tension_before=0.2,
            tension_after=0.6,
            strategy="learn",
            strategy_type="learn",
        )
    )
    ledger.record(
        ErrorEvent(
            behavior="state mismatch",
            context="unsafe boundary condition",
            behavior_type="action",
            tension_before=0.1,
            tension_after=0.15,
            strategy="avoid",
            strategy_type="avoid",
        )
    )

    analysis = ledger.pattern_analysis()

    assert analysis["total"] == 2
    assert analysis["harmful_count"] == 1
    assert analysis["behavior_distribution"] == {"response": 1, "action": 1}
    assert analysis["strategy_distribution"] == {"learn": 1, "avoid": 1}
    assert "unsafe" in analysis["insight"]


def test_error_ledger_pattern_analysis_handles_empty_ledger(tmp_path):
    ledger = ErrorLedger(str(tmp_path / "error_ledger.jsonl"))

    assert ledger.pattern_analysis() == {"total": 0, "patterns": []}


# ── ErrorEvent boundary conditions ────────────────────────────────────────────


def test_was_harmful_false_when_deltas_within_thresholds():
    event = ErrorEvent(
        behavior="minor",
        context="ctx",
        tension_before=0.1,
        tension_after=0.25,  # delta = 0.15 — NOT > 0.2
        stability_before=0.9,
        stability_after=0.75,  # delta = -0.15 — NOT < -0.2
    )
    assert event.was_harmful() is False


def test_was_harmful_triggered_by_stability_drop():
    event = ErrorEvent(
        behavior="issue",
        context="ctx",
        tension_before=0.3,
        tension_after=0.4,  # delta = 0.1 — safe
        stability_before=0.9,
        stability_after=0.65,  # delta = -0.25 — harmful
    )
    assert event.was_harmful() is True


def test_event_id_uses_provided_value():
    event = ErrorEvent(behavior="b", context="c", event_id="custom-id-00")
    assert event.event_id == "custom-id-00"


def test_error_event_default_fields():
    event = ErrorEvent(behavior="b", context="c")
    assert event.behavior_type == "response"
    assert event.strategy_type == "adjust"
    assert event.reviewed is False
    assert event.fs_delta == {}


# ── ErrorLedger.record return value ──────────────────────────────────────────


def test_record_returns_event_id(tmp_path):
    ledger = ErrorLedger(str(tmp_path / "ledger.jsonl"))
    event = ErrorEvent(behavior="b", context="c")
    returned = ledger.record(event)
    assert returned == event.event_id


# ── _generate_insight with no harmful events ──────────────────────────────────


def test_generate_insight_no_harmful_events(tmp_path):
    ledger = ErrorLedger(str(tmp_path / "ledger.jsonl"))
    ledger.record(
        ErrorEvent(
            behavior="fine output",
            context="routine context",
            tension_before=0.1,
            tension_after=0.15,
        )
    )
    analysis = ledger.pattern_analysis()
    assert analysis["insight"] == "No harmful patterns detected."
