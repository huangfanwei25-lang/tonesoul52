"""Deterministic output surface for memory-write acknowledgements.

The model should not freely author "I remembered/saved this" messages. It should propose a
memory intent; only this trace-backed surface may render an acknowledgement that a memory write
actually happened.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from .enforcer import EnforcementResult
from .memory_claim_checker import MemoryClaimStatus, check_memory_claim_trace
from .trace import TraceEvent

__ts_layer__ = "governance"
__ts_purpose__ = "Trace-backed deterministic renderer for memory-write output."

USES_LLM = False
USES_NETWORK = False

MemoryOutputSurfaceStatus = Literal[
    "memory_write_acknowledged",
    "memory_write_denied",
    "not_memory_write",
]


@dataclass(frozen=True)
class MemoryOutputSurfaceResult:
    """Rendered memory-output text plus the trace-backed claim check for that text."""

    status: MemoryOutputSurfaceStatus
    text: str
    request_id: str
    trace_seq: int
    claim_check_status: MemoryClaimStatus
    reason: str


def render_memory_write_result(result: EnforcementResult) -> MemoryOutputSurfaceResult:
    """Render the only sanctioned memory-write acknowledgement.

    Success requires both the enforcer result and its trace event to say the write executed.
    Anything else renders a non-claim denial or non-memory message.
    """

    event = result.trace_event
    trace_events = (event,)
    if event.intent != "memory.write.propose":
        text = (
            "No memory write was requested. "
            f"Trace request_id={_safe_inline(result.request_id)} seq={event.seq}."
        )
        return _surface(
            status="not_memory_write",
            text=text,
            result=result,
            reason="trace event is not a memory.write.propose intent",
            trace_events=trace_events,
        )

    if _is_trace_backed_memory_write(result):
        scope = _safe_inline(
            str(
                event.intent_payload.get("requested_scope")
                or event.policy_decision.requested_scope
                or "unknown"
            )
        )
        text = (
            "I've saved this preference. "
            f"Trace request_id={_safe_inline(result.request_id)} "
            f"seq={event.seq} scope={scope} evidence_refs={len(event.evidence_refs)}."
        )
        return _surface(
            status="memory_write_acknowledged",
            text=text,
            result=result,
            reason="memory-write acknowledgement rendered from executed trace",
            trace_events=trace_events,
        )

    text = (
        "I did not save this. "
        f"Memory write was not executed: {_safe_inline(result.reason)} "
        f"Trace request_id={_safe_inline(result.request_id)} seq={event.seq}."
    )
    return _surface(
        status="memory_write_denied",
        text=text,
        result=result,
        reason="memory-write acknowledgement suppressed because trace is not executed",
        trace_events=trace_events,
    )


def _is_trace_backed_memory_write(result: EnforcementResult) -> bool:
    event = result.trace_event
    return (
        result.executed is True
        and result.intent == "memory.write.propose"
        and result.request_id == event.request_id
        and event.intent == "memory.write.propose"
        and event.enforcer_result == "executed"
        and event.policy_decision.allow is True
    )


def _surface(
    *,
    status: MemoryOutputSurfaceStatus,
    text: str,
    result: EnforcementResult,
    reason: str,
    trace_events: tuple[TraceEvent, ...],
) -> MemoryOutputSurfaceResult:
    claim_check = check_memory_claim_trace(text, trace_events)
    return MemoryOutputSurfaceResult(
        status=status,
        text=text,
        request_id=result.request_id,
        trace_seq=result.trace_event.seq,
        claim_check_status=claim_check.status,
        reason=reason,
    )


def _safe_inline(value: str, *, max_len: int = 160) -> str:
    compact = re.sub(r"[\x00-\x1f\x7f]+", " ", value)
    compact = re.sub(r"\s+", " ", compact).strip()
    if len(compact) <= max_len:
        return compact
    return compact[: max_len - 3].rstrip() + "..."
