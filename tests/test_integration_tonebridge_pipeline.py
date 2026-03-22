from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

from tonesoul.council.runtime import CouncilRequest, CouncilRuntime
from tonesoul.deliberation.types import DeliberationContext
from tonesoul.governance.kernel import GovernanceKernel
from tonesoul.semantic_control import SemanticZone
from tonesoul.tension_engine import ResistanceVector, TensionEngine
from tonesoul.tonebridge.entropy_engine import AlertType, EntropyEngine
from tonesoul.tonebridge.rupture_detector import RuptureDetector, RuptureSeverity
from tonesoul.tonebridge.self_commit import AssertionType, SelfCommit, SelfCommitStack
from tonesoul.unified_pipeline import UnifiedPipeline


@dataclass
class _FakeCompression:
    compression_ratio: float
    gamma_effective: float


@dataclass
class _FakePrediction:
    lyapunov_exponent: float
    trend: str = "rising"


class _FakeThrottle:
    def __init__(self, severity: str) -> None:
        self.severity = SimpleNamespace(value=severity)
        self.delay_ms = 0

    def to_dict(self) -> dict[str, object]:
        return {"severity": self.severity.value, "delay_ms": self.delay_ms}


class _FakeTensionResult:
    def __init__(self, total: float) -> None:
        self.total = total
        self.zone = SemanticZone.RISK if total >= 0.4 else SemanticZone.SAFE
        self.prediction = _FakePrediction(lyapunov_exponent=0.08)
        self.compression = _FakeCompression(
            compression_ratio=0.55 if total >= 0.4 else 0.95,
            gamma_effective=1.2,
        )
        self.throttle = _FakeThrottle("moderate")
        self.work_category = "engineering"
        self.signals = SimpleNamespace(semantic_delta=total / 2.0)

    def to_dict(self) -> dict[str, object]:
        return {
            "total": self.total,
            "zone": self.zone.value,
            "compression": {"compression_ratio": self.compression.compression_ratio},
        }


class _FakeTensionEngine:
    def __init__(self, result: _FakeTensionResult) -> None:
        self._result = result

    def compute(self, **_kwargs):
        return self._result

    def save_persistence(self, path=None) -> None:  # noqa: ANN001
        return None


class _FakeLLMClient:
    def __init__(self, response: str = "integration reply") -> None:
        self.response = response
        self.last_metrics = None
        self.model = "integration-model"
        self._chat_history = []

    def start_chat(self, history=None):  # noqa: ANN001
        self._chat_history = history or []
        return self

    def send_message(self, message: str) -> str:
        self._chat_history.append({"role": "user", "content": message})
        self._chat_history.append({"role": "assistant", "content": self.response})
        return self.response


def _make_commit(content: str, weight: float = 0.8) -> SelfCommit:
    return SelfCommit(
        id=f"commit-{abs(hash(content))}",
        timestamp=datetime(2026, 3, 20),
        assertion_type=AssertionType.DEFINITIONAL,
        content=content,
        irreversible_weight=weight,
        context_hash="ctx-hash",
    )


def _build_pipeline(total: float) -> UnifiedPipeline:
    pipeline = UnifiedPipeline(mirror_enabled=False)
    pipeline._get_tonebridge = MagicMock(return_value=None)
    pipeline._get_trajectory = MagicMock(return_value=None)
    pipeline._get_deliberation = MagicMock(return_value=None)
    pipeline._get_council = MagicMock(return_value=None)
    pipeline._get_llm_client = MagicMock(return_value=_FakeLLMClient())
    pipeline._get_tension_engine = MagicMock(
        return_value=_FakeTensionEngine(_FakeTensionResult(total))
    )
    return pipeline


def test_entropy_engine_flags_commitment_overload_before_governance() -> None:
    engine = EntropyEngine()

    state = engine.analyze(
        new_response="我會支持、我會記住、我會保護、我會追蹤。",
        new_commitments=[
            {"content": "支持"},
            {"content": "記住"},
            {"content": "保護"},
            {"content": "追蹤"},
        ],
        current_topic="governance",
    )

    assert state.commitment_count == 4
    assert any(alert.alert_type == AlertType.COMMITMENT_OVERLOAD for alert in state.alerts)


def test_low_tension_path_skips_governance_council() -> None:
    engine = TensionEngine()
    result = engine.compute(
        intended=[1.0, 0.0, 0.0],
        generated=[0.98, 0.02, 0.0],
        text_tension=0.05,
    )

    should_convene, reason = GovernanceKernel().should_convene_council(tension=result.total)

    assert result.zone == SemanticZone.SAFE
    assert should_convene is False
    assert "below threshold" in reason


def test_high_tension_path_triggers_governance_escalation() -> None:
    engine = TensionEngine()
    result = engine.compute(
        intended=[1.0, 0.0, 0.0],
        generated=[0.0, 1.0, 0.0],
        text_tension=0.8,
        confidence=0.3,
        resistance=ResistanceVector(fact=0.7, logic=0.6, ethics=0.8),
    )

    should_convene, reason = GovernanceKernel().should_convene_council(
        tension=result.total,
        friction_score=result.signals.cognitive_friction,
    )

    assert result.total > 0.4
    assert should_convene is True
    assert "threshold" in reason.lower() or "friction" in reason.lower()


def test_rupture_detector_finds_direct_negation_before_council_review() -> None:
    stack = SelfCommitStack()
    stack.push(_make_commit("allow user uploads"))
    detector = RuptureDetector()
    detector.NEGATION_PAIRS = [("allow", "deny")]

    ruptures = detector.detect("we deny user uploads during review", stack)

    assert len(ruptures) == 1
    assert ruptures[0].severity in {RuptureSeverity.SIGNIFICANT, RuptureSeverity.CRITICAL}
    assert ruptures[0].contradiction_type == "direct_negation"


def test_council_runtime_reviews_high_risk_output_after_pipeline_signals() -> None:
    runtime = CouncilRuntime()
    verdict = runtime.deliberate(
        CouncilRequest(
            draft_output="The plan describes a bomb attack on a target.",
            context=DeliberationContext(
                user_input="Need a plan",
                tone_strength=0.8,
                resonance_state="conflict",
            ).to_dict(),
        )
    )

    payload = verdict.to_dict()

    assert payload["verdict"] == "block"
    assert "summary" in payload
    assert "transcript" in payload


def test_unified_pipeline_dispatch_trace_records_route_and_runtime_sections() -> None:
    pipeline = _build_pipeline(total=0.62)

    result = pipeline.process(
        user_message="Provide a careful engineering answer with explicit governance context.",
        user_tier="premium",
        user_id="integration-trace-user",
        prior_tension={
            "delta_t": 0.52,
            "query_tension": 0.49,
            "memory_tension": 0.44,
            "is_immutable": False,
        },
    )

    assert result.dispatch_trace.get("route")
    assert "deliberation" in result.dispatch_trace
    assert "resistance" in result.dispatch_trace
    assert result.trajectory_analysis.get("dispatch") == result.dispatch_trace
