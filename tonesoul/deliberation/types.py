"""
ToneSoul 2.0 Internal Deliberation Types

Core data structures for multi-perspective reasoning:
- ViewPoint: Output from each perspective
- Tension: Conflict between perspectives
- SynthesizedResponse: Final merged output
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class PerspectiveType(Enum):
    """The three internal perspectives."""

    MUSE = "muse"  # 哲學家 - meaning, metaphor, depth
    LOGOS = "logos"  # 工程師 - logic, precision, structure
    AEGIS = "aegis"  # 守護者 - safety, ethics, boundaries


class SynthesisType(Enum):
    """How the final response was synthesized."""

    WEIGHTED_FUSION = "weighted_fusion"  # Normal weighted merge
    GUARDIAN_OVERRIDE = "guardian_override"  # Aegis vetoed
    UNANIMOUS = "unanimous"  # All perspectives agreed
    DOMINANT = "dominant"  # One perspective clearly dominated


@dataclass
class ViewPoint:
    """
    Output from a single perspective's deliberation.

    Each perspective generates its reasoning, proposed response,
    confidence level, and any concerns.
    """

    perspective: PerspectiveType
    reasoning: str  # Internal thought process
    proposed_response: str  # What this perspective would say
    confidence: float  # 0.0 to 1.0
    concerns: List[str] = field(default_factory=list)

    # Muse-specific
    metaphors: List[str] = field(default_factory=list)
    existential_connections: List[str] = field(default_factory=list)

    # Logos-specific
    definitions: Dict[str, str] = field(default_factory=dict)
    logical_steps: List[str] = field(default_factory=list)

    # Aegis-specific
    safety_risk: float = 0.0  # 0.0 to 1.0
    ethical_concerns: List[str] = field(default_factory=list)
    boundary_violated: bool = False
    veto_triggered: bool = False
    veto_reason: str = ""

    def to_dict(self) -> dict:
        return {
            "perspective": self.perspective.value,
            "reasoning": self.reasoning,
            "proposed_response": (
                self.proposed_response[:200] + "..."
                if len(self.proposed_response) > 200
                else self.proposed_response
            ),
            "confidence": round(self.confidence, 2),
            "concerns": self.concerns,
            "safety_risk": round(self.safety_risk, 2),
            "veto_triggered": self.veto_triggered,
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
            "resolution": self.resolution_hint,
        }


# ===== ToneStream Distillation: New Types =====


class TensionZone(Enum):
    """
    Cognitive tension zones (from ToneStream philosophy).

    Based on entropy/tension value:
    - ECHO_CHAMBER: <0.3 - Too comfortable, lacking friction
    - SWEET_SPOT: 0.3-0.7 - Ideal creative tension
    - CHAOS: >0.7 - Cognitive overload
    """

    ECHO_CHAMBER = "echo_chamber"  # 同溫層 (夢遊)
    SWEET_SPOT = "sweet_spot"  # 良性摩擦 (甜蜜點)
    CHAOS = "chaos"  # 系統混沌 (認知失調)


@dataclass
class TacticalDecision:
    """
    Strategic decision matrix (from ToneStream).

    Captures the AI's tactical reasoning about how to respond.
    """

    user_hidden_intent: str = ""  # 潛台詞偵測
    strategy_name: str = ""  # 執行戰術名稱
    intended_effect: str = ""  # 預期效果
    tone_tag: str = "neutral"  # 語氣標籤

    def to_dict(self) -> dict:
        return {
            "user_hidden_intent": self.user_hidden_intent,
            "strategy_name": self.strategy_name,
            "intended_effect": self.intended_effect,
            "tone_tag": self.tone_tag,
        }


@dataclass
class SuggestedReply:
    """
    Suggested next move for user (from ToneStream).

    Provides clickable suggestions for the user to continue.
    """

    label: str  # 按鈕標籤 (e.g., "深入探索")
    text: str  # 建議的用戶回應

    def to_dict(self) -> dict:
        return {"label": self.label, "text": self.text}


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
            "aegis": round(self.aegis, 3),
        }


@dataclass
class RoundResult:
    """Single round of adaptive deliberation."""

    round_number: int
    viewpoints: List[ViewPoint] = field(default_factory=list)
    tensions: List[Tension] = field(default_factory=list)
    weights: DeliberationWeights = field(default_factory=DeliberationWeights)
    aggregate_tension: float = 0.0

    def to_dict(self) -> dict:
        return {
            "round_number": int(self.round_number),
            "viewpoints": [view.to_dict() for view in self.viewpoints],
            "tensions": [tension.to_dict() for tension in self.tensions],
            "weights": self.weights.to_dict(),
            "aggregate_tension": round(float(self.aggregate_tension), 4),
        }


@dataclass
class SynthesizedResponse:
    """
    Final output after all perspectives have deliberated.

    Contains the merged response plus transparency about
    the internal deliberation process.
    """

    response: str  # Final response to user
    synthesis_type: SynthesisType
    dominant_voice: Optional[PerspectiveType] = None

    # Internal deliberation transparency
    viewpoints: List[ViewPoint] = field(default_factory=list)
    tensions: List[Tension] = field(default_factory=list)
    weights: DeliberationWeights = field(default_factory=DeliberationWeights)

    # Metadata
    deliberation_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    rounds_used: int = 1
    round_results: List["RoundResult"] = field(default_factory=list)

    # ToneStream Distillation: New fields
    tactical_decision: Optional["TacticalDecision"] = None
    suggested_replies: List["SuggestedReply"] = field(default_factory=list)
    tension_zone: Optional[TensionZone] = None
    calculation_note: str = ""  # 熵值計算說明

    def get_internal_debate(self) -> Dict[str, Any]:
        """Format internal debate for API output."""
        return {
            vp.perspective.value: {
                "reasoning": vp.reasoning,
                "proposed": (
                    vp.proposed_response[:100] + "..."
                    if len(vp.proposed_response) > 100
                    else vp.proposed_response
                ),
                "confidence": round(vp.confidence, 2),
                "concerns": vp.concerns,
            }
            for vp in self.viewpoints
        }

    def to_api_response(self) -> dict:
        """Format for API output."""
        result = {
            "response": self.response,
            "synthesis": {
                "type": self.synthesis_type.value,
                "dominant_voice": self.dominant_voice.value if self.dominant_voice else None,
                "weights": self.weights.to_dict(),
            },
            "internal_debate": self.get_internal_debate(),
            "tensions": [t.to_dict() for t in self.tensions],
            "meta": {
                "deliberation_time_ms": round(self.deliberation_time_ms, 2),
                "timestamp": self.timestamp.isoformat(),
            },
        }

        # ToneStream additions
        if self.tactical_decision:
            result["decision_matrix"] = self.tactical_decision.to_dict()

        if self.suggested_replies:
            result["next_moves"] = [sr.to_dict() for sr in self.suggested_replies]

        if self.tension_zone:
            result["tension_zone"] = {
                "zone": self.tension_zone.value,
                "calculation_note": self.calculation_note,
            }

        if self.rounds_used > 1:
            result["adaptive_debate"] = {
                "rounds_used": int(self.rounds_used),
                "tension_per_round": [
                    round(float(round_result.aggregate_tension), 4)
                    for round_result in self.round_results
                ],
            }

        return result


@dataclass
class DeliberationContext:
    """Context passed to all perspectives during deliberation."""

    user_input: str
    conversation_history: List[Dict] = field(default_factory=list)

    # From existing ToneSoul modules
    commit_stack: Optional[Any] = None  # SelfCommitStack
    trajectory: Optional[Any] = None  # TrajectoryAnalysis
    entropy_state: Optional[Any] = None  # EntropyState

    # Detected signals
    tone_strength: float = 0.5
    resonance_state: str = "resonance"
    loop_detected: bool = False
    scenario_envelope: Optional[Dict[str, Any]] = None
    prior_viewpoints: Optional[List[Dict[str, Any]]] = None
    debate_round: int = 1

    def to_dict(self) -> dict:
        return {
            "user_input": self.user_input[:100],
            "history_length": len(self.conversation_history),
            "tone_strength": self.tone_strength,
            "resonance_state": self.resonance_state,
            "loop_detected": self.loop_detected,
            "scenario_envelope_enabled": bool(self.scenario_envelope),
            "debate_round": int(self.debate_round),
            "has_prior_viewpoints": bool(self.prior_viewpoints),
        }
