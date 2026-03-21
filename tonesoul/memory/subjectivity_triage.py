from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean
from typing import Dict, List, Optional

from .soul_db import MemorySource, SoulDB
from .subjectivity_handoff import build_handoff_surface, normalize_status_lines, primary_status_line
from .subjectivity_reporting import list_subjectivity_records

_FRICTION_LOW_MAX = 0.30
_FRICTION_MEDIUM_MAX = 0.50


def _normalize_text(value: object) -> str:
    return str(value or "").strip()


def _normalize_string_list(value: object) -> List[str]:
    if isinstance(value, list):
        return [text for item in value if (text := _normalize_text(item))]
    text = _normalize_text(value)
    return [text] if text else []


def _normalize_topic(payload: Dict[str, object], row: Dict[str, object]) -> str:
    for key in ("topic", "title", "summary", "reflection"):
        text = _normalize_text(payload.get(key))
        if not text:
            continue
        if text.startswith("Dream collision: "):
            return text.split("Dream collision: ", 1)[1].strip()
        if "Dream collision examined '" in text and "'. Friction=" in text:
            return (
                text.split("Dream collision examined '", 1)[1].split("'. Friction=", 1)[0].strip()
            )
        return text
    return _normalize_text(row.get("summary")) or "<unknown>"


def _extract_friction_score(payload: Dict[str, object], row: Dict[str, object]) -> float:
    for candidate in (
        payload.get("friction_score"),
        payload.get("tension"),
        payload.get("tension_score"),
    ):
        try:
            return float(candidate)
        except (TypeError, ValueError):
            continue

    summary = _normalize_text(row.get("summary"))
    marker = ". Friction="
    if marker in summary:
        try:
            return float(summary.split(marker, 1)[1].split(" ", 1)[0])
        except (TypeError, ValueError):
            return 0.0
    return 0.0


def _friction_band(score: float) -> str:
    if score < _FRICTION_LOW_MAX:
        return "low"
    if score <= _FRICTION_MEDIUM_MAX:
        return "medium"
    return "high"


def _infer_direction(payload: Dict[str, object], row: Dict[str, object]) -> str:
    haystack = " ".join(
        _normalize_text(value).lower()
        for value in (
            payload.get("summary"),
            payload.get("reflection"),
            payload.get("council_reason"),
            payload.get("topic"),
            payload.get("title"),
            payload.get("source_url"),
            row.get("summary"),
        )
    )
    if any(term in haystack for term in ("provenance", "traceable", "audit", "isnad")):
        return "provenance_discipline"
    if any(term in haystack for term in ("boundary", "guardrail", "constraint", "scope")):
        return "boundary_discipline"
    if any(
        term in haystack for term in ("safety", "harm", "risk", "fail-closed", "critical", "block")
    ):
        return "safety_boundary"
    if any(term in haystack for term in ("resource", "budget", "compute", "cost", "latency")):
        return "resource_discipline"
    if any(term in haystack for term in ("governance", "threshold", "council", "breaker")):
        return "governance_escalation"
    return "undifferentiated_tension"


def _dream_cycle_id(payload: Dict[str, object]) -> str:
    if _normalize_text(payload.get("dream_cycle_id")):
        return _normalize_text(payload.get("dream_cycle_id"))
    provenance = payload.get("provenance")
    if isinstance(provenance, dict):
        return _normalize_text(provenance.get("dream_cycle_id"))
    return ""


def _source_url(payload: Dict[str, object]) -> str:
    if _normalize_text(payload.get("source_url")):
        return _normalize_text(payload.get("source_url"))
    provenance = payload.get("provenance")
    if isinstance(provenance, dict):
        return _normalize_text(provenance.get("source_url"))
    return ""


def _stimulus_lineage(payload: Dict[str, object], row: Dict[str, object]) -> str:
    if _normalize_text(payload.get("stimulus_record_id")):
        return _normalize_text(payload.get("stimulus_record_id"))
    source_record_ids = _normalize_string_list(payload.get("source_record_ids"))
    if source_record_ids:
        return " + ".join(source_record_ids)
    row_source_ids = _normalize_string_list(row.get("source_record_ids"))
    if row_source_ids:
        return " + ".join(row_source_ids)
    return _normalize_text(row.get("record_id"))


