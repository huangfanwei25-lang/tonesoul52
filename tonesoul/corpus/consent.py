"""
ToneSoul Consent Manager

Handles user consent for data collection with:
- Versioned consent tracking
- Multiple consent types (research/commercial/anonymous)
- Opt-out/withdrawal support
- GDPR-friendly design
"""

import hashlib
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional


class ConsentType(Enum):
    """Types of consent users can grant."""

    ANONYMOUS = "anonymous"  # 匿名使用，不追蹤
    RESEARCH = "research"  # 研究用途
    IMPROVEMENT = "improvement"  # 用於改進 AI


@dataclass
class UserConsent:
    """
    Record of user consent.

    Privacy notes:
    - session_id is a random UUID, not linked to real identity
    - ip_hash is SHA256, original IP is never stored
    """

    session_id: str
    consent_type: ConsentType
    agreed_at: datetime = field(default_factory=datetime.now)
    consent_version: str = "1.0"
    ip_hash: str = ""  # SHA256 of IP
    user_agent_hash: str = ""  # SHA256 of User-Agent
    withdrawn: bool = False
    withdrawn_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "consent_type": self.consent_type.value,
            "agreed_at": self.agreed_at.isoformat(),
            "consent_version": self.consent_version,
            "withdrawn": self.withdrawn,
            "withdrawn_at": self.withdrawn_at.isoformat() if self.withdrawn_at else None,
        }


class ConsentManager:
    """
    Manages user consent for corpus collection.

    Storage: SQLite database in data/users.db
    """

    CURRENT_CONSENT_VERSION = "1.0"

    def __init__(self, db_path: str = "data/users.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                consent_type TEXT NOT NULL,
                consent_version TEXT NOT NULL,
                agreed_at TEXT NOT NULL,
                ip_hash TEXT,
                user_agent_hash TEXT,
                withdrawn INTEGER DEFAULT 0,
                withdrawn_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session
            ON consents(session_id)
        """)

        conn.commit()
        conn.close()

    @staticmethod
    def hash_identifier(value: str) -> str:
        """Hash sensitive data (IP, User-Agent)."""
        if not value:
            return ""
        return hashlib.sha256(value.encode()).hexdigest()[:32]

    def record_consent(
        self,
        session_id: str,
        consent_type: ConsentType,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> UserConsent:
        """Record user consent."""
        consent = UserConsent(
            session_id=session_id,
            consent_type=consent_type,
            consent_version=self.CURRENT_CONSENT_VERSION,
            ip_hash=self.hash_identifier(ip_address or ""),
            user_agent_hash=self.hash_identifier(user_agent or ""),
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO consents
                (session_id, consent_type, consent_version, agreed_at,
                 ip_hash, user_agent_hash, withdrawn, withdrawn_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    consent.session_id,
                    consent.consent_type.value,
                    consent.consent_version,
                    consent.agreed_at.isoformat(),
                    consent.ip_hash,
                    consent.user_agent_hash,
                    0,
                    None,
                ),
            )
            conn.commit()
        finally:
            conn.close()

        return consent

    def get_consent(self, session_id: str) -> Optional[UserConsent]:
        """Get consent record for a session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT session_id, consent_type, consent_version, agreed_at,
                       ip_hash, user_agent_hash, withdrawn, withdrawn_at
                FROM consents WHERE session_id = ?
            """,
                (session_id,),
            )

            row = cursor.fetchone()
            if not row:
                return None

            return UserConsent(
                session_id=row[0],
                consent_type=ConsentType(row[1]),
                consent_version=row[2],
                agreed_at=datetime.fromisoformat(row[3]),
                ip_hash=row[4] or "",
                user_agent_hash=row[5] or "",
                withdrawn=bool(row[6]),
                withdrawn_at=datetime.fromisoformat(row[7]) if row[7] else None,
            )
        finally:
            conn.close()

    def has_valid_consent(self, session_id: str) -> bool:
        """Check if session has valid (non-withdrawn) consent."""
        consent = self.get_consent(session_id)
        if not consent:
            return False
        return not consent.withdrawn

    def withdraw_consent(self, session_id: str) -> bool:
        """Withdraw consent (GDPR right to be forgotten)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE consents
                SET withdrawn = 1, withdrawn_at = ?
                WHERE session_id = ?
            """,
                (datetime.now().isoformat(), session_id),
            )

            affected = cursor.rowcount
            conn.commit()
            return affected > 0
        finally:
            conn.close()

    def get_consent_stats(self) -> Dict[str, Any]:
        """Get statistics about consents."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) FROM consents WHERE withdrawn = 0")
            active = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM consents WHERE withdrawn = 1")
            withdrawn = cursor.fetchone()[0]

            cursor.execute("""
                SELECT consent_type, COUNT(*) as cnt
                FROM consents WHERE withdrawn = 0
                GROUP BY consent_type
            """)
            by_type = {row[0]: row[1] for row in cursor.fetchall()}

            return {"active_consents": active, "withdrawn_consents": withdrawn, "by_type": by_type}
        finally:
            conn.close()


def create_consent_manager(db_path: str = "data/users.db") -> ConsentManager:
    """Factory function."""
    return ConsentManager(db_path)
