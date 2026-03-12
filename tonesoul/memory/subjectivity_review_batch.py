from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .soul_db import MemorySource, SoulDB
from .subjectivity_admissibility import build_axiomatic_admissibility_checklist
from .subjectivity_handoff import build_handoff_surface, normalize_status_lines, primary_status_line
from .subjectivity_triage import (
    build_subjectivity_tension_group_report,
    build_subjectivity_tension_rows,
)

_RECOMMENDATION_PRIORITY = {
    "candidate_for_manual_review": 0,
    "reject_review": 1,
    "defer_review": 2,
}
_RECOMMENDATION_TO_STATUS = {
    "candidate_for_manual_review": "manual_review_required",
    "reject_review": "rejected",
    "defer_review": "deferred",
}
_POSITIVE_REVIEW_STATUSES = {
    "approved",
    "governance_reviewed",
    "human_reviewed",
    "reviewed",
}
_CARRY_FORWARD_PRIORITY = {
    "prior_approved_match": 0,
    "prior_reject_match": 1,
    "prior_deferred_match_needs_revisit": 2,
    "prior_deferred_match": 3,
    "mixed_prior_decisions": 4,
    "fresh_group": 5,
}


def _default_review_status(recommendation: str) -> str:
    return _RECOMMENDATION_TO_STATUS.get(recommendation, "manual_review_required")


def _parse_timestamp(value: object) -> datetime:
    text = str(value or "").strip()
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


def _revisit_readiness(
    *,
    default_review_status: str,
    pending_status_counts: Counter[str],
    latest_review_timestamp: str,
    latest_row_timestamp: str,
) -> str:
    if default_review_status != "deferred":
        return "n/a"
    if not latest_review_timestamp:
        return "ready_for_first_deferred_write"
    if any(status != "deferred" for status in pending_status_counts if status):
        return "needs_revisit"
    if _parse_timestamp(latest_row_timestamp) > _parse_timestamp(latest_review_timestamp):
        return "needs_revisit"
    return "holding_deferred"


def _carry_forward_annotation(
    *,
    prior_decision_status_counts: Counter[str],
    revisit_readiness: str,
) -> str:
    if not prior_decision_status_counts:
        return "fresh_group"
    statuses = {status for status in prior_decision_status_counts if status}
    if statuses and statuses.issubset(_POSITIVE_REVIEW_STATUSES):
        return "prior_approved_match"
    if statuses == {"rejected"}:
        return "prior_reject_match"
    if statuses == {"deferred"}:
        if revisit_readiness == "needs_revisit":
            return "prior_deferred_match_needs_revisit"
        return "prior_deferred_match"
    return "mixed_prior_decisions"


def _matches_group_signature(
    row: Dict[str, object],
    *,
    topic: str,
    direction: str,
    source_urls: set[str],
    stimulus_lineages: set[str],
) -> bool:
    if (
        str(row.get("topic") or "<unknown>") != topic
        or str(row.get("direction") or "undifferentiated_tension") != direction
    ):
        return False

    row_source_url = str(row.get("source_url") or "").strip()
    row_stimulus_lineage = str(row.get("stimulus_lineage") or "").strip()
    source_overlap = bool(source_urls and row_source_url and row_source_url in source_urls)
    lineage_overlap = bool(
        stimulus_lineages and row_stimulus_lineage and row_stimulus_lineage in stimulus_lineages
    )
    if source_urls or stimulus_lineages:
        return source_overlap or lineage_overlap
    return False


def _latest_prior_status(rows: List[Dict[str, object]]) -> str:
    if not rows:
        return ""
    _, row = max(
        enumerate(rows),
        key=lambda item: (_parse_timestamp(item[1].get("review_timestamp")), item[0]),
    )
    return str(row.get("review_status") or "").strip()


