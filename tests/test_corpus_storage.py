import json
import sqlite3
from datetime import datetime

import pytest

from tonesoul.corpus.storage import Conversation, CorpusStorage


def _make_storage(tmp_path) -> CorpusStorage:
    return CorpusStorage(
        db_path=str(tmp_path / "data" / "corpus.db"),
        jsonl_path=str(tmp_path / "data" / "corpus.jsonl"),
    )


def test_add_turn_raises_for_missing_conversation_without_partial_insert(tmp_path) -> None:
    storage = _make_storage(tmp_path)

    with pytest.raises(ValueError, match="not found"):
        storage.add_turn("missing", "hello", "world")

    with sqlite3.connect(storage.db_path) as conn:
        turns = conn.execute("SELECT COUNT(*) FROM turns").fetchone()[0]

    assert turns == 0


def test_get_conversation_handles_missing_and_defaults_metadata_fields(tmp_path) -> None:
    storage = _make_storage(tmp_path)
    assert storage.get_conversation("missing") is None

    with sqlite3.connect(storage.db_path) as conn:
        conn.execute(
            """
            INSERT INTO conversations
            (id, session_id, consent_version, started_at, ended_at, model_used, tonesoul_version, turn_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "conv_defaulted",
                "session-1",
                "1.0",
                "2026-03-19T10:00:00",
                None,
                None,
                None,
                0,
            ),
        )
        conn.commit()

    conversation = storage.get_conversation("conv_defaulted")

    assert conversation is not None
    assert conversation.ended_at is None
    assert conversation.model_used == "formosa1"
    assert conversation.tonesoul_version == "2.0"


def test_get_session_conversations_orders_desc_and_empty_deliberation_round_trips_as_none(
    tmp_path,
) -> None:
    storage = _make_storage(tmp_path)
    older = storage.create_conversation("session-1")
    newer = storage.create_conversation("session-1")
    storage.add_turn(older.id, "u1", "a1", deliberation={})

    with sqlite3.connect(storage.db_path) as conn:
        conn.execute(
            "UPDATE conversations SET started_at = ? WHERE id = ?",
            ("2026-03-19T09:00:00", older.id),
        )
        conn.execute(
            "UPDATE conversations SET started_at = ? WHERE id = ?",
            ("2026-03-19T10:00:00", newer.id),
        )
        conn.commit()

    loaded = storage.get_conversation(older.id)

    assert loaded is not None
    assert loaded.turns[0].deliberation is None
    assert storage.get_session_conversations("session-1") == [newer.id, older.id]


def test_corpus_stats_delete_session_data_and_jsonl_export(tmp_path) -> None:
    storage = _make_storage(tmp_path)
    assert storage.get_corpus_stats() == {
        "total_conversations": 0,
        "total_turns": 0,
        "unique_sessions": 0,
        "average_turns_per_conversation": 0,
    }

    first = storage.create_conversation("session-a", model="model-a")
    storage.create_conversation("session-a")
    third = storage.create_conversation("session-b")
    storage.add_turn(first.id, "u1", "a1")
    storage.add_turn(first.id, "u2", "a2")
    storage.add_turn(third.id, "u3", "a3")

    stats = storage.get_corpus_stats()

    assert stats == {
        "total_conversations": 3,
        "total_turns": 3,
        "unique_sessions": 2,
        "average_turns_per_conversation": 1.5,
    }

    export_conversation = Conversation(
        id="conv_export",
        session_id="session-export",
        consent_version="1.0",
        turns=[],
        started_at=datetime(2026, 3, 19, 11, 0, 0),
        ended_at=datetime(2026, 3, 19, 11, 5, 0),
        model_used="model-x",
        tonesoul_version="2.1",
    )
    export_conversation.add_turn(
        "question",
        "answer",
        deliberation={"stance": "observe"},
    )
    storage.save_to_jsonl(export_conversation)

    exported = json.loads(storage.jsonl_path.read_text(encoding="utf-8").strip())
    assert exported["ended_at"] == "2026-03-19T11:05:00"
    assert exported["metadata"] == {"model": "model-x", "tonesoul_version": "2.1"}
    assert exported["turns"][0]["deliberation"] == {"stance": "observe"}

    assert storage.delete_session_data("missing") == 0
    assert storage.delete_session_data("session-a") == 2
    with sqlite3.connect(storage.db_path) as conn:
        remaining_conversations = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
        remaining_turns = conn.execute("SELECT COUNT(*) FROM turns").fetchone()[0]

    assert remaining_conversations == 1
    assert remaining_turns == 1
