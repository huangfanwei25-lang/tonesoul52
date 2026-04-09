from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from tonesoul.reflection import ReflectionVerdict, build_revision_prompt
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
        normalized_tier = str(getattr(tier, "value", tier) or "").strip().lower()
        if normalized_tier not in {"local", "cloud"}:
            normalized_alert = str(getattr(alert_level, "value", alert_level) or "").strip().upper()
            normalized_tier = "cloud" if normalized_alert in {"L2", "L3"} else "local"
        self.last_thinking_tier = normalized_tier
        self.tiers.append(normalized_tier)
        return self.chat(history=history, prompt=prompt)

    def chat(self, *, history=None, prompt: str) -> str:
        del history
        self.prompts.append(prompt)
        if not self._responses:
            raise AssertionError("router chat exhausted")
        return self._responses.pop(0)


class _FakeVerdict:
    def __init__(self, name: str = "APPROVE") -> None:
        self.verdict = SimpleNamespace(name=name)

    def to_dict(self) -> dict:
        return {"verdict": self.verdict.name.lower(), "metadata": {}}


class _FakeCouncil:
    def __init__(self, decision: str = "approve") -> None:
        self.decision = decision
        self.calls = []

    def deliberate(self, request):
        self.calls.append(request)
        return SimpleNamespace(verdict=SimpleNamespace(value=self.decision))


def _pipeline(*, router: _FakeRouter, council: object | None = None) -> UnifiedPipeline:
    pipeline = UnifiedPipeline(mirror_enabled=False)
    pipeline._llm_router = router
    pipeline._llm_client = SimpleNamespace(model="mock-model", last_metrics=None)
    pipeline._get_tonebridge = MagicMock(return_value=None)
    pipeline._get_trajectory = MagicMock(return_value=None)
    pipeline._get_deliberation = MagicMock(return_value=None)
    pipeline._get_tension_engine = MagicMock(return_value=None)
    pipeline._get_council = MagicMock(return_value=council)
    pipeline._get_governance_kernel = MagicMock(return_value=None)
    pipeline._get_drift_monitor = MagicMock(return_value=None)
    # Reflection-loop coverage should not depend on live reflex posture or persisted soul state.
    pipeline._compute_reflex_decision = MagicMock(return_value=None)
    return pipeline


def test_build_revision_prompt_includes_reasons_and_constraints() -> None:
    verdict = ReflectionVerdict(
        should_revise=True,
        reasons=["council:block", "tension_delta:0.33"],
        severity=0.9,
        council_decision="block",
        tension_delta=0.33,
    )

    prompt = build_revision_prompt("Draft answer.", verdict)

    assert "Why rewrite:" in prompt
    assert "council:block" in prompt
    assert "Revision constraints:" in prompt
    assert "Draft to revise:" in prompt
    assert "Goal function:" in prompt
    assert "Priority rules:" in prompt
    assert "- P0:" in prompt
    assert "- P1:" in prompt
    assert "- P2:" in prompt
    assert "Evidence discipline:" in prompt
    assert "Recovery instructions:" in prompt


def test_build_revision_prompt_uses_bounded_evidence_and_recovery_guidance() -> None:
    verdict = ReflectionVerdict(
        should_revise=True,
        reasons=["repair"],
        severity=0.6,
        council_decision="refine",
        tension_delta=0.31,
    )

    prompt = build_revision_prompt("Draft answer.", verdict)

    assert "only repair evidence" in prompt
    assert "Do not invent support for claims" in prompt
    assert "bounded repair instruction" in prompt
    assert "smallest safe correction" in prompt
    assert "remove or soften it instead of guessing" in prompt


def test_build_revision_prompt_truncates_long_draft() -> None:
    verdict = ReflectionVerdict(should_revise=True, reasons=["repair"], severity=0.5)
    draft = "x" * 5005

    prompt = build_revision_prompt(draft, verdict)

    assert "x" * 4100 not in prompt
    assert "..." in prompt


def test_process_without_revision_sets_reflection_count_zero() -> None:
    router = _FakeRouter(["initial response"])
    pipeline = _pipeline(router=router, council=None)
    pipeline._self_check = MagicMock(
        return_value=ReflectionVerdict(should_revise=False, reasons=[], severity=0.0)
    )

    result = pipeline.process(
        user_message="Summarize a bounded rollout plan.",
        user_tier="premium",
        user_id="reflection-loop-none",
    )

    assert result.response == "initial response"
    assert result.dispatch_trace["reflection_count"] == 0
    assert len(result.dispatch_trace["reflection_verdicts"]) == 1