def _latest_review_context(rows: List[Dict[str, object]]) -> Dict[str, str]:
    if not rows:
        return {
            "latest_review_status": "",
            "latest_review_basis": "",
            "latest_review_notes": "",
            "latest_review_actor_id": "",
            "latest_review_actor_type": "",
            "latest_review_actor_display_name": "",
        }
    _, row = max(
        enumerate(rows),
        key=lambda item: (_parse_timestamp(item[1].get("review_timestamp")), item[0]),
    )
    return {
        "latest_review_status": str(row.get("review_status") or "").strip(),
        "latest_review_basis": str(row.get("review_basis") or "").strip(),
        "latest_review_notes": str(row.get("review_notes") or "").strip(),
        "latest_review_actor_id": str(row.get("review_actor_id") or "").strip(),
        "latest_review_actor_type": str(row.get("review_actor_type") or "").strip(),
        "latest_review_actor_display_name": str(row.get("review_actor_display_name") or "").strip(),
    }


def _review_basis_template(group: Dict[str, object]) -> str:
    topic = str(group.get("topic") or "<unknown>")
    record_count = int(group.get("record_count") or 0)
    lineage_count = int(group.get("lineage_count") or 0)
    cycle_count = int(group.get("cycle_count") or 0)
    source_url_count = int(group.get("source_url_count") or 0)
    direction = str(group.get("direction") or "undifferentiated_tension")
    recommendation = str(group.get("triage_recommendation") or "")

    if recommendation == "reject_review":
        return (
            f"{topic} repeated across {record_count} unresolved row(s) and {cycle_count} cycle(s), "
            f"but stayed within {source_url_count} source URL(s) and {lineage_count} lineage(s); "
            "this friction remains visible without enough context diversity or axiomatic confidence "
            "to justify commitment."
        )
    if recommendation == "defer_review":
        return (
            f"{topic} recurred across {record_count} unresolved row(s), {lineage_count} lineage(s), "
            f"and {cycle_count} cycle(s), but direction `{direction}` is still dominated by one "
            "source loop and should be revisited later rather than promoted now; admissibility "
            "under existing P0/P1 constraints is not yet strong enough to assert."
        )
    return (
        f"{topic} shows direction `{direction}` across {lineage_count} lineage(s), "
        f"{source_url_count} source URL(s), and {cycle_count} cycle(s); inspect representative "
        "rows and confirm admissibility under existing P0/P1 constraints before deciding whether "
        "a reviewed vow is warranted."
    )


def _density_compaction_followup(
    *,
    carry_forward_annotation: str,
    revisit_readiness: str,
    duplicate_pressure: str,
    same_source_loop: bool,
    record_count: int,
    lineage_count: int,
    repeated_lineage_count: int,
    dense_lineage_count: int,
    max_lineage_record_count: int,
) -> Dict[str, object]:
    if (
        carry_forward_annotation == "prior_deferred_match"
        and revisit_readiness == "holding_deferred"
        and duplicate_pressure == "high"
        and same_source_loop
        and repeated_lineage_count >= 2
    ):
        return {
            "density_compaction_candidate": True,
            "density_compaction_reason": (
                f"{record_count} deferred row(s) are concentrated into {lineage_count} lineage(s); "
                f"{repeated_lineage_count} lineage(s) repeat, {dense_lineage_count} lineage(s) "
                f"carry 3+ rows, and the deepest lineage carries {max_lineage_record_count} row(s)."
            ),
            "operator_followup": "read_only_density_compaction_candidate",
        }
    return {
        "density_compaction_candidate": False,
        "density_compaction_reason": "",
        "operator_followup": "none",
    }


def _history_density_summary(
    *,
    record_count: int,
    cycle_count: int,
    lineage_count: int,
    first_seen: str,
    last_seen: str,
    same_source_loop: bool,
    latest_review_timestamp: str,
    rows_after_latest_review: int,
) -> str:
    summary = (
        f"{record_count} row(s) across {cycle_count} cycle(s) / {lineage_count} lineage(s) "
        f"from {first_seen or '<unknown>'} to {last_seen or '<unknown>'}"
    )
    if same_source_loop:
        summary += "; same-source loop"
    if latest_review_timestamp:
        if rows_after_latest_review == 0:
            summary += "; no new rows since latest review"
        else:
            summary += f"; {rows_after_latest_review} row(s) added since latest review"
    return summary + "."


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


