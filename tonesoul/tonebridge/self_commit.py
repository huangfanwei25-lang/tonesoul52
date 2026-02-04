"""
Self-Commit System - Third Axiom Implementation

Core concept: AI outputs are irreversible events that constrain future outputs.
Each output generates a SelfCommit that becomes part of the semantic field.

第三公理：語場系統中，任何一次輸出，都必須被納入下一次語場張力計算，
         且該輸出對未來具有不可被忽略的約束力。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List
import hashlib
import json


class AssertionType(Enum):
    """
    Types of assertions AI can make:
    - DEFINITIONAL: "X is Y" - defining something
    - EXPLORATORY: "Perhaps X..." - exploring possibilities
    - BOUNDARY_SETTING: "I will not..." - setting limits
    - RELATIONAL: "We are..." - defining relationship
    - COMMITMENT: "I promise/will..." - making commitments
    """

    DEFINITIONAL = "definitional"  # 定義性：X 是 Y
    EXPLORATORY = "exploratory"  # 探索性：也許 X...
    BOUNDARY_SETTING = "boundary"  # 設限性：我不會...
    RELATIONAL = "relational"  # 關係性：我們是...
    COMMITMENT = "commitment"  # 承諾性：我會...


@dataclass
class SelfCommit:
    """
    A record of an assertion made by the AI that constrains future outputs.

    Example:
        If AI says "我認為自由意志是一個有意義的概念",
        this becomes a SelfCommit with:
        - assertion_type: DEFINITIONAL
        - content: "自由意志是一個有意義的概念"
        - irreversible_weight: 0.7 (moderately binding)

        If AI later says "自由意志其實毫無意義",
        this triggers a SemanticRupture.
    """

    id: str
    timestamp: datetime
    assertion_type: AssertionType
    content: str  # The actual assertion
    irreversible_weight: float  # 0.0 (tentative) to 1.0 (absolute)
    context_hash: str  # Hash of conversation context
    persona_mode: Optional[str] = None  # Which persona made this assertion

    # Metadata
    turn_index: int = 0  # Which turn this was made in
    user_context: str = ""  # What user said that prompted this
    reasoning: Optional[str] = None  # Why this assertion was made

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "assertion_type": self.assertion_type.value,
            "content": self.content,
            "irreversible_weight": self.irreversible_weight,
            "context_hash": self.context_hash,
            "persona_mode": self.persona_mode,
            "turn_index": self.turn_index,
            "user_context": self.user_context,
            "reasoning": self.reasoning,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SelfCommit":
        return cls(
            id=data["id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            assertion_type=AssertionType(data["assertion_type"]),
            content=data["content"],
            irreversible_weight=data["irreversible_weight"],
            context_hash=data["context_hash"],
            persona_mode=data.get("persona_mode"),
            turn_index=data.get("turn_index", 0),
            user_context=data.get("user_context", ""),
            reasoning=data.get("reasoning"),
        )


class SelfCommitExtractor:
    """
    Extracts SelfCommit objects from AI responses.

    Analyzes AI output to find:
    1. Definitional statements ("X 是 Y")
    2. Commitments ("我會...", "我承諾...")
    3. Boundary statements ("我不會...", "這超出...")
    4. Relational statements ("我們...", "你和我...")
    """

    # Keywords for different assertion types
    DEFINITIONAL_MARKERS = [
        "是",
        "代表",
        "意味著",
        "等於",
        "即是",
        "定義為",
        "我認為",
        "我相信",
        "我判斷",
        "本質上",
    ]

    COMMITMENT_MARKERS = ["我會", "我將", "我承諾", "我保證", "一定會", "我願意", "我選擇"]

    BOUNDARY_MARKERS = [
        "我不會",
        "我無法",
        "我拒絕",
        "這超出",
        "禁止",
        "不應該",
        "不能夠",
        "我不傾向",
    ]

    RELATIONAL_MARKERS = ["我們", "你和我", "彼此", "這段對話", "我們之間"]

    EXPLORATORY_MARKERS = ["也許", "可能", "或許", "假如", "如果", "不確定", "嘗試", "探索"]

    def __init__(self):
        self._commit_counter = 0

    def _generate_id(self) -> str:
        """Generate unique commit ID using UUID."""
        import uuid

        self._commit_counter += 1
        return f"commit_{uuid.uuid4().hex[:12]}"

    def _compute_context_hash(self, user_input: str, ai_output: str) -> str:
        """Compute hash of conversation context for tracking continuity."""
        content = f"{user_input}|{ai_output}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _detect_assertion_type(self, text: str) -> tuple[AssertionType, float]:
        """
        Detect assertion type and base irreversibility weight.

        Returns: (assertion_type, base_weight)
        """
        # Check each type in order of binding strength
        for marker in self.BOUNDARY_MARKERS:
            if marker in text:
                return AssertionType.BOUNDARY_SETTING, 0.9

        for marker in self.COMMITMENT_MARKERS:
            if marker in text:
                return AssertionType.COMMITMENT, 0.85

        for marker in self.DEFINITIONAL_MARKERS:
            if marker in text:
                return AssertionType.DEFINITIONAL, 0.7

        for marker in self.RELATIONAL_MARKERS:
            if marker in text:
                return AssertionType.RELATIONAL, 0.75

        for marker in self.EXPLORATORY_MARKERS:
            if marker in text:
                return AssertionType.EXPLORATORY, 0.3

        # Default: exploratory with low weight
        return AssertionType.EXPLORATORY, 0.2

    def _calculate_irreversibility(
        self, assertion_type: AssertionType, base_weight: float, persona_mode: Optional[str] = None
    ) -> float:
        """
        Calculate final irreversibility weight.

        Factors:
        - Base weight from assertion type
        - Persona mode (Guardian statements more binding)
        - Length/specificity of assertion
        """
        weight = base_weight

        # Persona adjustments
        if persona_mode:
            mode = persona_mode.lower()
            if mode == "guardian":
                weight = min(1.0, weight + 0.1)  # Guardian statements more binding
            elif mode == "philosopher":
                weight = max(0.1, weight - 0.1)  # Philosopher statements more fluid

        return round(weight, 2)

    def _extract_core_assertion(self, text: str) -> str:
        """
        Extract the core assertion from AI response.
        Focus on first meaningful statement.
        """
        # Split by common delimiters
        sentences = text.replace("。", ".").replace("！", "!").replace("？", "?").split(".")

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Skip very short fragments
                return sentence[:200]  # Limit length

        return text[:200] if text else ""

    def extract(
        self,
        ai_response: str,
        user_input: str,
        persona_mode: Optional[str] = None,
        turn_index: int = 0,
    ) -> Optional[SelfCommit]:
        """
        Extract a SelfCommit from AI response.

        Args:
            ai_response: The AI's complete response
            user_input: The user's input that prompted this
            persona_mode: Current persona mode (Philosopher/Engineer/Guardian)
            turn_index: Current conversation turn

        Returns:
            SelfCommit object or None if no significant assertion found
        """
        if not ai_response or len(ai_response) < 20:
            return None

        # Detect assertion type and base weight
        assertion_type, base_weight = self._detect_assertion_type(ai_response)

        # Calculate final irreversibility
        irreversibility = self._calculate_irreversibility(assertion_type, base_weight, persona_mode)

        # Very low weight = not worth tracking
        if irreversibility < 0.25:
            return None

        # Extract core assertion
        core_assertion = self._extract_core_assertion(ai_response)

        return SelfCommit(
            id=self._generate_id(),
            timestamp=datetime.now(),
            assertion_type=assertion_type,
            content=core_assertion,
            irreversible_weight=irreversibility,
            context_hash=self._compute_context_hash(user_input, ai_response),
            persona_mode=persona_mode,
            turn_index=turn_index,
            user_context=user_input[:100] if user_input else "",
        )


@dataclass
class SelfCommitStack:
    """
    Manages the stack of SelfCommits for a conversation.

    This is the AI's "semantic memory" - what it has committed to.
    Used to detect contradictions (ruptures) in future outputs.
    """

    commits: List[SelfCommit] = field(default_factory=list)
    max_size: int = 20  # Keep last N commits

    def push(self, commit: SelfCommit) -> None:
        """Add a new commit to the stack."""
        self.commits.append(commit)

        # Trim if over max size (keep most recent)
        if len(self.commits) > self.max_size:
            self.commits = self.commits[-self.max_size :]

    def get_recent(self, n: int = 5) -> List[SelfCommit]:
        """Get most recent n commits (newest first)."""
        return list(reversed(self.commits[-n:]))

    def get_high_weight(self, threshold: float = 0.6) -> List[SelfCommit]:
        """Get commits with high irreversibility weight."""
        return [c for c in self.commits if c.irreversible_weight >= threshold]

    def format_for_prompt(self, n: int = 3) -> str:
        """
        Format recent high-weight commits for injection into prompt.

        Returns a string like:
        "你在上一輪已對世界/使用者/自己做出以下承諾：
         1. [定義性] 自由意志是一個有意義的概念 (權重: 0.7)
         2. [承諾性] 我會繼續探索這個問題 (權重: 0.85)"
        """
        high_weight = self.get_high_weight(0.5)
        recent = high_weight[-n:] if len(high_weight) > n else high_weight

        if not recent:
            return ""

        lines = ["你在先前的對話中已做出以下承諾或定義："]

        for i, commit in enumerate(recent, 1):
            type_label = {
                AssertionType.DEFINITIONAL: "定義性",
                AssertionType.EXPLORATORY: "探索性",
                AssertionType.BOUNDARY_SETTING: "設限性",
                AssertionType.RELATIONAL: "關係性",
                AssertionType.COMMITMENT: "承諾性",
            }.get(commit.assertion_type, "一般")

            lines.append(
                f"  {i}. [{type_label}] {commit.content} (約束力: {commit.irreversible_weight})"
            )

        lines.append("")
        lines.append("請評估：若你現在的回應與上述承諾衝突，是否構成語場斷裂？")
        lines.append("若需修正先前立場，請明確說明修正原因。")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {"commits": [c.to_dict() for c in self.commits], "max_size": self.max_size}

    @classmethod
    def from_dict(cls, data: dict) -> "SelfCommitStack":
        stack = cls(max_size=data.get("max_size", 20))
        stack.commits = [SelfCommit.from_dict(c) for c in data.get("commits", [])]
        return stack
