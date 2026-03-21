from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from tonesoul.dream_observability import (  # noqa: E402
    HTML_FILENAME,
    JSON_FILENAME,
    build_dashboard,
    render_html,
)


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate ToneSoul Dream observability dashboard artifacts."
    )
    parser.add_argument(
        "--journal-path",
        default="memory/self_journal.jsonl",
        help="Path to self_journal JSONL.",
    )
    parser.add_argument(
        "--wakeup-path",
        default="memory/autonomous/dream_wakeup_history.jsonl",
        help="Path to wake-up history JSONL or snapshot JSON.",
    )
    parser.add_argument(
        "--schedule-history-path",
        default=None,
        help="Optional path to schedule history JSONL or snapshot JSON.",
    )
    parser.add_argument(
        "--schedule-state-path",
        default=None,
        help="Optional path to schedule state JSON.",
    )
    parser.add_argument(
        "--out-dir",
        default="docs/status",
        help="Output directory for dashboard artifacts.",
    )
    parser.add_argument(
        "--max-points",
        type=int,
        default=120,
        help="Maximum number of points retained per chart.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero if invalid JSON lines or malformed history are detected.",
    )
    return parser


def run_dashboard(args: argparse.Namespace) -> dict[str, Any]:
    payload = build_dashboard(
        journal_path=Path(args.journal_path),
        wakeup_path=Path(args.wakeup_path),
        schedule_history_path=(
            None if args.schedule_history_path in (None, "") else Path(args.schedule_history_path)
        ),
        schedule_state_path=(
            None if args.schedule_state_path in (None, "") else Path(args.schedule_state_path)
        ),
        max_points=args.max_points,
    )
    out_dir = Path(args.out_dir)
    _write_json(out_dir / JSON_FILENAME, payload)
    _write_text(out_dir / HTML_FILENAME, render_html(payload))
    return payload


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    payload = run_dashboard(args)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.strict and not payload.get("overall_ok", True):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
