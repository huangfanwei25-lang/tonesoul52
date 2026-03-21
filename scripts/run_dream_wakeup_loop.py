from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from tonesoul.wakeup_loop import build_autonomous_wakeup_loop  # noqa: E402


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _append_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _derive_overall_status(results: list[dict[str, Any]]) -> str:
    statuses = [str(item.get("status") or "") for item in results]
    unique_statuses = {status for status in statuses if status}
    if not unique_statuses:
        return "idle"
    if len(unique_statuses) == 1:
        return next(iter(unique_statuses))
    return "mixed"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run ToneSoul autonomous Dream wake-up loop")
    parser.add_argument("--db-path", type=str, default=None, help="Path to soul.db")
    parser.add_argument(
        "--crystal-path", type=str, default=None, help="Path to crystals.jsonl override"
    )
    parser.add_argument(
        "--interval-seconds",
        type=float,
        default=10800.0,
        help="Seconds to sleep between cycles",
    )
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=1,
        help="Maximum number of cycles to execute in this process",
    )
    parser.add_argument("--limit", type=int, default=3, help="Number of stimuli to process")
    parser.add_argument(
        "--min-priority",
        type=float,
        default=0.35,
        help="Minimum priority score for selecting a stimulus",
    )
    parser.add_argument(
        "--related-limit",
        type=int,
        default=5,
        help="Maximum number of related memories to recall",
    )
    parser.add_argument(
        "--crystal-count",
        type=int,
        default=5,
        help="Maximum number of durable rules to use",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM reflection generation and use deterministic fallback only",
    )
    parser.add_argument(
        "--skip-llm-preflight",
        action="store_true",
        help="Skip bounded inference-readiness probe before reflection generation",
    )
    parser.add_argument(
        "--llm-probe-timeout-seconds",
        type=float,
        default=10.0,
        help="Timeout for the bounded LLM inference-readiness probe",
    )
    parser.add_argument(
        "--consolidate-every-cycles",
        type=int,
        default=3,
        help="Run sleep consolidation after every N successful wake-up cycles (0 disables).",
    )
    parser.add_argument(
        "--failure-threshold",
        type=int,
        default=3,
        help="Pause after this many consecutive Dream Engine failures.",
    )
    parser.add_argument(
        "--failure-pause-seconds",
        type=float,
        default=3600.0,
        help="Seconds to pause after the failure threshold is reached.",
    )
    parser.add_argument(
        "--snapshot-path",
        type=str,
        default=None,
        help="Optional path to write the full JSON snapshot",
    )
    parser.add_argument(
        "--history-path",
        type=str,
        default=None,
        help="Optional path to append per-cycle JSONL rows",
    )
    return parser


def run_wakeup_loop(args: argparse.Namespace) -> dict[str, object]:
    loop = build_autonomous_wakeup_loop(
        db_path=Path(args.db_path) if args.db_path else None,
        crystal_path=Path(args.crystal_path) if args.crystal_path else None,
        interval_seconds=args.interval_seconds,
        consolidate_every_cycles=args.consolidate_every_cycles,
        failure_threshold=args.failure_threshold,
        failure_pause_seconds=args.failure_pause_seconds,
    )
    dream_kwargs = {
        "limit": args.limit,
        "min_priority": args.min_priority,
        "related_limit": args.related_limit,
        "crystal_count": args.crystal_count,
        "generate_reflection": not bool(args.no_llm),
        "require_inference_ready": not bool(args.no_llm or args.skip_llm_preflight),
        "inference_timeout_seconds": float(args.llm_probe_timeout_seconds),
    }
    cycle_results = loop.run(max_cycles=args.max_cycles, dream_kwargs=dream_kwargs)
    results_payload = [result.to_dict() for result in cycle_results]
    payload: dict[str, object] = {
        "generated_at": _iso_now(),
        "overall_status": _derive_overall_status(results_payload),
        "config": {
            "interval_seconds": float(args.interval_seconds),
            "max_cycles": int(args.max_cycles),
            "limit": int(args.limit),
            "min_priority": float(args.min_priority),
            "related_limit": int(args.related_limit),
            "crystal_count": int(args.crystal_count),
            "generate_reflection": not bool(args.no_llm),
            "require_inference_ready": not bool(args.no_llm or args.skip_llm_preflight),
            "llm_probe_timeout_seconds": float(args.llm_probe_timeout_seconds),
            "consolidate_every_cycles": int(args.consolidate_every_cycles),
            "failure_threshold": int(args.failure_threshold),
            "failure_pause_seconds": float(args.failure_pause_seconds),
        },
        "results": results_payload,
    }

    if args.snapshot_path:
        _write_json(Path(args.snapshot_path), payload)
    if args.history_path:
        _append_jsonl(Path(args.history_path), results_payload)
    return payload


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    payload = run_wakeup_loop(args)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
