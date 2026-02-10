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
    DEFAULT_DISCUSSION_CURATED_PATH,
    DEFAULT_DISCUSSION_PATH,
    append_entry,
    audit_file,
    format_lessons_message,
    load_entries,
    normalize_file,
    rebuild_curated,
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
        "--curated-path",
        default=str(DEFAULT_DISCUSSION_CURATED_PATH),
        help="Curated discussion path to rebuild after normalize.",
    )
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
    append.add_argument(
        "--curated-path",
        default=str(DEFAULT_DISCUSSION_CURATED_PATH),
        help="Curated discussion path for mirrored writes.",
    )
    append.add_argument("--author", required=True)
    append.add_argument("--topic", required=True)
    append.add_argument("--status", default="noted")
    append.add_argument("--message", required=True)

    append_lessons = sub.add_parser(
        "append-lessons",
        help="Append one standardized lessons-learned entry (LESSONS_V1).",
    )
    append_lessons.add_argument("--path", default=str(DEFAULT_DISCUSSION_PATH))
    append_lessons.add_argument(
        "--curated-path",
        default=str(DEFAULT_DISCUSSION_CURATED_PATH),
        help="Curated discussion path for mirrored writes.",
    )
    append_lessons.add_argument("--author", required=True)
    append_lessons.add_argument("--topic", required=True)
    append_lessons.add_argument("--status", default="done")
    append_lessons.add_argument("--summary", required=True)
    append_lessons.add_argument(
        "--missed",
        action="append",
        required=True,
        help="Missed item. Repeat the flag for multiple items.",
    )
    append_lessons.add_argument(
        "--cause",
        action="append",
        default=[],
        help="Root cause item. Repeat the flag for multiple items.",
    )
    append_lessons.add_argument(
        "--correction",
        action="append",
        required=True,
        help="Correction item. Repeat the flag for multiple items.",
    )
    append_lessons.add_argument(
        "--guardrail",
        action="append",
        default=[],
        help="Guardrail rule. Repeat the flag for multiple items.",
    )
    append_lessons.add_argument(
        "--evidence",
        action="append",
        default=[],
        help="Evidence item. Repeat the flag for multiple items.",
    )
    append_lessons.add_argument(
        "--signature",
        default="",
        help="Optional signature string, e.g. signed_by=codex(gpt-5).",
    )

    curate = sub.add_parser("curate", help="Rebuild curated stream from raw discussion.")
    curate.add_argument("--path", default=str(DEFAULT_DISCUSSION_PATH))
    curate.add_argument(
        "--curated-path",
        default=str(DEFAULT_DISCUSSION_CURATED_PATH),
        help="Destination path for curated stream.",
    )
    curate.add_argument(
        "--no-backup",
        action="store_true",
        help="Do not write backup for curated file before rewrite.",
    )

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


def _cmd_normalize(path: Path, curated_path: Path, no_backup: bool, drop_invalid: bool) -> int:
    payload = normalize_file(
        path=path,
        create_backup=not no_backup,
        keep_invalid=not drop_invalid,
        curated_path=curated_path,
    )
    return _emit(payload)


def _cmd_append(
    path: Path,
    curated_path: Path,
    author: str,
    topic: str,
    status: str,
    message: str,
) -> int:
    try:
        entry = append_entry(
            {
                "author": author,
                "topic": topic,
                "status": status,
                "message": message,
            },
            path=path,
            curated_path=curated_path,
        )
    except (TypeError, ValueError) as exc:
        _emit({"path": str(path), "error": str(exc)})
        return 1
    return _emit({"path": str(path), "curated_path": str(curated_path), "appended": entry})


def _cmd_append_lessons(
    path: Path,
    curated_path: Path,
    author: str,
    topic: str,
    status: str,
    summary: str,
    missed: List[str],
    cause: List[str],
    correction: List[str],
    guardrail: List[str],
    evidence: List[str],
    signature: str,
) -> int:
    try:
        message = format_lessons_message(
            summary=summary,
            missed=missed,
            causes=cause,
            corrections=correction,
            guardrails=guardrail,
            evidence=evidence,
            signature=signature,
        )
    except ValueError as exc:
        _emit({"path": str(path), "error": str(exc)})
        return 1
    return _cmd_append(
        path=path,
        curated_path=curated_path,
        author=author,
        topic=topic,
        status=status,
        message=message,
    )


def _cmd_curate(path: Path, curated_path: Path, no_backup: bool) -> int:
    payload = rebuild_curated(
        raw_path=path,
        curated_path=curated_path,
        create_backup=not no_backup,
    )
    return _emit(payload)


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
        return _cmd_normalize(
            path=path,
            curated_path=Path(args.curated_path),
            no_backup=args.no_backup,
            drop_invalid=args.drop_invalid,
        )
    if command == "append":
        return _cmd_append(
            path=path,
            curated_path=Path(args.curated_path),
            author=args.author,
            topic=args.topic,
            status=args.status,
            message=args.message,
        )
    if command == "append-lessons":
        return _cmd_append_lessons(
            path=path,
            curated_path=Path(args.curated_path),
            author=args.author,
            topic=args.topic,
            status=args.status,
            summary=args.summary,
            missed=args.missed,
            cause=args.cause,
            correction=args.correction,
            guardrail=args.guardrail,
            evidence=args.evidence,
            signature=args.signature,
        )
    if command == "curate":
        return _cmd_curate(
            path=path,
            curated_path=Path(args.curated_path),
            no_backup=args.no_backup,
        )
    if command == "tail":
        return _cmd_tail(path=path, limit=args.limit, include_invalid=args.include_invalid)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
