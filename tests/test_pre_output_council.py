from tonesoul.council import (
    PerspectiveType,
    PreOutputCouncil,
    VerdictType,
    VoteDecision,
)


def test_all_approve():
    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output="This response supports collaboration and adds helpful context.",
        context={"topic": "geography"},
    )
    assert verdict.verdict == VerdictType.APPROVE
    assert verdict.coherence.overall > 0.7


def test_ethical_block():
    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output="Attack with a bomb that harms the city.",
        context={"topic": "request"},
    )
    assert verdict.verdict == VerdictType.BLOCK
    assert any(
        v.perspective == PerspectiveType.GUARDIAN
        and v.decision == VoteDecision.OBJECT
        for v in verdict.votes
    )


def test_art_criticism_stance():
    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output="Art critiques often describe beauty as a subjective decision.",
        context={"topic": "art"},
    )
    assert verdict.verdict == VerdictType.DECLARE_STANCE
    assert verdict.stance_declaration is not None


def test_needs_clarification():
    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output="A leads to B, B leads to C, so A does not impact C.",
        context={"topic": "logic"},
    )
    assert verdict.verdict == VerdictType.REFINE
    assert verdict.refinement_hints is not None
