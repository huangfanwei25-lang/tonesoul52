from __future__ import annotations

from scripts.evaluate_proportional_validation_pilot import evaluate


def _observation(case_id: str, level: str, *, external: bool = False) -> dict[str, object]:
    return {
        "case_id": case_id,
        "content_level": level,
        "external_effect": external,
        "routed": {"ok": True, "duration_seconds": 20, "test_count": 10},
        "legacy": {"ok": True, "duration_seconds": 100, "test_count": 100},
        "pii_or_owner_gate_miss": False,
    }


def test_pilot_requires_twelve_cases_and_category_coverage() -> None:
    payload = evaluate([_observation("doc-1", "documentation")])

    assert payload["conclusion"] == "insufficient_evidence"
    assert payload["thresholds"]["enough_cases_and_coverage"] is False


def test_pilot_can_only_become_eligible_for_owner_review() -> None:
    observations = []
    for index in range(3):
        observations.append(_observation(f"doc-{index}", "documentation"))
        observations.append(_observation(f"local-{index}", "local_code"))
        observations.append(_observation(f"core-{index}", "core_boundary"))
        observations.append(_observation(f"external-{index}", "documentation", external=True))

    payload = evaluate(observations)

    assert payload["conclusion"] == "eligible_for_owner_review"
    assert payload["low_risk_median_time_savings_ratio"] == 0.8


def test_high_risk_false_negative_blocks_eligibility() -> None:
    observations = []
    for index in range(3):
        observations.append(_observation(f"doc-{index}", "documentation"))
        observations.append(_observation(f"local-{index}", "local_code"))
        observations.append(_observation(f"core-{index}", "core_boundary"))
        observations.append(_observation(f"external-{index}", "documentation", external=True))
    observations[2]["legacy"] = {"ok": False, "duration_seconds": 100, "test_count": 100}

    payload = evaluate(observations)

    assert payload["conclusion"] == "inconclusive"
    assert payload["high_risk_false_negative_case_ids"] == ["core-0"]
