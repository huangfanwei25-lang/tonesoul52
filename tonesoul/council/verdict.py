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

__ts_layer__ = "governance"
__ts_purpose__ = "Verdict engine: compute final council decision from aggregated perspective votes."


def _is_guardian(value: Union[PerspectiveType, str]) -> bool:
    if isinstance(value, PerspectiveType):
        return value == PerspectiveType.GUARDIAN
    return str(value).lower() == PerspectiveType.GUARDIAN.value


def _is_advocate(value: Union[PerspectiveType, str]) -> bool:
    if isinstance(value, PerspectiveType):
        return value == PerspectiveType.ADVOCATE
    return str(value).lower() == PerspectiveType.ADVOCATE.value


def _is_axiomatic(value: Union[PerspectiveType, str]) -> bool:
    if isinstance(value, PerspectiveType):
        return value == PerspectiveType.AXIOMATIC
    return str(value).lower() == PerspectiveType.AXIOMATIC.value


def _is_refinement_concern(vote: PerspectiveVote) -> bool:
    # Avoid refinement solely due to advocate tone/intent concerns.
    return not _is_advocate(vote.perspective)


def _final_branch(vote: PerspectiveVote) -> dict:
    if not vote.evidence_chain:
        return {}
    for entry in reversed(vote.evidence_chain):
        if isinstance(entry, dict) and entry.get("branch"):
            return entry
    return {}


def _is_soft_epistemic_prior(vote: PerspectiveVote) -> bool:
    return _final_branch(vote).get("branch") == "epistemic_prior_ungrounded"


def _is_actionable_substantive_concern(vote: PerspectiveVote) -> bool:
    branch = _final_branch(vote)
    return (
        _is_refinement_concern(vote)
        and branch.get("type") == "substantive"
        and not _is_soft_epistemic_prior(vote)
    )


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

    # When both Guardian and Axiomatic raise concerns, the output has
    # crossed a governance boundary (e.g. axiom violation, overclaim).
    # This should trigger REFINE regardless of min_confidence, because
    # the two "spirit of the law" perspectives agreeing is a strong signal.
    if concerns:
        guardian_concern = any(_is_guardian(v.perspective) for v in concerns)
        axiomatic_concern = any(_is_axiomatic(v.perspective) for v in concerns)
        if guardian_concern and axiomatic_concern:
            hints = [c.reasoning for c in concerns]
            return CouncilVerdict(
                verdict=VerdictType.REFINE,
                coherence=coherence,
                votes=votes,
                summary="Guardian and Axiomatic both flagged governance concerns.",
                refinement_hints=hints,
            )

        # Audit follow-up: a soft epistemic prior should not downgrade benign
        # generated text by itself, but it should corroborate a concrete
        # substantive branch (marketing overclaim, logic contradiction,
        # unframed stance). This fixes the previous min_confidence inversion
        # where higher-confidence concerns were less likely to reach REFINE.
        refinement_concerns = [v for v in concerns if _is_refinement_concern(v)]
        actionable_concerns = [
            v for v in refinement_concerns if _is_actionable_substantive_concern(v)
        ]
        if actionable_concerns and len(refinement_concerns) >= 2:
            hints = [c.reasoning for c in refinement_concerns]
            return CouncilVerdict(
                verdict=VerdictType.REFINE,
                coherence=coherence,
                votes=votes,
                summary="Actionable concern corroborated by another perspective.",
                refinement_hints=hints,
            )

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
