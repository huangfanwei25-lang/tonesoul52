from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))


def _load_script_module(module_name: str, filename: str):
    path = repo_root / "scripts" / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_SCHEDULE_MODULE = _load_script_module(
    "run_autonomous_registry_schedule_script",
    "run_autonomous_registry_schedule.py",
)
_PREFLIGHT_MODULE = _load_script_module(
    "run_runtime_probe_watch_script",
    "run_runtime_probe_watch.py",
)


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def build_parser() -> argparse.ArgumentParser:
    parser = _SCHEDULE_MODULE.build_parser()
    parser.description = (
        "Run ToneSoul autonomous registry schedule only after a runtime probe succeeds."
    )
    for action in parser._actions:
        if "--llm-probe-timeout-seconds" in getattr(action, "option_strings", []):
            action.default = None
            break
    parser.add_argument(
        "--skip-runtime-probe-watch",
        action="store_true",
        help="Skip runtime_probe_watch gating before the long-running schedule",
    )
    parser.add_argument(
        "--reuse-runtime-probe-state",
        action="store_true",
        help="Reuse prior runtime probe artifacts instead of starting from a fresh preflight sample",
    )
    parser.add_argument(
        "--preflight-history-path",
        type=str,
        default=_PREFLIGHT_MODULE.DEFAULT_HISTORY_PATH,
        help="Path to append runtime probe wake-up history JSONL rows",
    )
    parser.add_argument(
        "--preflight-snapshot-path",
        type=str,
        default=_PREFLIGHT_MODULE.DEFAULT_SNAPSHOT_PATH,
        help="Path to write the latest runtime probe wake-up snapshot JSON",
    )
    parser.add_argument(
        "--preflight-dashboard-out-dir",
        type=str,
        default=_PREFLIGHT_MODULE.DEFAULT_DASHBOARD_OUT_DIR,
        help="Directory for runtime probe dream observability artifacts",
    )
    parser.add_argument(
        "--preflight-schedule-snapshot-path",
        type=str,
        default=_PREFLIGHT_MODULE.DEFAULT_SCHEDULE_SNAPSHOT_PATH,
        help="Path to write the latest runtime probe schedule snapshot JSON",
    )
    parser.add_argument(
        "--preflight-schedule-history-path",
        type=str,
        default=_PREFLIGHT_MODULE.DEFAULT_SCHEDULE_HISTORY_PATH,
        help="Path to append runtime probe schedule cycle history JSONL rows",
    )
    parser.add_argument(
        "--preflight-schedule-state-path",
        type=str,
        default=_PREFLIGHT_MODULE.DEFAULT_SCHEDULE_STATE_PATH,
        help="Path to persisted runtime probe schedule state JSON",
    )
    parser.add_argument(
        "--preflight-interval-seconds",
        type=float,
        default=0.0,
        help="Seconds between runtime probe schedule ticks",
    )
    parser.add_argument(
        "--preflight-max-cycles",
        type=int,
        default=2,
        help="Number of runtime probe schedule ticks to execute before the long run",
    )
    parser.add_argument(
        "--preflight-llm-probe-timeout-seconds",
        type=float,
        default=2.0,
        help="Timeout for the runtime probe bounded inference-readiness check",
    )
    return parser


def _build_preflight_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        db_path=args.db_path,
        crystal_path=args.crystal_path,
        journal_path=args.journal_path,
        registry_path=args.registry_path,
        profile_path=args.profile_path,
        history_path=args.preflight_history_path,
        snapshot_path=args.preflight_snapshot_path,
        dashboard_out_dir=args.preflight_dashboard_out_dir,
        schedule_snapshot_path=args.preflight_schedule_snapshot_path,
        schedule_history_path=args.preflight_schedule_history_path,
        schedule_state_path=args.preflight_schedule_state_path,
        interval_seconds=args.preflight_interval_seconds,
        max_cycles=args.preflight_max_cycles,
        limit=None,
        min_priority=None,
        related_limit=None,
        crystal_count=None,
        no_llm=False,
        skip_llm_preflight=False,
        llm_probe_timeout_seconds=args.preflight_llm_probe_timeout_seconds,
        strict=True,
        reuse_state=bool(args.reuse_runtime_probe_state),
    )


def run_long_run(args: argparse.Namespace) -> dict[str, object]:
    preflight_payload: dict[str, object] | None = None
    gate: dict[str, object]
    schedule_args = argparse.Namespace(**vars(args))

    if bool(args.no_llm):
        gate = {
            "status": "skipped",
            "reason": "llm_disabled",
            "profile": _PREFLIGHT_MODULE.PROFILE_NAME,
        }
    elif bool(args.skip_runtime_probe_watch):
        gate = {
            "status": "skipped",
            "reason": "operator_override",
            "profile": _PREFLIGHT_MODULE.PROFILE_NAME,
        }
    else:
        preflight_payload = _PREFLIGHT_MODULE.run_runtime_probe(_build_preflight_args(args))
        if not bool(preflight_payload.get("overall_ok", True)):
            return {
                "overall_ok": False,
                "gate": {
                    "status": "blocked",
                    "reason": "runtime_probe_failed",
                    "profile": _PREFLIGHT_MODULE.PROFILE_NAME,
                },
                "preflight": preflight_payload,
                "schedule": None,
            }
        gate = {
            "status": "passed",
            "reason": "runtime_probe_ok",
            "profile": _PREFLIGHT_MODULE.PROFILE_NAME,
        }
        if getattr(schedule_args, "llm_probe_timeout_seconds", None) is None:
            schedule_args.llm_probe_timeout_seconds = float(
                args.preflight_llm_probe_timeout_seconds
            )

    if getattr(schedule_args, "llm_probe_timeout_seconds", None) is None:
        schedule_args.llm_probe_timeout_seconds = float(args.preflight_llm_probe_timeout_seconds)

    schedule_payload = _SCHEDULE_MODULE.run_schedule(schedule_args)
    return {
        "overall_ok": bool(schedule_payload.get("overall_ok", True)),
        "gate": gate,
        "preflight": preflight_payload,
        "schedule": schedule_payload,
    }


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    args = build_parser().parse_args(argv)
    payload = run_long_run(args)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.strict and not payload.get("overall_ok", True):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
