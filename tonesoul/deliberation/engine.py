"""
ToneSoul 2.0 Internal Deliberation Engine

The main orchestrator that:
1. Invokes all three perspectives in parallel
2. Detects tensions between viewpoints
3. Synthesizes final output using Semantic Gravity
4. Respects Guardian veto power

This replaces the post-hoc persona system with
pre-output internal deliberation.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional

from .adaptive_rounds import TENSION_LOW, aggregate_tension_severity, calculate_debate_rounds
from .gravity import create_semantic_gravity
from .persona_track_record import create_persona_track_record
from .perspectives import (
    BasePerspective,
    create_perspectives,
)
from .types import (
    DeliberationContext,
    PerspectiveType,
    RoundResult,
    SynthesizedResponse,
    ViewPoint,
)


class InternalDeliberation:
    """
    ToneSoul 2.0 Core Engine

    The three internal voices (Muse, Logos, Aegis) deliberate
    BEFORE any output is generated, not after.

    Usage:
        engine = InternalDeliberation()
        result = await engine.deliberate(context)
        # or sync:
        result = engine.deliberate_sync(context)
    """

    def __init__(self):
        # Initialize three perspectives
        self._perspectives = create_perspectives()

        self._persona_track_record = create_persona_track_record()

        # Initialize synthesis engine
        self._gravity = create_semantic_gravity(track_record=self._persona_track_record)

        # State tracking
        self._deliberation_count = 0
        self._last_viewpoints: List[ViewPoint] = []

    async def deliberate(self, context: DeliberationContext) -> SynthesizedResponse:
        """
        Async deliberation - all perspectives think in parallel.

        This is more efficient as we don't wait for each
        perspective sequentially.
        """
        result, viewpoints = await self._run_adaptive_deliberation_async(context)
        self._deliberation_count += 1
        self._last_viewpoints = viewpoints
        return result

    def deliberate_sync(self, context: DeliberationContext) -> SynthesizedResponse:
        """
        Sync deliberation - for non-async contexts.

        Uses asyncio.run() or sequential execution as fallback.
        """
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            result, viewpoints = asyncio.run(self._run_adaptive_deliberation_async(context))
        else:
            # Already running inside an event loop; keep this sync seam explicit.
            result, viewpoints = self._run_adaptive_deliberation_sync(context)

        self._deliberation_count += 1
        self._last_viewpoints = viewpoints

        return result

    async def _run_adaptive_deliberation_async(
        self, context: DeliberationContext
    ) -> tuple[SynthesizedResponse, List[ViewPoint]]:
        start_time = time.time()
        round_results: List[RoundResult] = []

        viewpoints = await self._parallel_think(context)
        round_results.append(self._build_round_result(1, viewpoints, context))
        target_rounds = calculate_debate_rounds(round_results[0].tensions)

        aegis = self._gravity._find_aegis(viewpoints)
        if aegis and aegis.veto_triggered:
            elapsed_ms = (time.time() - start_time) * 1000
            result = self._gravity._guardian_override(aegis, viewpoints, elapsed_ms)
            self._attach_round_metadata(result, round_results)
            return result, viewpoints

        current_round = 2
        while current_round <= target_rounds:
            debate_context = self._build_debate_context(context, viewpoints, current_round)
            viewpoints = await self._parallel_think(debate_context)
            current_round_result = self._build_round_result(
                current_round, viewpoints, debate_context
            )
            round_results.append(current_round_result)

            aegis = self._gravity._find_aegis(viewpoints)
            if aegis and aegis.veto_triggered:
                elapsed_ms = (time.time() - start_time) * 1000
                result = self._gravity._guardian_override(aegis, viewpoints, elapsed_ms)
                self._attach_round_metadata(result, round_results)
                return result, viewpoints

            if current_round_result.aggregate_tension < TENSION_LOW:
                break
            current_round += 1

        elapsed_ms = (time.time() - start_time) * 1000
        result = self._gravity.synthesize(viewpoints, context, elapsed_ms)
        self._attach_round_metadata(result, round_results)
        return result, viewpoints

    def _run_adaptive_deliberation_sync(
        self, context: DeliberationContext
    ) -> tuple[SynthesizedResponse, List[ViewPoint]]:
        start_time = time.time()
        round_results: List[RoundResult] = []

        viewpoints = self._sequential_think(context)
        round_results.append(self._build_round_result(1, viewpoints, context))
        target_rounds = calculate_debate_rounds(round_results[0].tensions)

        aegis = self._gravity._find_aegis(viewpoints)
        if aegis and aegis.veto_triggered:
            elapsed_ms = (time.time() - start_time) * 1000
            result = self._gravity._guardian_override(aegis, viewpoints, elapsed_ms)
            self._attach_round_metadata(result, round_results)
            return result, viewpoints

        current_round = 2
        while current_round <= target_rounds:
            debate_context = self._build_debate_context(context, viewpoints, current_round)
            viewpoints = self._sequential_think(debate_context)
            current_round_result = self._build_round_result(
                current_round, viewpoints, debate_context
            )
            round_results.append(current_round_result)

            aegis = self._gravity._find_aegis(viewpoints)
            if aegis and aegis.veto_triggered:
                elapsed_ms = (time.time() - start_time) * 1000
                result = self._gravity._guardian_override(aegis, viewpoints, elapsed_ms)
                self._attach_round_metadata(result, round_results)
                return result, viewpoints

            if current_round_result.aggregate_tension < TENSION_LOW:
                break
            current_round += 1

        elapsed_ms = (time.time() - start_time) * 1000
        result = self._gravity.synthesize(viewpoints, context, elapsed_ms)
        self._attach_round_metadata(result, round_results)
        return result, viewpoints

    def _build_round_result(
        self,
        round_number: int,
        viewpoints: List[ViewPoint],
        context: DeliberationContext,
    ) -> RoundResult:
        tensions = self._gravity.detect_tensions(viewpoints)
        weights = self._gravity.calculate_weights(viewpoints, context)
        return RoundResult(
            round_number=round_number,
            viewpoints=viewpoints,
            tensions=tensions,
            weights=weights,
            aggregate_tension=aggregate_tension_severity(tensions),
        )

    @staticmethod
    def _build_debate_context(
        context: DeliberationContext,
        viewpoints: List[ViewPoint],
        round_number: int,
    ) -> DeliberationContext:
        return DeliberationContext(
            user_input=context.user_input,
            conversation_history=context.conversation_history,
            commit_stack=context.commit_stack,
            trajectory=context.trajectory,
            entropy_state=context.entropy_state,
            tone_strength=context.tone_strength,
            resonance_state=context.resonance_state,
            loop_detected=context.loop_detected,
            scenario_envelope=dict(context.scenario_envelope or {}),
            prior_viewpoints=[viewpoint.to_dict() for viewpoint in viewpoints],
            debate_round=round_number,
        )

    @staticmethod
    def _attach_round_metadata(result: Any, round_results: List[RoundResult]) -> None:
        if hasattr(result, "rounds_used"):
            result.rounds_used = len(round_results)
        if hasattr(result, "round_results"):
            result.round_results = list(round_results)

    async def _parallel_think(self, context: DeliberationContext) -> List[ViewPoint]:
        """Execute all perspectives in parallel."""

        async def think_async(perspective: BasePerspective) -> ViewPoint:
            # Wrap sync think() in async
            return perspective.think(context)

        tasks = [
            think_async(self._perspectives[PerspectiveType.MUSE]),
            think_async(self._perspectives[PerspectiveType.LOGOS]),
            think_async(self._perspectives[PerspectiveType.AEGIS]),
        ]

        viewpoints = await asyncio.gather(*tasks)
        return list(viewpoints)

    def _sequential_think(self, context: DeliberationContext) -> List[ViewPoint]:
        """Execute perspectives sequentially (fallback)."""
        return [
            self._perspectives[PerspectiveType.MUSE].think(context),
            self._perspectives[PerspectiveType.LOGOS].think(context),
            self._perspectives[PerspectiveType.AEGIS].think(context),
        ]

    def get_last_debate(self) -> Dict[str, Any]:
        """Get the last internal debate for debugging/transparency."""
        if not self._last_viewpoints:
            return {"status": "no_debate_yet"}

        return {
            "viewpoints": [vp.to_dict() for vp in self._last_viewpoints],
            "total_deliberations": self._deliberation_count,
        }

    @property
    def deliberation_count(self) -> int:
        return self._deliberation_count

    def record_outcome(
        self,
        dominant_voice: Optional[str],
        verdict: str,
        resonance_state: str = "unknown",
        loop_detected: bool = False,
    ) -> None:
        """Persist post-council outcome for dynamic future weighting."""
        if not dominant_voice:
            return
        self._persona_track_record.record_outcome(
            perspective=str(dominant_voice),
            verdict=str(verdict),
            resonance_state=resonance_state,
            loop_detected=loop_detected,
        )

    def get_persona_track_summary(self) -> Dict[str, Dict[str, float]]:
        return self._persona_track_record.summary()


def create_deliberation_engine() -> InternalDeliberation:
    """Factory function for InternalDeliberation."""
    return InternalDeliberation()


# Convenience function for simple usage
def deliberate(
    user_input: str, history: Optional[List[Dict]] = None, **kwargs
) -> SynthesizedResponse:
    """
    Simple function to deliberate on user input.

    Args:
        user_input: The user's message
        history: Conversation history
        **kwargs: Additional context parameters

    Returns:
        SynthesizedResponse with final output
    """
    context = DeliberationContext(
        user_input=user_input,
        conversation_history=history or [],
        tone_strength=kwargs.get("tone_strength", 0.5),
        resonance_state=kwargs.get("resonance_state", "resonance"),
        loop_detected=kwargs.get("loop_detected", False),
    )

    engine = create_deliberation_engine()
    return engine.deliberate_sync(context)
