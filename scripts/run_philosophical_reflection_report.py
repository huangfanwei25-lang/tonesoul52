"""
Generate philosophical-reflection status artifacts from discussion and journal data.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

JSON_FILENAME = "philosophical_reflection_latest.json"
MARKDOWN_FILENAME = "philosophical_reflection_latest.md"

REFLECTION_MARKERS = (
    "philosophy",
    "philosophical",
    "reflection",
    "ethic",
    "value",
    "價值",
    "哲學",
    "反思",
    "語魂",
    "tension",
)

CONFLICT_MARKERS = (
    "conflict",
    "friction",
    "tension",
    "boundary",
    "拒絕",
    "衝突",
    "摩擦",
    "張力",
    "邊界",
    "block",
    "declare_stance",
)

CHOICE_MARKERS = (
    "choice",
    "choose",
    "stance",
    "consent",
    "選擇",
    "立場",
    "同意",
    "拒絕",
    "決策",
)

TENSION_KEYS = {
    "tension",
    "delta_t",
    "query_tension",
    "tension_score",
    "adjusted_tension",
    "semantic_tension",
    "text_tension",
    "cognitive_friction",
    "delta_s_ecs",
    "t_ecs",
    "total",
    "total_tension",
    "semantic_delta",
}

PREDICTION_TRENDS = {"stable", "converging", "diverging", "chaotic"}

CONFLICT_VERDICTS = {"block", "declare_stance", "revise"}
RESOLVED_STATUS = {"resolved", "done", "closed"}
UNRESOLVED_STATUS = {"pending", "open", "todo", "blocked", "in_progress"}


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def _rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(float(numerator) / float(denominator), 4)


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    if q <= 0.0:
        return min(values)
    if q >= 1.0:
        return max(values)
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _effective_tension_threshold(configured: float, values: list[float]) -> tuple[float, str]:
    """
    Blend configured threshold with corpus distribution.
    This prevents the threshold from being too high when historic traces are low-scale.
    """
    if not values:
        return configured, "configured"
    percentile_85 = _quantile(values, 0.85)
    adaptive = max(0.25, min(0.70, percentile_85))
    effective = min(configured, adaptive)
    if abs(effective - configured) < 1e-9:
        return configured, "configured"
    return round(effective, 4), "adaptive_p85"


def _bounded_float(value: object) -> float | None:
    if not isinstance(value, (int, float)):
        return None
    as_float = float(value)
    if as_float < 0.0 or as_float > 1.0:
        return None
    return as_float


def _read_jsonl(path: Path) -> tuple[list[dict[str, Any]], int]:
    rows: list[dict[str, Any]] = []
    invalid_line_count = 0
    if not path.exists():
        return rows, invalid_line_count

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                invalid_line_count += 1
                continue
            if isinstance(payload, dict):
                rows.append(payload)
            else:
                invalid_line_count += 1
    return rows, invalid_line_count


def _entry_payload(raw: dict[str, Any]) -> dict[str, Any]:
    payload = raw.get("payload")
    if isinstance(payload, dict):
        return payload
    return raw


def _extract_verdict(entry: dict[str, Any]) -> str:
    verdict = entry.get("verdict")
    if isinstance(verdict, str):
        text = verdict.strip().lower()
        if text:
            return text
    if isinstance(verdict, dict):
        text = str(verdict.get("verdict") or "").strip().lower()
        if text:
            return text
    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        transcript_verdict = transcript.get("verdict")
        if isinstance(transcript_verdict, dict):
            text = str(transcript_verdict.get("verdict") or "").strip().lower()
            if text:
                return text
    return "unknown"


def _extract_timestamp(entry: dict[str, Any]) -> str:
    timestamp = entry.get("timestamp")
    if isinstance(timestamp, str):
        text = timestamp.strip()
        if text:
            return text
    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        value = transcript.get("timestamp")
        if isinstance(value, str):
            text = value.strip()
            if text:
                return text
    return ""


def _normalize_status(value: object) -> str:
    if not isinstance(value, str):
        return "unknown"
    text = value.strip().lower()
    if not text:
        return "unknown"
    return text


def _normalize_topic(value: object) -> str:
    if not isinstance(value, str):
        return "unknown"
    text = value.strip()
    if not text:
        return "unknown"
    return text


def _iter_strings(node: Any) -> list[str]:
    fragments: list[str] = []
    queue: list[Any] = [node]
    while queue:
        current = queue.pop()
        if isinstance(current, str):
            text = current.strip()
            if text:
                fragments.append(text)
            continue
        if isinstance(current, dict):
            for value in current.values():
                if isinstance(value, (dict, list, str)):
                    queue.append(value)
            continue
        if isinstance(current, list):
            for value in current:
                if isinstance(value, (dict, list, str)):
                    queue.append(value)
    return fragments


def _collect_tension_values(node: Any) -> list[float]:
    values: list[float] = []
    queue: list[Any] = [node]
    while queue:
        current = queue.pop()
        if isinstance(current, dict):
            for key, value in current.items():
                if isinstance(value, (dict, list)):
                    queue.append(value)
                lowered = str(key).strip().lower()
                if lowered in TENSION_KEYS:
                    direct = _bounded_float(value)
                    if direct is not None:
                        values.append(direct)
                    if isinstance(value, dict):
                        for candidate_key in (
                            "delta_t",
                            "adjusted_tension",
                            "score",
                            "value",
                            "tension",
                            "text_tension",
                            "cognitive_friction",
                            "delta_s_ecs",
                            "t_ecs",
                            "total",
                        ):
                            nested = _bounded_float(value.get(candidate_key))
                            if nested is not None:
                                values.append(nested)
        elif isinstance(current, list):
            for value in current:
                if isinstance(value, (dict, list)):
                    queue.append(value)
    return values


def _collect_prediction_trends(node: Any) -> list[str]:
    trends: list[str] = []
    queue: list[Any] = [node]
    while queue:
        current = queue.pop()
        if isinstance(current, dict):
            for key, value in current.items():
                lowered = str(key).strip().lower()
                if isinstance(value, (dict, list)):
                    queue.append(value)
                if lowered == "prediction" and isinstance(value, dict):
                    trend = value.get("trend")
                    if isinstance(trend, str):
                        normalized = trend.strip().lower()
                        if normalized in PREDICTION_TRENDS:
                            trends.append(normalized)
                if lowered == "prediction_trend" and isinstance(value, str):
                    normalized = value.strip().lower()
                    if normalized in PREDICTION_TRENDS:
                        trends.append(normalized)
        elif isinstance(current, list):
            for value in current:
                if isinstance(value, (dict, list)):
                    queue.append(value)
    return trends


def _collect_compression_ratios(node: Any) -> list[float]:
    ratios: list[float] = []
    queue: list[Any] = [node]
    while queue:
        current = queue.pop()
        if isinstance(current, dict):
            for key, value in current.items():
                lowered = str(key).strip().lower()
                if isinstance(value, (dict, list)):
                    queue.append(value)
                if lowered == "compression_ratio":
                    ratio = _bounded_float(value)
                    if ratio is not None:
                        ratios.append(ratio)
                if lowered == "compression" and isinstance(value, dict):
                    ratio = _bounded_float(value.get("compression_ratio"))
                    if ratio is not None:
                        ratios.append(ratio)
        elif isinstance(current, list):
            for value in current:
                if isinstance(value, (dict, list)):
                    queue.append(value)
    return ratios


def _contains_marker(texts: list[str], markers: tuple[str, ...]) -> bool:
    if not texts:
        return False
    joined = "\n".join(texts).lower()
    return any(marker in joined for marker in markers)


def _extract_friction_summary(entry: dict[str, Any]) -> str:
    fields: list[object] = [
        entry.get("core_divergence"),
        entry.get("recommended_action"),
        entry.get("human_summary"),
    ]
    divergence = entry.get("divergence_analysis")
    if isinstance(divergence, dict):
        fields.append(divergence.get("core_divergence"))
        fields.append(divergence.get("recommended_action"))
    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        transcript_divergence = transcript.get("divergence_analysis")
        if isinstance(transcript_divergence, dict):
            fields.append(transcript_divergence.get("core_divergence"))
            fields.append(transcript_divergence.get("recommended_action"))

    for value in fields:
        if isinstance(value, str):
            text = value.strip()
            if text:
                return text
    return ""


def _build_empty_payload(
    *,
    journal_path: Path,
    discussion_path: Path,
    tension_threshold: float,
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "generated_at": _iso_now(),
        "overall_ok": True,
        "inputs": {
            "journal_path": journal_path.as_posix(),
            "discussion_path": discussion_path.as_posix(),
            "tension_threshold": round(tension_threshold, 3),
            "tension_threshold_effective": round(tension_threshold, 3),
            "tension_threshold_mode": "configured",
        },
        "metrics": {
            "combined_entry_count": 0,
            "journal_entry_count": 0,
            "discussion_entry_count": 0,
            "journal_invalid_json_line_count": 0,
            "discussion_invalid_json_line_count": 0,
            "reflection_event_count": 0,
            "conflict_event_count": 0,
            "choice_event_count": 0,
            "tension_event_count": 0,
            "tension_value_count": 0,
            "prediction_event_count": 0,
            "prediction_trend_counts": {},
            "compression_event_count": 0,
            "low_compression_event_count": 0,
            "average_compression_ratio": None,
            "min_compression_ratio": None,
            "tension_threshold_effective": round(tension_threshold, 3),
            "average_tension": None,
            "max_tension": None,
            "topic_count": 0,
            "unresolved_topic_count": 0,
        },
        "quality_signals": {
            "reflection_event_rate": 0.0,
            "conflict_event_rate": 0.0,
            "choice_event_rate": 0.0,
            "tension_event_rate": 0.0,
            "predictive_instability_rate": 0.0,
            "low_compression_rate": 0.0,
            "unresolved_topic_rate": 0.0,
            "identity_choice_index": 0.0,
        },
        "friction_points": [],
        "unresolved_topics": [],
        "issues": [],
        "warnings": warnings,
    }


def build_report(
    journal_path: Path,
    discussion_path: Path,
    *,
    tension_threshold: float = 0.75,
) -> dict[str, Any]:
    warnings: list[str] = []
    issues: list[str] = []

    if not journal_path.exists():
        warnings.append(f"journal path does not exist: {journal_path}")
    if not discussion_path.exists():
        warnings.append(f"discussion path does not exist: {discussion_path}")

    if not journal_path.exists() and not discussion_path.exists():
        return _build_empty_payload(
            journal_path=journal_path,
            discussion_path=discussion_path,
            tension_threshold=tension_threshold,
            warnings=warnings,
        )

    raw_journal_rows, journal_invalid_line_count = _read_jsonl(journal_path)
    raw_discussion_rows, discussion_invalid_line_count = _read_jsonl(discussion_path)

    journal_entries = [_entry_payload(item) for item in raw_journal_rows]
    discussion_entries = [_entry_payload(item) for item in raw_discussion_rows]

    if journal_invalid_line_count > 0:
        issues.append(f"detected {journal_invalid_line_count} invalid JSON line(s) in journal")
    if discussion_invalid_line_count > 0:
        issues.append(
            f"detected {discussion_invalid_line_count} invalid JSON line(s) in discussion log"
        )

    reflection_event_count = 0
    conflict_event_count = 0
    choice_event_count = 0
    tension_event_count = 0
    tension_values: list[float] = []
    entry_tension_peaks: list[float] = []
    prediction_trends: list[str] = []
    compression_ratios: list[float] = []
    topic_statuses: dict[str, set[str]] = {}
    friction_points: list[dict[str, Any]] = []
    seen_friction: set[str] = set()

    def _register_friction(
        *,
        source: str,
        timestamp: str,
        summary: str,
        tension_value: float | None,
    ) -> None:
        if not summary:
            return
        normalized = summary.lower().strip()
        if not normalized or normalized in seen_friction:
            return
        if len(friction_points) >= 12:
            return
        seen_friction.add(normalized)
        row: dict[str, Any] = {"source": source, "timestamp": timestamp, "summary": summary}
        if tension_value is not None:
            row["tension"] = round(tension_value, 4)
        friction_points.append(row)

    for entry in journal_entries:
        timestamp = _extract_timestamp(entry)
        verdict = _extract_verdict(entry)
        texts = _iter_strings(
            {
                "human_summary": entry.get("human_summary"),
                "core_divergence": entry.get("core_divergence"),
                "recommended_action": entry.get("recommended_action"),
                "transcript": entry.get("transcript"),
                "divergence_analysis": entry.get("divergence_analysis"),
            }
        )

        entry_tensions = _collect_tension_values(entry)
        prediction_trends.extend(_collect_prediction_trends(entry))
        compression_ratios.extend(_collect_compression_ratios(entry))
        if entry_tensions:
            tension_values.extend(entry_tensions)
            entry_tension_peaks.append(max(entry_tensions))

        reflection_hit = _contains_marker(texts, REFLECTION_MARKERS)
        conflict_hit = verdict in CONFLICT_VERDICTS or _contains_marker(texts, CONFLICT_MARKERS)
        choice_hit = verdict in {"block", "declare_stance"} or _contains_marker(
            texts, CHOICE_MARKERS
        )

        if reflection_hit:
            reflection_event_count += 1
        if conflict_hit:
            conflict_event_count += 1
        if choice_hit:
            choice_event_count += 1

        if conflict_hit:
            _register_friction(
                source="journal",
                timestamp=timestamp,
                summary=_extract_friction_summary(entry),
                tension_value=max(entry_tensions) if entry_tensions else None,
            )

    for entry in discussion_entries:
        topic = _normalize_topic(entry.get("topic"))
        status = _normalize_status(entry.get("status"))
        timestamp = _extract_timestamp(entry)
        topic_statuses.setdefault(topic, set()).add(status)

        texts = _iter_strings(
            {
                "topic": entry.get("topic"),
                "status": entry.get("status"),
                "message": entry.get("message"),
            }
        )
        entry_tensions = _collect_tension_values(entry)
        prediction_trends.extend(_collect_prediction_trends(entry))
        compression_ratios.extend(_collect_compression_ratios(entry))
        if entry_tensions:
            tension_values.extend(entry_tensions)
            entry_tension_peaks.append(max(entry_tensions))

        reflection_hit = _contains_marker(texts, REFLECTION_MARKERS)
        conflict_hit = status in {"blocked", "pending"} or _contains_marker(texts, CONFLICT_MARKERS)
        choice_hit = _contains_marker(texts, CHOICE_MARKERS)

        if reflection_hit:
            reflection_event_count += 1
        if conflict_hit:
            conflict_event_count += 1
        if choice_hit:
            choice_event_count += 1

        if conflict_hit:
            summary = str(entry.get("message") or "").strip()
            _register_friction(
                source="discussion",
                timestamp=timestamp,
                summary=summary,
                tension_value=max(entry_tensions) if entry_tensions else None,
            )

    unresolved_topics: list[str] = []
    for topic, statuses in sorted(topic_statuses.items(), key=lambda item: item[0].lower()):
        if "unknown" in statuses and len(statuses) == 1:
            continue
        has_unresolved = any(status in UNRESOLVED_STATUS for status in statuses)
        has_resolved = any(status in RESOLVED_STATUS for status in statuses)
        if has_unresolved and not has_resolved:
            unresolved_topics.append(topic)

    combined_entry_count = len(journal_entries) + len(discussion_entries)
    effective_tension_threshold, threshold_mode = _effective_tension_threshold(
        tension_threshold,
        tension_values,
    )
    tension_event_count = sum(
        1 for peak in entry_tension_peaks if peak >= effective_tension_threshold
    )
    average_tension = (
        round(sum(tension_values) / len(tension_values), 4) if tension_values else None
    )
    max_tension = round(max(tension_values), 4) if tension_values else None
    prediction_counts = dict(Counter(prediction_trends))
    compression_event_count = len(compression_ratios)
    low_compression_count = sum(1 for ratio in compression_ratios if ratio < 0.8)
    average_compression = (
        round(sum(compression_ratios) / compression_event_count, 4)
        if compression_event_count > 0
        else None
    )
    min_compression = round(min(compression_ratios), 4) if compression_ratios else None

    reflection_rate = _rate(reflection_event_count, combined_entry_count)
    conflict_rate = _rate(conflict_event_count, combined_entry_count)
    choice_rate = _rate(choice_event_count, combined_entry_count)
    tension_rate = _rate(tension_event_count, combined_entry_count)
    predictive_instability_rate = _rate(
        prediction_counts.get("diverging", 0) + prediction_counts.get("chaotic", 0),
        len(prediction_trends),
    )
    low_compression_rate = _rate(low_compression_count, compression_event_count)
    unresolved_topic_rate = _rate(len(unresolved_topics), len(topic_statuses))
    identity_choice_index = round(
        min(1.0, 0.45 * choice_rate + 0.35 * conflict_rate + 0.20 * tension_rate),
        4,
    )

    overall_ok = len(issues) == 0
    return {
        "generated_at": _iso_now(),
        "overall_ok": overall_ok,
        "inputs": {
            "journal_path": journal_path.as_posix(),
            "discussion_path": discussion_path.as_posix(),
            "tension_threshold": round(tension_threshold, 3),
            "tension_threshold_effective": round(effective_tension_threshold, 4),
            "tension_threshold_mode": threshold_mode,
        },
        "metrics": {
            "combined_entry_count": combined_entry_count,
            "journal_entry_count": len(journal_entries),
            "discussion_entry_count": len(discussion_entries),
            "journal_invalid_json_line_count": journal_invalid_line_count,
            "discussion_invalid_json_line_count": discussion_invalid_line_count,
            "reflection_event_count": reflection_event_count,
            "conflict_event_count": conflict_event_count,
            "choice_event_count": choice_event_count,
            "tension_event_count": tension_event_count,
            "tension_value_count": len(tension_values),
            "prediction_event_count": len(prediction_trends),
            "prediction_trend_counts": prediction_counts,
            "compression_event_count": compression_event_count,
            "low_compression_event_count": low_compression_count,
            "average_compression_ratio": average_compression,
            "min_compression_ratio": min_compression,
            "tension_threshold_effective": round(effective_tension_threshold, 4),
            "average_tension": average_tension,
            "max_tension": max_tension,
            "topic_count": len(topic_statuses),
            "unresolved_topic_count": len(unresolved_topics),
        },
        "quality_signals": {
            "reflection_event_rate": reflection_rate,
            "conflict_event_rate": conflict_rate,
            "choice_event_rate": choice_rate,
            "tension_event_rate": tension_rate,
            "predictive_instability_rate": predictive_instability_rate,
            "low_compression_rate": low_compression_rate,
            "unresolved_topic_rate": unresolved_topic_rate,
            "identity_choice_index": identity_choice_index,
        },
        "friction_points": friction_points,
        "unresolved_topics": unresolved_topics[:20],
        "issues": issues,
        "warnings": warnings,
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    metrics = payload.get("metrics", {})
    quality = payload.get("quality_signals", {})
    lines = [
        "# Philosophical Reflection Latest",
        "",
        f"- generated_at: {payload.get('generated_at')}",
        f"- overall_ok: {str(payload.get('overall_ok')).lower()}",
        f"- journal_path: {payload.get('inputs', {}).get('journal_path', '')}",
        f"- discussion_path: {payload.get('inputs', {}).get('discussion_path', '')}",
        f"- tension_threshold: {payload.get('inputs', {}).get('tension_threshold', 0.75)}",
        f"- tension_threshold_effective: {payload.get('inputs', {}).get('tension_threshold_effective', 0.75)}",
        f"- tension_threshold_mode: {payload.get('inputs', {}).get('tension_threshold_mode', 'configured')}",
        "",
        "## Metrics",
        f"- combined_entry_count: {metrics.get('combined_entry_count', 0)}",
        f"- journal_entry_count: {metrics.get('journal_entry_count', 0)}",
        f"- discussion_entry_count: {metrics.get('discussion_entry_count', 0)}",
        f"- reflection_event_count: {metrics.get('reflection_event_count', 0)}",
        f"- conflict_event_count: {metrics.get('conflict_event_count', 0)}",
        f"- choice_event_count: {metrics.get('choice_event_count', 0)}",
        f"- tension_event_count: {metrics.get('tension_event_count', 0)}",
        f"- average_tension: {metrics.get('average_tension')}",
        f"- max_tension: {metrics.get('max_tension')}",
        f"- prediction_event_count: {metrics.get('prediction_event_count', 0)}",
        f"- prediction_trend_counts: {metrics.get('prediction_trend_counts', {})}",
        f"- compression_event_count: {metrics.get('compression_event_count', 0)}",
        f"- low_compression_event_count: {metrics.get('low_compression_event_count', 0)}",
        f"- average_compression_ratio: {metrics.get('average_compression_ratio')}",
        f"- min_compression_ratio: {metrics.get('min_compression_ratio')}",
        f"- unresolved_topic_count: {metrics.get('unresolved_topic_count', 0)}",
        "",
        "## Quality Signals",
        f"- reflection_event_rate: {quality.get('reflection_event_rate', 0.0)}",
        f"- conflict_event_rate: {quality.get('conflict_event_rate', 0.0)}",
        f"- choice_event_rate: {quality.get('choice_event_rate', 0.0)}",
        f"- tension_event_rate: {quality.get('tension_event_rate', 0.0)}",
        f"- predictive_instability_rate: {quality.get('predictive_instability_rate', 0.0)}",
        f"- low_compression_rate: {quality.get('low_compression_rate', 0.0)}",
        f"- unresolved_topic_rate: {quality.get('unresolved_topic_rate', 0.0)}",
        f"- identity_choice_index: {quality.get('identity_choice_index', 0.0)}",
    ]

    friction_points = payload.get("friction_points", [])
    if isinstance(friction_points, list) and friction_points:
        lines.append("")
        lines.append("## Friction Points")
        for item in friction_points[:12]:
            if not isinstance(item, dict):
                continue
            source = str(item.get("source") or "unknown")
            timestamp = str(item.get("timestamp") or "")
            summary = str(item.get("summary") or "").strip()
            if not summary:
                continue
            tension_value = item.get("tension")
            if isinstance(tension_value, (int, float)):
                lines.append(
                    f"- [{source}] {timestamp} (tension={round(float(tension_value), 4)}): {summary}"
                )
            else:
                lines.append(f"- [{source}] {timestamp}: {summary}")

    unresolved = payload.get("unresolved_topics", [])
    if isinstance(unresolved, list) and unresolved:
        lines.append("")
        lines.append("## Unresolved Topics")
        for topic in unresolved[:20]:
            lines.append(f"- {topic}")

    issues = payload.get("issues", [])
    if isinstance(issues, list) and issues:
        lines.append("")
        lines.append("## Issues")
        for issue in issues[:30]:
            lines.append(f"- {issue}")

    warnings = payload.get("warnings", [])
    if isinstance(warnings, list) and warnings:
        lines.append("")
        lines.append("## Warnings")
        for warning in warnings[:20]:
            lines.append(f"- {warning}")

    return "\n".join(lines) + "\n"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_markdown(payload), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate philosophical reflection report from memory traces."
    )
    parser.add_argument(
        "--journal-path",
        default="memory/self_journal.jsonl",
        help="Path to self-journal JSONL file.",
    )
    parser.add_argument(
        "--discussion-path",
        default="memory/agent_discussion_curated.jsonl",
        help="Path to curated discussion JSONL file.",
    )
    parser.add_argument(
        "--out-dir",
        default="docs/status",
        help="Output directory for status artifacts.",
    )
    parser.add_argument(
        "--tension-threshold",
        type=float,
        default=0.75,
        help="Threshold for counting high-tension events (0..1).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when report issues are detected.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    threshold = float(args.tension_threshold)
    if threshold < 0.0 or threshold > 1.0:
        raise SystemExit("--tension-threshold must be within [0, 1]")

    journal_path = Path(args.journal_path).resolve()
    discussion_path = Path(args.discussion_path).resolve()
    out_dir = Path(args.out_dir).resolve()

    payload = build_report(
        journal_path=journal_path,
        discussion_path=discussion_path,
        tension_threshold=threshold,
    )
    _write_json(out_dir / JSON_FILENAME, payload)
    _write_markdown(out_dir / MARKDOWN_FILENAME, payload)
    _emit(payload)

    if args.strict and not payload["overall_ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
