"""Deterministic fake policy decisions for the responsibility runtime.

This module is a local decision point for Phase 2 tests. It is not OPA, does not call a
network service, and does not judge whether evidence semantically supports a claim.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .intent_validator import DEFAULT_ALLOWED_SCOPES, IntentValidationResult

__ts_layer__ = "governance"
__ts_purpose__ = "Fake responsibility-runtime policy decision point."

USES_LLM = False
USES_NETWORK = False

DEFAULT_ALLOWED_INTENTS = frozenset({"memory.write.propose", "memory.read.request"})
DEFAULT_POLICY_ID = "fake.responsibility_runtime.v0"


@dataclass(frozen=True)
class PolicyDecision:
    """Decision-point output consumed by the Enforcer.

    `allow` must be a real bool. The Enforcer treats missing, malformed, or non-matching
    decisions as deny.
    """

    allow: bool
    reason: str
    policy_id: str
    intent: str
    requested_scope: str

    def __post_init__(self) -> None:
        if type(self.allow) is not bool:
            raise TypeError("allow must be a bool")
        for field_name in ("reason", "policy_id", "intent", "requested_scope"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")

    @classmethod
    def allow_action(
        cls,
        *,
        intent: str,
        requested_scope: str,
        reason: str = "fake policy allowed validated intent",
        policy_id: str = DEFAULT_POLICY_ID,
    ) -> PolicyDecision:
        return cls(
            allow=True,
            reason=reason,
            policy_id=policy_id,
            intent=intent,
            requested_scope=requested_scope,
        )

    @classmethod
    def deny_action(
        cls,
        *,
        intent: str,
        requested_scope: str,
        reason: str,
        policy_id: str = DEFAULT_POLICY_ID,
    ) -> PolicyDecision:
        return cls(
            allow=False,
            reason=reason,
            policy_id=policy_id,
            intent=intent,
            requested_scope=requested_scope,
        )


class FakePolicyEngine:
    """Deterministic local policy decision point for validated Phase-1 intents."""

    def __init__(
        self,
        *,
        allowed_intents: Iterable[str] | None = None,
        allowed_scopes: Iterable[str] | None = None,
        policy_id: str = DEFAULT_POLICY_ID,
    ) -> None:
        self.allowed_intents = (
            DEFAULT_ALLOWED_INTENTS if allowed_intents is None else frozenset(allowed_intents)
        )
        self.allowed_scopes = (
            DEFAULT_ALLOWED_SCOPES if allowed_scopes is None else frozenset(allowed_scopes)
        )
        self.policy_id = policy_id

    def decide(self, validation: IntentValidationResult) -> PolicyDecision:
        """Return allow/deny for a Phase-1 validation result without revalidating form."""

        intent, requested_scope = _intent_scope_for_decision(validation)
        if not validation.accepted or validation.normalized_payload is None:
            return PolicyDecision.deny_action(
                intent=intent,
                requested_scope=requested_scope,
                reason="intent failed Phase-1 validation",
                policy_id=self.policy_id,
            )

        payload = validation.normalized_payload
        intent = str(payload.get("intent") or intent)
        requested_scope = str(payload.get("requested_scope") or requested_scope)

        if intent not in self.allowed_intents:
            return PolicyDecision.deny_action(
                intent=intent,
                requested_scope=requested_scope,
                reason=f"intent not allowed by fake policy: {intent}",
                policy_id=self.policy_id,
            )
        if requested_scope not in self.allowed_scopes:
            return PolicyDecision.deny_action(
                intent=intent,
                requested_scope=requested_scope,
                reason=f"scope not allowed by fake policy: {requested_scope}",
                policy_id=self.policy_id,
            )

        return PolicyDecision.allow_action(
            intent=intent,
            requested_scope=requested_scope,
            policy_id=self.policy_id,
        )


def decide_fail_closed(
    decision_point: object,
    validation: IntentValidationResult,
    *,
    fallback_policy_id: str = DEFAULT_POLICY_ID,
) -> PolicyDecision:
    """Call a decision point and convert any error or malformed output into deny."""

    intent, requested_scope = _intent_scope_for_decision(validation)
    try:
        decision = decision_point.decide(validation)  # type: ignore[attr-defined]
    except Exception as exc:
        return PolicyDecision.deny_action(
            intent=intent,
            requested_scope=requested_scope,
            reason=f"decision point failed closed: {type(exc).__name__}",
            policy_id=fallback_policy_id,
        )

    if isinstance(decision, PolicyDecision):
        return decision

    return PolicyDecision.deny_action(
        intent=intent,
        requested_scope=requested_scope,
        reason="decision point returned malformed decision",
        policy_id=fallback_policy_id,
    )


def _intent_scope_for_decision(validation: IntentValidationResult) -> tuple[str, str]:
    if validation.normalized_payload is None:
        return validation.intent or "unknown", "unknown"
    return (
        str(validation.normalized_payload.get("intent") or validation.intent or "unknown"),
        str(validation.normalized_payload.get("requested_scope") or "unknown"),
    )
