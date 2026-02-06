from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure we can import repository modules when executed directly.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.agent_discussion import (
    DEFAULT_DISCUSSION_PATH,
    append_entry,
    audit_file,
    load_entries,
    normalize_file,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agent discussion channel utility.")
    sub = parser.add_subparsers(dest="command", required=True)

    audit = sub.add_parser("audit", help="Audit discussion file.")
    audit.add_argument("--path", default=str(DEFAULT_DISCUSSION_PATH))
    audit.add_argument("--sample-limit", type=int, default=5)

    normalize = sub.add_parser("normalize", help="Normalize discussion JSONL.")
    normalize.add_argument("--path", default=str(DEFAULT_DISCUSSION_PATH))
    normalize.add_argument(
        "--no-backup",
        action="store_true",
        help="Do not write backup file before rewrite.",
    )
    normalize.add_argument(
        "--drop-invalid",
        action="store_true",
        help="Drop invalid lines instead of preserving them as system records.",
    )

    append = sub.add_parser("append", help="Append one normalized discussion entry.")
    append.add_argument("--path", default=str(DEFAULT_DISCUSSION_PATH))
    append.add_argument("--author", required=True)
    append.add_argument("--topic", required=True)
    append.add_argument("--status", default="noted")
    append.add_argument("--message", required=True)

    tail = sub.add_parser("tail", help="Show recent discussion entries.")
    tail.add_argument("--path", default=str(DEFAULT_DISCUSSION_PATH))
    tail.add_argument("--limit", type=int, default=10)
    tail.add_argument(
        "--include-invalid",
        action="store_true",
        help="Include invalid lines as synthetic records.",
    )

    return parser


def _emit(payload: Dict[str, Any]) -> int:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))
    return 0


def _cmd_audit(path: Path, sample_limit: int) -> int:
    payload = audit_file(path=path, sample_limit=max(1, sample_limit))
    return _emit(payload)


def _cmd_normalize(path: Path, no_backup: bool, drop_invalid: bool) -> int:
    payload = normalize_file(
        path=path,
        create_backup=not no_backup,
        keep_invalid=not drop_invalid,
    )
    return _emit(payload)


def _cmd_append(path: Path, author: str, topic: str, status: str, message: str) -> int:
    entry = append_entry(
        {
            "author": author,
            "topic": topic,
            "status": status,
            "message": message,
        },
        path=path,
    )
    return _emit({"path": str(path), "appended": entry})


def _cmd_tail(path: Path, limit: int, include_invalid: bool) -> int:
    entries: List[Dict[str, Any]] = load_entries(path=path, include_invalid=include_invalid)
    safe_limit = max(0, limit)
    if safe_limit:
        entries = entries[-safe_limit:]
    else:
        entries = []
    return _emit({"path": str(path), "count": len(entries), "entries": entries})


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    command = args.command
    path = Path(args.path)

    if command == "audit":
        return _cmd_audit(path=path, sample_limit=args.sample_limit)
    if command == "normalize":
        return _cmd_normalize(path=path, no_backup=args.no_backup, drop_invalid=args.drop_invalid)
    if command == "append":
        return _cmd_append(
            path=path,
            author=args.author,
            topic=args.topic,
            status=args.status,
            message=args.message,
        )
    if command == "tail":
        return _cmd_tail(path=path, limit=args.limit, include_invalid=args.include_invalid)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
