from __future__ import annotations

import sqlite3
from pathlib import Path

from tonesoul.memory.soul_db import SqliteSoulDB


def test_sqlite_soul_db_migrates_legacy_action_logs_schema(tmp_path: Path) -> None:
    db_path = tmp_path / "legacy_soul.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE action_logs (
            id TEXT PRIMARY KEY,
            type TEXT,
            action TEXT,
            params TEXT,
            result TEXT,
            before_context TEXT,
            after_context TEXT,
            isnad_link TEXT,
            timestamp TEXT
        )
        """)
    conn.commit()
    conn.close()

    db = SqliteSoulDB(db_path=db_path)
    db.append_action_log(
        record_type="migration-test",
        action="append",
        params={"ok": True},
        result={"status": "ok"},
        before_context=None,
        after_context=None,
        isnad_link=None,
    )

    conn = sqlite3.connect(db_path)
    columns = {str(row[1]) for row in conn.execute("PRAGMA table_info(action_logs)")}
    conn.close()

    assert "stream" in columns
    assert "metadata" in columns
    latest = db.query_action_logs(limit=1)
    assert latest
    assert latest[0]["stream"] == "raw"
    assert latest[0]["metadata"] == {}
