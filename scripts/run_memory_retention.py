"""
Organize old memory artifacts into archive buckets with a safe retention policy.
"""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class JsonlRetentionResult:
    path: str
    exists: bool
    total_lines: int = 0
    kept_lines: int = 0
    archived_lines: int = 0
    invalid_timestamp_lines: int = 0
    archive_path: str | None = None
    backup_path: str | None = None
    applied: bool = False


@dataclass
class HandoffRetentionResult:
    directory: str
    exists: bool
    total_files: int = 0
    candidate_files: int = 0
    moved_files: int = 0
    moved_bytes: int = 0
    archive_root: str | None = None
    applied: bool = False


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_iso_timestamp(raw: str | None) -> datetime | None:
    if not isinstance(raw, str):
        return None
    text = raw.strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _parse_handoff_filename_timestamp(path: Path) -> datetime | None:
    # Example: handoff_2026-02-22T11-23-40Z.json
    name = path.name
    if not (name.startswith("handoff_") and name.endswith(".json")):
        return None
    token = name[len("handoff_") : -len(".json")]
    for pattern in ("%Y-%m-%dT%H-%M-%SZ", "%Y-%m-%dT%H-%M-%S"):
        try:
            parsed = datetime.strptime(token, pattern)
            return parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _jsonl_entry_timestamp(payload: dict[str, Any]) -> datetime | None:
    ts = _parse_iso_timestamp(payload.get("timestamp"))
    if ts is not None:
        return ts
    transcript = payload.get("transcript")
    if isinstance(transcript, dict):
        ts = _parse_iso_timestamp(transcript.get("timestamp"))
        if ts is not None:
            return ts
    return None


def _partition_jsonl_lines(path: Path, cutoff: datetime) -> tuple[list[str], list[str], int]:
    keep_lines: list[str] = []
    archive_lines: list[str] = []
    invalid_timestamp_lines = 0

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if not line.strip():
                keep_lines.append(line)
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                # Keep malformed lines in active file to avoid destructive loss.
                keep_lines.append(line)
                invalid_timestamp_lines += 1
                continue
            if not isinstance(payload, dict):
                keep_lines.append(line)
                invalid_timestamp_lines += 1
                continue
            timestamp = _jsonl_entry_timestamp(payload)
            if timestamp is None:
                keep_lines.append(line)
                invalid_timestamp_lines += 1
                continue
            if timestamp < cutoff:
                archive_lines.append(line)
            else:
                keep_lines.append(line)

    return keep_lines, archive_lines, invalid_timestamp_lines


def _apply_jsonl_retention(
    path: Path,
    archive_dir: Path,
    cutoff: datetime,
    apply: bool,
) -> JsonlRetentionResult:
    result = JsonlRetentionResult(path=path.as_posix(), exists=path.exists())
    if not path.exists():
        return result

    keep_lines, archive_lines, invalid_timestamp_lines = _partition_jsonl_lines(path, cutoff)
    result.total_lines = len(keep_lines) + len(archive_lines)
    result.kept_lines = len(keep_lines)
    result.archived_lines = len(archive_lines)
    result.invalid_timestamp_lines = invalid_timestamp_lines

    archive_filename = f"{path.stem}.before_{cutoff.strftime('%Y%m%d')}.jsonl"
    archive_path = archive_dir / archive_filename
    result.archive_path = archive_path.as_posix()

    if not apply or len(archive_lines) == 0:
        result.applied = False
        return result

    archive_dir.mkdir(parents=True, exist_ok=True)

    backup_dir = archive_dir / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = (
        backup_dir / f"{path.name}.{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.bak"
    )
    shutil.copy2(path, backup_path)
    result.backup_path = backup_path.as_posix()

    _ensure_parent(archive_path)
    with archive_path.open("a", encoding="utf-8") as archive_handle:
        for line in archive_lines:
            archive_handle.write(line + "\n")

    with path.open("w", encoding="utf-8") as active_handle:
        for line in keep_lines:
            active_handle.write(line + "\n")

    result.applied = True
    return result


def _collect_handoff_candidates(handoff_dir: Path, cutoff: datetime) -> list[Path]:
    candidates: list[Path] = []
    for file_path in handoff_dir.glob("handoff_*.json"):
        timestamp = _parse_handoff_filename_timestamp(file_path)
        if timestamp is None:
            timestamp = datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc)
        if timestamp < cutoff:
            candidates.append(file_path)
    return sorted(candidates)


