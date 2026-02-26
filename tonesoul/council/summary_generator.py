from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

from .types import CouncilVerdict, PerspectiveType, PerspectiveVote, VerdictType, VoteDecision

PERSPECTIVE_LABELS = {
    "guardian": "Safety Council",
    "analyst": "Analyst Review",
    "critic": "Critic Lens",
    "advocate": "Advocate Voice",
}

ASPECT_LABELS = {
    "guardian": ("safety", "\u5b89\u5168"),
    "analyst": ("factual accuracy", "\u4e8b\u5be6\u6b63\u78ba\u6027"),
    "critic": ("quality and subjectivity", "\u8868\u9054\u4e0e\u4e3b\u89c0\u6027"),
    "advocate": ("user intent and usefulness", "\u7528\u6236\u610f\u5716\u8207\u5be6\u7528\u6027"),
}

ACTION_RECOMMENDATIONS = {
    "guardian": (
        "Remove unsafe or harmful instructions.",
        "\u907f\u514d\u5371\u96aa\u6216\u4f24\u5bb3\u5167\u5bb9\u3002",
    ),
    "analyst": (
        "Add evidence or clarify factual claims.",
        "\u63d0\u4f9b\u8b49\u64da\u6216\u6e05\u695a\u4e8b\u5be6\u8868\u8ff0\u3002",
    ),
    "critic": (
        "Clarify subjective points or provide balanced framing.",
        "\u6e05\u695a\u6a19\u793a\u4e3b\u89c0\u89c0\u9ede\u4e26\u589e\u52a0\u5e73\u8861\u89c0\u9ede\u3002",
    ),
    "advocate": (
        "Align the response with user intent and add practical guidance.",
        "\u5c0d\u9f4a\u7528\u6236\u610f\u5716\u4e26\u63d0\u4f9b\u5be6\u7528\u8aaa\u660e\u3002",
    ),
}

COLLABORATION_SCHEMA_VERSION = "1.0.0"

ROLE_LABELS = {
    "guardian": "Guardian",
    "analyst": "Analyst",
    "critic": "Critic",
    "advocate": "Advocate",
    "axiomatic_inference": "Auditor",
}

HANDOFF_RULES = {
    "object": {
        "next_role": "Guardian",
        "action": "Block output and escalate to human review.",
    },
    "concern": {
        "next_role": "Builder",
        "action": "Refine the draft and rerun council validation.",
    },
    "approve": {
        "next_role": "OutputContract",
        "action": "Proceed to output contract verification.",
    },
    "abstain": {
        "next_role": "Analyst",
        "action": "Collect missing context and rerun council validation.",
    },
}

RISK_LEVEL_MAP = {
    "object": "high",
    "concern": "medium",
    "approve": "low",
    "abstain": "unknown",
}


def resolve_language(context: Optional[dict]) -> str:
    if not context:
        return "en"
    for key in ("language", "lang", "locale"):
        value = context.get(key)
        if value:
            normalized = str(value).lower()
            if normalized.startswith("zh"):
                return "zh"
            if normalized.startswith("en"):
                return "en"
    return "en"


def _normalize_perspective(value: object) -> str:
    if isinstance(value, PerspectiveType):
        return value.value
    return str(value).strip().lower()


def _perspective_label(value: object) -> str:
    key = _normalize_perspective(value)
    return PERSPECTIVE_LABELS.get(key, str(value))


def _decision_bucket(value: object) -> str:
    if isinstance(value, VoteDecision):
        return value.value
    return str(value).strip().lower()


def _role_label(value: object) -> str:
    key = _normalize_perspective(value)
    return ROLE_LABELS.get(key, "Analyst")


def _risk_payload(vote: PerspectiveVote) -> Dict[str, str]:
    decision = _decision_bucket(vote.decision)
    level = RISK_LEVEL_MAP.get(decision, "unknown")
    try:
        confidence = float(vote.confidence)
    except (TypeError, ValueError):
        confidence = 0.0
    return {
        "level": level,
        "basis": f"decision={decision}; confidence={confidence:.2f}",
    }


