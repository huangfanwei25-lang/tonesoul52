from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


def _iso_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


@dataclass
class MemoryRecord:
    record_type: str
    timestamp: str


@dataclass
class ActionRecord(MemoryRecord):
    action: str
    params: Dict[str, Any]
    result: Dict[str, Any]
    before: Dict[str, Any]
    after: Dict[str, Any]

    def __init__(
        self,
        action: str,
        params: Optional[Dict[str, Any]] = None,
        result: Optional[Dict[str, Any]] = None,
        before: Optional[Dict[str, Any]] = None,
        after: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None,
    ) -> None:
        super().__init__(record_type="action", timestamp=timestamp or _iso_now())
        self.action = action
        self.params = params or {}
        self.result = result or {}
        self.before = before or {}
        self.after = after or {}


@dataclass
class DecisionRecord(MemoryRecord):
    verdict: str
    reasoning: str
    isnad_link: Optional[str]

    def __init__(
        self,
        verdict: str,
        reasoning: str,
        isnad_link: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> None:
        super().__init__(record_type="decision", timestamp=timestamp or _iso_now())
        self.verdict = verdict
        self.reasoning = reasoning
        self.isnad_link = isnad_link


@dataclass
class CommitmentRecord(MemoryRecord):
    vow: str
    falsifiable_by: Optional[str]
    measurable_via: Optional[str]

    def __init__(
        self,
        vow: str,
        falsifiable_by: Optional[str] = None,
        measurable_via: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> None:
        super().__init__(record_type="commitment", timestamp=timestamp or _iso_now())
        self.vow = vow
        self.falsifiable_by = falsifiable_by
        self.measurable_via = measurable_via