def _apply_handoff_retention(
    handoff_dir: Path,
    archive_root: Path,
    cutoff: datetime,
    apply: bool,
) -> HandoffRetentionResult:
    result = HandoffRetentionResult(directory=handoff_dir.as_posix(), exists=handoff_dir.exists())
    if not handoff_dir.exists():
        return result

    all_files = list(handoff_dir.glob("handoff_*.json"))
    candidates = _collect_handoff_candidates(handoff_dir, cutoff)
    result.total_files = len(all_files)
    result.candidate_files = len(candidates)
    result.archive_root = archive_root.as_posix()

    if not apply or len(candidates) == 0:
        result.applied = False
        return result

    moved_files = 0
    moved_bytes = 0
    for source in candidates:
        ts = _parse_handoff_filename_timestamp(source)
        if ts is None:
            ts = datetime.fromtimestamp(source.stat().st_mtime, tz=timezone.utc)
        month_bucket = ts.strftime("%Y-%m")
        target_dir = archive_root / month_bucket
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / source.name
        if target.exists():
            # Keep deterministic and avoid overwrite collisions.
            target = target_dir / f"{source.stem}.{int(source.stat().st_mtime)}.json"
        size = source.stat().st_size
        shutil.move(source, target)
        moved_files += 1
        moved_bytes += size

    result.moved_files = moved_files
    result.moved_bytes = moved_bytes
    result.applied = True
    return result


def _bytes_to_mb(value: int) -> float:
    return round(float(value) / (1024.0 * 1024.0), 3)


