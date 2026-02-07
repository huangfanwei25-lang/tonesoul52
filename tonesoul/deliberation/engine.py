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

from .gravity import create_semantic_gravity
from .perspectives import (
    BasePerspective,
    create_perspectives,
)
from .types import (
    DeliberationContext,
    PerspectiveType,
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

        # Initialize synthesis engine
        self._gravity = create_semantic_gravity()

        # State tracking
        self._deliberation_count = 0
        self._last_viewpoints: List[ViewPoint] = []

    async def deliberate(self, context: DeliberationContext) -> SynthesizedResponse:
        """
        Async deliberation - all perspectives think in parallel.

        This is more efficient as we don't wait for each
        perspective sequentially.
        """
        start_time = time.time()

        # Parallel execution of all perspectives
        viewpoints = await self._parallel_think(context)

        # Synthesize
        elapsed_ms = (time.time() - start_time) * 1000
        result = self._gravity.synthesize(viewpoints, context, elapsed_ms)

        # Track state
        self._deliberation_count += 1
        self._last_viewpoints = viewpoints

        return result

    def deliberate_sync(self, context: DeliberationContext) -> SynthesizedResponse:
        """
        Sync deliberation - for non-async contexts.

        Uses asyncio.run() or sequential execution as fallback.
        """
        start_time = time.time()

        try:
            # Try to use asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're already in an async context, run sequentially
                viewpoints = self._sequential_think(context)
            else:
                viewpoints = asyncio.run(self._parallel_think(context))
        except RuntimeError:
            # No event loop, run sequentially
            viewpoints = self._sequential_think(context)

        # Synthesize
        elapsed_ms = (time.time() - start_time) * 1000
        result = self._gravity.synthesize(viewpoints, context, elapsed_ms)

        # Track state
        self._deliberation_count += 1
        self._last_viewpoints = viewpoints

        return result

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
