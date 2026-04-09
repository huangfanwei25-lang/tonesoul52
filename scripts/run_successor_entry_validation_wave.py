#!/usr/bin/env python3
"""Run bounded successor-entry validation against session-start and observer-window."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run successor-entry validation scenarios for canonical-center and hot-memory readouts.",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=REPO_ROOT / "temp" / "successor_entry_validation_wave",
        help="Workspace directory used for generated scenario fixtures.",
    )
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument("--markdown-out", type=Path, default=None)
    return parser


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _check(name: str, passed: bool, *, friction: str = "medium") -> dict[str, str]:
    return {
        "check": name,
        "result": "pass" if passed else "FAIL",
        "friction": friction,
    }


def _get_layer(anchor: dict[str, Any], layer_name: str) -> dict[str, Any]:
    for layer in (anchor.get("hot_memory_ladder") or {}).get("layers") or []:
        if str(layer.get("layer", "")) == layer_name:
            return layer
    return {}


def build_scenarios(workspace: Path) -> list[dict[str, Any]]:
    from scripts.run_launch_continuity_validation_wave import build_scenarios as _build

    wanted = {"clean_pass", "claim_conflict", "stale_compaction", "contested_dossier"}
    return [scenario for scenario in _build(workspace) if scenario["name"] in wanted]


def run_successor_validation(workspace: Path) -> list[dict[str, Any]]:
    from scripts.run_launch_continuity_validation_wave import run_session_start
    from scripts.run_observer_window import run_observer_window

    scenarios = build_scenarios(workspace)
    results: list[dict[str, Any]] = []

    for scenario in scenarios:
        agent_id = f"successor-wave-{scenario['name']}"
        session_payload = run_session_start(
            agent_id=agent_id,
            state_path=scenario["state_path"],
            traces_path=scenario["traces_path"],
        )
        anchor = run_observer_window(
            agent=agent_id,
            state_path=scenario["state_path"],
            traces_path=scenario["traces_path"],
        )

        canonical_center = session_payload.get("canonical_center") or {}
        correction = canonical_center.get("successor_correction") or {}
        ladder = anchor.get("hot_memory_ladder") or {}
        live_coordination = _get_layer(anchor, "live_coordination")
        bounded_handoff = _get_layer(anchor, "bounded_handoff")
        replay_review = _get_layer(anchor, "replay_review")

        correction_rule = str(correction.get("correction_rule", "")).strip()
        checks = [
            _check(
                "canonical_center_present", bool(canonical_center.get("present")), friction="high"
            ),
            _check(
                "short_board_visible",
                bool((canonical_center.get("current_short_board") or {}).get("present")),
                friction="high",
            ),
            _check("hot_memory_ladder_present", bool(ladder.get("layers")), friction="high"),
            _check(
                "hot_memory_ladder_starts_with_canonical_center",
                bool((ladder.get("layers") or [{}])[0].get("layer") == "canonical_center"),
                friction="medium",
            ),
            _check(
                "successor_correction_present",
                bool(correction.get("highest_risk_misread")),
                friction="high",
            ),
            _check(
                "correction_mentions_live_coordination",
                "readiness" in correction_rule and "claims" in correction_rule,
                friction="high",
            ),
        ]

        if scenario["name"] == "claim_conflict":
            checks.append(
                _check(
                    "claim_conflict_keeps_live_coordination_contested",
                    str(live_coordination.get("status", "")) == "contested",
                    friction="high",
                )
            )
        elif scenario["name"] == "stale_compaction":
            checks.append(
                _check(
                    "stale_compaction_keeps_bounded_handoff_contested",
                    str(bounded_handoff.get("status", "")) == "contested",
                    friction="high",
                )
            )
        elif scenario["name"] == "contested_dossier":
            checks.append(
                _check(
                    "contested_dossier_keeps_replay_review_contested",
                    str(replay_review.get("status", "")) == "contested",
                    friction="high",
                )
            )

        failed = [item for item in checks if item["result"] == "FAIL"]
        results.append(
            {
                "scenario": scenario["name"],
                "passed": len(checks) - len(failed),
                "failed": len(failed),
                "high_friction_fails": sum(1 for item in failed if item.get("friction") == "high"),
                "findings": checks,
                "readiness": str((session_payload.get("readiness") or {}).get("status", "unknown")),
                "anchor_counts": anchor.get("counts") or {},
                "anchor_summary": str(anchor.get("summary_text", "")),
                "ladder_summary": str(ladder.get("summary_text", "")),
                "misread_focus": str(correction.get("highest_risk_misread", "none")),
                "correction_summary": str(correction.get("summary_text", "")),
            }
        )

    return results


def build_report(results: list[dict[str, Any]]) -> dict[str, Any]:
    total_passed = sum(int(item.get("passed", 0) or 0) for item in results)
    total_failed = sum(int(item.get("failed", 0) or 0) for item in results)
    total_high_friction_fails = sum(
        int(item.get("high_friction_fails", 0) or 0) for item in results
    )
    failed_scenarios = [item for item in results if int(item.get("failed", 0) or 0) > 0]
    top_friction_scenario = failed_scenarios[0]["scenario"] if failed_scenarios else "none"
    top_friction_checks = (
        [
            finding["check"]
            for finding in failed_scenarios[0]["findings"]
            if finding.get("result") == "FAIL"
        ]
        if failed_scenarios
        else []
    )
    overall_ok = total_failed == 0

    return {
        "generated_at": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "overall_ok": overall_ok,
        "overall_status": "pass" if overall_ok else "needs_fix",
        "scenario_count": len(results),
        "total_passed": total_passed,
        "total_failed": total_failed,
        "total_high_friction_fails": total_high_friction_fails,
        "top_friction_scenario": top_friction_scenario,
        "top_friction_checks": top_friction_checks,
        "summary_text": (
            f"successor_entry_validation status={'pass' if overall_ok else 'needs_fix'} "
            f"scenarios={len(results)} passed={total_passed} failed={total_failed} "
            f"high_friction={total_high_friction_fails} top_friction_scenario={top_friction_scenario}"
        ),
        "scenarios": results,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Successor Entry Validation Wave",
        "",
        f"> Generated at `{report.get('generated_at', '')}`. Advisory only.",
        "",
        f"**Status**: `{report.get('overall_status', 'unknown')}`  ",
        f"**Scenarios**: {int(report.get('scenario_count', 0) or 0)} | **Passed**: {int(report.get('total_passed', 0) or 0)} | **Failed**: {int(report.get('total_failed', 0) or 0)} | **High-friction fails**: {int(report.get('total_high_friction_fails', 0) or 0)}",
        "",
        f"**Top friction scenario**: `{report.get('top_friction_scenario', 'none')}`  ",
        f"**Top friction checks**: `{', '.join(report.get('top_friction_checks') or ['none'])}`",
        "",
    ]

    for scenario in report.get("scenarios") or []:
        lines.extend(
            [
                f"## Scenario: `{scenario.get('scenario', 'unknown')}`",
                "",
                f"- Passed: {int(scenario.get('passed', 0) or 0)} | Failed: {int(scenario.get('failed', 0) or 0)} | High-friction: {int(scenario.get('high_friction_fails', 0) or 0)}",
                f"- Readiness: `{scenario.get('readiness', 'unknown')}`",
                f"- Misread focus: `{scenario.get('misread_focus', 'none')}`",
                f"- Correction: `{scenario.get('correction_summary', '')}`",
                f"- Counts: `{scenario.get('anchor_counts', {})}`",
                f"- Summary: `{scenario.get('anchor_summary', '')}`",
                f"- Ladder: `{scenario.get('ladder_summary', '')}`",
                "",
                "| Check | Result | Friction |",
                "|-------|--------|---------|",
            ]
        )
        for finding in scenario.get("findings") or []:
            lines.append(
                f"| `{finding.get('check', '')}` | {finding.get('result', '')} | {finding.get('friction', '')} |"
            )
        lines.append("")

    lines.extend(
        [
            "> [!NOTE]",
            "> This validation wave is advisory. It checks whether a fresh successor can see the canonical center,",
            "> the hot-memory ladder, and the explicit correction that observer stable output is not execution permission.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    results = run_successor_validation(args.workspace)
    report = build_report(results)

    if args.json_out is not None:
        _write_json(args.json_out, report)
    if args.markdown_out is not None:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(render_markdown(report), encoding="utf-8")

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
