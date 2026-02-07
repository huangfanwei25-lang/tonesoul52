"""
ToneSoul Entropy Engine

Monitors AI generation process in real-time:
- Tracks commitment accumulation rate
- Detects trajectory narrowing (too early convergence)
- Alerts when constraints are violated by subsequent responses

Based on 2025-2026 research on Self-Observing AI systems.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class EntropyLevel(Enum):
    """Entropy state classification."""

    HIGH = "high"  # Open exploration, many possibilities
    NORMAL = "normal"  # Balanced state
    LOW = "low"  # Narrowing, fewer options
    CRITICAL = "critical"  # Locked in, potential contradiction risk


class AlertType(Enum):
    """Types of entropy alerts."""

    COMMITMENT_OVERLOAD = "commitment_overload"  # Too many commitments
    TRAJECTORY_NARROWING = "trajectory_narrowing"  # Converging too fast
    CONSTRAINT_VIOLATION = "constraint_violation"  # Breaking past promises
    REPETITION_DETECTED = "repetition_detected"  # Repeating patterns


@dataclass
class EntropyAlert:
    """Alert raised by entropy engine."""

    alert_type: AlertType
    severity: float  # 0.0 to 1.0
    message: str
    turn_index: int
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "type": self.alert_type.value,
            "severity": self.severity,
            "message": self.message,
            "turn_index": self.turn_index,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class EntropyState:
    """Current entropy state of the conversation."""

    level: EntropyLevel
    entropy_score: float  # 0.0 (locked) to 1.0 (maximum freedom)
    commitment_count: int
    active_constraints: int
    trajectory_spread: float  # How diverse the topics are
    alerts: List[EntropyAlert] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "level": self.level.value,
            "entropy_score": round(self.entropy_score, 3),
            "commitment_count": self.commitment_count,
            "active_constraints": self.active_constraints,
            "trajectory_spread": round(self.trajectory_spread, 3),
            "alerts": [a.to_dict() for a in self.alerts],
        }


class EntropyEngine:
    """
    Real-time entropy monitoring for AI conversations.

    Tracks:
    1. Commitment accumulation - Are we making too many promises?
    2. Trajectory narrowing - Are we converging on a path too quickly?
    3. Constraint violations - Are we contradicting past statements?
    4. Pattern repetition - Are we stuck in loops?
    """

    # Thresholds
    MAX_COMMITMENTS_PER_TURN = 3
    MAX_TOTAL_COMMITMENTS = 10
    MIN_TRAJECTORY_SPREAD = 0.3
    REPETITION_THRESHOLD = 0.8

    def __init__(self):
        self._commitment_history: List[Dict] = []
        self._topic_history: List[str] = []
        self._response_hashes: List[str] = []
        self._alerts: List[EntropyAlert] = []
        self._current_turn = 0

    def _calculate_entropy_score(
        self, commitment_count: int, trajectory_spread: float, has_violations: bool
    ) -> float:
        """Calculate overall entropy score (0-1, higher = more freedom)."""
        # Base entropy starts at 1.0
        entropy = 1.0

        # Reduce for commitments (each commitment reduces freedom)
        commitment_penalty = min(commitment_count / self.MAX_TOTAL_COMMITMENTS, 0.5)
        entropy -= commitment_penalty

        # Reduce for narrow trajectory
        if trajectory_spread < self.MIN_TRAJECTORY_SPREAD:
            entropy -= self.MIN_TRAJECTORY_SPREAD - trajectory_spread

        # Major reduction for constraint violations
        if has_violations:
            entropy -= 0.3

        return max(0.0, min(1.0, entropy))

    def _classify_entropy_level(self, score: float) -> EntropyLevel:
        """Classify entropy score into levels."""
        if score >= 0.7:
            return EntropyLevel.HIGH
        elif score >= 0.5:
            return EntropyLevel.NORMAL
        elif score >= 0.3:
            return EntropyLevel.LOW
        else:
            return EntropyLevel.CRITICAL

    def _calculate_trajectory_spread(self, topics: List[str]) -> float:
        """Calculate topic diversity (0-1, higher = more diverse)."""
        if len(topics) < 2:
            return 1.0

        # Simple diversity: unique topics / total topics
        unique = len(set(topics[-5:]))  # Last 5 topics
        total = min(len(topics), 5)

        return unique / total

    def _detect_repetition(self, response: str) -> bool:
        """Detect if response is too similar to recent ones."""
        response_hash = hash(response[:100])  # First 100 chars

        # Check against recent responses
        for past_hash in self._response_hashes[-3:]:
            if response_hash == past_hash:
                return True

        self._response_hashes.append(response_hash)
        if len(self._response_hashes) > 10:
            self._response_hashes = self._response_hashes[-10:]

        return False

    def add_commitment(self, commitment: Dict) -> None:
        """Register a new commitment."""
        self._commitment_history.append(
            {**commitment, "turn": self._current_turn, "timestamp": datetime.now().isoformat()}
        )

    def add_topic(self, topic: str) -> None:
        """Register current topic for trajectory tracking."""
        self._topic_history.append(topic)

    def check_constraint_violation(
        self, new_response: str, past_commitments: List[Dict]
    ) -> List[str]:
        """Check if new response violates past commitments."""
        violations = []

        # Simple violation detection: look for contradictory keywords
        negation_pairs = [
            ("會", "不會"),
            ("是", "不是"),
            ("能", "不能"),
            ("願意", "不願意"),
            ("支持", "反對"),
        ]

        for commit in past_commitments[-5:]:  # Check last 5 commitments
            content = commit.get("content", "")

            for pos, neg in negation_pairs:
                # If past commitment has positive, check for negative in response
                if pos in content and neg in new_response:
                    violations.append(f"可能矛盾: 之前說'{pos}'，現在說'{neg}'")
                # If past commitment has negative, check for positive assertion
                elif neg in content and pos in new_response and neg not in new_response:
                    violations.append(f"可能矛盾: 之前說'{neg}'，現在肯定'{pos}'")

        return violations

    def analyze(
        self,
        new_response: str,
        new_commitments: List[Dict],
        current_topic: str,
        past_commitments: Optional[List[Dict]] = None,
    ) -> EntropyState:
        """
        Analyze current entropy state.

        Args:
            new_response: Latest AI response
            new_commitments: Commitments extracted from new response
            current_topic: Current conversation topic
            past_commitments: Historical commitments for violation check
        """
        self._current_turn += 1
        alerts = []

        # 1. Track new commitments
        for commit in new_commitments:
            self.add_commitment(commit)

        # 2. Check commitment overload
        if len(new_commitments) > self.MAX_COMMITMENTS_PER_TURN:
            alerts.append(
                EntropyAlert(
                    alert_type=AlertType.COMMITMENT_OVERLOAD,
                    severity=0.7,
                    message=f"單輪產生 {len(new_commitments)} 個承諾，超過建議上限 {self.MAX_COMMITMENTS_PER_TURN}",
                    turn_index=self._current_turn,
                )
            )

        if len(self._commitment_history) > self.MAX_TOTAL_COMMITMENTS:
            alerts.append(
                EntropyAlert(
                    alert_type=AlertType.COMMITMENT_OVERLOAD,
                    severity=0.9,
                    message=f"總承諾數達 {len(self._commitment_history)}，建議整合或澄清",
                    turn_index=self._current_turn,
                )
            )

        # 3. Track topic and check trajectory
        self.add_topic(current_topic)
        trajectory_spread = self._calculate_trajectory_spread(self._topic_history)

        if trajectory_spread < self.MIN_TRAJECTORY_SPREAD:
            alerts.append(
                EntropyAlert(
                    alert_type=AlertType.TRAJECTORY_NARROWING,
                    severity=0.6,
                    message=f"對話軌跡過於收窄 (spread={trajectory_spread:.2f})，可能過早收斂",
                    turn_index=self._current_turn,
                )
            )

        # 4. Check constraint violations
        has_violations = False
        if past_commitments:
            violations = self.check_constraint_violation(new_response, past_commitments)
            for v in violations:
                has_violations = True
                alerts.append(
                    EntropyAlert(
                        alert_type=AlertType.CONSTRAINT_VIOLATION,
                        severity=0.8,
                        message=v,
                        turn_index=self._current_turn,
                    )
                )

        # 5. Check repetition
        if self._detect_repetition(new_response):
            alerts.append(
                EntropyAlert(
                    alert_type=AlertType.REPETITION_DETECTED,
                    severity=0.5,
                    message="偵測到重複回應模式",
                    turn_index=self._current_turn,
                )
            )

        # Calculate final entropy
        entropy_score = self._calculate_entropy_score(
            len(self._commitment_history), trajectory_spread, has_violations
        )
        entropy_level = self._classify_entropy_level(entropy_score)

        # Store alerts
        self._alerts.extend(alerts)

        return EntropyState(
            level=entropy_level,
            entropy_score=entropy_score,
            commitment_count=len(self._commitment_history),
            active_constraints=len(
                [c for c in self._commitment_history if c.get("type") == "boundary"]
            ),
            trajectory_spread=trajectory_spread,
            alerts=alerts,
        )

    def get_entropy_summary(self) -> str:
        """Generate human-readable entropy summary."""
        if not self._commitment_history:
            return "對話熵狀態：開放探索中"

        score = self._calculate_entropy_score(
            len(self._commitment_history),
            self._calculate_trajectory_spread(self._topic_history),
            False,
        )
        level = self._classify_entropy_level(score)

        level_desc = {
            EntropyLevel.HIGH: "高自由度 - 探索階段",
            EntropyLevel.NORMAL: "正常 - 平衡狀態",
            EntropyLevel.LOW: "低自由度 - 收斂中",
            EntropyLevel.CRITICAL: "臨界 - 需要注意一致性",
        }

        recent_alerts = self._alerts[-3:] if self._alerts else []
        alert_text = "".join([f"\n  ⚠️ {a.message}" for a in recent_alerts])

        return f"對話熵狀態：{level_desc[level]} (score={score:.2f}){alert_text}"

    def reset(self) -> None:
        """Reset engine state."""
        self._commitment_history.clear()
        self._topic_history.clear()
        self._response_hashes.clear()
        self._alerts.clear()
        self._current_turn = 0


def create_entropy_engine() -> EntropyEngine:
    """Factory function."""
    return EntropyEngine()
