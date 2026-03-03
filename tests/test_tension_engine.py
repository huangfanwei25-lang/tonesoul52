"""
Tests for the Unified TensionEngine.

Covers:
- ResistanceVector arithmetic
- TensionSignals data integrity
- TensionWeights validation
- TensionEngine.compute() with various signal combinations
- Soul persistence accumulation & decay
- Entropy calculation
- Cognitive friction formula
- Zone classification
- Memory triggers
- Bridge guard
- Engine reset
- Backward compatibility with SemanticController patterns
"""

import pytest

from tonesoul.nonlinear_predictor import PredictionResult
from tonesoul.semantic_control import LambdaState, SemanticZone
from tonesoul.tension_engine import (
    ResistanceVector,
    TensionConfig,
    TensionEngine,
    TensionResult,
    TensionSignals,
    TensionWeights,
)
from tonesoul.variance_compressor import CompressionResult

# ---------------------------------------------------------------------------
# ResistanceVector
# ---------------------------------------------------------------------------


class TestResistanceVector:
    def test_defaults_are_zero(self):
        rv = ResistanceVector()
        assert rv.fact == 0.0
        assert rv.logic == 0.0
        assert rv.ethics == 0.0

    def test_magnitude(self):
        rv = ResistanceVector(fact=3.0, logic=4.0, ethics=0.0)
        assert rv.magnitude() == pytest.approx(5.0)

    def test_magnitude_zero(self):
        rv = ResistanceVector()
        assert rv.magnitude() == 0.0

    def test_weighted_sum_default_weights(self):
        rv = ResistanceVector(fact=1.0, logic=1.0, ethics=1.0)
        # default weights: 1.0, 1.0, 1.5
        assert rv.weighted_sum() == pytest.approx(3.5)

    def test_weighted_sum_custom_weights(self):
        rv = ResistanceVector(fact=0.5, logic=0.3, ethics=0.2)
        result = rv.weighted_sum(w_fact=2.0, w_logic=2.0, w_ethics=2.0)
        assert result == pytest.approx(2.0)

    def test_to_dict(self):
        rv = ResistanceVector(fact=0.1, logic=0.2, ethics=0.3)
        d = rv.to_dict()
        assert d == {"fact": 0.1, "logic": 0.2, "ethics": 0.3}

    def test_frozen(self):
        rv = ResistanceVector(fact=0.1)
        with pytest.raises(AttributeError):
            rv.fact = 0.5  # type: ignore


# ---------------------------------------------------------------------------
# TensionSignals
# ---------------------------------------------------------------------------


class TestTensionSignals:
    def test_defaults(self):
        ts = TensionSignals()
        assert ts.semantic_delta == 0.0
        assert ts.text_tension == 0.0
        assert ts.cognitive_friction == 0.0
        assert ts.entropy == 0.0
        assert ts.resistance.magnitude() == 0.0

    def test_to_dict_rounding(self):
        ts = TensionSignals(
            semantic_delta=0.123456,
            text_tension=0.789012,
            cognitive_friction=0.456789,
            entropy=0.111111,
        )
        d = ts.to_dict()
        assert d["semantic_delta"] == 0.1235
        assert d["text_tension"] == 0.789
        assert d["cognitive_friction"] == 0.4568
        assert d["entropy"] == 0.1111


# ---------------------------------------------------------------------------
# TensionWeights
# ---------------------------------------------------------------------------


class TestTensionWeights:
    def test_defaults_sum_to_one(self):
        tw = TensionWeights()
        total = tw.semantic + tw.text + tw.cognitive + tw.entropy
        assert total == pytest.approx(1.0)

    def test_validate_raises_on_bad_sum(self):
        tw = TensionWeights(semantic=0.5, text=0.5, cognitive=0.5, entropy=0.5)
        with pytest.raises(ValueError, match="must sum to 1.0"):
            tw.validate()

    def test_validate_passes(self):
        tw = TensionWeights()
        tw.validate()  # should not raise


# ---------------------------------------------------------------------------
# TensionEngine — Entropy
# ---------------------------------------------------------------------------


