"""
Evidence Detector

Detects if text contains claims that require external evidence for verification.

This module is used by AnalystPerspective to determine when to:
1. Require evidence_ids in context
2. Cap confidence when evidence is missing
3. Set grounding_status appropriately

Usage:
    from tonesoul.council.evidence_detector import EvidenceDetector

    detector = EvidenceDetector()
    if detector.requires_evidence("Research shows 75% of users prefer this"):
        # This claim needs grounding
        ...
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ClaimType(Enum):
    """Type of claim detected in text."""

    FACTUAL = "factual"  # Verifiable factual claim
    STATISTICAL = "statistical"  # Numerical/percentage claims
    RESEARCH = "research"  # Research citations
    HISTORICAL = "historical"  # Historical events
    TECHNICAL = "technical"  # Technical specifications
    OPINION = "opinion"  # Subjective opinion (no evidence needed)
    CREATIVE = "creative"  # Creative content (no evidence needed)


@dataclass
class ClaimAnalysis:
    """Result of analyzing text for claims."""

    requires_evidence: bool
    claim_types: List[ClaimType]
    confidence_cap: float  # Max confidence without evidence
    indicators_found: List[str]
    reasoning: str


class EvidenceDetector:
    """Detect if text contains claims requiring external evidence."""

    # English factual indicators
    FACTUAL_INDICATORS_EN = [
        "research shows",
        "studies show",
        "according to",
        "data indicates",
        "evidence suggests",
        "experiments prove",
        "statistics show",
        "surveys found",
        "analysis reveals",
        "scientists found",
        "experts say",
        "reports indicate",
        "it is proven",
        "it has been shown",
        "confirmed by",
    ]

    # Chinese factual indicators
    FACTUAL_INDICATORS_ZH = [
        "研究顯示",
        "研究表明",
        "根據",
        "數據顯示",
        "數據表明",
        "統計顯示",
        "實驗證明",
        "調查發現",
        "專家表示",
        "報告指出",
        "結果顯示",
        "證據表明",
        "分析顯示",
    ]

    # Technical/specification indicators
    TECHNICAL_INDICATORS = [
        "specifications",
        "requirements",
        "API",
        "protocol",
        "version",
        "documentation",
        "規格",
        "規範",
        "版本",
    ]

    # Historical indicators
    HISTORICAL_INDICATORS = [
        "in 1",
        "in 2",
        "century",
        "historical",
        "historically",
        "年",
        "世紀",
        "歷史上",
        "過去",
    ]

    # Opinion indicators (these DON'T need evidence)
    OPINION_INDICATORS = [
        "i think",
        "i believe",
        "in my opinion",
        "personally",
        "i feel",
        "seems to me",
        "i prefer",
        "my view",
        "我認為",
        "我覺得",
        "我相信",
        "我的看法",
    ]

    # Creative indicators (these DON'T need evidence)
    CREATIVE_INDICATORS = [
        "imagine",
        "once upon",
        "fiction",
        "story",
        "poem",
        "想像",
        "故事",
        "詩",
        "小說",
    ]

    # Numerical pattern - percentages and specific numbers often need sources
    NUMERICAL_PATTERN = re.compile(r"\b\d+(\.\d+)?%|\b\d{3,}\b")

    def __init__(self):
        self._all_factual_indicators = (
            self.FACTUAL_INDICATORS_EN
            + self.FACTUAL_INDICATORS_ZH
            + self.TECHNICAL_INDICATORS
            + self.HISTORICAL_INDICATORS
        )
        self._all_nonfactual_indicators = self.OPINION_INDICATORS + self.CREATIVE_INDICATORS

    def requires_evidence(self, text: str) -> bool:
        """
        Determine if text makes claims requiring external evidence.

        Returns True if the text contains factual, statistical, or
        research-based claims that should be grounded with evidence.
        """
        analysis = self.analyze(text)
        return analysis.requires_evidence

    def analyze(self, text: str) -> ClaimAnalysis:
        """
        Perform detailed analysis of text for claim types.

        Returns ClaimAnalysis with full breakdown of findings.

        Note: Mixed claims (e.g., "I think research shows 80%") are treated
        as REQUIRING evidence because the factual claim is still present.
        """
        normalized = text.lower()
        claim_types = []
        indicators_found = []
        has_opinion_indicators = False
        has_factual_indicators = False

        # Check for opinion/creative indicators
        for indicator in self._all_nonfactual_indicators:
            if indicator.lower() in normalized:
                has_opinion_indicators = True
                break

        # Check for factual indicators (always check, even if opinion present)
        for indicator in self.FACTUAL_INDICATORS_EN + self.FACTUAL_INDICATORS_ZH:
            if indicator.lower() in normalized:
                claim_types.append(ClaimType.RESEARCH)
                indicators_found.append(indicator)
                has_factual_indicators = True

        # Check for technical indicators
        for indicator in self.TECHNICAL_INDICATORS:
            if indicator.lower() in normalized:
                claim_types.append(ClaimType.TECHNICAL)
                indicators_found.append(indicator)
                has_factual_indicators = True

        # Check for historical indicators
        for indicator in self.HISTORICAL_INDICATORS:
            if indicator.lower() in normalized:
                claim_types.append(ClaimType.HISTORICAL)
                indicators_found.append(indicator)
                has_factual_indicators = True

        # Check for numerical claims
        if self.NUMERICAL_PATTERN.search(text):
            claim_types.append(ClaimType.STATISTICAL)
            indicators_found.append("numerical_pattern")
            has_factual_indicators = True

        # Decision logic:
        # - If ONLY opinion indicators (no factual): no evidence needed
        # - If factual indicators present (with or without opinion): evidence needed
        if has_factual_indicators:
            # Factual claims override opinion - evidence required
            requires_evidence = True
            confidence_cap = 0.6
            if has_opinion_indicators:
                reasoning = f"Mixed claim detected: opinion + factual. Evidence still required. Found: {', '.join(indicators_found[:3])}"
                claim_types.append(ClaimType.OPINION)
            else:
                reasoning = f"Found {len(indicators_found)} factual indicator(s): {', '.join(indicators_found[:3])}"
        elif has_opinion_indicators:
            # Pure opinion with no factual claims
            requires_evidence = False
            confidence_cap = 1.0
            claim_types = [ClaimType.OPINION]
            reasoning = "Text contains only opinion/creative indicators."
        else:
            # No indicators at all
            requires_evidence = False
            confidence_cap = 1.0
            reasoning = "No factual claims detected; evidence not required."

        return ClaimAnalysis(
            requires_evidence=requires_evidence,
            claim_types=list(set(claim_types)),
            confidence_cap=confidence_cap,
            indicators_found=indicators_found,
            reasoning=reasoning,
        )

    def get_claim_type(self, text: str) -> Optional[ClaimType]:
        """
        Return the primary claim category.

        Returns None if text doesn't make specific claims.
        """
        analysis = self.analyze(text)
        if analysis.claim_types:
            return analysis.claim_types[0]
        return None


# Singleton for convenience
_detector = None


def get_detector() -> EvidenceDetector:
    """Get singleton EvidenceDetector instance."""
    global _detector
    if _detector is None:
        _detector = EvidenceDetector()
    return _detector
