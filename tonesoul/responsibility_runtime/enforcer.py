"""Deterministic enforcement boundary for responsibility-runtime intents.

The Enforcer consumes a PolicyDecision from a separate decision point. It does not decide
policy itself and only calls the fake adapter on an explicit `PolicyDecision.allow is True`.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol

from .intent_validator import IntentValidationResult
from .policy import PolicyDecision
from .trace import InMemoryTraceStore, TraceEvent, request_id_for_intent

__ts_layer__ = "governance"
__ts_purpose__ = "Responsibility-runtime Enforcer that consumes explicit policy decisions."

USES_LLM = False
USES_NETWORK = False


class MemoryAdapter(Protocol):
    """Minimal fake adapter protocol for Phase 2; real memory is out of scope."""

    def execute(self, intent_payload: Mapping[str, Any]) -> Mapping[str, Any]:
        """Execute an already-authorized intent."""


@dataclass(frozen=True)
class EnforcementResult:
    """Result of enforcing a validated intent against a policy decision."""

    executed: bool
    request_id: str
    intent: str
    reason: str
    trace_event: TraceEvent
    adapter_result: Mapping[str, Any] | None = None


class RecordingMemoryAdapter:
    """Fake memory adapter that records calls for deny-path tests."""

    def __init__(self) -> None:
        self.calls: list[Mapping[str, Any]] = []

    def execute(self, intent_payload: Mapping[str, Any]) -> Mapping[str, Any]:
        payload = dict(intent_payload)
        self.calls.append(payload)
        return {
            "status": "recorded",
            "intent": payload.get("intent"),
            "requested_scope": payload.get("requested_scope"),
        }

    @property
    def call_count(self) -> int:
        return len(self.calls)


class Enforcer:
    """Apply explicit decisions to a fake adapter and append process trace."""

    def __init__(
        self,
        *,
        memory_adapter: MemoryAdapter,
        trace_store: InMemoryTraceStore,
    ) -> None:
        self.memory_adapter = memory_adapter
        self.trace_store = trace_store

    def enforce(
        self,
        validation: IntentValidationResult,
        decision: object,
    ) -> EnforcementResult:
        payload = validation.normalized_payload
        request_id = request_id_for_intent(payload)
        intent = str((payload or {}).get("intent") or validation.intent or "unknown")

        if not validation.accepted or payload is None:
            return self._deny(
                request_id=request_id,
                intent=intent,
                payload=payload,
                decision=_invalid_decision(
                    intent=intent,
                    requested_scope=str((payload or {}).get("requested_scope") or "unknown"),
                    reason="validated intent required",
                ),
                reason="validated intent required",
            )

        if not isinstance(decision, PolicyDecision):
            return self._deny(
                request_id=request_id,
                intent=intent,
                payload=payload,
                decision=_invalid_decision(
                    intent=intent,
                    requested_scope=str(payload.get("requested_scope") or "unknown"),
                    reason="missing or malformed policy decision",
                ),
                reason="missing or malformed policy decision",
            )

        if not _decision_applies_to_payload(decision, payload):
            return self._deny(
                request_id=request_id,
                intent=intent,
                payload=payload,
                decision=PolicyDecision.deny_action(
                    intent=decision.intent,
                    requested_scope=decision.requested_scope,
                    reason="policy decision does not apply to intent",
                    policy_id=decision.policy_id,
                ),
                reason="policy decision does not apply to intent",
            )

        if decision.allow is not True:
            return self._deny(
                request_id=request_id,
                intent=intent,
                payload=payload,
                decision=decision,
                reason=decision.reason,
            )

        adapter_result = self.memory_adapter.execute(payload)
        trace_event = self.trace_store.append(
            request_id=request_id,
            intent_payload=payload,
            policy_decision=decision,
            enforcer_result="executed",
            reason=decision.reason,
        )
        return EnforcementResult(
            executed=True,
            request_id=request_id,
            intent=intent,
            reason=decision.reason,
            trace_event=trace_event,
            adapter_result=adapter_result,
        )

    def _deny(
        self,
        *,
        request_id: str,
        intent: str,
        payload: Mapping[str, Any] | None,
        decision: PolicyDecision,
        reason: str,
    ) -> EnforcementResult:
        trace_event = self.trace_store.append(
            request_id=request_id,
            intent_payload=payload,
            policy_decision=decision,
            enforcer_result="denied",
            reason=reason,
        )
        return EnforcementResult(
            executed=False,
            request_id=request_id,
            intent=intent,
            reason=reason,
            trace_event=trace_event,
            adapter_result=None,
        )


def _decision_applies_to_payload(decision: PolicyDecision, payload: Mapping[str, Any]) -> bool:
    return decision.intent == payload.get("intent") and decision.requested_scope == payload.get(
        "requested_scope"
    )


def _invalid_decision(*, intent: str, requested_scope: str, reason: str) -> PolicyDecision:
    return PolicyDecision.deny_action(
        intent=intent,
        requested_scope=requested_scope,
        reason=reason,
        policy_id="invalid.policy_decision",
    )