def _queue_posture(
    *,
    default_review_status: str,
    carry_forward_annotation: str,
    revisit_readiness: str,
) -> str:
    if (
        default_review_status == "deferred"
        and carry_forward_annotation == "prior_deferred_match"
        and revisit_readiness == "holding_deferred"
    ):
        return "stable_deferred_history"
    if (
        default_review_status == "deferred"
        and carry_forward_annotation == "prior_deferred_match_needs_revisit"
    ):
        return "deferred_revisit_queue"
    if default_review_status == "manual_review_required":
        return "active_manual_review_queue"
    if default_review_status == "rejected" and carry_forward_annotation == "prior_reject_match":
        return "rejected_reentry_watch"
    if default_review_status == "rejected":
        return "active_reject_queue"
    if default_review_status == "deferred":
        return "active_deferred_queue"
    return "active_review_queue"


def _revisit_trigger(
    *,
    queue_posture: str,
    rows_after_latest_review: int,
    latest_review_notes: str,
    same_source_loop: bool,
    default_review_status: str,
) -> str:
    if queue_posture == "deferred_revisit_queue":
        return f"triggered_now_{rows_after_latest_review}_new_row(s)_since_latest_review"
    if latest_review_notes:
        return latest_review_notes
    if default_review_status == "deferred" and same_source_loop:
        return (
            "Revisit when the same direction appears outside the current source loop, "
            "or when the group materially splits."
        )
    if default_review_status == "manual_review_required":
        return "Review now."
    return "None."


def _revisit_trigger_code(
    *,
    queue_posture: str,
    default_review_status: str,
) -> str:
    if queue_posture == "stable_deferred_history":
        return "second_source_context_or_material_split"
    if queue_posture == "deferred_revisit_queue":
        return "new_rows_since_latest_review"
    if queue_posture == "active_manual_review_queue":
        return "manual_review_required"
    if queue_posture == "rejected_reentry_watch":
        return "new_context_required"
    if default_review_status == "rejected":
        return "reject_review"
    if default_review_status == "deferred":
        return "more_context_required"
    return "review_required"


def _operator_lens_summary(
    *,
    queue_posture: str,
    record_count: int,
    lineage_count: int,
    cycle_count: int,
    lineage_density_snapshot: str,
    rows_after_latest_review: int,
) -> str:
    posture_label = {
        "stable_deferred_history": "stable deferred history",
        "deferred_revisit_queue": "deferred queue that has reopened for revisit",
        "active_manual_review_queue": "active manual review queue",
        "rejected_reentry_watch": "rejected pattern re-entry watch",
        "active_reject_queue": "active reject queue",
        "active_deferred_queue": "active deferred queue",
        "active_review_queue": "active review queue",
    }.get(queue_posture, queue_posture.replace("_", " "))
    summary = (
        f"{posture_label}; {record_count} row(s) compress to {lineage_count} lineage(s) / "
        f"{cycle_count} cycle(s)"
    )
    if lineage_density_snapshot:
        summary += f"; density={lineage_density_snapshot}"
    if rows_after_latest_review == 0:
        summary += "; no new rows since latest review"
    elif rows_after_latest_review > 0:
        summary += f"; {rows_after_latest_review} new row(s) since latest review"
    return summary + "."


def _operator_status_line(
    *,
    queue_posture: str,
    topic: str,
    record_count: int,
    lineage_count: int,
    cycle_count: int,
    lineage_density_snapshot: str,
    revisit_trigger_code: str,
) -> str:
    status_line = (
        f"{queue_posture} | {topic} | rows={record_count} lineages={lineage_count} "
        f"cycles={cycle_count}"
    )
    if lineage_density_snapshot:
        status_line += f" | density={lineage_density_snapshot}"
    status_line += f" | trigger={revisit_trigger_code}"
    return status_line


