from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script_module():
    module_name = "test_run_launch_continuity_validation_wave_module"
    module_path = (
        Path(__file__).resolve().parents[1] / "scripts" / "run_launch_continuity_validation_wave.py"
    )
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_build_scenarios_writes_expected_fixture_files(tmp_path: Path) -> None:
    module = _load_script_module()
    scenarios = module.build_scenarios(tmp_path)

    assert [scenario["name"] for scenario in scenarios] == [
        "clean_pass",
        "claim_conflict",
        "stale_compaction",
        "contested_dossier",
        "session_end_lifecycle",
        "concurrent_claims",
        "working_style_reinforced",
    ]
    for scenario in scenarios:
        assert scenario["state_path"].exists()
        assert scenario["traces_path"].exists()


def test_run_validation_wave_returns_expected_summaries(tmp_path: Path) -> None:
    module = _load_script_module()
    results = module.run_validation_wave(tmp_path)
    by_name = {item["scenario"]: item for item in results}

    assert by_name["clean_pass"]["readiness"] == "pass"
    assert by_name["clean_pass"]["receiver_alert_count"] == 2
    assert by_name["claim_conflict"]["readiness"] == "needs_clarification"
    assert by_name["claim_conflict"]["receiver_alert_count"] == 2
    assert by_name["stale_compaction"]["compaction_receiver_obligation"] == "must_not_promote"
    assert by_name["stale_compaction"]["receiver_alert_count"] == 6
    assert all(
        "Evidence readout is a bounded honesty shortcut" not in alert
        for alert in by_name["stale_compaction"]["receiver_alerts"]
    )
    assert by_name["contested_dossier"]["council_calibration_status"] == "descriptive_only"
    assert by_name["contested_dossier"]["council_suppression_flag"] is True
    assert by_name["contested_dossier"]["receiver_alert_count"] == 6
    assert (
        "Latest council dossier confidence is descriptive_only"
        in by_name["contested_dossier"]["receiver_alerts"][0]
    )
    assert (
        "Latest council dossier carries minority dissent"
        in by_name["contested_dossier"]["receiver_alerts"][1]
    )
    assert (
        "Latest council dossier indicates potential evolution suppression"
        in by_name["contested_dossier"]["receiver_alerts"][2]
    )
    assert by_name["session_end_lifecycle"]["readiness"] == "pass"
    assert by_name["concurrent_claims"]["readiness"] == "needs_clarification"
    assert by_name["working_style_reinforced"]["working_style_validation"] == "sufficient"
    assert by_name["working_style_reinforced"]["receiver_alert_count"] == 5


def test_render_markdown_contains_key_columns(tmp_path: Path) -> None:
    module = _load_script_module()
    results = module.run_validation_wave(tmp_path)
    markdown = module.render_markdown(results)

    assert (
        "| Scenario | Readiness | Track | Mode | Style | Compaction posture | Council | Alerts |"
        in markdown
    )
    assert "clean_pass" in markdown
    assert "contested_dossier" in markdown


def test_main_writes_optional_outputs(tmp_path: Path, capsys) -> None:
    module = _load_script_module()
    json_out = tmp_path / "wave.json"
    markdown_out = tmp_path / "wave.md"

    module.main(
        [
            "--workspace",
            str(tmp_path / "workspace"),
            "--json-out",
            str(json_out),
            "--markdown-out",
            str(markdown_out),
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert json_out.exists()
    assert markdown_out.exists()
    assert len(payload) == 7
