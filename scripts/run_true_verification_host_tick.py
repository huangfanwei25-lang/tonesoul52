from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from tonesoul.true_verification_summary import summarize_long_run_payload  # noqa: E402


def _load_script_module(module_name: str, filename: str):
    path = repo_root / "scripts" / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_LONG_RUN_MODULE = _load_script_module(
    "run_autonomous_registry_long_run_script",
    "run_autonomous_registry_long_run.py",
)
_EXPERIMENT_MODULE = _load_script_module(
    "run_true_verification_experiment_script",
    "run_true_verification_experiment.py",
)

DEFAULT_TICK_SUMMARY_PATH = (
    "docs/status/true_verification_weekly/true_verification_host_tick_latest.json"
)


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
    _reset_file(dashboard_dir / _EXPERIMENT_MODULE.DEFAULT_DASHBOARD_JSON_PATH)
    _reset_file(dashboard_dir / _EXPERIMENT_MODULE.DEFAULT_DASHBOARD_HTML_PATH)


def _reset_experiment_artifacts(args: argparse.Namespace) -> None:
    _reset_file(Path(args.history_path))
    _reset_file(Path(args.snapshot_path))
    _reset_file(Path(args.schedule_snapshot_path))
    _reset_file(Path(args.schedule_history_path))
    _reset_file(Path(args.schedule_state_path))
    _reset_dashboard_artifacts(Path(args.dashboard_out_dir))
    _reset_file(Path(args.tick_summary_path))
    _reset_file(Path(_EXPERIMENT_MODULE.DEFAULT_EXPERIMENT_SUMMARY_PATH))


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
    parser.description = "Run one host-driven True Verification tick for Windows Task Scheduler / cron style orchestration."
    _set_action_default(parser, "--profile", _EXPERIMENT_MODULE.DEFAULT_PROFILE)
    _set_action_default(parser, "--history-path", _EXPERIMENT_MODULE.DEFAULT_HISTORY_PATH)
    _set_action_default(parser, "--snapshot-path", _EXPERIMENT_MODULE.DEFAULT_SNAPSHOT_PATH)
    _set_action_default(parser, "--dashboard-out-dir", _EXPERIMENT_MODULE.DEFAULT_DASHBOARD_OUT_DIR)
    _set_action_default(
        parser,
        "--schedule-snapshot-path",
        _EXPERIMENT_MODULE.DEFAULT_SCHEDULE_SNAPSHOT_PATH,
    )
    _set_action_default(
        parser,
        "--schedule-history-path",
        _EXPERIMENT_MODULE.DEFAULT_SCHEDULE_HISTORY_PATH,
    )
    _set_action_default(
        parser,
        "--schedule-state-path",
        _EXPERIMENT_MODULE.DEFAULT_SCHEDULE_STATE_PATH,
    )
    _set_action_default(
        parser,
        "--preflight-history-path",
        _EXPERIMENT_MODULE.DEFAULT_PREFLIGHT_HISTORY_PATH,
    )
    _set_action_default(
        parser,
        "--preflight-snapshot-path",
        _EXPERIMENT_MODULE.DEFAULT_PREFLIGHT_SNAPSHOT_PATH,
    )
    _set_action_default(
        parser,
        "--preflight-dashboard-out-dir",
        _EXPERIMENT_MODULE.DEFAULT_PREFLIGHT_DASHBOARD_OUT_DIR,
    )
    _set_action_default(
        parser,
        "--preflight-schedule-snapshot-path",
        _EXPERIMENT_MODULE.DEFAULT_PREFLIGHT_SCHEDULE_SNAPSHOT_PATH,
    )
    _set_action_default(
        parser,
        "--preflight-schedule-history-path",
        _EXPERIMENT_MODULE.DEFAULT_PREFLIGHT_SCHEDULE_HISTORY_PATH,
    )
    _set_action_default(
        parser,
        "--preflight-schedule-state-path",
        _EXPERIMENT_MODULE.DEFAULT_PREFLIGHT_SCHEDULE_STATE_PATH,
    )
    _set_action_default(parser, "--interval-seconds", 0.0)
    _set_action_default(parser, "--max-cycles", 1)
    parser.add_argument(
        "--experiment-days",
        type=float,
        default=_EXPERIMENT_MODULE.DEFAULT_EXPERIMENT_DAYS,
        help="Declared experiment horizon carried in host-tick artifacts",
    )
    parser.add_argument(
        "--wake-interval-hours",
        type=float,
        default=_EXPERIMENT_MODULE.DEFAULT_WAKE_INTERVAL_HOURS,
        help="Recommended host scheduler interval carried in host-tick artifacts",
    )
    parser.add_argument(
        "--tick-summary-path",
        type=str,
        default=DEFAULT_TICK_SUMMARY_PATH,
        help="Path to write the latest host-driven tick summary JSON",
    )
    parser.add_argument(
        "--fresh-experiment-state",
        action="store_true",
        help="Clear the weekly experiment long-run artifacts before executing this host tick",
    )
    return parser


def _validate_positive(name: str, value: float) -> None:
    if float(value) <= 0:
        raise ValueError(f"{name} must be > 0")


def run_host_tick(args: argparse.Namespace) -> dict[str, object]:
    _validate_positive("experiment_days", args.experiment_days)
    _validate_positive("wake_interval_hours", args.wake_interval_hours)
    if bool(args.fresh_experiment_state):
        _reset_experiment_artifacts(args)
    long_run_args = argparse.Namespace(**vars(args))
    long_run_args.interval_seconds = 0.0
    long_run_args.max_cycles = 1
    payload = _LONG_RUN_MODULE.run_long_run(long_run_args)
    result = {
        "overall_ok": bool(payload.get("overall_ok", True)),
        "experiment": {
            "name": _EXPERIMENT_MODULE.EXPERIMENT_NAME,
            "profile": long_run_args.profile,
            "days": float(args.experiment_days),
            "wake_interval_hours": float(args.wake_interval_hours),
            "host_trigger_mode": "single_tick",
            "max_cycles_per_invocation": 1,
            "interval_seconds": 0.0,
            "fresh_experiment_state": bool(args.fresh_experiment_state),
            "tick_summary_path": str(args.tick_summary_path),
            "experiment_summary_path": _EXPERIMENT_MODULE.DEFAULT_EXPERIMENT_SUMMARY_PATH,
        },
        "gate": payload.get("gate"),
        "preflight": payload.get("preflight"),
        "schedule": payload.get("schedule"),
    }
    _write_json(Path(args.tick_summary_path), summarize_long_run_payload(result) or result)
    return result


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    args = build_parser().parse_args(argv)
    payload = run_host_tick(args)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.strict and not payload.get("overall_ok", True):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
