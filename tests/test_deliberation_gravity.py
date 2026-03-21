from __future__ import annotations

from tonesoul.deliberation.gravity import SemanticGravity
from tonesoul.deliberation.types import (
    DeliberationContext,
    PerspectiveType,
    SynthesisType,
    TensionZone,
    ViewPoint,
)


def _context(**overrides) -> DeliberationContext:
    base = {
        "user_input": "Help me reason through this.",
        "tone_strength": 0.5,
        "resonance_state": "resonance",
        "loop_detected": False,
    }
    base.update(overrides)
    return DeliberationContext(**base)


def _vp(
    perspective: PerspectiveType,
    response: str,
    confidence: float,
    *,
    concerns: list[str] | None = None,
    safety_risk: float = 0.0,
    veto_triggered: bool = False,
) -> ViewPoint:
    return ViewPoint(
        perspective=perspective,
        reasoning=f"{perspective.value} reasoning",
        proposed_response=response,
        confidence=confidence,
        concerns=concerns or [],
        safety_risk=safety_risk,
        veto_triggered=veto_triggered,
    )


def test_gravity_synthesize_basic() -> None:
    gravity = SemanticGravity()
    viewpoints = [
        _vp(PerspectiveType.MUSE, "muse response", 0.8),
        _vp(PerspectiveType.LOGOS, "logos response", 0.7),
        _vp(PerspectiveType.AEGIS, "aegis response", 0.75, concerns=["boundary"]),
    ]

    result = gravity.synthesize(viewpoints, _context(), deliberation_time_ms=12.5)

    assert result.synthesis_type == SynthesisType.WEIGHTED_FUSION
    assert result.response
    assert result.viewpoints == viewpoints
    assert result.deliberation_time_ms == 12.5


def test_gravity_weighs_perspectives() -> None:
    gravity = SemanticGravity()
    viewpoints = [
        _vp(PerspectiveType.MUSE, "muse response", 0.8),
        _vp(PerspectiveType.LOGOS, "logos response", 0.8),
        _vp(PerspectiveType.AEGIS, "aegis response", 0.4),
    ]
    context = _context(tone_strength=0.9, resonance_state="tension", loop_detected=True)

    result = gravity.synthesize(viewpoints, context)

    assert result.dominant_voice == PerspectiveType.LOGOS
    assert result.weights.logos > result.weights.muse
    assert result.response.startswith("logos response")


def test_gravity_handles_empty_input() -> None:
    gravity = SemanticGravity()

    result = gravity.synthesize([], _context())

    assert result.response == ""
    assert result.viewpoints == []
    assert result.dominant_voice is None


def test_gravity_handles_single_voice() -> None:
    gravity = SemanticGravity()
    viewpoint = _vp(PerspectiveType.MUSE, "single voice", 0.95)

    result = gravity.synthesize([viewpoint], _context())

    assert result.synthesis_type == SynthesisType.UNANIMOUS
    assert result.response == "single voice"
    assert result.dominant_voice == PerspectiveType.MUSE


def test_gravity_guardian_override() -> None:
    gravity = SemanticGravity()
    viewpoints = [
        _vp(PerspectiveType.MUSE, "muse response", 0.9),
        _vp(PerspectiveType.LOGOS, "logos response", 0.9),
        _vp(
            PerspectiveType.AEGIS,
            "blocked by guardian",
            0.9,
            safety_risk=0.9,
            veto_triggered=True,
        ),
    ]

    result = gravity.synthesize(viewpoints, _context())

    assert result.synthesis_type == SynthesisType.GUARDIAN_OVERRIDE
    assert result.response == "blocked by guardian"
    assert result.dominant_voice == PerspectiveType.AEGIS


def test_gravity_conflict_resolution() -> None:
    gravity = SemanticGravity()
    viewpoints = [
        _vp(PerspectiveType.MUSE, "metaphor response", 0.95),
        _vp(PerspectiveType.LOGOS, "logic response", 0.4),
        _vp(PerspectiveType.AEGIS, "safety response", 0.8, safety_risk=0.6),
    ]

    result = gravity.synthesize(viewpoints, _context())

    assert result.synthesis_type == SynthesisType.WEIGHTED_FUSION
    assert result.tensions
    assert result.tension_zone is not None


def test_gravity_semantic_field_conservation() -> None:
    gravity = SemanticGravity()
    viewpoints = [
        _vp(PerspectiveType.MUSE, "metaphor bridge", 0.82),
        _vp(PerspectiveType.LOGOS, "evidence spine", 0.81),
        _vp(PerspectiveType.AEGIS, "guardrail note", 0.4),
    ]
    context = _context(tone_strength=0.8, resonance_state="tension", loop_detected=True)

    result = gravity.synthesize(viewpoints, context)

    assert result.response.startswith("evidence spine")
    assert "metaphor bridge" in result.response


def test_gravity_tension_preserved() -> None:
    gravity = SemanticGravity()
    viewpoints = [
        _vp(PerspectiveType.MUSE, "muse response", 0.9),
        _vp(PerspectiveType.LOGOS, "logos response", 0.5),
    ]

    result = gravity.synthesize(viewpoints, _context())

    assert result.tensions
    assert result.tension_zone == TensionZone.SWEET_SPOT
    assert result.calculation_note


def test_gravity_deterministic() -> None:
    gravity = SemanticGravity()
    viewpoints = [
        _vp(PerspectiveType.MUSE, "muse response", 0.82),
        _vp(PerspectiveType.LOGOS, "logos response", 0.79),
        _vp(PerspectiveType.AEGIS, "aegis response", 0.65),
    ]
    context = _context(tone_strength=0.8, resonance_state="tension", loop_detected=True)

    left = gravity.synthesize(viewpoints, context)
    right = gravity.synthesize(viewpoints, context)

    assert left.response == right.response
    assert left.synthesis_type == right.synthesis_type
    assert left.dominant_voice == right.dominant_voice
    assert left.weights.to_dict() == right.weights.to_dict()
    assert [t.to_dict() for t in left.tensions] == [t.to_dict() for t in right.tensions]


def test_gravity_output_structure() -> None:
    gravity = SemanticGravity()
    viewpoints = [
        _vp(PerspectiveType.MUSE, "muse response", 0.82),
        _vp(PerspectiveType.LOGOS, "logos response", 0.79),
        _vp(PerspectiveType.AEGIS, "aegis response", 0.65),
    ]

    payload = gravity.synthesize(viewpoints, _context()).to_api_response()

    assert payload["response"]
    assert {"type", "dominant_voice", "weights"} <= set(payload["synthesis"])
    assert "internal_debate" in payload
    assert "tensions" in payload
    assert "meta" in payload
    assert "decision_matrix" in payload
    assert "next_moves" in payload
    assert "tension_zone" in payload


def test_gravity_graceful_on_exception(monkeypatch) -> None:
    gravity = SemanticGravity()
    viewpoints = [
        _vp(PerspectiveType.MUSE, "muse response", 0.91),
        _vp(PerspectiveType.LOGOS, "logos response", 0.7),
    ]

    monkeypatch.setattr(
        gravity,
        "_weighted_merge",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    result = gravity.synthesize(viewpoints, _context())

    assert result.response == "muse response"
    assert result.dominant_voice == PerspectiveType.MUSE
    assert result.tensions == []
