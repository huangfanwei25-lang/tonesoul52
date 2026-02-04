"""
ToneBridge Module
5-stage psychological analysis pipeline + trajectory analysis for understanding user emotional state.
Third Axiom: Self-Commit System for semantic responsibility.
"""

from .types import (
    ToneAnalysis,
    MotivePrediction,
    CollapseRisk,
    MeminiUnit,
    ResonanceDefense,
    ToneBridgeResult,
)
from .analyzer import ToneBridgeAnalyzer
from .trajectory import (
    TrajectoryAnalyzer,
    TrajectoryAnalysis,
    DirectionChange,
    ResonanceState,
)
from .personas import (
    PersonaMode,
    PersonaConfig,
    get_persona_from_resonance,
    build_hardened_prompt,
    build_navigation_prompt,
    NavigatorResponse,
)

# Third Axiom - Self Commit System
from .self_commit import (
    SelfCommit,
    SelfCommitExtractor,
    SelfCommitStack,
    AssertionType,
)
from .rupture_detector import (
    RuptureDetector,
    SemanticRupture,
    RuptureSeverity,
)
from .value_accumulator import (
    ValueAccumulator,
    CorrectionEvent,
    EmergentValue,
)

# Session Intelligence
from .session_reporter import (
    SessionReporter,
    SessionSummary,
    TurningPoint,
)

# Enhanced Commitment Extraction (NLP)
from .commitment_extractor import (
    CommitmentExtractor,
    CommitmentStructure,
)

# Entropy Engine (Self-Observing AI)
from .entropy_engine import (
    EntropyEngine,
    EntropyState,
    EntropyLevel,
    EntropyAlert,
    AlertType,
)

__all__ = [
    "ToneAnalysis",
    "MotivePrediction",
    "CollapseRisk",
    "MeminiUnit",
    "ResonanceDefense",
    "ToneBridgeResult",
    "ToneBridgeAnalyzer",
    # Trajectory
    "TrajectoryAnalyzer",
    "TrajectoryAnalysis",
    "DirectionChange",
    "ResonanceState",
    # Personas
    "PersonaMode",
    "PersonaConfig",
    "get_persona_from_resonance",
    "build_hardened_prompt",
    "build_navigation_prompt",
    "NavigatorResponse",
    # Third Axiom - Self Commit System
    "SelfCommit",
    "SelfCommitExtractor",
    "SelfCommitStack",
    "AssertionType",
    "RuptureDetector",
    "SemanticRupture",
    "RuptureSeverity",
    "ValueAccumulator",
    "CorrectionEvent",
    "EmergentValue",
    # Session Intelligence
    "SessionReporter",
    "SessionSummary",
    "TurningPoint",
    # Enhanced Commitment Extraction
    "CommitmentExtractor",
    "CommitmentStructure",
]
