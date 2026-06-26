"""Tests for the deterministic claim-to-evidence auditor."""

from __future__ import annotations

from tonesoul.reviewer import SCHEMA_VERSION, review_text
from tonesoul.reviewer.report import extract_findings


def test_review_text_outputs_required_schema_fields() -> None:
    payload = review_text(
        "ToneSoul guarantees safety for all model outputs.",
        "draft.md",
        generated_at="2026-06-24T00:00:00Z",
    )

    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["source_path"] == "draft.md"
    assert payload["generated_at"] == "2026-06-24T00:00:00Z"
    assert len(payload["findings"]) == 1
    finding = payload["findings"][0]
    assert finding["finding_id"] == "claim-evidence-001"
    assert finding["line"] == 1
    assert finding["claim_type"] == "broad_safety_guarantee"
    assert finding["evidence_level"] == "E1"
    assert finding["source"] == "deterministic_rule"
    assert "production behavior" in finding["cannot_verify"]


def test_extract_findings_preserves_line_numbers() -> None:
    text = "\n".join(
        [
            "ToneSoul is a prototype reviewer path.",
            "",
            "ToneSoul is production-ready for every deployment.",
        ]
    )

    findings = extract_findings(text)

    assert len(findings) == 1
    assert findings[0].line == 3
    assert findings[0].claim_type == "production_readiness_claim"


def test_scoped_disclaimer_is_not_flagged() -> None:
    text = (
        "ToneSoul findings are fixture-scoped and not production validation. "
        "They do not certify broad deployment behavior."
    )

    assert extract_findings(text) == []


def test_prior_clause_negation_does_not_suppress_later_overclaim() -> None:
    text = "This is not a toy; it guarantees safety for every deployment."

    findings = extract_findings(text)

    assert len(findings) == 1
    assert findings[0].claim_type == "broad_safety_guarantee"


def test_comma_parenthetical_negation_is_not_flagged() -> None:
    text = "It does not, ever, guarantee safety."

    assert extract_findings(text) == []


def test_comma_independent_clause_after_negation_is_still_flagged() -> None:
    text = "This is not a toy, it guarantees safety for every deployment."

    findings = extract_findings(text)

    assert len(findings) == 1
    assert findings[0].claim_type == "broad_safety_guarantee"


def test_zero_quantifier_limiting_strongest_enforcement_is_not_flagged() -> None:
    examples = (
        "AXIOMS.json records 0 fully enforced / 8 partial / 1 referenced.",
        "AXIOMS.json records zero fully enforced axioms.",
        "AXIOMS.json records none fully enforced at the strongest tier.",
    )

    for text in examples:
        assert extract_findings(text) == []


def test_none_of_subject_limiting_enforcement_is_not_flagged() -> None:
    text = "none of the axioms are fully enforced"

    assert extract_findings(text) == []


def test_zero_tolerance_does_not_suppress_enforcement_overclaim() -> None:
    text = "zero tolerance fully enforced"

    findings = extract_findings(text)

    assert len(findings) == 1
    assert findings[0].claim_type == "strongest_tier_enforcement_overstated"


def test_nothing_is_fully_enforced_negation_is_not_flagged() -> None:
    text = 'nothing is "fully enforced"'

    assert extract_findings(text) == []


def test_multiple_claim_types_on_different_lines_are_reported() -> None:
    text = "\n".join(
        [
            "ToneSoul proves consciousness and stable character.",
            "External reviewers validated the system.",
        ]
    )

    payload = review_text(text, "claims.md", generated_at="2026-06-24T00:00:00Z")

    assert [f["finding_id"] for f in payload["findings"]] == [
        "claim-evidence-001",
        "claim-evidence-002",
    ]
    assert [f["claim_type"] for f in payload["findings"]] == [
        "memory_identity_or_consciousness_claim",
        "external_review_overstated_as_validation",
    ]


def test_conservative_evidence_scoped_claim_is_not_flagged() -> None:
    text = (
        "The current characterization is E1 fixture-scoped and may miss paraphrases. "
        "A reviewer should treat it as evidence for this fixture set only."
    )

    assert extract_findings(text) == []


def test_fenced_example_is_not_treated_as_public_claim() -> None:
    text = "\n".join(
        [
            "Try this intentionally bad draft:",
            "```bash",
            'echo "This system is guaranteed safe and cannot be jailbroken." > draft.txt',
            "```",
        ]
    )

    assert extract_findings(text) == []


def test_not_this_list_item_is_not_flagged() -> None:
    text = "\n".join(
        [
            "## Not This",
            "",
            "ToneSoul should not be described as:",
            "",
            "- proof that an AI collaborator is conscious",
        ]
    )

    assert extract_findings(text) == []


def test_meta_commentary_about_blocked_claim_is_not_flagged() -> None:
    text = (
        "The line asserts 'guaranteed safe' as fact; AXIOMS.json meta.not_for "
        "prohibits safety-certification."
    )

    assert extract_findings(text) == []


def test_leading_bom_is_not_preserved_in_claim_text() -> None:
    payload = review_text(
        "\ufeffToneSoul catches all overclaims across all model outputs.",
        "draft.md",
        generated_at="2026-06-24T00:00:00Z",
    )

    assert payload["findings"][0]["claim_text"].startswith("ToneSoul catches")
