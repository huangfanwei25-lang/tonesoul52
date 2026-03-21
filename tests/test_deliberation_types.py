from __future__ import annotations

from datetime import datetime

from tonesoul.deliberation.types import (
    DeliberationContext,
    DeliberationWeights,
    PerspectiveType,
    SuggestedReply,
    SynthesisType,
    SynthesizedResponse,
    TacticalDecision,
    Tension,
    TensionZone,
    ViewPoint,
)


def test_viewpoint_to_dict_truncates_and_rounds_fields() -> None:
    payload = ViewPoint(
        perspective=PerspectiveType.MUSE,
        reasoning="reasoning",
        proposed_response="x" * 250,
        confidence=0.876,
        concerns=["note"],
        safety_risk=0.333,
        veto_triggered=True,
    ).to_dict()

    assert payload["perspective"] == "muse"
    assert payload["proposed_response"].endswith("...")
    assert len(payload["proposed_response"]) == 203
    assert payload["confidence"] == 0.88
    assert payload["safety_risk"] == 0.33
    assert payload["veto_triggered"] is True


def test_tension_to_dict_serializes_between_pair_and_resolution() -> None:
    payload = Tension(
        between=(PerspectiveType.MUSE, PerspectiveType.LOGOS),
        description="conflict",
        severity=0.876,
        resolution_hint="merge",
    ).to_dict()

    assert payload == {
        "between": ["muse", "logos"],
        "description": "conflict",
        "severity": 0.88,
        "resolution": "merge",
    }


def test_tactical_decision_and_suggested_reply_to_dict() -> None:
    assert TacticalDecision("hidden", "strategy", "effect", "warm").to_dict() == {
        "user_hidden_intent": "hidden",
        "strategy_name": "strategy",
        "intended_effect": "effect",
        "tone_tag": "warm",
    }
    assert SuggestedReply("next", "continue").to_dict() == {"label": "next", "text": "continue"}


def test_deliberation_weights_normalize_and_export() -> None:
    weights = DeliberationWeights(muse=2.0, logos=1.0, aegis=1.0)
    weights.normalize()

    assert weights.to_dict() == {"muse": 0.5, "logos": 0.25, "aegis": 0.25}


def test_synthesized_response_formats_internal_debate_and_api_payload() -> None:
    viewpoint = ViewPoint(
        perspective=PerspectiveType.LOGOS,
        reasoning="reasoning",
        proposed_response="y" * 120,
        confidence=0.91,
        concerns=["clarify"],
    )
    tension = Tension(
        between=(PerspectiveType.MUSE, PerspectiveType.LOGOS),
        description="conflict",
        severity=0.7,
    )
    response = SynthesizedResponse(
        response="final answer",
        synthesis_type=SynthesisType.DOMINANT,
        dominant_voice=PerspectiveType.LOGOS,
        viewpoints=[viewpoint],
        tensions=[tension],
        weights=DeliberationWeights(),
        deliberation_time_ms=12.345,
        timestamp=datetime(2026, 3, 19, 12, 0, 0),
        tactical_decision=TacticalDecision("intent", "strategy", "effect", "warm"),
        suggested_replies=[SuggestedReply("next", "continue")],
        tension_zone=TensionZone.SWEET_SPOT,
        calculation_note="balanced tension",
        rounds_used=1,
    )

    debate = response.get_internal_debate()
    payload = response.to_api_response()

    assert debate["logos"]["proposed"].endswith("...")
    assert payload["synthesis"]["type"] == "dominant"
    assert payload["synthesis"]["dominant_voice"] == "logos"
    assert payload["meta"]["deliberation_time_ms"] == 12.35
    assert payload["decision_matrix"]["strategy_name"] == "strategy"
    assert payload["next_moves"] == [{"label": "next", "text": "continue"}]
    assert payload["tension_zone"] == {
        "zone": "sweet_spot",
        "calculation_note": "balanced tension",
    }
    assert "adaptive_debate" not in payload


def test_deliberation_context_to_dict_truncates_input_and_marks_scenario_envelope() -> None:
    payload = DeliberationContext(
        user_input="z" * 150,
        conversation_history=[{"role": "user"}],
        tone_strength=0.8,
        resonance_state="tension",
        loop_detected=True,
        scenario_envelope={"status": "active"},
    ).to_dict()

    assert payload == {
        "user_input": "z" * 100,
        "history_length": 1,
        "tone_strength": 0.8,
        "resonance_state": "tension",
        "loop_detected": True,
        "scenario_envelope_enabled": True,
        "debate_round": 1,
        "has_prior_viewpoints": False,
    }
