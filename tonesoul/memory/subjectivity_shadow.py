from __future__ import annotations

from typing import Dict, List, Optional

from .soul_db import MemorySource, SoulDB
from .subjectivity_reporting import (
    _REVIEWED_PROMOTION_STATUSES,
    _extract_promotion_status,
    _is_unresolved_tension,
    _normalize_memory_layer,
    _normalize_subjectivity_layer,
    _parse_timestamp,
    _record_excerpt,
)

_SHADOW_PROFILES = {
    "classified_first",
    "tension_first",
    "reviewed_vow_first",
}


def _normalize_profile(value: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized not in _SHADOW_PROFILES:
        raise ValueError(
            "shadow profile must be one of: classified_first, tension_first, reviewed_vow_first"
        )
    return normalized


def _subjectivity_distribution(rows: List[Dict[str, object]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for row in rows:
        layer = _normalize_subjectivity_layer(row.get("subjectivity_layer"))
        counts[layer] = counts.get(layer, 0) + 1
    return counts


def _score_candidate(
    row: Dict[str, object],
    *,
    profile: str,
) -> tuple[float, List[str]]:
    boost = 0.0
    reasons: List[str] = []
    subjectivity_layer = _normalize_subjectivity_layer(row.get("subjectivity_layer"))
    promotion_status = str(row.get("promotion_status") or "")
    reviewed = promotion_status in _REVIEWED_PROMOTION_STATUSES
    unresolved_tension = bool(row.get("unresolved_tension"))

    if profile == "classified_first":
        if subjectivity_layer != "unclassified":
            boost += 0.2
            reasons.append("classified_subjectivity")
        if reviewed:
            boost += 0.08
            reasons.append("reviewed_memory")
    elif profile == "tension_first":
        if subjectivity_layer == "tension":
            boost += 0.22
            reasons.append("tension_match")
        if unresolved_tension:
            boost += 0.12
            reasons.append("unresolved_tension")
        if row.get("source_record_ids"):
            boost += 0.05
            reasons.append("linked_source_trace")
    elif profile == "reviewed_vow_first":
        if subjectivity_layer == "vow":
            boost += 0.24
            reasons.append("vow_match")
        if reviewed:
            boost += 0.16
            reasons.append("reviewed_memory")
        if _normalize_memory_layer(row.get("layer")) == "factual":
            boost += 0.04
            reasons.append("factual_layer")

    return round(boost, 4), reasons


def _build_candidate_rows(
    soul_db: SoulDB,
    *,
    query: str,
    source: Optional[MemorySource],
    candidate_limit: int,
) -> List[Dict[str, object]]:
    resolved_candidate_limit = max(1, int(candidate_limit))
    search_limit = resolved_candidate_limit * (4 if source is not None else 1)
    search_rows = soul_db.search(query, limit=search_limit)
    if not search_rows:
        return []

    detail_rows = {row["id"]: row for row in soul_db.detail([str(item["id"]) for item in search_rows])}
    candidates: List[Dict[str, object]] = []
    for baseline_rank, search_row in enumerate(search_rows, start=1):
        record_id = str(search_row.get("id") or "").strip()
        detail = detail_rows.get(record_id)
        if not detail:
            continue
        current_source = str(detail.get("source") or "").strip().lower()
        if source is not None and current_source != source.value:
            continue
        payload = detail.get("payload")
        payload_dict = payload if isinstance(payload, dict) else {}
        row = {
            "record_id": record_id,
            "title": str(search_row.get("title") or detail.get("title") or "").strip(),
            "summary": _record_excerpt(payload_dict),
            "source": current_source,
            "timestamp": detail.get("timestamp"),
            "layer": _normalize_memory_layer(detail.get("layer")),
            "subjectivity_layer": _normalize_subjectivity_layer(
                payload_dict.get("subjectivity_layer")
            ),
            "promotion_status": _extract_promotion_status(payload_dict),
            "unresolved_tension": _is_unresolved_tension(payload_dict),
            "source_record_ids": list(payload_dict.get("source_record_ids") or []),
            "baseline_score": float(search_row.get("score") or 0.0),
            "baseline_rank": baseline_rank,
        }
        candidates.append(row)
        if len(candidates) >= resolved_candidate_limit:
            break
    return candidates


def build_subjectivity_shadow_report(
    soul_db: SoulDB,
    *,
    query: str,
    source: Optional[MemorySource] = None,
    profile: str = "classified_first",
    limit: int = 5,
    candidate_limit: int = 20,
) -> Dict[str, object]:
    resolved_limit = max(1, int(limit))
    normalized_profile = _normalize_profile(profile)
    candidates = _build_candidate_rows(
        soul_db,
        query=query,
        source=source,
        candidate_limit=max(resolved_limit, int(candidate_limit)),
    )

    baseline_results = [dict(row) for row in candidates[:resolved_limit]]
    shadow_candidates: List[Dict[str, object]] = []
    for row in candidates:
        boost, reasons = _score_candidate(row, profile=normalized_profile)
        shadow_row = dict(row)
        shadow_row["shadow_boost"] = boost
        shadow_row["shadow_reasons"] = reasons
        shadow_row["shadow_score"] = round(float(row["baseline_score"]) + boost, 4)
        shadow_candidates.append(shadow_row)

    shadow_candidates.sort(
        key=lambda item: (
            float(item.get("shadow_score") or 0.0),
            _parse_timestamp(item.get("timestamp")),
            -int(item.get("baseline_rank") or 0),
        ),
        reverse=True,
    )
    shadow_results = shadow_candidates[:resolved_limit]

    baseline_ids = [str(row["record_id"]) for row in baseline_results]
    shadow_ids = [str(row["record_id"]) for row in shadow_results]
    overlap = [record_id for record_id in shadow_ids if record_id in baseline_ids]
    promoted = [record_id for record_id in shadow_ids if record_id not in baseline_ids]
    demoted = [record_id for record_id in baseline_ids if record_id not in shadow_ids]

    return {
        "query": str(query or "").strip(),
        "profile": normalized_profile,
        "candidate_count": len(candidates),
        "baseline_results": baseline_results,
        "shadow_results": shadow_results,
        "metrics": {
            "baseline_count": len(baseline_results),
            "shadow_count": len(shadow_results),
            "overlap_count": len(overlap),
            "promoted_count": len(promoted),
            "demoted_count": len(demoted),
            "baseline_by_subjectivity_layer": _subjectivity_distribution(baseline_results),
            "shadow_by_subjectivity_layer": _subjectivity_distribution(shadow_results),
        },
        "delta": {
            "overlap_ids": overlap,
            "promoted_ids": promoted,
            "demoted_ids": demoted,
        },
    }


__all__ = ["build_subjectivity_shadow_report"]