def _enrich_row(row: Dict[str, object], detail: Dict[str, object]) -> Dict[str, object]:
    payload = detail.get("payload")
    payload_dict = payload if isinstance(payload, dict) else {}
    friction_score = _extract_friction_score(payload_dict, row)
    return {
        "record_id": _normalize_text(row.get("record_id")),
        "timestamp": _normalize_text(row.get("timestamp")),
        "summary": _normalize_text(row.get("summary")),
        "topic": _normalize_topic(payload_dict, row),
        "source_url": _source_url(payload_dict),
        "direction": _infer_direction(payload_dict, row),
        "friction_score": round(float(friction_score), 4),
        "friction_band": _friction_band(float(friction_score)),
        "dream_cycle_id": _dream_cycle_id(payload_dict),
        "stimulus_lineage": _stimulus_lineage(payload_dict, row),
        "source_record_ids": _normalize_string_list(
            payload_dict.get("source_record_ids") or row.get("source_record_ids")
        ),
    }


def _semantic_group_key(row: Dict[str, object]) -> tuple[str, str, str]:
    return (
        str(row.get("topic") or "<unknown>"),
        str(row.get("direction") or "undifferentiated_tension"),
        str(row.get("friction_band") or "low"),
    )


def _lineage_group_key(row: Dict[str, object]) -> tuple[str, str]:
    return (
        str(row.get("stimulus_lineage") or ""),
        str(row.get("topic") or "<unknown>"),
    )


def _recommend_semantic_group(group: Dict[str, object]) -> tuple[str, str]:
    direction = str(group.get("direction") or "undifferentiated_tension")
    source_url_count = int(group.get("source_url_count") or 0)
    lineage_count = int(group.get("lineage_count") or 0)
    cycle_count = int(group.get("cycle_count") or 0)

    if direction == "undifferentiated_tension":
        return (
            "reject_review",
            "No stable normative direction is visible beyond unresolved friction.",
        )
    if direction == "governance_escalation" and source_url_count <= 1 and lineage_count <= 1:
        return (
            "reject_review",
            "Same-source repetition without context diversity does not justify commitment weight.",
        )
    if direction == "governance_escalation" and source_url_count <= 1:
        return (
            "defer_review",
            "Cross-cycle repetition exists, but it is still dominated by one source loop and weak directionality.",
        )
    if (
        direction
        in {
            "boundary_discipline",
            "provenance_discipline",
            "resource_discipline",
            "safety_boundary",
        }
        and lineage_count >= 2
        and cycle_count >= 2
        and source_url_count >= 2
    ):
        return (
            "candidate_for_manual_review",
            "Directional choice appears across more than one lineage and source context.",
        )
    return (
        "defer_review",
        "A directional signal may be emerging, but review should wait for broader evidence or stronger context diversity.",
    )


def _duplicate_pressure_profile(group: Dict[str, object]) -> Dict[str, object]:
    source_url_count = int(group.get("source_url_count") or 0)
    record_count = int(group.get("record_count") or 0)
    lineage_count = max(1, int(group.get("lineage_count") or 0))
    cycle_count = max(1, int(group.get("cycle_count") or 0))
    rows_per_lineage = round(record_count / lineage_count, 2)
    rows_per_cycle = round(record_count / cycle_count, 2)
    same_source_loop = source_url_count <= 1

    if same_source_loop and record_count >= 6 and rows_per_lineage >= 2.0 and cycle_count >= 4:
        return {
            "same_source_loop": True,
            "rows_per_lineage": rows_per_lineage,
            "rows_per_cycle": rows_per_cycle,
            "duplicate_pressure": "high",
            "duplicate_pressure_reason": (
                "One source loop is reopening the queue with repeated collision rows across "
                "many cycles and lineages."
            ),
            "producer_followup": "upstream_dedup_candidate",
        }
    if same_source_loop and record_count >= 3 and rows_per_lineage >= 1.5 and cycle_count >= 2:
        return {
            "same_source_loop": True,
            "rows_per_lineage": rows_per_lineage,
            "rows_per_cycle": rows_per_cycle,
            "duplicate_pressure": "medium",
            "duplicate_pressure_reason": (
                "Single-source recurrence is beginning to dominate unresolved row volume."
            ),
            "producer_followup": "observe_same_source_loop",
        }
    return {
        "same_source_loop": same_source_loop,
        "rows_per_lineage": rows_per_lineage,
        "rows_per_cycle": rows_per_cycle,
        "duplicate_pressure": "low",
        "duplicate_pressure_reason": (
            "No dominant same-source duplicate loop is visible at the current grouping level."
        ),
        "producer_followup": "none",
    }