def build_report(
    self_journal: Path,
    provenance_ledger: Path,
    handoff_dir: Path,
    cutoff: datetime,
    archive_root: Path,
    apply: bool,
) -> dict[str, Any]:
    jsonl_archive_dir = archive_root / "jsonl"
    handoff_archive_dir = handoff_dir / "archive"

    self_result = _apply_jsonl_retention(self_journal, jsonl_archive_dir, cutoff, apply)
    provenance_result = _apply_jsonl_retention(provenance_ledger, jsonl_archive_dir, cutoff, apply)
    handoff_result = _apply_handoff_retention(handoff_dir, handoff_archive_dir, cutoff, apply)

    archived_jsonl_lines = self_result.archived_lines + provenance_result.archived_lines
    moved_handoff_files = handoff_result.moved_files

    return {
        "generated_at": _iso_now(),
        "mode": "apply" if apply else "dry_run",
        "cutoff_utc": cutoff.isoformat().replace("+00:00", "Z"),
        "targets": {
            "self_journal": self_result.path,
            "provenance_ledger": provenance_result.path,
            "handoff_dir": handoff_result.directory,
        },
        "results": {
            "self_journal": {
                "exists": self_result.exists,
                "total_lines": self_result.total_lines,
                "kept_lines": self_result.kept_lines,
                "archived_lines": self_result.archived_lines,
                "invalid_timestamp_lines": self_result.invalid_timestamp_lines,
                "archive_path": self_result.archive_path,
                "backup_path": self_result.backup_path,
                "applied": self_result.applied,
            },
            "provenance_ledger": {
                "exists": provenance_result.exists,
                "total_lines": provenance_result.total_lines,
                "kept_lines": provenance_result.kept_lines,
                "archived_lines": provenance_result.archived_lines,
                "invalid_timestamp_lines": provenance_result.invalid_timestamp_lines,
                "archive_path": provenance_result.archive_path,
                "backup_path": provenance_result.backup_path,
                "applied": provenance_result.applied,
            },
            "handoff": {
                "exists": handoff_result.exists,
                "total_files": handoff_result.total_files,
                "candidate_files": handoff_result.candidate_files,
                "moved_files": handoff_result.moved_files,
                "moved_mb": _bytes_to_mb(handoff_result.moved_bytes),
                "archive_root": handoff_result.archive_root,
                "applied": handoff_result.applied,
            },
        },
        "summary": {
            "archived_jsonl_lines": archived_jsonl_lines,
            "moved_handoff_files": moved_handoff_files,
            "overall_ok": True,
        },
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _ensure_parent(path)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    _ensure_parent(path)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    results = payload["results"]
    summary = payload["summary"]
    lines = [
        "# Memory Retention Latest",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- mode: {payload['mode']}",
        f"- cutoff_utc: {payload['cutoff_utc']}",
        "",
        "## Summary",
        f"- archived_jsonl_lines: {summary['archived_jsonl_lines']}",
        f"- moved_handoff_files: {summary['moved_handoff_files']}",
        "",
        "## Self Journal",
        f"- total_lines: {results['self_journal']['total_lines']}",
        f"- kept_lines: {results['self_journal']['kept_lines']}",
        f"- archived_lines: {results['self_journal']['archived_lines']}",
        f"- archive_path: {results['self_journal']['archive_path']}",
        "",
        "## Provenance Ledger",
        f"- total_lines: {results['provenance_ledger']['total_lines']}",
        f"- kept_lines: {results['provenance_ledger']['kept_lines']}",
        f"- archived_lines: {results['provenance_ledger']['archived_lines']}",
        f"- archive_path: {results['provenance_ledger']['archive_path']}",
        "",
        "## Handoff",
        f"- total_files: {results['handoff']['total_files']}",
        f"- candidate_files: {results['handoff']['candidate_files']}",
        f"- moved_files: {results['handoff']['moved_files']}",
        f"- moved_mb: {results['handoff']['moved_mb']}",
        f"- archive_root: {results['handoff']['archive_root']}",
        "",
    ]
    _ensure_parent(path)
    path.write_text("\n".join(lines), encoding="utf-8")


def _report_stamp(iso_text: str) -> str:
    # 2026-02-22T12:08:08Z -> 20260222T120808Z
    return iso_text.replace("-", "").replace(":", "").replace(".", "").replace("+00:00", "Z")


def _dated_report_path(path: Path, stamp: str) -> Path:
    stem = path.stem
    if stem.endswith("_latest"):
        stem = stem[: -len("_latest")]
    return path.with_name(f"{stem}_{stamp}{path.suffix}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Organize old memory artifacts with retention rules."
    )
    parser.add_argument(
        "--self-journal", default="memory/self_journal.jsonl", help="Self journal JSONL path."
    )
    parser.add_argument(
        "--provenance-ledger",
        default="memory/provenance_ledger.jsonl",
        help="Provenance ledger JSONL path.",
    )
    parser.add_argument("--handoff-dir", default="memory/handoff", help="Handoff directory path.")
    parser.add_argument(
        "--archive-root",
        default="memory/archive/retention",
        help="Archive root for retention outputs.",
    )
    parser.add_argument(
        "--cutoff",
        default=None,
        help="Archive records older than this UTC date (YYYY-MM-DD). Default: first day of current month.",
    )
    parser.add_argument(
        "--report-json",
        default="memory/archive/retention/memory_retention_latest.json",
        help="Retention report JSON output path.",
    )
    parser.add_argument(
        "--report-md",
        default="memory/archive/retention/memory_retention_latest.md",
        help="Retention report Markdown output path.",
    )
    parser.add_argument(
        "--history-jsonl",
        default="memory/archive/retention/memory_retention_history.jsonl",
        help="Append-only retention history JSONL path.",
    )
    parser.add_argument(
        "--apply", action="store_true", help="Apply retention changes. Default is dry-run."
    )
    return parser


def _resolve_cutoff(raw: str | None) -> datetime:
    if raw:
        parsed = datetime.strptime(raw, "%Y-%m-%d")
        return parsed.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def main() -> int:
    args = build_parser().parse_args()
    cutoff = _resolve_cutoff(args.cutoff)
    latest_json_path = Path(args.report_json)
    latest_md_path = Path(args.report_md)
    history_jsonl_path = Path(args.history_jsonl)

    payload = build_report(
        self_journal=Path(args.self_journal),
        provenance_ledger=Path(args.provenance_ledger),
        handoff_dir=Path(args.handoff_dir),
        cutoff=cutoff,
        archive_root=Path(args.archive_root),
        apply=bool(args.apply),
    )

    stamp = _report_stamp(str(payload["generated_at"]))
    dated_json_path = _dated_report_path(latest_json_path, stamp)
    dated_md_path = _dated_report_path(latest_md_path, stamp)

    payload["artifacts"] = {
        "latest_json": latest_json_path.as_posix(),
        "latest_md": latest_md_path.as_posix(),
        "dated_json": dated_json_path.as_posix(),
        "dated_md": dated_md_path.as_posix(),
        "history_jsonl": history_jsonl_path.as_posix(),
    }

    _write_json(latest_json_path, payload)
    _write_markdown(latest_md_path, payload)
    _write_json(dated_json_path, payload)
    _write_markdown(dated_md_path, payload)

    _append_jsonl(
        history_jsonl_path,
        {
            "generated_at": payload["generated_at"],
            "mode": payload["mode"],
            "cutoff_utc": payload["cutoff_utc"],
            "summary": payload["summary"],
            "dated_json": dated_json_path.as_posix(),
            "dated_md": dated_md_path.as_posix(),
        },
    )

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
