from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timezone, datetime
from typing import Any, Dict, Optional


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(kw_only=True)
class MemoryRecord:
    record_type: str
    timestamp: str = field(default_factory=_iso_now)
    stream: str = "raw"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(kw_only=True)
class ActionRecord(MemoryRecord):
    action: str
    params: Dict[str, Any] = field(default_factory=dict)
    result: Dict[str, Any] = field(default_factory=dict)
    before: Dict[str, Any] = field(default_factory=dict)
    after: Dict[str, Any] = field(default_factory=dict)

    def __init__(
        self,
        *,
        action: str,
        params: Optional[Dict[str, Any]] = None,
        result: Optional[Dict[str, Any]] = None,
        before: Optional[Dict[str, Any]] = None,
        after: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None,
        stream: str = "raw",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.record_type = "action"
        self.timestamp = timestamp or _iso_now()
        self.stream = stream
        self.metadata = metadata or {}
        self.action = action
        self.params = params or {}
        self.result = result or {}
        self.before = before or {}
        self.after = after or {}


@dataclass(kw_only=True)
class DecisionRecord(MemoryRecord):
    verdict: str
    reasoning: str
    isnad_link: Optional[str] = None

    def __init__(
        self,
        *,
        verdict: str,
        reasoning: str,
        isnad_link: Optional[str] = None,
        timestamp: Optional[str] = None,
        stream: str = "raw",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.record_type = "decision"
        self.timestamp = timestamp or _iso_now()
        self.stream = stream
        self.metadata = metadata or {}
        self.verdict = verdict
        self.reasoning = reasoning
        self.isnad_link = isnad_link


@dataclass(kw_only=True)
class CommitmentRecord(MemoryRecord):
    vow: str
    falsifiable_by: Optional[str] = None
    measurable_via: Optional[str] = None

    def __init__(
        self,
        *,
        vow: str,
        falsifiable_by: Optional[str] = None,
        measurable_via: Optional[str] = None,
        timestamp: Optional[str] = None,
        stream: str = "raw",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.record_type = "commitment"
        self.timestamp = timestamp or _iso_now()
        self.stream = stream
        self.metadata = metadata or {}
        self.vow = vow
        self.falsifiable_by = falsifiable_by
        self.measurable_via = measurable_via
