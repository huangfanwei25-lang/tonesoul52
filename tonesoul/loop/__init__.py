"""
ToneSoul Loop Module

Provides iterative execution engine with event streaming.

Usage:
    from tonesoul.loop import LoopEngine, LoopConfig

    config = LoopConfig(prompt="Fix this bug", max_iterations=5)

    async def handler(iteration: int, prompt: str):
        result = await my_ai.generate(prompt)
        yield result

    engine = LoopEngine(config=config, on_iteration=handler)
    result = await engine.start()
"""

from .config import LoopConfig, LoopResult, LoopState, default_loop_config
from .engine import LoopEngine
from .events import (
    AIResponseEvent,
    ErrorEvent,
    IterationCompleteEvent,
    IterationStartEvent,
    LoopCancelledEvent,
    LoopCompleteEvent,
    LoopEvent,
    LoopFailedEvent,
    LoopStartEvent,
    PromiseDetectedEvent,
    ToolExecutionEvent,
    ToolExecutionStartEvent,
    VowDeclarationEvent,
)

__all__ = [
    # Configuration
    "LoopConfig",
    "LoopResult",
    "LoopState",
    "default_loop_config",
    # Engine
    "LoopEngine",
    # Events
    "LoopEvent",
    "LoopStartEvent",
    "LoopCompleteEvent",
    "LoopFailedEvent",
    "LoopCancelledEvent",
    "IterationStartEvent",
    "IterationCompleteEvent",
    "AIResponseEvent",
    "ToolExecutionStartEvent",
    "ToolExecutionEvent",
    "PromiseDetectedEvent",
    "VowDeclarationEvent",
    "ErrorEvent",
]
