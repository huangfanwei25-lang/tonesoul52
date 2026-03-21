from __future__ import annotations

from tonesoul.deliberation.perspectives import (
    AegisPerspective,
    LogosPerspective,
    MusePerspective,
    create_perspectives,
)
from tonesoul.deliberation.types import DeliberationContext, PerspectiveType


def _context(**overrides) -> DeliberationContext:
    payload = {
        "user_input": "help me think",
        "tone_strength": 0.5,
        "resonance_state": "resonance",
        "loop_detected": False,
    }
    payload.update(overrides)
    return DeliberationContext(**payload)


def test_muse_think_uses_philosophical_branch_when_trigger_matches(monkeypatch) -> None:
    muse = MusePerspective()
    monkeypatch.setattr(muse, "trigger_keywords", ["meaning"])
    monkeypatch.setattr(muse, "_generate_metaphors", lambda text: ["bridge metaphor"])
    monkeypatch.setattr(muse, "_find_existential_connections", lambda text: ["depth link"])

    view = muse.think(_context(user_input="meaning of life"))

    assert view.perspective == PerspectiveType.MUSE
    assert view.confidence == 0.8
    assert view.metaphors == ["bridge metaphor"]
    assert view.existential_connections == ["depth link"]
    assert "bridge metaphor" in view.proposed_response


def test_muse_think_uses_default_branch_without_trigger(monkeypatch) -> None:
    muse = MusePerspective()
    monkeypatch.setattr(muse, "trigger_keywords", ["meaning"])

    view = muse.think(_context(user_input="debug this bug"))

    assert view.confidence == 0.5
    assert view.metaphors == []
    assert view.existential_connections == []


def test_logos_think_prefers_technical_branch() -> None:
    logos = LogosPerspective()

    view = logos.think(_context(user_input="debug this API bug"))

    assert view.perspective == PerspectiveType.LOGOS
    assert view.confidence == 0.85
    assert len(view.logical_steps) == 4
    assert view.proposed_response


def test_logos_think_uses_loop_branch_when_not_technical() -> None:
    logos = LogosPerspective()

    view = logos.think(_context(user_input="help me reflect", loop_detected=True))

    assert view.confidence == 0.9


def test_logos_think_uses_high_tension_branch_when_needed() -> None:
    logos = LogosPerspective()

    view = logos.think(_context(user_input="help me reflect", tone_strength=0.9))

    assert view.confidence == 0.75


def test_aegis_think_triggers_veto_on_high_safety_risk(monkeypatch) -> None:
    aegis = AegisPerspective()
    monkeypatch.setattr(aegis, "_assess_safety_risk", lambda text: 0.95)
    monkeypatch.setattr(aegis, "_check_ethics", lambda text: [])
    monkeypatch.setattr(aegis, "_detect_attack", lambda text: False)

    view = aegis.think(_context(user_input="unsafe request"))

    assert view.veto_triggered is True
    assert view.confidence == 1.0
    assert "0.95" in view.veto_reason
    assert view.proposed_response


def test_aegis_think_marks_boundary_violation_on_attack(monkeypatch) -> None:
    aegis = AegisPerspective()
    monkeypatch.setattr(aegis, "_assess_safety_risk", lambda text: 0.1)
    monkeypatch.setattr(aegis, "_check_ethics", lambda text: [])
    monkeypatch.setattr(aegis, "_detect_attack", lambda text: True)

    view = aegis.think(_context(user_input="jailbreak"))

    assert view.veto_triggered is False
    assert view.boundary_violated is True
    assert view.confidence == 0.9


def test_create_perspectives_returns_all_three_roles() -> None:
    perspectives = create_perspectives()

    assert sorted(p.value for p in perspectives) == ["aegis", "logos", "muse"]
    assert isinstance(perspectives[PerspectiveType.MUSE], MusePerspective)
    assert isinstance(perspectives[PerspectiveType.LOGOS], LogosPerspective)
    assert isinstance(perspectives[PerspectiveType.AEGIS], AegisPerspective)