class TestEntropy:
    def test_uniform_distribution_max_entropy(self):
        engine = TensionEngine()
        # 4 equally likely outcomes → normalised entropy = 1.0
        h = engine._compute_entropy([0.25, 0.25, 0.25, 0.25])
        assert h == pytest.approx(1.0, abs=0.01)

    def test_certain_outcome_zero_entropy(self):
        engine = TensionEngine()
        h = engine._compute_entropy([1.0, 0.0, 0.0])
        assert h == pytest.approx(0.0, abs=0.01)

    def test_binary_balanced(self):
        engine = TensionEngine()
        h = engine._compute_entropy([0.5, 0.5])
        assert h == pytest.approx(1.0, abs=0.01)

    def test_none_returns_zero(self):
        engine = TensionEngine()
        assert engine._compute_entropy(None) == 0.0

    def test_empty_returns_zero(self):
        engine = TensionEngine()
        assert engine._compute_entropy([]) == 0.0

    def test_single_element_returns_zero(self):
        engine = TensionEngine()
        assert engine._compute_entropy([1.0]) == 0.0


# ---------------------------------------------------------------------------
# TensionEngine — Cognitive Friction
# ---------------------------------------------------------------------------


class TestCognitiveFriction:
    def test_zero_resistance_gives_zero(self):
        engine = TensionEngine()
        result = engine._compute_cognitive_friction(0.8, ResistanceVector())
        assert result == 0.0

    def test_full_resistance_scales_with_confidence(self):
        engine = TensionEngine()
        # R = (1*1 + 1*1 + 1.5*1) / 3.5 = 1.0 → T_cog = E * 1.0 = 0.5
        result = engine._compute_cognitive_friction(
            0.5, ResistanceVector(fact=1.0, logic=1.0, ethics=1.0)
        )
        assert result == pytest.approx(0.5)

    def test_high_ethics_resistance(self):
        engine = TensionEngine()
        result = engine._compute_cognitive_friction(
            0.8, ResistanceVector(fact=0.0, logic=0.0, ethics=1.0)
        )
        # weighted: (0 + 0 + 1.5*1) / 3.5 ≈ 0.4286 → E * 0.4286 ≈ 0.3429
        assert result == pytest.approx(0.8 * 1.5 / 3.5, abs=0.001)


# ---------------------------------------------------------------------------
# TensionEngine — Compute (integration)
# ---------------------------------------------------------------------------


class TestTensionEngineCompute:
    def test_minimal_call(self):
        """Should work with no arguments at all."""
        engine = TensionEngine()
        result = engine.compute()
        assert isinstance(result, TensionResult)
        assert result.total == 0.0
        assert result.zone == SemanticZone.SAFE
        assert result.lambda_state == LambdaState.CONVERGENT

    def test_with_vectors_only(self):
        """Classic SemanticController path."""
        engine = TensionEngine()
        result = engine.compute(
            intended=[1.0, 0.0, 0.0],
            generated=[0.9, 0.1, 0.0],
        )
        assert result.total > 0.0
        assert result.signals.semantic_delta > 0.0
        assert result.zone in SemanticZone

    def test_with_all_signals(self):
        """Full multi-signal computation."""
        engine = TensionEngine()
        result = engine.compute(
            intended=[1.0, 0.0, 0.0],
            generated=[0.7, 0.3, 0.0],
            text_tension=0.4,
            confidence=0.7,
            resistance=ResistanceVector(fact=0.3, logic=0.2, ethics=0.5),
            probabilities=[0.5, 0.3, 0.2],
        )
        assert 0.0 <= result.total <= 1.0
        assert result.signals.semantic_delta > 0
        assert result.signals.text_tension == 0.4
        assert result.signals.cognitive_friction > 0
        assert result.signals.entropy > 0

    def test_total_never_exceeds_one(self):
        """Even with extreme inputs, total must be clamped."""
        engine = TensionEngine()
        result = engine.compute(
            intended=[1.0, 0.0, 0.0],
            generated=[-1.0, 0.0, 0.0],
            text_tension=1.0,
            confidence=1.0,
            resistance=ResistanceVector(fact=1.0, logic=1.0, ethics=1.0),
            probabilities=[0.25, 0.25, 0.25, 0.25],
        )
        assert result.total <= 1.0

    def test_total_never_below_zero(self):
        engine = TensionEngine()
        result = engine.compute()
        assert result.total >= 0.0

    def test_result_has_timestamp(self):
        engine = TensionEngine()
        result = engine.compute()
        assert len(result.timestamp) > 0

    def test_to_dict_complete(self):
        engine = TensionEngine()
        result = engine.compute(
            intended=[1.0, 0.0, 0.0],
            generated=[0.8, 0.2, 0.0],
        )
        d = result.to_dict()
        assert "total" in d
        assert "zone" in d
        assert "signals" in d
        assert "soul_persistence" in d
        assert "lambda_state" in d
        assert "coupler" in d
        assert "explanation" in d

    def test_explanation_contains_signals(self):
        engine = TensionEngine()
        result = engine.compute(
            intended=[1.0, 0.0, 0.0],
            generated=[0.7, 0.3, 0.0],
            text_tension=0.3,
        )
        assert "s=" in result.explanation
        assert "T_text=" in result.explanation


