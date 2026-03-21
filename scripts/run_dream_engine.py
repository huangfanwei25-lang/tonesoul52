from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from tonesoul.dream_engine import build_dream_engine  # noqa: E402


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run ToneSoul Dream Engine")
    parser.add_argument("--db-path", type=str, default=None, help="Path to soul.db")
    parser.add_argument(
        "--crystal-path", type=str, default=None, help="Path to crystals.jsonl override"
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
    return parser


def run_engine(args: argparse.Namespace) -> dict[str, object]:
    engine = build_dream_engine(
        db_path=Path(args.db_path) if args.db_path else None,
        crystal_path=Path(args.crystal_path) if args.crystal_path else None,
    )
    result = engine.run_cycle(
        limit=args.limit,
        min_priority=args.min_priority,
        related_limit=args.related_limit,
        crystal_count=args.crystal_count,
        generate_reflection=not bool(args.no_llm),
        require_inference_ready=not bool(args.no_llm or args.skip_llm_preflight),
        inference_timeout_seconds=float(args.llm_probe_timeout_seconds),
    )
    return result.to_dict()


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    payload = run_engine(args)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
