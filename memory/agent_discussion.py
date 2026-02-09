from __future__ import annotations

import json
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_DISCUSSION_RAW_PATH = Path("memory/agent_discussion.jsonl")
DEFAULT_DISCUSSION_CURATED_PATH = Path("memory/agent_discussion_curated.jsonl")
# Backward-compat alias
DEFAULT_DISCUSSION_PATH = DEFAULT_DISCUSSION_RAW_PATH
REQUIRED_FIELDS = ("timestamp", "author", "topic", "status", "message")
CURATED_EXCLUDED_STATUS = {"invalid"}
CURATED_EXCLUDED_TOPICS = {"agent-discussion-parse-error"}
TEXT_ANOMALY_REPLACEMENT = "replacement_char"
TEXT_ANOMALY_PRIVATE_USE = "private_use_char"


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _normalize_text(value: Any, fallback: str) -> str:
    if isinstance(value, str):
        stripped = value.strip()
        if stripped:
            if "\x00" in stripped:
                raise ValueError("NUL byte is not allowed in discussion fields")
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


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _detect_text_anomalies(value: Any) -> List[str]:
    if not isinstance(value, str):
        return []

    anomalies: List[str] = []
    if "\ufffd" in value:
        anomalies.append(TEXT_ANOMALY_REPLACEMENT)
    if any(unicodedata.category(char) == "Co" for char in value):
        anomalies.append(TEXT_ANOMALY_PRIVATE_USE)
    return anomalies


def _entry_text_anomalies(entry: Dict[str, Any]) -> Dict[str, List[str]]:
    result: Dict[str, List[str]] = {}
    for field in REQUIRED_FIELDS:
        anomalies = _detect_text_anomalies(entry.get(field))
        if anomalies:
            result[field] = anomalies
    return result


def _to_curated_entry(entry: Dict[str, Any]) -> Optional[Dict[str, str]]:
    status = str(entry.get("status", "")).strip().lower()
    topic = str(entry.get("topic", "")).strip()
    if status in CURATED_EXCLUDED_STATUS:
        return None
    if topic in CURATED_EXCLUDED_TOPICS:
        return None

    curated: Dict[str, str] = {}
    for field in REQUIRED_FIELDS:
        value = entry.get(field)
        curated[field] = str(value).strip() if value is not None else ""
    if not all(curated.values()):
        return None
    if _entry_text_anomalies(curated):
        return None
    return curated


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
                try:
                    entries.append(normalize_entry(payload))
                except (TypeError, ValueError) as exc:
                    if include_invalid:
                        entries.append(_invalid_line_record(line_number, line, str(exc)))
                continue

            if include_invalid:
                entries.append(
                    _invalid_line_record(line_number, line, "JSON root is not an object")
                )
    return entries


def append_entry(
    entry: Dict[str, Any],
    path: Path = DEFAULT_DISCUSSION_PATH,
    curated_path: Optional[Path] = None,
) -> Dict[str, Any]:
    normalized = normalize_entry(entry)
    _append_jsonl(path, normalized)
    if curated_path is not None:
        curated_entry = _to_curated_entry(normalized)
        if curated_entry is not None:
            _append_jsonl(curated_path, curated_entry)
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
        "text_anomaly_entries": 0,
        "text_anomaly_samples": [],
    }
    if not path.exists():
        return report

    samples: List[Dict[str, Any]] = []
    text_anomaly_samples: List[Dict[str, Any]] = []
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
                try:
                    normalized = normalize_entry(payload)
                    report["valid_entries"] += 1
                    anomalies = _entry_text_anomalies(normalized)
                    if anomalies:
                        report["text_anomaly_entries"] += 1
                        if len(text_anomaly_samples) < sample_limit:
                            text_anomaly_samples.append(
                                {
                                    "line_number": line_number,
                                    "fields": anomalies,
                                }
                            )
                except (TypeError, ValueError) as exc:
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
    report["text_anomaly_samples"] = text_anomaly_samples
    return report


def normalize_file(
    path: Path = DEFAULT_DISCUSSION_PATH,
    create_backup: bool = True,
    keep_invalid: bool = True,
    curated_path: Optional[Path] = None,
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
    curated_report: Optional[Dict[str, Any]] = None
    if curated_path is not None:
        curated_report = rebuild_curated(
            raw_path=path,
            curated_path=curated_path,
            create_backup=False,
        )
    return {
        **after,
        "rewritten": True,
        "written_entries": len(entries),
        "backup_path": str(backup_path) if backup_path else None,
        "invalid_entries_before": before.get("invalid_entries", 0),
        "curated": curated_report,
    }


def rebuild_curated(
    raw_path: Path = DEFAULT_DISCUSSION_RAW_PATH,
    curated_path: Path = DEFAULT_DISCUSSION_CURATED_PATH,
    create_backup: bool = True,
) -> Dict[str, Any]:
    source_entries = load_entries(path=raw_path, include_invalid=False)
    curated_entries: List[Dict[str, str]] = []
    dropped_entries = 0
    for entry in source_entries:
        curated = _to_curated_entry(entry)
        if curated is None:
            dropped_entries += 1
            continue
        curated_entries.append(curated)

    backup_path: Optional[Path] = None
    if create_backup and curated_path.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_path = curated_path.with_name(f"{curated_path.name}.bak.{stamp}")
        backup_path.write_bytes(curated_path.read_bytes())

    curated_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = curated_path.with_name(f"{curated_path.name}.tmp")
    with temp_path.open("w", encoding="utf-8") as handle:
        for entry in curated_entries:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    temp_path.replace(curated_path)

    return {
        "raw_path": str(raw_path),
        "curated_path": str(curated_path),
        "raw_entries": len(source_entries),
        "curated_entries": len(curated_entries),
        "dropped_entries": dropped_entries,
        "backup_path": str(backup_path) if backup_path else None,
    }
