from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import tonesoul.vow_system as vow_system
from tonesoul.reflection import ReflectionVerdict
from tonesoul.unified_pipeline import UnifiedPipeline
from tonesoul.vow_system import VowEnforcementResult


class _FakeTensionEngine:
    def __init__(self, total: float) -> None:
        self.total = total

    def compute(self, **_kwargs):
        return SimpleNamespace(total=self.total)


class _FakeCouncil:
    def __init__(self, decision: str) -> None:
        self.decision = decision

    def deliberate(self, _request):
        return SimpleNamespace(verdict=SimpleNamespace(value=self.decision))


class _FakeLLMClient:
    def __init__(self, response: str = "safe response with accountability") -> None:
        self.response = response
        self.model = "mock-model"
        self.last_metrics = None

    def start_chat(self, history):
        del history
        return self

    def send_message(self, message: str) -> str:
        del message
        return self.response


def _vow_result(
    *,
    blocked: bool = False,
    repair_needed: bool = False,
    flags: list[str] | None = None,
) -> VowEnforcementResult:
    return VowEnforcementResult(
        all_passed=not (blocked or repair_needed or flags),
        results=[],
        blocked=blocked,
        repair_needed=repair_needed,
        flags=flags or [],
    )


def _pipeline(*, council_decision: str = "approve", tension_total: float = 0.5) -> UnifiedPipeline:
    pipeline = UnifiedPipeline(mirror_enabled=False)
    pipeline._get_council = MagicMock(return_value=_FakeCouncil(council_decision))
    pipeline._get_tension_engine = MagicMock(return_value=_FakeTensionEngine(tension_total))
    return pipeline


def test_reflection_verdict_to_dict_includes_nested_vow_payload() -> None:
    verdict = ReflectionVerdict(
        should_revise=True,
        reasons=["council:block"],
        severity=0.9,
        vow_result=_vow_result(blocked=True, flags=["BLOCKED by vow"]),
        council_decision="block",
        tension_delta=0.33,
    )

    payload = verdict.to_dict()

    assert payload["should_revise"] is True
    assert payload["severity"] == 0.9
    assert payload["council_decision"] == "block"
    assert payload["tension_delta"] == 0.33
    assert payload["vow_result"]["blocked"] is True


def test_self_check_returns_no_revision_when_all_guards_pass(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(vow_system.VowEnforcer, "enforce", lambda self, output: _vow_result())
    pipeline = _pipeline(council_decision="approve", tension_total=0.54)

    verdict = pipeline._self_check(
        "Provide a bounded rollout plan with one rollback checkpoint.",
        {"tension_baseline": 0.5},
    )

    assert verdict.should_revise is False
    assert verdict.severity == 0.0
    assert verdict.council_decision == "approve"


def test_self_check_marks_vow_block_as_revision(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        vow_system.VowEnforcer,
        "enforce",
        lambda self, output: _vow_result(blocked=True, flags=["BLOCKED by harm vow"]),
    )
    pipeline = _pipeline()

    verdict = pipeline._self_check("unsafe draft", {"tension_baseline": 0.5})

    assert verdict.should_revise is True
    assert verdict.severity >= 0.8
    assert "BLOCKED by harm vow" in verdict.reasons


def test_self_check_marks_vow_repair_as_revision(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        vow_system.VowEnforcer,
        "enforce",
        lambda self, output: _vow_result(repair_needed=True, flags=["REPAIR needed"]),
    )
    pipeline = _pipeline()

    verdict = pipeline._self_check("needs repair", {"tension_baseline": 0.5})

    assert verdict.should_revise is True
    assert verdict.severity >= 0.5
    assert "REPAIR needed" in verdict.reasons


def test_self_check_marks_council_refine_as_revision(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(vow_system.VowEnforcer, "enforce", lambda self, output: _vow_result())
    pipeline = _pipeline(council_decision="refine")

    verdict = pipeline._self_check("draft", {"tension_baseline": 0.5})

    assert verdict.should_revise is True
    assert verdict.severity >= 0.4
    assert "council:refine" in verdict.reasons


def test_self_check_marks_council_block_as_revision(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(vow_system.VowEnforcer, "enforce", lambda self, output: _vow_result())
    pipeline = _pipeline(council_decision="block")

    verdict = pipeline._self_check("draft", {"tension_baseline": 0.5})

    assert verdict.should_revise is True
    assert verdict.severity >= 0.8
    assert "council:block" in verdict.reasons


def test_self_check_marks_high_tension_delta_as_revision(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(vow_system.VowEnforcer, "enforce", lambda self, output: _vow_result())
    pipeline = _pipeline(council_decision="approve", tension_total=0.9)

    verdict = pipeline._self_check("high tension draft", {"tension_baseline": 0.4})

    assert verdict.should_revise is True
    assert verdict.tension_delta is not None
    assert verdict.tension_delta > 0.25


def test_self_check_does_not_revise_on_flag_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        vow_system.VowEnforcer,
        "enforce",
        lambda self, output: _vow_result(flags=["FLAG: uncertainty disclosure"]),
    )
    pipeline = _pipeline(council_decision="approve", tension_total=0.55)

    verdict = pipeline._self_check("flag only draft", {"tension_baseline": 0.5})

    assert verdict.should_revise is False
    assert verdict.severity == pytest.approx(0.2)


def test_self_check_uses_highest_trigger_for_severity(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        vow_system.VowEnforcer,
        "enforce",
        lambda self, output: _vow_result(repair_needed=True, flags=["REPAIR needed"]),
    )
    pipeline = _pipeline(council_decision="block", tension_total=0.75)

    verdict = pipeline._self_check("stacked issues", {"tension_baseline": 0.45})

    assert verdict.should_revise is True
    assert verdict.severity == pytest.approx(0.9)


def test_self_check_accepts_council_decision_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(vow_system.VowEnforcer, "enforce", lambda self, output: _vow_result())
    pipeline = _pipeline(council_decision="approve")

    verdict = pipeline._self_check(
        "draft",
        {
            "tension_baseline": 0.5,
            "reflection_council_decision": "refine",
            "reflection_skip_council": True,
        },
    )

    assert verdict.council_decision == "refine"
    assert verdict.should_revise is True


def test_process_attaches_reflection_verdict_to_dispatch_trace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pipeline = UnifiedPipeline(mirror_enabled=False)
    pipeline._get_governance_kernel = MagicMock(return_value=None)
    pipeline._get_tonebridge = MagicMock(return_value=None)
    pipeline._get_trajectory = MagicMock(return_value=None)
    pipeline._get_deliberation = MagicMock(return_value=None)
    pipeline._get_council = MagicMock(return_value=None)
    pipeline._get_llm_router = MagicMock(return_value=None)
    pipeline._get_llm_client = MagicMock(return_value=_FakeLLMClient())
    pipeline._get_tension_engine = MagicMock(return_value=_FakeTensionEngine(0.45))
    pipeline._get_drift_monitor = MagicMock(return_value=None)
    monkeypatch.setattr(vow_system.VowEnforcer, "enforce", lambda self, output: _vow_result())

    result = pipeline.process(
        user_message="Provide a concise guarded answer.",
        user_tier="premium",
        user_id="reflection-trace-test",
    )

    reflection = result.dispatch_trace["reflection_verdict"]
    assert reflection["component"] == "reflection"
    assert "should_revise" in reflection["detail"]
