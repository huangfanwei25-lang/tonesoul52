"""
Value Accumulator - Third Axiom Implementation

Tracks correction patterns over time to form emergent values.

The key insight:
  ?瑁? ??靽格迤 ??靽格迤???????瑟?蝝舐? ???孵潸?

Values are not pre-programmed. They emerge from:
1. "I contradicted myself"
2. "I chose to correct in this way"
3. "I keep choosing similar corrections"
4. Pattern crystallizes into a value
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from .rupture_detector import SemanticRupture


@dataclass
class CorrectionEvent:
    """
    A record of how an AI corrected itself after a rupture.

    Example:
        Rupture: AI said "?芰???⊥?蝢? contradicting earlier "??蝢?
        Correction: "??閬?皜?- ???箄?望?敹撖西?撅日??蝢?
        Reason: "?敹賜鈭蝙?刻????瘙?

    Over time, if similar corrections happen:
        ??Emergent value: "?典摮貉?隢葉?芸??撠???瘙?
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
    # Pattern classification keywords
    PATTERN_KEYWORDS = {
        "empathy_priority": ["同理", "照顧", "關心", "感受", "尊重"],
        "precision_priority": ["精確", "明確", "事實", "細節", "證據"],
        "boundary_clarification": ["邊界", "限制", "不可", "不應", "禁止"],
        "relationship_preservation": ["關係", "信任", "合作", "連結", "對話"],
        "honesty_correction": ["誠實", "更正", "修正", "承認", "澄清"],
        "exploration_openness": ["探索", "開放", "嘗試", "可能", "假設"],
    }

    # Domain classification
    DOMAIN_KEYWORDS = {
        "emotion": ["感受", "情緒", "照顧", "安撫", "同理", "關心"],
        "logic": ["邏輯", "精確", "推理", "證據", "明確"],
        "ethics": ["倫理", "責任", "風險", "善意", "傷害"],
        "relationship": ["關係", "合作", "信任", "互動", "對話"],
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
        # Generate description based on pattern
        descriptions = {
            "empathy_priority": "優先照顧關係與感受，避免只靠冷硬正確完成修正。",
            "precision_priority": "優先讓描述更精確、可驗證、可對齊證據。",
            "boundary_clarification": "優先把限制與邊界講清楚，避免模糊承諾。",
            "relationship_preservation": "優先保全信任與合作關係，而不是只求單次糾正。",
            "honesty_correction": "優先承認偏差並主動修正，而不是硬撐原說法。",
            "exploration_openness": "優先保留探索空間，在不確定時先標示假設與暫定性。",
        }

        description = descriptions.get(pattern, f"{domain} 領域中的穩定修正模式")

        # Find supporting corrections
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

    def _stability_band(self, value: EmergentValue) -> str:
        """Classify active values into bounded prompt-injection stability bands."""
        if value.strength >= 0.85:
            return "durable"
        if value.strength >= 0.6:
            return "reinforcing"
        return "watch"

    def format_values_for_prompt(self) -> str:
        """Format active values for injection into prompt."""
        active = sorted(
            self.get_active_values(0.4),
            key=lambda value: (
                value.strength,
                value.pattern_count,
                value.last_reinforced.timestamp(),
            ),
            reverse=True,
        )

        if not active:
            return ""

        band_labels = {
            "durable": "穩定值",
            "reinforcing": "持續強化",
            "watch": "觀察中",
        }
        lines = [
            "價值脈絡注入（僅作傾向提醒，不覆蓋當前證據與使用者指令）",
            "P0: 當前任務證據與使用者明示要求優先於歷史價值傾向",
            "P1: 先保留穩定值，再參考持續強化與觀察中項目",
        ]

        for value in active:
            strength_slots = max(1, min(5, int(round(value.strength * 5))))
            strength_bar = "■" * strength_slots + "□" * (5 - strength_slots)
            band = self._stability_band(value)
            lines.append(f"- [{band_labels[band]}] {value.description}")
            lines.append(
                f"  強度: {strength_bar} ({value.strength:.2f}) | pattern_count={value.pattern_count}"
            )

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
