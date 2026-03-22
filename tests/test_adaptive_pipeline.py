from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from tonesoul.deliberation.types import (
    DeliberationWeights,
    PerspectiveType,
    RoundResult,
    SynthesisType,
    SynthesizedResponse,
    Tension,
    ViewPoint,
)
from tonesoul.reflection import ReflectionVerdict
from tonesoul.unified_pipeline import UnifiedPipeline


class _FakeTensionResult:
    def __init__(self) -> None:
        self.total = 0.62
        self.zone = SimpleNamespace(value="tension")
        self.prediction = SimpleNamespace(lyapunov_exponent=0.05, trend="rising")
        self.compression = SimpleNamespace(compression_ratio=0.6, gamma_effective=1.0)
        self.throttle = SimpleNamespace(
            value="moderate", severity=SimpleNamespace(value="moderate"), delay_ms=0
        )
        self.work_category = "engineering"
        self.signals = SimpleNamespace(semantic_delta=0.0)

    def to_dict(self) -> dict[str, object]:
        return {
            "total": self.total,
            "zone": self.zone.value,
            "prediction": {"lyapunov_exponent": self.prediction.lyapunov_exponent},
            "compression": {
                "compression_ratio": self.compression.compression_ratio,
                "gamma_effective": self.compression.gamma_effective,
            },
            "throttle": {
                "severity": self.throttle.severity.value,
                "delay_ms": self.throttle.delay_ms,
            },
        }


class _FakeTensionEngine:
    def compute(self, **_kwargs):
        return _FakeTensionResult()

    def save_persistence(self) -> None:
        return None


class _FakeLLMClient:
    def __init__(self, response: str = "adaptive pipeline response") -> None:
        self.response = response
        self.model = "mock-model"
        self.last_metrics = None

    def start_chat(self, history):
        del history
        return self

    def send_message(self, message: str) -> str:
        del message
        return self.response


class _FakeCouncilVerdict:
    def __init__(self, name: str = "APPROVE") -> None:
        self.verdict = SimpleNamespace(name=name, value=name.lower())

    def to_dict(self) -> dict[str, object]:
        return {"verdict": self.verdict.value, "metadata": {}}


class _FakeCouncil:
    def __init__(self, name: str = "APPROVE") -> None:
        self.name = name
        self.calls = []

    def deliberate(self, request):
        self.calls.append(request)
        return _FakeCouncilVerdict(self.name)


class _FakeDeliberationEngine:
    def __init__(self, result: SynthesizedResponse) -> None:
        self.result = result
        self.contexts = []
        self.record_calls = []

    def deliberate_sync(self, context):
        self.contexts.append(context)
        return self.result

    def record_outcome(
        self,
        dominant_voice: str,
        verdict: str,
        resonance_state: str = "unknown",
        loop_detected: bool = False,
    ) -> None:
        self.record_calls.append(
            {
                "dominant_voice": dominant_voice,
                "verdict": verdict,
                "resonance_state": resonance_state,
                "loop_detected": loop_detected,
            }
        )

    def get_persona_track_summary(self) -> dict[str, dict[str, float]]:
        return {"logos": {"total": 1, "score": 1.0}, "aegis": {"total": 1, "score": 1.0}}


def _viewpoint(perspective: PerspectiveType, confidence: float = 0.8) -> ViewPoint:
    return ViewPoint(
        perspective=perspective,
        reasoning=f"{perspective.value} reasoning",
        proposed_response=f"{perspective.value} response",
        confidence=confidence,
    )


def _tension(severity: float) -> Tension:
    return Tension(
        between=(PerspectiveType.MUSE, PerspectiveType.LOGOS),
        description="conflict",
        severity=severity,
    )


