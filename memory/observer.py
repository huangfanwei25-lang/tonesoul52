from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Optional

from tonesoul.memory.soul_db import SqliteSoulDB
from memory.protocols import ActionRecord, DecisionRecord, CommitmentRecord


class MemoryObserver:
    def __init__(self, soul_db: Optional[SqliteSoulDB] = None) -> None:
        self.soul_db = soul_db or SqliteSoulDB()

    def log_action(
        self,
        action: str,
        params: Optional[Dict[str, Any]] = None,
        result: Optional[Dict[str, Any]] = None,
        before_context: Optional[Dict[str, Any]] = None,
        after_context: Optional[Dict[str, Any]] = None,
        isnad_link: Optional[str] = None,
        stream: str = "raw",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        record = ActionRecord(
            action=action,
            params=params,
            result=result,
            before=before_context,
            after=after_context,
            stream=stream,
            metadata=metadata,
        )
        payload = asdict(record)
        return self._write_log(
            record_type=record.record_type,
            action=record.action,
            params=payload.get("params"),
            result=payload.get("result"),
            before_context=payload.get("before"),
            after_context=payload.get("after"),
            isnad_link=isnad_link,
            timestamp=record.timestamp,
            stream=payload.get("stream"),
            metadata=payload.get("metadata"),
        )

    def log_decision(
        self,
        council_verdict: Any,
        context: Optional[Dict[str, Any]] = None,
        stream: str = "raw",
    ) -> str:
        verdict_value = getattr(council_verdict, "verdict", None)
        verdict_str = getattr(verdict_value, "value", verdict_value) or "unknown"
        reasoning = getattr(council_verdict, "summary", "")
        if getattr(council_verdict, "human_summary", None):
            reasoning = str(council_verdict.human_summary)
        record = DecisionRecord(
            verdict=str(verdict_str),
            reasoning=str(reasoning),
            isnad_link=(context or {}).get("isnad_link"),
            stream=stream,
            metadata=(context or {}).get("metadata"),
        )
        payload = asdict(record)
        extra = {
            "structured_output": (
                council_verdict.to_structured_output()
                if hasattr(council_verdict, "to_structured_output")
                else None
            ),
            "context": context or {},
        }
        return self._write_log(
            record_type=record.record_type,
            action="council_verdict",
            params=extra,
            result=payload,
            before_context=None,
            after_context=None,
            isnad_link=record.isnad_link,
            timestamp=record.timestamp,
            stream=payload.get("stream"),
            metadata=payload.get("metadata"),
        )

    def log_commitment(
        self,
        vow: str,
        falsifiable_by: Optional[str] = None,
        measurable_via: Optional[str] = None,
        isnad_link: Optional[str] = None,
        stream: str = "raw",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        record = CommitmentRecord(
            vow=vow,
            falsifiable_by=falsifiable_by,
            measurable_via=measurable_via,
            stream=stream,
            metadata=metadata,
        )
        payload = asdict(record)
        return self._write_log(
            record_type=record.record_type,
            action="commitment",
            params=payload,
            result=None,
            before_context=None,
            after_context=None,
            isnad_link=isnad_link,
            timestamp=record.timestamp,
            stream=payload.get("stream"),
            metadata=payload.get("metadata"),
        )

    def query(self, type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        return self.soul_db.query_action_logs(record_type=type, limit=limit)

    def _write_log(
        self,
        record_type: str,
        action: Optional[str],
        params: Optional[Dict[str, Any]],
        result: Optional[Dict[str, Any]],
        before_context: Optional[Dict[str, Any]],
        after_context: Optional[Dict[str, Any]],
        isnad_link: Optional[str],
        timestamp: str,
        stream: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        return self.soul_db.append_action_log(
            record_type=record_type,
            action=action,
            params=params,
            result=result,
            before_context=before_context,
            after_context=after_context,
            isnad_link=isnad_link,
            timestamp=timestamp,
            stream=stream,
            metadata=metadata,
        )
