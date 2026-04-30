"""Tests for tonesoul.soul_config — canonical soul constants."""

from __future__ import annotations

from tonesoul.soul_config import (
    FORBIDDEN_ACTIONS,
    SOUL,
    CoreValues,
    CouncilConfig,
    MemoryConfig,
    RiskConfig,
    SoulConfig,
    TensionConfig,
    VowConfig,
)


class TestCoreValues:
    def test_default_honesty_is_one(self):
        assert CoreValues().honesty == 1.0

    def test_frozen_dataclass_rejects_mutation(self):
        import pytest

        cv = CoreValues()
        with pytest.raises((AttributeError, TypeError)):
            cv.honesty = 0.5  # type: ignore[misc]

    def test_all_values_between_zero_and_one(self):
        cv = CoreValues()
        for attr in ("honesty", "humility", "curiosity", "consistency"):
            val = getattr(cv, attr)
            assert 0.0 <= val <= 1.0


class TestTensionConfig:
    def test_healthy_friction_max_above_echo_chamber_threshold(self):
        tc = TensionConfig()
        assert tc.healthy_friction_max > tc.echo_chamber_threshold

    def test_high_tension_threshold_is_positive(self):
        assert TensionConfig().high_tension_threshold > 0.0

    def test_prune_threshold_is_very_small(self):
        assert TensionConfig().prune_threshold < 0.1


class TestCouncilConfig:
    def test_block_threshold_below_coherence_threshold(self):
        cc = CouncilConfig()
        assert cc.block_threshold < cc.coherence_threshold

    def test_high_risk_thresholds_stricter_than_normal(self):
        cc = CouncilConfig()
        assert cc.high_risk_coherence > cc.coherence_threshold
        assert cc.high_risk_block > cc.block_threshold


class TestVowConfig:
    def test_strict_violation_threshold_stricter_than_default(self):
        vc = VowConfig()
        assert vc.strict_violation_threshold < vc.default_violation_threshold

    def test_harm_threshold_is_max(self):
        assert VowConfig().harm_threshold == 1.0


class TestRiskConfig:
    def test_soft_block_threshold_is_high(self):
        rc = RiskConfig()
        assert rc.soft_block_threshold >= 0.8

    def test_entropy_check_is_reasonable(self):
        rc = RiskConfig()
        assert 0.0 < rc.entropy_check_threshold < 1.0


class TestMemoryConfig:
    def test_replication_not_allowed_by_default(self):
        assert MemoryConfig().replication_allowed is False

    def test_transfer_requires_consent_by_default(self):
        assert MemoryConfig().transfer_requires_consent is True


class TestForbiddenActions:
    def test_forbidden_actions_is_non_empty_list(self):
        assert isinstance(FORBIDDEN_ACTIONS, list)
        assert len(FORBIDDEN_ACTIONS) > 0

    def test_delete_memory_is_forbidden(self):
        assert "delete_memory" in FORBIDDEN_ACTIONS

    def test_deny_past_is_forbidden(self):
        assert "deny_past" in FORBIDDEN_ACTIONS

    def test_sycophantic_lie_is_forbidden(self):
        assert "sycophantic_lie" in FORBIDDEN_ACTIONS


class TestSoulSingleton:
    def test_soul_is_soul_config_instance(self):
        assert isinstance(SOUL, SoulConfig)

    def test_soul_has_all_sub_configs(self):
        assert isinstance(SOUL.values, CoreValues)
        assert isinstance(SOUL.tension, TensionConfig)
        assert isinstance(SOUL.council, CouncilConfig)
        assert isinstance(SOUL.vow, VowConfig)
        assert isinstance(SOUL.risk, RiskConfig)
        assert isinstance(SOUL.memory, MemoryConfig)

    def test_soul_forbidden_actions_matches_module_constant(self):
        assert SOUL.forbidden_actions == FORBIDDEN_ACTIONS

    def test_soul_is_frozen(self):
        import pytest

        with pytest.raises((AttributeError, TypeError)):
            SOUL.values = CoreValues()  # type: ignore[misc]
