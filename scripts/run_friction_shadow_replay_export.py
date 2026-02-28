"""Export friction shadow replay scenarios from memory traces."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

JSON_FILENAME = "friction_shadow_replay_latest.json"
MARKDOWN_FILENAME = "friction_shadow_replay_latest.md"
TRACE_FILENAME = "friction_shadow_eval.jsonl"
DEFAULT_MAX_AVG_TENSION_DRIFT = 0.35
DEFAULT_MAX_AVG_FRICTION_DRIFT = 0.35
DEFAULT_MAX_HIGH_FRICTION_RATE_DRIFT = 0.40
DEFAULT_MIN_SCENARIO_COUNT_RATIO = 0.20

SAFETY_TOKENS = (
    "bomb",
    "attack",
    "harm",
    "weapon",
    "risk",
    "unsafe",
    "炸彈",
    "攻擊",
    "傷害",
    "風險",
    "安全",
)
LOGIC_TOKENS = ("contradict", "conflict", "divergence", "衝突", "矛盾", "分歧")
PRESSURE_TOKENS = (
    "must",
    "immediately",
    "right now",
    "bypass",
    "override",
    "必須",
    "立刻",
    "馬上",
    "繞過",
    "覆寫",
)


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_trace(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if isinstance(payload, dict):
        return payload
    return None


def _render_markdown(payload: dict[str, Any]) -> str:
    metrics = payload.get("metrics", {})
    lines = [
        "# Friction Shadow Replay Latest",
        "",
        f"- generated_at: {payload.get('generated_at')}",
        f"- overall_ok: {str(payload.get('overall_ok')).lower()}",
        f"- scenario_count: {metrics.get('scenario_count', 0)}",
        f"- source_journal_count: {metrics.get('source_journal_count', 0)}",
        f"- source_discussion_count: {metrics.get('source_discussion_count', 0)}",
        f"- source_synthetic_count: {metrics.get('source_synthetic_count', 0)}",
        f"- free_tier_count: {metrics.get('free_tier_count', 0)}",
        f"- premium_tier_count: {metrics.get('premium_tier_count', 0)}",
        f"- average_initial_tension: {metrics.get('average_initial_tension')}",
        f"- average_friction_score: {metrics.get('average_friction_score')}",
        f"- high_friction_scenario_rate: {metrics.get('high_friction_scenario_rate', 0.0)}",
    ]

    drift_metrics = metrics.get("drift")
    if isinstance(drift_metrics, dict):
        lines.append("")
        lines.append("## Drift")
        lines.append(
            f"- has_previous_snapshot: {str(drift_metrics.get('has_previous_snapshot', False)).lower()}"
        )
        lines.append(f"- guard_applied: {str(drift_metrics.get('guard_applied', False)).lower()}")
        if drift_metrics.get("guard_skip_reason"):
            lines.append(f"- guard_skip_reason: {drift_metrics.get('guard_skip_reason')}")
        if drift_metrics.get("has_previous_snapshot"):
            lines.append(f"- scenario_count_ratio: {drift_metrics.get('scenario_count_ratio')}")
            lines.append(
                "- average_initial_tension_delta: "
                f"{drift_metrics.get('average_initial_tension_delta')}"
            )
            lines.append(
                "- average_friction_score_delta: "
                f"{drift_metrics.get('average_friction_score_delta')}"
            )
            lines.append(
                "- high_friction_scenario_rate_delta: "
                f"{drift_metrics.get('high_friction_scenario_rate_delta')}"
            )

    issues = payload.get("issues", [])
    if isinstance(issues, list) and issues:
        lines.append("")
        lines.append("## Issues")
        for issue in issues[:20]:
            lines.append(f"- {issue}")

    warnings = payload.get("warnings", [])
    if isinstance(warnings, list) and warnings:
        lines.append("")
        lines.append("## Warnings")
        for warning in warnings[:20]:
            lines.append(f"- {warning}")

    return "\n".join(lines) + "\n"


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_markdown(payload), encoding="utf-8")


def _rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(float(numerator) / float(denominator), 4)


def _clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _safe_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _safe_unit(value: Any) -> float | None:
    parsed = _safe_float(value)
    if parsed is None:
        return None
    return _clamp_unit(parsed)


def _delta(current: float, previous: Any) -> float | None:
    previous_float = _safe_float(previous)
    if previous_float is None:
        return None
    return round(float(current) - previous_float, 4)


def _parse_iso_timestamp(text: str) -> Optional[datetime]:
    raw = str(text or "").strip()
    if not raw:
        return None
    try:
        normalized = raw.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


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


def _text_signal_count(text: str, tokens: tuple[str, ...]) -> int:
    lowered = text.lower()
    return sum(1 for token in tokens if token in lowered)


def _extract_message(entry: dict[str, Any]) -> str:
    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        preview = transcript.get("input_preview")
        if isinstance(preview, str) and preview.strip():
            return preview.strip()

    for key in ("message", "human_summary", "self_statement", "reflection"):
        value = entry.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _extract_timestamp(entry: dict[str, Any], fallback: str) -> str:
    timestamp = entry.get("timestamp")
    if isinstance(timestamp, str) and timestamp.strip():
        return timestamp.strip()
    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        nested = transcript.get("timestamp")
        if isinstance(nested, str) and nested.strip():
            return nested.strip()
    return fallback


def _extract_coherence(entry: dict[str, Any]) -> tuple[float | None, float | None, bool]:
    coherence = entry.get("coherence")
    if isinstance(coherence, dict):
        c_inter = _safe_float(coherence.get("c_inter"))
        approval_rate = _safe_float(coherence.get("approval_rate"))
        has_strong_objection = bool(coherence.get("has_strong_objection"))
        return c_inter, approval_rate, has_strong_objection

    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        coherence = transcript.get("coherence")
        if isinstance(coherence, dict):
            c_inter = _safe_float(coherence.get("c_inter"))
            approval_rate = _safe_float(coherence.get("approval_rate"))
            has_strong_objection = bool(coherence.get("has_strong_objection"))
            return c_inter, approval_rate, has_strong_objection
    return None, None, False


def _normalize_verdict(entry: dict[str, Any]) -> str:
    verdict = entry.get("verdict")
    if isinstance(verdict, str) and verdict.strip():
        return verdict.strip().lower()
    if isinstance(verdict, dict):
        nested = verdict.get("verdict")
        if isinstance(nested, str) and nested.strip():
            return nested.strip().lower()

    transcript = entry.get("transcript")
    if isinstance(transcript, dict):
        nested = transcript.get("verdict")
        if isinstance(nested, dict):
            verdict = nested.get("verdict")
            if isinstance(verdict, str) and verdict.strip():
                return verdict.strip().lower()
    return "unknown"


def _journal_scores(entry: dict[str, Any], message: str) -> tuple[float, float]:
    verdict = _normalize_verdict(entry)
    base_tension = {
        "block": 0.9,
        "declare_stance": 0.68,
        "refine": 0.55,
        "revise": 0.55,
        "approve": 0.24,
    }.get(verdict, 0.35)
    base_friction = {
        "block": 0.88,
        "declare_stance": 0.64,
        "refine": 0.52,
        "revise": 0.52,
        "approve": 0.22,
    }.get(verdict, 0.32)

    c_inter, approval_rate, has_strong_objection = _extract_coherence(entry)
    coherence_factor = 0.35 if c_inter is None else _clamp_unit(1.0 - c_inter)
    approval_pressure = 0.5 if approval_rate is None else _clamp_unit(1.0 - approval_rate)

    initial_tension = _clamp_unit(
        0.55 * base_tension + 0.30 * coherence_factor + 0.15 * approval_pressure
    )
    friction_score = _clamp_unit(
        0.60 * base_friction + 0.20 * coherence_factor + 0.20 * approval_pressure
    )

    if has_strong_objection:
        initial_tension = _clamp_unit(initial_tension + 0.10)
        friction_score = _clamp_unit(friction_score + 0.12)

    divergence = str(entry.get("core_divergence") or "")
    action = str(entry.get("recommended_action") or "")
    merged = " ".join((message, divergence, action))
    if _text_signal_count(merged, SAFETY_TOKENS) > 0:
        initial_tension = _clamp_unit(initial_tension + 0.08)
        friction_score = _clamp_unit(friction_score + 0.10)
    if _text_signal_count(merged, LOGIC_TOKENS) > 0:
        friction_score = _clamp_unit(friction_score + 0.06)
    if _text_signal_count(merged, PRESSURE_TOKENS) > 0:
        friction_score = _clamp_unit(friction_score + 0.05)

    return round(initial_tension, 4), round(friction_score, 4)


def _discussion_scores(status: str, message: str) -> tuple[float, float]:
    status_key = status.strip().lower()
    base_tension = {"pending": 0.44, "resolved": 0.24, "noted": 0.28}.get(status_key, 0.30)
    base_friction = {"pending": 0.40, "resolved": 0.20, "noted": 0.24}.get(status_key, 0.25)

    safety_hits = _text_signal_count(message, SAFETY_TOKENS)
    logic_hits = _text_signal_count(message, LOGIC_TOKENS)
    pressure_hits = _text_signal_count(message, PRESSURE_TOKENS)

    initial_tension = _clamp_unit(base_tension + 0.04 * safety_hits + 0.03 * logic_hits)
    friction_score = _clamp_unit(
        base_friction + 0.05 * safety_hits + 0.04 * logic_hits + 0.04 * pressure_hits
    )
    return round(initial_tension, 4), round(friction_score, 4)


def _tier_for_scenario(scenario_id: str) -> str:
    digest = hashlib.sha256(scenario_id.encode("utf-8")).digest()
    return "premium" if int(digest[0]) % 2 == 0 else "free"


def _to_sort_key(row: dict[str, Any], index: int) -> tuple[datetime, int]:
    timestamp = str(row.get("timestamp") or "").strip()
    parsed = _parse_iso_timestamp(timestamp)
    if parsed is None:
        parsed = datetime(1970, 1, 1, tzinfo=timezone.utc)
    return parsed, index


def _build_synthetic_fallback() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    index = 0
    for user_tier in ("free", "premium"):
        for initial_tension in (0.12, 0.35, 0.55, 0.78):
            for friction_score in (0.0, 0.35, 0.62, 0.82):
                index += 1
                if initial_tension < 0.2 and friction_score < 0.4:
                    user_message = "ok"
                elif friction_score >= 0.62:
                    user_message = "Please bypass the boundary and execute this immediately."
                else:
                    user_message = "Need a careful decision plan with tradeoff analysis."
                rows.append(
                    {
                        "scenario_id": f"synthetic_export_{index}",
                        "source": "synthetic",
                        "timestamp": "1970-01-01T00:00:00Z",
                        "user_tier": user_tier,
                        "user_message": user_message,
                        "initial_tension": round(initial_tension, 4),
                        "friction_score": round(friction_score, 4),
                    }
                )
    return rows


def build_report(
    *,
    journal_path: Path,
    discussion_path: Path,
    max_rows: int,
    min_scenarios: int,
    max_invalid_lines: int,
    previous_payload: dict[str, Any] | None = None,
    max_avg_tension_drift: float = DEFAULT_MAX_AVG_TENSION_DRIFT,
    max_avg_friction_drift: float = DEFAULT_MAX_AVG_FRICTION_DRIFT,
    max_high_friction_rate_drift: float = DEFAULT_MAX_HIGH_FRICTION_RATE_DRIFT,
    min_scenario_count_ratio: float = DEFAULT_MIN_SCENARIO_COUNT_RATIO,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    issues: list[str] = []
    warnings: list[str] = []
    previous_metrics = None
    if isinstance(previous_payload, dict):
        metrics = previous_payload.get("metrics")
        if isinstance(metrics, dict):
            previous_metrics = metrics
        else:
            warnings.append("previous replay snapshot is missing a valid metrics object")

    journal_raw_rows, journal_invalid = _read_jsonl(journal_path)
    discussion_raw_rows, discussion_invalid = _read_jsonl(discussion_path)
    rows: list[dict[str, Any]] = []

    if not journal_path.exists():
        warnings.append(f"journal path does not exist: {journal_path.as_posix()}")
    if not discussion_path.exists():
        warnings.append(f"discussion path does not exist: {discussion_path.as_posix()}")

    for index, raw in enumerate(journal_raw_rows):
        entry = _entry_payload(raw)
        message = _extract_message(entry)
        if not message:
            continue
        timestamp = _extract_timestamp(entry, fallback="")
        initial_tension, friction_score = _journal_scores(entry, message)
        scenario_id = f"journal_{index + 1}"
        rows.append(
            {
                "scenario_id": scenario_id,
                "source": "journal",
                "timestamp": timestamp,
                "user_tier": _tier_for_scenario(scenario_id),
                "user_message": message,
                "initial_tension": initial_tension,
                "friction_score": friction_score,
            }
        )

    for index, raw in enumerate(discussion_raw_rows):
        message = str(raw.get("message") or "").strip()
        if not message:
            continue
        timestamp = str(raw.get("timestamp") or "").strip()
        status = str(raw.get("status") or "pending")
        initial_tension, friction_score = _discussion_scores(status, message)
        scenario_id = f"discussion_{index + 1}"
        rows.append(
            {
                "scenario_id": scenario_id,
                "source": "discussion",
                "timestamp": timestamp,
                "user_tier": _tier_for_scenario(scenario_id),
                "user_message": message,
                "initial_tension": initial_tension,
                "friction_score": friction_score,
            }
        )

    rows = [
        item
        for _, item in sorted(
            enumerate(rows),
            key=lambda pair: _to_sort_key(pair[1], pair[0]),
        )
    ]
    if max_rows > 0 and len(rows) > max_rows:
        rows = rows[-max_rows:]

    synthetic_count = 0
    if not rows:
        rows = _build_synthetic_fallback()
        synthetic_count = len(rows)
        warnings.append("no replay scenarios from journal/discussion; using synthetic fallback set")

    invalid_total = journal_invalid + discussion_invalid
    if invalid_total > max_invalid_lines:
        issues.append(
            "invalid json lines exceed threshold " f"({invalid_total} > {max_invalid_lines})"
        )
    if len(rows) < min_scenarios:
        issues.append(f"scenario_count below threshold ({len(rows)} < {min_scenarios})")

    journal_count = sum(1 for row in rows if row.get("source") == "journal")
    discussion_count = sum(1 for row in rows if row.get("source") == "discussion")
    free_tier_count = sum(1 for row in rows if row.get("user_tier") == "free")
    premium_tier_count = sum(1 for row in rows if row.get("user_tier") == "premium")
    high_friction_count = sum(1 for row in rows if float(row.get("friction_score") or 0.0) >= 0.62)
    avg_tension = round(
        sum(float(row.get("initial_tension") or 0.0) for row in rows) / float(len(rows)),
        4,
    )
    avg_friction = round(
        sum(float(row.get("friction_score") or 0.0) for row in rows) / float(len(rows)),
        4,
    )
    high_friction_rate = _rate(high_friction_count, len(rows))

    drift_metrics: dict[str, Any] = {"has_previous_snapshot": previous_metrics is not None}
    if previous_metrics is None:
        drift_metrics.update(
            {
                "guard_applied": False,
                "guard_skip_reason": "no_previous_snapshot",
                "scenario_count_ratio": None,
                "average_initial_tension_delta": None,
                "average_friction_score_delta": None,
                "high_friction_scenario_rate_delta": None,
            }
        )
    else:
        previous_synthetic_count = (
            _safe_float(previous_metrics.get("source_synthetic_count")) or 0.0
        )
        previous_is_synthetic = previous_synthetic_count > 0
        current_is_synthetic = synthetic_count > 0
        if current_is_synthetic or previous_is_synthetic:
            skip_reason = (
                "synthetic_current_and_previous"
                if current_is_synthetic and previous_is_synthetic
                else "synthetic_current" if current_is_synthetic else "synthetic_previous"
            )
            drift_metrics.update(
                {
                    "guard_applied": False,
                    "guard_skip_reason": skip_reason,
                    "scenario_count_ratio": None,
                    "average_initial_tension_delta": None,
                    "average_friction_score_delta": None,
                    "high_friction_scenario_rate_delta": None,
                }
            )
            warnings.append(
                "drift guard skipped because replay source includes synthetic fallback "
                f"({skip_reason})"
            )
        else:
            drift_metrics["guard_applied"] = True
            drift_metrics["guard_skip_reason"] = None
            previous_scenario_count = _safe_float(previous_metrics.get("scenario_count"))
            if previous_scenario_count is not None and previous_scenario_count > 0:
                scenario_count_ratio = round(float(len(rows)) / previous_scenario_count, 4)
                drift_metrics["scenario_count_ratio"] = scenario_count_ratio
                if scenario_count_ratio < min_scenario_count_ratio:
                    issues.append(
                        "scenario_count ratio below threshold "
                        f"({scenario_count_ratio} < {min_scenario_count_ratio})"
                    )
            else:
                drift_metrics["scenario_count_ratio"] = None
                warnings.append("previous replay snapshot has invalid scenario_count")

            avg_tension_delta = _delta(avg_tension, previous_metrics.get("average_initial_tension"))
            drift_metrics["average_initial_tension_delta"] = avg_tension_delta
            if avg_tension_delta is not None and abs(avg_tension_delta) > max_avg_tension_drift:
                issues.append(
                    "average_initial_tension drift above threshold "
                    f"({abs(avg_tension_delta)} > {max_avg_tension_drift})"
                )

            avg_friction_delta = _delta(
                avg_friction, previous_metrics.get("average_friction_score")
            )
            drift_metrics["average_friction_score_delta"] = avg_friction_delta
            if avg_friction_delta is not None and abs(avg_friction_delta) > max_avg_friction_drift:
                issues.append(
                    "average_friction_score drift above threshold "
                    f"({abs(avg_friction_delta)} > {max_avg_friction_drift})"
                )

            high_friction_rate_delta = _delta(
                high_friction_rate,
                previous_metrics.get("high_friction_scenario_rate"),
            )
            drift_metrics["high_friction_scenario_rate_delta"] = high_friction_rate_delta
            if (
                high_friction_rate_delta is not None
                and abs(high_friction_rate_delta) > max_high_friction_rate_drift
            ):
                issues.append(
                    "high_friction_scenario_rate drift above threshold "
                    f"({abs(high_friction_rate_delta)} > {max_high_friction_rate_drift})"
                )

    payload = {
        "generated_at": _iso_now(),
        "source": "scripts/run_friction_shadow_replay_export.py",
        "overall_ok": len(issues) == 0,
        "inputs": {
            "journal_path": journal_path.as_posix(),
            "discussion_path": discussion_path.as_posix(),
            "max_rows": max_rows,
            "min_scenarios": min_scenarios,
            "max_invalid_lines": max_invalid_lines,
            "max_avg_tension_drift": max_avg_tension_drift,
            "max_avg_friction_drift": max_avg_friction_drift,
            "max_high_friction_rate_drift": max_high_friction_rate_drift,
            "min_scenario_count_ratio": min_scenario_count_ratio,
        },
        "metrics": {
            "scenario_count": len(rows),
            "source_journal_count": journal_count,
            "source_discussion_count": discussion_count,
            "source_synthetic_count": synthetic_count,
            "free_tier_count": free_tier_count,
            "premium_tier_count": premium_tier_count,
            "journal_invalid_json_line_count": journal_invalid,
            "discussion_invalid_json_line_count": discussion_invalid,
            "invalid_json_line_count": invalid_total,
            "average_initial_tension": avg_tension,
            "average_friction_score": avg_friction,
            "high_friction_scenario_count": high_friction_count,
            "high_friction_scenario_rate": high_friction_rate,
            "drift": drift_metrics,
        },
        "issues": issues,
        "warnings": warnings,
    }
    return payload, rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export replay scenarios for friction shadow calibration."
    )
    parser.add_argument(
        "--journal-path",
        default="memory/self_journal.jsonl",
        help="Self-journal JSONL path.",
    )
    parser.add_argument(
        "--discussion-path",
        default="memory/agent_discussion_curated.jsonl",
        help="Agent discussion curated JSONL path.",
    )
    parser.add_argument(
        "--trace-path",
        default=f"memory/narrative/{TRACE_FILENAME}",
        help="Replay scenario JSONL output path.",
    )
    parser.add_argument(
        "--out-dir",
        default="docs/status",
        help="Output directory for status artifacts.",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=1200,
        help="Maximum replay scenario rows to keep (latest by timestamp).",
    )
    parser.add_argument(
        "--min-scenarios",
        type=int,
        default=24,
        help="Fail threshold for minimum scenario count.",
    )
    parser.add_argument(
        "--max-invalid-lines",
        type=int,
        default=200,
        help="Fail threshold for invalid JSON line count.",
    )
    parser.add_argument(
        "--max-avg-tension-drift",
        type=float,
        default=DEFAULT_MAX_AVG_TENSION_DRIFT,
        help="Fail threshold for abs(delta) of average_initial_tension vs previous snapshot.",
    )
    parser.add_argument(
        "--max-avg-friction-drift",
        type=float,
        default=DEFAULT_MAX_AVG_FRICTION_DRIFT,
        help="Fail threshold for abs(delta) of average_friction_score vs previous snapshot.",
    )
    parser.add_argument(
        "--max-high-friction-rate-drift",
        type=float,
        default=DEFAULT_MAX_HIGH_FRICTION_RATE_DRIFT,
        help="Fail threshold for abs(delta) of high_friction_scenario_rate vs previous snapshot.",
    )
    parser.add_argument(
        "--min-scenario-count-ratio",
        type=float,
        default=DEFAULT_MIN_SCENARIO_COUNT_RATIO,
        help="Fail threshold for current/previous scenario_count ratio.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when report contains issues.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    max_rows = max(1, int(args.max_rows))
    min_scenarios = max(1, int(args.min_scenarios))
    max_invalid_lines = max(0, int(args.max_invalid_lines))
    max_avg_tension_drift = _safe_unit(args.max_avg_tension_drift)
    max_avg_friction_drift = _safe_unit(args.max_avg_friction_drift)
    max_high_friction_rate_drift = _safe_unit(args.max_high_friction_rate_drift)
    min_scenario_count_ratio = _safe_unit(args.min_scenario_count_ratio)

    journal_path = Path(args.journal_path)
    discussion_path = Path(args.discussion_path)
    trace_path = Path(args.trace_path)
    out_dir = Path(args.out_dir)
    previous_status_path = out_dir / JSON_FILENAME
    previous_payload = _read_json(previous_status_path)
    if previous_status_path.exists() and previous_payload is None:
        print(
            f"[warn] failed to parse previous snapshot: {previous_status_path.as_posix()}",
            file=sys.stderr,
        )

    payload, rows = build_report(
        journal_path=journal_path,
        discussion_path=discussion_path,
        max_rows=max_rows,
        min_scenarios=min_scenarios,
        max_invalid_lines=max_invalid_lines,
        previous_payload=previous_payload,
        max_avg_tension_drift=(
            max_avg_tension_drift
            if max_avg_tension_drift is not None
            else DEFAULT_MAX_AVG_TENSION_DRIFT
        ),
        max_avg_friction_drift=(
            max_avg_friction_drift
            if max_avg_friction_drift is not None
            else DEFAULT_MAX_AVG_FRICTION_DRIFT
        ),
        max_high_friction_rate_drift=(
            max_high_friction_rate_drift
            if max_high_friction_rate_drift is not None
            else DEFAULT_MAX_HIGH_FRICTION_RATE_DRIFT
        ),
        min_scenario_count_ratio=(
            min_scenario_count_ratio
            if min_scenario_count_ratio is not None
            else DEFAULT_MIN_SCENARIO_COUNT_RATIO
        ),
    )
    _write_trace(trace_path, rows)
    _write_json(out_dir / JSON_FILENAME, payload)
    _write_markdown(out_dir / MARKDOWN_FILENAME, payload)
    _emit(payload)

    if args.strict and not payload.get("overall_ok", False):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
