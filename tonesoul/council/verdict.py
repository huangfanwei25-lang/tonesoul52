from __future__ import annotations

from typing import List, Optional, Union

from .types import (
    CoherenceScore,
    CouncilVerdict,
    PerspectiveType,
    PerspectiveVote,
    VerdictType,
    VoteDecision,
)
from .summary_generator import build_divergence_analysis, format_stance_declaration


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


def build_structured_output(verdict: CouncilVerdict) -> dict:
    votes = verdict.votes or []
    coherence = verdict.coherence

    core_reasons = [
        v.reasoning
        for v in votes
        if str(getattr(v, "decision", "")).lower() in ("concern", "object")
        and v.reasoning
    ]
    if not core_reasons:
        core_reasons = [v.reasoning for v in votes if v.reasoning]
    core_reasons = core_reasons[:3]

    decision_core = {
        "title": "Decision Core",
        "decision": verdict.verdict.value,
        "summary": verdict.summary,
        "human_summary": verdict.human_summary,
        "stance_declaration": verdict.stance_declaration,
        "refinement_hints": verdict.refinement_hints or [],
        "core_reasons": core_reasons,
    }

    tension_votes = []
    for v in votes:
        decision_value = getattr(v.decision, "value", str(v.decision))
        tension_votes.append(
            {
                "perspective": _perspective_label(v.perspective),
                "decision": decision_value,
                "confidence": v.confidence,
                "reasoning": v.reasoning,
            }
        )

    tension_scan = {
        "title": "Tension Scan",
        "coherence": {
            "overall": coherence.overall,
            "c_inter": coherence.c_inter,
            "approval_rate": coherence.approval_rate,
            "min_confidence": coherence.min_confidence,
            "has_strong_objection": coherence.has_strong_objection,
        },
        "votes": tension_votes,
    }

    memory_refs = []
    transcript = verdict.transcript if isinstance(verdict.transcript, dict) else {}
    for key in (
        "memory_context",
        "commitments",
        "past_commitments",
        "isnad",
        "provenance",
    ):
        value = transcript.get(key)
        if not value:
            continue
        if isinstance(value, list):
            memory_refs.extend(value)
        else:
            memory_refs.append(value)

    memory_context = {
        "title": "Memory Context",
        "commitments": memory_refs,
        "note": None if memory_refs else "No referenced commitments captured.",
    }

    confidence_score = coherence.overall
    if confidence_score >= 0.75:
        confidence_level = "high"
    elif confidence_score >= 0.5:
        confidence_level = "medium"
    else:
        confidence_level = "low"

    divergence = verdict.divergence_analysis or {}
    reflection = {
        "title": "Reflection",
        "confidence_score": round(confidence_score, 3),
        "confidence_level": confidence_level,
        "signals": {
            "approval_rate": coherence.approval_rate,
            "min_confidence": coherence.min_confidence,
            "has_strong_objection": coherence.has_strong_objection,
        },
        "core_divergence": divergence.get("core_divergence"),
    }

    follow_up_actions = []
    if verdict.verdict == VerdictType.BLOCK:
        follow_up_actions.append("Decline the request and provide safe alternatives.")
    elif verdict.verdict == VerdictType.REFINE:
        follow_up_actions.extend(verdict.refinement_hints or [])
        if not follow_up_actions:
            follow_up_actions.append("Refine the response based on council feedback.")
    elif verdict.verdict == VerdictType.DECLARE_STANCE:
        follow_up_actions.append("State the stance and document key disagreements.")
    else:
        follow_up_actions.append("Proceed with the response.")

    recommended = divergence.get("recommended_action")
    if recommended and recommended not in follow_up_actions:
        follow_up_actions.append(recommended)

    follow_up = {
        "title": "Follow-up",
        "actions": follow_up_actions,
    }

    return {
        "A": decision_core,
        "B": tension_scan,
        "C": memory_context,
        "D": reflection,
        "E": follow_up,
    }


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

    concerns = [
        v for v in votes if v.decision == VoteDecision.CONCERN
    ]
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
    return (
        "Multiple perspectives disagree; stance summary:\n"
        + "\n".join(parts)
    )
