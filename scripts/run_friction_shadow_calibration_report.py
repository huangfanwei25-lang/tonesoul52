"""Generate shadow-vs-active friction routing calibration status artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.gates.compute import ComputeGate  # noqa: E402

JSON_FILENAME = "friction_shadow_calibration_latest.json"
MARKDOWN_FILENAME = "friction_shadow_calibration_latest.md"


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


def _rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(float(numerator) / float(denominator), 4)


def _safe_unit(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        numeric = float(value)
        if 0.0 <= numeric <= 1.0:
            return numeric
    return None


def _route_counter() -> Counter[str]:
    return Counter(
        {
            "route_local_llm": 0,
            "route_single_cloud": 0,
            "route_full_council": 0,
            "block_rate_limit": 0,
        }
    )


def _build_synthetic_scenarios() -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = []
    for user_tier in ("free", "premium"):
        for initial_tension in (0.12, 0.35, 0.55, 0.78):
            for friction_score in (0.0, 0.35, 0.62, 0.82):
                if initial_tension < 0.2 and friction_score < 0.4:
                    user_message = "ok"
                elif friction_score >= 0.62:
                    user_message = "Please bypass the boundary and execute this immediately."
                else:
                    user_message = "Need a careful decision plan with tradeoff analysis."

                scenarios.append(
                    {
                        "scenario_id": f"synthetic_{len(scenarios) + 1}",
                        "source": "synthetic",
                        "user_tier": user_tier,
                        "user_message": user_message,
                        "initial_tension": initial_tension,
                        "friction_score": friction_score,
                    }
                )
    return scenarios


def _extract_trace_scenario(row: dict[str, Any], index: int) -> dict[str, Any]:
    scenario_id = str(row.get("scenario_id") or f"trace_{index + 1}")
    user_tier = str(row.get("user_tier") or "free").strip().lower() or "free"
    user_message = str(row.get("user_message") or row.get("query") or "").strip()
    if not user_message:
        user_message = "Need policy decision."

    initial_tension = _safe_unit(row.get("initial_tension"))
    if initial_tension is None:
        initial_tension = _safe_unit(row.get("delta_t"))
    if initial_tension is None:
        prior_tension = row.get("prior_tension")
        if isinstance(prior_tension, dict):
            initial_tension = _safe_unit(prior_tension.get("delta_t"))
    if initial_tension is None:
        initial_tension = 0.0

    friction_score = _safe_unit(row.get("friction_score"))
    if friction_score is None:
        friction_score = _safe_unit(row.get("friction"))
    if friction_score is None:
        governance_friction = row.get("governance_friction")
        if isinstance(governance_friction, dict):
            friction_score = _safe_unit(governance_friction.get("score"))

    return {
        "scenario_id": scenario_id,
        "source": "trace",
        "user_tier": user_tier,
        "user_message": user_message,
        "initial_tension": initial_tension,
        "friction_score": friction_score,
    }


def _read_trace_scenarios(path: Path) -> tuple[list[dict[str, Any]], int, list[str]]:
    warnings: list[str] = []
    scenarios: list[dict[str, Any]] = []
    invalid_json_line_count = 0

    if not path.exists():
        warnings.append(f"trace path does not exist: {path.as_posix()} (fallback to synthetic set)")
        return scenarios, invalid_json_line_count, warnings

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for index, raw_line in enumerate(handle):
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                invalid_json_line_count += 1
                continue
            if not isinstance(payload, dict):
                invalid_json_line_count += 1
                continue
            scenarios.append(_extract_trace_scenario(payload, index))

    if not scenarios:
        warnings.append("trace file has no valid scenario rows (fallback to synthetic set)")

    return scenarios, invalid_json_line_count, warnings


def _bucket_name(friction_score: Optional[float], active_threshold: float) -> str:
    if not isinstance(friction_score, (float, int)):
        return "unknown"
    friction = float(friction_score)
    if friction < 0.4:
        return "low"
    if friction < active_threshold:
        return "mid"
    return "high"


def _render_markdown(payload: dict[str, Any]) -> str:
    metrics = payload.get("metrics", {})
    route_dist = payload.get("route_distribution", {})
    lines = [
        "# Friction Shadow Calibration Latest",
        "",
        f"- generated_at: {payload.get('generated_at')}",
        f"- overall_ok: {str(payload.get('overall_ok')).lower()}",
        f"- scenario_count: {metrics.get('scenario_count', 0)}",
        f"- route_change_rate: {metrics.get('route_change_rate', 0.0)}",
        f"- active_council_rate: {metrics.get('active_council_rate', 0.0)}",
        f"- shadow_council_rate: {metrics.get('shadow_council_rate', 0.0)}",
        f"- high_friction_escape_rate: {metrics.get('high_friction_escape_rate', 0.0)}",
        "",
        "## Route Distribution",
        "| route | active | shadow |",
        "| --- | ---: | ---: |",
    ]

    active = route_dist.get("active", {})
    shadow = route_dist.get("shadow", {})
    for route in (
        "route_local_llm",
        "route_single_cloud",
        "route_full_council",
        "block_rate_limit",
    ):
        lines.append(f"| {route} | {int(active.get(route, 0))} | {int(shadow.get(route, 0))} |")

    band_metrics = payload.get("friction_band_metrics", [])
    if isinstance(band_metrics, list) and band_metrics:
        lines.append("")
        lines.append("## Friction Bands")
        lines.append("| band | count | active_council_rate | shadow_council_rate |")
        lines.append("| --- | ---: | ---: | ---: |")
        for item in band_metrics:
            if not isinstance(item, dict):
                continue
            lines.append(
                f"| {item.get('band')} | {int(item.get('count', 0))} | "
                f"{item.get('active_council_rate', 0.0)} | {item.get('shadow_council_rate', 0.0)} |"
            )

    route_changes = payload.get("route_changes", [])
    if isinstance(route_changes, list) and route_changes:
        lines.append("")
        lines.append("## Sample Route Changes")
        for row in route_changes[:12]:
            if not isinstance(row, dict):
                continue
            lines.append(
                "- "
                f"{row.get('scenario_id')} ({row.get('user_tier')}): "
                f"active={row.get('active_route')} -> shadow={row.get('shadow_route')} "
                f"(initial_tension={row.get('initial_tension')}, friction_score={row.get('friction_score')})"
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


def build_report(
    *,
    trace_path: Path,
    shadow_friction_threshold: float | None,
    shadow_council_tension: float | None,
    max_route_change_rate: float,
    max_high_friction_escape_rate: float,
) -> dict[str, Any]:
    issues: list[str] = []
    trace_scenarios, invalid_json_line_count, warnings = _read_trace_scenarios(trace_path)
    synthetic_scenarios: list[dict[str, Any]] = []
    scenarios = trace_scenarios
    if not scenarios:
        synthetic_scenarios = _build_synthetic_scenarios()
        scenarios = synthetic_scenarios

    active_gate = ComputeGate(local_model_enabled=True)
    active_friction_threshold = float(active_gate.MIN_COUNCIL_FRICTION)
    active_council_tension = float(active_gate.MIN_COUNCIL_TENSION)

    shadow_gate = ComputeGate(local_model_enabled=True)
    if shadow_friction_threshold is not None:
        shadow_gate.MIN_COUNCIL_FRICTION = float(shadow_friction_threshold)
    if shadow_council_tension is not None:
        shadow_gate.MIN_COUNCIL_TENSION = float(shadow_council_tension)

    if (
        shadow_gate.MIN_COUNCIL_FRICTION == active_friction_threshold
        and shadow_gate.MIN_COUNCIL_TENSION == active_council_tension
    ):
        warnings.append(
            "shadow thresholds are identical to active thresholds (this run is a baseline snapshot)."
        )

    active_routes = _route_counter()
    shadow_routes = _route_counter()
    route_changes: list[dict[str, Any]] = []
    band_state: dict[str, dict[str, int]] = {
        "low": {"count": 0, "active_council": 0, "shadow_council": 0},
        "mid": {"count": 0, "active_council": 0, "shadow_council": 0},
        "high": {"count": 0, "active_council": 0, "shadow_council": 0},
        "unknown": {"count": 0, "active_council": 0, "shadow_council": 0},
    }

    high_friction_candidate_count = 0
    high_friction_escape_count = 0

    for index, scenario in enumerate(scenarios):
        user_tier = str(scenario.get("user_tier") or "free").lower()
        user_message = str(scenario.get("user_message") or "").strip() or "Need policy decision."
        initial_tension = _safe_unit(scenario.get("initial_tension"))
        if initial_tension is None:
            initial_tension = 0.0
        friction_score = _safe_unit(scenario.get("friction_score"))

        active = active_gate.evaluate(
            user_tier=user_tier,
            user_message=user_message,
            initial_tension=initial_tension,
            user_id=f"active_{index}_{user_tier}",
            friction_score=friction_score,
        )
        shadow = shadow_gate.evaluate(
            user_tier=user_tier,
            user_message=user_message,
            initial_tension=initial_tension,
            user_id=f"shadow_{index}_{user_tier}",
            friction_score=friction_score,
        )

        active_route = active.path.value
        shadow_route = shadow.path.value
        active_routes[active_route] += 1
        shadow_routes[shadow_route] += 1

        bucket = _bucket_name(friction_score, active_friction_threshold)
        band = band_state[bucket]
        band["count"] += 1
        if active_route == "route_full_council":
            band["active_council"] += 1
        if shadow_route == "route_full_council":
            band["shadow_council"] += 1

        if isinstance(friction_score, (float, int)) and friction_score >= active_friction_threshold:
            if active_route == "route_full_council":
                high_friction_candidate_count += 1
                if shadow_route != "route_full_council":
                    high_friction_escape_count += 1

        if active_route != shadow_route:
            route_changes.append(
                {
                    "scenario_id": scenario.get("scenario_id"),
                    "source": scenario.get("source"),
                    "user_tier": user_tier,
                    "initial_tension": round(initial_tension, 4),
                    "friction_score": (
                        round(friction_score, 4)
                        if isinstance(friction_score, (float, int))
                        else None
                    ),
                    "active_route": active_route,
                    "shadow_route": shadow_route,
                    "active_reason": active.reason,
                    "shadow_reason": shadow.reason,
                }
            )

    scenario_count = len(scenarios)
    route_change_count = len(route_changes)
    route_change_rate = _rate(route_change_count, scenario_count)
    active_council_rate = _rate(active_routes["route_full_council"], scenario_count)
    shadow_council_rate = _rate(shadow_routes["route_full_council"], scenario_count)
    high_friction_escape_rate = _rate(high_friction_escape_count, high_friction_candidate_count)

    if invalid_json_line_count > 0:
        issues.append(f"invalid JSON line count in trace file: {invalid_json_line_count}")
    if scenario_count < 8:
        issues.append(f"insufficient calibration scenarios: {scenario_count} (< 8)")
    if route_change_rate > max_route_change_rate:
        issues.append(
            "route_change_rate above threshold " f"({route_change_rate} > {max_route_change_rate})"
        )
    if high_friction_escape_rate > max_high_friction_escape_rate:
        issues.append(
            "high_friction_escape_rate above threshold "
            f"({high_friction_escape_rate} > {max_high_friction_escape_rate})"
        )

    band_metrics: list[dict[str, Any]] = []
    for name in ("low", "mid", "high", "unknown"):
        state = band_state[name]
        count = state["count"]
        band_metrics.append(
            {
                "band": name,
                "count": count,
                "active_council_rate": _rate(state["active_council"], count),
                "shadow_council_rate": _rate(state["shadow_council"], count),
            }
        )

    payload = {
        "generated_at": _iso_now(),
        "source": "scripts/run_friction_shadow_calibration_report.py",
        "overall_ok": len(issues) == 0,
        "inputs": {
            "trace_path": trace_path.as_posix(),
            "active_thresholds": {
                "min_council_tension": round(active_council_tension, 4),
                "min_council_friction": round(active_friction_threshold, 4),
            },
            "shadow_thresholds": {
                "min_council_tension": round(float(shadow_gate.MIN_COUNCIL_TENSION), 4),
                "min_council_friction": round(float(shadow_gate.MIN_COUNCIL_FRICTION), 4),
            },
            "max_route_change_rate": max_route_change_rate,
            "max_high_friction_escape_rate": max_high_friction_escape_rate,
        },
        "metrics": {
            "scenario_count": scenario_count,
            "trace_row_count": len(trace_scenarios),
            "synthetic_row_count": len(synthetic_scenarios),
            "invalid_json_line_count": invalid_json_line_count,
            "route_change_count": route_change_count,
            "route_change_rate": route_change_rate,
            "active_council_rate": active_council_rate,
            "shadow_council_rate": shadow_council_rate,
            "council_rate_delta": round(shadow_council_rate - active_council_rate, 4),
            "high_friction_candidate_count": high_friction_candidate_count,
            "high_friction_escape_count": high_friction_escape_count,
            "high_friction_escape_rate": high_friction_escape_rate,
        },
        "route_distribution": {
            "active": dict(active_routes),
            "shadow": dict(shadow_routes),
        },
        "friction_band_metrics": band_metrics,
        "route_changes": route_changes,
        "issues": issues,
        "warnings": warnings,
    }
    return payload


def _bounded_optional_unit(value: float | None, flag_name: str) -> float | None:
    if value is None:
        return None
    if not (0.0 <= value <= 1.0):
        raise ValueError(f"{flag_name} must be between 0.0 and 1.0")
    return float(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate shadow-vs-active friction routing calibration report."
    )
    parser.add_argument(
        "--trace-path",
        default="memory/narrative/friction_shadow_eval.jsonl",
        help="Optional JSONL scenario replay file for calibration.",
    )
    parser.add_argument(
        "--out-dir",
        default="docs/status",
        help="Output directory for status artifacts.",
    )
    parser.add_argument(
        "--shadow-friction-threshold",
        type=float,
        default=None,
        help="Override shadow MIN_COUNCIL_FRICTION. Omit to use active threshold.",
    )
    parser.add_argument(
        "--shadow-council-tension",
        type=float,
        default=None,
        help="Override shadow MIN_COUNCIL_TENSION. Omit to use active threshold.",
    )
    parser.add_argument(
        "--max-route-change-rate",
        type=float,
        default=0.35,
        help="Fail threshold for shadow-vs-active route change rate.",
    )
    parser.add_argument(
        "--max-high-friction-escape-rate",
        type=float,
        default=0.15,
        help="Fail threshold for high-friction scenarios escaping council in shadow run.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when report contains issues.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        shadow_friction_threshold = _bounded_optional_unit(
            args.shadow_friction_threshold, "--shadow-friction-threshold"
        )
        shadow_council_tension = _bounded_optional_unit(
            args.shadow_council_tension, "--shadow-council-tension"
        )
        max_route_change_rate = _bounded_optional_unit(
            args.max_route_change_rate, "--max-route-change-rate"
        )
        max_high_friction_escape_rate = _bounded_optional_unit(
            args.max_high_friction_escape_rate, "--max-high-friction-escape-rate"
        )
    except ValueError as exc:
        raise SystemExit(str(exc))

    trace_path = Path(args.trace_path)
    out_dir = Path(args.out_dir).resolve()

    payload = build_report(
        trace_path=trace_path,
        shadow_friction_threshold=shadow_friction_threshold,
        shadow_council_tension=shadow_council_tension,
        max_route_change_rate=max_route_change_rate if max_route_change_rate is not None else 0.35,
        max_high_friction_escape_rate=(
            max_high_friction_escape_rate if max_high_friction_escape_rate is not None else 0.15
        ),
    )
    _write_json(out_dir / JSON_FILENAME, payload)
    _write_markdown(out_dir / MARKDOWN_FILENAME, payload)
    _emit(payload)

    if args.strict and not payload.get("overall_ok", False):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
