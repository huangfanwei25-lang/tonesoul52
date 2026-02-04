from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Protocol
import json
import sqlite3
import uuid


class MemorySource(Enum):
    SELF_JOURNAL = "self_journal"
    SUMMARY_BALLS = "summary_balls"
    PROVENANCE_LEDGER = "provenance_ledger"
    ENTROPY_MONITOR = "entropy_monitor"
    SCAN_LOG = "scan_log"
    CUSTOM = "custom"


@dataclass
class MemoryRecord:
    source: MemorySource
    timestamp: str
    payload: Dict[str, object]
    tags: List[str] = field(default_factory=list)
    record_id: Optional[str] = None


class SoulDB(Protocol):
    def append(self, source: MemorySource, payload: Dict[str, object]) -> str: ...

    def query(
        self, source: MemorySource, limit: Optional[int] = None
    ) -> Iterable[MemoryRecord]: ...

    def stream(
        self, source: MemorySource, limit: Optional[int] = None
    ) -> Iterable[MemoryRecord]: ...

    def list_sources(self) -> List[MemorySource]: ...


def _iso_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _default_memory_root() -> Path:
    return Path(__file__).resolve().parents[2] / "memory"


def _serialize_json(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _deserialize_json(payload: str) -> Dict[str, object]:
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


class JsonlSoulDB:
    def __init__(
        self,
        base_path: Optional[Path] = None,
        source_map: Optional[Dict[MemorySource, Path]] = None,
    ) -> None:
        self.base_path = base_path or _default_memory_root()
        self.source_map = source_map or {
            MemorySource.SELF_JOURNAL: self.base_path / "self_journal.jsonl",
            MemorySource.SUMMARY_BALLS: self.base_path / "summary_balls.jsonl",
            MemorySource.PROVENANCE_LEDGER: self.base_path / "provenance_ledger.jsonl",
            MemorySource.ENTROPY_MONITOR: self.base_path / "entropy_monitor_log.jsonl",
            MemorySource.SCAN_LOG: self.base_path / "scan_log.jsonl",
        }

    def register_source(self, source: MemorySource, path: Path) -> None:
        self.source_map[source] = path

    def append(self, source: MemorySource, payload: Dict[str, object]) -> str:
        path = self._resolve_path(source)
        path.parent.mkdir(parents=True, exist_ok=True)
        record_id = str(uuid.uuid4())
        record = {
            "record_id": record_id,
            "timestamp": payload.get("timestamp") or _iso_now(),
            "source": source.value,
            "payload": payload,
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record_id

    def query(self, source: MemorySource, limit: Optional[int] = None) -> Iterable[MemoryRecord]:
        return self.stream(source, limit=limit)

    def stream(self, source: MemorySource, limit: Optional[int] = None) -> Iterable[MemoryRecord]:
        path = self._resolve_path(source)
        if not path.exists():
            return []
        records: List[MemoryRecord] = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(payload, dict):
                    continue
                inner_payload = payload.get("payload")
                record_payload = inner_payload if isinstance(inner_payload, dict) else payload
                timestamp = payload.get("timestamp") or record_payload.get("timestamp") or ""
                record_id = payload.get("record_id")
                record = MemoryRecord(
                    source=source,
                    timestamp=str(timestamp),
                    payload=record_payload,
                    record_id=str(record_id) if record_id else None,
                )
                records.append(record)
                if limit is not None and len(records) >= limit:
                    break
        return records

    def list_sources(self) -> List[MemorySource]:
        return list(self.source_map.keys())

    def _resolve_path(self, source: MemorySource) -> Path:
        path = self.source_map.get(source)
        if path is None:
            raise ValueError(f"Unknown memory source: {source}")
        return path


class SqliteSoulDB:
    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = db_path or (_default_memory_root() / "soul.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding BLOB,
                timestamp TEXT,
                source TEXT,
                parent_id TEXT,
                tags TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS vows (
                id TEXT PRIMARY KEY,
                statement TEXT,
                scope TEXT,
                verdict TEXT,
                created_at TEXT,
                active INTEGER,
                falsifiable_by TEXT,
                measurable_via TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS isnad (
                id TEXT PRIMARY KEY,
                event_type TEXT,
                content TEXT,
                hash TEXT,
                prev_hash TEXT,
                timestamp TEXT,
                verified INTEGER
            )
            """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_source ON memories(source)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_isnad_timestamp ON isnad(timestamp)")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS action_logs (
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
            """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_action_logs_type ON action_logs(type)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_action_logs_timestamp ON action_logs(timestamp)"
        )
        conn.commit()
        conn.close()

    def append(self, source: MemorySource, payload: Dict[str, object]) -> str:
        record_id = None
        if isinstance(payload, dict):
            candidate = payload.get("record_id")
            if isinstance(candidate, str) and candidate:
                record_id = candidate
        record_id = record_id or str(uuid.uuid4())
        timestamp = payload.get("timestamp") if isinstance(payload, dict) else None
        timestamp = str(timestamp) if timestamp else _iso_now()

        if source == MemorySource.PROVENANCE_LEDGER:
            event_type = payload.get("event_type") or payload.get("type") or "provenance"
            content = _serialize_json(payload)
            hash_value = payload.get("hash") if isinstance(payload, dict) else None
            prev_hash = payload.get("prev_hash") if isinstance(payload, dict) else None
            verified_value = payload.get("verified") if isinstance(payload, dict) else False
            verified = 1 if verified_value else 0

            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO isnad (id, event_type, content, hash, prev_hash, timestamp, verified)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record_id,
                    str(event_type),
                    content,
                    str(hash_value) if hash_value else None,
                    str(prev_hash) if prev_hash else None,
                    timestamp,
                    verified,
                ),
            )
            conn.commit()
            conn.close()
            return record_id

        record_type = payload.get("type") if isinstance(payload, dict) else None
        record_type = str(record_type) if record_type else source.value
        content = _serialize_json(payload)
        embedding = payload.get("embedding") if isinstance(payload, dict) else None
        embedding_value = None
        if embedding is not None:
            embedding_value = (
                embedding
                if isinstance(embedding, (bytes, bytearray))
                else _serialize_json(embedding)
            )
        parent_id = payload.get("parent_id") if isinstance(payload, dict) else None
        tags = payload.get("tags") if isinstance(payload, dict) else None
        tags_value = None
        if tags:
            tags_value = _serialize_json(tags)

        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO memories (id, type, content, embedding, timestamp, source, parent_id, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record_id,
                record_type,
                content,
                embedding_value,
                timestamp,
                source.value,
                str(parent_id) if parent_id else None,
                tags_value,
            ),
        )
        conn.commit()
        conn.close()
        return record_id

    def query(self, source: MemorySource, limit: Optional[int] = None) -> Iterable[MemoryRecord]:
        return self.stream(source, limit=limit)

    def stream(self, source: MemorySource, limit: Optional[int] = None) -> Iterable[MemoryRecord]:
        if source == MemorySource.PROVENANCE_LEDGER:
            return self._stream_isnad(limit)
        return self._stream_memories(source, limit)

    def list_sources(self) -> List[MemorySource]:
        return [
            MemorySource.SELF_JOURNAL,
            MemorySource.SUMMARY_BALLS,
            MemorySource.PROVENANCE_LEDGER,
            MemorySource.ENTROPY_MONITOR,
            MemorySource.SCAN_LOG,
            MemorySource.CUSTOM,
        ]

    def _stream_memories(
        self, source: MemorySource, limit: Optional[int]
    ) -> Iterable[MemoryRecord]:
        conn = self._connect()
        cursor = conn.cursor()
        sql = """
            SELECT id, timestamp, content, tags
            FROM memories
            WHERE source = ?
            ORDER BY rowid ASC
        """
        params = [source.value]
        if limit is not None:
            sql += " LIMIT ?"
            params.append(int(limit))
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        records: List[MemoryRecord] = []
        for record_id, timestamp, content, tags in rows:
            payload = _deserialize_json(content or "{}")
            tag_list = []
            if tags:
                try:
                    parsed_tags = json.loads(tags)
                except json.JSONDecodeError:
                    parsed_tags = None
                if isinstance(parsed_tags, list):
                    tag_list = parsed_tags
            records.append(
                MemoryRecord(
                    source=source,
                    timestamp=str(timestamp) if timestamp else "",
                    payload=payload,
                    tags=tag_list,
                    record_id=str(record_id) if record_id else None,
                )
            )
        return records

    def _stream_isnad(self, limit: Optional[int]) -> Iterable[MemoryRecord]:
        conn = self._connect()
        cursor = conn.cursor()
        sql = """
            SELECT id, timestamp, content
            FROM isnad
            ORDER BY rowid ASC
        """
        params: List[object] = []
        if limit is not None:
            sql += " LIMIT ?"
            params.append(int(limit))
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        records: List[MemoryRecord] = []
        for record_id, timestamp, content in rows:
            payload = _deserialize_json(content or "{}")
            records.append(
                MemoryRecord(
                    source=MemorySource.PROVENANCE_LEDGER,
                    timestamp=str(timestamp) if timestamp else "",
                    payload=payload,
                    record_id=str(record_id) if record_id else None,
                )
            )
        return records

    def append_action_log(
        self,
        record_type: str,
        action: Optional[str],
        params: Optional[Dict[str, object]],
        result: Optional[Dict[str, object]],
        before_context: Optional[Dict[str, object]],
        after_context: Optional[Dict[str, object]],
        isnad_link: Optional[str],
        timestamp: Optional[str] = None,
    ) -> str:
        record_id = str(uuid.uuid4())
        ts_value = timestamp or _iso_now()
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO action_logs
            (id, type, action, params, result, before_context, after_context, isnad_link, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record_id,
                record_type,
                action,
                _serialize_json(params) if params is not None else None,
                _serialize_json(result) if result is not None else None,
                _serialize_json(before_context) if before_context is not None else None,
                _serialize_json(after_context) if after_context is not None else None,
                isnad_link,
                ts_value,
            ),
        )
        conn.commit()
        conn.close()
        return record_id

    def query_action_logs(
        self,
        record_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, object]]:
        conn = self._connect()
        cursor = conn.cursor()
        sql = """
            SELECT id, type, action, params, result, before_context, after_context, isnad_link, timestamp
            FROM action_logs
        """
        params: List[object] = []
        if record_type:
            sql += " WHERE type = ?"
            params.append(record_type)
        sql += " ORDER BY rowid DESC"
        if limit:
            sql += " LIMIT ?"
            params.append(int(limit))
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        logs: List[Dict[str, object]] = []
        for row in rows:
            (
                record_id,
                row_type,
                action,
                params_json,
                result_json,
                before_json,
                after_json,
                isnad_link,
                timestamp,
            ) = row
            logs.append(
                {
                    "id": record_id,
                    "type": row_type,
                    "action": action,
                    "params": _deserialize_json(params_json) if params_json else {},
                    "result": _deserialize_json(result_json) if result_json else {},
                    "before_context": _deserialize_json(before_json) if before_json else {},
                    "after_context": _deserialize_json(after_json) if after_json else {},
                    "isnad_link": isnad_link,
                    "timestamp": timestamp,
                }
            )
        return logs