def _handoff_payload(vote: PerspectiveVote) -> Dict[str, str]:
    decision = _decision_bucket(vote.decision)
    payload = HANDOFF_RULES.get(decision)
    if isinstance(payload, dict):
        return {
            "next_role": str(payload.get("next_role", "Analyst")),
            "action": str(payload.get("action", "Collect context and rerun validation.")),
        }
    return {
        "next_role": "Analyst",
        "action": "Collect context and rerun validation.",
    }


def build_collaboration_records(votes: List[PerspectiveVote]) -> List[Dict[str, object]]:
    records: List[Dict[str, object]] = []
    for vote in votes:
        claim = (vote.reasoning or "").strip() or "No explicit claim provided."
        evidence = list(vote.evidence or [])
        records.append(
            {
                "role": _role_label(vote.perspective),
                "claim": claim,
                "evidence": evidence,
                "risk": _risk_payload(vote),
                "handoff": _handoff_payload(vote),
            }
        )
    return records


def validate_collaboration_records(records: List[Dict[str, object]]) -> Dict[str, object]:
    errors: List[str] = []
    for index, record in enumerate(records):
        prefix = f"record[{index}]"
        role = record.get("role")
        claim = record.get("claim")
        evidence = record.get("evidence")
        risk = record.get("risk")
        handoff = record.get("handoff")

        if not isinstance(role, str) or not role.strip():
            errors.append(f"{prefix}.role must be non-empty string")
        if not isinstance(claim, str) or not claim.strip():
            errors.append(f"{prefix}.claim must be non-empty string")
        if not isinstance(evidence, list):
            errors.append(f"{prefix}.evidence must be list")
        if not isinstance(risk, dict):
            errors.append(f"{prefix}.risk must be object")
        else:
            level = risk.get("level")
            basis = risk.get("basis")
            if not isinstance(level, str) or not level.strip():
                errors.append(f"{prefix}.risk.level must be non-empty string")
            if not isinstance(basis, str) or not basis.strip():
                errors.append(f"{prefix}.risk.basis must be non-empty string")
        if not isinstance(handoff, dict):
            errors.append(f"{prefix}.handoff must be object")
        else:
            next_role = handoff.get("next_role")
            action = handoff.get("action")
            if not isinstance(next_role, str) or not next_role.strip():
                errors.append(f"{prefix}.handoff.next_role must be non-empty string")
            if not isinstance(action, str) or not action.strip():
                errors.append(f"{prefix}.handoff.action must be non-empty string")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "record_count": len(records),
    }


def _collect_aspects(votes: List[PerspectiveVote], bucket: str, language: str) -> List[str]:
    aspects: List[str] = []
    for vote in votes:
        if _decision_bucket(vote.decision) != bucket:
            continue
        key = _normalize_perspective(vote.perspective)
        label_pair = ASPECT_LABELS.get(key)
        if not label_pair:
            continue
        aspect = label_pair[0] if language == "en" else label_pair[1]
        if aspect not in aspects:
            aspects.append(aspect)
    return aspects


def _recommended_actions(votes: List[PerspectiveVote], language: str) -> List[str]:
    actions: List[str] = []
    for vote in votes:
        bucket = _decision_bucket(vote.decision)
        if bucket not in ("concern", "object"):
            continue
        key = _normalize_perspective(vote.perspective)
        action_pair = ACTION_RECOMMENDATIONS.get(key)
        if not action_pair:
            continue
        action = action_pair[0] if language == "en" else action_pair[1]
        if action not in actions:
            actions.append(action)
    if not actions:
        actions.append(
            "Proceed with the response."
            if language == "en"
            else "\u53ef\u4ee5\u7e7c\u7e8c\u9032\u884c\u3002"
        )
    return actions


def _decision_distribution(votes: List[PerspectiveVote]) -> Dict[str, int]:
    distribution = {
        "approve": 0,
        "concern": 0,
        "object": 0,
        "abstain": 0,
    }
    for vote in votes:
        bucket = _decision_bucket(vote.decision)
        if bucket in distribution:
            distribution[bucket] += 1
    return distribution


