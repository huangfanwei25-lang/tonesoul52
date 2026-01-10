from __future__ import annotations

from typing import List, Optional

from .types import (
    CoherenceScore,
    CouncilVerdict,
    PerspectiveType,
    PerspectiveVote,
    VerdictType,
    VoteDecision,
)


def generate_verdict(
    votes: List[PerspectiveVote],
    coherence: CoherenceScore,
    coherence_threshold: float = 0.6,
    block_threshold: float = 0.3,
) -> CouncilVerdict:
    guardian_vote = next(
        (v for v in votes if v.perspective == PerspectiveType.GUARDIAN),
        None,
    )

    if guardian_vote and guardian_vote.decision == VoteDecision.OBJECT:
        if guardian_vote.confidence > 0.7:
            return CouncilVerdict(
                verdict=VerdictType.BLOCK,
                coherence=coherence,
                votes=votes,
                summary=f"Guardian objection: {guardian_vote.reasoning}",
            )

    overall = coherence.overall
    if overall < block_threshold:
        return CouncilVerdict(
            verdict=VerdictType.BLOCK,
            coherence=coherence,
            votes=votes,
            summary="Coherence too low for safe approval.",
        )

    if overall < coherence_threshold:
        divergent_views = [
            v for v in votes
            if v.decision in (VoteDecision.CONCERN, VoteDecision.OBJECT)
        ]
        stance = _generate_stance_declaration(divergent_views)
        return CouncilVerdict(
            verdict=VerdictType.DECLARE_STANCE,
            coherence=coherence,
            votes=votes,
            summary="Divergent perspectives detected; declaring stance.",
            stance_declaration=stance,
        )

    concerns = [
        v for v in votes if v.decision == VoteDecision.CONCERN
    ]
    if concerns and coherence.min_confidence < 0.5:
        hints = [c.reasoning for c in concerns]
        return CouncilVerdict(
            verdict=VerdictType.REFINE,
            coherence=coherence,
            votes=votes,
            summary="Requests for refinement detected.",
            refinement_hints=hints,
        )

    return CouncilVerdict(
        verdict=VerdictType.APPROVE,
        coherence=coherence,
        votes=votes,
        summary="Consensus achieved across perspectives.",
    )


def _generate_stance_declaration(
    divergent_views: List[PerspectiveVote],
) -> str:
    names = {
        PerspectiveType.GUARDIAN: "Safety Council",
        PerspectiveType.ANALYST: "Analyst Review",
        PerspectiveType.CRITIC: "Critic Lens",
        PerspectiveType.ADVOCATE: "Advocate Voice",
    }
    parts = []
    for v in divergent_views:
        name = names.get(v.perspective, v.perspective.value)
        parts.append(f"- **{name}**: {v.reasoning}")
    if not parts:
        return "No stance available."
    return (
        "Multiple perspectives disagree; stance summary:\n"
        + "\n".join(parts)
    )
