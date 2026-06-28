"""Externalized cognition contracts.

The first public surface is a deterministic Cognitive Frame schema: it organizes a
problem into auditable lanes without claiming to prove understanding.
"""

from .cognitive_frame import (
    USES_LLM,
    USES_NETWORK,
    CognitiveFrame,
    CognitiveFrameIssue,
    CognitiveFrameValidationResult,
    FrameItem,
    validate_cognitive_frame,
)

__ts_layer__ = "semantic"
__ts_purpose__ = "Externalized cognitive-frame contracts for problem exploration."

__all__ = [
    "CognitiveFrame",
    "CognitiveFrameIssue",
    "CognitiveFrameValidationResult",
    "FrameItem",
    "USES_LLM",
    "USES_NETWORK",
    "validate_cognitive_frame",
]
