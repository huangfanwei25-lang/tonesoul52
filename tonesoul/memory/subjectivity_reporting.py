from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional

from tonesoul.schemas import SubjectivityLayer, SubjectivityPromotionStatus

from .soul_db import MemoryRecord, MemorySource, SoulDB

_KNOWN_SUBJECTIVITY_LAYERS = (
    SubjectivityLayer.EVENT.value,
    SubjectivityLayer.MEANING.value,
    SubjectivityLayer.TENSION.value,
    SubjectivityLayer.VOW.value,
    SubjectivityLayer.IDENTITY.value,
    "unclassified",
)

_REVIEWED_PROMOTION_STATUSES = {
    SubjectivityPromotionStatus.REVIEWED.value,
    SubjectivityPromotionStatus.HUMAN_REVIEWED.value,
    SubjectivityPromotionStatus.GOVERNANCE_REVIEWED.value,
    SubjectivityPromotionStatus.APPROVED.value,
}
_SETTLED_REVIEW_STATUSES = _REVIEWED_PROMOTION_STATUSES | {
    SubjectivityPromotionStatus.REJECTED.value,
}


def _normalize_text(value: object) -> str:
    return str(value or "").strip()


def _normalize_subjectivity_layer(value: object) -> str:
    normalized = _normalize_text(value).lower()
    if normalized in _KNOWN_SUBJECTIVITY_LAYERS:
        return normalized
    return "unclassified"


def _normalize_memory_layer(value: object) -> str:
    normalized = _normalize_text(value).lower()
    return normalized or "experiential"


def _extract_promotion_status(payload: Dict[str, object]) -> str:
    gate = payload.get("promotion_gate")
    if isinstance(gate, str):
        normalized = gate.strip().lower()
        return normalized or "none"
    if not isinstance(gate, dict):
        return "none"

    for key in ("status", "decision", "mode"):
        value = gate.get(key)
        normalized = _normalize_text(value).lower()
        if normalized:
            return normalized
    return "none"


def _parse_timestamp(value: object) -> datetime:
    text = _normalize_text(value)
    if not text:
        return datetime.min.replace(tzinfo=timezone.utc)
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _record_excerpt(payload: Dict[str, object]) -> str:
    for key in ("summary", "title", "text", "content", "reflection", "topic"):
        value = payload.get(key)
        text = _normalize_text(value)
        if text:
            return text[:160]
    return ""


