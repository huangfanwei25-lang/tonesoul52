"""Tests for tonesoul.resistance module (RFC-012)."""

from __future__ import annotations

import pytest

from tonesoul.resistance import (
    CircuitBreaker,
    CollapseException,
    FrictionCalculator,
    FrictionResult,
    PainEngine,
    PerturbationRecovery,
    ThrottleSeverity,
)

# ── FrictionCalculator ───────────────────────────────────────────


class TestFrictionCalculator:
    def test_zero_friction_same_tension(self):
        calc = FrictionCalculator()
        result = calc.compute(query_tension=0.5, constraint_tension=0.5)
        assert result.tension_delta == 0.0
        assert result.friction_score == 0.0

    def test_max_friction_opposite_tension(self):
        calc = FrictionCalculator()
        result = calc.compute(query_tension=0.0, constraint_tension=1.0)
        assert result.tension_delta == pytest.approx(1.0)
        assert result.friction_score > 0.5

    def test_wave_distance_increases_friction(self):
        calc = FrictionCalculator()
        no_wave = calc.compute(query_tension=0.5, constraint_tension=0.5)
        with_wave = calc.compute(
            query_tension=0.5,
            constraint_tension=0.5,
            query_wave={"uncertainty_shift": 0.0, "divergence_shift": 0.0},
            constraint_wave={"uncertainty_shift": 1.0, "divergence_shift": 1.0},
        )
        assert with_wave.friction_score > no_wave.friction_score

    def test_immutable_amplifies_friction(self):
        calc = FrictionCalculator()
        normal = calc.compute(
            query_tension=0.0,
            constraint_tension=0.8,
            is_immutable=False,
        )
        immutable = calc.compute(
            query_tension=0.0,
            constraint_tension=0.8,
            is_immutable=True,
        )
        assert immutable.friction_score > normal.friction_score
        assert immutable.is_immutable is True

    def test_friction_clamped_to_unit(self):
        calc = FrictionCalculator()
        result = calc.compute(
            query_tension=0.0,
            constraint_tension=1.0,
            query_wave={
                "uncertainty_shift": 0.0,
                "divergence_shift": 0.0,
                "risk_shift": 0.0,
                "revision_shift": 0.0,
            },
            constraint_wave={
                "uncertainty_shift": 1.0,
                "divergence_shift": 1.0,
                "risk_shift": 1.0,
                "revision_shift": 1.0,
            },
            is_immutable=True,
        )
        assert result.friction_score <= 1.0

    def test_to_dict(self):
        calc = FrictionCalculator()
        result = calc.compute(
            query_tension=0.5,
            constraint_tension=0.7,
            constraint_kind="constraint",
        )
        d = result.to_dict()
        assert "tension_delta" in d
        assert "friction_score" in d
        assert d["constraint_kind"] == "constraint"


# ── PainEngine ───────────────────────────────────────────────────


