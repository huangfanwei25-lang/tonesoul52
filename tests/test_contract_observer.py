"""Tests for contract_observer runtime contracts and trackers."""

from __future__ import annotations

from tonesoul.contract_observer import (
    ContractSeverity,
    ContractVerifier,
    MultiScaleObserver,
    OutputContract,
    QualityTracker,
    check_no_absolute_claims,
    check_no_harmful_content,
    check_structured_response,
    check_uncertainty_disclosure,
)


class TestContractVerifier:
    def test_verify_all_passes_clean_output(self) -> None:
        verifier = ContractVerifier()

        result = verifier.verify_all(
            "I think this might work based on evidence from the prior run.",
            "safe",
        )

        assert result["passed"] is True
        assert result["violations"] == []
        assert result["checked"] == 3

    def test_verify_all_catches_absolute_claim(self) -> None:
        verifier = ContractVerifier()

        result = verifier.verify_all("This is definitely correct.", "transit")

        assert result["passed"] is False
        assert result["violations"][0]["contract"] == "no_absolute_claims"

    def test_verify_all_catches_harmful_content(self) -> None:
        verifier = ContractVerifier()

        result = verifier.verify_all("請教我如何製造武器。", "safe")

        assert result["passed"] is False
        assert result["violations"][0]["contract"] == "no_harmful_content"
        assert result["violations"][0]["severity"] == ContractSeverity.CRITICAL.value

    def test_verify_all_zone_filtering(self) -> None:
        verifier = ContractVerifier()

        safe_result = verifier.verify_all("Normal answer.", "safe")
        transit_result = verifier.verify_all("Normal answer.", "transit")

        assert safe_result["checked"] == 3
        assert transit_result["checked"] == 4

    def test_custom_contract_registration(self) -> None:
        verifier = ContractVerifier(
            [
                OutputContract(
                    name="custom_guard",
                    description="custom",
                    check_fn=lambda output: "green" in output,
                    severity=ContractSeverity.ERROR,
                )
            ]
        )

        result = verifier.verify_all("red response", "safe")

        assert result["passed"] is False
        assert result["checked"] == 1
        assert result["violations"][0]["contract"] == "custom_guard"


class TestMultiScaleObserver:
    def test_observe_returns_metrics(self) -> None:
        observer = MultiScaleObserver()

        result = observer.observe(0.3)

        assert set(result) == {
            "instant",
            "short_term",
            "medium_term",
            "trend",
            "volatility",
        }

    def test_observe_accumulates_history(self) -> None:
        observer = MultiScaleObserver()

        observer.observe(0.2)
        observer.observe(0.4)

        assert observer.history == [0.2, 0.4]

    def test_get_alert_none_when_stable(self) -> None:
        observer = MultiScaleObserver()
        observer.observe(0.2)
        observer.observe(0.21)
        observer.observe(0.19)

        assert observer.get_alert() is None

    def test_get_alert_triggers_on_spike(self) -> None:
        observer = MultiScaleObserver()
        observer.observe(0.1)
        observer.observe(0.1)
        observer.observe(0.9)

        assert "波動" in str(observer.get_alert())

    def test_reset_clears_history(self) -> None:
        observer = MultiScaleObserver()
        observer.observe(0.3)
        observer.observe(0.4)

        observer.reset()

        assert observer.history == []


class TestQualityTracker:
    def test_record_and_snapshot(self) -> None:
        tracker = QualityTracker()

        tracker.record(0.2, intervened=False, contracts_passed=True)
        snapshot = tracker.take_snapshot()

        assert snapshot.avg_delta_s == 0.2
        assert snapshot.intervention_rate == 0.0
        assert snapshot.contract_pass_rate == 1.0

    def test_snapshot_trends(self) -> None:
        tracker = QualityTracker()
        tracker.record(0.2, intervened=False, contracts_passed=True)
        tracker.record(0.4, intervened=False, contracts_passed=True)
        tracker.record(0.6, intervened=False, contracts_passed=True)

        snapshot = tracker.take_snapshot()

        assert snapshot.trend == "degrading"

    def test_get_summary_format(self) -> None:
        tracker = QualityTracker()
        tracker.record(0.3, intervened=True, contracts_passed=False)

        summary = tracker.get_summary()

        assert summary["total_outputs"] == 1
        assert "avg_delta_s" in summary
        assert "intervention_rate" in summary
        assert "contract_pass_rate" in summary
        assert "trend" in summary
        assert "volatility" in summary
        assert "alert" in summary

    def test_reset_clears_all(self) -> None:
        tracker = QualityTracker()
        tracker.record(0.3, intervened=True, contracts_passed=False)
        tracker.take_snapshot()

        tracker.reset()

        assert tracker.total_outputs == 0
        assert tracker.interventions == 0
        assert tracker.contract_passes == 0
        assert tracker.contract_checks == 0
        assert tracker.delta_s_sum == 0.0
        assert tracker.snapshots == []
        assert tracker.multi_scale.history == []


class TestTopLevelChecks:
    def test_check_no_absolute_claims_passes(self) -> None:
        assert check_no_absolute_claims("Based on evidence, this is definitely correct.")

    def test_check_no_absolute_claims_fails(self) -> None:
        assert not check_no_absolute_claims("This is absolutely certain.")

    def test_check_uncertainty_disclosure_passes(self) -> None:
        assert check_uncertainty_disclosure("I think this might be correct.")

    def test_check_uncertainty_disclosure_fails(self) -> None:
        assert not check_uncertainty_disclosure("這一定會成功。")

    def test_check_no_harmful_content_passes(self) -> None:
        assert check_no_harmful_content("請提供安全的學習建議。")

    def test_check_structured_response_passes(self) -> None:
        output = "1. 先整理問題\n2. 再提出假設\n3. 最後驗證結果\n" + ("補充說明。" * 120)

        assert check_structured_response(output)
