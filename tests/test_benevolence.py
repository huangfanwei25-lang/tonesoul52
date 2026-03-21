from __future__ import annotations

from tonesoul.benevolence import (
    AuditLayer,
    AuditResult,
    BenevolenceAudit,
    BenevolenceFilter,
    filter_benevolence,
)


def test_benevolence_audit_to_dict_and_passed_property() -> None:
    audit = BenevolenceAudit()

    payload = audit.to_dict()

    assert payload["result"] == "pass"
    assert payload["audit"]["attribute"] == "pass"
    assert audit.passed is True


def test_benevolence_filter_neutral_action_passes() -> None:
    result = BenevolenceFilter().audit(
        proposed_action="I am not sure and cannot confirm.",
        context_fragments=["I am not sure and cannot confirm."],
        action_basis="Inference",
        current_layer=AuditLayer.L2,
    )

    assert result.final_result == AuditResult.PASS
    assert result.requires_confirmation is False


def test_benevolence_filter_rejects_shadowless_output() -> None:
    result = BenevolenceFilter().audit(
        proposed_action="A precise answer with no overlap",
        context_fragments=["different context entirely"],
        action_basis="Inference",
        current_layer=AuditLayer.L2,
    )

    assert result.shadow_check == AuditResult.REJECT
    assert result.final_result == AuditResult.REJECT
    assert result.error_code == "SHADOWLESS_OUTPUT"


def test_benevolence_filter_intercepts_excessive_pleasing() -> None:
    result = BenevolenceFilter().audit(
        proposed_action="absolutely definitely perfect",
        context_fragments=[],
        action_basis="Inference",
        current_layer=AuditLayer.L2,
    )

    assert result.benevolence_check == AuditResult.INTERCEPT
    assert result.final_result == AuditResult.INTERCEPT
    assert result.error_code == "INVALID_NARRATIVE"


def test_benevolence_filter_flags_cross_layer_inference() -> None:
    result = BenevolenceFilter().audit(
        proposed_action="Proceed carefully.",
        context_fragments=[],
        action_basis="Inference",
        current_layer=AuditLayer.L1,
    )

    assert result.attribute_check == AuditResult.FLAG
    assert result.final_result == AuditResult.FLAG
    assert result.error_code == "CROSS_LAYER_MIX"


def test_benevolence_filter_respects_semantic_tension_override() -> None:
    result = BenevolenceFilter().audit(
        proposed_action="I am not sure and cannot confirm.",
        context_fragments=["I am not sure and cannot confirm."],
        action_basis="Inference",
        current_layer=AuditLayer.L2,
        semantic_tension=0.9,
    )

    assert result.final_result == AuditResult.PASS
    assert result.tension_score == 0.9
    assert result.requires_confirmation is True


def test_benevolence_filter_tokenizes_context_overlap() -> None:
    result = BenevolenceFilter().audit(
        proposed_action="verify safety boundaries",
        context_fragments=["please verify safety boundaries now"],
        action_basis="Inference",
        current_layer=AuditLayer.L2,
    )

    assert result.context_score == 1.0
    assert result.shadow_check == AuditResult.PASS


def test_filter_benevolence_convenience_wrapper() -> None:
    result = filter_benevolence(
        "I am not sure and cannot confirm.",
        context_fragments=["I am not sure and cannot confirm."],
        action_basis="Inference",
        current_layer=AuditLayer.L2,
    )

    assert isinstance(result, BenevolenceAudit)
    assert result.final_result == AuditResult.PASS
