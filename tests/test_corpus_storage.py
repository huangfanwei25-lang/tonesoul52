import json
import sqlite3
from datetime import datetime

import pytest

from tonesoul.corpus.storage import Conversation, ConversationTurn, CorpusStorage


# ── ConversationTurn.to_dict ──────────────────────────────────────────────────

class TestConversationTurnToDict:
    def test_includes_required_fields(self):
        turn = ConversationTurn(
            timestamp=datetime(2026, 4, 1, 12, 0, 0),
            user_input="hello",
            ai_response="world",
        )
        d = turn.to_dict()
        assert d["user_input"] == "hello"
        assert d["ai_response"] == "world"
        assert "2026-04-01" in d["timestamp"]
        assert d["deliberation"] is None
        assert d["feedback"] is None

    def test_deliberation_and_feedback_included(self):
        turn = ConversationTurn(
            timestamp=datetime(2026, 4, 1),
            user_input="q",
            ai_response="a",
            deliberation={"verdict": "approve"},
            feedback="positive",
        )
        d = turn.to_dict()
        assert d["deliberation"] == {"verdict": "approve"}
        assert d["feedback"] == "positive"


# ── Conversation.add_turn / to_dict / to_jsonl_line ──────────────────────────

class TestConversation:
    def _conv(self):
        return Conversation(
            id="conv-1",
            session_id="sess-1",
            consent_version="1.0",
            started_at=datetime(2026, 4, 1, 10, 0, 0),
        )

    def test_add_turn_appends(self):
        conv = self._conv()
        conv.add_turn("hello", "hi there")
        assert len(conv.turns) == 1
        assert conv.turns[0].user_input == "hello"

    def test_to_dict_fields(self):
        conv = self._conv()
        d = conv.to_dict()
        assert d["id"] == "conv-1"
        assert d["session_id"] == "sess-1"
        assert d["ended_at"] is None
        assert d["metadata"]["model"] == "formosa1"
        assert d["metadata"]["tonesoul_version"] == "2.0"

    def test_to_dict_with_ended_at(self):
        conv = self._conv()
        conv.ended_at = datetime(2026, 4, 1, 11, 0, 0)
        assert "2026-04-01" in conv.to_dict()["ended_at"]

    def test_to_jsonl_line_is_parseable_json(self):
        conv = self._conv()
        conv.add_turn("q", "a")
        line = conv.to_jsonl_line()
        parsed = json.loads(line)
        assert parsed["id"] == "conv-1"
        assert len(parsed["turns"]) == 1


# ── CorpusStorage.get_corpus_stats ────────────────────────────────────────────

def test_get_corpus_stats_returns_counts(tmp_path) -> None:
    storage = _make_storage(tmp_path)
    conv = storage.create_conversation("session-stats")
    storage.add_turn(conv.id, "u", "a")

    stats = storage.get_corpus_stats()

    assert stats["total_conversations"] >= 1
    assert stats["total_turns"] >= 1
    assert "unique_sessions" in stats


# ── CorpusStorage.get_session_conversations ───────────────────────────────────

def test_get_session_conversations_returns_ids_for_session(tmp_path) -> None:
    storage = _make_storage(tmp_path)
    c1 = storage.create_conversation("sess-a")
    c2 = storage.create_conversation("sess-a")
    storage.create_conversation("sess-b")

    ids = storage.get_session_conversations("sess-a")

    assert set(ids) == {c1.id, c2.id}


def test_get_session_conversations_empty_for_missing(tmp_path) -> None:
    storage = _make_storage(tmp_path)
    assert storage.get_session_conversations("no_such_session") == []


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
