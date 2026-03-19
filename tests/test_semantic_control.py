from __future__ import annotations

import pytest

from tonesoul.semantic_control import (
    Coupler,
    LambdaObserver,
    LambdaState,
    SemanticController,
    SemanticTension,
    SemanticZone,
    cosine_similarity,
    get_zone,
)


def test_semantic_tension_from_vectors_basic() -> None:
    tension = SemanticTension.from_vectors([1.0, 0.0, 0.0], [1.0, 0.0, 0.0])

    assert tension.delta_s == 0.0
    assert tension.delta_sigma == 0.0
    assert tension.zone == SemanticZone.SAFE
    assert tension.to_dict()["zone"] == "safe"


def test_semantic_tension_from_estimate_weighted_average() -> None:
    tension = SemanticTension.from_estimate(0.8, 0.5, 0.0)

    assert tension.delta_s == 0.45
    assert tension.zone == SemanticZone.TRANSIT


def test_semantic_tension_from_tonesoul_distance_clamps_to_one() -> None:
    tension = SemanticTension.from_tonesoul_distance({"mean": 1.7})

    assert tension.delta_s == 1.0
    assert tension.zone == SemanticZone.DANGER


def test_cosine_similarity_raises_on_length_mismatch() -> None:
    with pytest.raises(ValueError):
        cosine_similarity([1.0, 0.0], [1.0])


def test_get_zone_boundary_values() -> None:
    assert get_zone(0.39) == SemanticZone.SAFE
    assert get_zone(0.40) == SemanticZone.TRANSIT
    assert get_zone(0.60) == SemanticZone.RISK
    assert get_zone(0.85) == SemanticZone.DANGER


def test_coupler_compute_tracks_hysteresis_direction() -> None:
    coupler = Coupler()

    first = coupler.compute(0.2)
    second = coupler.compute(0.1)

    assert first["Phi"] < 0
    assert second["Phi"] > 0
    assert len(coupler.history) == 2
    assert second["prog"] == 0.1


def test_coupler_reset_clears_state() -> None:
    coupler = Coupler()
    coupler.compute(0.4)

    coupler.reset()

    assert coupler.history == []
    assert coupler.prev_delta_s == 0.0
    assert coupler.prev_alt == 1


def test_lambda_observer_transition_sequence() -> None:
    observer = LambdaObserver()

    states = [
        observer.observe(0.5),
        observer.observe(0.5),
        observer.observe(0.7),
    ]

    assert states == [
        LambdaState.CONVERGENT,
        LambdaState.RECURSIVE,
        LambdaState.CHAOTIC,
    ]


def test_lambda_observer_reset_clears_history() -> None:
    observer = LambdaObserver()
    observer.observe(0.4)
    observer.observe(0.4)

    observer.reset()

    assert observer.history == []


def test_semantic_controller_process_returns_structure() -> None:
    controller = SemanticController()

    result = controller.process([1.0, 0.0, 0.0], [1.0, 0.0, 0.0])

    assert result["tension"]["zone"] == "safe"
    assert result["coupler"]["prog"] == 0.1
    assert result["lambda_state"] == "convergent"
    assert result["memory_action"] == "record_exemplar"
    assert result["bridge_allowed"] is True
    assert "timestamp" in result


def test_semantic_controller_process_from_tonesoul_distance() -> None:
    controller = SemanticController()

    result = controller.process_from_tonesoul({"mean": 0.95})

    assert result["tension"]["delta_s"] == 0.95
    assert result["tension"]["zone"] == "danger"
    assert result["memory_action"] == "record_hard"


def test_semantic_controller_reset_clears_internal_state() -> None:
    controller = SemanticController()
    controller.process([1.0, 0.0, 0.0], [0.2, 0.8, 0.0])

    controller.reset()

    assert controller.coupler.history == []
    assert controller.observer.history == []
    assert controller.memory_triggers == []
