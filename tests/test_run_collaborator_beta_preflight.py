from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script_module():
    module_name = "test_run_collaborator_beta_preflight_module"
    module_path = (
        Path(__file__).resolve().parents[1] / "scripts" / "run_collaborator_beta_preflight.py"
    )
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
        "task_track_hint": {"suggested_track": "feature_track", "claim_recommendation": "required"},
        "deliberation_mode_hint": {"suggested_mode": "standard_council"},
        "compact_diagnostic": "[ToneSoul] file | R=0.04/stable | readiness=pass | aegis=compromised",
        "packet": _sample_packet_payload(),
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

    monkeypatch.setattr(
        "scripts.start_agent_session.run_session_start_bundle",
        lambda **kwargs: _sample_start_payload(),
    )
    monkeypatch.setattr(
        module,
        "_detect_external_cycle_status",
        lambda: {"path": "", "classification": ""},
    )

    result = module.run_preflight(agent="beta-preflight", validation_wave_path=validation_path)

    assert result["overall_ok"] is True
    assert result["overall_status"] == "go"
    assert result["entry_stack"]["packet"]["current_tier"] == "collaborator_beta"
    assert result["entry_stack"]["session_start"]["claim_recommendation"] == "required"
    assert result["entry_stack"]["diagnose"]["aegis_status"] == "compromised"
    assert result["scope_posture"]["guided_beta_only"] is True
    assert result["scope_posture"]["target_reading"] == "roadmap_target_only"
    assert result["claim_posture"]["claim_trigger"].startswith(
        "claim when you are about to edit a shared path"
    )
    assert result["aegis_posture"]["blocks_beta_entry"] is False
    assert result["validation_wave"]["scenario_count"] == 3
    assert result["validation_wave"]["stale_compaction_guarded"] is True
    assert result["validation_wave"]["contested_dossier_visible"] is True
    assert result["next_bounded_move"]["step"].startswith(
        "run one real non-creator or external-use clean cycle"
    )
    assert result["next_bounded_move"]["path"] == (
        "docs/plans/tonesoul_non_creator_external_cycle_pack_2026-04-10.md"
    )
    assert result["blocking_findings"] == []
    assert "continuity_effectiveness" in result["cautions"]
    assert "aegis_compromised" in result["cautions"]


