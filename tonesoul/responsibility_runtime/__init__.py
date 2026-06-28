"""Responsibility runtime contracts.

The current public surface is deterministic and fake-backed: it validates intent form,
separates policy decisions from enforcement, records process traces, and does not call an LLM,
use network policy services, touch real memory, or decide whether evidence semantically supports
a claim.
"""

from .enforcer import EnforcementResult, Enforcer, MemoryAdapter, RecordingMemoryAdapter
from .identity import request_id_for_intent
from .intent_validator import (
    DEFAULT_ALLOWED_SCOPES,
    USES_LLM,
    IntentValidationIssue,
    IntentValidationResult,
    validate_intent,
)
from .memory_claim_checker import (
    MemoryClaimTraceCheck,
    check_memory_claim_trace,
    detect_memory_write_claim,
)
from .memory_output_surface import MemoryOutputSurfaceResult, render_memory_write_result
from .memory_response_composer import MemoryResponseComposition, compose_memory_response
from .policy import (
    DEFAULT_ALLOWED_INTENTS,
    DEFAULT_POLICY_ID,
    FakePolicyEngine,
    PolicyDecision,
    decide_fail_closed,
)
from .responsibility_graph import (
    EdgeProvenance,
    EdgeRejected,
    FakeResponsibilityGraph,
    ResponsibilityEdge,
    edge_from_enforcement,
)
from .trace import (
    InMemoryTraceStore,
    TraceEvent,
    TracePolicyDecision,
    TraceReplayRecord,
    replay_trace,
)

__ts_layer__ = "governance"
__ts_purpose__ = "Responsibility runtime contracts for deterministic intent validation."

__all__ = [
    "DEFAULT_ALLOWED_INTENTS",
    "DEFAULT_ALLOWED_SCOPES",
    "DEFAULT_POLICY_ID",
    "EdgeProvenance",
    "EdgeRejected",
    "Enforcer",
    "EnforcementResult",
    "FakePolicyEngine",
    "FakeResponsibilityGraph",
    "InMemoryTraceStore",
    "ResponsibilityEdge",
    "edge_from_enforcement",
    "USES_LLM",
    "IntentValidationIssue",
    "IntentValidationResult",
    "MemoryAdapter",
    "MemoryClaimTraceCheck",
    "MemoryOutputSurfaceResult",
    "MemoryResponseComposition",
    "PolicyDecision",
    "RecordingMemoryAdapter",
    "TraceEvent",
    "TracePolicyDecision",
    "TraceReplayRecord",
    "check_memory_claim_trace",
    "decide_fail_closed",
    "detect_memory_write_claim",
    "compose_memory_response",
    "render_memory_write_result",
    "replay_trace",
    "request_id_for_intent",
    "validate_intent",
]
