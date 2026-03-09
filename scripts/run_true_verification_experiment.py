from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from tonesoul.true_verification_summary import summarize_long_run_payload  # noqa: E402

EXPERIMENT_NAME = "true_verification_weekly"
DEFAULT_PROFILE = "security_watch"
DEFAULT_EXPERIMENT_DAYS = 7.0
DEFAULT_WAKE_INTERVAL_HOURS = 3.0
DEFAULT_HISTORY_PATH = "memory/autonomous/true_verification_weekly/dream_wakeup_history.jsonl"
DEFAULT_SNAPSHOT_PATH = "docs/status/true_verification_weekly/dream_wakeup_snapshot.json"
DEFAULT_DASHBOARD_OUT_DIR = "docs/status/true_verification_weekly"
DEFAULT_SCHEDULE_SNAPSHOT_PATH = (
    "docs/status/true_verification_weekly/autonomous_registry_schedule_latest.json"
)
DEFAULT_SCHEDULE_HISTORY_PATH = (
    "memory/autonomous/true_verification_weekly/registry_schedule_history.jsonl"
)
DEFAULT_SCHEDULE_STATE_PATH = (
    "memory/autonomous/true_verification_weekly/registry_schedule_state.json"
)
DEFAULT_PREFLIGHT_HISTORY_PATH = (
    "memory/autonomous/true_verification_weekly/preflight/dream_wakeup_history.jsonl"
)
DEFAULT_PREFLIGHT_SNAPSHOT_PATH = (
    "docs/status/true_verification_weekly/preflight/dream_wakeup_snapshot.json"
)
DEFAULT_PREFLIGHT_DASHBOARD_OUT_DIR = "docs/status/true_verification_weekly/preflight"
DEFAULT_PREFLIGHT_SCHEDULE_SNAPSHOT_PATH = (
    "docs/status/true_verification_weekly/preflight/autonomous_registry_schedule_latest.json"
)
DEFAULT_PREFLIGHT_SCHEDULE_HISTORY_PATH = (
    "memory/autonomous/true_verification_weekly/preflight/registry_schedule_history.jsonl"
)
DEFAULT_PREFLIGHT_SCHEDULE_STATE_PATH = (
    "memory/autonomous/true_verification_weekly/preflight/registry_schedule_state.json"
)
DEFAULT_EXPERIMENT_SUMMARY_PATH = (
    "docs/status/true_verification_weekly/true_verification_experiment_latest.json"
)
DEFAULT_DASHBOARD_JSON_PATH = "dream_observability_latest.json"
DEFAULT_DASHBOARD_HTML_PATH = "dream_observability_latest.html"


