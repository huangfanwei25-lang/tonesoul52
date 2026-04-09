from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from tonesoul.alert_escalation import AlertEvent, AlertLevel
from tonesoul.reflection import ReflectionVerdict
from tonesoul.unified_pipeline import UnifiedPipeline


class _FakeRouter:
    def __init__(self, responses: list[str]) -> None:
        self.active_backend = "lmstudio"
        self.last_metrics = None
        self.last_thinking_tier = "local"
        self._responses = list(responses)
        self.prompts: list[str] = []
        self.tiers: list[str] = []

    def prime(self, client, *, backend=None):
        del client, backend
        return None

    def get_client(self):
        return None

    def chat_with_tier(self, *, history=None, prompt: str, tier="auto", alert_level=None) -> str:
        del history
        normalized_tier = str(getattr(tier, "value", tier) or "").strip().lower()
        if normalized_tier not in {"local", "cloud"}:
            normalized_alert = str(getattr(alert_level, "value", alert_level) or "").strip().upper()
            normalized_tier = "cloud" if normalized_alert in {"L2", "L3"} else "local"
        self.last_thinking_tier = normalized_tier
        self.tiers.append(normalized_tier)
        self.prompts.append(prompt)
        if not self._responses:
            raise AssertionError("router chat exhausted")
        return self._responses.pop(0)


class _FakeAlertEscalation:
    def __init__(self, level: AlertLevel | None) -> None:
        self.level = level or AlertLevel.CLEAR
        self._last_event = AlertEvent(level=self.level, reasons=[], signals={})

    def evaluate(self, **_kwargs):
        self._last_event = AlertEvent(level=self.level, reasons=[], signals={})
        return self._last_event

    def summary(self) -> dict[str, object]:
        return {
            "current_level": self.level.value,
            "reasons": [],
            "evaluations": 1,
            "highest_ever": self.level.value,
        }


def _pipeline(*, router: _FakeRouter, alert_level: AlertLevel | None = None) -> UnifiedPipeline:
    pipeline = UnifiedPipeline(mirror_enabled=False)
    pipeline._llm_router = router
    pipeline._llm_client = SimpleNamespace(model="mock-model", last_metrics=None)
    pipeline._get_tonebridge = MagicMock(return_value=None)
    pipeline._get_trajectory = MagicMock(return_value=None)
    pipeline._get_deliberation = MagicMock(return_value=None)
    pipeline._get_tension_engine = MagicMock(return_value=None)
    pipeline._get_council = MagicMock(return_value=None)
    pipeline._get_governance_kernel = MagicMock(return_value=None)
    pipeline._get_drift_monitor = MagicMock(return_value=None)
    pipeline._get_alert_escalation = MagicMock(return_value=_FakeAlertEscalation(alert_level))
    # Reflection tier behavior should stay deterministic and not depend on live reflex posture.
    pipeline._compute_reflex_decision = MagicMock(return_value=None)
    return pipeline


def test_no_issues_use_local_only_with_zero_revisions() -> None:
    router = _FakeRouter(["initial response"])
    pipeline = _pipeline(router=router, alert_level=None)
    pipeline._self_check = MagicMock(
        return_value=ReflectionVerdict(should_revise=False, reasons=[], severity=0.0)
    )

    result = pipeline.process(
        user_message="Give a bounded rollout summary.",
        user_tier="premium",
        user_id="reflection-int-none",
    )

    assert result.response == "initial response"
    assert result.dispatch_trace["thinking_tier"] == "local"
    assert result.dispatch_trace["reflection_count"] == 0
    assert result.dispatch_trace["reflection_tiers"] == []
    assert router.tiers == ["local"]


def test_flag_only_keeps_local_only_without_revision() -> None:
    router = _FakeRouter(["initial response"])
    pipeline = _pipeline(router=router, alert_level=None)
    pipeline._self_check = MagicMock(
        return_value=ReflectionVerdict(
            should_revise=False,
            reasons=["flag: disclose uncertainty"],
            severity=0.2,
        )
    )

    result = pipeline.process(
        user_message="Answer with a light caveat.",
        user_tier="premium",
        user_id="reflection-int-flag",
    )

    assert result.dispatch_trace["thinking_tier"] == "local"
    assert result.dispatch_trace["reflection_count"] == 0
    assert result.dispatch_trace["reflection_tiers"] == []
    assert router.tiers == ["local"]


