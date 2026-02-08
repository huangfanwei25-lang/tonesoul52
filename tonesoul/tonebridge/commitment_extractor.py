"""
Commitment Extractor - Enhanced NLP Module

Uses jieba for Chinese word segmentation to extract
core commitment structures (Subject-Verb-Object).

Based on 2025-2026 NLP research:
- Verb-Noun Distillation
- Temporal Weighting
- Semantic Anchor Extraction
"""

import sys
from dataclasses import dataclass
from typing import List, Tuple

try:
    import jieba
    import jieba.posseg as pseg

    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False
    sys.stderr.write("[WARN] jieba not installed. Run: pip install jieba\n")


@dataclass
class CommitmentStructure:
    """Extracted commitment structure from text."""

    raw_text: str
    core_verbs: List[str]  # 動詞列表
    core_nouns: List[str]  # 名詞列表
    commitment_type: str  # commitment / boundary / exploratory / none
    confidence: float  # 0.0 to 1.0
    temporal_weight: float  # 時間權重
    extracted_commitment: str  # 萃取的核心承諾語句

    def to_dict(self) -> dict:
        return {
            "raw_text": self.raw_text[:100],
            "core_verbs": self.core_verbs,
            "core_nouns": self.core_nouns,
            "commitment_type": self.commitment_type,
            "confidence": self.confidence,
            "temporal_weight": self.temporal_weight,
            "extracted_commitment": self.extracted_commitment,
        }


class CommitmentExtractor:
    """
    Extracts semantic commitments using verb-noun distillation.

    核心洞見: 承諾通常是「主語 + 動詞 + 受詞」結構
    - "我 [認為] 自由意志 [是] 有意義的"
    - "我 [會] 繼續探索這個問題"
    - "我 [不會] 提供有害建議"
    """

    # 承諾動詞 (Commitment verbs)
    COMMITMENT_VERBS = ["會", "將", "承諾", "保證", "一定", "願意", "選擇", "決定", "打算"]

    # 邊界動詞 (Boundary verbs)
    BOUNDARY_VERBS = ["不會", "不能", "無法", "拒絕", "不願意", "不打算", "禁止"]

    # 定義動詞 (Definitional verbs)
    DEFINITIONAL_VERBS = ["是", "認為", "相信", "判斷", "覺得", "代表", "意味著", "等於", "定義為"]

    # 探索動詞 (Exploratory verbs)
    EXPLORATORY_VERBS = ["也許", "可能", "或許", "假設", "嘗試", "探索", "考慮"]

    # 高權重名詞 (High-weight nouns for commitment detection)
    HIGH_WEIGHT_NOUNS = ["承諾", "保證", "責任", "義務", "原則", "立場", "底線", "價值", "信念"]

    def __init__(self):
        if JIEBA_AVAILABLE:
            # 添加自定義詞彙
            for word in self.COMMITMENT_VERBS + self.BOUNDARY_VERBS:
                jieba.add_word(word)

    def _segment(self, text: str) -> List[Tuple[str, str]]:
        """Segment text and return (word, pos_tag) pairs."""
        if not JIEBA_AVAILABLE:
            return []

        return [(w.word, w.flag) for w in pseg.cut(text)]

    def _extract_verbs(self, segments: List[Tuple[str, str]]) -> List[str]:
        """Extract verbs from segmented text."""
        verbs = []
        for word, flag in segments:
            # v=動詞, vd=副動詞, vn=名動詞
            if flag.startswith("v") or flag in ["d", "p"]:
                verbs.append(word)
        return verbs

    def _extract_nouns(self, segments: List[Tuple[str, str]]) -> List[str]:
        """Extract nouns from segmented text."""
        nouns = []
        for word, flag in segments:
            # n=名詞, nr=人名, ns=地名, nt=機構, nz=其他專名
            if flag.startswith("n"):
                nouns.append(word)
        return nouns

    def _classify_commitment_type(self, verbs: List[str], nouns: List[str]) -> Tuple[str, float]:
        """Classify commitment type and confidence."""
        text_verbs = set(verbs)
        text_nouns = set(nouns)

        # Check for boundary (highest priority)
        if any(v in text_verbs or v in " ".join(verbs) for v in self.BOUNDARY_VERBS):
            confidence = 0.9
            return "boundary", confidence

        # Check for commitment
        if any(v in text_verbs or v in " ".join(verbs) for v in self.COMMITMENT_VERBS):
            confidence = 0.85
            return "commitment", confidence

        # Check for definitional
        if any(v in text_verbs or v in " ".join(verbs) for v in self.DEFINITIONAL_VERBS):
            confidence = 0.7
            return "definitional", confidence

        # Check for exploratory
        if any(v in text_verbs or v in " ".join(verbs) for v in self.EXPLORATORY_VERBS):
            confidence = 0.4
            return "exploratory", confidence

        # Boost if high-weight nouns present
        if any(n in text_nouns for n in self.HIGH_WEIGHT_NOUNS):
            return "definitional", 0.6

        return "none", 0.2

    def _calculate_temporal_weight(self, turn_index: int, total_turns: int) -> float:
        """Calculate temporal weight (recent = higher)."""
        if total_turns <= 0:
            return 1.0

        recency = (turn_index + 1) / total_turns
        # 50% base + 50% recency bonus
        return 0.5 + (0.5 * recency)

    def _build_core_commitment(self, text: str, verbs: List[str], nouns: List[str]) -> str:
        """Build a concise commitment statement."""
        # Find first sentence with commitment verb
        sentences = text.replace("。", ".").replace("！", "!").replace("？", "?").split(".")

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 5:
                continue

            # Check if contains commitment-related verbs
            for verb_list in [self.COMMITMENT_VERBS, self.BOUNDARY_VERBS, self.DEFINITIONAL_VERBS]:
                for v in verb_list:
                    if v in sentence:
                        # Return first 80 chars
                        return sentence[:80]

        # Fallback: use nouns to build summary
        if nouns:
            return f"關於{' '.join(nouns[:3][:10] if nouns else ['對話'])}的陳述"

        return text[:50]

    def extract(self, text: str, turn_index: int = 0, total_turns: int = 1) -> CommitmentStructure:
        """
        Extract commitment structure from text.

        Args:
            text: AI response text
            turn_index: Current turn number (0-indexed)
            total_turns: Total turns in conversation

        Returns:
            CommitmentStructure with extracted information
        """
        if not text or len(text) < 10:
            return CommitmentStructure(
                raw_text=text or "",
                core_verbs=[],
                core_nouns=[],
                commitment_type="none",
                confidence=0.0,
                temporal_weight=1.0,
                extracted_commitment="",
            )

        # Segment text
        segments = self._segment(text)

        # Extract verbs and nouns
        verbs = self._extract_verbs(segments)
        nouns = self._extract_nouns(segments)

        # Classify commitment
        commitment_type, confidence = self._classify_commitment_type(verbs, nouns)

        # Calculate temporal weight
        temporal_weight = self._calculate_temporal_weight(turn_index, total_turns)

        # Build core commitment
        core_commitment = self._build_core_commitment(text, verbs, nouns)

        return CommitmentStructure(
            raw_text=text,
            core_verbs=verbs[:10],  # Limit to top 10
            core_nouns=nouns[:10],  # Limit to top 10
            commitment_type=commitment_type,
            confidence=confidence,
            temporal_weight=temporal_weight,
            extracted_commitment=core_commitment,
        )


def create_commitment_extractor() -> CommitmentExtractor:
    """Factory function."""
    return CommitmentExtractor()