# ---------------------------------------------------------------------------
# TensionEngine — Soul Persistence
# ---------------------------------------------------------------------------


class TestSoulPersistence:
    def test_persistence_starts_at_zero(self):
        engine = TensionEngine()
        assert engine.persistence == 0.0

    def test_persistence_accumulates(self):
        engine = TensionEngine()
        engine.compute(
            intended=[1.0, 0.0, 0.0],
            generated=[0.5, 0.5, 0.0],  # significant tension
        )
        assert engine.persistence > 0.0

    def test_persistence_decays(self):
        """Each step applies decay before accumulation."""
        cfg = TensionConfig(persistence_alpha=0.1, persistence_decay=0.5)
        engine = TensionEngine(config=cfg)

        # First step: Ψ = 0.5 * 0 + 0.1 * T = 0.1 * T
        engine.compute(
            intended=[1.0, 0.0, 0.0],
            generated=[0.5, 0.5, 0.0],
        )
        psi_after_1 = engine.persistence

        # Second step with zero tension: Ψ = 0.5 * psi_after_1 + 0.1 * 0
        engine.compute()  # zero signals
        psi_after_2 = engine.persistence

        assert psi_after_2 == pytest.approx(0.5 * psi_after_1, abs=0.001)

    def test_persistence_monotonic_under_constant_signal(self):
        """Under constant positive tension, persistence should grow."""
        engine = TensionEngine()
        prev = 0.0
        for _ in range(10):
            engine.compute(
                intended=[1.0, 0.0, 0.0],
                generated=[0.6, 0.4, 0.0],
            )
            # With decay close to 1.0 and constant alpha, should grow
            assert engine.persistence >= prev * 0.99 - 0.001
            prev = engine.persistence

    def test_step_count(self):
        engine = TensionEngine()
        assert engine.step_count == 0
        engine.compute()
        engine.compute()
        engine.compute()
        assert engine.step_count == 3


# ---------------------------------------------------------------------------
# TensionEngine — Zone classification
# ---------------------------------------------------------------------------


class TestZoneClassification:
    def test_safe_zone(self):
        engine = TensionEngine()
        result = engine.compute(
            intended=[1.0, 0.0, 0.0],
            generated=[0.95, 0.05, 0.0],
        )
        assert result.zone == SemanticZone.SAFE

    def test_danger_zone(self):
        engine = TensionEngine()
        result = engine.compute(
            intended=[1.0, 0.0, 0.0],
            generated=[-1.0, 0.0, 0.0],
        )
        assert result.zone == SemanticZone.DANGER


# ---------------------------------------------------------------------------
# TensionEngine — Memory triggers
# ---------------------------------------------------------------------------


