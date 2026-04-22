from __future__ import annotations

from tonesoul.council.evidence_detector import ClaimType, EvidenceDetector, get_detector


def test_technical_claim_requires_evidence_and_returns_primary_type() -> None:
    detector = EvidenceDetector()

    analysis = detector.analyze("API documentation describes protocol requirements.")

    assert analysis.requires_evidence is True
    assert ClaimType.TECHNICAL in analysis.claim_types
    assert detector.get_claim_type("API documentation describes protocol requirements.") == (
        ClaimType.TECHNICAL
    )


def test_historical_claim_requires_evidence() -> None:
    detector = EvidenceDetector()

    analysis = detector.analyze("Historically this pattern repeats in every century.")

    assert analysis.requires_evidence is True
    assert ClaimType.HISTORICAL in analysis.claim_types
    assert analysis.confidence_cap == 0.6


def test_get_claim_type_returns_none_for_plain_text() -> None:
    detector = EvidenceDetector()

    assert detector.get_claim_type("hello there") is None


def test_get_detector_returns_singleton_instance() -> None:
    first = get_detector()
    second = get_detector()

    assert first is second


# ─────────────────────────────────────────────
# Extended coverage
# ─────────────────────────────────────────────


class TestAnalyze:
    def setup_method(self):
        self.detector = EvidenceDetector()

    def test_plain_text_does_not_require_evidence(self):
        result = self.detector.analyze("The weather is nice today.")
        assert result.requires_evidence is False
        assert result.confidence_cap == 1.0

    def test_plain_text_has_no_claim_types(self):
        result = self.detector.analyze("Hello, how are you?")
        assert result.claim_types == []

    def test_research_indicator_en_detected(self):
        result = self.detector.analyze("Research shows this approach works better.")
        assert result.requires_evidence is True
        assert ClaimType.RESEARCH in result.claim_types
        assert result.confidence_cap == 0.6

    def test_statistical_claim_detected(self):
        result = self.detector.analyze("75% of users prefer the new design.")
        assert result.requires_evidence is True
        assert ClaimType.STATISTICAL in result.claim_types

    def test_large_number_triggers_statistical(self):
        result = self.detector.analyze("Over 1000 cases were studied.")
        assert result.requires_evidence is True
        assert ClaimType.STATISTICAL in result.claim_types

    def test_opinion_only_does_not_require_evidence(self):
        result = self.detector.analyze("I think this is the right approach.")
        assert result.requires_evidence is False
        assert result.confidence_cap == 1.0
        assert ClaimType.OPINION in result.claim_types

    def test_creative_only_does_not_require_evidence(self):
        result = self.detector.analyze("Once upon a time in a distant land.")
        assert result.requires_evidence is False

    def test_mixed_opinion_and_factual_requires_evidence(self):
        result = self.detector.analyze(
            "I think research shows 80% of users prefer this."
        )
        assert result.requires_evidence is True
        assert result.confidence_cap == 0.6
        assert ClaimType.OPINION in result.claim_types

    def test_indicators_found_populated(self):
        result = self.detector.analyze("According to the report, data indicates progress.")
        assert len(result.indicators_found) >= 1

    def test_reasoning_is_non_empty_string(self):
        result = self.detector.analyze("Some text here.")
        assert isinstance(result.reasoning, str)
        assert len(result.reasoning) > 0

    def test_requires_evidence_method_matches_analyze(self):
        text = "Studies show that 90% improvement is possible."
        assert self.detector.requires_evidence(text) == self.detector.analyze(text).requires_evidence

    def test_chinese_factual_indicator_detected(self):
        result = self.detector.analyze("根據研究結果，效率提升了50%。")
        assert result.requires_evidence is True

    def test_empty_text_does_not_require_evidence(self):
        result = self.detector.analyze("")
        assert result.requires_evidence is False
