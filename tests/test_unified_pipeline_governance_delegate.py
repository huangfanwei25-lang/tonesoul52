from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from tonesoul.unified_pipeline import UnifiedPipeline


class _FakeVerdict:
    def __init__(self, name: str = "APPROVE") -> None:
        self.verdict = SimpleNamespace(name=name)

    def to_dict(self) -> dict:
        return {"verdict": self.verdict.name.lower(), "metadata": {}}


class _FakeKernel:
    def __init__(self, should_convene: bool) -> None:
        self._should_convene = should_convene
        self.should_convene_council = MagicMock(return_value=(should_convene, "kernel_decision"))

    def build_routing_trace(self, *, route, journal_eligible, reason):
        return {
            "route": route,
            "journal_eligible": journal_eligible,
            "reason": reason,
        }

    def compute_prior_governance_friction(self, prior_tension, user_message):
        return None

    def compute_runtime_friction(self, *, prior_tension, tone_strength):
        return None


def _build_pipeline(*, should_convene: bool):
    pipeline = UnifiedPipeline()
    kernel = _FakeKernel(should_convene=should_convene)
    council = MagicMock()
    council.deliberate.return_value = _FakeVerdict()
    pipeline._get_governance_kernel = MagicMock(return_value=kernel)
    pipeline._get_llm_client = MagicMock(return_value=None)
    pipeline._get_tonebridge = MagicMock(return_value=None)
    pipeline._get_trajectory = MagicMock(return_value=None)
    pipeline._get_deliberation = MagicMock(return_value=None)
    pipeline._get_tension_engine = MagicMock(return_value=None)
    pipeline._get_council = MagicMock(return_value=council)
    return pipeline, kernel, council


def test_pipeline_skips_council_when_kernel_declines_convening() -> None:
    pipeline, kernel, council = _build_pipeline(should_convene=False)

    result = pipeline.process(
        user_message="Please give me a detailed engineering review of this runtime design.",
        user_tier="premium",
        user_id="kernel-skip-test",
    )

    council.deliberate.assert_not_called()
    kernel.should_convene_council.assert_called_once()
    assert result.dispatch_trace["council"]["convened"] is False
    assert result.dispatch_trace["council"]["reason"] == "kernel_decision"


def test_pipeline_convenes_council_when_kernel_requests_it() -> None:
    pipeline, kernel, council = _build_pipeline(should_convene=True)

    result = pipeline.process(
        user_message="Please give me a detailed engineering review of this runtime design.",
        user_tier="premium",
        user_id="kernel-convene-test",
    )

    # At least 2 deliberations (main + reflection); reflex arc may add more
    assert council.deliberate.call_count >= 2
    kernel.should_convene_council.assert_called_once()
    assert result.dispatch_trace["council"]["convened"] is True
    assert result.dispatch_trace["council"]["reason"] == "kernel_decision"
