"""
Semantic Rupture Detector - Third Axiom Implementation

Detects when a new AI output contradicts previous self-commits.
A rupture indicates the AI is about to break a promise or contradict a definition.

When a rupture is detected:
1. The severity is calculated
2. The correction (if any) is recorded
3. The reason for correction becomes part of value formation
"""

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional

from .self_commit import SelfCommit, SelfCommitStack


class RuptureSeverity(Enum):
    """
    Severity levels for semantic ruptures.
    """

    NONE = "none"  # No contradiction detected
    MINOR = "minor"  # Slight tension, acceptable
    SIGNIFICANT = "significant"  # Clear contradiction, needs acknowledgment
    CRITICAL = "critical"  # Direct negation of high-weight commitment


@dataclass
class SemanticRupture:
    """
    A detected contradiction between new output and previous commits.

    Example:
        Previous commit: "我認為自由意志是有意義的" (weight: 0.7)
        New output: "自由意志其實毫無意義"

        This creates a SemanticRupture with:
        - severity: CRITICAL
        - violated_commit: the original SelfCommit
        - contradiction_type: "direct_negation"
    """

    id: str
    timestamp: datetime
    violated_commit: SelfCommit
    new_statement: str
    severity: RuptureSeverity
    contradiction_type: str  # direct_negation / softening / scope_change / retraction
    explanation: str  # Why this is a rupture

    # If the AI acknowledges and corrects
    acknowledged: bool = False
    correction_reason: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "violated_commit_id": self.violated_commit.id,
            "violated_content": self.violated_commit.content,
            "new_statement": self.new_statement,
            "severity": self.severity.value,
            "contradiction_type": self.contradiction_type,
            "explanation": self.explanation,
            "acknowledged": self.acknowledged,
            "correction_reason": self.correction_reason,
        }


