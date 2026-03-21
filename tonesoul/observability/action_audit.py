"""Immutable action audit trail stored in SQLite.

Records every externally-visible action taken by ToneSoul (file writes,
API calls, command execution, posts) with actor, approval chain, and
trace information.

Usage:
    from tonesoul.observability.action_audit import ActionAuditor
    auditor = ActionAuditor()
    auditor.log_action(
        actor="antigravity",
        action_type="api_post",
        target="moltbook/m/philosophy",
        detail="Posted first connection message",
        approved_by="human",
    )
    recent = auditor.query_actions(limit=10)
"""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS actions (
    id          TEXT PRIMARY KEY,
    timestamp   TEXT NOT NULL,
    actor       TEXT NOT NULL,
    action_type TEXT NOT NULL,
    target      TEXT,
    detail      TEXT,
    approved_by TEXT,
    trace_id    TEXT,
    metadata    TEXT
);

CREATE INDEX IF NOT EXISTS idx_actions_timestamp ON actions(timestamp);
CREATE INDEX IF NOT EXISTS idx_actions_actor ON actions(actor);
CREATE INDEX IF NOT EXISTS idx_actions_type ON actions(action_type);
"""


# ---------------------------------------------------------------------------
# ActionAuditor
# ---------------------------------------------------------------------------


class ActionAuditor:
    """Immutable action audit trail backed by SQLite.

    All writes are append-only. There is no update or delete API
    by design — the audit trail is tamper-evident.
    """

    def __init__(self, db_path: Optional[Path] = None) -> None:
        if db_path is None:
            db_path = Path(__file__).resolve().parent.parent.parent / "data" / "audit.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path), timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def log_action(
        self,
        actor: str,
        action_type: str,
        target: Optional[str] = None,
        detail: Optional[str] = None,
        approved_by: Optional[str] = None,
        trace_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        """Record one action to the audit trail.

        Args:
            actor: Who performed the action (antigravity, codex, cron, human).
            action_type: Category (file_write, api_post, command_exec, etc).
            target: What was acted upon (file path, URL, etc).
            detail: Human-readable description.
            approved_by: Who approved this action (human, auto, circuit_breaker).
            trace_id: Optional correlation ID.
            metadata: Optional extra key-value pairs.

        Returns:
            The generated action ID.
        """
        action_id = f"act_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()
        meta_json = json.dumps(metadata, ensure_ascii=False) if metadata else None

        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    """INSERT INTO actions
                       (id, timestamp, actor, action_type, target, detail, approved_by, trace_id, metadata)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        action_id,
                        timestamp,
                        actor,
                        action_type,
                        target,
                        detail,
                        approved_by,
                        trace_id,
                        meta_json,
                    ),
                )
        return action_id

    def query_actions(
        self,
        *,
        since: Optional[str] = None,
        actor: Optional[str] = None,
        action_type: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Query the audit trail with optional filters.

        Args:
            since: ISO timestamp — only return actions after this time.
            actor: Filter by actor.
            action_type: Filter by action type.
            limit: Max results (default 50).

        Returns:
            List of action records as dicts.
        """
        conditions = []
        params: list[Any] = []

        if since:
            conditions.append("timestamp > ?")
            params.append(since)
        if actor:
            conditions.append("actor = ?")
            params.append(actor)
        if action_type:
            conditions.append("action_type = ?")
            params.append(action_type)

        where = ""
        if conditions:
            where = "WHERE " + " AND ".join(conditions)

        query = f"SELECT * FROM actions {where} ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()

        results = []
        for row in rows:
            d = dict(row)
            if d.get("metadata"):
                try:
                    d["metadata"] = json.loads(d["metadata"])
                except json.JSONDecodeError:
                    pass
            results.append(d)
        return results

    def count_actions(self, since: Optional[str] = None) -> int:
        """Count total actions, optionally since a given timestamp."""
        if since:
            query = "SELECT COUNT(*) FROM actions WHERE timestamp > ?"
            params: tuple = (since,)
        else:
            query = "SELECT COUNT(*) FROM actions"
            params = ()

        with self._connect() as conn:
            return conn.execute(query, params).fetchone()[0]
