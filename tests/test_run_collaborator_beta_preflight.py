from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script_module():
    module_name = "test_run_collaborator_beta_preflight_module"
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "run_collaborator_beta_preflight.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _sample_start_payload() -> dict:
    return {
        "readiness": {"status": "pass"},
        "task_track_hint": {"suggested_track": "feature_track"},
        "deliberation_mode_hint": {"suggested_mode": "standard_council"},
        "compact_diagnostic": "[ToneSoul] file | R=0.04/stable | readiness=pass",
    }


def _sample_packet_payload() -> dict:
    return {
        "project_memory_summary": {
            "launch_claim_posture": {
                "current_tier": "collaborator_beta",
                "next_target_tier": "public_launch",
                "public_launch_ready": False,
                "blocked_overclaims": [
                    {
                        "claim": "continuity_effectiveness",
                        "current_classification": "runtime_present",
                        "reason": "bounded only",
                    },
                    {
                        "claim": "council_decision_quality",
                        "current_classification": "descriptive_only",
                        "reason": "not calibrated",
                    },
                ],
                "summary_text": (
                    "launch_claims=current:collaborator_beta public_launch:deferred "
                    "blocked=continuity_effectiveness,council_decision_quality,live_shared_memory"
                ),
            },
            "evidence_readout_posture": {"summary_text": "evidence=tested(...)"},
        },
        "coordination_mode": {
            "launch_default_mode": "file-backed",
            "launch_alignment": "aligned_with_launch_default",
        },
    }


