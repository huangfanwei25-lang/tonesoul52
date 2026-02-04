"""
Test helpers following Ralph patterns

Provides:
- build_config: Factory for test configurations with overrides
- drain_events: Collect all events from engine stream
"""

from typing import Any, List

from tonesoul.loop.config import LoopConfig, default_loop_config
from tonesoul.loop.engine import LoopEngine
from tonesoul.loop.events import LoopEvent


def build_config(**overrides: Any) -> LoopConfig:
    """
    Factory for test configurations.

    Creates a default config and applies overrides.
    Following Ralph's buildConfig pattern.

    Usage:
        config = build_config(max_iterations=3, timeout_ms=1000)
    """
    config = default_loop_config()

    # Apply overrides
    for key, value in overrides.items():
        if hasattr(config, key):
            setattr(config, key, value)

    return config


async def drain_events(engine: LoopEngine) -> List[LoopEvent]:
    """
    Collect all events from engine stream.

    Following Ralph's drainEvents pattern.

    Usage:
        events = await drain_events(engine)
        promise_events = [e for e in events if isinstance(e, PromiseDetectedEvent)]
    """
    events: List[LoopEvent] = []
    async for event in engine.events_stream():
        events.append(event)
    return events
