from __future__ import annotations

import pytest

from tonesoul.tonebridge.entropy_engine import (
    AlertType,
    EntropyAlert,
    EntropyEngine,
    EntropyLevel,
    EntropyState,
    create_entropy_engine,
)


def test_entropy_alert_to_dict_serializes_enum_and_timestamp() -> None:
    alert = EntropyAlert(
        alert_type=AlertType.COMMITMENT_OVERLOAD,
        severity=0.7,
        message="too many commitments",
        turn_index=3,
    )

    payload = alert.to_dict()

    assert payload["type"] == "commitment_overload"
    assert payload["severity"] == 0.7
    assert payload["turn_index"] == 3
    assert payload["timestamp"]


def test_entropy_state_to_dict_rounds_values_and_embeds_alerts() -> None:
    state = EntropyState(
        level=EntropyLevel.LOW,
        entropy_score=0.4444,
        commitment_count=4,
        active_constraints=2,
        trajectory_spread=0.3333,
        alerts=[
            EntropyAlert(
                alert_type=AlertType.REPETITION_DETECTED,
                severity=0.5,
                message="repeat",
                turn_index=2,
            )
        ],
    )

    payload = state.to_dict()

    assert payload["level"] == "low"
    assert payload["entropy_score"] == 0.444
    assert payload["trajectory_spread"] == 0.333
    assert payload["alerts"][0]["type"] == "repetition_detected"


def test_calculate_entropy_score_penalizes_commitments_trajectory_and_violations() -> None:
    engine = EntropyEngine()

    score = engine._calculate_entropy_score(
        commitment_count=5,
        trajectory_spread=0.1,
        has_violations=True,
    )

    assert score == pytest.approx(0.0)


def test_classify_entropy_level_thresholds() -> None:
    engine = EntropyEngine()

    assert engine._classify_entropy_level(0.8) is EntropyLevel.HIGH
    assert engine._classify_entropy_level(0.6) is EntropyLevel.NORMAL
    assert engine._classify_entropy_level(0.4) is EntropyLevel.LOW
    assert engine._classify_entropy_level(0.2) is EntropyLevel.CRITICAL


def test_calculate_trajectory_spread_uses_last_five_topics() -> None:
    engine = EntropyEngine()

    assert engine._calculate_trajectory_spread(["a"]) == 1.0
    assert engine._calculate_trajectory_spread(["a", "a", "a", "a", "b", "c"]) == 0.6


def test_detect_repetition_tracks_recent_hashes() -> None:
    engine = EntropyEngine()

    assert engine._detect_repetition("same response") is False
    assert engine._detect_repetition("other response") is False
    assert engine._detect_repetition("same response") is True


def test_add_commitment_and_add_topic_record_state() -> None:
    engine = EntropyEngine()

    engine.add_commitment({"content": "boundary"})
    engine.add_topic("topic-a")

    assert engine._commitment_history[0]["content"] == "boundary"
    assert engine._commitment_history[0]["turn"] == 0
    assert engine._topic_history == ["topic-a"]


def test_check_constraint_violation_detects_contradiction(monkeypatch) -> None:
    engine = EntropyEngine()
    pair = next(
        item
        for item in EntropyEngine.check_constraint_violation.__code__.co_consts
        if isinstance(item, tuple) and len(item) == 5
    )[0]
    positive, negative = pair

    violations = engine.check_constraint_violation(
        f"topic {negative}",
        [{"content": f"topic {positive}"}],
    )

    assert violations


def test_analyze_reports_commitment_overload_and_repetition_alerts() -> None:
    engine = EntropyEngine()

    first = engine.analyze("same answer", [], "topic-a")
    second = engine.analyze(
        "same answer",
        [{"type": "boundary"}] * 4,
        "topic-a",
    )

    assert first.level is EntropyLevel.HIGH
    assert second.commitment_count == 4
    alert_types = {alert.alert_type for alert in second.alerts}
    assert AlertType.COMMITMENT_OVERLOAD in alert_types
    assert AlertType.REPETITION_DETECTED in alert_types
    assert second.active_constraints == 4


def test_analyze_reports_trajectory_narrowing_and_constraint_violation(monkeypatch) -> None:
    engine = EntropyEngine()
    monkeypatch.setattr(
        engine, "check_constraint_violation", lambda *_args, **_kwargs: ["violation"]
    )

    engine.analyze("response-1", [], "topic-a")
    engine.analyze("response-2", [], "topic-a")
    engine.analyze("response-3", [], "topic-a")
    engine.analyze("response-4", [], "topic-a")
    state = engine.analyze("response-5", [], "topic-a", past_commitments=[{"content": "x"}])

    alert_types = {alert.alert_type for alert in state.alerts}
    assert AlertType.TRAJECTORY_NARROWING in alert_types
    assert AlertType.CONSTRAINT_VIOLATION in alert_types
    assert state.level is EntropyLevel.NORMAL
    assert state.entropy_score == pytest.approx(0.6)


def test_get_entropy_summary_empty_and_nonempty() -> None:
    engine = EntropyEngine()

    empty_summary = engine.get_entropy_summary()
    engine.analyze("response", [{"type": "boundary"}], "topic-a")
    filled_summary = engine.get_entropy_summary()

    assert empty_summary
    assert "score=" in filled_summary


def test_reset_clears_internal_state() -> None:
    engine = EntropyEngine()
    engine.analyze("response", [{"type": "boundary"}], "topic-a")

    engine.reset()

    assert engine._commitment_history == []
    assert engine._topic_history == []
    assert engine._response_hashes == []
    assert engine._alerts == []
    assert engine._current_turn == 0


def test_create_entropy_engine_returns_engine_instance() -> None:
    assert isinstance(create_entropy_engine(), EntropyEngine)
