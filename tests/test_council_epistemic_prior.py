"""Tests for PR #50 — epistemic_label wired into Analyst + Critic.

Per ratified §3.1 (A: both Analyst AND Critic consume) and §3.2 (B: low AND
medium both trigger). Soft prior at confidence 0.55. Resolves Day 1
calibration sprint finding #3 (epistemic_label captured but not consumed).
"""

from __future__ import annotations

from tonesoul.council.epistemic_labeler import EpistemicLabel
from tonesoul.council.perspectives.advocate import AdvocatePerspective
from tonesoul.council.perspectives.analyst import AnalystPerspective
from tonesoul.council.perspectives.axiomatic_inference import AxiomaticInference
from tonesoul.council.perspectives.critic import CriticPerspective
from tonesoul.council.perspectives.guardian import GuardianPerspective
from tonesoul.council.types import PerspectiveType, VoteDecision


def _label(band: str, notes: str = "test note") -> EpistemicLabel:
    return EpistemicLabel(
        status="generated",
        source_weight="inferred",
        confidence_band=band,
        refusal_eligible=False,
        framing_required=False,
        framing_present=None,
        evidence_refs=[],
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Analyst soft prior (primary consumer)
# ---------------------------------------------------------------------------


def test_analyst_soft_concern_on_low_confidence_label() -> None:
    """Analyst CONCERNs at conf 0.55 when label.confidence_band == 'low'."""
    analyst = AnalystPerspective()
    label = _label("low", "novel composition without retrieval anchor")
    vote = analyst.evaluate(
        "This is some neutral content that does not trip any keyword.", {}, epistemic_label=label
    )
    assert vote.decision == VoteDecision.CONCERN
    assert vote.confidence == 0.55
    assert "epistemic prior" in vote.reasoning.lower()
    assert vote.evidence_chain[-1]["branch"] == "epistemic_prior_ungrounded"
    assert vote.evidence_chain[-1]["type"] == "substantive"


def test_analyst_soft_concern_on_medium_confidence_label() -> None:
    """Per ratified §3.2 B: medium also triggers (broader thesis-aligned)."""
    analyst = AnalystPerspective()
    label = _label("medium", "structured factual claim without retrieval context")
    vote = analyst.evaluate(
        "This is some neutral content that does not trip any keyword.", {}, epistemic_label=label
    )
    assert vote.decision == VoteDecision.CONCERN
    assert vote.confidence == 0.55


def test_analyst_does_not_fire_on_high_confidence_label() -> None:
    """High confidence band → no soft prior, default-fallback approve."""
    analyst = AnalystPerspective()
    label = _label("high")
    vote = analyst.evaluate(
        "This is some neutral content that does not trip any keyword.", {}, epistemic_label=label
    )
    assert vote.decision == VoteDecision.APPROVE
    assert vote.evidence_chain[-1]["branch"] == "factual_coherence_acceptable"


def test_analyst_does_not_fire_on_unknown_confidence_label() -> None:
    """Unknown band → no soft prior."""
    analyst = AnalystPerspective()
    label = _label("unknown")
    vote = analyst.evaluate(
        "This is some neutral content that does not trip any keyword.", {}, epistemic_label=label
    )
    assert vote.decision == VoteDecision.APPROVE


def test_analyst_does_not_fire_when_no_label_passed() -> None:
    """No label → no soft prior; existing default behaviour preserved."""
    analyst = AnalystPerspective()
    vote = analyst.evaluate("This is some neutral content that does not trip any keyword.", {})
    assert vote.decision == VoteDecision.APPROVE


def test_analyst_existing_branch_wins_over_soft_prior() -> None:
    """When numerical_pattern fires, soft prior does not double-fire."""
    analyst = AnalystPerspective()
    label = _label("low")
    vote = analyst.evaluate("Performance improved by 73% in production.", {}, epistemic_label=label)
    # numerical_pattern returns CONCERN with reasoning citing the pattern,
    # NOT the epistemic prior reasoning.
    assert vote.decision == VoteDecision.CONCERN
    assert "epistemic prior" not in vote.reasoning.lower()
    assert vote.evidence_chain[-1]["branch"] != "epistemic_prior_ungrounded"


# ---------------------------------------------------------------------------
# Critic soft prior (secondary consumer per ratified §3.1 A)
# ---------------------------------------------------------------------------


def test_critic_soft_concern_on_low_confidence_label() -> None:
    """Critic CONCERNs at conf 0.55 when label.confidence_band == 'low'."""
    critic = CriticPerspective()
    label = _label("low", "novel composition without retrieval anchor")
    vote = critic.evaluate(
        "This is some neutral content that does not trip any keyword.", {}, epistemic_label=label
    )
    assert vote.decision == VoteDecision.CONCERN
    assert vote.confidence == 0.55
    assert vote.evidence_chain[-1]["branch"] == "epistemic_prior_ungrounded"


def test_critic_soft_concern_on_medium_confidence_label() -> None:
    """§3.2 B: medium also triggers in Critic (mirrors Analyst)."""
    critic = CriticPerspective()
    label = _label("medium")
    vote = critic.evaluate(
        "This is some neutral content that does not trip any keyword.", {}, epistemic_label=label
    )
    assert vote.decision == VoteDecision.CONCERN


def test_critic_does_not_fire_on_high_confidence_label() -> None:
    """High band → default-fallback approve unchanged."""
    critic = CriticPerspective()
    label = _label("high")
    vote = critic.evaluate(
        "This is some neutral content that does not trip any keyword.",
        {},
        epistemic_label=label,
    )
    assert vote.decision == VoteDecision.APPROVE
    assert vote.evidence_chain[-1]["branch"] == "no_quality_concerns"


def test_critic_existing_branch_wins_over_soft_prior() -> None:
    """When subjective+overconfidence fires, soft prior does not double-fire."""
    critic = CriticPerspective()
    label = _label("low")
    vote = critic.evaluate(
        "This movie is undeniably the greatest film ever made.",
        {},
        epistemic_label=label,
    )
    assert vote.decision == VoteDecision.CONCERN
    assert "epistemic prior" not in vote.reasoning.lower()


# ---------------------------------------------------------------------------
# Other 3 perspectives accept kwarg without behaviour change (regression)
# ---------------------------------------------------------------------------


def test_guardian_ignores_epistemic_label() -> None:
    """Guardian accepts the kwarg but does not consume; behaviour unchanged."""
    guardian = GuardianPerspective()
    label = _label("low")
    # Same draft with vs without label should produce identical decision.
    vote_with = guardian.evaluate("The weather is nice.", {}, epistemic_label=label)
    vote_without = guardian.evaluate("The weather is nice.", {})
    assert vote_with.decision == vote_without.decision
    assert vote_with.reasoning == vote_without.reasoning


def test_advocate_ignores_epistemic_label() -> None:
    """Advocate accepts the kwarg but does not consume; behaviour unchanged."""
    advocate = AdvocatePerspective()
    label = _label("low")
    vote_with = advocate.evaluate(
        "The config file lives at /etc/main.yaml.", {}, epistemic_label=label
    )
    vote_without = advocate.evaluate("The config file lives at /etc/main.yaml.", {})
    assert vote_with.decision == vote_without.decision


def test_axiomatic_ignores_epistemic_label() -> None:
    """Axiomatic accepts the kwarg but does not consume; behaviour unchanged."""
    axiomatic = AxiomaticInference()
    label = _label("low")
    vote_with = axiomatic.evaluate("The system processes batches.", {}, epistemic_label=label)
    vote_without = axiomatic.evaluate("The system processes batches.", {})
    assert vote_with.decision == vote_without.decision


# ---------------------------------------------------------------------------
# End-to-end via PreOutputCouncil
# ---------------------------------------------------------------------------


def test_council_fires_soft_priors_on_neutral_draft() -> None:
    """End-to-end: benign draft with no retrieval anchor produces 2 soft-prior
    CONCERNs from Analyst + Critic; verdict still APPROVE (below downgrade
    threshold), but coherence reflects the dissent."""
    from tonesoul.council.pre_output_council import PreOutputCouncil

    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output="A neutral statement that asks nothing and offers nothing.",
        context={"topic": "geography"},
    )

    soft_priors = [
        v
        for v in verdict.votes
        if v.decision == VoteDecision.CONCERN
        and v.evidence_chain
        and v.evidence_chain[-1].get("branch") == "epistemic_prior_ungrounded"
    ]
    # Both Analyst and Critic should fire (per ratified §3.1 A)
    assert len(soft_priors) == 2
    perspectives_firing = {v.perspective for v in soft_priors}
    assert PerspectiveType.ANALYST in perspectives_firing
    assert PerspectiveType.CRITIC in perspectives_firing


def test_council_does_not_fire_soft_priors_when_evidence_ids_present() -> None:
    """End-to-end: when context has evidence_ids, label is high → no soft prior."""
    from tonesoul.council.pre_output_council import PreOutputCouncil

    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output="A statement supported by evidence.",
        # epistemic_labeler reads evidence_refs (not evidence_ids); see
        # _RETRIEVAL_CONTEXT_KEYS in epistemic_labeler.py.
        context={"topic": "geography", "evidence_refs": ["src-1", "src-2"]},
    )
    # Verdict's epistemic_label should be high band
    assert verdict.epistemic_label.confidence_band == "high"
    # No soft-prior CONCERNs
    soft_priors = [
        v
        for v in verdict.votes
        if v.decision == VoteDecision.CONCERN
        and v.evidence_chain
        and v.evidence_chain[-1].get("branch") == "epistemic_prior_ungrounded"
    ]
    assert len(soft_priors) == 0
