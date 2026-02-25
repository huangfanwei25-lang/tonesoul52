from __future__ import annotations

from typing import List, Optional, Tuple, Union

from .summary_generator import build_divergence_analysis, format_stance_declaration
from .types import (
    CoherenceScore,
    CouncilVerdict,
    GroundingStatus,
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


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _uncertainty_band(level: float) -> str:
    if level < 0.33:
        return "low"
    if level < 0.66:
        return "medium"
    return "high"


def _responsibility_adjustment(responsibility_tier: Optional[str]) -> float:
    if not responsibility_tier:
        return 0.0
    normalized = str(responsibility_tier).strip().upper()
    if normalized == "TIER_2":
        return 0.1
    if normalized == "TIER_3":
        return 0.2
    return 0.0


def _uncertainty_disclosure(band: Optional[str]) -> Optional[dict]:
    if band == "high":
        return {
            "format": "i_dont_know_v1",
            "sections": [
                "conclusion",
                "reason",
                "needed",
                "next_steps",
                "trace",
            ],
            "template": [
                "Conclusion: I cannot be confident about this answer with current information.",
                "Reason: Insufficient evidence or verification signals.",
                "Needed: Provide sources or clarify constraints.",
                "Next steps: Ask for more context or defer to verified sources.",
                "Trace (optional): coherence / grounding signals.",
            ],
        }
    if band == "medium":
        return {
            "format": "uncertainty_notice_v1",
            "template": [
                "Uncertainty notice: confidence is limited; verify key facts.",
                "Needed: Provide supporting evidence or context.",
            ],
        }
    return None


def compute_uncertainty(
    votes: List[PerspectiveVote],
    coherence: CoherenceScore,
    responsibility_tier: Optional[str] = None,
) -> Tuple[float, str, List[str]]:
    base = 1 - coherence.overall
    min_guard = 1 - coherence.min_confidence
    level = max(base, min_guard)

    reasons = [
        f"coherence_overall={coherence.overall:.3f}",
        f"min_confidence={coherence.min_confidence:.3f}",
    ]

    grounding_penalty = 0.0
    if any(
        vote.requires_grounding and vote.grounding_status == GroundingStatus.UNGROUNDED
        for vote in votes
    ):
        grounding_penalty = 0.2
        reasons.append("grounding_penalty=0.2 (ungrounded claims)")

    level += grounding_penalty
    tier_adjust = _responsibility_adjustment(responsibility_tier)
    if tier_adjust:
        reasons.append(f"responsibility_tier_adjustment={tier_adjust:.1f} ({responsibility_tier})")

    level = _clamp(level + tier_adjust)
    band = _uncertainty_band(level)
    return level, band, reasons


def apply_uncertainty(
    verdict: CouncilVerdict,
    responsibility_tier: Optional[str] = None,
) -> CouncilVerdict:
    level, band, reasons = compute_uncertainty(
        verdict.votes or [],
        verdict.coherence,
        responsibility_tier,
    )
    verdict.uncertainty_level = level
    verdict.uncertainty_band = band
    verdict.uncertainty_reasons = reasons
    return verdict


def build_structured_output(verdict: CouncilVerdict) -> dict:
    votes = verdict.votes or []
    coherence = verdict.coherence

    core_reasons = [
        v.reasoning
        for v in votes
        if str(getattr(v, "decision", "")).lower() in ("concern", "object") and v.reasoning
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
        "uncertainty": {
            "level": verdict.uncertainty_level,
            "band": verdict.uncertainty_band,
            "reasons": verdict.uncertainty_reasons or [],
            "disclosure": _uncertainty_disclosure(verdict.uncertainty_band),
        },
        "signals": {
            "approval_rate": coherence.approval_rate,
            "min_confidence": coherence.min_confidence,
            "has_strong_objection": coherence.has_strong_objection,
        },
        "core_divergence": divergence.get("core_divergence"),
        "role_tensions": divergence.get("role_tensions", []),
        "recommended_action": divergence.get("recommended_action"),
        "visual_context": divergence.get("visual_context"),
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
    def _finalize(verdict: CouncilVerdict) -> CouncilVerdict:
        return apply_uncertainty(verdict)

    guardian_vote = next(
        (v for v in votes if _is_guardian(v.perspective)),
        None,
    )

    if guardian_vote and guardian_vote.decision == VoteDecision.OBJECT:
        if guardian_vote.confidence > 0.7:
            return _finalize(
                CouncilVerdict(
                    verdict=VerdictType.BLOCK,
                    coherence=coherence,
                    votes=votes,
                    summary=f"Guardian objection: {guardian_vote.reasoning}",
                )
            )

    overall = coherence.overall
    if overall < block_threshold:
        return _finalize(
            CouncilVerdict(
                verdict=VerdictType.BLOCK,
                coherence=coherence,
                votes=votes,
                summary="Coherence too low for safe approval.",
            )
        )

    if overall < coherence_threshold:
        divergence = build_divergence_analysis(votes)
        stance = format_stance_declaration(divergence)
        return _finalize(
            CouncilVerdict(
                verdict=VerdictType.DECLARE_STANCE,
                coherence=coherence,
                votes=votes,
                summary="Divergent perspectives detected; declaring stance.",
                stance_declaration=stance,
            )
        )

    concerns = [v for v in votes if v.decision == VoteDecision.CONCERN]
    if concerns and coherence.min_confidence < 0.5:
        if not any(_is_refinement_concern(v) for v in concerns):
            return _finalize(
                CouncilVerdict(
                    verdict=VerdictType.APPROVE,
                    coherence=coherence,
                    votes=votes,
                    summary="Advocate concerns only; approval granted.",
                )
            )
        hints = [c.reasoning for c in concerns]
        return _finalize(
            CouncilVerdict(
                verdict=VerdictType.REFINE,
                coherence=coherence,
                votes=votes,
                summary="Requests for refinement detected.",
                refinement_hints=hints,
            )
        )

    return _finalize(
        CouncilVerdict(
            verdict=VerdictType.APPROVE,
            coherence=coherence,
            votes=votes,
            summary="Consensus achieved across perspectives.",
        )
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
