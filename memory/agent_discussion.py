from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_DISCUSSION_PATH = Path("memory/agent_discussion.jsonl")


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _normalize_text(value: Any, fallback: str) -> str:
    if isinstance(value, str):
        stripped = value.strip()
        if stripped:
            return stripped
    return fallback


def normalize_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(entry, dict):
        raise TypeError("entry must be a dict")

    normalized = dict(entry)
    normalized["timestamp"] = _normalize_text(normalized.get("timestamp"), _iso_now())
    normalized["author"] = _normalize_text(normalized.get("author"), "unknown")
    normalized["topic"] = _normalize_text(normalized.get("topic"), "general")
    normalized["status"] = _normalize_text(normalized.get("status"), "noted")
    normalized["message"] = _normalize_text(normalized.get("message"), "(empty message)")
    return normalized


def _invalid_line_record(line_number: int, raw_line: str, reason: str) -> Dict[str, Any]:
    return {
        "timestamp": _iso_now(),
        "author": "system",
        "topic": "agent-discussion-parse-error",
        "status": "invalid",
        "message": "Invalid discussion line was preserved for audit.",
        "line_number": line_number,
        "reason": reason,
        "raw_line": raw_line,
    }


def load_entries(
    path: Path = DEFAULT_DISCUSSION_PATH,
    include_invalid: bool = False,
) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    entries: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                if include_invalid:
                    entries.append(_invalid_line_record(line_number, line, str(exc)))
                continue

            if isinstance(payload, dict):
                entries.append(normalize_entry(payload))
                continue

            if include_invalid:
                entries.append(_invalid_line_record(line_number, line, "JSON root is not an object"))
    return entries


def append_entry(
    entry: Dict[str, Any],
    path: Path = DEFAULT_DISCUSSION_PATH,
) -> Dict[str, Any]:
    normalized = normalize_entry(entry)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(normalized, ensure_ascii=False) + "\n")
    return normalized


def audit_file(
    path: Path = DEFAULT_DISCUSSION_PATH,
    sample_limit: int = 5,
) -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "total_lines": 0,
        "valid_entries": 0,
        "invalid_entries": 0,
        "invalid_samples": [],
    }
    if not path.exists():
        return report

    samples: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            report["total_lines"] += 1
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                report["invalid_entries"] += 1
                if len(samples) < sample_limit:
                    samples.append(
                        {
                            "line_number": line_number,
                            "reason": str(exc),
                            "raw_line": line,
                        }
                    )
                continue

            if isinstance(payload, dict):
                report["valid_entries"] += 1
                continue

            report["invalid_entries"] += 1
            if len(samples) < sample_limit:
                samples.append(
                    {
                        "line_number": line_number,
                        "reason": "JSON root is not an object",
                        "raw_line": line,
                    }
                )

    report["invalid_samples"] = samples
    return report


def normalize_file(
    path: Path = DEFAULT_DISCUSSION_PATH,
    create_backup: bool = True,
    keep_invalid: bool = True,
) -> Dict[str, Any]:
    before = audit_file(path=path, sample_limit=10)
    if not path.exists():
        return {
            **before,
            "rewritten": False,
            "written_entries": 0,
            "backup_path": None,
        }

    entries = load_entries(path=path, include_invalid=keep_invalid)
    backup_path: Optional[Path] = None
    if create_backup:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_path = path.with_name(f"{path.name}.bak.{stamp}")
        backup_path.write_bytes(path.read_bytes())

    temp_path = path.with_name(f"{path.name}.tmp")
    with temp_path.open("w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    temp_path.replace(path)

    after = audit_file(path=path, sample_limit=10)
    return {
        **after,
        "rewritten": True,
        "written_entries": len(entries),
        "backup_path": str(backup_path) if backup_path else None,
        "invalid_entries_before": before.get("invalid_entries", 0),
    }
