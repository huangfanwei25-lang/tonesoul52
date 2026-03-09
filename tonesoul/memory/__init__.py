from __future__ import annotations

from .adversarial import AdversarialReflector, Challenge, ChallengeType, Repair
from .consolidator import consolidate, generate_meta_reflection, identify_patterns
from .decay import calculate_decay, should_forget
from .stats import average_coherence, count_by_verdict, most_common_divergence
from .write_gateway import (
    ENVIRONMENT_STIMULUS_LAYER,
    ENVIRONMENT_STIMULUS_SOURCE,
    ENVIRONMENT_STIMULUS_TYPE,
    MemoryWriteGateway,
    MemoryWriteResult,
)

__all__ = [
    "ChallengeType",
    "Challenge",
    "Repair",
    "AdversarialReflector",
    "calculate_decay",
    "should_forget",
    "count_by_verdict",
    "most_common_divergence",
    "average_coherence",
    "identify_patterns",
    "generate_meta_reflection",
    "consolidate",
    "ENVIRONMENT_STIMULUS_TYPE",
    "ENVIRONMENT_STIMULUS_SOURCE",
    "ENVIRONMENT_STIMULUS_LAYER",
    "MemoryWriteGateway",
    "MemoryWriteResult",
]
