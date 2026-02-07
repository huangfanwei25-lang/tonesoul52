"""
Loop Configuration - Clean Type Definitions

Following Copilot Ralph's pattern of:
- Dataclass for configuration
- Literal types for state
- Factory function for defaults
"""

from dataclasses import dataclass
from typing import Literal, Optional

# State machine type
LoopState = Literal["idle", "running", "complete", "failed", "cancelled"]


@dataclass
class LoopConfig:
    """
    Configuration for iteration loop.

    Attributes:
        prompt: The task prompt to iterate on
        max_iterations: Maximum number of iterations (0 = unlimited)
        timeout_ms: Timeout in milliseconds (0 = no timeout)
        promise_phrase: Phrase that signals task completion
        working_dir: Working directory for the loop
        dry_run: If True, only validate config without executing
    """

    prompt: str = ""
    max_iterations: int = 10
    timeout_ms: int = 30 * 60 * 1000  # 30 minutes
    promise_phrase: str = "任務完成！🥇"
    working_dir: str = "."
    dry_run: bool = False


@dataclass
class LoopResult:
    """
    Result of loop execution.

    Attributes:
        state: Final state of the loop
        iterations: Number of iterations completed
        duration_ms: Total duration in milliseconds
        error: Error if loop failed, None otherwise
    """

    state: LoopState
    iterations: int
    duration_ms: int
    error: Optional[Exception] = None


def default_loop_config() -> LoopConfig:
    """
    Factory function for default configuration.

    Returns:
        LoopConfig with sensible defaults
    """
    return LoopConfig()
