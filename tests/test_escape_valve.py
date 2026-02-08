"""Tests for the Escape Valve circuit breaker."""

from tonesoul.escape_valve import (
    EscapeReason,
    EscapeValve,
    EscapeValveConfig,
    EscapeValveResult,
)


class TestEscapeValveConfig:
    """Tests for EscapeValveConfig defaults."""

    def test_default_values(self):
        config = EscapeValveConfig()
        assert config.max_retries == 3
        assert config.circuit_breaker_threshold == 5
        assert config.uncertainty_allowed is True
        assert config.same_failure_threshold == 2


class TestEscapeValveResult:
    """Tests for EscapeValveResult."""

    def test_to_dict(self):
        result = EscapeValveResult(
            triggered=True,
            reason=EscapeReason.MAX_RETRIES_EXCEEDED,
            retry_count=3,
            failure_history=["fail1", "fail2", "fail3"],
            final_output="test output",
            uncertainty_tag=True,
        )
        payload = result.to_dict()
        assert payload["triggered"] is True
        assert payload["reason"] == "max_retries_exceeded"
        assert payload["retry_count"] == 3
        assert payload["uncertainty_tag"] is True


class TestEscapeValve:
    """Tests for the EscapeValve circuit breaker."""

    def test_no_escape_on_first_failure(self):
        valve = EscapeValve()
        valve.record_failure("first fail")
        result = valve.evaluate()
        assert result.triggered is False
        assert result.retry_count == 1

    def test_escape_on_max_retries(self):
        valve = EscapeValve(EscapeValveConfig(max_retries=3))
        valve.record_failure("fail1")
        valve.record_failure("fail2")
        valve.record_failure("fail3")
        result = valve.evaluate("proposed output")
        assert result.triggered is True
        assert result.reason == EscapeReason.MAX_RETRIES_EXCEEDED
        assert result.uncertainty_tag is True
        assert "[UNCERTAINTY]" in (result.final_output or "")

    def test_escape_on_same_failure_repeated(self):
        valve = EscapeValve(EscapeValveConfig(same_failure_threshold=2))
        valve.record_failure("same_error")
        valve.record_failure("same_error")
        result = valve.evaluate()
        assert result.triggered is True
        assert result.reason == EscapeReason.SAME_FAILURE_REPEATED

    def test_no_escape_on_different_failures(self):
        valve = EscapeValve(EscapeValveConfig(same_failure_threshold=2, max_retries=5))
        valve.record_failure("error_a")
        valve.record_failure("error_b")
        result = valve.evaluate()
        assert result.triggered is False

    def test_circuit_breaker_opens(self):
        valve = EscapeValve(EscapeValveConfig(circuit_breaker_threshold=3))
        valve.record_failure("fail1")
        valve.record_failure("fail2")
        valve.record_failure("fail3")
        assert valve.is_circuit_open is True
        result = valve.evaluate()
        assert result.triggered is True
        assert result.reason == EscapeReason.CIRCUIT_BREAKER_OPEN

    def test_reset_clears_history(self):
        valve = EscapeValve()
        valve.record_failure("fail")
        valve.record_failure("fail")
        valve.reset()
        assert valve.failure_count == 0
        result = valve.evaluate()
        assert result.triggered is False

    def test_record_success_resets_consecutive_failures(self):
        valve = EscapeValve(EscapeValveConfig(circuit_breaker_threshold=3))
        valve.record_failure("fail1")
        valve.record_failure("fail2")
        valve.record_success()
        assert valve.is_circuit_open is False
        valve.record_failure("fail3")
        assert valve.is_circuit_open is False

    def test_uncertainty_output_format(self):
        valve = EscapeValve()
        valve.record_failure("benevolence_intercept: invalid narrative")
        valve.record_failure("benevolence_intercept: invalid narrative")
        valve.record_failure("benevolence_intercept: invalid narrative")
        result = valve.evaluate("Original output text")
        assert "[UNCERTAINTY]" in (result.final_output or "")
        assert "Escape valve reason:" in (result.final_output or "")
        assert "Total failures: 3" in (result.final_output or "")

    def test_blocked_output_when_uncertainty_not_allowed(self):
        config = EscapeValveConfig(max_retries=1, uncertainty_allowed=False)
        valve = EscapeValve(config)
        valve.record_failure("fail")
        result = valve.evaluate()
        assert result.triggered is True
        assert "[BLOCKED]" in (result.final_output or "")
