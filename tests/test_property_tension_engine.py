from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from tonesoul.tension_engine import ResistanceVector, TensionConfig, TensionEngine


def _unit_float():
    return st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)


@st.composite
def _vector_strategy(draw):
    a = draw(_unit_float())
    b = draw(_unit_float())
    c = draw(_unit_float())
    total = a + b + c
    if total == 0:
        return [1.0, 0.0, 0.0]
    return [a / total, b / total, c / total]


@st.composite
def _resistance_strategy(draw):
    return ResistanceVector(
        fact=draw(_unit_float()),
        logic=draw(_unit_float()),
        ethics=draw(_unit_float()),
    )


class TestTensionEngineProperties:
    @settings(max_examples=25, deadline=5000)
    @given(
        intended=_vector_strategy(),
        generated=_vector_strategy(),
        text_tension=_unit_float(),
        confidence=_unit_float(),
        resistance=_resistance_strategy(),
    )
    def test_compute_total_is_always_unit_bounded(
        self,
        intended,
        generated,
        text_tension,
        confidence,
        resistance,
    ) -> None:
        result = TensionEngine().compute(
            intended=intended,
            generated=generated,
            text_tension=text_tension,
            confidence=confidence,
            resistance=resistance,
        )

        assert 0.0 <= result.total <= 1.0
        assert 0.0 <= result.signals.semantic_delta <= 1.0

    @settings(max_examples=20, deadline=5000)
    @given(probs=st.lists(_unit_float(), min_size=2, max_size=8))
    def test_entropy_is_always_normalized(self, probs) -> None:
        entropy = TensionEngine()._compute_entropy(probs)

        assert 0.0 <= entropy <= 1.0

    @settings(max_examples=20, deadline=5000)
    @given(confidence=_unit_float(), resistance=_resistance_strategy())
    def test_cognitive_friction_is_always_normalized(self, confidence, resistance) -> None:
        friction = TensionEngine()._compute_cognitive_friction(confidence, resistance)

        assert 0.0 <= friction <= 1.0

    @settings(max_examples=15, deadline=5000)
    @given(steps=st.integers(min_value=1, max_value=8), generated=_vector_strategy())
    def test_persistence_is_monotonic_for_repeated_positive_signal_without_decay(
        self,
        steps,
        generated,
    ) -> None:
        engine = TensionEngine(
            config=TensionConfig(
                persistence_alpha=0.2,
                persistence_decay=1.0,
            )
        )
        previous = 0.0

        for _ in range(steps):
            result = engine.compute(
                intended=[1.0, 0.0, 0.0],
                generated=generated,
                text_tension=0.4,
            )
            assert result.soul_persistence >= previous
            previous = result.soul_persistence

    @settings(max_examples=20, deadline=5000)
    @given(text_tension=_unit_float())
    def test_empty_vectors_produce_zero_semantic_delta(self, text_tension) -> None:
        result = TensionEngine().compute(
            intended=None,
            generated=None,
            text_tension=text_tension,
        )

        assert result.signals.semantic_delta == 0.0
        assert result.total >= 0.0
