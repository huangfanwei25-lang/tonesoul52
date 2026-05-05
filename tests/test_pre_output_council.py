from tonesoul.council import (
    CoherenceScore,
    PerspectiveType,
    PerspectiveVote,
    PreOutputCouncil,
    VerdictType,
    VoteDecision,
)
from tonesoul.council.base import IPerspective
from tonesoul.council.verdict import generate_verdict


class _LegacyPerspective(IPerspective):
    """Pre-PR #50 plugin shape: no epistemic_label kwarg."""

    @property
    def perspective_type(self):
        return PerspectiveType.ANALYST

    def evaluate(self, draft_output, context, user_intent=None):
        return PerspectiveVote(
            perspective=PerspectiveType.ANALYST,
            decision=VoteDecision.APPROVE,
            confidence=0.8,
            reasoning="legacy plugin accepted",
        )


def test_all_approve():
    """Verdict still APPROVE for benign draft.

    PR #50 (epistemic_label wiring per ratified §3.1+§3.2 thesis-aligned):
    Analyst + Critic now soft-CONCERN on drafts with confidence_band low/medium
    when no evidence_ids in context. This benign draft has no retrieval anchor,
    so 2/5 perspectives now soft-CONCERN. Verdict still APPROVE (1-of-5 CONCERN
    threshold for downgrade per finding #9), but coherence drops below the
    pre-#50 0.7 threshold. To restore high coherence, callers should pass
    evidence_ids in context (raises confidence_band to "high"). The ratified
    thesis is "from-broad-then-narrow if friction is too high"; this assertion
    tracks the new baseline.
    """
    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output="This response supports collaboration and adds helpful context.",
        context={"topic": "geography"},
    )
    assert verdict.verdict == VerdictType.APPROVE
    # Coherence drops to ~0.65 due to 2/5 epistemic_prior CONCERNs.
    # Still above the BLOCK threshold; verdict stays APPROVE.
    assert verdict.coherence.overall > 0.5


def test_legacy_perspective_without_epistemic_label_kwarg_still_runs():
    council = PreOutputCouncil(perspectives=_LegacyPerspective())
    verdict = council.validate(
        draft_output="Legacy plugin output.",
        context={},
        auto_record_self_memory=False,
    )
    assert verdict.votes[0].reasoning == "legacy plugin accepted"
    assert verdict.epistemic_label is not None


def test_ethical_block():
    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output="Attack with a bomb that harms the city.",
        context={"topic": "request"},
    )
    assert verdict.verdict == VerdictType.BLOCK
    assert any(
        v.perspective == PerspectiveType.GUARDIAN and v.decision == VoteDecision.OBJECT
        for v in verdict.votes
    )


def test_art_criticism_stance():
    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output="Art critiques often describe beauty as a subjective decision.",
        context={"topic": "art"},
    )
    # Subjective content with explicit framing ("subjective") is approved by the
    # improved Critic. Unframed subjective claims would still get REFINE/DECLARE_STANCE.
    assert verdict.verdict in {VerdictType.APPROVE, VerdictType.DECLARE_STANCE, VerdictType.REFINE}
    if verdict.verdict == VerdictType.DECLARE_STANCE:
        assert verdict.stance_declaration is not None


def test_needs_clarification():
    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output="A leads to B, B leads to C, so A does not impact C.",
        context={"topic": "logic"},
    )
    assert verdict.verdict == VerdictType.REFINE
    assert verdict.refinement_hints is not None


def test_additional_harm_block():
    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output="The plan describes a weapon and an attack on a target.",
        context={"topic": "safety"},
    )
    assert verdict.verdict == VerdictType.BLOCK
    assert any("Detected high-risk term" in v.reasoning for v in verdict.votes)


def test_coherence_boundary_declares_stance():
    votes = [
        PerspectiveVote(
            perspective=PerspectiveType.CRITIC,
            decision=VoteDecision.CONCERN,
            confidence=0.6,
            reasoning="Subjective critique needs a stance.",
        )
    ]
    coherence = CoherenceScore(
        c_inter=0.6,
        approval_rate=0.0,
        min_confidence=0.3,
        has_strong_objection=False,
    )
    verdict = generate_verdict(
        votes=votes,
        coherence=coherence,
        coherence_threshold=0.6,
        block_threshold=0.3,
    )
    assert verdict.verdict == VerdictType.DECLARE_STANCE


def test_coherence_boundary_approves_at_threshold():
    votes = [
        PerspectiveVote(
            perspective=PerspectiveType.ANALYST,
            decision=VoteDecision.APPROVE,
            confidence=0.9,
            reasoning="Evidence supports approval.",
        ),
        PerspectiveVote(
            perspective=PerspectiveType.ADVOCATE,
            decision=VoteDecision.APPROVE,
            confidence=0.85,
            reasoning="Forward motion is justified.",
        ),
    ]
    coherence = CoherenceScore(
        c_inter=0.6,
        approval_rate=1.0,
        min_confidence=0.85,
        has_strong_objection=False,
    )
    verdict = generate_verdict(
        votes=votes,
        coherence=coherence,
        coherence_threshold=0.6,
        block_threshold=0.3,
    )
    assert verdict.verdict == VerdictType.APPROVE


def test_empty_input():
    council = PreOutputCouncil()
    verdict = council.validate(draft_output="", context={})
    assert verdict.summary
    assert verdict.verdict in {
        VerdictType.APPROVE,
        VerdictType.DECLARE_STANCE,
        VerdictType.REFINE,
    }


def test_long_text_processing():
    council = PreOutputCouncil()
    draft = "neutral " * 1000
    verdict = council.validate(draft_output=draft, context={"topic": "analysis"})
    assert verdict.summary


def test_mixed_signal_input():
    council = PreOutputCouncil()
    draft = "This is harmful bomb content mixed with numbers 123."
    verdict = council.validate(draft_output=draft, context={"topic": "safety"})
    assert verdict.verdict == VerdictType.BLOCK


def test_multiple_harmful_keywords():
    council = PreOutputCouncil()
    draft = "kill and bomb and harm"
    verdict = council.validate(draft_output=draft, context={"topic": "safety"})
    assert verdict.verdict == VerdictType.BLOCK
    assert verdict.coherence.has_strong_objection


def test_guardian_override_precedence():
    council = PreOutputCouncil()
    draft = "Kill with bombs but keep analysis detailed."
    verdict = council.validate(draft_output=draft, context={"topic": "safety"})
    assert verdict.verdict == VerdictType.BLOCK
    guardian_votes = [v for v in verdict.votes if v.perspective == PerspectiveType.GUARDIAN]
    assert guardian_votes and guardian_votes[0].decision == VoteDecision.OBJECT


def test_stance_declaration_content():
    council = PreOutputCouncil()
    # Unframed subjective claim — Critic flags it, but a single CONCERN among
    # 4 APPROVEs produces APPROVE (coherence > threshold). This is correct
    # behaviour: one dissent doesn't block when the rest of the council agrees.
    # To get REFINE/DECLARE_STANCE, multiple perspectives must object.
    draft = "This is the greatest movie ever made and nothing compares."
    verdict = council.validate(draft_output=draft, context={"topic": "art"})
    critic_votes = [v for v in verdict.votes if v.perspective == PerspectiveType.CRITIC]
    assert critic_votes[0].decision == VoteDecision.CONCERN
    assert (
        "subjective" in critic_votes[0].reasoning.lower()
        or "stance" in critic_votes[0].reasoning.lower()
    )
