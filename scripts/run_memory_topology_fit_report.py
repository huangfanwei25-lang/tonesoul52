"""Generate pragmatic memory-topology fit recommendation for ToneSoul."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

JSON_FILENAME = "memory_topology_fit_latest.json"
MARKDOWN_FILENAME = "memory_topology_fit_latest.md"

DEFAULT_PROFILE = "basic"
DEFAULT_MAX_VRAM_GB = 8.0
DEFAULT_MAX_LATENCY_MS = 2500
DEFAULT_MIN_RECOMMENDATION_SCORE = 0.45

DEFAULT_HIGH_FRICTION_RATE = 0.5
DEFAULT_UNRESOLVED_TOPIC_RATE = 0.1
DEFAULT_IDENTITY_CHOICE_INDEX = 0.6
DEFAULT_HIGH_FRICTION_ESCAPE_RATE = 0.0
DEFAULT_ROUTE_CHANGE_RATE = 0.0

TOPOLOGY_CANDIDATES = (
    {
        "name": "flat",
        "required_budget": 0.15,
        "governance_capacity": 0.45,
        "memory_stack": [
            "flat_jsonl_experience_log",
            "rolling_summary_memory",
            "tension_friction_event_index",
        ],
    },
    {
        "name": "planar",
        "required_budget": 0.40,
        "governance_capacity": 0.74,
        "memory_stack": [
            "flat_jsonl_experience_log",
            "rolling_summary_memory",
            "tension_friction_event_index",
            "conflict_graph_links",
            "topic_to_boundary_relation_index",
        ],
    },
    {
        "name": "hierarchical",
        "required_budget": 0.72,
        "governance_capacity": 0.9,
        "memory_stack": [
            "flat_jsonl_experience_log",
            "conflict_graph_links",
            "multi_layer_summary_pyramid",
            "policy_trace_memory_layer",
        ],
    },
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


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_markdown(payload), encoding="utf-8")


def _render_markdown(payload: dict[str, Any]) -> str:
    recommendation = payload.get("recommendation", {})
    diagnostics = payload.get("diagnostics", {})
    candidates = payload.get("candidate_scores", [])
    lines = [
        "# Memory Topology Fit Latest",
        "",
        f"- generated_at: {payload.get('generated_at')}",
        f"- overall_ok: {str(payload.get('overall_ok')).lower()}",
        f"- recommended_topology: {recommendation.get('topology', 'unknown')}",
        f"- profile: {payload.get('inputs', {}).get('profile')}",
        f"- recommendation_score: {recommendation.get('score')}",
        "",
        "## Diagnostics",
        f"- governance_need_score: {diagnostics.get('governance_need_score')}",
        f"- resource_budget_score: {diagnostics.get('resource_budget_score')}",
        f"- high_friction_rate: {diagnostics.get('high_friction_rate')}",
        f"- unresolved_topic_rate: {diagnostics.get('unresolved_topic_rate')}",
        f"- identity_choice_index: {diagnostics.get('identity_choice_index')}",
        f"- high_friction_escape_rate: {diagnostics.get('high_friction_escape_rate')}",
        f"- route_change_rate: {diagnostics.get('route_change_rate')}",
        "",
        "## Candidate Scores",
        "",
        "| topology | feasible | fit_score | required_budget | governance_capacity |",
        "| --- | --- | ---: | ---: | ---: |",
    ]

    if isinstance(candidates, list):
        for item in candidates:
            if not isinstance(item, dict):
                continue
            lines.append(
                f"| {item.get('name')} | {str(item.get('feasible')).lower()} | "
                f"{item.get('fit_score')} | {item.get('required_budget')} | "
                f"{item.get('governance_capacity')} |"
            )

    stack = recommendation.get("memory_stack", [])
    if isinstance(stack, list) and stack:
        lines.append("")
        lines.append("## Recommended Stack")
        for entry in stack:
            lines.append(f"- {entry}")

    warnings = payload.get("warnings", [])
    if isinstance(warnings, list) and warnings:
        lines.append("")
        lines.append("## Warnings")
        for warning in warnings[:20]:
            lines.append(f"- {warning}")

    issues = payload.get("issues", [])
    if isinstance(issues, list) and issues:
        lines.append("")
        lines.append("## Issues")
        for issue in issues[:20]:
            lines.append(f"- {issue}")

    return "\n".join(lines) + "\n"


def _safe_read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, f"file missing: {path.as_posix()}"
    try:
        payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError as exc:
        return None, f"invalid json: {exc}"
    if not isinstance(payload, dict):
        return None, "top-level json must be object"
    return payload, None


def _safe_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _metric_or_default(
    value: Any,
    default: float,
    *,
    metric_name: str,
    warnings: list[str],
) -> float:
    parsed = _safe_float(value)
    if parsed is None:
        warnings.append(f"{metric_name} missing; using default {default}")
        return round(_clamp_unit(default), 4)
    return round(_clamp_unit(parsed), 4)


def build_report(
    *,
    replay_payload: dict[str, Any] | None,
    calibration_payload: dict[str, Any] | None,
    reflection_payload: dict[str, Any] | None,
    profile: str,
    max_vram_gb: float,
    max_latency_ms: int,
    min_recommendation_score: float,
) -> dict[str, Any]:
    warnings: list[str] = []
    issues: list[str] = []

    replay_metrics = replay_payload.get("metrics", {}) if isinstance(replay_payload, dict) else {}
    calibration_metrics = (
        calibration_payload.get("metrics", {}) if isinstance(calibration_payload, dict) else {}
    )
    reflection_quality = (
        reflection_payload.get("quality_signals", {})
        if isinstance(reflection_payload, dict)
        else {}
    )

    high_friction_rate = _metric_or_default(
        replay_metrics.get("high_friction_scenario_rate"),
        DEFAULT_HIGH_FRICTION_RATE,
        metric_name="high_friction_rate",
        warnings=warnings,
    )
    unresolved_topic_rate = _metric_or_default(
        reflection_quality.get("unresolved_topic_rate"),
        DEFAULT_UNRESOLVED_TOPIC_RATE,
        metric_name="unresolved_topic_rate",
        warnings=warnings,
    )
    identity_choice_index = _metric_or_default(
        reflection_quality.get("identity_choice_index"),
        DEFAULT_IDENTITY_CHOICE_INDEX,
        metric_name="identity_choice_index",
        warnings=warnings,
    )
    high_friction_escape_rate = _metric_or_default(
        calibration_metrics.get("high_friction_escape_rate"),
        DEFAULT_HIGH_FRICTION_ESCAPE_RATE,
        metric_name="high_friction_escape_rate",
        warnings=warnings,
    )
    route_change_rate = _metric_or_default(
        calibration_metrics.get("route_change_rate"),
        DEFAULT_ROUTE_CHANGE_RATE,
        metric_name="route_change_rate",
        warnings=warnings,
    )

    governance_need_score = round(
        _clamp_unit(
            0.42 * high_friction_rate
            + 0.23 * unresolved_topic_rate
            + 0.20 * (1.0 - identity_choice_index)
            + 0.15 * high_friction_escape_rate
        ),
        4,
    )

    vram_score = _clamp_unit((max_vram_gb - 4.0) / 16.0)
    latency_score = _clamp_unit((float(max_latency_ms) - 800.0) / 4200.0)
    resource_budget_score = min(vram_score, latency_score)
    if profile == "basic":
        resource_budget_score = _clamp_unit(resource_budget_score - 0.10)
    elif profile == "governance":
        resource_budget_score = _clamp_unit(resource_budget_score + 0.10)
    resource_budget_score = round(resource_budget_score, 4)

    candidate_scores: list[dict[str, Any]] = []
    for candidate in TOPOLOGY_CANDIDATES:
        required_budget = float(candidate["required_budget"])
        governance_capacity = float(candidate["governance_capacity"])
        feasible = required_budget <= (resource_budget_score + 0.08)
        fit_score = 1.0 - (
            0.7 * abs(governance_need_score - governance_capacity)
            + 0.3 * abs(resource_budget_score - required_budget)
        )
        if not feasible:
            fit_score -= 0.35
        fit_score = round(max(0.0, min(1.0, fit_score)), 4)
        candidate_scores.append(
            {
                "name": candidate["name"],
                "feasible": feasible,
                "fit_score": fit_score,
                "required_budget": round(required_budget, 4),
                "governance_capacity": round(governance_capacity, 4),
                "memory_stack": list(candidate["memory_stack"]),
            }
        )

    ranked = sorted(candidate_scores, key=lambda item: item["fit_score"], reverse=True)
    feasible_ranked = [item for item in ranked if bool(item.get("feasible"))]
    if feasible_ranked:
        chosen = feasible_ranked[0]
    elif ranked:
        chosen = ranked[0]
        issues.append("no feasible topology under current budget; selected best-effort candidate")
    else:
        chosen = {
            "name": "flat",
            "feasible": False,
            "fit_score": 0.0,
            "required_budget": 0.15,
            "governance_capacity": 0.45,
            "memory_stack": [],
        }
        issues.append("no topology candidates available")

    if float(chosen.get("fit_score", 0.0)) < min_recommendation_score:
        issues.append(
            "recommendation score below threshold "
            f"({chosen.get('fit_score')} < {round(min_recommendation_score, 4)})"
        )

    if chosen.get("name") == "flat" and governance_need_score >= 0.62:
        warnings.append(
            "governance pressure is high while recommendation remains flat; consider planar upgrade"
        )

    payload = {
        "generated_at": _iso_now(),
        "source": "scripts/run_memory_topology_fit_report.py",
        "overall_ok": len(issues) == 0,
        "inputs": {
            "profile": profile,
            "max_vram_gb": round(float(max_vram_gb), 4),
            "max_latency_ms": int(max_latency_ms),
            "min_recommendation_score": round(float(min_recommendation_score), 4),
            "replay_status_path": f"docs/status/{'friction_shadow_replay_latest.json'}",
            "calibration_status_path": f"docs/status/{'friction_shadow_calibration_latest.json'}",
            "reflection_status_path": f"docs/status/{'philosophical_reflection_latest.json'}",
        },
        "diagnostics": {
            "governance_need_score": governance_need_score,
            "resource_budget_score": resource_budget_score,
            "high_friction_rate": high_friction_rate,
            "unresolved_topic_rate": unresolved_topic_rate,
            "identity_choice_index": identity_choice_index,
            "high_friction_escape_rate": high_friction_escape_rate,
            "route_change_rate": route_change_rate,
        },
        "recommendation": {
            "topology": chosen.get("name"),
            "score": chosen.get("fit_score"),
            "feasible_under_budget": bool(chosen.get("feasible", False)),
            "memory_stack": list(chosen.get("memory_stack", [])),
            "tonesoul_delta": (
                "Prioritize memory of friction/boundary choices over raw transcript recall."
            ),
        },
        "candidate_scores": ranked,
        "issues": issues,
        "warnings": warnings,
    }
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate memory topology fit recommendation for ToneSoul."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument(
        "--out-dir", default="docs/status", help="Output directory for status artifacts."
    )
    parser.add_argument(
        "--profile",
        default=DEFAULT_PROFILE,
        choices=("basic", "governance"),
        help="Target operation profile.",
    )
    parser.add_argument(
        "--max-vram-gb",
        type=float,
        default=DEFAULT_MAX_VRAM_GB,
        help="Approximate available VRAM budget in GB.",
    )
    parser.add_argument(
        "--max-latency-ms",
        type=int,
        default=DEFAULT_MAX_LATENCY_MS,
        help="Maximum acceptable p95 latency in milliseconds.",
    )
    parser.add_argument(
        "--min-recommendation-score",
        type=float,
        default=DEFAULT_MIN_RECOMMENDATION_SCORE,
        help="Fail threshold for recommendation confidence.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when report contains issues.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo_root).resolve()
    out_dir = (repo_root / args.out_dir).resolve()

    replay_payload, replay_error = _safe_read_json(
        repo_root / "docs/status/friction_shadow_replay_latest.json"
    )
    calibration_payload, calibration_error = _safe_read_json(
        repo_root / "docs/status/friction_shadow_calibration_latest.json"
    )
    reflection_payload, reflection_error = _safe_read_json(
        repo_root / "docs/status/philosophical_reflection_latest.json"
    )

    payload = build_report(
        replay_payload=replay_payload,
        calibration_payload=calibration_payload,
        reflection_payload=reflection_payload,
        profile=args.profile,
        max_vram_gb=float(args.max_vram_gb),
        max_latency_ms=max(1, int(args.max_latency_ms)),
        min_recommendation_score=_clamp_unit(float(args.min_recommendation_score)),
    )

    if replay_error:
        payload["warnings"].append(f"replay_status: {replay_error}")
    if calibration_error:
        payload["warnings"].append(f"calibration_status: {calibration_error}")
    if reflection_error:
        payload["warnings"].append(f"reflection_status: {reflection_error}")

    _write_json(out_dir / JSON_FILENAME, payload)
    _write_markdown(out_dir / MARKDOWN_FILENAME, payload)
    _emit(payload)

    if args.strict and not payload.get("overall_ok", False):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
