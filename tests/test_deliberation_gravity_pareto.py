from __future__ import annotations

from pathlib import Path

from tonesoul.deliberation.gravity import SemanticGravity
from tonesoul.deliberation.persona_track_record import PersonaTrackRecord
from tonesoul.deliberation.types import DeliberationContext, PerspectiveType, ViewPoint


def _vp(p: PerspectiveType, confidence: float, risk: float) -> ViewPoint:
    return ViewPoint(
        perspective=p,
        reasoning=f"{p.value} reasoning",
        proposed_response=f"{p.value} response",
        confidence=confidence,
        safety_risk=risk,
    )


def test_pareto_frontier_excludes_dominated_viewpoint() -> None:
    gravity = SemanticGravity()
    v1 = _vp(PerspectiveType.MUSE, confidence=0.9, risk=0.1)
    v2 = _vp(PerspectiveType.LOGOS, confidence=0.8, risk=0.3)
    v3 = _vp(PerspectiveType.AEGIS, confidence=0.85, risk=0.2)

    frontier = gravity._pareto_frontier([v1, v2, v3])

    assert v1 in frontier
    assert v3 not in frontier
    assert v2 not in frontier


def test_calculate_weights_applies_pareto_boost_to_frontier() -> None:
    gravity = SemanticGravity()
    context = DeliberationContext(user_input="test")

    # logos is dominated by muse (lower confidence, higher risk)
    muse = _vp(PerspectiveType.MUSE, confidence=0.9, risk=0.1)
    logos = _vp(PerspectiveType.LOGOS, confidence=0.8, risk=0.3)
    aegis = _vp(PerspectiveType.AEGIS, confidence=0.85, risk=0.2)

    weights = gravity.calculate_weights([muse, logos, aegis], context)

    # Muse should receive Pareto boost and dominate Logos in this setup.
    assert weights.muse > weights.logos
    assert weights.aegis < weights.logos


def test_pareto_frontier_keeps_all_when_tradeoff_exists() -> None:
    gravity = SemanticGravity()
    a = _vp(PerspectiveType.MUSE, confidence=0.95, risk=0.5)
    b = _vp(PerspectiveType.LOGOS, confidence=0.75, risk=0.1)
    c = _vp(PerspectiveType.AEGIS, confidence=0.85, risk=0.3)

    frontier = gravity._pareto_frontier([a, b, c])

    # No one strictly dominates everyone else due to confidence/risk trade-offs.
    assert len(frontier) == 3


def test_calculate_weights_applies_persona_track_bias(tmp_path: Path) -> None:
    track = PersonaTrackRecord.create(tmp_path / "ptr.json")
    # Muse historically strong, Logos historically weak
    for _ in range(10):
        track.record_outcome("muse", "approve", resonance_state="resonance")
    for _ in range(10):
        track.record_outcome("logos", "block", resonance_state="resonance")

    gravity = SemanticGravity(track_record=track)
    context = DeliberationContext(user_input="test", resonance_state="resonance")
    muse = _vp(PerspectiveType.MUSE, confidence=0.8, risk=0.2)
    logos = _vp(PerspectiveType.LOGOS, confidence=0.8, risk=0.2)
    aegis = _vp(PerspectiveType.AEGIS, confidence=0.8, risk=0.2)

    weights = gravity.calculate_weights([muse, logos, aegis], context)

    assert weights.muse > weights.logos
