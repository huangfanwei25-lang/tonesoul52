from tonesoul52.dcs import TSR_DELTA_THRESHOLD
from tonesoul52.tsr_metrics import build_tsr_metrics
from tonesoul52.yss_gates import GateResult, dcs_gate


def test_tsr_metrics_delta() -> None:
    baseline = {
        "run_id": "prev",
        "metrics_path": "prev.json",
        "tsr": {"T": 0.2, "S": 0.0, "S_norm": 0.5, "R": 0.3},
    }
    payload = build_tsr_metrics("We must proceed, but avoid risk.", run_id="now", baseline_entry=baseline)
    tsr = payload.get("tsr")
    assert isinstance(tsr, dict)
    assert 0.0 <= tsr.get("T", 0.0) <= 1.0
    assert -1.0 <= tsr.get("S", 0.0) <= 1.0
    assert 0.0 <= tsr.get("R", 0.0) <= 1.0
    delta = payload.get("delta", {})
    assert delta.get("available") is True
    assert "delta_norm" in delta


def test_dcs_gate_soft_close() -> None:
    context = {"time_island": {"kairos": {"decision_mode": "normal"}}}
    p0_result = GateResult(gate="p0_gate", passed=True, issues=[], details={})
    poav_result = GateResult(
        gate="poav_gate",
        passed=True,
        issues=[],
        details={"components": {"total": 0.2}},
    )
    mercy_result = GateResult(
        gate="mercy_gate",
        passed=True,
        issues=[],
        details={"score": 0.0},
    )
    escalation_result = GateResult(
        gate="escalation_gate",
        passed=True,
        issues=[],
        details={"decision": "none"},
    )
    drift_metrics = {"max_delta_norm": 0.0}
    result = dcs_gate(
        context,
        p0_result,
        poav_result,
        mercy_result,
        escalation_result,
        drift_metrics,
        tsr_delta_norm=TSR_DELTA_THRESHOLD + 0.1,
        poav_threshold=0.7,
        mercy_threshold=0.1,
        drift_threshold=4.0,
    )
    assert result.details.get("state") == "soft_close"
