"""Append-only process trace for responsibility-runtime decisions.

Trace events record what the runtime did. They do not prove that a claim is true, and this
Phase 3 store is not yet tamper-evident.
"""

from __future__ import annotations

import copy
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from .policy import PolicyDecision

__ts_layer__ = "governance"
__ts_purpose__ = "Append-only responsibility-runtime trace skeleton."

USES_LLM = False
USES_NETWORK = False


@dataclass(frozen=True)
class TracePolicyDecision:
    """Trace-safe copy of a policy decision."""

    allow: bool
    reason: str
    policy_id: str
    intent: str
    requested_scope: str
    request_id: str


@dataclass(frozen=True)
class TraceEvent:
    """Immutable process fact for a responsibility-runtime decision."""

    seq: int
    request_id: str
    intent: str
    intent_payload: Mapping[str, Any]
    policy_decision: TracePolicyDecision
    enforcer_result: str
    evidence_refs: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class TraceReplayRecord:
    """Replay summary reconstructed from trace events alone."""

    request_id: str
    intent: str
    policy_allow: bool
    policy_id: str
    enforcer_result: str
    evidence_refs: tuple[str, ...]
    deny_reason: str | None


class InMemoryTraceStore:
    """Append-only in-memory trace store for Phase 3 tests."""

    def __init__(self) -> None:
        self._events: list[TraceEvent] = []

    def append(
        self,
        *,
        request_id: str,
        intent_payload: Mapping[str, Any] | None,
        policy_decision: PolicyDecision,
        enforcer_result: str,
        reason: str,
    ) -> TraceEvent:
        payload = copy.deepcopy(dict(intent_payload or {}))
        intent = str(payload.get("intent") or policy_decision.intent)
        event = TraceEvent(
            seq=len(self._events) + 1,
            request_id=request_id,
            intent=intent,
            intent_payload=MappingProxyType(payload),
            policy_decision=TracePolicyDecision(
                allow=policy_decision.allow,
                reason=policy_decision.reason,
                policy_id=policy_decision.policy_id,
                intent=policy_decision.intent,
                requested_scope=policy_decision.requested_scope,
                request_id=policy_decision.request_id,
            ),
            enforcer_result=enforcer_result,
            evidence_refs=tuple(str(ref) for ref in payload.get("evidence_refs", ())),
            reason=reason,
        )
        self._events.append(event)
        return event

    @property
    def events(self) -> tuple[TraceEvent, ...]:
        return tuple(self._events)


def replay_trace(events: Iterable[TraceEvent]) -> tuple[TraceReplayRecord, ...]:
    """Reconstruct request outcomes from trace events alone."""

    records: list[TraceReplayRecord] = []
    for event in events:
        records.append(
            TraceReplayRecord(
                request_id=event.request_id,
                intent=event.intent,
                policy_allow=event.policy_decision.allow,
                policy_id=event.policy_decision.policy_id,
                enforcer_result=event.enforcer_result,
                evidence_refs=event.evidence_refs,
                deny_reason=None if event.enforcer_result == "executed" else event.reason,
            )
        )
    return tuple(records)