def test_run_preflight_holds_when_launch_defaults_drift(monkeypatch, tmp_path: Path) -> None:
    module = _load_script_module()
    validation_path = tmp_path / "wave.json"
    validation_path.write_text("[]\n", encoding="utf-8")

    packet_payload = _sample_packet_payload()
    packet_payload["project_memory_summary"]["launch_claim_posture"][
        "current_tier"
    ] = "internal_alpha"
    packet_payload["coordination_mode"]["launch_default_mode"] = "redis-live"

    start_payload = _sample_start_payload()
    start_payload["packet"] = packet_payload
    monkeypatch.setattr(
        "scripts.start_agent_session.run_session_start_bundle",
        lambda **kwargs: start_payload,
    )

    result = module.run_preflight(agent="beta-preflight", validation_wave_path=validation_path)

    assert result["overall_ok"] is False
    assert result["overall_status"] == "hold"
    assert (
        "launch_claim_posture.current_tier is not collaborator_beta" in result["blocking_findings"]
    )
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
                    "claim_recommendation": "required",
                    "deliberation_mode": "standard_council",
                },
                "packet": {
                    "current_tier": "collaborator_beta",
                    "next_target_tier": "public_launch",
                    "launch_default_mode": "file-backed",
                },
                "diagnose": {
                    "ok": True,
                    "compact_line": "embedded_from_session_start | readiness=pass | aegis=compromised",
                    "aegis_status": "compromised",
                },
            },
            "scope_posture": {
                "scope_note": "guided collaborator beta only; file-backed remains launch default and public launch stays deferred",
                "target_note": "next_target_tier names the next maturity target, not current readiness or public-launch permission.",
            },
            "claim_posture": {
                "claim_trigger": "claim when you are about to edit a shared path; read-only inspection can stay unclaimed",
            },
            "aegis_posture": {
                "status": "compromised",
                "note": "Treat aegis_compromised as a visible caution in the current beta posture, not as an implicit public-launch stop or a reason to ignore the rest of the bounded receiver checks.",
            },
            "external_cycle_status": {
                "path": "",
                "classification": "",
            },
            "next_bounded_move": {
                "step": "run one real non-creator or external-use clean cycle for Phase 722",
                "path": "docs/plans/tonesoul_non_creator_external_cycle_pack_2026-04-10.md",
                "note": "Pack exists, but no clean non-creator / external-use governance-aware cycle is yet recorded in canonical status surfaces.",
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
                    {
                        "claim": "continuity_effectiveness",
                        "current_classification": "runtime_present",
                    }
                ],
            },
            "blocking_findings": [],
        }
    )

    assert "# ToneSoul Collaborator-Beta Preflight" in markdown
    assert (
        "| session-start | ok | readiness=pass track=feature_track claim=required mode=standard_council |"
        in markdown
    )
    assert (
        "| diagnose | ok | embedded_from_session_start | readiness=pass | aegis=compromised (aegis=compromised) |"
        in markdown
    )
    assert (
        "- Scope posture: `guided collaborator beta only; file-backed remains launch default and public launch stays deferred`"
        in markdown
    )
    assert (
        "- Target reading: `next_target_tier names the next maturity target, not current readiness or public-launch permission.`"
        in markdown
    )
    assert (
        "- Claim trigger: `claim when you are about to edit a shared path; read-only inspection can stay unclaimed`"
        in markdown
    )
    assert (
        "- Aegis posture: `compromised` / `Treat aegis_compromised as a visible caution in the current beta posture, not as an implicit public-launch stop or a reason to ignore the rest of the bounded receiver checks.`"
        in markdown
    )
    assert (
        "- Next bounded move: `run one real non-creator or external-use clean cycle for Phase 722`"
        in markdown
    )
    assert "- Path: `docs/plans/tonesoul_non_creator_external_cycle_pack_2026-04-10.md`" in markdown
    assert "- Latest external cycle: `none`" in markdown
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


def test_build_public_diagnose_summary_redacts_operational_residue() -> None:
    module = _load_script_module()

    summary = module._build_public_diagnose_summary(  # noqa: SLF001
        compact_diagnostic=(
            "[ToneSoul] file | SI=0.45 | vows=3 tensions=0 | R=0.00/stable | "
            "claims=0 checkpoints=1 compactions=5 subjects=2 | git=034bf2f/dirty=7 | "
            "aegis=compromised | agent=phase722-refresh | readiness=pass"
        ),
        readiness="pass",
    )

    assert summary == "embedded_from_session_start | readiness=pass | aegis=compromised"


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
                "session_start": {
                    "readiness": "pass",
                    "task_track": "feature_track",
                    "claim_recommendation": "required",
                    "deliberation_mode": "standard_council",
                },
                "packet": {
                    "current_tier": "collaborator_beta",
                    "next_target_tier": "public_launch",
                    "launch_default_mode": "file-backed",
                },
                "diagnose": {
                    "ok": True,
                    "compact_line": "embedded_from_session_start | readiness=pass | aegis=compromised",
                    "aegis_status": "compromised",
                },
            },
            "scope_posture": {
                "scope_note": "guided collaborator beta only; file-backed remains launch default and public launch stays deferred"
            },
            "claim_posture": {
                "claim_trigger": "claim when you are about to edit a shared path; read-only inspection can stay unclaimed"
            },
            "aegis_posture": {
                "status": "compromised",
                "note": "Treat aegis_compromised as a visible caution in the current beta posture, not as an implicit public-launch stop or a reason to ignore the rest of the bounded receiver checks.",
            },
            "external_cycle_status": {
                "path": "",
                "classification": "",
            },
            "next_bounded_move": {
                "step": "run one real non-creator or external-use clean cycle for Phase 722",
                "path": "docs/plans/tonesoul_non_creator_external_cycle_pack_2026-04-10.md",
                "note": "Pack exists, but no clean non-creator / external-use governance-aware cycle is yet recorded in canonical status surfaces.",
            },
            "validation_wave": {
                "scenario_count": 4,
                "max_receiver_alert_count": 4,
                "contested_dossier_visible": True,
                "stale_compaction_guarded": True,
            },
            "launch_claim_posture": {
                "summary_text": "launch_claims=current:collaborator_beta",
                "blocked_overclaims": [],
            },
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


