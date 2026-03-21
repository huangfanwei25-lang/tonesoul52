from __future__ import annotations

from datetime import datetime

from tonesoul.deliberation.adaptive_rounds import (
    MAX_DEBATE_ROUNDS,
    TENSION_HIGH,
    TENSION_LOW,
    aggregate_tension_severity,
    calculate_debate_rounds,
)
from tonesoul.deliberation.types import (
    DeliberationWeights,
    PerspectiveType,
    RoundResult,
    SynthesisType,
    SynthesizedResponse,
    Tension,
    ViewPoint,
)


def _tension(severity: float) -> Tension:
    return Tension(
        between=(PerspectiveType.MUSE, PerspectiveType.LOGOS),
        description="conflict",
        severity=severity,
    )


def _viewpoint() -> ViewPoint:
    return ViewPoint(
        perspective=PerspectiveType.LOGOS,
        reasoning="reasoning",
        proposed_response="structured response",
        confidence=0.8,
    )


def test_aggregate_tension_severity_returns_zero_for_empty_list() -> None:
    assert aggregate_tension_severity([]) == 0.0


def test_aggregate_tension_severity_returns_single_tension_severity() -> None:
    assert aggregate_tension_severity([_tension(0.42)]) == 0.42


def test_aggregate_tension_severity_averages_multiple_tensions() -> None:
    assert aggregate_tension_severity([_tension(0.2), _tension(0.8)]) == 0.5


def test_aggregate_tension_severity_clamps_out_of_range_values() -> None:
    assert aggregate_tension_severity([_tension(-1.0), _tension(2.0)]) == 0.5


def test_calculate_debate_rounds_defaults_to_one_for_empty_tensions() -> None:
    assert calculate_debate_rounds([]) == 1


def test_calculate_debate_rounds_returns_one_below_low_threshold() -> None:
    assert calculate_debate_rounds([_tension(0.1)]) == 1
    assert calculate_debate_rounds([_tension(TENSION_LOW - 0.01)]) == 1


def test_calculate_debate_rounds_returns_two_at_low_threshold_and_mid_band() -> None:
    assert calculate_debate_rounds([_tension(TENSION_LOW)]) == 2
    assert calculate_debate_rounds([_tension(0.5)]) == 2
    assert calculate_debate_rounds([_tension(TENSION_HIGH - 0.01)]) == 2


def test_calculate_debate_rounds_returns_three_at_high_threshold_and_above() -> None:
    assert calculate_debate_rounds([_tension(TENSION_HIGH)]) == MAX_DEBATE_ROUNDS
    assert calculate_debate_rounds([_tension(0.9)]) == MAX_DEBATE_ROUNDS


def test_round_result_to_dict_serializes_nested_fields() -> None:
    round_result = RoundResult(
        round_number=2,
        viewpoints=[_viewpoint()],
        tensions=[_tension(0.7)],
        weights=DeliberationWeights(muse=0.2, logos=0.5, aegis=0.3),
        aggregate_tension=0.7,
    )

    payload = round_result.to_dict()

    assert payload["round_number"] == 2
    assert payload["viewpoints"][0]["perspective"] == "logos"
    assert payload["tensions"][0]["severity"] == 0.7
    assert payload["weights"] == {"muse": 0.2, "logos": 0.5, "aegis": 0.3}
    assert payload["aggregate_tension"] == 0.7


def test_synthesized_response_keeps_round_metadata_on_instance() -> None:
    round_results = [
        RoundResult(round_number=1, aggregate_tension=0.4),
        RoundResult(round_number=2, aggregate_tension=0.2),
    ]
    response = SynthesizedResponse(
        response="final answer",
        synthesis_type=SynthesisType.WEIGHTED_FUSION,
        dominant_voice=PerspectiveType.LOGOS,
        rounds_used=2,
        round_results=round_results,
        timestamp=datetime(2026, 3, 21, 12, 0, 0),
    )

    assert response.rounds_used == 2
    assert response.round_results == round_results


def test_to_api_response_omits_adaptive_debate_for_single_round() -> None:
    payload = SynthesizedResponse(
        response="answer",
        synthesis_type=SynthesisType.DOMINANT,
        dominant_voice=PerspectiveType.LOGOS,
        rounds_used=1,
    ).to_api_response()

    assert "adaptive_debate" not in payload


def test_to_api_response_includes_adaptive_debate_for_multi_round_results() -> None:
    payload = SynthesizedResponse(
        response="answer",
        synthesis_type=SynthesisType.DOMINANT,
        dominant_voice=PerspectiveType.LOGOS,
        rounds_used=2,
        round_results=[
            RoundResult(round_number=1, aggregate_tension=0.6),
            RoundResult(round_number=2, aggregate_tension=0.2),
        ],
    ).to_api_response()

    assert payload["adaptive_debate"] == {
        "rounds_used": 2,
        "tension_per_round": [0.6, 0.2],
    }
