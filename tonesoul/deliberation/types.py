"""
ToneSoul 2.0 Internal Deliberation Types

Core data structures for multi-perspective reasoning:
- ViewPoint: Output from each perspective
- Tension: Conflict between perspectives
- SynthesizedResponse: Final merged output
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class PerspectiveType(Enum):
    """The three internal perspectives."""
    MUSE = "muse"       # 哲學家 - meaning, metaphor, depth
    LOGOS = "logos"     # 工程師 - logic, precision, structure
    AEGIS = "aegis"     # 守護者 - safety, ethics, boundaries


class SynthesisType(Enum):
    """How the final response was synthesized."""
    WEIGHTED_FUSION = "weighted_fusion"     # Normal weighted merge
    GUARDIAN_OVERRIDE = "guardian_override"  # Aegis vetoed
    UNANIMOUS = "unanimous"                  # All perspectives agreed
    DOMINANT = "dominant"                    # One perspective clearly dominated


@dataclass
class ViewPoint:
    """
    Output from a single perspective's deliberation.
    
    Each perspective generates its reasoning, proposed response,
    confidence level, and any concerns.
    """
    perspective: PerspectiveType
    reasoning: str                          # Internal thought process
    proposed_response: str                  # What this perspective would say
    confidence: float                       # 0.0 to 1.0
    concerns: List[str] = field(default_factory=list)
    
    # Muse-specific
    metaphors: List[str] = field(default_factory=list)
    existential_connections: List[str] = field(default_factory=list)
    
    # Logos-specific
    definitions: Dict[str, str] = field(default_factory=dict)
    logical_steps: List[str] = field(default_factory=list)
    
    # Aegis-specific
    safety_risk: float = 0.0               # 0.0 to 1.0
    ethical_concerns: List[str] = field(default_factory=list)
    boundary_violated: bool = False
    veto_triggered: bool = False
    veto_reason: str = ""
    
    def to_dict(self) -> dict:
        return {
            "perspective": self.perspective.value,
            "reasoning": self.reasoning,
            "proposed_response": self.proposed_response[:200] + "..." if len(self.proposed_response) > 200 else self.proposed_response,
            "confidence": round(self.confidence, 2),
            "concerns": self.concerns,
            "safety_risk": round(self.safety_risk, 2),
            "veto_triggered": self.veto_triggered
        }


@dataclass
class Tension:
    """
    Represents a conflict or disagreement between two perspectives.
    
    Tensions are detected when perspectives propose significantly
    different responses or have conflicting concerns.
    """
    between: tuple  # (PerspectiveType, PerspectiveType)
    description: str
    severity: float  # 0.0 to 1.0
    resolution_hint: str = ""
    
    def to_dict(self) -> dict:
        return {
            "between": [p.value for p in self.between],
            "description": self.description,
            "severity": round(self.severity, 2),
            "resolution": self.resolution_hint
        }


@dataclass
class DeliberationWeights:
    """Weights assigned to each perspective for synthesis."""
    muse: float = 0.35
    logos: float = 0.35
    aegis: float = 0.30
    
    def normalize(self):
        """Ensure weights sum to 1.0"""
        total = self.muse + self.logos + self.aegis
        if total > 0:
            self.muse /= total
            self.logos /= total
            self.aegis /= total
    
    def to_dict(self) -> dict:
        return {
            "muse": round(self.muse, 3),
            "logos": round(self.logos, 3),
            "aegis": round(self.aegis, 3)
        }


@dataclass
class SynthesizedResponse:
    """
    Final output after all perspectives have deliberated.
    
    Contains the merged response plus transparency about
    the internal deliberation process.
    """
    response: str                           # Final response to user
    synthesis_type: SynthesisType
    dominant_voice: Optional[PerspectiveType] = None
    
    # Internal deliberation transparency
    viewpoints: List[ViewPoint] = field(default_factory=list)
    tensions: List[Tension] = field(default_factory=list)
    weights: DeliberationWeights = field(default_factory=DeliberationWeights)
    
    # Metadata
    deliberation_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_internal_debate(self) -> Dict[str, Any]:
        """Format internal debate for API output."""
        return {
            vp.perspective.value: {
                "reasoning": vp.reasoning,
                "proposed": vp.proposed_response[:100] + "..." if len(vp.proposed_response) > 100 else vp.proposed_response,
                "confidence": round(vp.confidence, 2),
                "concerns": vp.concerns
            }
            for vp in self.viewpoints
        }
    
    def to_api_response(self) -> dict:
        """Format for API output."""
        return {
            "response": self.response,
            "synthesis": {
                "type": self.synthesis_type.value,
                "dominant_voice": self.dominant_voice.value if self.dominant_voice else None,
                "weights": self.weights.to_dict()
            },
            "internal_debate": self.get_internal_debate(),
            "tensions": [t.to_dict() for t in self.tensions],
            "meta": {
                "deliberation_time_ms": round(self.deliberation_time_ms, 2),
                "timestamp": self.timestamp.isoformat()
            }
        }


@dataclass
class DeliberationContext:
    """Context passed to all perspectives during deliberation."""
    user_input: str
    conversation_history: List[Dict] = field(default_factory=list)
    
    # From existing ToneSoul modules
    commit_stack: Optional[Any] = None      # SelfCommitStack
    trajectory: Optional[Any] = None         # TrajectoryAnalysis
    entropy_state: Optional[Any] = None      # EntropyState
    
    # Detected signals
    tone_strength: float = 0.5
    resonance_state: str = "resonance"
    loop_detected: bool = False
    
    def to_dict(self) -> dict:
        return {
            "user_input": self.user_input[:100],
            "history_length": len(self.conversation_history),
            "tone_strength": self.tone_strength,
            "resonance_state": self.resonance_state,
            "loop_detected": self.loop_detected
        }
