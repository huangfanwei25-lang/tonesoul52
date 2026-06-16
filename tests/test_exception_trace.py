"""Tests for lightweight suppressed-exception tracing."""

from __future__ import annotations

from tonesoul.exception_trace import ExceptionTrace


def test_empty_trace_summary() -> None:
    trace = ExceptionTrace()

    assert trace.summary() == {"suppressed_count": 0}


def test_record_adds_error() -> None:
    trace = ExceptionTrace()

    trace.record("component", "operation", RuntimeError("boom"))

    assert trace.count == 1


def test_summary_structure() -> None:
    trace = ExceptionTrace()
    trace.record("governance_kernel", "_try_ollama", RuntimeError("offline"))

    assert trace.summary() == {
        "suppressed_count": 1,
        "tiers": {"optional": 1},
        "errors": [
            {
                "component": "governance_kernel",
                "operation": "_try_ollama",
                "error_type": "RuntimeError",
                "message": "offline",
                "tier": "optional",
            }
        ],
    }


def test_default_tier_is_optional() -> None:
    trace = ExceptionTrace()
    trace.record("component", "operation", RuntimeError("boom"))

    assert trace.summary()["errors"][0]["tier"] == "optional"


def test_explicit_tiers_recorded_and_counted() -> None:
    trace = ExceptionTrace()
    trace.record("pipeline", "_get_optional_subsystem", RuntimeError("offline"))
    trace.record("telemetry_sink", "flush", RuntimeError("dropped"), tier="telemetry")
    trace.record("telemetry_sink", "flush", RuntimeError("dropped again"), tier="telemetry")

    summary = trace.summary()
    # telemetry is counted (not silenced); optional stays visible.
    assert summary["tiers"] == {"optional": 1, "telemetry": 2}
    assert {e["tier"] for e in summary["errors"]} == {"optional", "telemetry"}


def test_message_truncation() -> None:
    trace = ExceptionTrace()
    message = "x" * 240

    trace.record("component", "operation", RuntimeError(message))

    summary = trace.summary()
    assert len(summary["errors"][0]["message"]) == 200


def test_has_errors_flag() -> None:
    trace = ExceptionTrace()

    assert trace.has_errors is False

    trace.record("component", "operation", ValueError("bad input"))

    assert trace.has_errors is True
