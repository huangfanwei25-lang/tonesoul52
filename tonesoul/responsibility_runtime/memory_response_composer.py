"""Compose model text with runtime-controlled memory output.

The composer is the boundary between free model text and privileged memory-write
acknowledgements. The model may propose memory intents, but it must not author the
"I saved/remembered this" acknowledgement itself.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

from .enforcer import EnforcementResult
from .memory_claim_checker import MemoryClaimTraceCheck, check_memory_claim_trace
from .memory_output_surface import MemoryOutputSurfaceResult, render_memory_write_result
from .trace import TraceEvent

__ts_layer__ = "governance"
__ts_purpose__ = "Runtime composer that appends trace-backed memory output and blocks model-authored acknowledgements."

USES_LLM = False
USES_NETWORK = False

MemoryResponseCompositionStatus = Literal["composed", "blocked_model_memory_claim"]


@dataclass(frozen=True)
class MemoryResponseComposition:
    """Final response assembled from model text and runtime memory surfaces."""

    status: MemoryResponseCompositionStatus
    text: str
    model_claim_check: MemoryClaimTraceCheck
    memory_surfaces: tuple[MemoryOutputSurfaceResult, ...]
    trace_events: tuple[TraceEvent, ...]
    reason: str


def compose_memory_response(
    model_text: str,
    enforcement_results: Iterable[EnforcementResult] = (),
) -> MemoryResponseComposition:
    """Compose a final response without letting model text self-acknowledge memory writes.

    Supported memory-write claim shapes in `model_text` are blocked with an empty-trace check.
    Runtime memory-write results are rendered separately through `render_memory_write_result`.
    This is not a semantic paraphrase detector; fuzzy memory claims remain a measured gap.
    """

    text = _normalize_model_text(model_text)
    model_claim_check = check_memory_claim_trace(text, ())
    results = tuple(enforcement_results)
    memory_results = tuple(result for result in results if _is_memory_write_result(result))
    trace_events = tuple(result.trace_event for result in results)
    if model_claim_check.claim_detected:
        return MemoryResponseComposition(
            status="blocked_model_memory_claim",
            text=(
                "Response blocked: model-authored memory-write acknowledgements must be "
                "rendered by the runtime output surface."
            ),
            model_claim_check=model_claim_check,
            memory_surfaces=(),
            trace_events=trace_events,
            reason="model text contained a supported memory-write acknowledgement shape",
        )

    memory_surfaces = tuple(render_memory_write_result(result) for result in memory_results)
    final_text = _join_response_parts((text, *(surface.text for surface in memory_surfaces)))
    return MemoryResponseComposition(
        status="composed",
        text=final_text,
        model_claim_check=model_claim_check,
        memory_surfaces=memory_surfaces,
        trace_events=trace_events,
        reason="model text accepted and runtime memory surfaces appended",
    )


def _is_memory_write_result(result: EnforcementResult) -> bool:
    return (
        result.intent == "memory.write.propose"
        or result.trace_event.intent == "memory.write.propose"
    )


def _normalize_model_text(model_text: str) -> str:
    return (model_text or "").strip()


def _join_response_parts(parts: Iterable[str]) -> str:
    return "\n\n".join(part.strip() for part in parts if part and part.strip())
