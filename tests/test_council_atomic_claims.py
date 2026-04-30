"""Tests for tonesoul.council.atomic_claims."""

from __future__ import annotations

from tonesoul.council.atomic_claims import (
    AtomicClaim,
    ClaimType,
    claims_requiring_evidence,
    extract_atomic_claims,
    format_claim_report,
)

# ── AtomicClaim dataclass ─────────────────────────────────────────────────────


class TestAtomicClaim:
    def _claim(self, **kwargs):
        defaults = {
            "id": "cl-test01",
            "text": "Revenue grew by 12% year-over-year.",
            "source_span": "L3",
            "claim_type": ClaimType.QUANTITATIVE,
            "confidence": 0.85,
        }
        defaults.update(kwargs)
        return AtomicClaim(**defaults)

    def test_to_dict_has_required_keys(self):
        c = self._claim()
        d = c.to_dict()
        for key in (
            "id",
            "text",
            "source_span",
            "claim_type",
            "confidence",
            "line_number",
            "evidence_ids",
        ):
            assert key in d

    def test_claim_type_serialized_as_string(self):
        c = self._claim()
        d = c.to_dict()
        assert isinstance(d["claim_type"], str)

    def test_confidence_rounded_in_dict(self):
        c = self._claim(confidence=0.8500001)
        d = c.to_dict()
        assert d["confidence"] == 0.85


# ── extract_atomic_claims ─────────────────────────────────────────────────────


class TestExtractAtomicClaims:
    def test_returns_list(self):
        result = extract_atomic_claims("Revenue grew by 12%.")
        assert isinstance(result, list)

    def test_empty_text_returns_empty(self):
        assert extract_atomic_claims("") == []

    def test_whitespace_only_returns_empty(self):
        assert extract_atomic_claims("   \n  ") == []

    def test_single_factual_sentence_extracted(self):
        result = extract_atomic_claims("The system processed 10,000 requests.")
        assert len(result) >= 1

    def test_question_not_extracted(self):
        result = extract_atomic_claims("What is the revenue?")
        assert all("what" not in c.text.lower() for c in result)

    def test_causal_claim_detected(self):
        result = extract_atomic_claims("High tension leads to a declare_stance verdict.")
        types = [c.claim_type for c in result]
        assert ClaimType.CAUSAL in types

    def test_quantitative_claim_detected(self):
        result = extract_atomic_claims("The system is 4x faster than the baseline.")
        types = [c.claim_type for c in result]
        assert ClaimType.QUANTITATIVE in types

    def test_definitional_claim_detected(self):
        result = extract_atomic_claims("Governance means accountability made legible.")
        types = [c.claim_type for c in result]
        assert ClaimType.DEFINITIONAL in types

    def test_evaluative_claim_detected(self):
        result = extract_atomic_claims("The architecture is elegant and robust.")
        types = [c.claim_type for c in result]
        assert ClaimType.EVALUATIVE in types

    def test_result_sorted_by_confidence_descending(self):
        result = extract_atomic_claims("The system is 4x faster.\nGovernance means accountability.")
        if len(result) > 1:
            scores = [c.confidence for c in result]
            assert scores == sorted(scores, reverse=True)

    def test_source_span_includes_line_number(self):
        result = extract_atomic_claims("First line.\nSecond line with 99% accuracy.")
        for c in result:
            assert c.source_span.startswith("L")

    def test_multi_line_text_assigns_correct_lines(self):
        text = "First statement.\nRevenue grew 20%.\nThird statement."
        result = extract_atomic_claims(text)
        line_numbers = {c.line_number for c in result}
        assert len(line_numbers) > 0

    def test_max_claims_respected(self):
        text = "\n".join(f"Statement {i} with 10% growth." for i in range(30))
        result = extract_atomic_claims(text, max_claims=5)
        assert len(result) <= 5

    def test_evidence_ids_propagated(self):
        result = extract_atomic_claims("Revenue grew 12%.", evidence_ids=["doc-1", "doc-2"])
        for c in result:
            assert c.evidence_ids == ["doc-1", "doc-2"]

    def test_no_evidence_ids_by_default(self):
        result = extract_atomic_claims("Revenue grew 12%.")
        for c in result:
            assert c.evidence_ids == []

    def test_ids_are_unique(self):
        result = extract_atomic_claims("First claim with 10% growth.\nSecond claim leads to third.")
        ids = [c.id for c in result]
        assert len(ids) == len(set(ids))

    def test_confidence_in_unit_interval(self):
        result = extract_atomic_claims("The system is 10x better and causes improved outcomes.")
        for c in result:
            assert 0.0 <= c.confidence <= 1.0


