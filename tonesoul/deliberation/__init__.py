"""
ToneSoul 2.0 Internal Deliberation Module

The core of ToneSoul 2.0 - multi-perspective internal reasoning
that happens BEFORE output generation.

Key Concepts:
- Three perspectives (Muse, Logos, Aegis) think in parallel
- Tensions between viewpoints are detected
- SemanticGravity synthesizes a unified response
- Aegis (Guardian) has veto power for safety

Usage:
    from tonesoul.deliberation import deliberate, InternalDeliberation

    # Simple usage
    result = deliberate("What is the meaning of life?")
    print(result.response)
    print(result.to_api_response())

    # Full control
    engine = InternalDeliberation()
    context = DeliberationContext(user_input="...")
    result = engine.deliberate_sync(context)
"""

from .engine import InternalDeliberation, create_deliberation_engine, deliberate
from .gravity import SemanticGravity, create_semantic_gravity
from .persona_track_record import (
    PersonaTrackRecord,
    create_persona_track_record,
    default_track_record_path,
)
from .perspectives import (
    AegisPerspective,
    BasePerspective,
    LogosPerspective,
    MusePerspective,
    create_perspectives,
)
from .types import (
    DeliberationContext,
    DeliberationWeights,
    PerspectiveType,
    RoundResult,
    SuggestedReply,
    SynthesisType,
    SynthesizedResponse,
    TacticalDecision,
    Tension,
    # ToneStream Distillation
    TensionZone,
    ViewPoint,
)

__all__ = [
    # Types
    "ViewPoint",
    "Tension",
    "SynthesizedResponse",
    "SynthesisType",
    "PerspectiveType",
    "DeliberationWeights",
    "DeliberationContext",
    "RoundResult",
    # ToneStream Distillation
    "TensionZone",
    "TacticalDecision",
    "SuggestedReply",
    # Perspectives
    "BasePerspective",
    "MusePerspective",
    "LogosPerspective",
    "AegisPerspective",
    "create_perspectives",
    # Synthesis
    "SemanticGravity",
    "create_semantic_gravity",
    "PersonaTrackRecord",
    "create_persona_track_record",
    "default_track_record_path",
    # Main Engine
    "InternalDeliberation",
    "create_deliberation_engine",
    "deliberate",
]
