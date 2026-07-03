from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from types import ModuleType
from typing import Optional

import pytest

import tonesoul.council.pre_output_council as pre_output_module
import tonesoul.deliberation.gravity as gravity_module
from tonesoul.council.base import IPerspective
from tonesoul.council.types import (
    PerspectiveType as CouncilPerspectiveType,
)
from tonesoul.council.types import (
    PerspectiveVote,
    VerdictType,
    VoteDecision,
)
from tonesoul.council.voting_evolution import CouncilEvolution
from tonesoul.deliberation.persona_track_record import PersonaTrackRecord
from tonesoul.deliberation.types import (
    MIN_SHARE,
    DeliberationContext,
    DeliberationWeights,
    ViewPoint,
)
from tonesoul.deliberation.types import (
    PerspectiveType as DeliberationPerspectiveType,
)


def _patch_council_config(monkeypatch: pytest.MonkeyPatch, module: ModuleType, **flags) -> None:
    council = replace(module.SOUL.council, **flags)
    monkeypatch.setattr(module, "SOUL", replace(module.SOUL, council=council))


@dataclass
class StaticPerspective(IPerspective):
    kind: CouncilPerspectiveType
    decision: VoteDecision
    confidence: float = 0.9

    @property
    def perspective_type(self) -> CouncilPerspectiveType:
        return self.kind

    def evaluate(
        self,
        draft_output: str,
        context: dict,
        user_intent: Optional[str] = None,
        epistemic_label: Optional[object] = None,
    ) -> PerspectiveVote:
        return PerspectiveVote(
            perspective=self.kind,
            decision=self.decision,
            confidence=self.confidence,
            reasoning=f"{self.kind.value} voted {self.decision.value}",
        )


class FakeEvolution:
    def __init__(self, weights: dict[str, float]) -> None:
        self.weights = weights
        self.calls = 0

    def get_weights(self) -> dict[str, float]:
        self.calls += 1
        return dict(self.weights)


def _verdict_perspectives() -> list[StaticPerspective]:
    return [
        StaticPerspective(CouncilPerspectiveType.GUARDIAN, VoteDecision.APPROVE),
        StaticPerspective(CouncilPerspectiveType.ANALYST, VoteDecision.APPROVE),
        StaticPerspective(CouncilPerspectiveType.CRITIC, VoteDecision.CONCERN),
        StaticPerspective(CouncilPerspectiveType.ADVOCATE, VoteDecision.APPROVE),
        StaticPerspective(CouncilPerspectiveType.AXIOMATIC, VoteDecision.APPROVE),
    ]


def test_evolution_weight_flag_debinds_pre_output_verdict(monkeypatch: pytest.MonkeyPatch) -> None:
    heavy_critic = {
        "guardian": 1.0,
        "analyst": 1.0,
        "critic": 10.0,
        "advocate": 1.0,
        "axiomatic": 1.0,
    }

    _patch_council_config(
        monkeypatch,
        pre_output_module,
        evolution_weights_applied=False,
    )
    off_evolution = FakeEvolution(heavy_critic)
    off_council = pre_output_module.PreOutputCouncil(
        perspectives=_verdict_perspectives(),
        coherence_threshold=0.7,
        block_threshold=0.3,
    )
    off_council._evolution = off_evolution

    off_verdict = off_council.validate(
        draft_output="same draft",
        context={},
        auto_record_self_memory=False,
    )

    assert off_evolution.calls == 0
    assert off_verdict.verdict == VerdictType.APPROVE

    _patch_council_config(
        monkeypatch,
        pre_output_module,
        evolution_weights_applied=True,
    )
    on_evolution = FakeEvolution(heavy_critic)
    on_council = pre_output_module.PreOutputCouncil(
        perspectives=_verdict_perspectives(),
        coherence_threshold=0.7,
        block_threshold=0.3,
    )
    on_council._evolution = on_evolution

    on_verdict = on_council.validate(
        draft_output="same draft",
        context={},
        auto_record_self_memory=False,
    )

    assert on_evolution.calls == 1
    assert on_verdict.verdict == VerdictType.DECLARE_STANCE


def test_evolution_flag_off_keeps_suppression_observability(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _patch_council_config(
        monkeypatch,
        pre_output_module,
        evolution_weights_applied=False,
    )
    evolution = CouncilEvolution(state_path=tmp_path / "council_evolution.json")

    for _ in range(5):
        evolution.record_deliberation(
            perspective_verdicts={
                "guardian": "approve",
                "analyst": "approve",
                "critic": "block",
                "advocate": "approve",
                "axiomatic": "approve",
            },
            final_verdict="approve",
            perspective_confidences={
                "guardian": 0.8,
                "analyst": 0.8,
                "critic": 0.91,
                "advocate": 0.8,
                "axiomatic": 0.8,
            },
        )
        evolution.evolve_weights()

    suppression = evolution.get_summary()["suppression_observability"]

    assert suppression["flag"] is True
    assert suppression["suppressed_perspectives"][0]["perspective"] == "critic"


def _viewpoint(perspective: DeliberationPerspectiveType) -> ViewPoint:
    return ViewPoint(
        perspective=perspective,
        reasoning=f"{perspective.value} reasoning",
        proposed_response=f"{perspective.value} response",
        confidence=0.8,
        safety_risk=0.2,
    )


def _biased_track_record(path: Path) -> PersonaTrackRecord:
    track = PersonaTrackRecord.create(path)
    for _ in range(10):
        track.record_outcome("muse", "approve", resonance_state="resonance")
    for _ in range(10):
        track.record_outcome("logos", "block", resonance_state="resonance")
    return track


def test_persona_multiplier_flag_controls_track_record_bias(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    track = _biased_track_record(tmp_path / "persona_track_record.json")
    viewpoints = [
        _viewpoint(DeliberationPerspectiveType.MUSE),
        _viewpoint(DeliberationPerspectiveType.LOGOS),
        _viewpoint(DeliberationPerspectiveType.AEGIS),
    ]
    context = DeliberationContext(user_input="test", resonance_state="resonance")

    _patch_council_config(
        monkeypatch,
        gravity_module,
        persona_multiplier_applied=False,
    )
    baseline = gravity_module.SemanticGravity().calculate_weights(viewpoints, context)
    off_weights = gravity_module.SemanticGravity(track_record=track).calculate_weights(
        viewpoints,
        context,
    )

    assert off_weights.muse == pytest.approx(baseline.muse)
    assert off_weights.logos == pytest.approx(baseline.logos)
    assert off_weights.aegis == pytest.approx(baseline.aegis)

    _patch_council_config(
        monkeypatch,
        gravity_module,
        persona_multiplier_applied=True,
    )
    on_weights = gravity_module.SemanticGravity(track_record=track).calculate_weights(
        viewpoints,
        context,
    )

    assert on_weights.muse > off_weights.muse
    assert on_weights.logos < off_weights.logos


def test_normalize_applies_minimum_share_floor_after_normalization() -> None:
    weights = DeliberationWeights(muse=100.0, logos=1.0, aegis=0.001)

    weights.normalize()

    assert weights.muse >= MIN_SHARE
    assert weights.logos >= MIN_SHARE
    assert weights.aegis >= MIN_SHARE
    assert weights.muse + weights.logos + weights.aegis == pytest.approx(1.0)
