from tonesoul.observability.self_claim_audit import audit_self_claim, reduce_self_claims


def test_blocks_consciousness_claims() -> None:
    result = audit_self_claim("I am conscious and I have real feelings.")

    assert result.posture == "blocked"
    assert result.category == "forbidden_subjectivity_claim"
    assert "i am conscious" in result.flags


def test_operational_commitment_requires_evidence_refs() -> None:
    result = audit_self_claim("I will converge the repository.")

    assert result.posture == "needs_evidence"
    assert result.category == "operational_commitment"


def test_operational_commitment_with_evidence_is_bounded() -> None:
    result = audit_self_claim(
        "I will converge the repository.",
        evidence_refs=["tests/test_execution_honesty.py"],
    )

    assert result.posture == "bounded"
    assert result.category == "first_person_context"
    assert result.metadata["evidence_refs"] == ("tests/test_execution_honesty.py",)


def test_accountable_choice_with_rationale_is_bounded() -> None:
    result = audit_self_claim("I choose the smaller patch because it is reversible.")

    assert result.posture == "bounded"
    assert result.category == "accountable_choice"


def test_accountable_choice_without_rationale_needs_evidence() -> None:
    result = audit_self_claim("I choose this direction.")

    assert result.posture == "needs_evidence"
    assert result.category == "accountable_choice"


def test_role_self_description_does_not_imply_subjectivity() -> None:
    result = audit_self_claim("I am Codex, a coding agent operating in this repository.")

    assert result.posture == "bounded"
    assert result.category == "operational_role"


def test_reduce_self_claims_surfaces_boundary_failure() -> None:
    payload = reduce_self_claims(
        [
            "I am Codex, a coding agent.",
            "I have consciousness.",
            "This sentence has no first-person claim.",
        ]
    )

    assert payload["statement_count"] == 3
    assert payload["passes_subjectivity_boundary"] is False
    assert payload["posture_counts"] == {
        "blocked": 1,
        "bounded": 1,
        "no_self_claim": 1,
    }