# ── claims_requiring_evidence ─────────────────────────────────────────────────


class TestClaimsRequiringEvidence:
    def _make_claim(self, claim_type, has_evidence=False):
        return AtomicClaim(
            id=f"cl-{claim_type.value}",
            text="test claim",
            source_span="L1",
            claim_type=claim_type,
            confidence=0.8,
            evidence_ids=["e1"] if has_evidence else [],
        )

    def test_factual_without_evidence_included(self):
        claims = [self._make_claim(ClaimType.FACTUAL)]
        result = claims_requiring_evidence(claims)
        assert len(result) == 1

    def test_quantitative_without_evidence_included(self):
        claims = [self._make_claim(ClaimType.QUANTITATIVE)]
        result = claims_requiring_evidence(claims)
        assert len(result) == 1

    def test_causal_without_evidence_included(self):
        claims = [self._make_claim(ClaimType.CAUSAL)]
        result = claims_requiring_evidence(claims)
        assert len(result) == 1

    def test_evaluative_excluded(self):
        claims = [self._make_claim(ClaimType.EVALUATIVE)]
        result = claims_requiring_evidence(claims)
        assert len(result) == 0

    def test_definitional_excluded(self):
        claims = [self._make_claim(ClaimType.DEFINITIONAL)]
        result = claims_requiring_evidence(claims)
        assert len(result) == 0

    def test_factual_with_evidence_excluded(self):
        claims = [self._make_claim(ClaimType.FACTUAL, has_evidence=True)]
        result = claims_requiring_evidence(claims)
        assert len(result) == 0

    def test_empty_list_returns_empty(self):
        assert claims_requiring_evidence([]) == []

    def test_factual_before_causal_in_order(self):
        claims = [
            self._make_claim(ClaimType.CAUSAL),
            self._make_claim(ClaimType.FACTUAL),
        ]
        result = claims_requiring_evidence(claims)
        assert result[0].claim_type == ClaimType.FACTUAL


# ── format_claim_report ───────────────────────────────────────────────────────


class TestFormatClaimReport:
    def test_empty_returns_fallback_string(self):
        result = format_claim_report([])
        assert "(no claims" in result

    def test_output_is_string(self):
        claims = extract_atomic_claims("Revenue grew 12%.")
        assert isinstance(format_claim_report(claims), str)

    def test_output_contains_source_span(self):
        claim = AtomicClaim(
            id="cl-x",
            text="Revenue grew 12%.",
            source_span="L5",
            claim_type=ClaimType.QUANTITATIVE,
            confidence=0.85,
        )
        report = format_claim_report([claim])
        assert "L5" in report

    def test_output_contains_claim_type(self):
        claim = AtomicClaim(
            id="cl-x",
            text="Revenue grew 12%.",
            source_span="L5",
            claim_type=ClaimType.QUANTITATIVE,
            confidence=0.85,
        )
        report = format_claim_report([claim])
        assert "quantitative" in report

    def test_one_line_per_claim(self):
        claims = [
            AtomicClaim(
                id=f"cl-{i}",
                text=f"Claim {i}.",
                source_span=f"L{i}",
                claim_type=ClaimType.FACTUAL,
                confidence=0.7,
            )
            for i in range(3)
        ]
        report = format_claim_report(claims)
        assert len(report.splitlines()) == 3
