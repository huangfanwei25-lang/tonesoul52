import os
import shutil
import uuid
from pathlib import Path

from tonesoul52.yss_gates import escalation_gate, poav_gate, tech_trace_gate


_BASE_TEMP = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "temp"))
os.makedirs(_BASE_TEMP, exist_ok=True)


def _make_temp_dir() -> Path:
    path = Path(_BASE_TEMP) / f"manual_{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=False)
    return path


def test_poav_gate_empty_string() -> None:
    result = poav_gate("", threshold=0.7, enforce=False)
    assert result.passed is True
    assert "poav_text_empty" in result.issues


def test_poav_gate_whitespace_only() -> None:
    result = poav_gate("   \n\t", threshold=0.7, enforce=False)
    assert result.passed is True
    assert "poav_text_empty" in result.issues


def test_escalation_gate_missing_poav() -> None:
    context = {"time_island": {"kairos": {"decision_mode": "normal"}}}
    drift_metrics = {
        "max_delta_norm": None,
        "avg_delta_norm": None,
        "count": 0,
        "available": False,
    }
    result = escalation_gate(context, None, drift_metrics)
    assert result.passed is True
    assert result.details.get("decision") == "none"


def test_tech_trace_gate_invalid_json() -> None:
    temp_dir = _make_temp_dir()
    try:
        bad_path = temp_dir / "bad.json"
        bad_path.write_text("{not: json", encoding="utf-8")
        result = tech_trace_gate(str(bad_path), require=True)
        assert result.passed is False
        assert any(issue.startswith("tech_trace_load_failed") for issue in result.issues)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
