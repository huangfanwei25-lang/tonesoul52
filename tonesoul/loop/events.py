"""
Loop Events - Structured Event System

Ported from Copilot Ralph's loop-events.ts with ToneSoul extensions.

Events provide:
- Typed event objects for all loop phases
- Clean serialization via to_dict()
- ToneSoul-specific events (VowDeclaration)
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .config import LoopConfig, LoopResult


@dataclass
class LoopEvent:
    """Base class for all loop events"""

    event_type: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize event to dictionary"""
        return {"event_type": self.event_type}


# =============================================================================
# Loop Lifecycle Events
# =============================================================================


@dataclass
class LoopStartEvent(LoopEvent):
    """Emitted when loop starts"""

    config: Optional[LoopConfig] = None
    event_type: str = "loop_start"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "max_iterations": self.config.max_iterations if self.config else 0,
            "timeout_ms": self.config.timeout_ms if self.config else 0,
        }


@dataclass
class LoopCompleteEvent(LoopEvent):
    """Emitted when loop completes successfully"""

    result: Optional[LoopResult] = None
    event_type: str = "loop_complete"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "iterations": self.result.iterations if self.result else 0,
            "duration_ms": self.result.duration_ms if self.result else 0,
        }


@dataclass
class LoopFailedEvent(LoopEvent):
    """Emitted when loop fails"""

    error: Optional[Exception] = None
    result: Optional[LoopResult] = None
    event_type: str = "loop_failed"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "error": str(self.error) if self.error else None,
            "iterations": self.result.iterations if self.result else 0,
        }


@dataclass
class LoopCancelledEvent(LoopEvent):
    """Emitted when loop is cancelled"""

    result: Optional[LoopResult] = None
    event_type: str = "loop_cancelled"


# =============================================================================
# Iteration Events
# =============================================================================


@dataclass
class IterationStartEvent(LoopEvent):
    """Emitted at start of each iteration"""

    iteration: int = 0
    max_iterations: int = 0
    event_type: str = "iteration_start"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "iteration": self.iteration,
            "max_iterations": self.max_iterations,
        }


@dataclass
class IterationCompleteEvent(LoopEvent):
    """Emitted at end of each iteration"""

    iteration: int = 0
    duration_ms: int = 0
    event_type: str = "iteration_complete"


# =============================================================================
# AI Response Events
# =============================================================================


@dataclass
class AIResponseEvent(LoopEvent):
    """Emitted for AI text responses"""

    text: str = ""
    iteration: int = 0
    event_type: str = "ai_response"


@dataclass
class ToolExecutionStartEvent(LoopEvent):
    """Emitted when tool execution starts"""

    tool_name: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    iteration: int = 0
    event_type: str = "tool_execution_start"


@dataclass
class ToolExecutionEvent(LoopEvent):
    """Emitted when tool execution completes"""

    tool_name: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    result: Optional[str] = None
    error: Optional[str] = None
    duration_ms: int = 0
    iteration: int = 0
    event_type: str = "tool_execution"


# =============================================================================
# Detection Events
# =============================================================================


@dataclass
class PromiseDetectedEvent(LoopEvent):
    """Emitted when promise phrase is detected in output"""

    phrase: str = ""
    source: str = ""  # "ai_response" or "tool_result"
    iteration: int = 0
    event_type: str = "promise_detected"


@dataclass
class VowDeclarationEvent(LoopEvent):
    """
    ToneSoul-specific: AI declares vow compliance.

    Similar to promise detection but for semantic vows.
    """

    vow_id: str = ""
    declared: bool = False
    iteration: int = 0
    event_type: str = "vow_declaration"


# =============================================================================
# Error Events
# =============================================================================


@dataclass
class ErrorEvent(LoopEvent):
    """Emitted for errors during iteration"""

    error: Optional[Exception] = None
    iteration: int = 0
    recoverable: bool = True
    event_type: str = "error"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "error": str(self.error) if self.error else None,
            "iteration": self.iteration,
            "recoverable": self.recoverable,
        }