def _round_result(number: int, aggregate: float, *, severity: float | None = None) -> RoundResult:
    tensions = [] if severity is None else [_tension(severity)]
    return RoundResult(
        round_number=number,
        viewpoints=[
            _viewpoint(PerspectiveType.MUSE),
            _viewpoint(PerspectiveType.LOGOS),
            _viewpoint(PerspectiveType.AEGIS),
        ],
        tensions=tensions,
        weights=DeliberationWeights(),
        aggregate_tension=aggregate,
    )


def _synthesized_response(
    *,
    dominant_voice: PerspectiveType = PerspectiveType.LOGOS,
    rounds_used: int = 1,
    round_results: list[RoundResult] | None = None,
) -> SynthesizedResponse:
    return SynthesizedResponse(
        response="deliberated answer",
        synthesis_type=SynthesisType.WEIGHTED_FUSION,
        dominant_voice=dominant_voice,
        viewpoints=[
            _viewpoint(PerspectiveType.MUSE),
            _viewpoint(PerspectiveType.LOGOS),
            _viewpoint(PerspectiveType.AEGIS),
        ],
        tensions=[_tension(0.2)],
        weights=DeliberationWeights(),
        rounds_used=rounds_used,
        round_results=round_results or [_round_result(1, 0.2, severity=0.2)],
    )


def _build_pipeline(
    result: SynthesizedResponse,
    *,
    council: object | None = None,
    should_convene: bool = False,
) -> tuple[UnifiedPipeline, _FakeDeliberationEngine]:
    pipeline = UnifiedPipeline(mirror_enabled=False)
    deliberation = _FakeDeliberationEngine(result)
    pipeline._get_governance_kernel = MagicMock(return_value=None)
    pipeline._get_tonebridge = MagicMock(return_value=None)
    pipeline._get_trajectory = MagicMock(return_value=None)
    pipeline._get_deliberation = MagicMock(return_value=deliberation)
    pipeline._get_council = MagicMock(return_value=council)
    pipeline._get_llm_router = MagicMock(return_value=None)
    pipeline._get_llm_client = MagicMock(return_value=_FakeLLMClient())
    pipeline._get_tension_engine = MagicMock(return_value=_FakeTensionEngine())
    pipeline._get_drift_monitor = MagicMock(return_value=None)
    pipeline._self_check = MagicMock(
        return_value=ReflectionVerdict(should_revise=False, reasons=[], severity=0.0)
    )
    pipeline._resolve_council_decision = MagicMock(
        return_value=(
            should_convene,
            "adaptive_test" if should_convene else "",
            0.4 if should_convene else None,
        )
    )
    return pipeline, deliberation


def _run_pipeline(
    result: SynthesizedResponse,
    *,
    council: object | None = None,
    should_convene: bool = False,
):
    pipeline, deliberation = _build_pipeline(
        result,
        council=council,
        should_convene=should_convene,
    )
    response = pipeline.process(
        user_message="Provide a bounded adaptive debate trace.",
        user_tier="premium",
        user_id="adaptive-pipeline-test",
        prior_tension={
            "delta_t": 0.4,
            "query_tension": 0.4,
            "memory_tension": 0.3,
            "is_immutable": False,
        },
    )
    return response, deliberation


def test_pipeline_records_single_round_count_without_extra_round_fields() -> None:
    result, _deliberation = _run_pipeline(_synthesized_response(rounds_used=1))

    assert result.dispatch_trace["deliberation_rounds"] == 1
    assert "tensions_per_round" not in result.dispatch_trace
    assert "debate_converged_early" not in result.dispatch_trace


def test_pipeline_records_multi_round_tensions_for_adaptive_debate() -> None:
    result, _deliberation = _run_pipeline(
        _synthesized_response(
            rounds_used=3,
            round_results=[
                _round_result(1, 0.8, severity=0.8),
                _round_result(2, 0.75, severity=0.75),
                _round_result(3, 0.72, severity=0.72),
            ],
        )
    )

    assert result.dispatch_trace["deliberation_rounds"] == 3
    assert result.dispatch_trace["tensions_per_round"] == [0.8, 0.75, 0.72]
    assert result.dispatch_trace["debate_converged_early"] is False


