from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from .soul_db import MemorySource, SoulDB
from .write_gateway import MemoryWriteGateway


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _iso_from_mtime(path: Path) -> str:
    dt = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


class HandoffIngester:
    """
    Ingest AI-to-AI handoff artifacts into SoulDB custom memory stream.
    """

    def __init__(self, soul_db: SoulDB) -> None:
        self.soul_db = soul_db
        self.write_gateway = MemoryWriteGateway(soul_db)

    def ingest_handoff_dir(
        self,
        handoff_dir: Path = Path("memory/handoff"),
        *,
        since: Optional[str] = None,
    ) -> Dict[str, int]:
        since_dt = _parse_iso(since)
        counts = {"ingested": 0, "skipped": 0, "errors": 0}

        if not handoff_dir.exists() or not handoff_dir.is_dir():
            return counts

        for path in sorted(handoff_dir.iterdir()):
            if not path.is_file():
                continue
            suffix = path.suffix.lower()
            try:
                if suffix == ".json":
                    status = self._ingest_json(path, since_dt=since_dt)
                elif suffix == ".md":
                    status = self._ingest_markdown(path, since_dt=since_dt, kind="handoff_md")
                else:
                    counts["skipped"] += 1
                    continue
            except Exception:
                counts["errors"] += 1
                continue
            counts[status] += 1

        try:
            from memory.provenance_chain import ProvenanceManager

            ProvenanceManager().add_record(
                event_type="memory_event",
                content={"event": "handoff_ingest", "ingested": int(counts.get("ingested", 0))},
                metadata={"source": str(handoff_dir)},
            )
        except Exception:
            pass
        return counts

    def ingest_sync_md(self, path: Path) -> Dict[str, int]:
        if not path.exists() or not path.is_file():
            return {"ingested": 0, "skipped": 1, "errors": 0}
        try:
            status = self._ingest_markdown(path, since_dt=None, kind="handoff_sync_md")
        except Exception:
            return {"ingested": 0, "skipped": 0, "errors": 1}
        return {
            "ingested": 1 if status == "ingested" else 0,
            "skipped": 1 if status == "skipped" else 0,
            "errors": 0,
        }

    def _ingest_json(self, path: Path, *, since_dt: Optional[datetime]) -> str:
        raw = path.read_text(encoding="utf-8", errors="replace").strip()
        if not raw:
            return "skipped"
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            raise ValueError(f"invalid JSON handoff: {path}")
        if not isinstance(payload, dict):
            return "skipped"

        timestamp = str(payload.get("timestamp") or _iso_from_mtime(path))
        record_dt = _parse_iso(timestamp)
        if since_dt is not None and record_dt is not None and record_dt < since_dt:
            return "skipped"

        context_summary = payload.get("context_summary")
        summary = ""
        files_changed = []
        if isinstance(context_summary, dict):
            summary = str(context_summary.get("user_goal") or "").strip()
            current_files = context_summary.get("current_files")
            if isinstance(current_files, list):
                files_changed = [str(item) for item in current_files if str(item).strip()]

        pending = payload.get("pending_tasks")
        key_decisions = []
        if isinstance(pending, list):
            for item in pending:
                if isinstance(item, dict):
                    text = str(item.get("description") or "").strip()
                    if text:
                        key_decisions.append(text)

        if not summary:
            phase = payload.get("phase")
            if isinstance(phase, dict):
                summary = str(phase.get("reason") or "").strip()
        if not summary:
            summary = f"handoff imported from {path.name}"

        memory_payload = {
            "type": "handoff",
            "from_agent": str(payload.get("source_model") or "unknown"),
            "to_agent": str(payload.get("target_model") or "unknown"),
            "summary": summary,
            "key_decisions": key_decisions,
            "files_changed": files_changed,
            "tension_snapshot": {
                "phase": payload.get("phase"),
                "drift_log_count": (
                    len(payload.get("drift_log", []))
                    if isinstance(payload.get("drift_log"), list)
                    else 0
                ),
            },
            "timestamp": timestamp,
            "source_file": path.name,
            "evidence": [summary, path.name],
            "provenance": {
                "kind": "handoff_json",
                "source_file": path.name,
                "imported_at": timestamp,
            },
        }
        self.write_gateway.write_payload(MemorySource.CUSTOM, memory_payload)
        return "ingested"

    def _ingest_markdown(
        self,
        path: Path,
        *,
        since_dt: Optional[datetime],
        kind: str,
    ) -> str:
        content = path.read_text(encoding="utf-8", errors="replace")
        if not content.strip():
            return "skipped"

        timestamp = _iso_from_mtime(path)
        record_dt = _parse_iso(timestamp)
        if since_dt is not None and record_dt is not None and record_dt < since_dt:
            return "skipped"

        first_line = ""
        for line in content.splitlines():
            stripped = line.strip()
            if stripped:
                first_line = stripped
                break
        if not first_line:
            first_line = f"handoff markdown imported from {path.name}"

        memory_payload = {
            "type": kind,
            "from_agent": "unknown",
            "to_agent": "unknown",
            "summary": first_line[:200],
            "key_decisions": [],
            "files_changed": [],
            "tension_snapshot": {},
            "timestamp": timestamp,
            "source_file": path.name,
            "content": content[:4000],
            "evidence": [first_line[:200], path.name],
            "provenance": {
                "kind": kind,
                "source_file": path.name,
                "imported_at": timestamp,
            },
        }
        self.write_gateway.write_payload(MemorySource.CUSTOM, memory_payload)
        return "ingested"
