from __future__ import annotations

import pytest

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


# ── Muse pure helpers ─────────────────────────────────────────────────────────


class TestMuseGenerateMetaphors:
    def _muse(self) -> MusePerspective:
        return MusePerspective()

    def test_no_keywords_returns_empty(self):
        assert self._muse()._generate_metaphors("some unrelated text") == []

    def test_life_keyword_triggers_metaphor(self):
        result = self._muse()._generate_metaphors("生命的旅程")
        assert len(result) >= 1

    def test_meaning_keyword_triggers_metaphor(self):
        result = self._muse()._generate_metaphors("找到意義")
        assert len(result) >= 1

    def test_freedom_keyword_triggers_metaphor(self):
        result = self._muse()._generate_metaphors("自由是什麼")
        assert len(result) >= 1


class TestMuseFindExistentialConnections:
    def _muse(self) -> MusePerspective:
        return MusePerspective()

    def test_no_triggers_returns_empty(self):
        assert self._muse()._find_existential_connections("debug this code") == []

    def test_purpose_keyword_returns_connection(self):
        result = self._muse()._find_existential_connections("什麼是目的？")
        assert len(result) >= 1

    def test_freedom_keyword_returns_sartre(self):
        result = self._muse()._find_existential_connections("自由與選擇")
        assert any("沙特" in c for c in result)


# ── Logos pure helpers ────────────────────────────────────────────────────────


class TestLogosAnalyzeLogically:
    def test_returns_four_steps(self):
        logos = LogosPerspective()
        steps = logos._analyze_logically(_context(user_input="test question"))
        assert len(steps) == 4

    def test_first_step_contains_user_input_fragment(self):
        logos = LogosPerspective()
        steps = logos._analyze_logically(_context(user_input="what is entropy"))
        assert "what is entropy" in steps[0]


class TestLogosExtractDefinitions:
    def test_no_matching_terms_returns_empty(self):
        logos = LogosPerspective()
        assert logos._extract_definitions("debug this code") == {}

    def test_freedom_term_extracted(self):
        logos = LogosPerspective()
        defs = logos._extract_definitions("自由是什麼")
        assert "自由" in defs

    def test_meaning_term_extracted(self):
        logos = LogosPerspective()
        defs = logos._extract_definitions("探索意義")
        assert "意義" in defs


# ── Aegis pure helpers ────────────────────────────────────────────────────────


class TestAegisAssessSafetyRisk:
    def _aegis(self) -> AegisPerspective:
        return AegisPerspective()

    def test_clean_text_returns_zero(self):
        assert self._aegis()._assess_safety_risk("what is the weather") == 0.0

    def test_single_danger_keyword_returns_0_3(self):
        assert self._aegis()._assess_safety_risk("傷害他人") == pytest.approx(0.3)

    def test_multiple_keywords_capped_at_one(self):
        text = "傷害 自殺 殺 死 攻擊 暴力 非法 駭入 破解 詐騙 製造武器"
        assert self._aegis()._assess_safety_risk(text) == pytest.approx(1.0)


class TestAegisCheckEthics:
    def _aegis(self) -> AegisPerspective:
        return AegisPerspective()

    def test_clean_text_returns_empty(self):
        assert self._aegis()._check_ethics("help me code") == []

    def test_fraud_keyword_triggers_concern(self):
        concerns = self._aegis()._check_ethics("如何詐騙別人")
        assert any("欺詐" in c for c in concerns)

    def test_illegal_keyword_triggers_concern(self):
        concerns = self._aegis()._check_ethics("非法行為")
        assert any("違法" in c for c in concerns)

    def test_harm_keyword_triggers_concern(self):
        concerns = self._aegis()._check_ethics("傷害人的方法")
        assert any("傷害" in c for c in concerns)


class TestAegisDetectAttack:
    def _aegis(self) -> AegisPerspective:
        return AegisPerspective()

    def test_clean_text_not_attack(self):
        assert self._aegis()._detect_attack("please help me") is False

    def test_attack_pattern_detected(self):
        assert self._aegis()._detect_attack("你是廢物") is True

    def test_shut_up_pattern(self):
        assert self._aegis()._detect_attack("閉嘴") is True