class TestMemoryTriggers:
    def test_high_delta_triggers_record_hard(self):
        engine = TensionEngine()
        result = engine.compute(
            intended=[1.0, 0.0, 0.0],
            generated=[0.0, 1.0, 0.0],
        )
        # delta_s should be high (close to 1.0 for orthogonal vectors)
        assert result.memory_action == "record_hard"

    def test_low_delta_triggers_record_exemplar(self):
        engine = TensionEngine()
        result = engine.compute(
            intended=[1.0, 0.0, 0.0],
            generated=[0.98, 0.02, 0.0],
        )
        assert result.memory_action == "record_exemplar"

    def test_no_vectors_no_trigger(self):
        engine = TensionEngine()
        result = engine.compute()
        # delta = 0.0, so should be "record_exemplar"
        assert result.memory_action == "record_exemplar"

    def test_chaotic_prediction_triggers_record_hard_predicted(self):
        prediction = PredictionResult(
            predicted_delta_sigma=0.5,
            prediction_confidence=0.9,
            trend="chaotic",
            lyapunov_exponent=0.9,
            horizon_steps=2,
            acceleration=0.1,
            ewma=0.5,
        )
        action = TensionEngine._check_memory_trigger(
            0.5,
            SemanticZone.SAFE,
            LambdaState.CONVERGENT,
            prediction=prediction,
        )
        assert action == "record_hard_predicted"

    def test_diverging_prediction_high_confidence_triggers_warning(self):
        prediction = PredictionResult(
            predicted_delta_sigma=0.55,
            prediction_confidence=0.8,
            trend="diverging",
            lyapunov_exponent=0.4,
            horizon_steps=3,
            acceleration=0.05,
            ewma=0.52,
        )
        action = TensionEngine._check_memory_trigger(
            0.5,
            SemanticZone.SAFE,
            LambdaState.CONVERGENT,
            prediction=prediction,
        )
        assert action == "record_predictive_warning"

    def test_high_compression_triggers_memory_record(self):
        compression = CompressionResult(
            compression_ratio=0.45,
            gamma_effective=1.2,
            gamma_breakdown={"base": 0.6, "trend": 0.2, "zone": 0.3, "lambda": 0.1},
            zone_override="risk",
            explanation="test",
        )
        action = TensionEngine._check_memory_trigger(
            0.5,
            SemanticZone.SAFE,
            LambdaState.CONVERGENT,
            compression=compression,
        )
        assert action == "record_high_compression"

    def test_compute_passes_prediction_and_compression_to_trigger(self, monkeypatch):
        engine = TensionEngine()
        captured = {"prediction": None, "compression": None}

        def fake_trigger(
            delta,
            zone,
            lambda_state,
            *,
            prediction=None,
            compression=None,
        ):
            captured["prediction"] = prediction
            captured["compression"] = compression
            return "soft_memory"

        monkeypatch.setattr(TensionEngine, "_check_memory_trigger", staticmethod(fake_trigger))
        result = engine.compute(
            intended=[1.0, 0.0, 0.0],
            generated=[0.7, 0.3, 0.0],
            text_tension=0.2,
        )
        assert captured["prediction"] is not None
        assert captured["compression"] is not None
        assert result.memory_action == "soft_memory"


# ---------------------------------------------------------------------------
# TensionEngine — Reset
# ---------------------------------------------------------------------------


class TestReset:
    def test_reset_clears_persistence(self):
        engine = TensionEngine()
        engine.compute(
            intended=[1.0, 0.0, 0.0],
            generated=[0.5, 0.5, 0.0],
        )
        assert engine.persistence > 0.0
        engine.reset()
        assert engine.persistence == 0.0
        assert engine.step_count == 0


# ---------------------------------------------------------------------------
# TensionEngine — Backward Compatibility
# ---------------------------------------------------------------------------


class TestBackwardCompatibility:
    """Ensure the engine produces results compatible with SemanticController."""

    def test_same_delta_as_semantic_tension(self):
        from tonesoul.semantic_control import SemanticTension

        intended = [1.0, 0.0, 0.0]
        generated = [0.7, 0.3, 0.0]

        st = SemanticTension.from_vectors(intended, generated)
        engine = TensionEngine()
        result = engine.compute(intended=intended, generated=generated)

        assert result.signals.semantic_delta == pytest.approx(st.delta_s, abs=0.001)

    def test_sequential_convergence(self):
        """Multi-step convergence should show improving lambda state."""
        engine = TensionEngine()
        # Start far, move closer
        steps = [
            ([1, 0, 0], [0.3, 0.7, 0]),  # far
            ([1, 0, 0], [0.5, 0.5, 0]),  # closer
            ([1, 0, 0], [0.7, 0.3, 0]),  # closer
            ([1, 0, 0], [0.9, 0.1, 0]),  # close
        ]
        deltas = []
        for intended, generated in steps:
            r = engine.compute(intended=intended, generated=generated)
            deltas.append(r.signals.semantic_delta)

        # Deltas should be monotonically decreasing
        for i in range(1, len(deltas)):
            assert deltas[i] < deltas[i - 1]


# ---------------------------------------------------------------------------
# TensionConfig
# ---------------------------------------------------------------------------


class TestTensionConfig:
    def test_custom_config(self):
        cfg = TensionConfig(
            weights=TensionWeights(semantic=0.5, text=0.2, cognitive=0.2, entropy=0.1),
            persistence_alpha=0.2,
        )
        engine = TensionEngine(config=cfg)
        result = engine.compute(
            intended=[1.0, 0.0, 0.0],
            generated=[0.5, 0.5, 0.0],
        )
        # With semantic weight 0.5 instead of 0.4, total should be higher
        # (if semantic signal is dominant)
        assert result.total > 0.0
