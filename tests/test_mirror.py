from __future__ import annotations

from dataclasses import dataclass, field

from tonesoul.mirror import ToneSoulMirror


@dataclass
class _DummySignals:
    cognitive_friction: float
    text_tension: float

    def to_dict(self) -> dict[str, object]:
        return {
            "semantic_delta": 0.0,
            "delta_sigma": 0.0,
            "text_tension": round(self.text_tension, 4),
            "cognitive_friction": round(self.cognitive_friction, 4),
            "entropy": 0.0,
            "delta_s_ecs": 0.0,
            "t_ecs": round(self.cognitive_friction, 4),
            "resistance": {"fact": 0.0, "logic": 0.0, "ethics": 0.0},
        }


@dataclass
class _DummyPrediction:
    lyapunov_exponent: float = 0.0


@dataclass
class _DummyZone:
    value: str


@dataclass
class _DummyTensionResult:
    total: float
    signals: _DummySignals
    zone: _DummyZone
    prediction: _DummyPrediction = field(default_factory=_DummyPrediction)
    timestamp: str = "2026-03-10T12:00:00Z"


class _DummyTensionEngine:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def compute(self, *, text_tension: float = 0.0, confidence: float = 0.8, **_: object):
        self.calls.append(
            {"text_tension": float(text_tension), "confidence": float(confidence)}
        )
        total = max(0.0, min(1.0, float(text_tension)))
        phase = "unstable" if total >= 0.4 else "stable"
        return _DummyTensionResult(
            total=total,
            signals=_DummySignals(cognitive_friction=total, text_tension=total),
            zone=_DummyZone(phase),
            prediction=_DummyPrediction(0.22 if total >= 0.4 else 0.01),
        )


class _DummyGovernanceKernel:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def should_convene_council(
        self,
        *,
        tension: float,
        friction_score: float | None = None,
        user_tier: str = "free",
        message_length: int = 0,
        min_council_tension: float = 0.4,
        min_council_friction: float = 0.62,
    ) -> tuple[bool, str]:
        self.calls.append(
            {
                "tension": tension,
                "friction_score": friction_score,
                "user_tier": user_tier,
                "message_length": message_length,
            }
        )
        effective = max(float(tension), float(friction_score or 0.0))
        if effective >= max(min_council_tension, min_council_friction):
            return True, "High governance friction"
        return False, "Council not needed"


def test_mirror_passthrough_low_tension() -> None:
    mirror = ToneSoulMirror(_DummyTensionEngine(), _DummyGovernanceKernel())

    dual = mirror.reflect("Calm response.", {"tone_strength": 0.2, "confidence": 0.9})

    assert dual.governed_response == dual.raw_response
    assert dual.final_choice == "raw"
    assert dual.mirror_delta.mirror_triggered is False
    assert dual.mirror_delta.subjectivity_flags == []


def test_mirror_triggered_high_tension() -> None:
    mirror = ToneSoulMirror(_DummyTensionEngine(), _DummyGovernanceKernel())

    dual = mirror.reflect("THIS NEEDS AN ANSWER NOW!", {"tone_strength": 0.84})

    assert dual.mirror_delta.mirror_triggered is True
    assert dual.final_choice == "governed"
    assert dual.governed_response != dual.raw_response
    assert dual.mirror_delta.subjectivity_flags == ["tension"]
    assert dual.mirror_delta.governance_decision is not None
    assert dual.mirror_delta.governance_decision.should_convene_council is True


def test_mirror_graceful_no_engine() -> None:
    mirror = ToneSoulMirror()

    dual = mirror.reflect("Fallback response.", {"tone_strength": 0.9})

    assert dual.raw_response == "Fallback response."
    assert dual.governed_response == "Fallback response."
    assert dual.final_choice == "raw"
    assert dual.mirror_delta.mirror_triggered is False
    assert "unavailable" in dual.reflection_note.lower()


def test_mirror_delta_serializable() -> None:
    mirror = ToneSoulMirror(_DummyTensionEngine(), _DummyGovernanceKernel())

    dual = mirror.reflect("PLEASE RESPOND IMMEDIATELY!", {"tone_strength": 0.9})
    payload = dual.model_dump(mode="json")

    assert payload["final_choice"] == "governed"
    assert payload["mirror_delta"]["mirror_triggered"] is True
    assert payload["mirror_delta"]["subjectivity_flags"] == ["tension"]
    assert payload["mirror_delta"]["governance_decision"]["circuit_breaker_status"] == "ok"