def _load_long_run_module():
    path = repo_root / "scripts" / "run_autonomous_registry_long_run.py"
    spec = importlib.util.spec_from_file_location("run_autonomous_registry_long_run_script", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_LONG_RUN_MODULE = _load_long_run_module()


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _reset_file(path: Path) -> None:
    if path.exists():
        path.unlink()


def _reset_dashboard_artifacts(dashboard_dir: Path) -> None:
    _reset_file(dashboard_dir / DEFAULT_DASHBOARD_JSON_PATH)
    _reset_file(dashboard_dir / DEFAULT_DASHBOARD_HTML_PATH)


def _set_action_default(
    parser: argparse.ArgumentParser,
    option: str,
    value: object,
) -> None:
    for action in parser._actions:
        if option in getattr(action, "option_strings", []):
            action.default = value
            return
    raise ValueError(f"unknown parser option: {option}")


def build_parser() -> argparse.ArgumentParser:
    parser = _LONG_RUN_MODULE.build_parser()
    parser.description = "Run the weekly ToneSoul True Verification experiment."
    _set_action_default(parser, "--profile", DEFAULT_PROFILE)
    _set_action_default(parser, "--history-path", DEFAULT_HISTORY_PATH)
    _set_action_default(parser, "--snapshot-path", DEFAULT_SNAPSHOT_PATH)
    _set_action_default(parser, "--dashboard-out-dir", DEFAULT_DASHBOARD_OUT_DIR)
    _set_action_default(parser, "--schedule-snapshot-path", DEFAULT_SCHEDULE_SNAPSHOT_PATH)
    _set_action_default(parser, "--schedule-history-path", DEFAULT_SCHEDULE_HISTORY_PATH)
    _set_action_default(parser, "--schedule-state-path", DEFAULT_SCHEDULE_STATE_PATH)
    _set_action_default(parser, "--preflight-history-path", DEFAULT_PREFLIGHT_HISTORY_PATH)
    _set_action_default(parser, "--preflight-snapshot-path", DEFAULT_PREFLIGHT_SNAPSHOT_PATH)
    _set_action_default(
        parser, "--preflight-dashboard-out-dir", DEFAULT_PREFLIGHT_DASHBOARD_OUT_DIR
    )
    _set_action_default(
        parser,
        "--preflight-schedule-snapshot-path",
        DEFAULT_PREFLIGHT_SCHEDULE_SNAPSHOT_PATH,
    )
    _set_action_default(
        parser,
        "--preflight-schedule-history-path",
        DEFAULT_PREFLIGHT_SCHEDULE_HISTORY_PATH,
    )
    _set_action_default(
        parser,
        "--preflight-schedule-state-path",
        DEFAULT_PREFLIGHT_SCHEDULE_STATE_PATH,
    )
    _set_action_default(parser, "--max-cycles", None)
    parser.add_argument(
        "--experiment-days",
        type=float,
        default=DEFAULT_EXPERIMENT_DAYS,
        help="Planned duration of the True Verification experiment in days",
    )
    parser.add_argument(
        "--wake-interval-hours",
        type=float,
        default=DEFAULT_WAKE_INTERVAL_HOURS,
        help="Hours between autonomous wake-up ticks when --interval-seconds is not explicitly set",
    )
    parser.add_argument(
        "--experiment-summary-path",
        type=str,
        default=DEFAULT_EXPERIMENT_SUMMARY_PATH,
        help="Path to write the latest experiment wrapper summary JSON",
    )
    parser.add_argument(
        "--reuse-experiment-state",
        action="store_true",
        help="Reuse the long-run experiment state/history instead of starting from a fresh weekly sample",
    )
    return parser


def _validate_positive(name: str, value: float) -> None:
    if float(value) <= 0:
        raise ValueError(f"{name} must be > 0")


def _derive_interval_seconds(args: argparse.Namespace) -> float:
    if args.interval_seconds is not None:
        return float(args.interval_seconds)
    return float(args.wake_interval_hours) * 3600.0


def _derive_max_cycles(args: argparse.Namespace) -> int:
    if args.max_cycles is not None:
        return int(args.max_cycles)
    total_hours = float(args.experiment_days) * 24.0
    planned = int(math.ceil(total_hours / float(args.wake_interval_hours)))
    return max(1, planned)


def _reset_experiment_artifacts(args: argparse.Namespace) -> None:
    _reset_file(Path(args.history_path))
    _reset_file(Path(args.snapshot_path))
    _reset_file(Path(args.schedule_snapshot_path))
    _reset_file(Path(args.schedule_history_path))
    _reset_file(Path(args.schedule_state_path))
    _reset_dashboard_artifacts(Path(args.dashboard_out_dir))
    _reset_file(Path(args.experiment_summary_path))


def _build_long_run_args(args: argparse.Namespace) -> argparse.Namespace:
    long_run_args = argparse.Namespace(**vars(args))
    long_run_args.interval_seconds = _derive_interval_seconds(args)
    long_run_args.max_cycles = _derive_max_cycles(args)
    return long_run_args


def run_experiment(args: argparse.Namespace) -> dict[str, object]:
    _validate_positive("experiment_days", args.experiment_days)
    _validate_positive("wake_interval_hours", args.wake_interval_hours)
    if not bool(args.reuse_experiment_state):
        _reset_experiment_artifacts(args)
    long_run_args = _build_long_run_args(args)
    payload = _LONG_RUN_MODULE.run_long_run(long_run_args)
    result = {
        "overall_ok": bool(payload.get("overall_ok", True)),
        "experiment": {
            "name": EXPERIMENT_NAME,
            "profile": long_run_args.profile,
            "days": float(args.experiment_days),
            "wake_interval_hours": float(args.wake_interval_hours),
            "interval_seconds": float(long_run_args.interval_seconds),
            "planned_cycles": int(long_run_args.max_cycles),
            "reuse_experiment_state": bool(args.reuse_experiment_state),
            "summary_path": str(args.experiment_summary_path),
        },
        "gate": payload.get("gate"),
        "preflight": payload.get("preflight"),
        "schedule": payload.get("schedule"),
    }
    _write_json(Path(args.experiment_summary_path), summarize_long_run_payload(result) or result)
    return result


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    args = build_parser().parse_args(argv)
    payload = run_experiment(args)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.strict and not payload.get("overall_ok", True):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
