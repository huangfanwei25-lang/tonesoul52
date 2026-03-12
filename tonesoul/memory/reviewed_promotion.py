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

_REPLAYABLE_REVIEW_STATUSES = {
    SubjectivityPromotionStatus.REVIEWED,
    SubjectivityPromotionStatus.HUMAN_REVIEWED,
    SubjectivityPromotionStatus.GOVERNANCE_REVIEWED,
    SubjectivityPromotionStatus.APPROVED,
}
_SETTLED_REVIEW_STATUSES = _REPLAYABLE_REVIEW_STATUSES | {
    SubjectivityPromotionStatus.REJECTED,
}
_REVIEW_LOG_TYPE = "subjectivity_review"
_REVIEW_LOG_ACTION = "reviewed_promotion"


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
        str(payload.get(key) or "") for key in ("text", "content", "summary", "reflection", "topic")
    ).lower()
    if any(
        keyword in text for keyword in ("conflict", "tension", "friction", "diverge", "rupture")
    ):
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
    reviewed_record_id: Optional[str] = None,
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
            "reviewed_record_id": str(reviewed_record_id or "").strip() or None,
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
    if reviewed_decision.status not in _REPLAYABLE_REVIEW_STATUSES:
        raise ValueError("non-approved review decisions cannot be replayed")
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
    if reviewed_decision.reviewed_record_id:
        normalized_payload["reviewed_record_id"] = reviewed_decision.reviewed_record_id

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
    gateway = (
        destination
        if isinstance(destination, MemoryWriteGateway)
        else MemoryWriteGateway(destination)
    )
    reviewed_payload = build_reviewed_promotion_payload(payload, decision=decision)
    return gateway.write_payload(source, reviewed_payload)


def apply_reviewed_promotion(
    destination: MemoryWriteGateway | SoulDB,
    *,
    source: MemorySource,
    payload: Dict[str, object],
    decision: ReviewedPromotionDecision | Dict[str, object],
) -> Dict[str, object]:
    """Record a reviewed-promotion decision and replay approved promotions."""
    reviewed_decision = _normalize_decision(decision)
    gateway = (
        destination
        if isinstance(destination, MemoryWriteGateway)
        else MemoryWriteGateway(destination)
    )
    soul_db = gateway.soul_db if isinstance(destination, MemoryWriteGateway) else destination

    promoted_record_id: Optional[str] = None
    promoted_payload: Optional[Dict[str, object]] = None
    if reviewed_decision.status in _REPLAYABLE_REVIEW_STATUSES:
        promoted_payload = build_reviewed_promotion_payload(payload, decision=reviewed_decision)
        promoted_record_id = gateway.write_payload(source, promoted_payload)

    review_log_id = _append_review_log(
        soul_db,
        source=source,
        payload=payload,
        decision=reviewed_decision,
        promoted_record_id=promoted_record_id,
        promoted_payload=promoted_payload,
    )
    return {
        "review_log_id": review_log_id,
        "promoted_record_id": promoted_record_id,
        "settled": reviewed_decision.status in _SETTLED_REVIEW_STATUSES,
        "replayed": reviewed_decision.status in _REPLAYABLE_REVIEW_STATUSES,
        "decision": reviewed_decision.model_dump(mode="json"),
    }


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


def _append_review_log(
    destination: object,
    *,
    source: MemorySource,
    payload: Dict[str, object],
    decision: ReviewedPromotionDecision,
    promoted_record_id: Optional[str],
    promoted_payload: Optional[Dict[str, object]],
) -> Optional[str]:
    append_action_log = getattr(destination, "append_action_log", None)
    if not callable(append_action_log):
        return None

    metadata = {
        "reviewed_record_id": decision.reviewed_record_id,
        "status": decision.status.value,
        "settled": decision.status in _SETTLED_REVIEW_STATUSES,
        "replayed_to_memory": bool(promoted_record_id),
        "promoted_record_id": promoted_record_id,
        "source": source.value,
        "source_record_ids": list(decision.source_record_ids),
        "review_decision": decision.model_dump(mode="json"),
    }
    params = {
        "reviewed_record_id": decision.reviewed_record_id,
        "status": decision.status.value,
        "source": source.value,
        "review_actor": decision.review_actor.model_dump(mode="json"),
    }
    result = {
        "settled": decision.status in _SETTLED_REVIEW_STATUSES,
        "replayed": bool(promoted_record_id),
        "promoted_record_id": promoted_record_id,
    }
    before_context = {
        "reviewed_record_id": decision.reviewed_record_id,
        "summary": _payload_excerpt(payload),
        "subjectivity_layer": infer_subjectivity_layer(
            payload,
            target_layer=str(payload.get("layer") or "working").strip().lower() or "working",
        ),
    }
    after_context = {
        "promotion_status": decision.status.value,
        "review_basis": decision.review_basis,
        "promoted_payload": promoted_payload,
    }
    return append_action_log(
        _REVIEW_LOG_TYPE,
        _REVIEW_LOG_ACTION,
        params,
        result,
        before_context,
        after_context,
        None,
        timestamp=decision.reviewed_at,
        stream="curated",
        metadata=metadata,
    )


def _payload_excerpt(payload: Dict[str, object]) -> str:
    for key in ("summary", "title", "text", "content", "reflection", "topic"):
        text = str(payload.get(key) or "").strip()
        if text:
            return text[:160]
    return ""


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


__all__ = [
    "apply_reviewed_promotion",
    "build_reviewed_promotion_decision",
    "build_reviewed_promotion_payload",
    "infer_subjectivity_layer",
    "replay_reviewed_promotion",
]