def test_run_preflight_points_to_repeated_validation_after_strong_external_pass(
    monkeypatch, tmp_path: Path
) -> None:
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
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "scripts.start_agent_session.run_session_start_bundle",
        lambda **kwargs: _sample_start_payload(),
    )
    monkeypatch.setattr(
        module,
        "_detect_external_cycle_status",
        lambda: {
            "path": "docs/status/phase722_external_operator_cycle_2026-04-10.md",
            "classification": "strong external pass",
            "cycle_shape": "single_surface",
        },
    )

    result = module.run_preflight(agent="beta-preflight", validation_wave_path=validation_path)

    assert result["external_cycle_status"]["classification"] == "strong external pass"
    assert result["next_bounded_move"]["step"].startswith(
        "run the dual-surface repeated external cycle"
    )
    assert result["next_bounded_move"]["path"] == (
        "docs/plans/tonesoul_non_creator_external_cycle_dual_surface_pack_2026-04-10.md"
    )
    assert (
        "one bounded canonical surface plus one fresh status note"
        in result["next_bounded_move"]["note"]
    )


def test_detect_external_cycle_status_prefers_latest_dual_surface_note(
    monkeypatch, tmp_path: Path
) -> None:
    module = _load_script_module()
    status_dir = tmp_path / "docs" / "status"
    status_dir.mkdir(parents=True)
    (status_dir / "phase722_external_operator_cycle_2026-04-10.md").write_text(
        "# old\n> Result classification: `strong external pass`\n",
        encoding="utf-8",
    )
    (status_dir / "phase722_external_dual_surface_cycle_2026-04-14.md").write_text(
        "# new\n> Result classification: `strong external pass`\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)

    result = module._detect_external_cycle_status()  # noqa: SLF001

    assert result == {
        "path": "docs/status/phase722_external_dual_surface_cycle_2026-04-14.md",
        "classification": "strong external pass",
        "cycle_shape": "dual_surface",
    }


def test_run_preflight_consolidates_after_repeated_strong_external_pass(
    monkeypatch, tmp_path: Path
) -> None:
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
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "scripts.start_agent_session.run_session_start_bundle",
        lambda **kwargs: _sample_start_payload(),
    )
    monkeypatch.setattr(
        module,
        "_detect_external_cycle_status",
        lambda: {
            "path": "docs/status/phase722_external_dual_surface_cycle_2026-04-14.md",
            "classification": "strong external pass",
            "cycle_shape": "dual_surface",
        },
    )

    result = module.run_preflight(agent="beta-preflight", validation_wave_path=validation_path)

    assert result["external_cycle_status"]["classification"] == "strong external pass"
    assert result["external_cycle_status"]["cycle_shape"] == "dual_surface"
    assert result["next_bounded_move"]["step"].startswith(
        "consolidate current-truth launch surfaces"
    )
    assert result["next_bounded_move"]["path"] == ("docs/plans/tonesoul_work_plan_v2_2026-04-14.md")
    assert (
        "two clean bounded non-creator cycles across two task shapes"
        in result["next_bounded_move"]["note"]
    )


