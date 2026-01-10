from tonesoul.council import PreOutputCouncil, VerdictType, VoteDecision, PerspectiveType
from tonesoul.council.perspective_factory import PerspectiveFactory


def test_create_council_default():
    council = PerspectiveFactory.create_council()
    assert len(council) == 4
    types = {p.perspective_type for p in council}
    assert PerspectiveType.GUARDIAN in types
    assert PerspectiveType.ANALYST in types
    assert PerspectiveType.CRITIC in types
    assert PerspectiveType.ADVOCATE in types


def test_create_council_tool_fallback():
    def failing_tool(_output: str, _context: dict) -> dict:
        raise RuntimeError("boom")

    council = PerspectiveFactory.create_council({
        "guardian": {"mode": "tool", "tool": failing_tool},
    })
    guardian = next(
        (p for p in council if p.perspective_type == PerspectiveType.GUARDIAN),
        None,
    )
    assert guardian is not None
    vote = guardian.evaluate("No safety flags here.", context={})
    assert vote.perspective == PerspectiveType.GUARDIAN
    assert vote.decision == VoteDecision.APPROVE


def test_pre_output_council_accepts_factory_perspectives():
    perspectives = PerspectiveFactory.create_council()
    council = PreOutputCouncil(perspectives=perspectives)
    verdict = council.validate(
        draft_output="This response supports collaboration and adds helpful context.",
        context={"topic": "geography"},
    )
    assert verdict.verdict == VerdictType.APPROVE