def _lineage_density_profile(lineage_groups: List[Dict[str, object]]) -> Dict[str, object]:
    record_counts = [
        int(group.get("record_count") or 0)
        for group in lineage_groups
        if int(group.get("record_count") or 0) > 0
    ]
    histogram = Counter(record_counts)
    repeated_lineage_count = sum(1 for count in record_counts if count >= 2)
    dense_lineage_count = sum(1 for count in record_counts if count >= 3)
    singleton_lineage_count = sum(1 for count in record_counts if count == 1)
    return {
        "repeated_lineage_count": repeated_lineage_count,
        "dense_lineage_count": dense_lineage_count,
        "singleton_lineage_count": singleton_lineage_count,
        "max_lineage_record_count": max(record_counts, default=0),
        "lineage_record_histogram": {
            str(count): int(total) for count, total in sorted(histogram.items())
        },
    }


def _lineage_density_snapshot(histogram: Dict[str, object]) -> str:
    if not histogram:
        return ""
    parts: List[str] = []
    for row_count, lineage_total in sorted(
        ((int(key), int(value)) for key, value in histogram.items()),
        reverse=True,
    ):
        parts.append(f"{row_count}r x{lineage_total}")
    return ", ".join(parts)


def _semantic_group_shape(group: Dict[str, object]) -> str:
    recommendation = str(group.get("triage_recommendation") or "")
    duplicate_pressure = str(group.get("duplicate_pressure") or "low")
    same_source_loop = bool(group.get("same_source_loop"))
    source_url_count = int(group.get("source_url_count") or 0)
    lineage_count = int(group.get("lineage_count") or 0)

    if recommendation == "candidate_for_manual_review":
        return "manual_review_candidate"
    if same_source_loop and duplicate_pressure == "high":
        return "high_duplicate_same_source_loop"
    if same_source_loop:
        return "same_source_loop_monitor"
    if source_url_count >= 2 and lineage_count >= 2:
        return "cross_context_group"
    return "unresolved_group"


def _semantic_group_status_line(group: Dict[str, object]) -> str:
    density_snapshot = _lineage_density_snapshot(dict(group.get("lineage_record_histogram") or {}))
    status_line = (
        f"{group.get('group_shape', '')} | {group.get('topic', '<unknown>')} | "
        f"recommendation={group.get('triage_recommendation', '')} | "
        f"rows={group.get('record_count', 0)} lineages={group.get('lineage_count', 0)} "
        f"cycles={group.get('cycle_count', 0)}"
    )
    if density_snapshot:
        status_line += f" | density={density_snapshot}"
    producer_followup = str(group.get("producer_followup") or "none")
    if producer_followup and producer_followup != "none":
        status_line += f" | followup={producer_followup}"
    return status_line


def _handoff_shape(
    *,
    semantic_groups: List[Dict[str, object]],
    multi_direction_topic_count: int,
) -> str:
    if not semantic_groups:
        return "empty_queue"
    if multi_direction_topic_count > 0 or any(
        str(group.get("triage_recommendation") or "") == "candidate_for_manual_review"
        for group in semantic_groups
    ):
        return "action_required"
    if len(semantic_groups) == 1 and bool(semantic_groups[0].get("same_source_loop")):
        return "monitoring_queue"
    if len(semantic_groups) == 1:
        return "single_group"
    return "multi_group"


