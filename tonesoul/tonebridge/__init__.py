"""
ToneBridge Module
5-stage psychological analysis pipeline + trajectory analysis for understanding user emotional state.
Third Axiom: Self-Commit System for semantic responsibility.
"""

from .analyzer import ToneBridgeAnalyzer

# Enhanced Commitment Extraction (NLP)
from .commitment_extractor import (
    CommitmentExtractor,
    CommitmentStructure,
)

# Entropy Engine (Self-Observing AI)
from .entropy_engine import (
    AlertType,
    EntropyAlert,
    EntropyEngine,
    EntropyLevel,
    EntropyState,
)
from .personas import (
    NavigatorResponse,
    PersonaConfig,
    PersonaMode,
    build_hardened_prompt,
    build_navigation_prompt,
    get_persona_from_resonance,
)
from .rupture_detector import (
    RuptureDetector,
    RuptureSeverity,
    SemanticRupture,
)
from .scenario_envelope import (
    ScenarioEnvelopeBuilder,
)

# Third Axiom - Self Commit System
from .self_commit import (
    AssertionType,
    SelfCommit,
    SelfCommitExtractor,
    SelfCommitStack,
)

# Session Intelligence
from .session_reporter import (
    SessionReporter,
    SessionSummary,
    TurningPoint,
)
from .trajectory import (
    DirectionChange,
    ResonanceState,
    TrajectoryAnalysis,
    TrajectoryAnalyzer,
)
from .types import (
    CollapseRisk,
    MeminiUnit,
    MotivePrediction,
    ResonanceDefense,
    ToneAnalysis,
    ToneBridgeResult,
)
from .value_accumulator import (
    CorrectionEvent,
    EmergentValue,
    ValueAccumulator,
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
    "ScenarioEnvelopeBuilder",
    # Enhanced Commitment Extraction
    "CommitmentExtractor",
    "CommitmentStructure",
    # Entropy Engine
    "AlertType",
    "EntropyAlert",
    "EntropyEngine",
    "EntropyLevel",
    "EntropyState",
]
