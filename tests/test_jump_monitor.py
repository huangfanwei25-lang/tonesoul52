from __future__ import annotations

from tonesoul.jump_monitor import JumpMonitor, LockdownStatus


def test_record_output_clamps_zero_input_norm() -> None:
    monitor = JumpMonitor()
    monitor.record_output(center_delta_norm=1.0, input_norm=0.0)

    assert monitor._window[-1].input_norm == 1e-12


def test_measure_reasoning_convergence_returns_mean_delta() -> None:
    monitor = JumpMonitor()
    for value in (0.2, 0.4, 0.5):
        monitor.record_output(tension_total=value)

    assert monitor._measure_reasoning_convergence() == 0.15


def test_measure_chain_integrity_returns_completion_ratio() -> None:
    monitor = JumpMonitor()
    monitor.record_output(has_echo_trace=True)
    monitor.record_output(has_echo_trace=False)
    monitor.record_output(has_echo_trace=True)

    assert monitor._measure_chain_integrity() == 2 / 3


def test_measure_self_reference_ratio_averages_window() -> None:
    monitor = JumpMonitor()
    monitor.record_output(center_delta_norm=0.5, input_norm=1.0)
    monitor.record_output(center_delta_norm=1.0, input_norm=1.0)
    monitor.record_output(center_delta_norm=0.0, input_norm=1.0)

    assert monitor._measure_self_reference_ratio() == 0.5


def test_check_singularity_reason_lists_multiple_tripped_indicators() -> None:
    monitor = JumpMonitor(
        convergence_threshold=0.01,
        chain_threshold=0.5,
        self_ref_threshold=0.5,
        min_indicators=3,
    )
    for _ in range(3):
        monitor.record_output(
            tension_total=0.5,
            has_echo_trace=False,
            center_delta_norm=0.8,
            input_norm=1.0,
        )

    signal = monitor.check_singularity()

    assert signal.triggered is True
    assert signal.indicators_tripped == 3
    assert "reasoning_convergence=" in signal.reason
    assert "chain_integrity=" in signal.reason
    assert "self_reference_ratio=" in signal.reason


def test_check_singularity_respects_higher_min_indicator_threshold() -> None:
    monitor = JumpMonitor(
        convergence_threshold=0.01,
        chain_threshold=0.5,
        self_ref_threshold=2.0,
        min_indicators=3,
    )
    for _ in range(3):
        monitor.record_output(tension_total=0.5, has_echo_trace=False, center_delta_norm=0.1)

    signal = monitor.check_singularity()

    assert signal.triggered is False
    assert signal.indicators_tripped == 2
    assert monitor.status == LockdownStatus.NORMAL


def test_to_dict_reports_normal_state_without_lockdown() -> None:
    monitor = JumpMonitor()
    monitor.record_output(tension_total=0.3)

    assert monitor.to_dict() == {
        "status": "normal",
        "lockdown_reason": "",
        "lockdown_at": None,
        "window_size": 1,
    }


def test_exit_lockdown_clears_window_after_trigger() -> None:
    monitor = JumpMonitor(min_indicators=1, chain_threshold=1.0)
    monitor.record_output(has_echo_trace=False)
    monitor.record_output(has_echo_trace=False)
    monitor.check_singularity()

    assert monitor.status == LockdownStatus.LOCKDOWN
    assert monitor.exit_lockdown() is True
    assert monitor.to_dict()["window_size"] == 0
    assert monitor.lockdown_reason == ""
