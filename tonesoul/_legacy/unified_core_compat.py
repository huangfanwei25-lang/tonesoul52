"""
UnifiedCore compatibility wrappers extracted during RFC-002 convergence.

These wrappers preserve legacy APIs while runtime chat has moved to
`tonesoul.unified_pipeline.UnifiedPipeline`.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import TYPE_CHECKING, AsyncIterator, Dict, Optional, Tuple

if TYPE_CHECKING:
    from tonesoul.unified_core import UnifiedCore

__deprecated__ = True  # Scheduled for removal. Use tonesoul.unified_pipeline instead.


def process_with_domain_compat(
    core: "UnifiedCore",
    output: str,
    task_domain: str,
    context: Optional[Dict] = None,
) -> Tuple[str, Dict]:
    warnings.warn(
        "UnifiedCore.process_with_domain is deprecated; use UnifiedPipeline + council capability routing.",
        category=DeprecationWarning,
        stacklevel=2,
    )

    coverage, suggestion = core.capability_boundary.check_coverage(task_domain)
    capability_prefix = core.capability_boundary.generate_prefix(coverage)
    tolerance_multiplier = core.capability_boundary.get_tolerance_multiplier(coverage)

    final_output, report = core.process(output, context)
    report["capability"] = {
        "domain": task_domain,
        "coverage": coverage,
        "suggestion": suggestion,
        "tolerance_multiplier": tolerance_multiplier,
    }

    if capability_prefix and not report.get("correction"):
        final_output = capability_prefix + "\n\n" + final_output
        report["capability"]["prefix_added"] = True

    return final_output, report


async def process_with_correction_compat(
    core: "UnifiedCore",
    output: str,
    context: Optional[Dict] = None,
    max_corrections: int = 3,
    correction_threshold: float = 0.7,
) -> Dict:
    warnings.warn(
        "UnifiedCore.process_with_correction is deprecated; use UnifiedPipeline internal deliberation flow.",
        category=DeprecationWarning,
        stacklevel=2,
    )

    correction_history = []
    current_output = output
    events_captured = []

    async def correction_handler(iteration: int, prompt: str) -> AsyncIterator[str]:
        nonlocal current_output

        result_output, result_report = core.process(current_output, context=context)
        correction_info = {
            "iteration": iteration,
            "semantic_tension": result_report.get("semantic_tension"),
            "intervention": result_report.get("intervention"),
            "corrected": result_report.get("correction") is not None,
        }
        correction_history.append(correction_info)

        tension = result_report.get("semantic_tension", {})
        mean_tension = tension.get("mean", 0)

        if mean_tension < correction_threshold or result_report.get("correction") is None:
            yield f"{result_output} <promise>correction_complete</promise>"
            current_output = result_output
        else:
            current_output = result_output
            yield result_output

    try:
        from ..loop import LoopConfig, LoopEngine
    except ImportError:
        from loop import LoopConfig, LoopEngine

    config = LoopConfig(
        prompt=output,
        max_iterations=max_corrections,
        promise_phrase="correction_complete",
        timeout_ms=60000,
    )
    engine = LoopEngine(config=config, on_iteration=correction_handler)

    import asyncio

    async def collect_events() -> None:
        async for event in engine.events_stream():
            events_captured.append(event)

    events_task = asyncio.create_task(collect_events())
    loop_result = await engine.start()
    await events_task

    return {
        "final_output": current_output,
        "corrections": loop_result.iterations,
        "state": loop_result.state,
        "duration_ms": loop_result.duration_ms,
        "events": events_captured,
        "correction_history": correction_history,
        "success": loop_result.state == "complete",
    }


def create_core_compat(unified_core_cls: type["UnifiedCore"], persona_id: str, base_path: Path):
    persona_path = base_path / "memory" / "personas" / f"{persona_id}.yaml"
    return unified_core_cls(persona_path=persona_path)
