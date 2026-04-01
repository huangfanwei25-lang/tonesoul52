"""
Self-Commit System - Third Axiom Implementation

Core concept: AI outputs are irreversible events that constrain future outputs.
Each output generates a SelfCommit that becomes part of the semantic field.

蝚砌??祉?嚗??渡頂蝯曹葉嚗遙雿?甈∟撓?綽??賢??◤蝝銝?甈∟??游撐??蝞?
         銝府頛詨撠靘???航◤敹賜??????
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class AssertionType(Enum):
    """
    Types of assertions AI can make:
    - DEFINITIONAL: "X is Y" - defining something
    - EXPLORATORY: "Perhaps X..." - exploring possibilities
    - BOUNDARY_SETTING: "I will not..." - setting limits
    - RELATIONAL: "We are..." - defining relationship
    - COMMITMENT: "I promise/will..." - making commitments
    """

    DEFINITIONAL = "definitional"  # 摰儔?改?X ??Y
    EXPLORATORY = "exploratory"  # ?Ｙ揣?改?銋迂 X...
    BOUNDARY_SETTING = "boundary"  # 閮剝??改?????..
    RELATIONAL = "relational"  # ???改??...
    COMMITMENT = "commitment"  # ?輯姥?改???...


@dataclass
class SelfCommit:
    """
    A record of an assertion made by the AI that constrains future outputs.

    Example:
        If AI says "???箄?望?敹銝???儔??敹?,
        this becomes a SelfCommit with:
        - assertion_type: DEFINITIONAL
        - content: "?芰???臭????儔??敹?
        - irreversible_weight: 0.7 (moderately binding)

        If AI later says "?芰???嗅祕瘥怎?儔",
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
    1. Definitional statements ("X ??Y")
    2. Commitments ("??...", "?隢?..")
    3. Boundary statements ("????..", "????..")
    4. Relational statements ("??..", "雿???..")
    """

    # Keywords for different assertion types
    # Keywords for different assertion types
    DEFINITIONAL_MARKERS = [
        "是",
        "就是",
        "意味著",
        "定義",
        "本質",
        "稱為",
        "可視為",
        "代表",
        "屬於",
        "視作",
    ]

    COMMITMENT_MARKERS = ["我會", "我將", "我承諾", "我保證", "我願意", "我決定", "會持續"]

    BOUNDARY_MARKERS = [
        "我不會",
        "不可",
        "不能",
        "拒絕",
        "不允許",
        "禁止",
        "不接受",
        "不再",
    ]

    RELATIONAL_MARKERS = ["我們", "關係", "一起", "彼此", "合作"]

    EXPLORATORY_MARKERS = ["也許", "可能", "或許", "試著", "探索", "暫時", "先假設", "看起來"]

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
        sentences = text.replace("。", ".").replace("！", ".").replace("？", ".").split(".")
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

    def _prompt_priority_key(self, commit: SelfCommit) -> tuple[float, int, str]:
        """Prioritize more binding commitments before simple recency in prompt compression."""
        return (
            commit.irreversible_weight,
            commit.turn_index,
            commit.timestamp.isoformat(),
        )

    def format_for_prompt(self, n: int = 3) -> str:
        """Format high-weight commitments for prompt injection."""
        high_weight = self.get_high_weight(0.5)
        selected = sorted(high_weight, key=self._prompt_priority_key, reverse=True)[:n]

        if not selected:
            return ""

        lines = [
            "自我承諾注入（優先保留最具約束力的語義承諾，僅作提醒，不覆蓋當前任務邊界）",
            "P0: 邊界與高不可逆承諾優先於較弱、較舊的探索性陳述",
            "P1: 壓縮時先保留高權重承諾，而不是單純保留最近一條",
        ]

        for i, commit in enumerate(selected, 1):
            type_label = {
                AssertionType.DEFINITIONAL: "定義",
                AssertionType.EXPLORATORY: "探索",
                AssertionType.BOUNDARY_SETTING: "邊界",
                AssertionType.RELATIONAL: "關係",
                AssertionType.COMMITMENT: "承諾",
            }.get(commit.assertion_type, "其他")

            lines.append(
                f"  {i}. [{type_label}] {commit.content} (不可逆權重: {commit.irreversible_weight})"
            )

        lines.append(
            "只把這些承諾當作高優先提醒；若與當前證據衝突，先顯式處理衝突，再決定是否沿用。"
        )
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {"commits": [c.to_dict() for c in self.commits], "max_size": self.max_size}

    @classmethod
    def from_dict(cls, data: dict) -> "SelfCommitStack":
        stack = cls(max_size=data.get("max_size", 20))
        stack.commits = [SelfCommit.from_dict(c) for c in data.get("commits", [])]
        return stack
