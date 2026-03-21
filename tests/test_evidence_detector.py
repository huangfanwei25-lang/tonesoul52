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