def _infer_source_from_filename(filename: str) -> MemorySource:
    name = filename.lower()
    mapping = {
        "self_journal.jsonl": MemorySource.SELF_JOURNAL,
        "summary_balls.jsonl": MemorySource.SUMMARY_BALLS,
        "provenance_ledger.jsonl": MemorySource.PROVENANCE_LEDGER,
        "entropy_monitor_log.jsonl": MemorySource.ENTROPY_MONITOR,
        "scan_log.jsonl": MemorySource.SCAN_LOG,
    }
    return mapping.get(name, MemorySource.CUSTOM)


def migrate_from_jsonl(jsonl_path: Path, sqlite_path: Path) -> SqliteSoulDB:
    jsonl_path = Path(jsonl_path)
    sqlite_path = Path(sqlite_path)
    sqlite_db = SqliteSoulDB(sqlite_path)

    if jsonl_path.is_dir():
        jsonl_db = JsonlSoulDB(base_path=jsonl_path)
        for source in jsonl_db.list_sources():
            for record in jsonl_db.stream(source):
                sqlite_db.append(source, record.payload)
        return sqlite_db

    source = _infer_source_from_filename(jsonl_path.name)
    if not jsonl_path.exists():
        return sqlite_db

    with jsonl_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(record, dict):
                continue
            payload = record.get("payload") if isinstance(record.get("payload"), dict) else record
            if not isinstance(payload, dict):
                continue
            if "timestamp" not in payload and "timestamp" in record:
                payload["timestamp"] = record.get("timestamp")
            if "record_id" not in payload and "record_id" in record:
                payload["record_id"] = record.get("record_id")
            inferred = source
            source_value = record.get("source")
            if isinstance(source_value, str):
                try:
                    inferred = MemorySource(source_value)
                except ValueError:
                    inferred = source
            sqlite_db.append(inferred, payload)
    return sqlite_db