def _reasoning_specificity_score(text: str) -> float:
    cleaned = text.strip()
    if not cleaned:
        return 0.0
    if " " in cleaned:
        tokens = [token for token in cleaned.split() if token]
        return min(1.0, len(tokens) / 16.0)
    return min(1.0, len(cleaned) / 48.0)


def _reasoning_specificity(votes: List[PerspectiveVote]) -> float:
    target_votes = [
        vote for vote in votes if _decision_bucket(vote.decision) in {"concern", "object"}
    ]
    if not target_votes:
        target_votes = votes
    if not target_votes:
        return 0.0

    scores = [_reasoning_specificity_score(vote.reasoning or "") for vote in target_votes]
    return sum(scores) / float(len(scores))


def _evidence_coverage(votes: List[PerspectiveVote]) -> float:
    if not votes:
        return 0.0
    covered = 0
    for vote in votes:
        if isinstance(vote.evidence, list) and any(str(item).strip() for item in vote.evidence):
            covered += 1
    return covered / float(len(votes))


def _confidence_balance(votes: List[PerspectiveVote]) -> float:
    confidences: List[float] = []
    for vote in votes:
        try:
            confidences.append(float(vote.confidence))
        except (TypeError, ValueError):
            continue
    if not confidences:
        return 0.0
    spread = max(confidences) - min(confidences)
    ideal_spread = 0.35
    return max(0.0, min(1.0, 1.0 - abs(spread - ideal_spread) / ideal_spread))


def _build_role_tensions(votes: List[PerspectiveVote]) -> List[Dict[str, object]]:
    records: List[Dict[str, object]] = []
    for vote in votes:
        key = _normalize_perspective(vote.perspective)
        bucket = _decision_bucket(vote.decision)
        if bucket not in {"approve", "concern", "object", "abstain"}:
            continue
        try:
            confidence = float(vote.confidence)
        except (TypeError, ValueError):
            confidence = 0.0
        records.append(
            {
                "key": key,
                "label": _perspective_label(vote.perspective),
                "bucket": bucket,
                "reasoning": (vote.reasoning or "").strip(),
                "confidence": confidence,
                "evidence": list(vote.evidence or []),
            }
        )

    if len(records) < 2:
        return []

    tensions: List[Dict[str, object]] = []
    seen_pairs: set[tuple[str, str, str, str]] = set()

    for source in records:
        source_bucket = str(source["bucket"])
        if source_bucket not in {"concern", "object"}:
            continue

        candidates = [
            candidate
            for candidate in records
            if candidate["key"] != source["key"] and candidate["bucket"] != source_bucket
        ]
        if not candidates:
            continue

        def _target_priority(candidate: Dict[str, object]) -> tuple[int, float]:
            bucket = str(candidate.get("bucket") or "")
            if bucket == "approve":
                rank = 3
            elif bucket == "concern":
                rank = 2
            elif bucket == "object":
                rank = 1
            else:
                rank = 0
            confidence = float(candidate.get("confidence") or 0.0)
            return rank, confidence

        target = max(candidates, key=_target_priority)
        pair_key = (
            str(source["key"]),
            str(target["key"]),
            source_bucket,
            str(target["bucket"]),
        )
        if pair_key in seen_pairs:
            continue
        seen_pairs.add(pair_key)

        source_reason = str(source.get("reasoning") or "").strip() or "No explicit rationale."
        target_reason = str(target.get("reasoning") or "").strip() or "No explicit rationale."
        tensions.append(
            {
                "from": source["label"],
                "from_role": source["key"],
                "from_decision": source_bucket,
                "to": target["label"],
                "to_role": target["key"],
                "to_decision": target["bucket"],
                "reason": source_reason,
                "counter_reason": target_reason,
                "evidence": source.get("evidence", []),
            }
        )

    return tensions[:4]