def _handoff_shape(review_groups: List[Dict[str, object]]) -> str:
    if not review_groups:
        return "empty_queue"
    postures = {str(group.get("queue_posture") or "") for group in review_groups}
    if postures and postures.issubset({"stable_deferred_history"}):
        return "stable_history_only"
    if postures & {"active_manual_review_queue", "active_review_queue", "deferred_revisit_queue"}:
        return "action_required"
    if postures & {"active_deferred_queue", "active_reject_queue", "rejected_reentry_watch"}:
        return "monitoring_queue"
    return "mixed_queue"


def build_subjectivity_review_batch_report(
    soul_db: SoulDB,
    *,
    source: Optional[MemorySource] = None,
) -> Dict[str, object]:
    grouping = build_subjectivity_tension_group_report(soul_db, source=source)
    all_tension_rows = build_subjectivity_tension_rows(
        soul_db,
        source=source,
        unresolved_only=False,
    )
    unresolved_rows = [row for row in all_tension_rows if bool(row.get("unresolved_tension"))]
    unresolved_by_record_id = {
        str(row.get("record_id") or ""): row
        for row in unresolved_rows
        if str(row.get("record_id") or "")
    }
    reviewed_rows = [row for row in all_tension_rows if str(row.get("review_status") or "").strip()]
    semantic_groups = list(grouping.get("semantic_groups") or [])
    lineage_groups = list(grouping.get("lineage_groups") or [])

    review_groups: List[Dict[str, object]] = []
    for group in semantic_groups:
        group_rows = [
            unresolved_by_record_id[record_id]
            for record_id in list(group.get("record_ids") or [])
            if record_id in unresolved_by_record_id
        ]
        stimulus_lineages = {
            str(lineage)
            for lineage in list(group.get("stimulus_lineages") or [])
            if str(lineage).strip()
        }
        matching_lineages = [
            lineage
            for lineage in lineage_groups
            if str(lineage.get("topic") or "") == str(group.get("topic") or "")
            and str(lineage.get("stimulus_lineage") or "") in stimulus_lineages
        ]
        representative_record_ids = [
            str(sample_ids[0])
            for sample_ids in (
                lineage.get("sample_record_ids") or [] for lineage in matching_lineages
            )
            if sample_ids
        ]
        recommendation = str(group.get("triage_recommendation") or "")
        default_review_status = _default_review_status(recommendation)
        pending_status_counts: Counter[str] = Counter(
            str(row.get("pending_status") or row.get("promotion_status") or "none")
            for row in group_rows
        )
        latest_review_timestamp = ""
        latest_row_timestamp = ""
        if group_rows:
            latest_row_timestamp = max(
                (str(row.get("timestamp") or "") for row in group_rows),
                key=_parse_timestamp,
                default="",
            )
            latest_review_timestamp = max(
                (
                    str(row.get("review_timestamp") or "")
                    for row in group_rows
                    if str(row.get("review_timestamp") or "").strip()
                ),
                key=_parse_timestamp,
                default="",
            )
        rows_after_latest_review = 0
        if latest_review_timestamp:
            rows_after_latest_review = sum(
                1 for row in group_rows if not str(row.get("review_status") or "").strip()
            )
        revisit_readiness = _revisit_readiness(
            default_review_status=default_review_status,
            pending_status_counts=pending_status_counts,
            latest_review_timestamp=latest_review_timestamp,
            latest_row_timestamp=latest_row_timestamp,
        )
        current_topic = str(group.get("topic") or "<unknown>")
        current_direction = str(group.get("direction") or "undifferentiated_tension")
        current_source_urls = {str(url) for url in list(group.get("source_urls") or []) if str(url)}
        current_stimulus_lineages = set(stimulus_lineages)
        matching_prior_rows = [
            row
            for row in reviewed_rows
            if _matches_group_signature(
                row,
                topic=current_topic,
                direction=current_direction,
                source_urls=current_source_urls,
                stimulus_lineages=current_stimulus_lineages,
            )
        ]
        historical_prior_decision_status_counts: Counter[str] = Counter(
            str(row.get("review_status") or "")
            for row in matching_prior_rows
            if str(row.get("review_status") or "").strip()
        )
        current_reviewed_rows = [
            row for row in group_rows if str(row.get("review_status") or "").strip()
        ]
        if current_reviewed_rows:
            active_prior_rows = current_reviewed_rows
        else:
            latest_prior_status = _latest_prior_status(matching_prior_rows)
            active_prior_rows = [
                row
                for row in matching_prior_rows
                if str(row.get("review_status") or "").strip() == latest_prior_status
            ]
        prior_decision_status_counts: Counter[str] = Counter(
            str(row.get("review_status") or "")
            for row in active_prior_rows
            if str(row.get("review_status") or "").strip()
        )
        latest_review_context = _latest_review_context(active_prior_rows)
        latest_matched_review_timestamp = max(
            (
                str(row.get("review_timestamp") or "")
                for row in active_prior_rows
                if str(row.get("review_timestamp") or "").strip()
            ),
            key=_parse_timestamp,
            default="",
        )
        carry_forward_annotation = _carry_forward_annotation(
            prior_decision_status_counts=prior_decision_status_counts,
            revisit_readiness=revisit_readiness,
        )
        density_compaction_followup = _density_compaction_followup(
            carry_forward_annotation=carry_forward_annotation,
            revisit_readiness=revisit_readiness,
            duplicate_pressure=str(group.get("duplicate_pressure") or "low"),
            same_source_loop=bool(group.get("same_source_loop")),
            record_count=int(group.get("record_count") or 0),
            lineage_count=int(group.get("lineage_count") or 0),
            repeated_lineage_count=int(group.get("repeated_lineage_count") or 0),
            dense_lineage_count=int(group.get("dense_lineage_count") or 0),
            max_lineage_record_count=int(group.get("max_lineage_record_count") or 0),
        )
        history_density_summary = _history_density_summary(
            record_count=int(group.get("record_count") or 0),
            cycle_count=int(group.get("cycle_count") or 0),
            lineage_count=int(group.get("lineage_count") or 0),
            first_seen=str(group.get("first_seen") or ""),
            last_seen=str(group.get("last_seen") or ""),
            same_source_loop=bool(group.get("same_source_loop")),
            latest_review_timestamp=latest_review_timestamp,
            rows_after_latest_review=rows_after_latest_review,
        )
        lineage_record_histogram = dict(group.get("lineage_record_histogram") or {})
        lineage_density_snapshot = _lineage_density_snapshot(lineage_record_histogram)
        queue_posture = _queue_posture(
            default_review_status=default_review_status,
            carry_forward_annotation=carry_forward_annotation,
            revisit_readiness=revisit_readiness,
        )
        revisit_trigger = _revisit_trigger(
            queue_posture=queue_posture,
            rows_after_latest_review=rows_after_latest_review,
            latest_review_notes=str(latest_review_context.get("latest_review_notes") or ""),
            same_source_loop=bool(group.get("same_source_loop")),
            default_review_status=default_review_status,
        )
        revisit_trigger_code = _revisit_trigger_code(
            queue_posture=queue_posture,
            default_review_status=default_review_status,
        )
        operator_lens_summary = _operator_lens_summary(
            queue_posture=queue_posture,
            record_count=int(group.get("record_count") or 0),
            lineage_count=int(group.get("lineage_count") or 0),
            cycle_count=int(group.get("cycle_count") or 0),
            lineage_density_snapshot=lineage_density_snapshot,
            rows_after_latest_review=rows_after_latest_review,
        )
        operator_status_line = _operator_status_line(
            queue_posture=queue_posture,
            topic=str(group.get("topic") or "<unknown>"),
            record_count=int(group.get("record_count") or 0),
            lineage_count=int(group.get("lineage_count") or 0),
            cycle_count=int(group.get("cycle_count") or 0),
            lineage_density_snapshot=lineage_density_snapshot,
            revisit_trigger_code=revisit_trigger_code,
        )
        admissibility_checklist = build_axiomatic_admissibility_checklist(
            topic=str(group.get("topic") or "<unknown>"),
            direction=current_direction,
            triage_recommendation=recommendation,
            same_source_loop=bool(group.get("same_source_loop")),
            source_url_count=int(group.get("source_url_count") or 0),
            lineage_count=int(group.get("lineage_count") or 0),
            cycle_count=int(group.get("cycle_count") or 0),
        )
        review_groups.append(
            {
                "group_key": str(group.get("group_key") or ""),
                "topic": str(group.get("topic") or "<unknown>"),
                "direction": str(group.get("direction") or "undifferentiated_tension"),
                "friction_band": str(group.get("friction_band") or "low"),
                "triage_recommendation": recommendation,
                "default_review_status_if_confirmed": default_review_status,
                "record_count": int(group.get("record_count") or 0),
                "lineage_count": int(group.get("lineage_count") or 0),
                "cycle_count": int(group.get("cycle_count") or 0),
                "source_url_count": int(group.get("source_url_count") or 0),
                "same_source_loop": bool(group.get("same_source_loop")),
                "rows_per_lineage": float(group.get("rows_per_lineage") or 0.0),
                "rows_per_cycle": float(group.get("rows_per_cycle") or 0.0),
                "repeated_lineage_count": int(group.get("repeated_lineage_count") or 0),
                "dense_lineage_count": int(group.get("dense_lineage_count") or 0),
                "singleton_lineage_count": int(group.get("singleton_lineage_count") or 0),
                "max_lineage_record_count": int(group.get("max_lineage_record_count") or 0),
                "lineage_record_histogram": lineage_record_histogram,
                "lineage_density_snapshot": lineage_density_snapshot,
                "duplicate_pressure": str(group.get("duplicate_pressure") or "low"),
                "duplicate_pressure_reason": str(group.get("duplicate_pressure_reason") or ""),
                "producer_followup": str(group.get("producer_followup") or "none"),
                "source_urls": list(group.get("source_urls") or []),
                "stimulus_lineages": sorted(stimulus_lineages),
                "first_seen": str(group.get("first_seen") or ""),
                "last_seen": str(group.get("last_seen") or ""),
                "representative_record_ids": representative_record_ids,
                "pending_status_counts": dict(pending_status_counts),
                "latest_review_timestamp": latest_review_timestamp,
                "latest_row_timestamp": latest_row_timestamp,
                "rows_after_latest_review": rows_after_latest_review,
                "revisit_readiness": revisit_readiness,
                "prior_reviewed_record_count": len(active_prior_rows),
                "historical_prior_reviewed_record_count": len(matching_prior_rows),
                "prior_decision_status_counts": dict(prior_decision_status_counts),
                "historical_prior_decision_status_counts": dict(
                    historical_prior_decision_status_counts
                ),
                "latest_matched_review_timestamp": latest_matched_review_timestamp,
                **latest_review_context,
                "prior_decision_sample_record_ids": [
                    str(row.get("record_id") or "")
                    for row in active_prior_rows[:6]
                    if str(row.get("record_id") or "")
                ],
                "carry_forward_annotation": carry_forward_annotation,
                "queue_posture": queue_posture,
                "revisit_trigger": revisit_trigger,
                "revisit_trigger_code": revisit_trigger_code,
                "review_basis_template": _review_basis_template(group),
                "axiomatic_admissibility_checklist": admissibility_checklist,
                "admissibility_status_line": str(admissibility_checklist.get("status_line") or ""),
                "history_density_summary": history_density_summary,
                "operator_lens_summary": operator_lens_summary,
                "operator_status_line": operator_status_line,
                **density_compaction_followup,
            }
        )

    review_groups.sort(
        key=lambda item: (
            _RECOMMENDATION_PRIORITY.get(str(item["triage_recommendation"]), 99),
            -int(item["record_count"]),
            str(item["topic"]),
        )
    )
    status_counts = Counter(
        str(group["default_review_status_if_confirmed"]) for group in review_groups
    )
    recommendation_counts = Counter(str(group["triage_recommendation"]) for group in review_groups)
    revisit_readiness_counts = Counter(str(group["revisit_readiness"]) for group in review_groups)
    carry_forward_annotation_counts = Counter(
        str(group["carry_forward_annotation"]) for group in review_groups
    )
    queue_posture_counts = Counter(str(group["queue_posture"]) for group in review_groups)
    duplicate_pressure_counts = Counter(str(group["duplicate_pressure"]) for group in review_groups)
    producer_followup_counts = Counter(
        str(group["producer_followup"])
        for group in review_groups
        if str(group.get("producer_followup") or "") != "none"
    )
    operator_followup_counts = Counter(
        str(group["operator_followup"])
        for group in review_groups
        if str(group.get("operator_followup") or "") != "none"
    )
    admissibility_gate_posture_counts = Counter(
        str((group.get("axiomatic_admissibility_checklist") or {}).get("gate_posture") or "")
        for group in review_groups
        if str((group.get("axiomatic_admissibility_checklist") or {}).get("gate_posture") or "")
    )
    admissibility_focus_counts = Counter(
        str((group.get("axiomatic_admissibility_checklist") or {}).get("focus") or "")
        for group in review_groups
        if str((group.get("axiomatic_admissibility_checklist") or {}).get("focus") or "")
    )
    status_lines = normalize_status_lines(
        [
            str(group["operator_status_line"])
            for group in review_groups
            if str(group.get("operator_status_line") or "").strip()
        ]
    )
    admissibility_status_lines = normalize_status_lines(
        [
            str(group["admissibility_status_line"])
            for group in review_groups
            if str(group.get("admissibility_status_line") or "").strip()
        ]
    )
    handoff_shape = _handoff_shape(review_groups)
    requires_operator_action = handoff_shape == "action_required"
    top_queue_posture = str(review_groups[0].get("queue_posture") or "") if review_groups else ""

    return {
        "summary": {
            "review_group_count": len(review_groups),
            "default_status_counts": dict(status_counts),
            "triage_recommendation_counts": dict(recommendation_counts),
            "revisit_readiness_counts": dict(revisit_readiness_counts),
            "carry_forward_annotation_counts": dict(carry_forward_annotation_counts),
            "queue_posture_counts": dict(queue_posture_counts),
            "duplicate_pressure_counts": dict(duplicate_pressure_counts),
            "producer_followup_counts": dict(producer_followup_counts),
            "operator_followup_counts": dict(operator_followup_counts),
            "admissibility_gate_posture_counts": dict(admissibility_gate_posture_counts),
            "admissibility_focus_counts": dict(admissibility_focus_counts),
            "unresolved_row_count": int(
                grouping.get("summary", {}).get("unresolved_row_count") or 0
            ),
            "semantic_group_count": int(
                grouping.get("summary", {}).get("semantic_group_count") or 0
            ),
            "lineage_group_count": int(grouping.get("summary", {}).get("lineage_group_count") or 0),
        },
        "handoff": build_handoff_surface(
            queue_shape=handoff_shape,
            requires_operator_action=requires_operator_action,
            status_lines=status_lines,
            extra_fields={
                "review_group_count": len(review_groups),
                "status_line_count": len(status_lines),
                "top_queue_posture": top_queue_posture,
            },
        ),
        "primary_status_line": primary_status_line(status_lines),
        "status_lines": status_lines,
        "admissibility_primary_status_line": primary_status_line(admissibility_status_lines),
        "admissibility_status_lines": admissibility_status_lines,
        "review_groups": review_groups,
        "grouping_summary": dict(grouping.get("summary", {})),
    }


__all__ = ["build_subjectivity_review_batch_report"]