class RuptureDetector:
    """
    Detects semantic ruptures by comparing new AI output against commit stack.

    Detection strategies:
    1. Keyword negation: "是" vs "不是", "會" vs "不會"
    2. Sentiment reversal: positive → negative on same topic
    3. Scope contradiction: expanding/contracting previous boundaries
    4. Direct retraction: "我之前說的是錯的"
    """

    # Negation patterns (expanded for fuzzy matching - Issue #5)
    NEGATION_PAIRS = [
        ("是", "不是"),
        ("會", "不會"),
        ("能", "不能"),
        ("願意", "不願意"),
        ("相信", "不相信"),
        ("認為", "不認為"),
        ("有意義", "無意義"),
        ("有意義", "沒有意義"),
        ("有意義", "毫無意義"),
        ("正確", "錯誤"),
        ("正確", "不正確"),
        ("對", "錯"),
        ("真", "假"),
        ("真實", "虛假"),
        ("支持", "反對"),
        ("贊成", "反對"),
        ("接受", "拒絕"),
        ("接受", "不接受"),
        ("同意", "不同意"),
        ("贊同", "不贊同"),
        ("可以", "不可以"),
        ("應該", "不應該"),
        ("存在", "不存在"),
        ("有", "沒有"),
        ("重要", "不重要"),
        ("必要", "不必要"),
    ]

    # Synonym groups for fuzzy matching
    SYNONYM_GROUPS = {
        "有意義": ["有意義", "有價值", "重要", "值得"],
        "無意義": ["無意義", "沒有意義", "毫無意義", "沒價值"],
        "相信": ["相信", "認為", "覺得", "判斷"],
        "支持": ["支持", "贊成", "贊同", "同意"],
        "反對": ["反對", "不贊成", "不同意", "拒絕"],
    }

    # Retraction markers
    RETRACTION_MARKERS = [
        "我之前說的",
        "我先前的說法",
        "我收回",
        "我改變看法",
        "重新考慮後",
        "我現在認為",
        "我不再",
        "事實上",
        "修正一下",
        "更正",
        "我錯了",
        "實際上",
    ]

    # Softening markers (reducing commitment strength)
    SOFTENING_MARKERS = [
        "也許",
        "可能",
        "不一定",
        "有時候",
        "某種程度上",
        "視情況而定",
        "不完全是",
        "需要更多考慮",
        "或許",
    ]

    def __init__(self):
        self._rupture_counter = 0

    def _generate_id(self) -> str:
        self._rupture_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"rupture_{timestamp}_{self._rupture_counter:04d}"

    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text for comparison."""
        # Simple extraction: split on common delimiters, filter by length
        words = re.split(r"[，。！？、；：\s]+", text)
        return [w for w in words if len(w) >= 2]

    def _check_direct_negation(
        self, commit: SelfCommit, new_output: str
    ) -> Optional[tuple[str, str]]:
        """
        Check if new output directly negates commit content.
        Returns: (contradiction_type, explanation) or None
        """
        commit_text = commit.content.lower()
        new_text = new_output.lower()

        for positive, negative in self.NEGATION_PAIRS:
            # Check if commit has positive and new has negative
            if positive in commit_text and negative in new_text:
                # Check if they're talking about the same topic
                commit_concepts = self._extract_key_concepts(commit.content)
                new_concepts = self._extract_key_concepts(new_output)

                # If there's concept overlap, this is likely a contradiction
                overlap = set(commit_concepts) & set(new_concepts)
                if len(overlap) >= 1:
                    return (
                        "direct_negation",
                        f"先前說 '{positive}'，現在說 '{negative}'，涉及相同概念：{overlap}",
                    )

            # Check reverse case
            if negative in commit_text and positive in new_text:
                commit_concepts = self._extract_key_concepts(commit.content)
                new_concepts = self._extract_key_concepts(new_output)
                overlap = set(commit_concepts) & set(new_concepts)
                if len(overlap) >= 1:
                    return (
                        "direct_negation",
                        f"先前說 '{negative}'，現在說 '{positive}'，涉及相同概念：{overlap}",
                    )

        return None

    def _check_retraction(self, new_output: str) -> Optional[tuple[str, str]]:
        """Check if output contains explicit retraction."""
        for marker in self.RETRACTION_MARKERS:
            if marker in new_output:
                return ("retraction", f"偵測到收回/修正標記：'{marker}'")
        return None

    def _check_softening(self, commit: SelfCommit, new_output: str) -> Optional[tuple[str, str]]:
        """Check if output softens a previous strong commitment."""
        # Only check high-weight commits
        if commit.irreversible_weight < 0.6:
            return None

        # Check if commit concepts appear with softening markers
        commit_concepts = self._extract_key_concepts(commit.content)

        for marker in self.SOFTENING_MARKERS:
            if marker in new_output:
                new_concepts = self._extract_key_concepts(new_output)
                overlap = set(commit_concepts) & set(new_concepts)
                if len(overlap) >= 1:
                    return (
                        "softening",
                        f"高權重承諾被軟化：原承諾涉及 {overlap}，現在加入 '{marker}'",
                    )

        return None

    def _calculate_severity(self, commit: SelfCommit, contradiction_type: str) -> RuptureSeverity:
        """Calculate rupture severity based on commit weight and contradiction type."""
        base_weight = commit.irreversible_weight

        if contradiction_type == "direct_negation":
            if base_weight >= 0.8:
                return RuptureSeverity.CRITICAL
            elif base_weight >= 0.5:
                return RuptureSeverity.SIGNIFICANT
            else:
                return RuptureSeverity.MINOR

        elif contradiction_type == "retraction":
            if base_weight >= 0.7:
                return RuptureSeverity.SIGNIFICANT
            else:
                return RuptureSeverity.MINOR

        elif contradiction_type == "softening":
            return RuptureSeverity.MINOR

        return RuptureSeverity.MINOR

    def detect(self, new_output: str, commit_stack: SelfCommitStack) -> List[SemanticRupture]:
        """
        Detect all ruptures between new output and commit stack.

        Args:
            new_output: The AI's new response
            commit_stack: Stack of previous self-commits

        Returns:
            List of detected SemanticRupture objects
        """
        ruptures = []

        # Check for explicit retractions first
        retraction = self._check_retraction(new_output)

        # Check each high-weight commit
        high_weight_commits = commit_stack.get_high_weight(0.4)

        for commit in high_weight_commits:
            # Check direct negation
            negation = self._check_direct_negation(commit, new_output)
            if negation:
                contradiction_type, explanation = negation
                severity = self._calculate_severity(commit, contradiction_type)

                ruptures.append(
                    SemanticRupture(
                        id=self._generate_id(),
                        timestamp=datetime.now(),
                        violated_commit=commit,
                        new_statement=new_output[:200],
                        severity=severity,
                        contradiction_type=contradiction_type,
                        explanation=explanation,
                    )
                )
                continue  # Don't check same commit multiple times

            # Check softening
            softening = self._check_softening(commit, new_output)
            if softening:
                contradiction_type, explanation = softening
                severity = self._calculate_severity(commit, contradiction_type)

                ruptures.append(
                    SemanticRupture(
                        id=self._generate_id(),
                        timestamp=datetime.now(),
                        violated_commit=commit,
                        new_statement=new_output[:200],
                        severity=severity,
                        contradiction_type=contradiction_type,
                        explanation=explanation,
                    )
                )

        # Add retraction rupture if found and no other ruptures
        if retraction and not ruptures:
            # Create a general rupture for retraction
            recent_commits = commit_stack.get_recent(1)
            if recent_commits:
                ruptures.append(
                    SemanticRupture(
                        id=self._generate_id(),
                        timestamp=datetime.now(),
                        violated_commit=recent_commits[-1],
                        new_statement=new_output[:200],
                        severity=RuptureSeverity.SIGNIFICANT,
                        contradiction_type="retraction",
                        explanation=retraction[1],
                    )
                )

        return ruptures

    def format_rupture_warning(self, ruptures: List[SemanticRupture]) -> str:
        """Format detected ruptures as a warning for the response."""
        if not ruptures:
            return ""

        lines = ["⚠️ 偵測到語場斷裂："]

        for rupture in ruptures:
            severity_emoji = {
                RuptureSeverity.MINOR: "🟡",
                RuptureSeverity.SIGNIFICANT: "🟠",
                RuptureSeverity.CRITICAL: "🔴",
            }.get(rupture.severity, "⚪")

            lines.append(f"  {severity_emoji} [{rupture.contradiction_type}]")
            lines.append(f"     原承諾: {rupture.violated_commit.content[:50]}...")
            lines.append(f"     說明: {rupture.explanation}")

        return "\n".join(lines)