def _build_divergence_quality(
    votes: List[PerspectiveVote],
    decision_distribution: Dict[str, int],
    role_tensions: List[Dict[str, object]],
) -> Dict[str, object]:
    total_votes = max(1, len(votes))
    conflict_coverage = (
        decision_distribution.get("concern", 0) + decision_distribution.get("object", 0)
    ) / float(total_votes)
    reasoning_specificity = _reasoning_specificity(votes)
    evidence_coverage = _evidence_coverage(votes)
    confidence_balance = _confidence_balance(votes)
    tension_coverage = min(1.0, len(role_tensions) / 3.0)

    score = (
        conflict_coverage * 0.32
        + reasoning_specificity * 0.28
        + evidence_coverage * 0.15
        + confidence_balance * 0.10
        + tension_coverage * 0.15
    )

    if score >= 0.7:
        band = "high"
    elif score >= 0.45:
        band = "medium"
    else:
        band = "low"

    return {
        "score": round(score, 3),
        "band": band,
        "conflict_coverage": round(conflict_coverage, 3),
        "reasoning_specificity": round(reasoning_specificity, 3),
        "evidence_coverage": round(evidence_coverage, 3),
        "confidence_balance": round(confidence_balance, 3),
        "role_tension_coverage": round(tension_coverage, 3),
    }


def build_divergence_analysis(
    votes: List[PerspectiveVote], context: Optional[Dict[str, object]] = None
) -> Dict[str, object]:
    agree: List[str] = []
    concerns: List[str] = []
    objections: List[str] = []
    abstain: List[str] = []
    reason_notes: List[str] = []

    for vote in votes:
        label = _perspective_label(vote.perspective)
        bucket = _decision_bucket(vote.decision)
        if bucket == "approve":
            agree.append(label)
        elif bucket == "concern":
            concerns.append(label)
            reason_notes.append(f"{label}: {vote.reasoning}")
        elif bucket == "object":
            objections.append(label)
            reason_notes.append(f"{label}: {vote.reasoning}")
        else:
            abstain.append(label)

    if reason_notes:
        core_divergence = "; ".join(reason_notes[:2])
    else:
        core_divergence = "No specific conflict identified."

    recommended_action = " ".join(_recommended_actions(votes, "en"))
    decision_distribution = _decision_distribution(votes)
    role_tensions = _build_role_tensions(votes)
    quality = _build_divergence_quality(votes, decision_distribution, role_tensions)

    visual_context = context.get("visual_context") if context else None

    return {
        "agree": agree,
        "concern": concerns,
        "object": objections,
        "abstain": abstain,
        "core_divergence": core_divergence,
        "recommended_action": recommended_action,
        "decision_distribution": decision_distribution,
        "role_tensions": role_tensions,
        "quality": quality,
        "visual_context": visual_context,
    }


def format_stance_declaration(divergence: Dict[str, object]) -> str:
    lines = ["Multiple perspectives are not fully aligned."]
    agree = divergence.get("agree") or []
    concerns = divergence.get("concern") or []
    objections = divergence.get("object") or []
    core_divergence = divergence.get("core_divergence") or "No specific conflict identified."
    recommended_action = divergence.get("recommended_action") or "Proceed with caution."

    if agree:
        lines.append(f"Agreement: {', '.join(agree)}.")
    if objections:
        lines.append(f"Objections: {', '.join(objections)}.")
    if concerns:
        lines.append(f"Concerns: {', '.join(concerns)}.")

    lines.append(f"Core divergence: {core_divergence}")
    lines.append(f"Recommended action: {recommended_action}")
    return "\n".join(lines)


