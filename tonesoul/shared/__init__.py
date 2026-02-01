"""
ToneSoul Shared Module

Contains shared utilities used across ToneSoul components.
"""

from .errors import (
    ToneSoulError,
    LoopError,
    ValidationError,
    StateError,
    VowError,
    ERR_LOOP_CANCELLED,
    ERR_LOOP_TIMEOUT,
    ERR_MAX_ITERATIONS,
    ERR_INVALID_INPUT,
    ERR_EMPTY_OUTPUT,
    ERR_STATE_VIOLATION,
    ERR_ALREADY_RUNNING,
    ERR_VOW_VIOLATION,
    ERR_VOW_BLOCKED,
)

from .async_queue import AsyncQueue

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
