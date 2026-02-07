"""
ToneSoul Corpus Storage

Dual-write storage for conversations:
- SQLite for queries and management
- JSONL for backup and ML training

Privacy: All data is linked to session_id only,
no personal identifiers stored.
"""

import json
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ConversationTurn:
    """A single turn in a conversation."""

    timestamp: datetime
    user_input: str
    ai_response: str

    # ToneSoul 2.0 deliberation data
    deliberation: Optional[Dict[str, Any]] = None

    # User feedback (optional)
    feedback: Optional[str] = None  # "positive", "negative", None

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "user_input": self.user_input,
            "ai_response": self.ai_response,
            "deliberation": self.deliberation,
            "feedback": self.feedback,
        }


@dataclass
class Conversation:
    """
    A complete conversation with all its turns.

    Linked to a session_id (anonymous) rather than user identity.
    """

    id: str
    session_id: str
    consent_version: str
    turns: List[ConversationTurn] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None

    # Metadata
    model_used: str = "formosa1"
    tonesoul_version: str = "2.0"

    def add_turn(self, user_input: str, ai_response: str, deliberation: Optional[Dict] = None):
        """Add a new turn to the conversation."""
        self.turns.append(
            ConversationTurn(
                timestamp=datetime.now(),
                user_input=user_input,
                ai_response=ai_response,
                deliberation=deliberation,
            )
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "consent_version": self.consent_version,
            "turns": [t.to_dict() for t in self.turns],
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "metadata": {"model": self.model_used, "tonesoul_version": self.tonesoul_version},
        }

    def to_jsonl_line(self) -> str:
        """Format for JSONL export."""
        return json.dumps(self.to_dict(), ensure_ascii=False)


class CorpusStorage:
    """
    Manages corpus storage with dual-write to SQLite and JSONL.

    SQLite: For queries, statistics, management
    JSONL: For backup and ML training export
    """

    def __init__(self, db_path: str = "data/corpus.db", jsonl_path: str = "data/corpus.jsonl"):
        self.db_path = Path(db_path)
        self.jsonl_path = Path(jsonl_path)

        # Ensure directories exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.jsonl_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    def _init_db(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                consent_version TEXT NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                model_used TEXT,
                tonesoul_version TEXT,
                turn_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Turns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS turns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                turn_index INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                user_input TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                deliberation_json TEXT,
                feedback TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)

        # Indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conv_session
            ON conversations(session_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_turns_conv
            ON turns(conversation_id)
        """)

        conn.commit()
        conn.close()

    def create_conversation(
        self, session_id: str, consent_version: str = "1.0", model: str = "formosa1"
    ) -> Conversation:
        """Create a new conversation."""
        conv_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        conversation = Conversation(
            id=conv_id, session_id=session_id, consent_version=consent_version, model_used=model
        )

        # Save to SQLite
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO conversations
            (id, session_id, consent_version, started_at, model_used, tonesoul_version)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                conversation.id,
                conversation.session_id,
                conversation.consent_version,
                conversation.started_at.isoformat(),
                conversation.model_used,
                conversation.tonesoul_version,
            ),
        )

        conn.commit()
        conn.close()

        return conversation

    def add_turn(
        self,
        conversation_id: str,
        user_input: str,
        ai_response: str,
        deliberation: Optional[Dict] = None,
    ) -> int:
        """Add a turn to an existing conversation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Get current turn count
            cursor.execute("SELECT turn_count FROM conversations WHERE id = ?", (conversation_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Conversation {conversation_id} not found")

            turn_index = row[0]

            # Insert turn
            cursor.execute(
                """
                INSERT INTO turns
                (conversation_id, turn_index, timestamp, user_input, ai_response, deliberation_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    conversation_id,
                    turn_index,
                    datetime.now().isoformat(),
                    user_input,
                    ai_response,
                    json.dumps(deliberation, ensure_ascii=False) if deliberation else None,
                ),
            )

            # Update turn count
            cursor.execute(
                "UPDATE conversations SET turn_count = ? WHERE id = ?",
                (turn_index + 1, conversation_id),
            )

            conn.commit()
            return turn_index

        finally:
            conn.close()

    def save_to_jsonl(self, conversation: Conversation):
        """Append conversation to JSONL backup."""
        with open(self.jsonl_path, "a", encoding="utf-8") as f:
            f.write(conversation.to_jsonl_line() + "\n")

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Load a conversation from SQLite."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT id, session_id, consent_version, started_at, ended_at,
                       model_used, tonesoul_version
                FROM conversations WHERE id = ?
            """,
                (conversation_id,),
            )

            row = cursor.fetchone()
            if not row:
                return None

            conv = Conversation(
                id=row[0],
                session_id=row[1],
                consent_version=row[2],
                started_at=datetime.fromisoformat(row[3]),
                ended_at=datetime.fromisoformat(row[4]) if row[4] else None,
                model_used=row[5] or "formosa1",
                tonesoul_version=row[6] or "2.0",
            )

            # Load turns
            cursor.execute(
                """
                SELECT timestamp, user_input, ai_response, deliberation_json, feedback
                FROM turns WHERE conversation_id = ?
                ORDER BY turn_index
            """,
                (conversation_id,),
            )

            for turn_row in cursor.fetchall():
                conv.turns.append(
                    ConversationTurn(
                        timestamp=datetime.fromisoformat(turn_row[0]),
                        user_input=turn_row[1],
                        ai_response=turn_row[2],
                        deliberation=json.loads(turn_row[3]) if turn_row[3] else None,
                        feedback=turn_row[4],
                    )
                )

            return conv

        finally:
            conn.close()

    def get_session_conversations(self, session_id: str) -> List[str]:
        """Get all conversation IDs for a session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT id FROM conversations WHERE session_id = ? ORDER BY started_at DESC",
                (session_id,),
            )
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_corpus_stats(self) -> Dict[str, Any]:
        """Get statistics about the corpus."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) FROM conversations")
            total_convs = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM turns")
            total_turns = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT session_id) FROM conversations")
            unique_sessions = cursor.fetchone()[0]

            cursor.execute("SELECT AVG(turn_count) FROM conversations WHERE turn_count > 0")
            avg_turns = cursor.fetchone()[0] or 0

            return {
                "total_conversations": total_convs,
                "total_turns": total_turns,
                "unique_sessions": unique_sessions,
                "average_turns_per_conversation": round(avg_turns, 2),
            }
        finally:
            conn.close()

    def delete_session_data(self, session_id: str) -> int:
        """Delete all data for a session (GDPR right to be forgotten)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Get conversation IDs
            cursor.execute("SELECT id FROM conversations WHERE session_id = ?", (session_id,))
            conv_ids = [row[0] for row in cursor.fetchall()]

            # Delete turns
            for conv_id in conv_ids:
                cursor.execute("DELETE FROM turns WHERE conversation_id = ?", (conv_id,))

            # Delete conversations
            cursor.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))

            conn.commit()
            return len(conv_ids)

        finally:
            conn.close()


def create_corpus_storage(
    db_path: str = "data/corpus.db", jsonl_path: str = "data/corpus.jsonl"
) -> CorpusStorage:
    """Factory function."""
    return CorpusStorage(db_path, jsonl_path)
