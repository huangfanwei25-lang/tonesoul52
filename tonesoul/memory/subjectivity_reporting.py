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


def _is_unresolved_tension(payload: Dict[str, object]) -> bool:
    subjectivity_layer = _normalize_subjectivity_layer(payload.get("subjectivity_layer"))
    if subjectivity_layer != SubjectivityLayer.TENSION.value:
        return False
    return _extract_promotion_status(payload) not in _REVIEWED_PROMOTION_STATUSES


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
    by_source: Dict[str, int] = {}
    event_only_count = 0
    unresolved_tension_count = 0
    total_records = 0

    for record in _iter_records(soul_db, source=source, layer=layer):
        total_records += 1
        payload = record.payload if isinstance(record.payload, dict) else {}
        subjectivity_layer = _normalize_subjectivity_layer(payload.get("subjectivity_layer"))
        memory_layer = _normalize_memory_layer(getattr(record, "layer", None))
        promotion_status = _extract_promotion_status(payload)
        source_name = getattr(record.source, "value", str(record.source))

        by_subjectivity_layer[subjectivity_layer] = (
            by_subjectivity_layer.get(subjectivity_layer, 0) + 1
        )
        by_memory_layer[memory_layer] = by_memory_layer.get(memory_layer, 0) + 1
        by_promotion_status[promotion_status] = by_promotion_status.get(promotion_status, 0) + 1
        by_source[source_name] = by_source.get(source_name, 0) + 1

        if subjectivity_layer == SubjectivityLayer.EVENT.value:
            event_only_count += 1
        if _is_unresolved_tension(payload):
            unresolved_tension_count += 1

    return {
        "total_records": total_records,
        "by_subjectivity_layer": by_subjectivity_layer,
        "by_memory_layer": by_memory_layer,
        "by_promotion_status": by_promotion_status,
        "by_source": by_source,
        "event_only_count": event_only_count,
        "unresolved_tension_count": unresolved_tension_count,
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
        _normalize_subjectivity_layer(subjectivity_layer) if subjectivity_layer is not None else None
    )
    rows: List[Dict[str, object]] = []

    for record in _iter_records(soul_db, source=source, layer=layer):
        payload = record.payload if isinstance(record.payload, dict) else {}
        current_subjectivity = _normalize_subjectivity_layer(payload.get("subjectivity_layer"))
        is_unresolved_tension = _is_unresolved_tension(payload)
        if requested_subjectivity is not None and current_subjectivity != requested_subjectivity:
            continue
        if unresolved_only and not is_unresolved_tension:
            continue

        rows.append(
            {
                "record_id": record.record_id,
                "source": getattr(record.source, "value", str(record.source)),
                "timestamp": record.timestamp,
                "layer": _normalize_memory_layer(getattr(record, "layer", None)),
                "subjectivity_layer": current_subjectivity,
                "promotion_status": _extract_promotion_status(payload),
                "unresolved_tension": is_unresolved_tension,
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