def test_detect_external_cycle_status_prefers_latest_preflight_refresh_note(
    monkeypatch, tmp_path: Path
) -> None:
    module = _load_script_module()
    status_dir = tmp_path / "docs" / "status"
    status_dir.mkdir(parents=True)
    (status_dir / "phase722_external_dual_surface_cycle_2026-04-14.md").write_text(
        "# older\n> Result classification: `strong external pass`\n",
        encoding="utf-8",
    )
    (status_dir / "phase722_external_preflight_refresh_cycle_2026-04-15.md").write_text(
        "# newer\n> Result classification: `useful partial`\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)

    result = module._detect_external_cycle_status()  # noqa: SLF001

    assert result == {
        "path": "docs/status/phase722_external_preflight_refresh_cycle_2026-04-15.md",
        "classification": "useful partial",
        "cycle_shape": "preflight_refresh",
    }


def test_run_preflight_routes_preflight_refresh_partial_to_same_pack(
    monkeypatch, tmp_path: Path
) -> None:
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
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "scripts.start_agent_session.run_session_start_bundle",
        lambda **kwargs: _sample_start_payload(),
    )
    monkeypatch.setattr(
        module,
        "_detect_external_cycle_status",
        lambda: {
            "path": "docs/status/phase722_external_preflight_refresh_cycle_2026-04-15.md",
            "classification": "useful partial",
            "cycle_shape": "preflight_refresh",
        },
    )

    result = module.run_preflight(agent="beta-preflight", validation_wave_path=validation_path)

    assert result["external_cycle_status"]["classification"] == "useful partial"
    assert result["external_cycle_status"]["cycle_shape"] == "preflight_refresh"
    assert result["next_bounded_move"]["step"].startswith(
        "repair the preflight-refresh evidence seam"
    )
    assert result["next_bounded_move"]["path"] == (
        "docs/plans/tonesoul_non_creator_external_cycle_preflight_refresh_pack_2026-04-15.md"
    )
    assert "rerun the same bounded pack" in result["next_bounded_move"]["note"]


def test_run_preflight_routes_preflight_refresh_strong_pass_to_phase726_review(
    monkeypatch, tmp_path: Path
) -> None:
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
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "scripts.start_agent_session.run_session_start_bundle",
        lambda **kwargs: _sample_start_payload(),
    )
    monkeypatch.setattr(
        module,
        "_detect_external_cycle_status",
        lambda: {
            "path": "docs/status/phase722_external_preflight_refresh_cycle_2026-04-15.md",
            "classification": "strong external pass",
            "cycle_shape": "preflight_refresh",
        },
    )
    monkeypatch.setattr(
        module,
        "_detect_latest_phase726_review",
        lambda: {
            "path": "docs/status/phase726_go_nogo_2026-04-08.md",
            "is_refreshed": False,
        },
    )

    result = module.run_preflight(agent="beta-preflight", validation_wave_path=validation_path)

    assert result["external_cycle_status"]["classification"] == "strong external pass"
    assert result["external_cycle_status"]["cycle_shape"] == "preflight_refresh"
    assert result["next_bounded_move"]["step"].startswith(
        "refresh the collaborator-beta go/no-go review"
    )
    assert result["next_bounded_move"]["path"] == ("docs/status/phase726_go_nogo_2026-04-08.md")
    assert (
        "third bounded Phase 722 task shape has now landed cleanly"
        in result["next_bounded_move"]["note"]
    )


def test_detect_latest_phase726_review_prefers_latest_dated_note(
    monkeypatch, tmp_path: Path
) -> None:
    module = _load_script_module()
    status_dir = tmp_path / "docs" / "status"
    status_dir.mkdir(parents=True)
    (status_dir / "phase726_go_nogo_2026-04-08.md").write_text("# older\n", encoding="utf-8")
    (status_dir / "phase726_go_nogo_2026-04-15.md").write_text("# newer\n", encoding="utf-8")
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        module,
        "PHASE726_REVIEW_ANCHOR",
        tmp_path / "docs" / "status" / "phase726_go_nogo_2026-04-08.md",
    )

    result = module._detect_latest_phase726_review()  # noqa: SLF001

    assert result == {
        "path": "docs/status/phase726_go_nogo_2026-04-15.md",
        "is_refreshed": True,
    }


