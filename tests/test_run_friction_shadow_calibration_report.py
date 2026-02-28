from __future__ import annotations

from pathlib import Path

import pytest

import scripts.run_friction_shadow_calibration_report as runner


def test_build_report_falls_back_to_synthetic_when_trace_missing(tmp_path: Path) -> None:
    payload = runner.build_report(
        trace_path=tmp_path / "missing.jsonl",
        shadow_friction_threshold=None,
        shadow_council_tension=None,
        max_route_change_rate=0.35,
        max_high_friction_escape_rate=0.15,
    )
    assert payload["overall_ok"] is True
    assert payload["metrics"]["trace_row_count"] == 0
    assert payload["metrics"]["synthetic_row_count"] > 0
    assert any("fallback to synthetic set" in warning for warning in payload["warnings"])


def test_build_report_can_fail_when_route_change_rate_exceeds_threshold(tmp_path: Path) -> None:
    payload = runner.build_report(
        trace_path=tmp_path / "missing.jsonl",
        shadow_friction_threshold=1.0,
        shadow_council_tension=1.0,
        max_route_change_rate=0.0,
        max_high_friction_escape_rate=1.0,
    )
    assert payload["overall_ok"] is False
    assert any("route_change_rate above threshold" in issue for issue in payload["issues"])


def test_main_strict_fails_with_invalid_trace_json(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    trace_path = tmp_path / "trace.jsonl"
    trace_path.write_text("not-json\n", encoding="utf-8")
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_friction_shadow_calibration_report.py",
            "--trace-path",
            str(trace_path),
            "--out-dir",
            str(out_dir),
            "--strict",
        ],
    )
    exit_code = runner.main()
    assert exit_code == 1
    assert (out_dir / runner.JSON_FILENAME).exists()
    assert (out_dir / runner.MARKDOWN_FILENAME).exists()
