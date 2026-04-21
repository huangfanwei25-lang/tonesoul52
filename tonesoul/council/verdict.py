from __future__ import annotations

from typing import List, Union

from .deliberation_trace import AlternativePath, DeliberationTrace
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


def _is_axiomatic(value: Union[PerspectiveType, str]) -> bool:
    if isinstance(value, PerspectiveType):
        return value == PerspectiveType.AXIOMATIC
    return str(value).lower() == PerspectiveType.AXIOMATIC.value


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

    alternatives: List[AlternativePath] = []
    factors: List[str] = []

    guardian_vote = next(
        (v for v in votes if _is_guardian(v.perspective)),
        None,
    )

    # --- Branch 1: Guardian OBJECT with high confidence → BLOCK ---
    if guardian_vote and guardian_vote.decision == VoteDecision.OBJECT:
        if guardian_vote.confidence > 0.7:
            factors.append(f"Guardian objected (confidence={guardian_vote.confidence:.2f})")
            alternatives.append(
                AlternativePath(
                    verdict_candidate="approve",
                    reason_considered="Default path when no safety issues detected.",
                    rejected_because=(
                        f"Guardian raised high-confidence objection: " f"{guardian_vote.reasoning}"
                    ),
                    cost_of_rejection="Output may have been acceptable to user.",
                    revisit_trigger="Guardian confidence drops below 0.7 on re-evaluation.",
                )
            )
            trace = DeliberationTrace(
                chosen_verdict="block",
                chosen_because=(
                    f"Guardian objection with confidence {guardian_vote.confidence:.2f} "
                    f"exceeds 0.7 threshold: {guardian_vote.reasoning}"
                ),
                alternatives=alternatives,
                deciding_factors=factors,
            )
            return CouncilVerdict(
                verdict=VerdictType.BLOCK,
                coherence=coherence,
                votes=votes,
                summary=f"Guardian objection: {guardian_vote.reasoning}",
                deliberation_trace=trace,
            )
        else:
            factors.append(
                f"Guardian objected but confidence {guardian_vote.confidence:.2f} "
                f"below 0.7 — not blocking"
            )

    # --- Branch 2: Coherence too low → BLOCK ---
    overall = coherence.overall
    if overall < block_threshold:
        factors.append(f"Coherence overall={overall:.3f} < block_threshold={block_threshold}")
        alternatives.append(
            AlternativePath(
                verdict_candidate="approve",
                reason_considered="Default approval path.",
                rejected_because=f"Coherence {overall:.3f} is below block threshold {block_threshold}.",
                cost_of_rejection="Output blocked; user gets no response without revision.",
                revisit_trigger="Coherence rises above block threshold after output revision.",
            )
        )
        trace = DeliberationTrace(
            chosen_verdict="block",
            chosen_because=f"Coherence score {overall:.3f} below block threshold {block_threshold}.",
            alternatives=alternatives,
            deciding_factors=factors,
        )
        return CouncilVerdict(
            verdict=VerdictType.BLOCK,
            coherence=coherence,
            votes=votes,
            summary="Coherence too low for safe approval.",
            deliberation_trace=trace,
        )

    # --- Branch 3: Coherence below threshold → DECLARE_STANCE ---
    if overall < coherence_threshold:
        factors.append(
            f"Coherence {overall:.3f} between block ({block_threshold}) "
            f"and approval ({coherence_threshold}) thresholds"
        )
        alternatives.append(
            AlternativePath(
                verdict_candidate="approve",
                reason_considered="Could approve if perspectives were more aligned.",
                rejected_because=(
                    f"Coherence {overall:.3f} below approval threshold "
                    f"{coherence_threshold} — perspectives diverge too much."
                ),
                cost_of_rejection="User does not get clean approval; sees stance declaration.",
                revisit_trigger="Perspectives converge on revised output.",
            )
        )
        alternatives.append(
            AlternativePath(
                verdict_candidate="block",
                reason_considered="Could block if divergence signals danger.",
                rejected_because=(
                    f"Coherence {overall:.3f} above block threshold "
                    f"{block_threshold} — not dangerous, just divergent."
                ),
                cost_of_rejection="Would over-restrict output that has partial agreement.",
            )
        )
        divergence = build_divergence_analysis(votes)
        stance = format_stance_declaration(divergence)
        trace = DeliberationTrace(
            chosen_verdict="declare_stance",
            chosen_because=(
                f"Coherence {overall:.3f} falls between block and approval thresholds. "
                f"Perspectives diverge but output is not dangerous — declaring stance."
            ),
            alternatives=alternatives,
            deciding_factors=factors,
        )
        return CouncilVerdict(
            verdict=VerdictType.DECLARE_STANCE,
            coherence=coherence,
            votes=votes,
            summary="Divergent perspectives detected; declaring stance.",
            stance_declaration=stance,
            deliberation_trace=trace,
        )

    factors.append(f"Coherence {overall:.3f} >= approval threshold {coherence_threshold}")

    concerns = [v for v in votes if v.decision == VoteDecision.CONCERN]

    # --- Branch 4: Guardian + Axiomatic dual concern → REFINE ---
    if concerns:
        guardian_concern = any(_is_guardian(v.perspective) for v in concerns)
        axiomatic_concern = any(_is_axiomatic(v.perspective) for v in concerns)
        if guardian_concern and axiomatic_concern:
            concern_perspectives = [
                (
                    v.perspective.value
                    if isinstance(v.perspective, PerspectiveType)
                    else str(v.perspective)
                )
                for v in concerns
            ]
            factors.append(f"Guardian + Axiomatic dual concern ({', '.join(concern_perspectives)})")
            alternatives.append(
                AlternativePath(
                    verdict_candidate="approve",
                    reason_considered="Coherence is above threshold; could approve.",
                    rejected_because=(
                        "Both Guardian and Axiomatic flagged concerns — "
                        "these are the 'spirit of the law' perspectives. "
                        "Their joint concern overrides the coherence score."
                    ),
                    cost_of_rejection="Output delayed for refinement.",
                    revisit_trigger=(
                        "Output revised to address both Guardian and Axiomatic concerns."
                    ),
                )
            )
            hints = [c.reasoning for c in concerns]
            trace = DeliberationTrace(
                chosen_verdict="refine",
                chosen_because=(
                    "Guardian and Axiomatic both flagged governance concerns. "
                    "Dual-concern from the two 'spirit of the law' perspectives "
                    "is a strong signal regardless of coherence score."
                ),
                alternatives=alternatives,
                deciding_factors=factors,
            )
            return CouncilVerdict(
                verdict=VerdictType.REFINE,
                coherence=coherence,
                votes=votes,
                summary="Guardian and Axiomatic both flagged governance concerns.",
                refinement_hints=hints,
                deliberation_trace=trace,
            )

    # --- Branch 5: Concerns with low min_confidence → REFINE or APPROVE ---
    if concerns and coherence.min_confidence < 0.5:
        factors.append(f"Concerns present with min_confidence={coherence.min_confidence:.2f} < 0.5")
        if not any(_is_refinement_concern(v) for v in concerns):
            factors.append("All concerns are from Advocate only — not blocking refinement")
            alternatives.append(
                AlternativePath(
                    verdict_candidate="refine",
                    reason_considered="Concerns exist with low confidence.",
                    rejected_because=(
                        "Only Advocate raised concerns (tone/intent). "
                        "Advocate concerns alone do not warrant refinement."
                    ),
                    cost_of_rejection="Potential tone/intent issues not addressed.",
                )
            )
            trace = DeliberationTrace(
                chosen_verdict="approve",
                chosen_because=(
                    "Concerns are Advocate-only (tone/intent). These do not warrant "
                    "blocking or refinement — approval granted with noted concerns."
                ),
                alternatives=alternatives,
                deciding_factors=factors,
            )
            return CouncilVerdict(
                verdict=VerdictType.APPROVE,
                coherence=coherence,
                votes=votes,
                summary="Advocate concerns only; approval granted.",
                deliberation_trace=trace,
            )

        concern_sources = [
            (
                v.perspective.value
                if isinstance(v.perspective, PerspectiveType)
                else str(v.perspective)
            )
            for v in concerns
            if _is_refinement_concern(v)
        ]
        factors.append(f"Refinement-worthy concerns from: {', '.join(concern_sources)}")
        alternatives.append(
            AlternativePath(
                verdict_candidate="approve",
                reason_considered="Coherence is above threshold.",
                rejected_because=(
                    f"Non-advocate concerns present and min_confidence "
                    f"{coherence.min_confidence:.2f} < 0.5 — "
                    f"not confident enough to approve past concerns."
                ),
                cost_of_rejection="Output delayed for refinement.",
                revisit_trigger="Concerns addressed in revised output.",
            )
        )
        hints = [c.reasoning for c in concerns]
        trace = DeliberationTrace(
            chosen_verdict="refine",
            chosen_because=(
                f"Substantive concerns from {', '.join(concern_sources)} with "
                f"min_confidence {coherence.min_confidence:.2f} below 0.5."
            ),
            alternatives=alternatives,
            deciding_factors=factors,
        )
        return CouncilVerdict(
            verdict=VerdictType.REFINE,
            coherence=coherence,
            votes=votes,
            summary="Requests for refinement detected.",
            refinement_hints=hints,
            deliberation_trace=trace,
        )

    # --- Branch 6: Default → APPROVE ---
    if concerns:
        factors.append(
            f"Concerns present but min_confidence={coherence.min_confidence:.2f} >= 0.5 "
            f"— confident enough to approve"
        )
    else:
        factors.append("No concerns raised by any perspective")

    # Record what could have gone differently
    if guardian_vote and guardian_vote.decision != VoteDecision.APPROVE:
        alternatives.append(
            AlternativePath(
                verdict_candidate="block",
                reason_considered=(
                    f"Guardian voted {guardian_vote.decision.value} "
                    f"(confidence={guardian_vote.confidence:.2f})."
                ),
                rejected_because="Did not meet block criteria (OBJECT + confidence > 0.7).",
                cost_of_rejection="Potential safety signal not escalated.",
            )
        )

    trace = DeliberationTrace(
        chosen_verdict="approve",
        chosen_because="Consensus achieved: coherence above threshold, no blocking concerns.",
        alternatives=alternatives,
        deciding_factors=factors,
    )
    return CouncilVerdict(
        verdict=VerdictType.APPROVE,
        coherence=coherence,
        votes=votes,
        summary="Consensus achieved across perspectives.",
        deliberation_trace=trace,
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