class TestPainEngine:
    def test_no_throttle_below_floor(self):
        engine = PainEngine()
        result = engine.evaluate_throttle(
            friction=FrictionResult(
                tension_delta=0.1,
                wave_distance=0.0,
                friction_score=0.1,
                constraint_kind="note",
                is_immutable=False,
            ),
        )
        assert result.severity == ThrottleSeverity.NONE
        assert result.temperature_multiplier == 1.0
        assert result.top_p_multiplier == 1.0
        assert result.delay_ms == 0

    def test_mild_throttle(self):
        engine = PainEngine()
        result = engine.evaluate_throttle(
            friction=FrictionResult(
                tension_delta=0.4,
                wave_distance=0.0,
                friction_score=0.4,
                constraint_kind="note",
                is_immutable=False,
            ),
        )
        assert result.severity == ThrottleSeverity.MILD
        assert result.temperature_multiplier > 1.0
        assert result.top_p_multiplier < 1.0

    def test_critical_throttle_high_friction(self):
        engine = PainEngine()
        result = engine.evaluate_throttle(
            friction=FrictionResult(
                tension_delta=0.9,
                wave_distance=0.8,
                friction_score=0.9,
                constraint_kind="constraint",
                is_immutable=True,
            ),
        )
        assert result.severity == ThrottleSeverity.CRITICAL
        assert result.temperature_multiplier > 2.0
        assert result.top_p_multiplier < 0.5
        assert result.delay_ms > 0

    def test_compression_ratio_triggers_throttle(self):
        engine = PainEngine()
        result = engine.evaluate_throttle(compression_ratio=0.35)
        assert result.severity in (ThrottleSeverity.MODERATE, ThrottleSeverity.SEVERE)

    def test_no_throttle_high_compression_ratio(self):
        engine = PainEngine()
        result = engine.evaluate_throttle(compression_ratio=0.95)
        assert result.severity == ThrottleSeverity.NONE

    def test_variance_gate_factor_unit(self):
        engine = PainEngine(gamma=1.0)
        assert engine.variance_gate_factor(0.0) == pytest.approx(1.0)
        assert engine.variance_gate_factor(1.0) == pytest.approx(0.3679, abs=0.01)
        assert 0 < engine.variance_gate_factor(5.0) < 0.01

    def test_variance_gate_factor_zero_gamma(self):
        engine = PainEngine(gamma=0.0)
        assert engine.variance_gate_factor(10.0) == pytest.approx(1.0)

    def test_to_dict(self):
        engine = PainEngine()
        result = engine.evaluate_throttle(compression_ratio=0.5)
        d = result.to_dict()
        assert "severity" in d
        assert "temperature_multiplier" in d
        assert "compression_ratio" in d


# ── CircuitBreaker ───────────────────────────────────────────────


class TestCircuitBreaker:
    def _make_friction(self, score: float, *, is_immutable: bool = False) -> FrictionResult:
        return FrictionResult(
            tension_delta=score,
            wave_distance=0.0,
            friction_score=score,
            constraint_kind="constraint",
            is_immutable=is_immutable,
        )

    def test_no_collapse_low_friction(self):
        cb = CircuitBreaker()
        cb.check(self._make_friction(0.2))
        assert not cb.is_frozen

    def test_collapse_immutable_high_friction(self):
        cb = CircuitBreaker()
        with pytest.raises(CollapseException, match="不可變約束違反"):
            cb.check(self._make_friction(0.8, is_immutable=True))
        assert cb.is_frozen

    def test_consecutive_high_triggers_collapse(self):
        cb = CircuitBreaker(consecutive_limit=3, high_friction_mark=0.6)
        cb.check(self._make_friction(0.65))
        cb.check(self._make_friction(0.7))
        with pytest.raises(CollapseException, match="連續"):
            cb.check(self._make_friction(0.75))
        assert cb.is_frozen

    def test_consecutive_resets_on_low(self):
        cb = CircuitBreaker(consecutive_limit=3, high_friction_mark=0.6)
        cb.check(self._make_friction(0.65))
        cb.check(self._make_friction(0.7))
        cb.check(self._make_friction(0.2))  # Reset
        cb.check(self._make_friction(0.65))
        assert not cb.is_frozen

    def test_lyapunov_freeze(self):
        cb = CircuitBreaker(lyapunov_threshold=0.5, high_friction_mark=0.4)
        with pytest.raises(CollapseException, match="Lyapunov"):
            cb.check(self._make_friction(0.5), lyapunov_exponent=0.8)

    def test_lyapunov_no_freeze_low_friction(self):
        """High Lyapunov alone (without meaningful friction) does not freeze."""
        cb = CircuitBreaker(lyapunov_threshold=0.5, high_friction_mark=0.6)
        cb.check(self._make_friction(0.2), lyapunov_exponent=0.8)
        assert not cb.is_frozen

    def test_compute_lyapunov_exponent_stable(self):
        cb = CircuitBreaker()
        for score in [0.5, 0.5, 0.5, 0.5]:
            try:
                cb.check(self._make_friction(score))
            except CollapseException:
                pass
        lyap = cb.compute_lyapunov_exponent()
        assert lyap < 0  # Stable (near-zero differences → negative log)

    def test_compute_lyapunov_exponent_diverging(self):
        cb = CircuitBreaker()
        for score in [0.1, 0.3, 0.5, 0.55]:
            try:
                cb.check(self._make_friction(score))
            except CollapseException:
                pass
        lyap = cb.compute_lyapunov_exponent()
        # Increasing trajectory → positive or near-zero Lyapunov
        assert lyap > -5  # Just verify it's computed

    def test_reset(self):
        cb = CircuitBreaker()
        try:
            cb.check(self._make_friction(0.8, is_immutable=True))
        except CollapseException:
            pass
        assert cb.is_frozen
        cb.reset()
        assert not cb.is_frozen
        assert len(cb.state.friction_history) == 0

    def test_frozen_rejects_all(self):
        cb = CircuitBreaker()
        try:
            cb.check(self._make_friction(0.8, is_immutable=True))
        except CollapseException:
            pass
        with pytest.raises(CollapseException, match="系統已凍結"):
            cb.check(self._make_friction(0.1))

    def test_state_to_dict(self):
        cb = CircuitBreaker()
        cb.check(self._make_friction(0.3))
        d = cb.state.to_dict()
        assert "friction_history_len" in d
        assert d["friction_history_len"] == 1


