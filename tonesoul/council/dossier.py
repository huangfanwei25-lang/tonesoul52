from __future__ import annotations

from typing import Any, Iterable

from .types import CouncilVerdict, PerspectiveType, PerspectiveVote, VoteDecision

DOSSIER_VERSION = "v1"
_DISSENT_DECISIONS = {"concern", "object"}


def _perspective_name(value: PerspectiveType | str) -> str:
    if isinstance(value, PerspectiveType):
        return value.value
    return str(value).strip().lower()


def _decision_name(value: VoteDecision | str) -> str:
    if isinstance(value, VoteDecision):
        return value.value
    return str(value).strip().lower()


def _string_list(values: Iterable[str] | None) -> list[str]:
    if not values:
        return []
    items: list[str] = []
    for value in values:
        text = str(value).strip()
        if text:
            items.append(text)
    return items


def _grounding_name(value: object) -> str:
    grounded_value = getattr(value, "value", value)
    return str(grounded_value).strip().lower()


def _coerce_ratio(value: float | None) -> float | None:
    if value is None:
        return None
    return max(0.0, min(1.0, round(float(value), 3)))


def extract_minority_report(votes: list[PerspectiveVote]) -> list[dict[str, Any]]:
    report: list[dict[str, Any]] = []
    for vote in votes:
        decision = _decision_name(vote.decision)
        if decision not in _DISSENT_DECISIONS:
            continue
        report.append(
            {
                "perspective": _perspective_name(vote.perspective),
                "decision": decision,
                "confidence": round(float(vote.confidence), 3),
                "reasoning": vote.reasoning,
                "evidence": _string_list(vote.evidence),
            }
        )
    return report


def derive_dissent_ratio(
    votes: list[PerspectiveVote],
    provided_dissent_ratio: float | None = None,
) -> float:
    coerced = _coerce_ratio(provided_dissent_ratio)
    if coerced is not None:
        return coerced
    if not votes:
        return 0.0
    dissent_count = sum(1 for vote in votes if _decision_name(vote.decision) in _DISSENT_DECISIONS)
    return round(dissent_count / len(votes), 3)


def derive_confidence_posture(
    verdict: CouncilVerdict,
    dissent_ratio: float,
    minority_report: list[dict[str, Any]] | None = None,
) -> str:
    coherence_score = verdict.coherence.overall
    minority_report = (
        minority_report if minority_report is not None else extract_minority_report(verdict.votes)
    )
    has_high_confidence_dissent = any(
        float(entry.get("confidence", 0.0)) >= 0.7 for entry in minority_report
    )
    has_object_vote = any(entry.get("decision") == "object" for entry in minority_report)

    if coherence_score < 0.5:
        return "low"
    if dissent_ratio >= 0.3 or has_high_confidence_dissent or has_object_vote:
        return "contested"
    if coherence_score >= 0.7 and dissent_ratio < 0.1:
        return "high"
    return "moderate"


