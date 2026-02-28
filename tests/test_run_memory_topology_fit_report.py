from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.run_memory_topology_fit_report as runner


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_build_report_recommends_planar_with_high_governance_pressure() -> None:
    replay_payload = {"metrics": {"high_friction_scenario_rate": 0.9}}
    calibration_payload = {
        "metrics": {"high_friction_escape_rate": 0.25, "route_change_rate": 0.05}
    }
    reflection_payload = {
        "quality_signals": {"unresolved_topic_rate": 0.35, "identity_choice_index": 0.25}
    }

    payload = runner.build_report(
        replay_payload=replay_payload,
        calibration_payload=calibration_payload,
        reflection_payload=reflection_payload,
        profile="basic",
        max_vram_gb=12.0,
        max_latency_ms=3000,
        min_recommendation_score=0.45,
    )
    assert payload["overall_ok"] is True
    assert payload["recommendation"]["topology"] == "planar"
    assert payload["diagnostics"]["governance_need_score"] >= 0.62


def test_build_report_uses_defaults_when_sources_missing() -> None:
    payload = runner.build_report(
        replay_payload=None,
        calibration_payload=None,
        reflection_payload=None,
        profile="basic",
        max_vram_gb=8.0,
        max_latency_ms=2500,
        min_recommendation_score=0.45,
    )
    assert payload["overall_ok"] is True
    assert payload["recommendation"]["topology"] in {"flat", "planar", "hierarchical"}
    assert any("missing; using default" in warning for warning in payload["warnings"])


def test_main_writes_status_artifacts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _write_json(
        tmp_path / "docs" / "status" / "friction_shadow_replay_latest.json",
        {"metrics": {"high_friction_scenario_rate": 0.75}},
    )
    _write_json(
        tmp_path / "docs" / "status" / "friction_shadow_calibration_latest.json",
        {"metrics": {"high_friction_escape_rate": 0.03, "route_change_rate": 0.01}},
    )
    _write_json(
        tmp_path / "docs" / "status" / "philosophical_reflection_latest.json",
        {"quality_signals": {"unresolved_topic_rate": 0.08, "identity_choice_index": 0.82}},
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "run_memory_topology_fit_report.py",
            "--repo-root",
            str(tmp_path),
            "--out-dir",
            "docs/status",
            "--strict",
        ],
    )
    exit_code = runner.main()
    assert exit_code == 0
    assert (tmp_path / "docs" / "status" / runner.JSON_FILENAME).exists()
    assert (tmp_path / "docs" / "status" / runner.MARKDOWN_FILENAME).exists()