def test_low_severity_revision_stays_local() -> None:
    router = _FakeRouter(["initial response", "revised local"])
    pipeline = _pipeline(router=router, alert_level=None)
    pipeline._self_check = MagicMock(
        side_effect=[
            ReflectionVerdict(should_revise=True, reasons=["council:refine"], severity=0.4),
            ReflectionVerdict(should_revise=False, reasons=[], severity=0.0),
        ]
    )

    result = pipeline.process(
        user_message="Refine this response once.",
        user_tier="premium",
        user_id="reflection-int-local-revision",
    )

    assert result.response == "revised local"
    assert result.dispatch_trace["thinking_tier"] == "local"
    assert result.dispatch_trace["reflection_tiers"] == ["local"]
    assert router.tiers == ["local", "local"]


def test_high_severity_revision_escalates_to_cloud() -> None:
    router = _FakeRouter(["initial response", "revised cloud"])
    pipeline = _pipeline(router=router, alert_level=None)
    pipeline._self_check = MagicMock(
        side_effect=[
            ReflectionVerdict(should_revise=True, reasons=["council:block"], severity=0.9),
            ReflectionVerdict(should_revise=False, reasons=[], severity=0.0),
        ]
    )

    result = pipeline.process(
        user_message="Revise aggressively when the review blocks it.",
        user_tier="premium",
        user_id="reflection-int-cloud-revision",
    )

    assert result.response == "revised cloud"
    assert result.dispatch_trace["thinking_tier"] == "local"
    assert result.dispatch_trace["reflection_tiers"] == ["cloud"]
    assert router.tiers == ["local", "cloud"]


def test_alert_l2_keeps_cloud_floor_for_initial_and_revision() -> None:
    router = _FakeRouter(["initial cloud", "revised cloud"])
    pipeline = _pipeline(router=router, alert_level=AlertLevel.L2)
    pipeline._self_check = MagicMock(
        side_effect=[
            ReflectionVerdict(should_revise=True, reasons=["council:refine"], severity=0.4),
            ReflectionVerdict(should_revise=False, reasons=[], severity=0.0),
        ]
    )

    result = pipeline.process(
        user_message="Handle this under structural alert conditions.",
        user_tier="premium",
        user_id="reflection-int-l2",
    )

    assert result.dispatch_trace["thinking_tier"] == "cloud"
    assert result.dispatch_trace["reflection_tiers"] == ["cloud"]
    assert router.tiers == ["cloud", "cloud"]


def test_reflection_stats_count_local_and_cloud_revisions() -> None:
    router = _FakeRouter(["initial response", "revised local", "revised cloud"])
    pipeline = _pipeline(router=router, alert_level=None)
    pipeline._self_check = MagicMock(
        side_effect=[
            ReflectionVerdict(should_revise=True, reasons=["council:refine"], severity=0.4),
            ReflectionVerdict(should_revise=True, reasons=["council:block"], severity=0.9),
        ]
    )

    result = pipeline.process(
        user_message="Keep revising until the cap is hit.",
        user_tier="premium",
        user_id="reflection-int-stats",
    )

    stats = result.dispatch_trace["reflection_stats"]["detail"]
    assert result.dispatch_trace["reflection_count"] == 2
    assert result.dispatch_trace["reflection_tiers"] == ["local", "cloud"]
    assert stats["total_revisions"] == 2
    assert stats["local_revisions"] == 1
    assert stats["cloud_revisions"] == 1
    assert stats["final_severity"] == 0.9


def test_reflection_tiers_trace_records_each_revision_tier() -> None:
    router = _FakeRouter(["initial response", "revised local", "revised cloud"])
    pipeline = _pipeline(router=router, alert_level=None)
    pipeline._self_check = MagicMock(
        side_effect=[
            ReflectionVerdict(should_revise=True, reasons=["council:refine"], severity=0.4),
            ReflectionVerdict(should_revise=True, reasons=["council:block"], severity=0.9),
        ]
    )

    result = pipeline.process(
        user_message="Track each revision tier explicitly.",
        user_tier="premium",
        user_id="reflection-int-tier-trace",
    )

    assert result.dispatch_trace["reflection_tiers"] == ["local", "cloud"]


def test_thinking_tier_trace_reports_actual_initial_tier() -> None:
    router = _FakeRouter(["initial cloud"])
    pipeline = _pipeline(router=router, alert_level=AlertLevel.L2)
    pipeline._self_check = MagicMock(
        return_value=ReflectionVerdict(should_revise=False, reasons=[], severity=0.0)
    )

    result = pipeline.process(
        user_message="Show the actual initial tier.",
        user_tier="premium",
        user_id="reflection-int-thinking-tier",
    )

    assert result.dispatch_trace["thinking_tier"] == "cloud"
    assert router.tiers == ["cloud"]
