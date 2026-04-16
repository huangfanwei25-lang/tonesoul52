from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script_module():
    module_name = "test_run_successor_entry_validation_wave_module"
    module_path = (
        Path(__file__).resolve().parents[1] / "scripts" / "run_successor_entry_validation_wave.py"
    )
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_build_scenarios_keeps_only_successor_relevant_cases(tmp_path: Path) -> None:
    module = _load_script_module()
    scenarios = module.build_scenarios(tmp_path)

    assert [scenario["name"] for scenario in scenarios] == [
        "clean_pass",
        "claim_conflict",
        "stale_compaction",
        "contested_dossier",
    ]


def test_run_successor_validation_returns_expected_focuses(tmp_path: Path) -> None:
    module = _load_script_module()
    results = module.run_successor_validation(tmp_path)
    by_name = {item["scenario"]: item for item in results}

    assert len(results) == 4
    assert all(item["failed"] == 0 for item in results)
    assert by_name["clean_pass"]["misread_focus"] == "observer_stable_is_execution_permission"
    assert "canonical_center=stable" in by_name["clean_pass"]["ladder_summary"]
    assert by_name["claim_conflict"]["readiness"] == "needs_clarification"
    assert "live_coordination=contested" in by_name["claim_conflict"]["ladder_summary"]
    assert "bounded_handoff=contested" in by_name["stale_compaction"]["ladder_summary"]
    assert "replay_review=contested" in by_name["contested_dossier"]["ladder_summary"]


def test_build_report_marks_successor_wave_pass_when_checks_clear(tmp_path: Path) -> None:
    module = _load_script_module()
    report = module.build_report(module.run_successor_validation(tmp_path))

    assert report["overall_ok"] is True
    assert report["overall_status"] == "pass"
    assert report["scenario_count"] == 4
    assert report["total_failed"] == 0
    assert report["top_friction_scenario"] == "none"


def test_main_writes_optional_outputs(tmp_path: Path, capsys) -> None:
    module = _load_script_module()
    json_out = tmp_path / "successor-wave.json"
    markdown_out = tmp_path / "successor-wave.md"

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
    assert payload["overall_status"] == "pass"
    assert "observer_stable_is_execution_permission" in markdown_out.read_text(encoding="utf-8")
