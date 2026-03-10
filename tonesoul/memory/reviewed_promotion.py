from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence

from tonesoul.schemas import (
    ReviewedPromotionDecision,
    SubjectivityLayer,
    SubjectivityPromotionGate,
    SubjectivityPromotionStatus,
    SubjectivityReviewActor,
)

from .soul_db import MemorySource, SoulDB
from .write_gateway import MemoryWriteGateway


def infer_subjectivity_layer(payload: Dict[str, object], *, target_layer: str) -> str:
    """Infer a semantic subjectivity layer when the payload is still unlabeled."""
    existing = str(payload.get("subjectivity_layer") or "").strip().lower()
    if existing:
        return existing

    tension_markers = (
        payload.get("friction_score"),
        payload.get("tension"),
        payload.get("tension_score"),
        payload.get("dream_cycle_id"),
        payload.get("council_reason"),
    )
    if any(marker not in (None, "", [], {}) for marker in tension_markers):
        return SubjectivityLayer.TENSION.value

    text = " ".join(
        str(payload.get(key) or "")
        for key in ("text", "content", "summary", "reflection", "topic")
    ).lower()
    if any(keyword in text for keyword in ("conflict", "tension", "friction", "diverge", "rupture")):
        return SubjectivityLayer.TENSION.value

    if target_layer == "experiential":
        return SubjectivityLayer.MEANING.value
    return SubjectivityLayer.EVENT.value


def build_reviewed_promotion_decision(
    payload: Dict[str, object],
    *,
    review_actor: object,
    review_basis: str,
    reviewed_at: Optional[str] = None,
    source_record_ids: Optional[Sequence[str]] = None,
    promotion_source: str = "manual_review",
    status: str = SubjectivityPromotionStatus.REVIEWED.value,
    target_subjectivity_layer: str = SubjectivityLayer.VOW.value,
    notes: Optional[str] = None,
) -> ReviewedPromotionDecision:
    """Create the canonical audited artifact for an explicit promotion review."""
    if not isinstance(payload, dict):
        raise TypeError("build_reviewed_promotion_decision expects a dict payload")

    actor_input = {"actor_id": review_actor} if isinstance(review_actor, str) else review_actor
    actor = SubjectivityReviewActor.model_validate(actor_input)

    basis = str(review_basis or "").strip()
    if not basis:
        raise ValueError("review_basis is required")

    current_layer = str(payload.get("layer") or "working").strip().lower() or "working"
    source_subjectivity = infer_subjectivity_layer(payload, target_layer=current_layer)
    if source_subjectivity != SubjectivityLayer.TENSION.value:
        raise ValueError("reviewed promotion expects a tension candidate")

    target_subjectivity = str(target_subjectivity_layer or "").strip().lower()
    if target_subjectivity != SubjectivityLayer.VOW.value:
        raise ValueError("current reviewed promotion workflow only supports tension -> vow")

    merged_source_ids = _merge_source_record_ids(
        source_record_ids=source_record_ids,
        payload_source_ids=payload.get("source_record_ids"),
    )

    return ReviewedPromotionDecision.model_validate(
        {
            "status": status,
            "promotion_source": promotion_source,
            "review_actor": actor.model_dump(mode="json"),
            "source_subjectivity_layer": source_subjectivity,
            "target_subjectivity_layer": target_subjectivity,
            "source_record_ids": merged_source_ids,
            "reviewed_at": reviewed_at or _utcnow_iso(),
            "review_basis": basis,
            "notes": notes,
        }
    )


def build_reviewed_promotion_payload(
    payload: Dict[str, object],
    *,
    decision: ReviewedPromotionDecision | Dict[str, object],
) -> Dict[str, object]:
    """Convert an approved reviewed-promotion decision into a gateway-valid payload."""
    if not isinstance(payload, dict):
        raise TypeError("build_reviewed_promotion_payload expects a dict payload")

    reviewed_decision = _normalize_decision(decision)
    if reviewed_decision.status == SubjectivityPromotionStatus.REJECTED:
        raise ValueError("rejected promotion decisions cannot be replayed")
    if reviewed_decision.source_subjectivity_layer != SubjectivityLayer.TENSION:
        raise ValueError("reviewed promotion replay expects a tension source decision")
    if reviewed_decision.target_subjectivity_layer != SubjectivityLayer.VOW:
        raise ValueError("reviewed promotion replay currently only supports vow targets")

    normalized_payload = dict(payload)
    normalized_payload["layer"] = "factual"
    normalized_payload["subjectivity_layer"] = reviewed_decision.target_subjectivity_layer.value
    normalized_payload["promotion_gate"] = SubjectivityPromotionGate.build_payload(
        status=reviewed_decision.status.value,
        source=reviewed_decision.promotion_source,
        reviewed_by=reviewed_decision.review_actor.actor_id,
        reviewed_at=reviewed_decision.reviewed_at,
        review_basis=reviewed_decision.review_basis,
        human_review=reviewed_decision.review_actor.actor_type in {"human", "operator"},
        governance_review=reviewed_decision.review_actor.actor_type == "governance",
    )
    normalized_payload["review_basis"] = reviewed_decision.review_basis
    normalized_payload["review_decision"] = reviewed_decision.model_dump(mode="json")

    merged_source_ids = _merge_source_record_ids(
        source_record_ids=reviewed_decision.source_record_ids,
        payload_source_ids=normalized_payload.get("source_record_ids"),
    )
    if merged_source_ids:
        normalized_payload["source_record_ids"] = merged_source_ids

    return normalized_payload


def replay_reviewed_promotion(
    destination: MemoryWriteGateway | SoulDB,
    *,
    source: MemorySource,
    payload: Dict[str, object],
    decision: ReviewedPromotionDecision | Dict[str, object],
) -> str:
    """Replay an approved reviewed-promotion artifact through the write gateway."""
    gateway = destination if isinstance(destination, MemoryWriteGateway) else MemoryWriteGateway(destination)
    reviewed_payload = build_reviewed_promotion_payload(payload, decision=decision)
    return gateway.write_payload(source, reviewed_payload)


def _merge_source_record_ids(
    *,
    source_record_ids: Optional[Sequence[str]],
    payload_source_ids: object,
) -> List[str]:
    merged: List[str] = []
    seen: set[str] = set()
    candidate_values = list(source_record_ids or [])
    if isinstance(payload_source_ids, list):
        candidate_values.extend(payload_source_ids)

    for item in candidate_values:
        text = str(item).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        merged.append(text)
    return merged


def _normalize_decision(
    decision: ReviewedPromotionDecision | Dict[str, object],
) -> ReviewedPromotionDecision:
    if isinstance(decision, ReviewedPromotionDecision):
        return decision
    return ReviewedPromotionDecision.model_validate(decision)


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


__all__ = [
    "build_reviewed_promotion_decision",
    "build_reviewed_promotion_payload",
    "infer_subjectivity_layer",
    "replay_reviewed_promotion",
]
