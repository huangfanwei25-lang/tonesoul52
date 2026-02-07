"""
ToneSoul Shared Module

Contains shared utilities used across ToneSoul components.
"""

from .async_queue import AsyncQueue
from .errors import (
    ERR_ALREADY_RUNNING,
    ERR_EMPTY_OUTPUT,
    ERR_INVALID_INPUT,
    ERR_LOOP_CANCELLED,
    ERR_LOOP_TIMEOUT,
    ERR_MAX_ITERATIONS,
    ERR_STATE_VIOLATION,
    ERR_VOW_BLOCKED,
    ERR_VOW_VIOLATION,
    LoopError,
    StateError,
    ToneSoulError,
    ValidationError,
    VowError,
)

__all__ = [
    # Error classes
    "ToneSoulError",
    "LoopError",
    "ValidationError",
    "StateError",
    "VowError",
    # Singleton errors
    "ERR_LOOP_CANCELLED",
    "ERR_LOOP_TIMEOUT",
    "ERR_MAX_ITERATIONS",
    "ERR_INVALID_INPUT",
    "ERR_EMPTY_OUTPUT",
    "ERR_STATE_VIOLATION",
    "ERR_ALREADY_RUNNING",
    "ERR_VOW_VIOLATION",
    "ERR_VOW_BLOCKED",
    # Utilities
    "AsyncQueue",
]
