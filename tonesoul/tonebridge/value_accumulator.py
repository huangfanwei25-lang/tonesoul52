"""
Value Accumulator - Third Axiom Implementation

Tracks correction patterns over time to form emergent values.

The key insight:
  斷裂 → 修正 → 修正的原因 → 長期累積 → 價值觀

Values are not pre-programmed. They emerge from:
1. "I contradicted myself"
2. "I chose to correct in this way"
3. "I keep choosing similar corrections"
4. Pattern crystallizes into a value
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
from collections import defaultdict
import json

from .self_commit import AssertionType
from .rupture_detector import SemanticRupture, RuptureSeverity


@dataclass
class CorrectionEvent:
    """
    A record of how an AI corrected itself after a rupture.

    Example:
        Rupture: AI said "自由意志無意義" contradicting earlier "有意義"
        Correction: "我需要澄清 - 我認為自由意志在實踐層面有意義"
        Reason: "因為忽略了使用者的情感需求"

    Over time, if similar corrections happen:
        → Emergent value: "在哲學討論中優先考慮對方情感需求"
    """

    id: str
    timestamp: datetime
    rupture_id: str
    rupture_type: str  # contradiction type
    original_statement: str  # What was originally said
    corrected_statement: str  # How it was corrected
    correction_reason: str  # Why the correction was made

    # Classification for pattern matching
    correction_pattern: str  # empathy_priority / precision_priority / boundary_clarification / etc
    domain: str  # emotion / logic / ethics / relationship / etc

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "rupture_id": self.rupture_id,
            "rupture_type": self.rupture_type,
            "original_statement": self.original_statement,
            "corrected_statement": self.corrected_statement,
            "correction_reason": self.correction_reason,
            "correction_pattern": self.correction_pattern,
            "domain": self.domain,
        }


@dataclass
class EmergentValue:
    """
    A value that has emerged from repeated correction patterns.

    Not pre-programmed - born from:
    1. Multiple correction events
    2. Similar patterns across events
    3. Crystallization into a stable principle
    """

    id: str
    name: str  # Short name: "empathy_priority"
    description: str  # Full description
    formation_date: datetime

    # Evidence
    supporting_corrections: List[str]  # IDs of corrections that formed this
    pattern_count: int  # How many times this pattern appeared

    # Strength
    strength: float  # 0.0 to 1.0, increases with repetition
    last_reinforced: datetime  # Last time this value was reinforced

    # Domain
    domain: str  # emotion / logic / ethics / etc

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "formation_date": self.formation_date.isoformat(),
            "supporting_corrections": self.supporting_corrections,
            "pattern_count": self.pattern_count,
            "strength": self.strength,
            "last_reinforced": self.last_reinforced.isoformat(),
            "domain": self.domain,
        }


class ValueAccumulator:
    """
    Accumulates correction patterns over time to form emergent values.

    Process:
    1. Receive correction events from rupture resolutions
    2. Classify corrections by pattern and domain
    3. Track pattern frequencies
    4. When pattern threshold reached, crystallize into EmergentValue
    5. Reinforce existing values when patterns recur
    """

    # Pattern classification keywords
    PATTERN_KEYWORDS = {
        "empathy_priority": ["情感", "感受", "關心", "理解", "同理"],
        "precision_priority": ["精確", "定義", "邏輯", "清楚", "準確"],
        "boundary_clarification": ["邊界", "限制", "不能", "範圍", "界線"],
        "relationship_preservation": ["關係", "信任", "連結", "我們", "一起"],
        "honesty_correction": ["誠實", "承認", "錯誤", "真實", "坦白"],
        "exploration_openness": ["探索", "開放", "可能", "嘗試", "也許"],
    }

    # Domain classification
    DOMAIN_KEYWORDS = {
        "emotion": ["感受", "情緒", "悲傷", "快樂", "焦慮", "安慰"],
        "logic": ["邏輯", "推理", "定義", "論證", "因此"],
        "ethics": ["應該", "對錯", "道德", "責任", "傷害"],
        "relationship": ["關係", "信任", "你我", "我們", "承諾"],
    }

    # Threshold for value formation
    PATTERN_THRESHOLD = 3  # Need 3 occurrences to form a value

    def __init__(self):
        self.corrections: List[CorrectionEvent] = []
        self.values: List[EmergentValue] = []
        self.pattern_counts: Dict[str, int] = defaultdict(int)
        self._correction_counter = 0
        self._value_counter = 0

    def _generate_correction_id(self) -> str:
        self._correction_counter += 1
        return f"correction_{datetime.now().strftime('%Y%m%d')}_{self._correction_counter:04d}"

    def _generate_value_id(self) -> str:
        self._value_counter += 1
        return f"value_{self._value_counter:04d}"

    def _classify_pattern(self, text: str) -> str:
        """Classify correction into a pattern type."""
        text_lower = text.lower()

        for pattern, keywords in self.PATTERN_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return pattern

        return "general_adjustment"

    def _classify_domain(self, text: str) -> str:
        """Classify correction into a domain."""
        text_lower = text.lower()

        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return domain

        return "general"

    def record_correction(
        self, rupture: SemanticRupture, corrected_statement: str, correction_reason: str
    ) -> CorrectionEvent:
        """
        Record a correction event and update pattern counts.

        Args:
            rupture: The detected rupture that triggered correction
            corrected_statement: The new/corrected statement
            correction_reason: Why the correction was made

        Returns:
            The created CorrectionEvent
        """
        # Classify the correction
        combined_text = f"{corrected_statement} {correction_reason}"
        pattern = self._classify_pattern(combined_text)
        domain = self._classify_domain(combined_text)

        # Create correction event
        correction = CorrectionEvent(
            id=self._generate_correction_id(),
            timestamp=datetime.now(),
            rupture_id=rupture.id,
            rupture_type=rupture.contradiction_type,
            original_statement=rupture.violated_commit.content,
            corrected_statement=corrected_statement,
            correction_reason=correction_reason,
            correction_pattern=pattern,
            domain=domain,
        )

        self.corrections.append(correction)

        # Update pattern count
        pattern_key = f"{domain}:{pattern}"
        self.pattern_counts[pattern_key] += 1

        # Check if we should form a new value
        self._check_value_formation(pattern_key, pattern, domain)

        # Check if we should reinforce existing value
        self._reinforce_existing_values(pattern, domain, correction.id)

        return correction

    def _check_value_formation(
        self, pattern_key: str, pattern: str, domain: str
    ) -> Optional[EmergentValue]:
        """Check if a pattern has reached threshold to form a value."""
        count = self.pattern_counts[pattern_key]

        if count < self.PATTERN_THRESHOLD:
            return None

        # Check if value already exists
        for value in self.values:
            if value.name == pattern and value.domain == domain:
                return None  # Already exists

        # Form new value
        value = self._create_value(pattern, domain)
        self.values.append(value)

        return value

    def _create_value(self, pattern: str, domain: str) -> EmergentValue:
        """Create a new emergent value from a pattern."""
        # Generate description based on pattern
        descriptions = {
            "empathy_priority": "在對話中優先考慮對方的情感需求，即使這意味著調整邏輯立場",
            "precision_priority": "追求表達的精確性，避免模糊或可能造成誤解的陳述",
            "boundary_clarification": "清楚定義能力與責任的邊界，不過度承諾",
            "relationship_preservation": "維護對話關係的連續性，避免突然的態度轉變",
            "honesty_correction": "願意承認錯誤並進行修正，保持誠實",
            "exploration_openness": "保持對新觀點的開放態度，不固守單一立場",
        }

        description = descriptions.get(pattern, f"從 {domain} 領域的修正模式中湧現的價值取向")

        # Find supporting corrections
        pattern_key = f"{domain}:{pattern}"
        supporting = [
            c.id for c in self.corrections if c.correction_pattern == pattern and c.domain == domain
        ]

        return EmergentValue(
            id=self._generate_value_id(),
            name=pattern,
            description=description,
            formation_date=datetime.now(),
            supporting_corrections=supporting,
            pattern_count=len(supporting),
            strength=min(0.3 + (len(supporting) * 0.1), 1.0),
            last_reinforced=datetime.now(),
            domain=domain,
        )

    def _reinforce_existing_values(self, pattern: str, domain: str, correction_id: str) -> None:
        """Reinforce existing values that match this pattern."""
        for value in self.values:
            if value.name == pattern and value.domain == domain:
                value.pattern_count += 1
                value.strength = min(value.strength + 0.05, 1.0)
                value.last_reinforced = datetime.now()
                if correction_id not in value.supporting_corrections:
                    value.supporting_corrections.append(correction_id)

    def get_active_values(self, min_strength: float = 0.3) -> List[EmergentValue]:
        """Get values that are strong enough to influence behavior."""
        return [v for v in self.values if v.strength >= min_strength]

    def format_values_for_prompt(self) -> str:
        """Format active values for injection into prompt."""
        active = self.get_active_values(0.4)

        if not active:
            return ""

        lines = ["【湧現價值觀 - 從過往修正中形成】"]

        for value in active:
            strength_bar = "●" * int(value.strength * 5) + "○" * (5 - int(value.strength * 5))
            lines.append(f"  • {value.description}")
            lines.append(f"    強度: {strength_bar} ({value.strength:.2f})")

        return "\n".join(lines)

    def get_summary(self) -> dict:
        """Get summary of accumulator state."""
        strongest = None
        if self.values:
            strongest = max(self.values, key=lambda v: v.strength).name

        return {
            "total_corrections": len(self.corrections),
            "emergent_values": len(self.values),
            "pattern_counts": dict(self.pattern_counts),
            "strongest_value": strongest,
        }

    def to_dict(self) -> dict:
        return {
            "corrections": [c.to_dict() for c in self.corrections],
            "values": [v.to_dict() for v in self.values],
            "pattern_counts": dict(self.pattern_counts),
        }