def _latest_review_status_by_record_id(soul_db: SoulDB) -> Dict[str, Dict[str, object]]:
    query_action_logs = getattr(soul_db, "query_action_logs", None)
    if not callable(query_action_logs):
        return {}

    try:
        rows = query_action_logs(record_type="subjectivity_review", stream="curated", limit=0)
    except TypeError:
        rows = query_action_logs(record_type="subjectivity_review", limit=0)
    if not isinstance(rows, list):
        return {}

    latest: Dict[str, Dict[str, object]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        metadata = row.get("metadata")
        metadata_dict = metadata if isinstance(metadata, dict) else {}
        review_decision = metadata_dict.get("review_decision")
        review_decision_dict = review_decision if isinstance(review_decision, dict) else {}
        review_actor = review_decision_dict.get("review_actor")
        review_actor_dict = review_actor if isinstance(review_actor, dict) else {}
        reviewed_record_id = _normalize_text(metadata_dict.get("reviewed_record_id"))
        if not reviewed_record_id or reviewed_record_id in latest:
            continue
        status = _normalize_text(metadata_dict.get("status")).lower()
        latest[reviewed_record_id] = {
            "status": status or "none",
            "settled": status in _SETTLED_REVIEW_STATUSES,
            "review_log_id": _normalize_text(row.get("id")),
            "promoted_record_id": _normalize_text(metadata_dict.get("promoted_record_id")),
            "timestamp": _normalize_text(row.get("timestamp")),
            "review_basis": _normalize_text(review_decision_dict.get("review_basis")),
            "review_notes": _normalize_text(review_decision_dict.get("notes")),
            "review_actor_id": _normalize_text(review_actor_dict.get("actor_id")),
            "review_actor_type": _normalize_text(review_actor_dict.get("actor_type")),
            "review_actor_display_name": _normalize_text(review_actor_dict.get("display_name")),
        }
    return latest


def _is_unresolved_tension(
    payload: Dict[str, object],
    *,
    record_id: Optional[str] = None,
    review_status_by_record_id: Optional[Dict[str, Dict[str, object]]] = None,
) -> bool:
    subjectivity_layer = _normalize_subjectivity_layer(payload.get("subjectivity_layer"))
    if subjectivity_layer != SubjectivityLayer.TENSION.value:
        return False
    if _extract_promotion_status(payload) in _REVIEWED_PROMOTION_STATUSES:
        return False
    reviewed_record_id = _normalize_text(record_id)
    if reviewed_record_id and review_status_by_record_id:
        settlement = review_status_by_record_id.get(reviewed_record_id)
        if settlement and bool(settlement.get("settled")):
            return False
    return True


def _iter_records(
    soul_db: SoulDB,
    *,
    source: Optional[MemorySource] = None,
    layer: Optional[str] = None,
) -> Iterable[MemoryRecord]:
    requested_layer = _normalize_memory_layer(layer) if layer is not None else None
    sources = [source] if source is not None else list(soul_db.list_sources())
    for current_source in sources:
        for record in soul_db.stream(current_source, limit=None):
            record_layer = _normalize_memory_layer(getattr(record, "layer", None))
            if requested_layer is not None and record_layer != requested_layer:
                continue
            yield record


def summarize_subjectivity_distribution(
    soul_db: SoulDB,
    *,
    source: Optional[MemorySource] = None,
    layer: Optional[str] = None,
) -> Dict[str, object]:
    by_subjectivity_layer = {name: 0 for name in _KNOWN_SUBJECTIVITY_LAYERS}
    by_memory_layer: Dict[str, int] = {}
    by_promotion_status: Dict[str, int] = {}
    unresolved_by_status: Dict[str, int] = {}
    by_source: Dict[str, int] = {}
    event_only_count = 0
    unresolved_tension_count = 0
    deferred_tension_count = 0
    settled_tension_count = 0
    total_records = 0
    review_status_by_record_id = _latest_review_status_by_record_id(soul_db)

    for record in _iter_records(soul_db, source=source, layer=layer):
        total_records += 1
        payload = record.payload if isinstance(record.payload, dict) else {}
        subjectivity_layer = _normalize_subjectivity_layer(payload.get("subjectivity_layer"))
        memory_layer = _normalize_memory_layer(getattr(record, "layer", None))
        promotion_status = _extract_promotion_status(payload)
        review_status = review_status_by_record_id.get(_normalize_text(record.record_id), {})
        source_name = getattr(record.source, "value", str(record.source))

        by_subjectivity_layer[subjectivity_layer] = (
            by_subjectivity_layer.get(subjectivity_layer, 0) + 1
        )
        by_memory_layer[memory_layer] = by_memory_layer.get(memory_layer, 0) + 1
        by_promotion_status[promotion_status] = by_promotion_status.get(promotion_status, 0) + 1
        by_source[source_name] = by_source.get(source_name, 0) + 1

        if subjectivity_layer == SubjectivityLayer.EVENT.value:
            event_only_count += 1
        if _is_unresolved_tension(
            payload,
            record_id=record.record_id,
            review_status_by_record_id=review_status_by_record_id,
        ):
            pending_status = str(review_status.get("status") or "").strip() or promotion_status
            unresolved_tension_count += 1
            unresolved_by_status[pending_status] = unresolved_by_status.get(pending_status, 0) + 1
            if pending_status == SubjectivityPromotionStatus.DEFERRED.value:
                deferred_tension_count += 1
        elif (
            subjectivity_layer == SubjectivityLayer.TENSION.value
            and review_status_by_record_id.get(_normalize_text(record.record_id), {}).get("settled")
        ):
            settled_tension_count += 1

    return {
        "total_records": total_records,
        "by_subjectivity_layer": by_subjectivity_layer,
        "by_memory_layer": by_memory_layer,
        "by_promotion_status": by_promotion_status,
        "unresolved_by_status": unresolved_by_status,
        "by_source": by_source,
        "event_only_count": event_only_count,
        "unresolved_tension_count": unresolved_tension_count,
        "deferred_tension_count": deferred_tension_count,
        "settled_tension_count": settled_tension_count,
    }


def list_subjectivity_records(
    soul_db: SoulDB,
    *,
    source: Optional[MemorySource] = None,
    layer: Optional[str] = None,
    subjectivity_layer: Optional[str] = None,
    unresolved_only: bool = False,
    limit: Optional[int] = None,
) -> List[Dict[str, object]]:
    requested_subjectivity = (
        _normalize_subjectivity_layer(subjectivity_layer)
        if subjectivity_layer is not None
        else None
    )
    rows: List[Dict[str, object]] = []
    review_status_by_record_id = _latest_review_status_by_record_id(soul_db)

    for record in _iter_records(soul_db, source=source, layer=layer):
        payload = record.payload if isinstance(record.payload, dict) else {}
        current_subjectivity = _normalize_subjectivity_layer(payload.get("subjectivity_layer"))
        promotion_status = _extract_promotion_status(payload)
        review_status = review_status_by_record_id.get(_normalize_text(record.record_id), {})
        is_unresolved_tension = _is_unresolved_tension(
            payload,
            record_id=record.record_id,
            review_status_by_record_id=review_status_by_record_id,
        )
        if requested_subjectivity is not None and current_subjectivity != requested_subjectivity:
            continue
        if unresolved_only and not is_unresolved_tension:
            continue

        rows.append(
            {
                "record_id": record.record_id,
                "source": getattr(record.source, "value", str(record.source)),
                "timestamp": record.timestamp,
                "type": str(payload.get("type") or ""),
                "title": str(payload.get("title") or ""),
                "topic": str(payload.get("topic") or ""),
                "source_url": str(payload.get("source_url") or ""),
                "layer": _normalize_memory_layer(getattr(record, "layer", None)),
                "subjectivity_layer": current_subjectivity,
                "promotion_status": promotion_status,
                "pending_status": str(review_status.get("status") or "").strip()
                or promotion_status,
                "unresolved_tension": is_unresolved_tension,
                "review_status": str(review_status.get("status") or ""),
                "settled_by_review": bool(review_status.get("settled")),
                "review_log_id": str(review_status.get("review_log_id") or ""),
                "review_timestamp": str(review_status.get("timestamp") or ""),
                "promoted_record_id": str(review_status.get("promoted_record_id") or ""),
                "review_basis": str(review_status.get("review_basis") or ""),
                "review_notes": str(review_status.get("review_notes") or ""),
                "review_actor_id": str(review_status.get("review_actor_id") or ""),
                "review_actor_type": str(review_status.get("review_actor_type") or ""),
                "review_actor_display_name": str(
                    review_status.get("review_actor_display_name") or ""
                ),
                "summary": _record_excerpt(payload),
                "source_record_ids": list(payload.get("source_record_ids") or []),
            }
        )

    rows.sort(key=lambda item: _parse_timestamp(item.get("timestamp")), reverse=True)

    if limit is None:
        return rows
    resolved_limit = int(limit)
    if resolved_limit <= 0:
        return []
    return rows[:resolved_limit]
