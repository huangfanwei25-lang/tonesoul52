from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from tonesoul.autonomous_cycle import build_autonomous_cycle_runner  # noqa: E402
from tonesoul.perception.source_registry import select_curated_registry_urls  # noqa: E402


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def _read_url_file(path: str | None) -> list[str]:
    if not path:
        return []
    file_path = Path(path)
    if not file_path.exists():
        return []
    urls: list[str] = []
    with file_path.open("r", encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            urls.append(line)
    return urls


def _merge_unique_urls(*groups: list[str]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for raw in group:
            url = str(raw).strip()
            if not url or url in seen:
                continue
            seen.add(url)
            merged.append(url)
    return merged


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one autonomous ToneSoul dream cycle.")
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
        "--history-path",
        type=str,
        default="memory/autonomous/dream_wakeup_history.jsonl",
        help="Path to append wake-up history JSONL rows",
    )
    parser.add_argument(
        "--snapshot-path",
        type=str,
        default="docs/status/dream_wakeup_snapshot_latest.json",
        help="Path to write the latest wake-up snapshot JSON",
    )
    parser.add_argument(
        "--state-path",
        type=str,
        default="memory/autonomous/dream_wakeup_state.json",
        help="Path to persisted wake-up runtime state JSON",
    )
    parser.add_argument(
        "--dashboard-out-dir",
        type=str,
        default="docs/status",
        help="Directory for dream observability artifacts",
    )
    parser.add_argument(
        "--interval-seconds",
        type=float,
        default=0.0,
        help="Seconds between cycles when max-cycles > 1",
    )
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=1,
        help="Number of wake-up cycles to execute in this run",
    )
    parser.add_argument(
        "--url",
        action="append",
        default=[],
        help="URL to ingest before running the wake-up loop (repeatable)",
    )
    parser.add_argument(
        "--url-file",
        type=str,
        default=None,
        help="Optional newline-delimited URL file",
    )
    parser.add_argument(
        "--registry-path",
        type=str,
        default=None,
        help="Optional curated external source registry YAML path",
    )
    parser.add_argument(
        "--registry-id",
        action="append",
        default=[],
        help="Registry entry id to include (repeatable)",
    )
    parser.add_argument(
        "--registry-category",
        action="append",
        default=[],
        help="Registry category to include (repeatable)",
    )
    parser.add_argument(
        "--registry-limit",
        type=int,
        default=None,
        help="Maximum curated registry URLs to include before ingestion",
    )
    parser.add_argument(
        "--allow-stale-registry",
        action="store_true",
        help="Allow stale reviewed registry entries to be selected",
    )
    parser.add_argument("--limit", type=int, default=3, help="Dream stimulus selection limit")
    parser.add_argument(
        "--min-priority",
        type=float,
        default=0.35,
        help="Minimum priority score for DreamEngine selection",
    )
    parser.add_argument(
        "--related-limit",
        type=int,
        default=5,
        help="Maximum related memories per collision",
    )
    parser.add_argument(
        "--crystal-count",
        type=int,
        default=5,
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
        default=10.0,
        help="Timeout for the bounded LLM inference-readiness probe",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero if ingestion or downstream artifact generation is not fully OK",
    )
    parser.add_argument(
        "--disable-scribe",
        action="store_true",
        help="Disable post-cycle Scribe chronicle generation inside the wake-up runner.",
    )
    parser.add_argument(
        "--scribe-out-dir",
        type=str,
        default="docs/chronicles",
        help="Directory for Scribe chronicle markdown/companion outputs.",
    )
    parser.add_argument(
        "--scribe-status-path",
        type=str,
        default="docs/status/scribe_status_latest.json",
        help="Path for the compact latest Scribe status artifact.",
    )
    parser.add_argument(
        "--scribe-state-path",
        type=str,
        default="memory/autonomous/dream_wakeup_scribe_state.json",
        help="Path to persisted Scribe dedupe state JSON.",
    )
    return parser


def run_cycle(args: argparse.Namespace) -> dict[str, object]:
    runner = build_autonomous_cycle_runner(
        db_path=Path(args.db_path) if args.db_path else None,
        crystal_path=Path(args.crystal_path) if args.crystal_path else None,
        journal_path=Path(args.journal_path),
        history_path=Path(args.history_path),
        snapshot_path=Path(args.snapshot_path),
        state_path=Path(args.state_path),
        dashboard_out_dir=Path(args.dashboard_out_dir),
        interval_seconds=args.interval_seconds,
        enable_scribe=not bool(args.disable_scribe),
        scribe_out_dir=Path(args.scribe_out_dir),
        scribe_status_path=Path(args.scribe_status_path),
        scribe_state_path=Path(args.scribe_state_path),
    )
    explicit_urls = [str(url).strip() for url in args.url if str(url).strip()]
    file_urls = _read_url_file(args.url_file)
    registry_selection = None
    registry_urls: list[str] = []
    if args.registry_path:
        registry_selection = select_curated_registry_urls(
            Path(args.registry_path),
            entry_ids=args.registry_id,
            categories=args.registry_category,
            limit=args.registry_limit,
            include_stale=bool(args.allow_stale_registry),
        )
        registry_urls = list(registry_selection.selected_urls)
    urls = _merge_unique_urls(explicit_urls, file_urls, registry_urls)
    result = runner.run(
        urls=urls,
        max_cycles=args.max_cycles,
        limit=args.limit,
        min_priority=args.min_priority,
        related_limit=args.related_limit,
        crystal_count=args.crystal_count,
        generate_reflection=not bool(args.no_llm),
        require_inference_ready=not bool(args.no_llm or args.skip_llm_preflight),
        inference_timeout_seconds=float(args.llm_probe_timeout_seconds),
    )
    payload = result.to_dict()
    if registry_selection is not None:
        payload["registry_selection"] = registry_selection.to_dict()
        payload["overall_ok"] = bool(payload.get("overall_ok", True)) and bool(
            registry_selection.ok
        )
    return payload


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    payload = run_cycle(args)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.strict and not payload.get("overall_ok", True):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