def _build_vote_summary(votes: list[PerspectiveVote]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for vote in votes:
        summary.append(
            {
                "perspective": _perspective_name(vote.perspective),
                "decision": _decision_name(vote.decision),
                "confidence": round(float(vote.confidence), 3),
                "reasoning": vote.reasoning,
                "evidence": _string_list(vote.evidence),
            }
        )
    return summary


def _aggregate_evidence(votes: list[PerspectiveVote]) -> list[str]:
    seen: set[str] = set()
    refs: list[str] = []
    for vote in votes:
        for item in _string_list(vote.evidence):
            if item in seen:
                continue
            seen.add(item)
            refs.append(item)
    return refs


def _build_grounding_summary(votes: list[PerspectiveVote]) -> dict[str, Any]:
    return {
        "has_ungrounded_claims": any(
            _grounding_name(vote.grounding_status) == "ungrounded" for vote in votes
        ),
        "total_evidence_sources": sum(len(_string_list(vote.evidence)) for vote in votes),
    }


def _coverage_posture(votes: list[PerspectiveVote]) -> tuple[int, str]:
    distinct_perspectives = len({_perspective_name(vote.perspective) for vote in votes})
    if distinct_perspectives >= 4:
        return distinct_perspectives, "broad"
    if distinct_perspectives >= 2:
        return distinct_perspectives, "partial"
    if distinct_perspectives == 1:
        return distinct_perspectives, "thin"
    return 0, "none"


def _evidence_posture(evidence_density: float) -> str:
    if evidence_density <= 0.0:
        return "none"
    if evidence_density < 0.5:
        return "sparse"
    if evidence_density < 1.0:
        return "moderate"
    return "dense"


def _adversarial_posture(
    verdict: CouncilVerdict,
    minority_report: list[dict[str, Any]],
) -> str:
    if not minority_report:
        return "not_tested"
    if verdict.verdict.value == "block":
        return "triggered_block"
    if verdict.verdict.value == "refine":
        return "triggered_refine"
    if verdict.verdict.value == "declare_stance":
        return "triggered_stance"
    return "survived_dissent"


def _grounding_posture(votes: list[PerspectiveVote]) -> str:
    statuses = {_grounding_name(vote.grounding_status) for vote in votes}
    if "ungrounded" in statuses:
        return "ungrounded"
    if "partial" in statuses:
        return "partial"
    if "grounded" in statuses:
        return "grounded"
    return "not_required"


def _build_confidence_decomposition(
    verdict: CouncilVerdict,
    minority_report: list[dict[str, Any]],
    grounding_summary: dict[str, Any],
) -> dict[str, Any]:
    vote_count = max(1, len(verdict.votes))
    distinct_perspectives, coverage_posture = _coverage_posture(verdict.votes)
    evidence_density = round(
        float(grounding_summary.get("total_evidence_sources", 0) or 0) / vote_count,
        3,
    )
    return {
        "calibration_status": "descriptive_only",
        "agreement_score": round(float(verdict.coherence.approval_rate), 3),
        "coverage_posture": coverage_posture,
        "distinct_perspectives": distinct_perspectives,
        "evidence_density": evidence_density,
        "evidence_posture": _evidence_posture(evidence_density),
        "grounding_posture": _grounding_posture(verdict.votes),
        "adversarial_posture": _adversarial_posture(verdict, minority_report),
    }


def _transcript_string(transcript: dict[str, Any] | None, key: str) -> str:
    if not isinstance(transcript, dict):
        return ""
    value = transcript.get(key)
    if value is None:
        return ""
    return str(value).strip()


def _transcript_list(transcript: dict[str, Any] | None, key: str) -> list[dict[str, Any]]:
    if not isinstance(transcript, dict):
        return []
    value = transcript.get(key)
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def _transcript_evolution_suppression_flag(transcript: dict[str, Any] | None) -> bool | None:
    if not isinstance(transcript, dict):
        return None
    evolution = transcript.get("council_evolution")
    if not isinstance(evolution, dict):
        return None
    suppression = evolution.get("suppression_observability")
    if not isinstance(suppression, dict):
        return None
    if "flag" not in suppression:
        return None
    return bool(suppression.get("flag"))


def build_dossier(
    verdict: CouncilVerdict,
    *,
    dissent_ratio: float | None = None,
    deliberation_mode: str | None = None,
    opacity_declaration: str = "partially_observable",
    change_of_position: list[dict[str, Any]] | None = None,
    evolution_suppression_flag: bool | None = None,
    dossier_version: str = DOSSIER_VERSION,
) -> dict[str, Any]:
    transcript = verdict.transcript if isinstance(verdict.transcript, dict) else {}
    minority_report = extract_minority_report(verdict.votes)
    computed_dissent_ratio = derive_dissent_ratio(verdict.votes, dissent_ratio)
    resolved_deliberation_mode = (
        deliberation_mode or _transcript_string(transcript, "deliberation_mode")
    ).strip()
    resolved_change_of_position = (
        change_of_position
        if change_of_position is not None
        else _transcript_list(transcript, "change_of_position")
    )
    resolved_evolution_suppression_flag = (
        evolution_suppression_flag
        if evolution_suppression_flag is not None
        else _transcript_evolution_suppression_flag(transcript)
    )
    grounding_summary = _build_grounding_summary(verdict.votes)
    payload: dict[str, Any] = {
        "dossier_version": dossier_version,
        "final_verdict": verdict.verdict.value,
        "confidence_posture": derive_confidence_posture(
            verdict=verdict,
            dissent_ratio=computed_dissent_ratio,
            minority_report=minority_report,
        ),
        "coherence_score": round(float(verdict.coherence.overall), 3),
        "dissent_ratio": computed_dissent_ratio,
        "minority_report": minority_report,
        "vote_summary": _build_vote_summary(verdict.votes),
        "deliberation_mode": resolved_deliberation_mode,
        "change_of_position": resolved_change_of_position,
        "evidence_refs": _aggregate_evidence(verdict.votes),
        "grounding_summary": grounding_summary,
        "confidence_decomposition": _build_confidence_decomposition(
            verdict,
            minority_report,
            grounding_summary,
        ),
        "opacity_declaration": opacity_declaration,
    }
    if resolved_evolution_suppression_flag is not None:
        payload["evolution_suppression_flag"] = bool(resolved_evolution_suppression_flag)
    return payload
