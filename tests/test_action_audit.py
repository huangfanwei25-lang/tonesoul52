import sqlite3

from tonesoul.observability.action_audit import ActionAuditor


def _update_action_row(
    db_path,
    action_id: str,
    *,
    timestamp: str | None = None,
    metadata: str | None = None,
) -> None:
    with sqlite3.connect(db_path) as conn:
        if timestamp is not None:
            conn.execute("UPDATE actions SET timestamp = ? WHERE id = ?", (timestamp, action_id))
        if metadata is not None:
            conn.execute("UPDATE actions SET metadata = ? WHERE id = ?", (metadata, action_id))
        conn.commit()


def test_query_actions_combines_filters_and_limit(tmp_path) -> None:
    db_path = tmp_path / "audit.db"
    auditor = ActionAuditor(db_path=db_path)
    old_match = auditor.log_action(actor="codex", action_type="write", detail="old")
    latest_match = auditor.log_action(actor="codex", action_type="write", detail="latest")
    auditor.log_action(actor="antigravity", action_type="write", detail="other actor")
    auditor.log_action(actor="codex", action_type="read", detail="other type")

    _update_action_row(db_path, old_match, timestamp="2026-03-19T10:00:00+00:00")
    _update_action_row(db_path, latest_match, timestamp="2026-03-19T11:00:00+00:00")

    results = auditor.query_actions(
        since="2026-03-19T09:30:00+00:00",
        actor="codex",
        action_type="write",
        limit=1,
    )

    assert len(results) == 1
    assert results[0]["id"] == latest_match
    assert results[0]["detail"] == "latest"


def test_query_actions_preserves_invalid_metadata_string(tmp_path) -> None:
    db_path = tmp_path / "audit.db"
    auditor = ActionAuditor(db_path=db_path)
    action_id = auditor.log_action(
        actor="codex",
        action_type="write",
        metadata={"ok": True},
    )
    _update_action_row(db_path, action_id, metadata="{bad json")

    results = auditor.query_actions()

    assert results[0]["metadata"] == "{bad json"


def test_count_actions_since_only_counts_newer_rows(tmp_path) -> None:
    db_path = tmp_path / "audit.db"
    auditor = ActionAuditor(db_path=db_path)
    first = auditor.log_action(actor="codex", action_type="write")
    second = auditor.log_action(actor="codex", action_type="write")
    third = auditor.log_action(actor="codex", action_type="write")

    _update_action_row(db_path, first, timestamp="2026-03-19T08:00:00+00:00")
    _update_action_row(db_path, second, timestamp="2026-03-19T12:00:00+00:00")
    _update_action_row(db_path, third, timestamp="2026-03-19T13:00:00+00:00")

    assert auditor.count_actions(since="2026-03-19T11:00:00+00:00") == 2


def test_log_action_with_empty_metadata_stores_null(tmp_path) -> None:
    db_path = tmp_path / "audit.db"
    auditor = ActionAuditor(db_path=db_path)
    action_id = auditor.log_action(actor="codex", action_type="write", metadata={})

    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT metadata FROM actions WHERE id = ?", (action_id,)).fetchone()

    assert row[0] is None