def test_process_runs_one_revision_then_stops() -> None:
    router = _FakeRouter(["initial response", "revised response"])
    pipeline = _pipeline(router=router, council=None)
    pipeline._self_check = MagicMock(
        side_effect=[
            ReflectionVerdict(should_revise=True, reasons=["repair"], severity=0.5),
            ReflectionVerdict(should_revise=False, reasons=[], severity=0.0),
        ]
    )

    result = pipeline.process(
        user_message="Refine this answer with one rollback checkpoint.",
        user_tier="premium",
        user_id="reflection-loop-one",
    )

    assert result.response == "revised response"
    assert result.dispatch_trace["reflection_count"] == 1
    assert len(result.dispatch_trace["reflection_verdicts"]) == 2
    assert router.prompts[1].startswith("Revise the draft below")
    assert "Goal function:" in router.prompts[1]


def test_process_caps_revisions_at_max_two() -> None:
    router = _FakeRouter(["initial response", "revised once", "revised twice"])
    pipeline = _pipeline(router=router, council=None)
    pipeline._self_check = MagicMock(
        side_effect=[
            ReflectionVerdict(should_revise=True, reasons=["repair-1"], severity=0.5),
            ReflectionVerdict(should_revise=True, reasons=["repair-2"], severity=0.5),
        ]
    )

    result = pipeline.process(
        user_message="Keep revising until stable.",
        user_tier="premium",
        user_id="reflection-loop-max",
    )

    assert result.response == "revised twice"
    assert result.dispatch_trace["reflection_count"] == 2


def test_dispatch_trace_stores_reflection_verdict_history() -> None:
    router = _FakeRouter(["initial response"])
    pipeline = _pipeline(router=router, council=None)
    pipeline._self_check = MagicMock(
        return_value=ReflectionVerdict(should_revise=False, reasons=["flag"], severity=0.2)
    )

    result = pipeline.process(
        user_message="Return a concise answer.",
        user_tier="premium",
        user_id="reflection-history",
    )

    history = result.dispatch_trace["reflection_verdicts"]
    assert isinstance(history, list)
    assert history[0]["severity"] == 0.2


def test_dispatch_trace_stores_last_reflection_section() -> None:
    router = _FakeRouter(["initial response"])
    pipeline = _pipeline(router=router, council=None)
    pipeline._self_check = MagicMock(
        return_value=ReflectionVerdict(should_revise=False, reasons=[], severity=0.0)
    )

    result = pipeline.process(
        user_message="Give a practical answer.",
        user_tier="premium",
        user_id="reflection-section",
    )

    section = result.dispatch_trace["reflection_verdict"]
    assert section["component"] == "reflection"
    assert section["detail"]["should_revise"] is False


def test_reflection_loop_keeps_original_response_when_self_check_raises() -> None:
    router = _FakeRouter(["initial response"])
    pipeline = _pipeline(router=router, council=None)
    pipeline._self_check = MagicMock(side_effect=RuntimeError("reflection exploded"))

    result = pipeline.process(
        user_message="Stay stable under reflection errors.",
        user_tier="premium",
        user_id="reflection-error",
    )

    assert result.response == "initial response"
    assert result.dispatch_trace.get("reflection_count", 0) == 0


def test_reflection_loop_uses_router_for_revision_prompt() -> None:
    router = _FakeRouter(["initial response", "revised response"])
    pipeline = _pipeline(router=router, council=None)
    pipeline._self_check = MagicMock(
        side_effect=[
            ReflectionVerdict(should_revise=True, reasons=["council:refine"], severity=0.4),
            ReflectionVerdict(should_revise=False, reasons=[], severity=0.0),
        ]
    )

    pipeline.process(
        user_message="Refine this answer.",
        user_tier="premium",
        user_id="reflection-router",
    )

    assert len(router.prompts) == 2
    assert "council:refine" in router.prompts[1]


def test_reflection_self_check_uses_council_without_custom_perspectives() -> None:
    router = _FakeRouter(["initial response"])
    council = _FakeCouncil(decision="approve")
    pipeline = _pipeline(router=router, council=council)

    verdict = pipeline._self_check(
        "draft",
        {
            "language": "zh",
            "tension_baseline": 0.5,
        },
    )

    assert verdict.council_decision == "approve"
    assert council.calls
    assert council.calls[0].perspectives is None


def test_governance_delegate_path_now_runs_reflection_and_final_council() -> None:
    router = _FakeRouter(["initial response"])
    council = _FakeCouncil(decision="approve")
    pipeline = _pipeline(router=router, council=council)

    result = pipeline.process(
        user_message="Provide a detailed engineering review.",
        user_tier="premium",
        user_id="reflection-council-count",
    )

    assert result.dispatch_trace["reflection_count"] == 0
    assert len(council.calls) == 2
