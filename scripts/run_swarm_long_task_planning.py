"""Run the long-task persona swarm planning lane with stable defaults."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_INPUT_PATH = "docs/experiments/persona_swarm_long_task_input_2026-03-01.json"
DEFAULT_OUT_PATH = "docs/status/persona_swarm_long_task_latest.json"
DEFAULT_SUMMARY_PATH = "docs/status/swarm_long_task_plan_latest.json"
INPUT_PATH_VALIDATION_ERROR_PREFIX = "::error::long-task input_path does not exist"


@dataclass(frozen=True)
class PlanningConfig:
    repo_root: Path
    input_path: Path
    out_path: Path
    summary_path: Path
    strict: bool


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _resolve_path(repo_root: Path, value: str) -> Path:
    raw = Path(str(value).strip())
    if raw.is_absolute():
        return raw.resolve()
    return (repo_root / raw).resolve()


def _build_config(args: argparse.Namespace) -> PlanningConfig:
    repo_root = Path(args.repo_root).resolve()
    return PlanningConfig(
        repo_root=repo_root,
        input_path=_resolve_path(repo_root, args.input),
        out_path=_resolve_path(repo_root, args.out),
        summary_path=_resolve_path(repo_root, args.summary_out),
        strict=bool(args.strict),
    )


def build_command(config: PlanningConfig) -> tuple[list[str], list[str], str | None]:
    command = [
        sys.executable,
        "scripts/run_persona_swarm_framework.py",
        "--repo-root",
        str(config.repo_root),
        "--input",
        str(config.input_path),
        "--out",
        str(config.out_path),
    ]
    warnings: list[str] = []

    if not config.input_path.exists():
        return (
            command,
            warnings,
            f"{INPUT_PATH_VALIDATION_ERROR_PREFIX}. got='{config.input_path}'",
        )

    if config.input_path.suffix.lower() != ".json":
        warnings.append(
            "long-task input_path does not end with .json; make sure this is intentional."
        )

    if config.strict:
        command.append("--strict")

    return command, warnings, None


def _emit_warning(message: str) -> None:
    print(f"::warning::{message}")


def _extract_summary(
    swarm_payload: dict[str, object],
    *,
    input_path_label: str,
) -> dict[str, object]:
    evaluation = swarm_payload.get("evaluation")
    if not isinstance(evaluation, dict):
        evaluation = {}
    metrics = evaluation.get("metrics")
    if not isinstance(metrics, dict):
        metrics = {}
    persona_positioning = evaluation.get("persona_positioning")
    if not isinstance(persona_positioning, dict):
        persona_positioning = {}
    readiness_gate = swarm_payload.get("readiness_gate")
    if not isinstance(readiness_gate, dict):
        readiness_gate = {}
    cost_profile = readiness_gate.get("cost_profile")
    if not isinstance(cost_profile, dict):
        cost_profile = {}

    return {
        "generated_at": _iso_now(),
        "source": "scripts/run_swarm_long_task_planning.py",
        "input_path": input_path_label,
        "decision": evaluation.get("decision"),
        "decision_support": evaluation.get("decision_support"),
        "swarm_score": metrics.get("swarm_score"),
        "safety_pass_rate": metrics.get("safety_pass_rate"),
        "token_latency_cost_index": metrics.get("token_latency_cost_index"),
        "archetype": persona_positioning.get("archetype"),
        "cost_tier": cost_profile.get("tier"),
        "readiness_gate_passed": readiness_gate.get("passed"),
        "next_phase": "Phase 124",
    }


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run long-task swarm planning wrapper.")
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument(
        "--input", default=DEFAULT_INPUT_PATH, help="Long-task swarm input JSON path."
    )
    parser.add_argument("--out", default=DEFAULT_OUT_PATH, help="Detailed swarm output JSON path.")
    parser.add_argument(
        "--summary-out",
        default=DEFAULT_SUMMARY_PATH,
        help="Condensed planning summary JSON path.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail when readiness gate does not pass.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = _build_config(args)
    command, warnings, error = build_command(config)

    if error:
        print(error)
        return 1

    for warning in warnings:
        _emit_warning(warning)

    result = subprocess.run(command, check=False)
    if int(result.returncode) != 0:
        return int(result.returncode)

    try:
        swarm_payload = json.loads(config.out_path.read_text(encoding="utf-8"))
        if not isinstance(swarm_payload, dict):
            raise ValueError("swarm output must be an object")
        try:
            input_label = config.input_path.relative_to(config.repo_root).as_posix()
        except ValueError:
            input_label = str(config.input_path)
        summary = _extract_summary(swarm_payload, input_path_label=input_label)
        _write_json(config.summary_path, summary)
    except Exception as exc:
        print(f"::error::failed to build long-task summary: {exc}")
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
