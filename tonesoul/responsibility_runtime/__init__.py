"""Responsibility runtime contracts.

The current public surface is deterministic and fake-backed: it validates intent form,
separates policy decisions from enforcement, records process traces, and does not call an LLM,
use network policy services, touch real memory, or decide whether evidence semantically supports
a claim.
"""

from .enforcer import EnforcementResult, Enforcer, MemoryAdapter, RecordingMemoryAdapter
from .intent_validator import (
    DEFAULT_ALLOWED_SCOPES,
    USES_LLM,
    IntentValidationIssue,
    IntentValidationResult,
    validate_intent,
)
from .policy import (
    DEFAULT_ALLOWED_INTENTS,
    DEFAULT_POLICY_ID,
    FakePolicyEngine,
    PolicyDecision,
    decide_fail_closed,
)
from .trace import (
    InMemoryTraceStore,
    TraceEvent,
    TracePolicyDecision,
    TraceReplayRecord,
    replay_trace,
    request_id_for_intent,
)

__ts_layer__ = "governance"
__ts_purpose__ = "Responsibility runtime contracts for deterministic intent validation."

__all__ = [
    "DEFAULT_ALLOWED_INTENTS",
    "DEFAULT_ALLOWED_SCOPES",
    "DEFAULT_POLICY_ID",
    "Enforcer",
    "EnforcementResult",
    "FakePolicyEngine",
    "InMemoryTraceStore",
    "USES_LLM",
    "IntentValidationIssue",
    "IntentValidationResult",
    "MemoryAdapter",
    "PolicyDecision",
    "RecordingMemoryAdapter",
    "TraceEvent",
    "TracePolicyDecision",
    "TraceReplayRecord",
    "decide_fail_closed",
    "replay_trace",
    "request_id_for_intent",
    "validate_intent",
]
