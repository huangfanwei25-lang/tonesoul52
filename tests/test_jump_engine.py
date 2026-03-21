"""Tests for JUMP Engine — singularity detection & Seabed Lockdown."""

from __future__ import annotations

from tonesoul.action_set import ACTION_POLICY
from tonesoul.jump_monitor import JumpMonitor, LockdownStatus

# ---------------------------------------------------------------------------
# Action Set
# ---------------------------------------------------------------------------


def test_lockdown_action_set_matches_vol5_spec() -> None:
    """Seabed Lockdown allows verify, cite, inquire per Vol-5 §2."""
    assert sorted(ACTION_POLICY["lockdown"]) == ["cite", "inquire", "verify"]


# ---------------------------------------------------------------------------
# JumpMonitor basics
# ---------------------------------------------------------------------------


def test_initial_status_is_normal() -> None:
    m = JumpMonitor()
    assert m.status == LockdownStatus.NORMAL


def test_check_needs_at_least_two_records() -> None:
    m = JumpMonitor()
    m.record_output(tension_total=0.5)
    signal = m.check_singularity()
    assert signal.triggered is False


def test_no_trigger_under_normal_conditions() -> None:
    m = JumpMonitor(window_size=5)
    for i in range(5):
        m.record_output(
            tension_total=0.3 + i * 0.1,
            has_echo_trace=True,
            center_delta_norm=0.1,
            input_norm=1.0,
        )
    signal = m.check_singularity()
    assert signal.triggered is False
    assert m.status == LockdownStatus.NORMAL


# ---------------------------------------------------------------------------
# Singularity indicator: reasoning convergence
# ---------------------------------------------------------------------------


def test_convergence_trips_when_tension_stagnant() -> None:
    """When tension barely changes, ΔU/ΔInput → 0 (convergence)."""
    m = JumpMonitor(window_size=5, convergence_threshold=0.01)
    for _ in range(5):
        m.record_output(tension_total=0.5)  # identical tension each time
    signal = m.check_singularity()
    assert signal.reasoning_convergence < 0.01


# ---------------------------------------------------------------------------
# Singularity indicator: chain integrity
# ---------------------------------------------------------------------------


def test_chain_integrity_trips_when_traces_missing() -> None:
    m = JumpMonitor(window_size=5, chain_threshold=0.5)
    for _ in range(5):
        m.record_output(has_echo_trace=False)
    signal = m.check_singularity()
    assert signal.chain_integrity == 0.0


# ---------------------------------------------------------------------------
# Singularity indicator: self-reference ratio
# ---------------------------------------------------------------------------


def test_self_reference_trips_when_high() -> None:
    m = JumpMonitor(window_size=5, self_ref_threshold=0.5)
    for _ in range(5):
        m.record_output(center_delta_norm=0.9, input_norm=1.0)
    signal = m.check_singularity()
    assert signal.self_reference_ratio > 0.5


# ---------------------------------------------------------------------------
# JUMP trigger (multiple indicators)
# ---------------------------------------------------------------------------


def test_jump_triggers_with_two_indicators() -> None:
    """JUMP trips when ≥2 of 3 indicators exceed thresholds."""
    m = JumpMonitor(
        window_size=5,
        convergence_threshold=0.01,
        chain_threshold=0.5,
        self_ref_threshold=0.5,
        min_indicators=2,
    )
    for _ in range(5):
        m.record_output(
            tension_total=0.5,  # constant → convergence trips
            has_echo_trace=False,  # missing → chain integrity trips
            center_delta_norm=0.1,  # low → self-ref does NOT trip
            input_norm=1.0,
        )
    signal = m.check_singularity()
    assert signal.triggered is True
    assert signal.indicators_tripped >= 2
    assert m.status == LockdownStatus.LOCKDOWN


def test_jump_does_not_trigger_with_only_one_indicator() -> None:
    m = JumpMonitor(
        window_size=5,
        convergence_threshold=0.01,
        chain_threshold=0.5,
        self_ref_threshold=0.5,
        min_indicators=2,
    )
    for _ in range(5):
        m.record_output(
            tension_total=0.5,  # constant → convergence trips
            has_echo_trace=True,  # OK
            center_delta_norm=0.1,  # OK
            input_norm=1.0,
        )
    signal = m.check_singularity()
    assert signal.triggered is False


# ---------------------------------------------------------------------------
# Seabed Lockdown: enter / exit
# ---------------------------------------------------------------------------


def test_exit_lockdown() -> None:
    m = JumpMonitor(window_size=3, min_indicators=1, convergence_threshold=999)
    # Force lockdown via all-false traces
    for _ in range(3):
        m.record_output(has_echo_trace=False)
    m.check_singularity()
    assert m.status == LockdownStatus.LOCKDOWN

    assert m.exit_lockdown() is True
    assert m.status == LockdownStatus.NORMAL


def test_exit_lockdown_when_not_locked_returns_false() -> None:
    m = JumpMonitor()
    assert m.exit_lockdown() is False


def test_to_dict_reflects_lockdown() -> None:
    m = JumpMonitor(window_size=3, min_indicators=1, convergence_threshold=999)
    for _ in range(3):
        m.record_output(has_echo_trace=False)
    m.check_singularity()
    d = m.to_dict()
    assert d["status"] == "lockdown"
    assert d["lockdown_at"] is not None


# ---------------------------------------------------------------------------
# GovernanceKernel integration
# ---------------------------------------------------------------------------


def test_governance_kernel_check_jump_trigger() -> None:
    from tonesoul.governance.kernel import GovernanceKernel

    k = GovernanceKernel()
    # Feed normal data — should not trigger
    for _ in range(5):
        result = k.check_jump_trigger(tension_total=0.3 + _ * 0.05)
    assert result["triggered"] is False
    assert result["status"] == "normal"


def test_governance_kernel_jump_triggers_on_convergence_and_chain() -> None:
    from tonesoul.governance.kernel import GovernanceKernel

    k = GovernanceKernel()
    for _ in range(10):
        result = k.check_jump_trigger(
            tension_total=0.5,  # constant
            has_echo_trace=False,  # missing
        )
    assert result["triggered"] is True
    assert result["status"] == "lockdown"