def _build_multi_direction_topics(
    semantic_groups: List[Dict[str, object]],
) -> List[Dict[str, object]]:
    topic_to_directions: Dict[str, set[str]] = defaultdict(set)
    for group in semantic_groups:
        topic = str(group.get("topic") or "<unknown>")
        direction = str(group.get("direction") or "undifferentiated_tension")
        topic_to_directions[topic].add(direction)

    topics: List[Dict[str, object]] = []
    for topic, directions in topic_to_directions.items():
        if len(directions) <= 1:
            continue
        topics.append(
            {
                "topic": topic,
                "directions": sorted(directions),
                "direction_count": len(directions),
            }
        )
    topics.sort(key=lambda item: (-int(item["direction_count"]), str(item["topic"])))
    return topics


def build_subjectivity_tension_rows(
    soul_db: SoulDB,
    *,
    source: Optional[MemorySource] = None,
    unresolved_only: bool = False,
) -> List[Dict[str, object]]:
    rows = list_subjectivity_records(
        soul_db,
        source=source,
        subjectivity_layer="tension",
        unresolved_only=unresolved_only,
        limit=None,
    )
    if not rows:
        return []

    details = {row["id"]: row for row in soul_db.detail([str(item["record_id"]) for item in rows])}
    return [
        {
            **dict(row),
            **_enrich_row(row, details.get(str(row["record_id"]), {})),
        }
        for row in rows
    ]