def test_run_preflight_reports_go(monkeypatch, tmp_path: Path) -> None:
    module = _load_script_module()
    validation_path = tmp_path / "wave.json"
    validation_path.write_text(
        json.dumps(
            [
                {
                    "scenario": "clean_pass",
                    "receiver_alert_count": 1,
                    "council_calibration_status": "absent",
                    "compaction_receiver_obligation": "should_consider",
                },
                {
                    "scenario": "stale_compaction",
                    "receiver_alert_count": 4,
                    "council_calibration_status": "absent",
                    "compaction_receiver_obligation": "must_not_promote",
                },
                {
                    "scenario": "contested_dossier",
                    "receiver_alert_count": 4,
                    "council_calibration_status": "descriptive_only",
                    "compaction_receiver_obligation": "should_consider",
                },
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    payloads = [_sample_start_payload(), _sample_packet_payload()]

    monkeypatch.setattr(module, "_run_json_command", lambda command: payloads.pop(0))
    monkeypatch.setattr(
        module,
        "_run_text_command",
        lambda command: "[ToneSoul] file | R=0.04/stable | agent=beta-preflight | readiness=pass",
    )

    result = module.run_preflight(agent="beta-preflight", validation_wave_path=validation_path)

    assert result["overall_ok"] is True
    assert result["overall_status"] == "go"
    assert result["entry_stack"]["packet"]["current_tier"] == "collaborator_beta"
    assert result["validation_wave"]["scenario_count"] == 3
    assert result["validation_wave"]["stale_compaction_guarded"] is True
    assert result["validation_wave"]["contested_dossier_visible"] is True
    assert result["blocking_findings"] == []
    assert "continuity_effectiveness" in result["cautions"]


def test_run_preflight_holds_when_launch_defaults_drift(monkeypatch, tmp_path: Path) -> None:
    module = _load_script_module()
    validation_path = tmp_path / "wave.json"
    validation_path.write_text("[]\n", encoding="utf-8")

    packet_payload = _sample_packet_payload()
    packet_payload["project_memory_summary"]["launch_claim_posture"]["current_tier"] = "internal_alpha"
    packet_payload["coordination_mode"]["launch_default_mode"] = "redis-live"

    payloads = [_sample_start_payload(), packet_payload]
    monkeypatch.setattr(module, "_run_json_command", lambda command: payloads.pop(0))
    monkeypatch.setattr(module, "_run_text_command", lambda command: "compact")

    result = module.run_preflight(agent="beta-preflight", validation_wave_path=validation_path)

    assert result["overall_ok"] is False
    assert result["overall_status"] == "hold"
    assert "launch_claim_posture.current_tier is not collaborator_beta" in result["blocking_findings"]
    assert "launch_default_mode is not file-backed" in result["blocking_findings"]
    assert "launch_continuity_validation_wave artifact is missing" in result["blocking_findings"]


def test_render_markdown_contains_core_sections() -> None:
    module = _load_script_module()
    markdown = module.render_markdown(
        {
            "generated_at": "2026-03-30T00:00:00Z",
            "overall_status": "go",
            "entry_stack": {
                "session_start": {
                    "readiness": "pass",
                    "task_track": "feature_track",
                    "deliberation_mode": "standard_council",
                },
                "packet": {
                    "current_tier": "collaborator_beta",
                    "next_target_tier": "public_launch",
                    "launch_default_mode": "file-backed",
                },
                "diagnose": {
                    "ok": True,
                    "compact_line": "[ToneSoul] file | R=0.04/stable",
                },
            },
            "validation_wave": {
                "scenario_count": 4,
                "max_receiver_alert_count": 4,
                "contested_dossier_visible": True,
                "stale_compaction_guarded": True,
            },
            "launch_claim_posture": {
                "summary_text": "launch_claims=current:collaborator_beta public_launch:deferred",
                "blocked_overclaims": [
                    {"claim": "continuity_effectiveness", "current_classification": "runtime_present"}
                ],
            },
            "blocking_findings": [],
        }
    )

    assert "# ToneSoul Collaborator-Beta Preflight" in markdown
    assert "| session-start | ok | readiness=pass track=feature_track mode=standard_council |" in markdown
    assert "- Scenario count: `4`" in markdown
    assert "- `continuity_effectiveness` = `runtime_present`" in markdown


def test_parse_json_stdout_tolerates_storage_banner() -> None:
    module = _load_script_module()

    payload = module._parse_json_stdout(  # noqa: SLF001
        '[ToneSoul] Storage: FileStore (Redis not available)\n{"ok": true, "tier": "collaborator_beta"}\n',
        command=["python", "scripts/run_r_memory_packet.py", "--agent", "beta-smoke"],
    )

    assert payload == {"ok": True, "tier": "collaborator_beta"}


def test_normalize_compact_diagnostic_strips_storage_banner() -> None:
    module = _load_script_module()

    normalized = module._normalize_compact_diagnostic(  # noqa: SLF001
        "[ToneSoul] file | R=0.04/stable | readiness=pass\n"
        "[ToneSoul] Storage: FileStore (Redis not available)\n"
    )

    assert normalized == "[ToneSoul] file | R=0.04/stable | readiness=pass"


def test_main_writes_optional_outputs(tmp_path: Path, monkeypatch, capsys) -> None:
    module = _load_script_module()
    json_out = tmp_path / "preflight.json"
    markdown_out = tmp_path / "preflight.md"

    monkeypatch.setattr(
        module,
        "run_preflight",
        lambda **kwargs: {
            "generated_at": "2026-03-30T00:00:00Z",
            "overall_ok": True,
            "overall_status": "go",
            "entry_stack": {
                "session_start": {"readiness": "pass", "task_track": "feature_track", "deliberation_mode": "standard_council"},
                "packet": {"current_tier": "collaborator_beta", "next_target_tier": "public_launch", "launch_default_mode": "file-backed"},
                "diagnose": {"ok": True, "compact_line": "compact"},
            },
            "validation_wave": {"scenario_count": 4, "max_receiver_alert_count": 4, "contested_dossier_visible": True, "stale_compaction_guarded": True},
            "launch_claim_posture": {"summary_text": "launch_claims=current:collaborator_beta", "blocked_overclaims": []},
            "blocking_findings": [],
        },
    )

    exit_code = module.main(
        [
            "--agent",
            "beta-preflight",
            "--json-out",
            str(json_out),
            "--markdown-out",
            str(markdown_out),
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert json_out.exists()
    assert markdown_out.exists()
    assert payload["overall_status"] == "go"