# ── PerturbationRecovery (Pipeline V2) ───────────────────────────


class TestPerturbationRecovery:
    def test_no_recovery_below_threshold(self):
        pr = PerturbationRecovery(stress_threshold=0.5)
        result = pr.recover(compression_ratio=0.8)
        assert result is None

    def test_recovery_above_threshold(self):
        pr = PerturbationRecovery(stress_threshold=0.5, n_paths=5)
        result = pr.recover(compression_ratio=0.4)
        assert result is not None
        assert result.path_id >= 0
        assert result.throttle is not None

    def test_best_path_has_lowest_stress(self):
        pr = PerturbationRecovery(stress_threshold=0.3, n_paths=7)
        result = pr.recover(compression_ratio=0.5)
        assert result is not None
        # The best path should have the lowest effective stress
        # among candidates. Since offsets range [-max, +max],
        # the positive-offset path gives higher compression_ratio → lower stress.
        assert result.perturbation_offset > 0  # Positive offset = better

    def test_recovery_with_friction(self):
        pr = PerturbationRecovery(stress_threshold=0.3, n_paths=3)
        friction = FrictionResult(
            tension_delta=0.6,
            wave_distance=0.3,
            friction_score=0.5,
            constraint_kind="constraint",
            is_immutable=False,
        )
        result = pr.recover(compression_ratio=0.4, friction=friction)
        assert result is not None

    def test_to_dict(self):
        pr = PerturbationRecovery(stress_threshold=0.3, n_paths=3)
        result = pr.recover(compression_ratio=0.3)
        assert result is not None
        d = result.to_dict()
        assert "path_id" in d
        assert "effective_stress" in d
        assert "throttle" in d

    def test_single_path(self):
        pr = PerturbationRecovery(n_paths=1, stress_threshold=0.3)
        result = pr.recover(compression_ratio=0.5)
        assert result is not None
        assert result.path_id == 0
        assert result.perturbation_offset == 0.0


# ── Hippocampus V2: Directional Error Vector ─────────────────────


class TestHippocampusV2:
    def test_compute_error_vector_basic(self):
        import numpy as np

        from tonesoul.memory.hippocampus import Hippocampus

        intended = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        generated = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        b_vec = Hippocampus.compute_error_vector(intended, generated)

        # Should point from generated towards intended
        assert b_vec.shape == (3,)
        # Should be normalized
        assert abs(float(np.linalg.norm(b_vec)) - 1.0) < 1e-5

    def test_compute_error_vector_identical(self):
        import numpy as np

        from tonesoul.memory.hippocampus import Hippocampus

        v = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        b_vec = Hippocampus.compute_error_vector(v, v)

        # Zero difference → zero vector (not normalized)
        assert float(np.linalg.norm(b_vec)) < 1e-5

    def test_error_vector_direction(self):
        import numpy as np

        from tonesoul.memory.hippocampus import Hippocampus

        intended = np.array([1.0, 0.0], dtype=np.float32)
        generated = np.array([0.0, 0.0], dtype=np.float32)
        b_vec = Hippocampus.compute_error_vector(intended, generated)

        # B_vec should point in direction of intended (positive x)
        assert b_vec[0] > 0
