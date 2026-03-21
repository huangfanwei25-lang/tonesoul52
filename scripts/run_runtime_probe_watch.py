from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

PROFILE_NAME = "runtime_probe_watch"
DEFAULT_HISTORY_PATH = "memory/autonomous/runtime_probe_watch/dream_wakeup_history.jsonl"
DEFAULT_SNAPSHOT_PATH = "docs/status/runtime_probe_watch/dream_wakeup_snapshot.json"
DEFAULT_DASHBOARD_OUT_DIR = "docs/status/runtime_probe_watch"
DEFAULT_SCHEDULE_SNAPSHOT_PATH = (
    "docs/status/runtime_probe_watch/autonomous_registry_schedule_latest.json"
)
DEFAULT_SCHEDULE_HISTORY_PATH = (
    "memory/autonomous/runtime_probe_watch/registry_schedule_history.jsonl"
)
DEFAULT_SCHEDULE_STATE_PATH = "memory/autonomous/runtime_probe_watch/registry_schedule_state.json"
DEFAULT_DASHBOARD_JSON_PATH = "dream_observability_latest.json"
DEFAULT_DASHBOARD_HTML_PATH = "dream_observability_latest.html"


def _load_schedule_module():
    path = repo_root / "scripts" / "run_autonomous_registry_schedule.py"
    spec = importlib.util.spec_from_file_location("run_autonomous_registry_schedule_script", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_SCHEDULE_MODULE = _load_schedule_module()


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


def _reset_probe_artifacts(args: argparse.Namespace) -> None:
    _reset_file(Path(args.history_path))
    _reset_file(Path(args.snapshot_path))
    _reset_file(Path(args.schedule_snapshot_path))
    _reset_file(Path(args.schedule_history_path))
    _reset_file(Path(args.schedule_state_path))
    dashboard_dir = Path(args.dashboard_out_dir)
    _reset_file(dashboard_dir / DEFAULT_DASHBOARD_JSON_PATH)
    _reset_file(dashboard_dir / DEFAULT_DASHBOARD_HTML_PATH)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the governed ToneSoul runtime preflight using runtime_probe_watch."
    )
    parser.add_argument("--db-path", type=str, default=None, help="Path to soul.db")
    parser.add_argument(
        "--crystal-path", type=str, default=None, help="Path to crystals.jsonl override"
    )
    parser.add_argument(
        "--journal-path",
        type=str,
        default="memory/self_journal.jsonl",
        help="Path to self_journal JSONL",
    )
    parser.add_argument(
        "--registry-path",
        type=str,
        default="spec/external_source_registry.yaml",
        help="Curated external source registry YAML path",
    )
    parser.add_argument(
        "--profile-path",
        type=str,
        default="spec/registry_schedule_profiles.yaml",
        help="Schedule profile YAML path",
    )
    parser.add_argument(
        "--history-path",
        type=str,
        default=DEFAULT_HISTORY_PATH,
        help="Path to append wake-up history JSONL rows",
    )
    parser.add_argument(
        "--snapshot-path",
        type=str,
        default=DEFAULT_SNAPSHOT_PATH,
        help="Path to write the latest wake-up snapshot JSON",
    )
    parser.add_argument(
        "--dashboard-out-dir",
        type=str,
        default=DEFAULT_DASHBOARD_OUT_DIR,
        help="Directory for dream observability artifacts",
    )
    parser.add_argument(
        "--schedule-snapshot-path",
        type=str,
        default=DEFAULT_SCHEDULE_SNAPSHOT_PATH,
        help="Path to write the latest schedule snapshot JSON",
    )
    parser.add_argument(
        "--schedule-history-path",
        type=str,
        default=DEFAULT_SCHEDULE_HISTORY_PATH,
        help="Path to append schedule cycle history JSONL rows",
    )
    parser.add_argument(
        "--schedule-state-path",
        type=str,
        default=DEFAULT_SCHEDULE_STATE_PATH,
        help="Path to persisted schedule cursor state JSON",
    )
    parser.add_argument(
        "--interval-seconds",
        type=float,
        default=0.0,
        help="Seconds between schedule ticks during the preflight run",
    )
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=2,
        help="Number of schedule ticks to execute for runtime verification",
    )
    parser.add_argument("--limit", type=int, default=None, help="Dream stimulus selection limit")
    parser.add_argument(
        "--min-priority",
        type=float,
        default=None,
        help="Minimum priority score for DreamEngine selection",
    )
    parser.add_argument(
        "--related-limit",
        type=int,
        default=None,
        help="Maximum related memories per collision",
    )
    parser.add_argument(
        "--crystal-count",
        type=int,
        default=None,
        help="Maximum crystal rules used by DreamEngine",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM reflection generation",
    )
    parser.add_argument(
        "--skip-llm-preflight",
        action="store_true",
        help="Skip bounded inference-readiness probe before reflection generation",
    )
    parser.add_argument(
        "--llm-probe-timeout-seconds",
        type=float,
        default=2.0,
        help="Timeout for the bounded LLM inference-readiness probe",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero if the runtime preflight is not fully OK",
    )
    parser.add_argument(
        "--reuse-state",
        action="store_true",
        help="Reuse existing runtime probe state/history instead of starting from a fresh preflight sample",
    )
    return parser


def _build_schedule_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        db_path=args.db_path,
        crystal_path=args.crystal_path,
        journal_path=args.journal_path,
        history_path=args.history_path,
        snapshot_path=args.snapshot_path,
        dashboard_out_dir=args.dashboard_out_dir,
        registry_path=args.registry_path,
        profile_path=args.profile_path,
        profile=PROFILE_NAME,
        registry_id=[],
        registry_category=[],
        entries_per_cycle=None,
        urls_per_cycle=None,
        revisit_interval_cycles=None,
        failure_backoff_cycles=None,
        category_weight=[],
        category_backoff_multiplier=[],
        tension_max_friction_score=None,
        tension_max_lyapunov_proxy=None,
        tension_max_council_count=None,
        tension_max_llm_preflight_latency_ms=None,
        tension_max_llm_selection_latency_ms=None,
        tension_max_llm_probe_latency_ms=None,
        tension_max_llm_timeout_count=None,
        tension_cooldown_cycles=None,
        allow_stale_registry=None,
        schedule_state_path=args.schedule_state_path,
        schedule_snapshot_path=args.schedule_snapshot_path,
        schedule_history_path=args.schedule_history_path,
        interval_seconds=args.interval_seconds,
        max_cycles=args.max_cycles,
        limit=args.limit,
        min_priority=args.min_priority,
        related_limit=args.related_limit,
        crystal_count=args.crystal_count,
        no_llm=args.no_llm,
        skip_llm_preflight=args.skip_llm_preflight,
        llm_probe_timeout_seconds=args.llm_probe_timeout_seconds,
        strict=args.strict,
    )


def run_runtime_probe(args: argparse.Namespace) -> dict[str, object]:
    if not bool(args.reuse_state):
        _reset_probe_artifacts(args)
    payload = _SCHEDULE_MODULE.run_schedule(_build_schedule_args(args))
    payload["preflight_profile"] = PROFILE_NAME
    _write_json(Path(args.schedule_snapshot_path), payload)
    return payload


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    args = build_parser().parse_args(argv)
    payload = run_runtime_probe(args)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.strict and not payload.get("overall_ok", True):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