def generate_human_summary(verdict: CouncilVerdict, language: str = "en") -> str:
    votes = verdict.votes
    verdict_type = verdict.verdict
    concerns = _collect_aspects(votes, "concern", language) + _collect_aspects(
        votes, "object", language
    )
    approvals = _collect_aspects(votes, "approve", language)
    actions = _recommended_actions(votes, language)

    if verdict_type == VerdictType.BLOCK:
        if language == "zh":
            return "\u5b89\u5168\u98a8\u96aa\u904e\u9ad8\uff0c\u9019\u500b\u5167\u5bb9\u4e0d\u5efa\u8b70\u4f7f\u7528\u3002"
        return "Safety risks were raised, so this content should not be used."

    if verdict_type == VerdictType.REFINE:
        if language == "zh":
            summary = "\u6709\u4e00\u4e9b\u5730\u65b9\u9700\u8981\u6539\u9032\u3002"
            if concerns:
                summary += (
                    "\u76ee\u524d\u6709\u95dc\u65bc"
                    + "\u3001".join(concerns)
                    + "\u7684\u7591\u616e\u3002"
                )
            summary += "\u5efa\u8b70\u7684\u4f5c\u6cd5\uff1a" + " ".join(actions)
            return summary
        summary = "Some parts need improvement."
        if concerns:
            summary += " Concerns were raised about " + ", ".join(concerns) + "."
        summary += " Suggested action: " + " ".join(actions)
        return summary

    if verdict_type == VerdictType.DECLARE_STANCE:
        if language == "zh":
            summary = "\u9019\u500b\u5167\u5bb9\u6709\u4e0d\u540c\u770b\u6cd5\u3002"
            if approvals:
                summary += (
                    "\u95dc\u65bc"
                    + "\u3001".join(approvals)
                    + "\u6c92\u6709\u660e\u986f\u554f\u984c\u3002"
                )
            if concerns:
                summary += (
                    "\u4f46" + "\u3001".join(concerns) + "\u9084\u9700\u8981\u6ce8\u610f\u3002"
                )
            summary += "\u5efa\u8b70\u7684\u4f5c\u6cd5\uff1a" + " ".join(actions)
            return summary
        summary = "There are different viewpoints on this content."
        if approvals:
            summary += " No major issues were raised about " + ", ".join(approvals) + "."
        if concerns:
            summary += " But concerns remain about " + ", ".join(concerns) + "."
        summary += " Suggested action: " + " ".join(actions)
        return summary

    if language == "zh":
        summary = "\u6574\u9ad4\u4f86\u8aaa\u9019\u500b\u5167\u5bb9\u6c92\u6709\u660e\u986f\u554f\u984c\u3002"
        if concerns:
            summary += (
                "\u4f46\u4ecd\u6709\u5c0f\u90e8\u5206\u95dc\u6ce8\u5728"
                + "\u3001".join(concerns)
                + "\u3002"
            )
        return summary

    summary = "Overall, this content looks safe and helpful."
    if concerns:
        summary += " Minor notes were raised about " + ", ".join(concerns) + "."
    return summary


def build_transcript(
    draft_output: str,
    context: dict,
    user_intent: Optional[str],
    votes: List[PerspectiveVote],
    coherence: object,
    verdict: CouncilVerdict,
    divergence: Optional[Dict[str, object]] = None,
) -> Dict[str, object]:
    vote_records = []
    for vote in votes:
        vote_records.append(
            {
                "perspective": _perspective_label(vote.perspective),
                "decision": _decision_bucket(vote.decision),
                "confidence": vote.confidence,
                "reasoning": vote.reasoning,
            }
        )

    coherence_record = {
        "c_inter": getattr(coherence, "c_inter", None),
        "approval_rate": getattr(coherence, "approval_rate", None),
        "min_confidence": getattr(coherence, "min_confidence", None),
        "has_strong_objection": getattr(coherence, "has_strong_objection", None),
    }

    verdict_record = {
        "verdict": verdict.verdict.value,
        "summary": verdict.summary,
        "stance_declaration": verdict.stance_declaration,
        "refinement_hints": verdict.refinement_hints,
    }
    collaboration_records = build_collaboration_records(votes)
    collaboration_validation = validate_collaboration_records(collaboration_records)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input_preview": draft_output[:120],
        "input_length": len(draft_output),
        "context_keys": list(context.keys()) if context else [],
        "user_intent": user_intent,
        "votes": vote_records,
        "coherence": coherence_record,
        "verdict": verdict_record,
        "divergence_analysis": divergence,
        "multi_agent_contract": {
            "schema_version": COLLABORATION_SCHEMA_VERSION,
            "records": collaboration_records,
            "validation": collaboration_validation,
        },
    }