def build_subjectivity_tension_group_report(
    soul_db: SoulDB,
    *,
    source: Optional[MemorySource] = None,
) -> Dict[str, object]:
    enriched_rows = build_subjectivity_tension_rows(
        soul_db,
        source=source,
        unresolved_only=True,
    )
    if not enriched_rows:
        return {
            "summary": {
                "unresolved_row_count": 0,
                "semantic_group_count": 0,
                "lineage_group_count": 0,
                "multi_direction_topic_count": 0,
            },
            "handoff": build_handoff_surface(
                queue_shape="empty_queue",
                requires_operator_action=False,
                status_lines=[],
                extra_fields={
                    "semantic_group_count": 0,
                    "status_line_count": 0,
                    "top_group_shape": "",
                },
            ),
            "primary_status_line": "",
            "status_lines": [],
            "semantic_groups": [],
            "lineage_groups": [],
            "multi_direction_topics": [],
        }

    semantic_buckets: Dict[tuple[str, str, str], List[Dict[str, object]]] = defaultdict(list)
    lineage_buckets: Dict[tuple[str, str], List[Dict[str, object]]] = defaultdict(list)
    for row in enriched_rows:
        semantic_buckets[_semantic_group_key(row)].append(row)
        lineage_buckets[_lineage_group_key(row)].append(row)

    lineage_groups: List[Dict[str, object]] = []
    for key, rows in lineage_buckets.items():
        timestamps = sorted({str(row["timestamp"]) for row in rows})
        cycles = sorted({str(row["dream_cycle_id"]) for row in rows if str(row["dream_cycle_id"])})
        lineage_groups.append(
            {
                "lineage_key": f"{key[0]}::{key[1]}",
                "stimulus_lineage": key[0],
                "topic": key[1],
                "record_count": len(rows),
                "cycle_count": len(cycles),
                "timestamps": timestamps,
                "dream_cycle_ids": cycles,
                "sample_record_ids": [str(row["record_id"]) for row in rows[:5]],
            }
        )
    lineage_groups.sort(key=lambda item: (-int(item["record_count"]), str(item["topic"])))

    semantic_groups: List[Dict[str, object]] = []
    for key, rows in semantic_buckets.items():
        lineages = sorted(
            {str(row["stimulus_lineage"]) for row in rows if str(row["stimulus_lineage"])}
        )
        matching_lineage_groups = [
            lineage_group
            for lineage_group in lineage_groups
            if str(lineage_group.get("topic") or "") == key[0]
            and str(lineage_group.get("stimulus_lineage") or "") in lineages
        ]
        cycles = sorted({str(row["dream_cycle_id"]) for row in rows if str(row["dream_cycle_id"])})
        source_urls = sorted({str(row["source_url"]) for row in rows if str(row["source_url"])})
        recommendation, reason = _recommend_semantic_group(
            {
                "direction": key[1],
                "source_url_count": len(source_urls),
                "lineage_count": len(lineages),
                "cycle_count": len(cycles),
            }
        )
        duplicate_pressure = _duplicate_pressure_profile(
            {
                "source_url_count": len(source_urls),
                "record_count": len(rows),
                "lineage_count": len(lineages),
                "cycle_count": len(cycles),
            }
        )
        lineage_density = _lineage_density_profile(matching_lineage_groups)
        group_shape = _semantic_group_shape(
            {
                "triage_recommendation": recommendation,
                "duplicate_pressure": duplicate_pressure.get("duplicate_pressure"),
                "same_source_loop": duplicate_pressure.get("same_source_loop"),
                "source_url_count": len(source_urls),
                "lineage_count": len(lineages),
            }
        )
        semantic_groups.append(
            {
                "group_key": " | ".join(
                    (
                        key[0] or "<unknown>",
                        key[1] or "undifferentiated_tension",
                        key[2] or "low",
                    )
                ),
                "topic": key[0],
                "primary_source_url": source_urls[0] if len(source_urls) == 1 else "",
                "source_urls": source_urls,
                "direction": key[1],
                "friction_band": key[2],
                "avg_friction_score": round(mean(float(row["friction_score"]) for row in rows), 4),
                "record_count": len(rows),
                "record_ids": [str(row["record_id"]) for row in rows],
                "lineage_count": len(lineages),
                "cycle_count": len(cycles),
                "source_url_count": len(source_urls),
                "stimulus_lineages": lineages,
                "dream_cycle_ids": cycles,
                "first_seen": min(str(row["timestamp"]) for row in rows),
                "last_seen": max(str(row["timestamp"]) for row in rows),
                "sample_record_ids": [str(row["record_id"]) for row in rows[:6]],
                "sample_summaries": list(dict.fromkeys(str(row["summary"]) for row in rows))[:3],
                "triage_recommendation": recommendation,
                "triage_reason": reason,
                "group_shape": group_shape,
                **duplicate_pressure,
                **lineage_density,
            }
        )
    semantic_groups.sort(
        key=lambda item: (
            -int(item["record_count"]),
            -int(item["cycle_count"]),
            str(item["topic"]),
        )
    )

    multi_direction_topics = _build_multi_direction_topics(semantic_groups)
    recommendation_counts = Counter(group["triage_recommendation"] for group in semantic_groups)
    direction_counts = Counter(group["direction"] for group in semantic_groups)
    duplicate_pressure_counts = Counter(group["duplicate_pressure"] for group in semantic_groups)
    producer_followup_counts = Counter(
        str(group.get("producer_followup") or "")
        for group in semantic_groups
        if str(group.get("producer_followup") or "")
        and str(group.get("producer_followup")) != "none"
    )
    status_lines = normalize_status_lines(
        [_semantic_group_status_line(group) for group in semantic_groups]
    )
    handoff_shape = _handoff_shape(
        semantic_groups=semantic_groups,
        multi_direction_topic_count=len(multi_direction_topics),
    )
    summary = {
        "unresolved_row_count": len(enriched_rows),
        "semantic_group_count": len(semantic_groups),
        "lineage_group_count": len(lineage_groups),
        "multi_direction_topic_count": len(multi_direction_topics),
        "recommendation_counts": dict(recommendation_counts),
        "direction_counts": dict(direction_counts),
        "duplicate_pressure_counts": dict(duplicate_pressure_counts),
        "producer_followup_counts": dict(producer_followup_counts),
    }
    return {
        "summary": summary,
        "handoff": build_handoff_surface(
            queue_shape=handoff_shape,
            requires_operator_action=handoff_shape == "action_required",
            status_lines=status_lines,
            extra_fields={
                "semantic_group_count": len(semantic_groups),
                "status_line_count": len(status_lines),
                "top_group_shape": (
                    str(semantic_groups[0].get("group_shape") or "") if semantic_groups else ""
                ),
            },
        ),
        "primary_status_line": primary_status_line(status_lines),
        "status_lines": status_lines,
        "semantic_groups": semantic_groups,
        "lineage_groups": lineage_groups,
        "multi_direction_topics": multi_direction_topics,
    }


__all__ = ["build_subjectivity_tension_group_report"]
