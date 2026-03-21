from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tonesoul.memory.handoff_ingester import HandoffIngester
from tonesoul.memory.soul_db import MemorySource


class DummySoulDB:
    def __init__(self) -> None:
        self.records = []

    def append(self, source: MemorySource, payload, provenance=None):  # noqa: ANN001
        self.records.append({"source": source, "payload": payload})
        return str(len(self.records))


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_ingest_handoff_json_file(tmp_path: Path):
    handoff_dir = tmp_path / "handoff"
    _write_json(
        handoff_dir / "handoff_2026-03-02T01-00-00Z.json",
        {
            "timestamp": "2026-03-02T01:00:00Z",
            "source_model": "codex",
            "target_model": "antigravity",
            "phase": {"current": "implement", "reason": "phase checkpoint"},
            "pending_tasks": [{"description": "fix compute gate"}],
            "context_summary": {
                "user_goal": "finish release gate",
                "current_files": ["task.md", "tests/test_pipeline_compute_gate.py"],
            },
            "drift_log": [],
        },
    )

    db = DummySoulDB()
    ingester = HandoffIngester(db)
    result = ingester.ingest_handoff_dir(handoff_dir)

    assert result == {"ingested": 1, "skipped": 0, "errors": 0}
    assert len(db.records) == 1
    payload = db.records[0]["payload"]
    assert db.records[0]["source"] == MemorySource.CUSTOM
    assert payload["type"] == "handoff"
    assert payload["from_agent"] == "codex"
    assert payload["to_agent"] == "antigravity"
    assert "fix compute gate" in payload["key_decisions"]
    assert payload["provenance"]["source_file"] == "handoff_2026-03-02T01-00-00Z.json"
    assert payload["evidence"][0] == "finish release gate"


def test_ingest_handoff_markdown_and_sync_md(tmp_path: Path):
    handoff_dir = tmp_path / "handoff"
    handoff_dir.mkdir(parents=True, exist_ok=True)
    (handoff_dir / "session_note.md").write_text(
        "# Session Note\n\nNeed to align calibration thresholds.\n",
        encoding="utf-8",
    )
    sync_md = tmp_path / "ANTIGRAVITY_SYNC.md"
    sync_md.write_text(
        "# Sync\n\nArchitect says finalize regression and calibration.\n",
        encoding="utf-8",
    )

    db = DummySoulDB()
    ingester = HandoffIngester(db)
    dir_result = ingester.ingest_handoff_dir(handoff_dir)
    sync_result = ingester.ingest_sync_md(sync_md)

    assert dir_result["ingested"] == 1
    assert sync_result["ingested"] == 1
    assert len(db.records) == 2
    assert db.records[0]["payload"]["type"] == "handoff_md"
    assert db.records[1]["payload"]["type"] == "handoff_sync_md"
    assert db.records[0]["payload"]["provenance"]["kind"] == "handoff_md"
    assert db.records[1]["payload"]["provenance"]["kind"] == "handoff_sync_md"


def test_ingest_handoff_since_filter(tmp_path: Path):
    handoff_dir = tmp_path / "handoff"
    old_ts = datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc)
    new_ts = old_ts + timedelta(hours=5)

    _write_json(
        handoff_dir / "handoff_old.json",
        {
            "timestamp": old_ts.isoformat().replace("+00:00", "Z"),
            "source_model": "codex",
            "target_model": "antigravity",
            "context_summary": {"user_goal": "old"},
        },
    )
    _write_json(
        handoff_dir / "handoff_new.json",
        {
            "timestamp": new_ts.isoformat().replace("+00:00", "Z"),
            "source_model": "codex",
            "target_model": "antigravity",
            "context_summary": {"user_goal": "new"},
        },
    )

    db = DummySoulDB()
    ingester = HandoffIngester(db)
    result = ingester.ingest_handoff_dir(
        handoff_dir,
        since=(old_ts + timedelta(hours=1)).isoformat().replace("+00:00", "Z"),
    )

    assert result["ingested"] == 1
    assert result["skipped"] == 1
    assert len(db.records) == 1
    assert db.records[0]["payload"]["summary"] == "new"
