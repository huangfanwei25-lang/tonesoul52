from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from tonesoul.alert_escalation import AlertLevel
from tonesoul.governance.kernel import GovernanceKernel
from tonesoul.unified_pipeline import UnifiedPipeline


@dataclass
class _FakeSignals:
    semantic_delta: float = 0.0


@dataclass
class _FakeCompression:
    compression_ratio: float = 0.6
    gamma_effective: float = 1.0


@dataclass
class _FakePrediction:
    lyapunov_exponent: float = 0.05


class _FakeThrottle:
    def __init__(self, severity: str = "moderate") -> None:
        self.severity = SimpleNamespace(value=severity)
        self.delay_ms = 0

    def to_dict(self) -> dict[str, object]:
        return {"severity": self.severity.value, "delay_ms": self.delay_ms}


class _FakeTensionResult:
    def __init__(self) -> None:
        self.total = 0.62
        self.zone = SimpleNamespace(value="tension")
        self.prediction = _FakePrediction()
        self.compression = _FakeCompression()
        self.throttle = _FakeThrottle()
        self.work_category = "engineering"
        self.signals = _FakeSignals()

    def to_dict(self) -> dict[str, object]:
        return {
            "total": self.total,
            "zone": self.zone.value,
            "prediction": {"lyapunov_exponent": self.prediction.lyapunov_exponent},
            "compression": {
                "compression_ratio": self.compression.compression_ratio,
                "gamma_effective": self.compression.gamma_effective,
            },
            "throttle": self.throttle.to_dict(),
        }


class _FakeTensionEngine:
    def compute(self, **_kwargs):
        return _FakeTensionResult()

    def save_persistence(self) -> None:
        return None


class _FakeLLMClient:
    def __init__(self, response: str = "trace contract") -> None:
        self.response = response
        self.model = "mock-model"
        self.last_metrics = None

    def start_chat(self, history):
        del history
        return self

    def send_message(self, message: str) -> str:
        del message
        return self.response


class _FakeDriftMonitor:
    def __init__(self) -> None:
        self.step_count = 1
        self.current_alert = SimpleNamespace(value="warning")

    def summary(self) -> dict[str, object]:
        return {
            "current_alert": "warning",
            "step_count": 1,
        }


class _FakeAlertEscalation:
    def evaluate(self, **_kwargs):
        return SimpleNamespace(
            level=AlertLevel.L3,
            reasons=["jump warning"],
            is_clear=False,
        )

    def summary(self) -> dict[str, object]:
        return {
            "current_level": "L3",
            "evaluations": 1,
            "highest_ever": "L3",
            "reasons": ["jump warning"],
        }


def _build_pipeline() -> UnifiedPipeline:
    pipeline = UnifiedPipeline(mirror_enabled=False)
    pipeline._get_governance_kernel = MagicMock(return_value=None)
    pipeline._get_tonebridge = MagicMock(return_value=None)
    pipeline._get_trajectory = MagicMock(return_value=None)
    pipeline._get_deliberation = MagicMock(return_value=None)
    pipeline._get_council = MagicMock(return_value=None)
    pipeline._get_llm_router = MagicMock(return_value=None)
    pipeline._get_llm_client = MagicMock(return_value=_FakeLLMClient())
    pipeline._get_tension_engine = MagicMock(return_value=_FakeTensionEngine())
    pipeline._get_drift_monitor = MagicMock(return_value=_FakeDriftMonitor())
    pipeline._get_alert_escalation = MagicMock(return_value=_FakeAlertEscalation())
    return pipeline


def _run_pipeline() -> dict[str, object]:
    result = _build_pipeline().process(
        user_message="Provide a structured runtime trace review with explicit guardrails.",
        user_tier="premium",
        user_id="dispatch-trace-contract",
        prior_tension={
            "delta_t": 0.4,
            "query_tension": 0.4,
            "memory_tension": 0.3,
            "is_immutable": False,
        },
    )
    return result.dispatch_trace


def test_all_trace_sections_have_component() -> None:
    trace = _run_pipeline()

    for key, value in trace.items():
        if isinstance(value, dict):
            assert "component" in value, key


def test_all_trace_sections_have_timestamp() -> None:
    trace = _run_pipeline()

    for key, value in trace.items():
        if isinstance(value, dict):
            datetime.fromisoformat(str(value["timestamp"]))


def test_trace_section_status_values() -> None:
    trace = _run_pipeline()

    for key, value in trace.items():
        if isinstance(value, dict):
            assert value["status"] in {"ok", "degraded", "error"}, key


def test_routing_trace_has_component() -> None:
    kernel = GovernanceKernel()

    result = kernel.build_routing_trace(
        route="route_single_cloud",
        journal_eligible=True,
        reason="test",
    )

    assert result["component"] == "governance_kernel"
    assert "timestamp" in result


def test_trace_backward_compatible() -> None:
    trace = _run_pipeline()

    assert trace["routing_trace"]["route"] == trace["route"]
    assert trace["alert"]["current_level"] == "L3"
    assert trace["action_set"]["allowed_actions"] == ["verify", "cite", "inquire"]


def test_alert_trace_section_preserves_summary_fields() -> None:
    trace = _run_pipeline()
    alert = trace["alert"]

    assert alert["current_level"] == "L3"
    assert alert["detail"]["current_level"] == "L3"


def test_suppressed_errors_trace_section_preserves_count() -> None:
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

    with patch(
        "tonesoul.alert_escalation.AlertEscalation",
        side_effect=RuntimeError("alert init failed"),
    ):
        result = pipeline.process(
            user_message="Need a concise trace output.",
            user_tier="premium",
            user_id="dispatch-trace-suppressed",
            prior_tension={
                "delta_t": 0.4,
                "query_tension": 0.4,
                "memory_tension": 0.3,
                "is_immutable": False,
            },
        )

    suppressed = result.dispatch_trace["suppressed_errors"]
    assert suppressed["suppressed_count"] == 1
    assert suppressed["component"] == "exception_trace"
    assert suppressed["detail"]["suppressed_count"] == 1


def test_action_set_trace_section_preserves_allowed_actions() -> None:
    trace = _run_pipeline()

    assert trace["action_set"]["mode"] == "lockdown"
    assert trace["action_set"]["allowed_actions"] == ["verify", "cite", "inquire"]


def test_drift_trace_section_preserves_monitor_fields() -> None:
    trace = _run_pipeline()

    assert trace["drift"]["current_alert"] == "warning"
    assert trace["drift"]["detail"]["step_count"] == 1


def test_soul_integral_trace_section_present_when_tension_engine_runs() -> None:
    trace = _run_pipeline()

    assert trace["soul_integral"]["component"] == "tension_engine"
    assert trace["soul_integral"]["detail"]["total"] == 0.62


def test_trajectory_trace_section_present() -> None:
    trace = _run_pipeline()

    assert trace["trajectory"]["component"] == "trajectory"
    assert "detail" in trace["trajectory"]
