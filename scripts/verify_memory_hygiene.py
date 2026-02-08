"""
Memory hygiene verifier.

Checks:
1. Selected files are valid UTF-8 and do not start with BOM.
2. Recent lines in discussion channel are strict JSON objects
   with required fields.
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
from typing import Any

DEFAULT_TARGETS = (
    ".github/workflows/*.yml",
    "apps/api/server.py",
    "memory/agent_discussion.py",
    "scripts/verify_7d.py",
    "scripts/verify_web_api.py",
    "scripts/verify_memory_hygiene.py",
    "tests/red_team/**/*.py",
    "tools/agent_discussion_tool.py",
)
DEFAULT_DISCUSSION_PATH = "memory/agent_discussion.jsonl"
REQUIRED_DISCUSSION_FIELDS = ("timestamp", "author", "topic", "status", "message")
UTF8_BOM = b"\xef\xbb\xbf"


def _has_glob_token(pattern: str) -> bool:
    return any(token in pattern for token in ("*", "?", "["))


def _expand_targets(patterns: list[str]) -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    missing_literals: list[str] = []
    seen: set[Path] = set()

    for pattern in patterns:
        matches = sorted(glob.glob(pattern, recursive=True))
        if matches:
            for match in matches:
                candidate = Path(match)
                if candidate.is_file() and candidate not in seen:
                    seen.add(candidate)
                    files.append(candidate)
            continue
        if not _has_glob_token(pattern):
            missing_literals.append(pattern)

    return files, missing_literals


def _check_utf8_no_bom(paths: list[Path]) -> dict[str, Any]:
    bom_files: list[str] = []
    decode_errors: list[dict[str, str]] = []

    for path in paths:
        raw = path.read_bytes()
        if raw.startswith(UTF8_BOM):
            bom_files.append(path.as_posix())
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            decode_errors.append({"path": path.as_posix(), "error": str(exc)})

    return {
        "files_scanned": len(paths),
        "bom_files": bom_files,
        "decode_errors": decode_errors,
    }


def _validate_discussion_entry(entry: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for field in REQUIRED_DISCUSSION_FIELDS:
        value = entry.get(field)
        if not isinstance(value, str) or not value.strip():
            missing.append(field)
    return missing


def _check_discussion_tail(path: Path, tail_lines: int) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": path.as_posix(),
            "exists": False,
            "tail_checked": 0,
            "invalid_json": [],
            "missing_fields": [],
        }

    raw = path.read_bytes()
    if raw.startswith(UTF8_BOM):
        bom = True
    else:
        bom = False

    text = raw.decode("utf-8", errors="replace")
    non_empty_lines = [line.strip() for line in text.splitlines() if line.strip()]
    tail = non_empty_lines[-max(1, tail_lines) :]
    invalid_json: list[dict[str, Any]] = []
    missing_fields: list[dict[str, Any]] = []

    start_line = len(non_empty_lines) - len(tail) + 1
    for idx, line in enumerate(tail, start=start_line):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            invalid_json.append({"line_number": idx, "reason": str(exc)})
            continue
        if not isinstance(payload, dict):
            invalid_json.append({"line_number": idx, "reason": "JSON root is not an object"})
            continue
        missing = _validate_discussion_entry(payload)
        if missing:
            missing_fields.append({"line_number": idx, "missing_fields": missing})

    return {
        "path": path.as_posix(),
        "exists": True,
        "bom": bom,
        "tail_checked": len(tail),
        "invalid_json": invalid_json,
        "missing_fields": missing_fields,
    }


def _build_report(
    targets: list[str],
    discussion_path: Path,
    tail_lines: int,
    allow_missing_discussion: bool,
) -> dict[str, Any]:
    files, missing_literals = _expand_targets(targets)
    file_report = _check_utf8_no_bom(files)
    discussion_report = _check_discussion_tail(discussion_path, tail_lines)
    discussion_ok = (
        discussion_report["exists"]
        and not discussion_report.get("bom", False)
        and len(discussion_report["invalid_json"]) == 0
        and len(discussion_report["missing_fields"]) == 0
    )
    if allow_missing_discussion and not discussion_report["exists"]:
        discussion_ok = True

    ok = (
        len(missing_literals) == 0
        and len(file_report["bom_files"]) == 0
        and len(file_report["decode_errors"]) == 0
        and discussion_ok
    )

    return {
        "ok": ok,
        "targets": targets,
        "allow_missing_discussion": allow_missing_discussion,
        "missing_literal_paths": missing_literals,
        "file_hygiene": file_report,
        "discussion_tail": discussion_report,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify memory/channel hygiene checks.")
    parser.add_argument(
        "--targets",
        nargs="*",
        default=list(DEFAULT_TARGETS),
        help="File/glob targets for UTF-8 no-BOM checks.",
    )
    parser.add_argument(
        "--discussion-path",
        default=DEFAULT_DISCUSSION_PATH,
        help="Discussion JSONL path.",
    )
    parser.add_argument(
        "--tail-lines",
        type=int,
        default=200,
        help="How many recent non-empty discussion lines to validate.",
    )
    parser.add_argument(
        "--allow-missing-discussion",
        action="store_true",
        help="Pass when discussion file is missing (useful for CI clean checkouts).",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = _build_report(
        args.targets,
        Path(args.discussion_path),
        max(1, args.tail_lines),
        args.allow_missing_discussion,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