def test_pipeline_marks_early_convergence_when_rounds_end_before_planned_target() -> None:
    result, _deliberation = _run_pipeline(
        _synthesized_response(
            rounds_used=2,
            round_results=[
                _round_result(1, 0.9, severity=0.9),
                _round_result(2, 0.2, severity=0.2),
            ],
        )
    )

    assert result.dispatch_trace["deliberation_rounds"] == 2
    assert result.dispatch_trace["tensions_per_round"] == [0.9, 0.2]
    assert result.dispatch_trace["debate_converged_early"] is True


def test_pipeline_uses_first_round_tension_for_convergence_baseline() -> None:
    synth = _synthesized_response(
        rounds_used=2,
        round_results=[
            _round_result(1, 0.9, severity=0.9),
            _round_result(2, 0.2, severity=0.2),
        ],
    )
    synth.tensions = [_tension(0.2)]

    result, _deliberation = _run_pipeline(synth)

    assert result.dispatch_trace["debate_converged_early"] is True


def test_deliberation_section_preserves_round_metadata() -> None:
    result, _deliberation = _run_pipeline(
        _synthesized_response(
            rounds_used=2,
            round_results=[
                _round_result(1, 0.6, severity=0.6),
                _round_result(2, 0.4, severity=0.4),
            ],
        )
    )

    detail = result.dispatch_trace["deliberation"]["detail"]
    assert detail["rounds_used"] == 2
    assert detail["tensions_per_round"] == [0.6, 0.4]
    assert detail["debate_converged_early"] is False


def test_deliberation_section_keeps_existing_core_fields() -> None:
    result, _deliberation = _run_pipeline(_synthesized_response(rounds_used=1))

    detail = result.dispatch_trace["deliberation"]["detail"]
    assert detail["used"] is True
    assert detail["dominant_voice"] == "logos"
    assert detail["persona_mode"] == "Engineer"


def test_record_outcome_uses_final_dominant_voice_from_adaptive_result() -> None:
    council = _FakeCouncil(name="APPROVE")
    result, deliberation = _run_pipeline(
        _synthesized_response(
            dominant_voice=PerspectiveType.AEGIS,
            rounds_used=2,
            round_results=[
                _round_result(1, 0.8, severity=0.8),
                _round_result(2, 0.6, severity=0.6),
            ],
        ),
        council=council,
        should_convene=True,
    )

    assert result.dispatch_trace["deliberation"]["detail"]["dominant_voice"] == "aegis"
    assert deliberation.record_calls[0]["dominant_voice"] == "aegis"
    assert deliberation.record_calls[0]["verdict"] == "approve"


def test_pipeline_leaves_round_telemetry_absent_when_engine_is_unavailable() -> None:
    pipeline = UnifiedPipeline(mirror_enabled=False)
    pipeline._get_governance_kernel = MagicMock(return_value=None)
    pipeline._get_tonebridge = MagicMock(return_value=None)
    pipeline._get_trajectory = MagicMock(return_value=None)
    pipeline._get_deliberation = MagicMock(return_value=None)
    pipeline._get_council = MagicMock(return_value=None)
    pipeline._get_llm_router = MagicMock(return_value=None)
    pipeline._get_llm_client = MagicMock(return_value=_FakeLLMClient())
    pipeline._get_tension_engine = MagicMock(return_value=_FakeTensionEngine())
    pipeline._get_drift_monitor = MagicMock(return_value=None)
    pipeline._self_check = MagicMock(
        return_value=ReflectionVerdict(should_revise=False, reasons=[], severity=0.0)
    )

    result = pipeline.process(
        user_message="Keep the old path when deliberation is missing.",
        user_tier="premium",
        user_id="adaptive-pipeline-no-engine",
    )

    assert "deliberation_rounds" not in result.dispatch_trace
    assert "tensions_per_round" not in result.dispatch_trace
    assert "debate_converged_early" not in result.dispatch_trace