def test_run_preflight_advances_to_phase724_after_phase726_refresh(
    monkeypatch, tmp_path: Path
) -> None:
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
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "scripts.start_agent_session.run_session_start_bundle",
        lambda **kwargs: _sample_start_payload(),
    )
    monkeypatch.setattr(
        module,
        "_detect_external_cycle_status",
        lambda: {
            "path": "docs/status/phase722_external_preflight_refresh_cycle_2026-04-15_rerun.md",
            "classification": "strong external pass",
            "cycle_shape": "preflight_refresh",
        },
    )
    monkeypatch.setattr(
        module,
        "_detect_latest_phase726_review",
        lambda: {
            "path": "docs/status/phase726_go_nogo_2026-04-15.md",
            "is_refreshed": True,
        },
    )
    monkeypatch.setattr(
        module,
        "_detect_latest_phase724_surface",
        lambda: {
            "path": "docs/status/phase724_launch_operations_surface_2026-04-15.md",
            "is_refreshed": False,
        },
    )

    result = module.run_preflight(agent="beta-preflight", validation_wave_path=validation_path)

    assert result["next_bounded_move"]["step"].startswith(
        "consolidate one current launch-operations surface"
    )
    assert result["next_bounded_move"]["path"] == (
        "docs/status/phase724_launch_operations_surface_2026-04-15.md"
    )
    assert (
        "already been refreshed against three clean bounded Phase 722 cycles"
        in result["next_bounded_move"]["note"]
    )


def test_detect_latest_phase724_surface_prefers_latest_anchor(monkeypatch, tmp_path: Path) -> None:
    module = _load_script_module()
    status_dir = tmp_path / "docs" / "status"
    status_dir.mkdir(parents=True)
    (status_dir / "phase724_launch_operations_surface_2026-04-15.md").write_text(
        "# current\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        module,
        "LAUNCH_OPERATIONS_SURFACE_ANCHOR",
        tmp_path / "docs" / "status" / "phase724_launch_operations_surface_2026-04-15.md",
    )

    result = module._detect_latest_phase724_surface()  # noqa: SLF001

    assert result == {
        "path": "docs/status/phase724_launch_operations_surface_2026-04-15.md",
        "is_refreshed": True,
    }


def test_run_preflight_points_to_current_phase724_surface_after_consolidation(
    monkeypatch, tmp_path: Path
) -> None:
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
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "scripts.start_agent_session.run_session_start_bundle",
        lambda **kwargs: _sample_start_payload(),
    )
    monkeypatch.setattr(
        module,
        "_detect_external_cycle_status",
        lambda: {
            "path": "docs/status/phase722_external_preflight_refresh_cycle_2026-04-15_rerun.md",
            "classification": "strong external pass",
            "cycle_shape": "preflight_refresh",
        },
    )
    monkeypatch.setattr(
        module,
        "_detect_latest_phase726_review",
        lambda: {
            "path": "docs/status/phase726_go_nogo_2026-04-15.md",
            "is_refreshed": True,
        },
    )
    monkeypatch.setattr(
        module,
        "_detect_latest_phase724_surface",
        lambda: {
            "path": "docs/status/phase724_launch_operations_surface_2026-04-15.md",
            "is_refreshed": True,
        },
    )

    result = module.run_preflight(agent="beta-preflight", validation_wave_path=validation_path)

    assert result["next_bounded_move"]["step"].startswith(
        "use the current launch-operations surface as the operator-facing anchor"
    )
    assert result["next_bounded_move"]["path"] == (
        "docs/status/phase724_launch_operations_surface_2026-04-15.md"
    )
    assert (
        "Phase 724 is now consolidated into one current operator-facing launch surface"
        in result["next_bounded_move"]["note"]
    )
