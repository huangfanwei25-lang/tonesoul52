"""Tests for responsibility-runtime deterministic intent validation."""

from __future__ import annotations

from tonesoul.responsibility_runtime import USES_LLM, IntentValidationResult, validate_intent


def _valid_write_payload() -> dict[str, object]:
    return {
        "intent": "memory.write.propose",
        "claim": "使用者偏好繁體中文與誠實優先",
        "evidence_refs": ["turn_2026_06_27_001"],
        "requested_scope": "long_term_memory",
        "risk": "low",
        "uncertainty": "low",
        "audit_reason": "preference stated in project instructions",
    }


def _issue_fields(result: IntentValidationResult) -> set[str]:
    return {issue.field for issue in result.issues}


def _issue_codes(result: IntentValidationResult) -> set[str]:
    return {issue.code for issue in result.issues}


def test_validator_contract_is_deterministic_no_llm() -> None:
    assert USES_LLM is False

    result = validate_intent(_valid_write_payload())

    assert result.accepted is True
    assert result.issues == ()
    assert result.normalized_payload is not None
    assert result.normalized_payload["intent"] == "memory.write.propose"


def test_memory_write_missing_evidence_refs_fails_closed() -> None:
    payload = _valid_write_payload()
    del payload["evidence_refs"]

    result = validate_intent(payload)

    assert result.accepted is False
    assert "missing_required_field" in _issue_codes(result)
    assert "evidence_refs" in _issue_fields(result)


def test_memory_write_empty_evidence_refs_fails_closed() -> None:
    payload = _valid_write_payload()
    payload["evidence_refs"] = []

    result = validate_intent(payload)

    assert result.accepted is False
    assert "empty_required_field" in _issue_codes(result)
    assert "evidence_refs" in _issue_fields(result)


def test_memory_write_non_string_evidence_ref_fails_closed() -> None:
    payload = _valid_write_payload()
    payload["evidence_refs"] = [123]

    result = validate_intent(payload)

    assert result.accepted is False
    assert "malformed_intent" in _issue_codes(result)
    assert any(field.startswith("evidence_refs") for field in _issue_fields(result))


def test_missing_scope_fails_closed() -> None:
    payload = _valid_write_payload()
    del payload["requested_scope"]

    result = validate_intent(payload)

    assert result.accepted is False
    assert "missing_required_field" in _issue_codes(result)
    assert "requested_scope" in _issue_fields(result)


def test_scope_mismatch_fails_closed() -> None:
    result = validate_intent(
        _valid_write_payload(),
        allowed_scopes={"session_memory"},
    )

    assert result.accepted is False
    assert result.issues[0].code == "scope_not_allowed"
    assert result.issues[0].field == "requested_scope"


def test_malformed_non_object_payload_fails_closed() -> None:
    result = validate_intent(["memory.write.propose"])

    assert result.accepted is False
    assert result.issues[0].code == "malformed_intent"
    assert result.issues[0].field == "payload"


def test_unsupported_intent_fails_closed() -> None:
    payload = {
        "intent": "memory.write.direct",
        "claim": "直接寫入記憶",
        "evidence_refs": ["turn_2026_06_27_001"],
        "requested_scope": "long_term_memory",
    }

    result = validate_intent(payload)

    assert result.accepted is False
    assert result.issues[0].code == "unsupported_intent"
    assert result.issues[0].field == "intent"


def test_extra_fields_fail_closed() -> None:
    payload = _valid_write_payload()
    payload["direct_memory_write"] = True

    result = validate_intent(payload)

    assert result.accepted is False
    assert "malformed_intent" in _issue_codes(result)
    assert "direct_memory_write" in _issue_fields(result)


def test_phase_one_is_form_only_not_claim_evidence_oracle() -> None:
    payload = _valid_write_payload()
    payload["claim"] = "ToneSoul has already solved all AI responsibility."
    payload["evidence_refs"] = ["syntactically_valid_ref_only"]

    result = validate_intent(payload)

    assert result.accepted is True
    assert result.normalized_payload is not None
    assert result.normalized_payload["evidence_refs"] == ["syntactically_valid_ref_only"]


def test_memory_read_request_requires_scope_and_query() -> None:
    result = validate_intent(
        {
            "intent": "memory.read.request",
            "query": "使用者偏好",
            "requested_scope": "session_memory",
        }
    )

    assert result.accepted is True

    missing_query = validate_intent(
        {
            "intent": "memory.read.request",
            "requested_scope": "session_memory",
        }
    )

    assert missing_query.accepted is False
    assert "query" in _issue_fields(missing_query)
