"""Responsibility runtime contracts.

This package starts with deterministic intent-form validation only. It does not call an LLM,
authorize actions, write memory, or decide whether evidence semantically supports a claim.
"""

from .intent_validator import (
    DEFAULT_ALLOWED_SCOPES,
    USES_LLM,
    IntentValidationIssue,
    IntentValidationResult,
    validate_intent,
)

__ts_layer__ = "governance"
__ts_purpose__ = "Responsibility runtime contracts for deterministic intent validation."

__all__ = [
    "DEFAULT_ALLOWED_SCOPES",
    "USES_LLM",
    "IntentValidationIssue",
    "IntentValidationResult",
    "validate_intent",
]
