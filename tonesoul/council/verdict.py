from __future__ import annotations

from typing import List, Union

from .summary_generator import build_divergence_analysis, format_stance_declaration
from .types import (
    CoherenceScore,
    CouncilVerdict,
    PerspectiveType,
    PerspectiveVote,
    VerdictType,
    VoteDecision,
)


def _is_guardian(value: Union[PerspectiveType, str]) -> bool:
    if isinstance(value, PerspectiveType):
        return value == PerspectiveType.GUARDIAN
    return str(value).lower() == PerspectiveType.GUARDIAN.value


def _is_advocate(value: Union[PerspectiveType, str]) -> bool:
    if isinstance(value, PerspectiveType):
        return value == PerspectiveType.ADVOCATE
    return str(value).lower() == PerspectiveType.ADVOCATE.value


def _is_refinement_concern(vote: PerspectiveVote) -> bool:
    # Avoid refinement solely due to advocate tone/intent concerns.
    return not _is_advocate(vote.perspective)


def _perspective_label(value: Union[PerspectiveType, str]) -> str:
    names = {
        PerspectiveType.GUARDIAN: "Safety Council",
        PerspectiveType.ANALYST: "Analyst Review",
        PerspectiveType.CRITIC: "Critic Lens",
        PerspectiveType.ADVOCATE: "Advocate Voice",
    }
    if isinstance(value, PerspectiveType):
        return names.get(value, value.value)
    try:
        key = PerspectiveType(str(value).lower())
    except ValueError:
        return str(value)
    return names.get(key, key.value)


def generate_verdict(
    votes: List[PerspectiveVote],
    coherence: CoherenceScore,
    coherence_threshold: float = 0.6,
    block_threshold: float = 0.3,
) -> CouncilVerdict:

    guardian_vote = next(
        (v for v in votes if _is_guardian(v.perspective)),
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
        divergence = build_divergence_analysis(votes)
        stance = format_stance_declaration(divergence)
        return CouncilVerdict(
            verdict=VerdictType.DECLARE_STANCE,
            coherence=coherence,
            votes=votes,
            summary="Divergent perspectives detected; declaring stance.",
            stance_declaration=stance,
        )

    concerns = [v for v in votes if v.decision == VoteDecision.CONCERN]
    if concerns and coherence.min_confidence < 0.5:
        if not any(_is_refinement_concern(v) for v in concerns):
            return CouncilVerdict(
                verdict=VerdictType.APPROVE,
                coherence=coherence,
                votes=votes,
                summary="Advocate concerns only; approval granted.",
            )
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
    parts = []
    for v in divergent_views:
        label = _perspective_label(v.perspective)
        parts.append(f"- **{label}**: {v.reasoning}")
    if not parts:
        return "No stance available."
    return "Multiple perspectives disagree; stance summary:\n" + "\n".join(parts)
