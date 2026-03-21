import json
from pathlib import Path

import scripts.run_repo_healthcheck as healthcheck


def test_is_ci_environment_detects_truthy_values(monkeypatch) -> None:
    monkeypatch.setenv("CI", "true")
    assert healthcheck._is_ci_environment() is True

    monkeypatch.setenv("CI", "1")
    assert healthcheck._is_ci_environment() is True


def test_is_ci_environment_detects_falsey_values(monkeypatch) -> None:
    monkeypatch.delenv("CI", raising=False)
    assert healthcheck._is_ci_environment() is False

    monkeypatch.setenv("CI", "0")
    assert healthcheck._is_ci_environment() is False


def test_display_command_normalizes_python_executable() -> None:
    command = [
        r"C:\\Users\\user\\Desktop\\repo\\.venv\\Scripts\\python.exe",
        "scripts/run_repo_healthcheck.py",
        "--strict",
    ]
    assert command[0] != "python"
    assert (
        healthcheck._display_command(command) == "python scripts/run_repo_healthcheck.py --strict"
    )


def test_display_command_normalizes_npm_executable() -> None:
    command = [
        r"C:\\Program Files\\nodejs\\npm.cmd",
        "--prefix",
        "apps/web",
        "run",
        "test",
    ]
    assert healthcheck._display_command(command) == "npm --prefix apps/web run test"


def test_build_check_specs_includes_verify_7d_flags(tmp_path: Path) -> None:
    discussion_path = tmp_path / "agent_discussion_curated.jsonl"
    discussion_path.write_text('{"status":"final"}\n', encoding="utf-8")

    specs = healthcheck._build_check_specs(
        python_executable=r"C:\\repo\\.venv\\Scripts\\python.exe",
        include_sdh=True,
        check_council_modes=True,
        strict_soft_fail=True,
        web_base=None,
        api_base=None,
        sdh_timeout=None,
        allow_missing_discussion=False,
        discussion_path=discussion_path,
    )
    audit_7d = next(item for item in specs if item["name"] == "audit_7d")
    git_hygiene = next(item for item in specs if item["name"] == "git_hygiene")
    assert git_hygiene["command"] == [
        r"C:\\repo\\.venv\\Scripts\\python.exe",
        "scripts/verify_git_hygiene.py",
        "--strict",
        "--max-tracked-ignored",
        "28",
    ]
    assert "--include-sdh" in audit_7d["command"]
    assert "--check-council-modes" in audit_7d["command"]
    assert "--strict-soft-fail" in audit_7d["command"]
    assert "skip_reason" not in audit_7d


def test_build_check_specs_skips_7d_if_discussion_missing_and_allowed(tmp_path: Path) -> None:
    discussion_path = tmp_path / "missing.jsonl"

    specs = healthcheck._build_check_specs(
        python_executable=r"C:\\repo\\.venv\\Scripts\\python.exe",
        include_sdh=False,
        check_council_modes=True,
        strict_soft_fail=False,
        web_base=None,
        api_base=None,
        sdh_timeout=None,
        allow_missing_discussion=True,
        discussion_path=discussion_path,
    )
    audit_7d = next(item for item in specs if item["name"] == "audit_7d")
    git_hygiene = next(item for item in specs if item["name"] == "git_hygiene")
    assert audit_7d["command"] == [r"C:\\repo\\.venv\\Scripts\\python.exe", "scripts/verify_7d.py"]
    assert audit_7d["skip_reason"] == f"missing discussion file: {discussion_path}"
    assert "skip_reason" not in git_hygiene
    assert git_hygiene["command"] == [
        r"C:\\repo\\.venv\\Scripts\\python.exe",
        "scripts/verify_git_hygiene.py",
        "--strict",
        "--max-tracked-ignored",
        "28",
    ]


def test_build_check_specs_can_disable_council_mode_checks(tmp_path: Path) -> None:
    discussion_path = tmp_path / "agent_discussion_curated.jsonl"
    discussion_path.write_text('{"status":"final"}\n', encoding="utf-8")

    specs = healthcheck._build_check_specs(
        python_executable=r"C:\\repo\\.venv\\Scripts\\python.exe",
        include_sdh=True,
        check_council_modes=False,
        strict_soft_fail=False,
        web_base=None,
        api_base=None,
        sdh_timeout=None,
        allow_missing_discussion=False,
        discussion_path=discussion_path,
    )
    audit_7d = next(item for item in specs if item["name"] == "audit_7d")
    assert "--include-sdh" in audit_7d["command"]
    assert "--no-check-council-modes" in audit_7d["command"]
    assert "--check-council-modes" not in audit_7d["command"]


def test_build_check_specs_passes_sdh_endpoint_overrides(tmp_path: Path) -> None:
    discussion_path = tmp_path / "agent_discussion_curated.jsonl"
    discussion_path.write_text('{"status":"final"}\n', encoding="utf-8")

    specs = healthcheck._build_check_specs(
        python_executable=r"C:\\repo\\.venv\\Scripts\\python.exe",
        include_sdh=True,
        check_council_modes=True,
        strict_soft_fail=False,
        web_base="http://127.0.0.1:3002",
        api_base="http://127.0.0.1:5001",
        sdh_timeout=55,
        allow_missing_discussion=False,
        discussion_path=discussion_path,
    )

    audit_7d = next(item for item in specs if item["name"] == "audit_7d")
    assert "--web-base" in audit_7d["command"]
    assert "http://127.0.0.1:3002" in audit_7d["command"]
    assert "--api-base" in audit_7d["command"]
    assert "http://127.0.0.1:5001" in audit_7d["command"]
    assert "--timeout" in audit_7d["command"]
    assert "55" in audit_7d["command"]


def test_build_check_specs_includes_persona_swarm_strict_check(tmp_path: Path) -> None:
    discussion_path = tmp_path / "agent_discussion_curated.jsonl"
    discussion_path.write_text('{"status":"final"}\n', encoding="utf-8")

    python_executable = r"C:\\repo\\.venv\\Scripts\\python.exe"
    specs = healthcheck._build_check_specs(
        python_executable=python_executable,
        include_sdh=False,
        check_council_modes=True,
        strict_soft_fail=False,
        web_base=None,
        api_base=None,
        sdh_timeout=None,
        allow_missing_discussion=False,
        discussion_path=discussion_path,
    )

    persona_swarm = next(item for item in specs if item["name"] == "persona_swarm")
    assert persona_swarm["command"] == [
        python_executable,
        "scripts/run_persona_swarm_framework.py",
        "--strict",
    ]


def test_build_check_specs_includes_external_source_registry_check(tmp_path: Path) -> None:
    discussion_path = tmp_path / "agent_discussion_curated.jsonl"
    discussion_path.write_text('{"status":"final"}\n', encoding="utf-8")

    python_executable = r"C:\\repo\\.venv\\Scripts\\python.exe"
    specs = healthcheck._build_check_specs(
        python_executable=python_executable,
        include_sdh=False,
        check_council_modes=True,
        strict_soft_fail=False,
        web_base=None,
        api_base=None,
        sdh_timeout=None,
        allow_missing_discussion=False,
        discussion_path=discussion_path,
    )

    source_registry = next(item for item in specs if item["name"] == "external_source_registry")
    assert source_registry["command"] == [
        python_executable,
        "scripts/verify_external_source_registry.py",
        "--strict",
    ]


def test_build_check_specs_includes_skill_registry_check(tmp_path: Path) -> None:
    discussion_path = tmp_path / "agent_discussion_curated.jsonl"
    discussion_path.write_text('{"status":"final"}\n', encoding="utf-8")

    python_executable = r"C:\\repo\\.venv\\Scripts\\python.exe"
    specs = healthcheck._build_check_specs(
        python_executable=python_executable,
        include_sdh=False,
        check_council_modes=True,
        strict_soft_fail=False,
        web_base=None,
        api_base=None,
        sdh_timeout=None,
        allow_missing_discussion=False,
        discussion_path=discussion_path,
    )

    skill_registry = next(item for item in specs if item["name"] == "skill_registry")
    assert skill_registry["command"] == [
        python_executable,
        "scripts/verify_skill_registry.py",
        "--strict",
    ]


def test_build_check_specs_includes_multi_agent_divergence_check(tmp_path: Path) -> None:
    discussion_path = tmp_path / "agent_discussion_curated.jsonl"
    discussion_path.write_text('{"status":"final"}\n', encoding="utf-8")

    python_executable = r"C:\\repo\\.venv\\Scripts\\python.exe"
    specs = healthcheck._build_check_specs(
        python_executable=python_executable,
        include_sdh=False,
        check_council_modes=True,
        strict_soft_fail=False,
        web_base=None,
        api_base=None,
        sdh_timeout=None,
        allow_missing_discussion=False,
        discussion_path=discussion_path,
    )

    divergence = next(item for item in specs if item["name"] == "multi_agent_divergence")
    assert divergence["command"] == [
        python_executable,
        "scripts/run_multi_agent_divergence_report.py",
        "--strict",
    ]


def test_build_check_specs_includes_memory_quality_check(tmp_path: Path) -> None:
    discussion_path = tmp_path / "agent_discussion_curated.jsonl"
    discussion_path.write_text('{"status":"final"}\n', encoding="utf-8")

    python_executable = r"C:\\repo\\.venv\\Scripts\\python.exe"
    specs = healthcheck._build_check_specs(
        python_executable=python_executable,
        include_sdh=False,
        check_council_modes=True,
        strict_soft_fail=False,
        web_base=None,
        api_base=None,
        sdh_timeout=None,
        allow_missing_discussion=False,
        discussion_path=discussion_path,
    )

    memory_quality = next(item for item in specs if item["name"] == "memory_quality")
    assert memory_quality["command"] == [
        python_executable,
        "scripts/run_memory_quality_report.py",
        "--strict",
    ]


def test_build_check_specs_includes_memory_governance_contract_check(tmp_path: Path) -> None:
    discussion_path = tmp_path / "agent_discussion_curated.jsonl"
    discussion_path.write_text('{"status":"final"}\n', encoding="utf-8")

    python_executable = r"C:\\repo\\.venv\\Scripts\\python.exe"
    specs = healthcheck._build_check_specs(
        python_executable=python_executable,
        include_sdh=False,
        check_council_modes=True,
        strict_soft_fail=False,
        web_base=None,
        api_base=None,
        sdh_timeout=None,
        allow_missing_discussion=False,
        discussion_path=discussion_path,
    )

    contract = next(item for item in specs if item["name"] == "memory_governance_contract")
    assert contract["command"] == [
        python_executable,
        "scripts/run_memory_governance_contract_check.py",
        "--strict",
    ]


def test_build_check_specs_includes_friction_shadow_calibration_check(tmp_path: Path) -> None:
    discussion_path = tmp_path / "agent_discussion_curated.jsonl"
    discussion_path.write_text('{"status":"final"}\n', encoding="utf-8")

    python_executable = r"C:\\repo\\.venv\\Scripts\\python.exe"
    specs = healthcheck._build_check_specs(
        python_executable=python_executable,
        include_sdh=False,
        check_council_modes=True,
        strict_soft_fail=False,
        web_base=None,
        api_base=None,
        sdh_timeout=None,
        allow_missing_discussion=False,
        discussion_path=discussion_path,
    )

    report = next(item for item in specs if item["name"] == "friction_shadow_calibration")
    assert report["command"] == [
        python_executable,
        "scripts/run_friction_shadow_calibration_report.py",
        "--strict",
    ]


def test_build_check_specs_includes_friction_shadow_replay_export_check(tmp_path: Path) -> None:
    discussion_path = tmp_path / "agent_discussion_curated.jsonl"
    discussion_path.write_text('{"status":"final"}\n', encoding="utf-8")

    python_executable = r"C:\\repo\\.venv\\Scripts\\python.exe"
    specs = healthcheck._build_check_specs(
        python_executable=python_executable,
        include_sdh=False,
        check_council_modes=True,
        strict_soft_fail=False,
        web_base=None,
        api_base=None,
        sdh_timeout=None,
        allow_missing_discussion=False,
        discussion_path=discussion_path,
    )

    export = next(item for item in specs if item["name"] == "friction_shadow_replay_export")
    assert export["command"] == [
        python_executable,
        "scripts/run_friction_shadow_replay_export.py",
        "--strict",
    ]


def test_build_check_specs_includes_philosophical_reflection_check(tmp_path: Path) -> None:
    discussion_path = tmp_path / "agent_discussion_curated.jsonl"
    discussion_path.write_text('{"status":"final"}\n', encoding="utf-8")

    python_executable = r"C:\\repo\\.venv\\Scripts\\python.exe"
    specs = healthcheck._build_check_specs(
        python_executable=python_executable,
        include_sdh=False,
        check_council_modes=True,
        strict_soft_fail=False,
        web_base=None,
        api_base=None,
        sdh_timeout=None,
        allow_missing_discussion=False,
        discussion_path=discussion_path,
    )

    reflection = next(item for item in specs if item["name"] == "philosophical_reflection")
    assert reflection["command"] == [
        python_executable,
        "scripts/run_philosophical_reflection_report.py",
        "--strict",
    ]


def test_build_check_specs_includes_memory_topology_fit_check(tmp_path: Path) -> None:
    discussion_path = tmp_path / "agent_discussion_curated.jsonl"
    discussion_path.write_text('{"status":"final"}\n', encoding="utf-8")

    python_executable = r"C:\\repo\\.venv\\Scripts\\python.exe"
    specs = healthcheck._build_check_specs(
        python_executable=python_executable,
        include_sdh=False,
        check_council_modes=True,
        strict_soft_fail=False,
        web_base=None,
        api_base=None,
        sdh_timeout=None,
        allow_missing_discussion=False,
        discussion_path=discussion_path,
    )

    topology_fit = next(item for item in specs if item["name"] == "memory_topology_fit")
    assert topology_fit["command"] == [
        python_executable,
        "scripts/run_memory_topology_fit_report.py",
        "--strict",
    ]


def test_build_check_specs_includes_repo_intelligence_check(tmp_path: Path) -> None:
    discussion_path = tmp_path / "agent_discussion_curated.jsonl"
    discussion_path.write_text('{"status":"final"}\n', encoding="utf-8")

    python_executable = r"C:\\repo\\.venv\\Scripts\\python.exe"
    specs = healthcheck._build_check_specs(
        python_executable=python_executable,
        include_sdh=False,
        check_council_modes=True,
        strict_soft_fail=False,
        web_base=None,
        api_base=None,
        sdh_timeout=None,
        allow_missing_discussion=False,
        discussion_path=discussion_path,
    )

    repo_intelligence = next(item for item in specs if item["name"] == "repo_intelligence")
    assert repo_intelligence["command"] == [
        python_executable,
        "scripts/run_repo_intelligence_report.py",
    ]
    assert repo_intelligence["structured_output"] == "json"


def test_build_check_specs_includes_dual_track_boundary_check(tmp_path: Path) -> None:
    discussion_path = tmp_path / "agent_discussion_curated.jsonl"
    discussion_path.write_text('{"status":"final"}\n', encoding="utf-8")

    python_executable = r"C:\\repo\\.venv\\Scripts\\python.exe"
    specs = healthcheck._build_check_specs(
        python_executable=python_executable,
        include_sdh=False,
        check_council_modes=True,
        strict_soft_fail=False,
        web_base=None,
        api_base=None,
        sdh_timeout=None,
        allow_missing_discussion=False,
        discussion_path=discussion_path,
    )

    dual_track = next(item for item in specs if item["name"] == "dual_track_boundary")
    assert dual_track["command"] == [
        python_executable,
        "scripts/verify_dual_track_boundary.py",
        "--strict",
        "--staged",
    ]


def test_build_check_specs_includes_incremental_commit_attribution_check(tmp_path: Path) -> None:
    discussion_path = tmp_path / "agent_discussion_curated.jsonl"
    discussion_path.write_text('{"status":"final"}\n', encoding="utf-8")

    python_executable = r"C:\\repo\\.venv\\Scripts\\python.exe"
    specs = healthcheck._build_check_specs(
        python_executable=python_executable,
        include_sdh=False,
        check_council_modes=True,
        strict_soft_fail=False,
        web_base=None,
        api_base=None,
        sdh_timeout=None,
        allow_missing_discussion=False,
        discussion_path=discussion_path,
    )

    commit_attribution = next(item for item in specs if item["name"] == "commit_attribution")
    assert commit_attribution["command"] == [
        python_executable,
        "scripts/verify_incremental_commit_attribution.py",
        "--strict",
        "--artifact-path",
        "docs/status/commit_attribution_local.json",
    ]


def test_build_check_specs_includes_true_verification_weekly_check_on_windows(
    monkeypatch,
    tmp_path: Path,
) -> None:
    discussion_path = tmp_path / "agent_discussion_curated.jsonl"
    discussion_path.write_text('{"status":"final"}\n', encoding="utf-8")

    python_executable = r"C:\\repo\\.venv\\Scripts\\python.exe"
    monkeypatch.setattr(healthcheck, "_is_windows_environment", lambda: True)
    specs = healthcheck._build_check_specs(
        python_executable=python_executable,
        include_sdh=False,
        check_council_modes=True,
        strict_soft_fail=False,
        web_base=None,
        api_base=None,
        sdh_timeout=None,
        allow_missing_discussion=False,
        discussion_path=discussion_path,
    )

    weekly = next(item for item in specs if item["name"] == "true_verification_weekly")
    assert weekly["command"] == [
        python_executable,
        "scripts/report_true_verification_task_status.py",
        "--strict",
    ]
    assert "skip_reason" not in weekly


def test_build_check_specs_skips_true_verification_weekly_check_on_non_windows(
    monkeypatch,
    tmp_path: Path,
) -> None:
    discussion_path = tmp_path / "agent_discussion_curated.jsonl"
    discussion_path.write_text('{"status":"final"}\n', encoding="utf-8")

    python_executable = r"C:\\repo\\.venv\\Scripts\\python.exe"
    monkeypatch.setattr(healthcheck, "_is_windows_environment", lambda: False)
    specs = healthcheck._build_check_specs(
        python_executable=python_executable,
        include_sdh=False,
        check_council_modes=True,
        strict_soft_fail=False,
        web_base=None,
        api_base=None,
        sdh_timeout=None,
        allow_missing_discussion=False,
        discussion_path=discussion_path,
    )

    weekly = next(item for item in specs if item["name"] == "true_verification_weekly")
    assert weekly["command"] == [
        python_executable,
        "scripts/report_true_verification_task_status.py",
        "--strict",
    ]
    assert weekly["skip_reason"] == "requires Windows Task Scheduler host"


def test_collect_recovery_advice_skips_when_commit_attribution_is_not_failing(
    tmp_path: Path,
) -> None:
    advice = healthcheck._collect_recovery_advice(
        checks=[
            {
                "name": "commit_attribution",
                "status": "pass",
            }
        ],
        repo_root=tmp_path,
        python_executable=r"C:\\repo\\.venv\\Scripts\\python.exe",
    )

    assert advice == []


def test_collect_recovery_advice_runs_base_switch_planner(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_run_json_command(name: str, command: list[str], cwd: Path):
        captured["name"] = name
        captured["command"] = command
        captured["cwd"] = cwd
        return (
            {
                "name": name,
                "status": "pass",
                "ok": True,
                "exit_code": 0,
                "duration_seconds": 0.12,
                "command": healthcheck._display_command(command),
                "stdout_tail": "",
                "stderr_tail": "",
            },
            {
                "recommendation": "defer_until_worktree_clean",
                "rationale": "worktree dirty",
                "tree_equal": True,
                "current_missing_count": 5,
                "backfill_missing_count": 0,
                "suggested_commands": [
                    "git worktree add <clean-path> feat/env-perception-attribution-backfill"
                ],
            },
        )

    monkeypatch.setattr(healthcheck, "_run_json_command", fake_run_json_command)

    advice = healthcheck._collect_recovery_advice(
        checks=[
            {
                "name": "commit_attribution",
                "status": "fail",
            }
        ],
        repo_root=tmp_path,
        python_executable=r"C:\\repo\\.venv\\Scripts\\python.exe",
    )

    assert captured["name"] == "commit_attribution_recovery"
    assert captured["cwd"] == tmp_path
    assert captured["command"] == [
        r"C:\\repo\\.venv\\Scripts\\python.exe",
        "scripts/plan_commit_attribution_base_switch.py",
        "--artifact-path",
        "docs/status/commit_attribution_base_switch_latest.json",
    ]
    assert advice == [
        {
            "name": "commit_attribution_recovery",
            "status": "pass",
            "ok": True,
            "exit_code": 0,
            "duration_seconds": 0.12,
            "command": (
                "python scripts/plan_commit_attribution_base_switch.py "
                "--artifact-path docs/status/commit_attribution_base_switch_latest.json"
            ),
            "stdout_tail": "",
            "stderr_tail": "",
            "artifact_path": "docs/status/commit_attribution_base_switch_latest.json",
            "detail": {
                "recommendation": "defer_until_worktree_clean",
                "rationale": "worktree dirty",
                "tree_equal": True,
                "current_missing_count": 5,
                "backfill_missing_count": 0,
                "suggested_commands": [
                    "git worktree add <clean-path> feat/env-perception-attribution-backfill"
                ],
            },
        }
    ]


def test_extract_handoff_surface_reads_runtime_and_policy_lines() -> None:
    payload = {
        "primary_status_line": (
            "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
            "runtime_source=host_tick session=weekly-session resumed=yes"
        ),
        "runtime_status_line": (
            "host_tick | session=weekly-session resumed=yes next_cycle=4 "
            "failures=1 max_failure=1 tension=breached"
        ),
        "semantic_retrieval_protocol": (
            "alias_first -> neighborhood_before_file -> status_surface_before_source"
        ),
        "semantic_preferred_neighborhood": "repo_governance",
        "anchor_status_line": (
            "anchor | [tension_afbd38eb] tension: High PE valuation in a market pullback..."
        ),
        "artifact_policy_status_line": "artifacts_ready | strict=true missing=0 stale=0",
        "admissibility_primary_status_line": (
            "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
        ),
        "scribe_status_line": (
            "scribe | status=generated mode=template_assist "
            "posture=pressure_without_counterweight"
        ),
        "handoff": {
            "queue_shape": "weekly_host_status",
            "primary_status_line": (
                "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
                "runtime_source=host_tick session=weekly-session resumed=yes"
            ),
            "requires_operator_action": False,
        },
    }

    assert healthcheck._extract_handoff_surface(payload) == {
        "queue_shape": "weekly_host_status",
        "primary_status_line": (
            "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
            "runtime_source=host_tick session=weekly-session resumed=yes"
        ),
        "runtime_status_line": (
            "host_tick | session=weekly-session resumed=yes next_cycle=4 "
            "failures=1 max_failure=1 tension=breached"
        ),
        "semantic_retrieval_protocol": (
            "alias_first -> neighborhood_before_file -> status_surface_before_source"
        ),
        "semantic_preferred_neighborhood": "repo_governance",
        "anchor_status_line": (
            "anchor | [tension_afbd38eb] tension: High PE valuation in a market pullback..."
        ),
        "artifact_policy_status_line": "artifacts_ready | strict=true missing=0 stale=0",
        "admissibility_primary_status_line": (
            "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
        ),
        "scribe_status_line": (
            "scribe | status=generated mode=template_assist "
            "posture=pressure_without_counterweight"
        ),
        "requires_operator_action": "false",
    }


def test_extract_handoff_surface_reads_artifact_and_admissibility_from_handoff_only() -> None:
    payload = {
        "primary_status_line": (
            "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
            "runtime_source=host_tick session=weekly-session resumed=yes"
        ),
        "handoff": {
            "queue_shape": "weekly_host_status",
            "primary_status_line": (
                "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
                "runtime_source=host_tick session=weekly-session resumed=yes"
            ),
            "runtime_status_line": (
                "host_tick | session=weekly-session resumed=yes next_cycle=4 "
                "failures=1 max_failure=1 tension=breached"
            ),
            "semantic_retrieval_protocol": (
                "alias_first -> neighborhood_before_file -> status_surface_before_source"
            ),
            "semantic_preferred_neighborhood": "repo_governance",
            "artifact_policy_status_line": (
                "artifacts_ready | strict=true install=present template=present"
            ),
            "admissibility_primary_status_line": (
                "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
            ),
            "requires_operator_action": False,
        },
    }

    assert healthcheck._extract_handoff_surface(payload) == {
        "queue_shape": "weekly_host_status",
        "primary_status_line": (
            "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
            "runtime_source=host_tick session=weekly-session resumed=yes"
        ),
        "runtime_status_line": (
            "host_tick | session=weekly-session resumed=yes next_cycle=4 "
            "failures=1 max_failure=1 tension=breached"
        ),
        "semantic_retrieval_protocol": (
            "alias_first -> neighborhood_before_file -> status_surface_before_source"
        ),
        "semantic_preferred_neighborhood": "repo_governance",
        "anchor_status_line": "",
        "artifact_policy_status_line": (
            "artifacts_ready | strict=true install=present template=present"
        ),
        "admissibility_primary_status_line": (
            "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
        ),
        "scribe_status_line": "",
        "requires_operator_action": "false",
    }


def test_select_handoff_preview_returns_matching_queue_shape() -> None:
    previews = [
        {
            "name": "subjectivity_report",
            "queue_shape": "stable_history_only",
            "primary_status_line": "stable_history_only | records=2",
            "runtime_status_line": "",
            "anchor_status_line": "",
            "artifact_policy_status_line": "",
            "requires_operator_action": "false",
        },
        {
            "name": "true_verification_weekly",
            "queue_shape": "weekly_host_status",
            "primary_status_line": "task_ready | scheduler=Ready",
            "runtime_status_line": "host_tick | session=weekly-session resumed=yes",
            "anchor_status_line": "",
            "artifact_policy_status_line": "",
            "admissibility_primary_status_line": (
                "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
            ),
            "requires_operator_action": "false",
        },
    ]

    assert healthcheck._select_handoff_preview(
        previews,
        queue_shape="weekly_host_status",
    ) == {
        "name": "true_verification_weekly",
        "queue_shape": "weekly_host_status",
        "primary_status_line": "task_ready | scheduler=Ready",
        "runtime_status_line": "host_tick | session=weekly-session resumed=yes",
        "anchor_status_line": "",
        "artifact_policy_status_line": "",
        "admissibility_primary_status_line": (
            "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
        ),
        "requires_operator_action": "false",
    }


def test_select_subjectivity_focus_preview_returns_first_admissibility_surface() -> None:
    previews = [
        {
            "name": "true_verification_weekly",
            "queue_shape": "weekly_host_status",
            "primary_status_line": "task_ready | scheduler=Ready",
            "runtime_status_line": "host_tick | session=weekly-session resumed=yes",
            "anchor_status_line": "",
            "artifact_policy_status_line": "",
            "requires_operator_action": "false",
        },
        {
            "name": "subjectivity_review_batch",
            "queue_shape": "subjectivity_review_ready",
            "primary_status_line": "review_ready | entries=2",
            "runtime_status_line": "review_batch | unresolved=1",
            "anchor_status_line": "",
            "artifact_policy_status_line": "artifacts_ready | strict=true",
            "admissibility_primary_status_line": (
                "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
            ),
            "requires_operator_action": "true",
        },
    ]

    assert healthcheck._select_subjectivity_focus_preview(previews) == {
        "name": "subjectivity_review_batch",
        "queue_shape": "subjectivity_review_ready",
        "primary_status_line": "review_ready | entries=2",
        "runtime_status_line": "review_batch | unresolved=1",
        "anchor_status_line": "",
        "artifact_policy_status_line": "artifacts_ready | strict=true",
        "admissibility_primary_status_line": (
            "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
        ),
        "requires_operator_action": "true",
    }


def test_render_markdown_contains_summary_and_failures() -> None:
    payload = {
        "generated_at": "2026-02-09T00:00:00Z",
        "overall_ok": False,
        "repo_intelligence_preview": {
            "name": "repo_intelligence",
            "queue_shape": "repo_intelligence_ready",
            "primary_status_line": (
                "repo_intelligence_ready | available_surfaces=5/5 "
                "protected_files=5 watched_dirs=3 adoption=sidecar_only"
            ),
            "runtime_status_line": (
                "entrypoints | repo=repo_healthcheck_latest.json "
                "settlement=repo_governance_settlement_latest.json "
                "review=runtime_source_change_groups_latest.json "
                "weekly=true_verification_task_status_latest.json "
                "scribe=scribe_status_latest.json"
            ),
            "semantic_retrieval_protocol": (
                "alias_first -> neighborhood_before_file -> status_surface_before_source"
            ),
            "semantic_preferred_neighborhood": "repo_governance",
            "artifact_policy_status_line": (
                "external_repo_intelligence=sidecar_only | "
                "main_repo_install=no hooks=no protected_files=no"
            ),
            "requires_operator_action": "false",
        },
        "handoff_previews": [
            {
                "name": "repo_intelligence",
                "queue_shape": "repo_intelligence_ready",
                "primary_status_line": (
                    "repo_intelligence_ready | available_surfaces=5/5 "
                    "protected_files=5 watched_dirs=3 adoption=sidecar_only"
                ),
                "runtime_status_line": (
                    "entrypoints | repo=repo_healthcheck_latest.json "
                    "settlement=repo_governance_settlement_latest.json "
                    "review=runtime_source_change_groups_latest.json "
                    "weekly=true_verification_task_status_latest.json "
                    "scribe=scribe_status_latest.json"
                ),
                "semantic_retrieval_protocol": (
                    "alias_first -> neighborhood_before_file -> status_surface_before_source"
                ),
                "semantic_preferred_neighborhood": "repo_governance",
                "artifact_policy_status_line": (
                    "external_repo_intelligence=sidecar_only | "
                    "main_repo_install=no hooks=no protected_files=no"
                ),
                "requires_operator_action": "false",
            },
            {
                "name": "true_verification_weekly",
                "queue_shape": "weekly_host_status",
                "primary_status_line": (
                    "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
                    "runtime_source=host_tick session=weekly-session resumed=yes"
                ),
                "runtime_status_line": (
                    "host_tick | session=weekly-session resumed=yes next_cycle=4 "
                    "failures=1 max_failure=1 tension=breached"
                ),
                "anchor_status_line": (
                    "anchor | [tension_afbd38eb] tension: High PE valuation in a market pullback..."
                ),
                "problem_route_status_line": (
                    "route | family=F1_grounding_evidence_integrity "
                    "invariant=observed_history_grounding "
                    "repair=anchor_and_boundary_guardrail"
                ),
                "problem_route_secondary_labels": (
                    "F6_semantic_role_boundary_integrity,F4_execution_contract_integrity"
                ),
                "artifact_policy_status_line": (
                    "artifacts_ready | strict=true install=present template=present"
                ),
                "admissibility_primary_status_line": (
                    "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
                ),
                "scribe_status_line": (
                    "scribe | status=generated mode=template_assist "
                    "posture=pressure_without_counterweight"
                ),
                "requires_operator_action": "false",
            },
        ],
        "weekly_host_status_preview": {
            "name": "true_verification_weekly",
            "queue_shape": "weekly_host_status",
            "primary_status_line": (
                "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
                "runtime_source=host_tick session=weekly-session resumed=yes"
            ),
            "runtime_status_line": (
                "host_tick | session=weekly-session resumed=yes next_cycle=4 "
                "failures=1 max_failure=1 tension=breached"
            ),
            "anchor_status_line": (
                "anchor | [tension_afbd38eb] tension: High PE valuation in a market pullback..."
            ),
            "problem_route_status_line": (
                "route | family=F1_grounding_evidence_integrity "
                "invariant=observed_history_grounding "
                "repair=anchor_and_boundary_guardrail"
            ),
            "problem_route_secondary_labels": (
                "F6_semantic_role_boundary_integrity,F4_execution_contract_integrity"
            ),
            "artifact_policy_status_line": (
                "artifacts_ready | strict=true install=present template=present"
            ),
            "admissibility_primary_status_line": (
                "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
            ),
            "scribe_status_line": (
                "scribe | status=generated mode=template_assist "
                "posture=pressure_without_counterweight"
            ),
            "requires_operator_action": "false",
        },
        "subjectivity_focus_preview": {
            "name": "true_verification_weekly",
            "queue_shape": "weekly_host_status",
            "primary_status_line": (
                "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
                "runtime_source=host_tick session=weekly-session resumed=yes"
            ),
            "runtime_status_line": (
                "host_tick | session=weekly-session resumed=yes next_cycle=4 "
                "failures=1 max_failure=1 tension=breached"
            ),
            "anchor_status_line": (
                "anchor | [tension_afbd38eb] tension: High PE valuation in a market pullback..."
            ),
            "problem_route_status_line": (
                "route | family=F1_grounding_evidence_integrity "
                "invariant=observed_history_grounding "
                "repair=anchor_and_boundary_guardrail"
            ),
            "problem_route_secondary_labels": (
                "F6_semantic_role_boundary_integrity,F4_execution_contract_integrity"
            ),
            "dream_weekly_alignment_line": (
                "dream_weekly_alignment | alignment=aligned "
                "weekly=F1_grounding_evidence_integrity "
                "dream=F1_grounding_evidence_integrity"
            ),
            "artifact_policy_status_line": (
                "artifacts_ready | strict=true install=present template=present"
            ),
            "admissibility_primary_status_line": (
                "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
            ),
            "scribe_status_line": (
                "scribe | status=generated mode=template_assist "
                "posture=pressure_without_counterweight"
            ),
            "requires_operator_action": "false",
        },
        "scribe_status_preview": {
            "name": "scribe_status",
            "path": "docs/status/scribe_status_latest.json",
            "queue_shape": "scribe_chronicle_ready",
            "primary_status_line": (
                "generated | mode=template_assist model=gemma3:4b "
                "fallback_mode=observed_history attempts=3 latest=chronicle_pair"
            ),
            "runtime_status_line": (
                "state_document | tensions=1 collisions=0 crystals=0 "
                "posture=pressure_without_counterweight"
            ),
            "anchor_status_line": (
                "anchor | [tension_afbd38eb] tension: High PE valuation in a market pullback..."
            ),
            "problem_route_status_line": (
                "route | family=F1_grounding_evidence_integrity "
                "invariant=observed_history_grounding "
                "repair=anchor_and_boundary_guardrail"
            ),
            "problem_route_secondary_labels": (
                "F6_semantic_role_boundary_integrity,F4_execution_contract_integrity"
            ),
            "artifact_policy_status_line": (
                "artifact_source=chronicle_pair | chronicle=yes companion=yes"
            ),
            "requires_operator_action": "false",
        },
        "checks": [
            {
                "name": "python_lint",
                "status": "pass",
                "exit_code": 0,
                "duration_seconds": 1.23,
                "command": "python -m ruff check tonesoul tests scripts",
            },
            {
                "name": "audit_7d",
                "status": "fail",
                "exit_code": 1,
                "duration_seconds": 2.34,
                "command": "python scripts/verify_7d.py",
                "stdout_tail": "",
                "stderr_tail": "blocking failure",
            },
            {
                "name": "audit_7d_ci",
                "status": "skip",
                "exit_code": None,
                "duration_seconds": 0.0,
                "command": "python scripts/verify_7d.py",
                "skip_reason": "missing discussion file: memory/agent_discussion_curated.jsonl",
            },
        ],
        "recovery_advice": [
            {
                "name": "commit_attribution_recovery",
                "status": "pass",
                "detail": {
                    "recommendation": "defer_until_worktree_clean",
                    "rationale": "worktree dirty",
                    "suggested_commands": [
                        "git worktree add <clean-path> feat/env-perception-attribution-backfill"
                    ],
                },
            }
        ],
    }

    markdown = healthcheck._render_markdown(payload)
    assert "# Repo Healthcheck Latest" in markdown
    assert "- overall_ok: false" in markdown
    assert "- handoff_preview_count: 2" in markdown
    assert "- repo_intelligence:" in markdown
    assert "- repo_intelligence_entrypoints:" in markdown
    assert "- repo_intelligence_semantic_protocol:" in markdown
    assert "- repo_intelligence_first_neighborhood:" in markdown
    assert "- weekly_host_status:" in markdown
    assert "- weekly_runtime_posture:" in markdown
    assert "- weekly_anchor_posture:" in markdown
    assert "- weekly_problem_route:" in markdown
    assert "- weekly_problem_route_secondary:" in markdown
    assert "- weekly_scribe_posture:" in markdown
    assert "- subjectivity_focus:" in markdown
    assert "- subjectivity_runtime_posture:" in markdown
    assert "- subjectivity_scribe_posture:" in markdown
    assert "- subjectivity_anchor_posture:" in markdown
    assert "- subjectivity_problem_route:" in markdown
    assert "- subjectivity_problem_route_secondary:" in markdown
    assert "- subjectivity_alignment:" in markdown
    assert "- subjectivity_artifact_policy:" in markdown
    assert "- subjectivity_admissibility:" in markdown
    assert "- scribe_state_document:" in markdown
    assert "- scribe_state_posture:" in markdown
    assert "- scribe_lead_anchor:" in markdown
    assert "- scribe_problem_route:" in markdown
    assert "- scribe_problem_route_secondary:" in markdown
    assert "- scribe_artifact_policy:" in markdown
    assert "## Handoff Previews" in markdown
    assert "## Subjectivity Focus Mirror" in markdown
    assert "## Repo Intelligence Mirror" in markdown
    assert "`repo_intelligence` (`repo_intelligence_ready`):" in markdown
    assert "`true_verification_weekly` (`weekly_host_status`):" in markdown
    assert "runtime_status_line" in markdown
    assert "semantic_retrieval_protocol" in markdown
    assert "semantic_preferred_neighborhood" in markdown
    assert "anchor_status_line" in markdown
    assert "problem_route_status_line" in markdown
    assert "problem_route_secondary_labels" in markdown
    assert "artifact_policy_status_line" in markdown
    assert "scribe_status_line" in markdown
    assert "admissibility_primary_status_line" in markdown
    assert "requires_operator_action" in markdown
    assert (
        "| python_lint | PASS | 0 | 1.23 | `python -m ruff check tonesoul tests scripts` |"
        in markdown
    )
    assert "## Failures" in markdown
    assert "`audit_7d`: blocking failure" in markdown
    assert "## Skipped" in markdown
    assert "missing discussion file: memory/agent_discussion_curated.jsonl" in markdown
    assert "## Recovery Advice" in markdown
    assert "`commit_attribution_recovery`: defer_until_worktree_clean" in markdown
    assert "git worktree add <clean-path> feat/env-perception-attribution-backfill" in markdown


def test_main_mirrors_weekly_host_status_preview_from_structured_check(
    monkeypatch,
    tmp_path: Path,
) -> None:
    weekly_payload = {
        "overall_ok": True,
        "primary_status_line": (
            "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
            "runtime_source=host_tick session=weekly-session resumed=yes"
        ),
        "runtime_status_line": (
            "host_tick | session=weekly-session resumed=yes next_cycle=4 "
            "failures=1 max_failure=1 tension=breached"
        ),
        "anchor_status_line": (
            "anchor | [tension_afbd38eb] tension: High PE valuation in a market pullback..."
        ),
        "problem_route_status_line": (
            "route | family=F1_grounding_evidence_integrity "
            "invariant=observed_history_grounding "
            "repair=anchor_and_boundary_guardrail"
        ),
        "problem_route_secondary_labels": (
            "F6_semantic_role_boundary_integrity,F4_execution_contract_integrity"
        ),
        "dream_weekly_alignment_line": (
            "dream_weekly_alignment | alignment=aligned "
            "weekly=F1_grounding_evidence_integrity "
            "dream=F1_grounding_evidence_integrity"
        ),
        "artifact_policy_status_line": (
            "artifacts_ready | strict=true install=present template=present"
        ),
        "admissibility_primary_status_line": (
            "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
        ),
        "scribe_status_line": (
            "scribe | status=generated mode=template_assist "
            "posture=pressure_without_counterweight"
        ),
        "handoff": {
            "queue_shape": "weekly_host_status",
            "primary_status_line": (
                "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
                "runtime_source=host_tick session=weekly-session resumed=yes"
            ),
            "requires_operator_action": False,
        },
    }

    monkeypatch.setattr(
        healthcheck,
        "_build_check_specs",
        lambda **kwargs: [
            {
                "name": "true_verification_weekly",
                "command": [
                    "python",
                    "scripts/report_true_verification_task_status.py",
                    "--strict",
                ],
                "structured_output": "json",
            },
            {
                "name": "python_lint",
                "command": ["python", "-m", "ruff", "check", "tonesoul"],
            },
        ],
    )
    monkeypatch.setattr(
        healthcheck,
        "_run_json_command",
        lambda name, command, cwd: (
            {
                "name": name,
                "status": "pass",
                "ok": True,
                "exit_code": 0,
                "duration_seconds": 0.12,
                "command": "python scripts/report_true_verification_task_status.py --strict",
                "stdout_tail": json.dumps(weekly_payload, ensure_ascii=False),
                "stderr_tail": "",
            },
            weekly_payload,
        ),
    )
    monkeypatch.setattr(
        healthcheck,
        "_run_check",
        lambda name, command, cwd: {
            "name": name,
            "status": "pass",
            "ok": True,
            "exit_code": 0,
            "duration_seconds": 0.05,
            "command": "python -m ruff check tonesoul",
            "stdout_tail": "",
            "stderr_tail": "",
        },
    )
    monkeypatch.setattr(healthcheck, "_collect_recovery_advice", lambda **kwargs: [])
    monkeypatch.setattr(healthcheck, "_emit", lambda payload: None)
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_repo_healthcheck.py",
            "--repo-root",
            str(tmp_path),
            "--out-dir",
            str(out_dir),
        ],
    )

    exit_code = healthcheck.main()

    assert exit_code == 0
    saved = json.loads((out_dir / healthcheck.JSON_FILENAME).read_text(encoding="utf-8"))
    assert saved["handoff_previews"] == [
        {
            "name": "true_verification_weekly",
            "queue_shape": "weekly_host_status",
            "primary_status_line": weekly_payload["primary_status_line"],
            "runtime_status_line": weekly_payload["runtime_status_line"],
            "anchor_status_line": weekly_payload["anchor_status_line"],
            "problem_route_status_line": weekly_payload["problem_route_status_line"],
            "problem_route_secondary_labels": weekly_payload["problem_route_secondary_labels"],
            "dream_weekly_alignment_line": weekly_payload["dream_weekly_alignment_line"],
            "artifact_policy_status_line": weekly_payload["artifact_policy_status_line"],
            "admissibility_primary_status_line": weekly_payload[
                "admissibility_primary_status_line"
            ],
            "scribe_status_line": weekly_payload["scribe_status_line"],
            "requires_operator_action": "false",
        }
    ]
    assert saved["weekly_host_status_preview"] == saved["handoff_previews"][0]
    assert saved["subjectivity_focus_preview"] == saved["handoff_previews"][0]
    assert saved["dream_weekly_alignment_line"] == weekly_payload["dream_weekly_alignment_line"]
    markdown = (out_dir / healthcheck.MARKDOWN_FILENAME).read_text(encoding="utf-8")
    assert "weekly_host_status" in markdown
    assert "weekly_runtime_posture" in markdown
    assert "weekly_anchor_posture" in markdown
    assert "weekly_problem_route" in markdown
    assert "weekly_problem_route_secondary" in markdown
    assert "weekly_artifact_policy" in markdown
    assert "weekly_admissibility" in markdown
    assert "weekly_scribe_posture" in markdown
    assert "subjectivity_focus" in markdown
    assert "subjectivity_admissibility" in markdown
    assert "## Weekly Host Status Mirror" in markdown
    assert "true_verification_weekly" in markdown
    assert "admissibility_primary_status_line" in markdown
    assert "## Subjectivity Focus Mirror" in markdown
    assert "dream_weekly_alignment" in markdown
    assert "requires_operator_action" in markdown


def test_main_mirrors_repo_intelligence_preview_from_structured_check(
    monkeypatch,
    tmp_path: Path,
) -> None:
    intelligence_payload = {
        "status": "ready",
        "primary_status_line": (
            "repo_intelligence_ready | available_surfaces=5/5 "
            "protected_files=5 watched_dirs=3 adoption=sidecar_only"
        ),
        "runtime_status_line": (
            "entrypoints | repo=repo_healthcheck_latest.json "
            "settlement=repo_governance_settlement_latest.json "
            "review=runtime_source_change_groups_latest.json "
            "weekly=true_verification_task_status_latest.json "
            "scribe=scribe_status_latest.json"
        ),
        "artifact_policy_status_line": (
            "external_repo_intelligence=sidecar_only | "
            "main_repo_install=no hooks=no protected_files=no"
        ),
        "semantic_retrieval_protocol": (
            "alias_first -> neighborhood_before_file -> status_surface_before_source"
        ),
        "semantic_preferred_neighborhood": "repo_governance",
        "handoff": {
            "queue_shape": "repo_intelligence_ready",
            "primary_status_line": (
                "repo_intelligence_ready | available_surfaces=5/5 "
                "protected_files=5 watched_dirs=3 adoption=sidecar_only"
            ),
            "requires_operator_action": False,
        },
    }

    monkeypatch.setattr(
        healthcheck,
        "_build_check_specs",
        lambda **kwargs: [
            {
                "name": "repo_intelligence",
                "command": ["python", "scripts/run_repo_intelligence_report.py"],
                "structured_output": "json",
            },
            {
                "name": "python_lint",
                "command": ["python", "-m", "ruff", "check", "tonesoul"],
            },
        ],
    )
    monkeypatch.setattr(
        healthcheck,
        "_run_json_command",
        lambda name, command, cwd: (
            {
                "name": name,
                "status": "pass",
                "ok": True,
                "exit_code": 0,
                "duration_seconds": 0.08,
                "command": "python scripts/run_repo_intelligence_report.py",
                "stdout_tail": json.dumps(intelligence_payload, ensure_ascii=False),
                "stderr_tail": "",
            },
            intelligence_payload,
        ),
    )
    monkeypatch.setattr(
        healthcheck,
        "_run_check",
        lambda name, command, cwd: {
            "name": name,
            "status": "pass",
            "ok": True,
            "exit_code": 0,
            "duration_seconds": 0.05,
            "command": "python -m ruff check tonesoul",
            "stdout_tail": "",
            "stderr_tail": "",
        },
    )
    monkeypatch.setattr(healthcheck, "_collect_recovery_advice", lambda **kwargs: [])
    monkeypatch.setattr(healthcheck, "_emit", lambda payload: None)
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_repo_healthcheck.py",
            "--repo-root",
            str(tmp_path),
            "--out-dir",
            str(out_dir),
        ],
    )

    exit_code = healthcheck.main()

    assert exit_code == 0
    saved = json.loads((out_dir / healthcheck.JSON_FILENAME).read_text(encoding="utf-8"))
    assert saved["repo_intelligence_preview"] == {
        "name": "repo_intelligence",
        "queue_shape": "repo_intelligence_ready",
        "primary_status_line": intelligence_payload["primary_status_line"],
        "runtime_status_line": intelligence_payload["runtime_status_line"],
        "anchor_status_line": "",
        "artifact_policy_status_line": intelligence_payload["artifact_policy_status_line"],
        "semantic_retrieval_protocol": intelligence_payload["semantic_retrieval_protocol"],
        "semantic_preferred_neighborhood": intelligence_payload["semantic_preferred_neighborhood"],
        "requires_operator_action": "false",
    }
    markdown = (out_dir / healthcheck.MARKDOWN_FILENAME).read_text(encoding="utf-8")
    assert "repo_intelligence" in markdown
    assert "repo_intelligence_entrypoints" in markdown
    assert "repo_intelligence_semantic_protocol" in markdown
    assert "repo_intelligence_first_neighborhood" in markdown
    assert "## Repo Intelligence Mirror" in markdown


def test_main_mirrors_repo_semantic_atlas_preview_from_existing_status_artifact(
    monkeypatch,
    tmp_path: Path,
) -> None:
    atlas_payload = {
        "primary_status_line": (
            "repo_semantic_atlas_ready | aliases=7 neighborhoods=6 chronicles=19 "
            "doc_threads=431 rules=8 graph_edges=7"
        ),
        "runtime_status_line": (
            "entrypoints | atlas=repo_semantic_atlas_latest.json "
            "repo=repo_healthcheck_latest.json dream=dream_observability_latest.json "
            "weekly=true_verification_task_status_latest.json scribe=scribe_status_latest.json "
            "protocol=alias_first"
        ),
        "artifact_policy_status_line": (
            "semantic_map=domain_level | aliases=source_declared "
            "graph=passive_no_reparse protocol=backend_agnostic"
        ),
        "handoff": {
            "queue_shape": "repo_semantic_atlas_ready",
            "primary_status_line": (
                "repo_semantic_atlas_ready | aliases=7 neighborhoods=6 chronicles=19 "
                "doc_threads=431 rules=8 graph_edges=7"
            ),
            "requires_operator_action": False,
        },
    }
    artifact_path = tmp_path / "docs" / "status" / "repo_semantic_atlas_latest.json"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        json.dumps(atlas_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        healthcheck,
        "_build_check_specs",
        lambda **kwargs: [
            {
                "name": "python_lint",
                "command": ["python", "-m", "ruff", "check", "tonesoul"],
            },
        ],
    )
    monkeypatch.setattr(
        healthcheck,
        "_run_check",
        lambda name, command, cwd: {
            "name": name,
            "status": "pass",
            "ok": True,
            "exit_code": 0,
            "duration_seconds": 0.05,
            "command": "python -m ruff check tonesoul",
            "stdout_tail": "",
            "stderr_tail": "",
        },
    )
    monkeypatch.setattr(healthcheck, "_collect_recovery_advice", lambda **kwargs: [])
    monkeypatch.setattr(healthcheck, "_emit", lambda payload: None)
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_repo_healthcheck.py",
            "--repo-root",
            str(tmp_path),
            "--out-dir",
            str(out_dir),
        ],
    )

    exit_code = healthcheck.main()

    assert exit_code == 0
    saved = json.loads((out_dir / healthcheck.JSON_FILENAME).read_text(encoding="utf-8"))
    assert saved["repo_semantic_atlas_preview"] == {
        "name": "repo_semantic_atlas",
        "path": "docs/status/repo_semantic_atlas_latest.json",
        "queue_shape": "repo_semantic_atlas_ready",
        "primary_status_line": atlas_payload["primary_status_line"],
        "runtime_status_line": atlas_payload["runtime_status_line"],
        "anchor_status_line": "",
        "artifact_policy_status_line": atlas_payload["artifact_policy_status_line"],
        "requires_operator_action": "false",
    }
    markdown = (out_dir / healthcheck.MARKDOWN_FILENAME).read_text(encoding="utf-8")
    assert "repo_semantic_atlas" in markdown
    assert "repo_semantic_protocol" in markdown
    assert "repo_semantic_artifact_policy" in markdown
    assert "## Repo Semantic Atlas Mirror" in markdown


def test_main_mirrors_dream_observability_preview_from_existing_status_artifact(
    monkeypatch,
    tmp_path: Path,
) -> None:
    dream_payload = {
        "primary_status_line": (
            "dream_observability_ready | cycles=8 collisions=3 councils=3 " "scribe=generated"
        ),
        "runtime_status_line": (
            "wakeup_dashboard | session=wakeup-session resumed=yes "
            "posture=pressure_without_counterweight"
        ),
        "anchor_status_line": "anchor | [T1] tension: observed grounding...",
        "problem_route_status_line": (
            "route | family=F6_semantic_role_boundary_integrity "
            "invariant=chronicle_self_scope "
            "repair=semantic_boundary_guardrail"
        ),
        "problem_route_secondary_labels": (
            "F4_execution_contract_integrity,F7_representation_localization_integrity"
        ),
        "artifact_policy_status_line": (
            "dashboard_artifacts_ready | html=yes json=yes recent_rows=8"
        ),
        "handoff": {
            "queue_shape": "dream_observability_ready",
            "primary_status_line": (
                "dream_observability_ready | cycles=8 collisions=3 councils=3 " "scribe=generated"
            ),
            "requires_operator_action": False,
        },
    }
    artifact_path = tmp_path / "docs" / "status" / "dream_observability_latest.json"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        json.dumps(dream_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        healthcheck,
        "_build_check_specs",
        lambda **kwargs: [
            {
                "name": "python_lint",
                "command": ["python", "-m", "ruff", "check", "tonesoul"],
            },
        ],
    )
    monkeypatch.setattr(
        healthcheck,
        "_run_check",
        lambda name, command, cwd: {
            "name": name,
            "status": "pass",
            "ok": True,
            "exit_code": 0,
            "duration_seconds": 0.05,
            "command": "python -m ruff check tonesoul",
            "stdout_tail": "",
            "stderr_tail": "",
        },
    )
    monkeypatch.setattr(healthcheck, "_collect_recovery_advice", lambda **kwargs: [])
    monkeypatch.setattr(healthcheck, "_emit", lambda payload: None)
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_repo_healthcheck.py",
            "--repo-root",
            str(tmp_path),
            "--out-dir",
            str(out_dir),
        ],
    )

    exit_code = healthcheck.main()

    assert exit_code == 0
    saved = json.loads((out_dir / healthcheck.JSON_FILENAME).read_text(encoding="utf-8"))
    assert saved["dream_observability_preview"] == {
        "name": "dream_observability",
        "path": "docs/status/dream_observability_latest.json",
        "queue_shape": "dream_observability_ready",
        "primary_status_line": dream_payload["primary_status_line"],
        "runtime_status_line": dream_payload["runtime_status_line"],
        "anchor_status_line": dream_payload["anchor_status_line"],
        "problem_route_status_line": dream_payload["problem_route_status_line"],
        "problem_route_secondary_labels": dream_payload["problem_route_secondary_labels"],
        "artifact_policy_status_line": dream_payload["artifact_policy_status_line"],
        "requires_operator_action": "false",
    }
    markdown = (out_dir / healthcheck.MARKDOWN_FILENAME).read_text(encoding="utf-8")
    assert "dream_observability" in markdown
    assert "dream_runtime_posture" in markdown
    assert "dream_anchor_posture" in markdown
    assert "dream_problem_route" in markdown
    assert "dream_problem_route_secondary" in markdown
    assert "dream_artifact_policy" in markdown


def test_main_backfills_subjectivity_focus_preview_from_passive_status_artifact(
    monkeypatch,
    tmp_path: Path,
) -> None:
    subjectivity_payload = {
        "primary_status_line": (
            "stable_deferred_history | rows=50 lineages=12 cycles=30 "
            "trigger=second_source_context_or_material_split"
        ),
        "runtime_status_line": "history_density | rows_per_lineage=4.2 rows_per_cycle=1.7",
        "anchor_status_line": "anchor | [subjectivity_tension_a1] tension: authority pressure...",
        "problem_route_status_line": (
            "route | family=F1_grounding_evidence_integrity "
            "invariant=second_source_context_missing "
            "repair=subjectivity_review_batch"
        ),
        "problem_route_secondary_labels": "F6_semantic_role_boundary_integrity",
        "artifact_policy_status_line": (
            "review_batch_artifacts_ready | strict=true markdown=yes json=yes"
        ),
        "admissibility_primary_status_line": (
            "admissibility_not_yet_clear | focus=authority_and_exception_pressure"
        ),
        "handoff": {
            "queue_shape": "stable_history_only",
            "primary_status_line": (
                "stable_deferred_history | rows=50 lineages=12 cycles=30 "
                "trigger=second_source_context_or_material_split"
            ),
            "requires_operator_action": False,
        },
    }
    artifact_path = tmp_path / "docs" / "status" / "subjectivity_review_batch_latest.json"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        json.dumps(subjectivity_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        healthcheck,
        "_build_check_specs",
        lambda **kwargs: [
            {
                "name": "python_lint",
                "command": ["python", "-m", "ruff", "check", "tonesoul"],
            },
        ],
    )
    monkeypatch.setattr(
        healthcheck,
        "_run_check",
        lambda name, command, cwd: {
            "name": name,
            "status": "pass",
            "ok": True,
            "exit_code": 0,
            "duration_seconds": 0.05,
            "command": "python -m ruff check tonesoul",
            "stdout_tail": "",
            "stderr_tail": "",
        },
    )
    monkeypatch.setattr(healthcheck, "_collect_recovery_advice", lambda **kwargs: [])
    monkeypatch.setattr(healthcheck, "_emit", lambda payload: None)
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_repo_healthcheck.py",
            "--repo-root",
            str(tmp_path),
            "--out-dir",
            str(out_dir),
        ],
    )

    exit_code = healthcheck.main()

    assert exit_code == 0
    saved = json.loads((out_dir / healthcheck.JSON_FILENAME).read_text(encoding="utf-8"))
    assert saved["subjectivity_focus_preview"] == {
        "name": "subjectivity_review_batch",
        "path": "docs/status/subjectivity_review_batch_latest.json",
        "queue_shape": "stable_history_only",
        "primary_status_line": subjectivity_payload["primary_status_line"],
        "runtime_status_line": subjectivity_payload["runtime_status_line"],
        "anchor_status_line": subjectivity_payload["anchor_status_line"],
        "problem_route_status_line": subjectivity_payload["problem_route_status_line"],
        "problem_route_secondary_labels": subjectivity_payload["problem_route_secondary_labels"],
        "artifact_policy_status_line": subjectivity_payload["artifact_policy_status_line"],
        "admissibility_primary_status_line": (
            subjectivity_payload["admissibility_primary_status_line"]
        ),
        "requires_operator_action": "false",
    }
    markdown = (out_dir / healthcheck.MARKDOWN_FILENAME).read_text(encoding="utf-8")
    assert "subjectivity_focus" in markdown
    assert "subjectivity_admissibility" in markdown
    assert "## Subjectivity Focus Mirror" in markdown
    assert "docs/status/subjectivity_review_batch_latest.json" in markdown


def test_main_surfaces_dream_weekly_alignment_line(
    monkeypatch,
    tmp_path: Path,
) -> None:
    weekly_payload = {
        "primary_status_line": (
            "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
            "runtime_source=host_tick session=weekly-session resumed=yes"
        ),
        "runtime_status_line": (
            "host_tick | session=weekly-session resumed=yes next_cycle=4 "
            "failures=1 max_failure=1 tension=breached"
        ),
        "problem_route_status_line": (
            "route | family=F6_semantic_role_boundary_integrity "
            "invariant=chronicle_self_scope "
            "repair=semantic_boundary_guardrail"
        ),
        "problem_route_secondary_labels": (
            "F4_execution_contract_integrity,F7_representation_localization_integrity"
        ),
        "handoff": {
            "queue_shape": "weekly_host_status",
            "primary_status_line": (
                "task_ready | scheduler=Ready registered=yes host_trigger_mode=single_tick "
                "runtime_source=host_tick session=weekly-session resumed=yes"
            ),
            "requires_operator_action": False,
        },
    }
    dream_payload = {
        "primary_status_line": (
            "dream_observability_ready | cycles=8 collisions=3 councils=3 " "scribe=generated"
        ),
        "runtime_status_line": (
            "wakeup_dashboard | session=wakeup-session resumed=yes "
            "posture=pressure_without_counterweight"
        ),
        "problem_route_status_line": (
            "route | family=F6_semantic_role_boundary_integrity "
            "invariant=chronicle_self_scope "
            "repair=semantic_boundary_guardrail"
        ),
        "problem_route_secondary_labels": (
            "F4_execution_contract_integrity,F7_representation_localization_integrity"
        ),
        "artifact_policy_status_line": (
            "dashboard_artifacts_ready | html=yes json=yes recent_rows=8"
        ),
        "handoff": {
            "queue_shape": "dream_observability_ready",
            "primary_status_line": (
                "dream_observability_ready | cycles=8 collisions=3 councils=3 " "scribe=generated"
            ),
            "requires_operator_action": False,
        },
    }
    artifact_path = tmp_path / "docs" / "status" / "dream_observability_latest.json"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        json.dumps(dream_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        healthcheck,
        "_build_check_specs",
        lambda **kwargs: [
            {
                "name": "true_verification_weekly",
                "command": [
                    "python",
                    "scripts/report_true_verification_task_status.py",
                    "--strict",
                ],
                "structured_output": "json",
            },
            {
                "name": "python_lint",
                "command": ["python", "-m", "ruff", "check", "tonesoul"],
            },
        ],
    )
    monkeypatch.setattr(
        healthcheck,
        "_run_json_command",
        lambda name, command, cwd: (
            {
                "name": name,
                "status": "pass",
                "ok": True,
                "exit_code": 0,
                "duration_seconds": 0.12,
                "command": "python scripts/report_true_verification_task_status.py --strict",
                "stdout_tail": json.dumps(weekly_payload, ensure_ascii=False),
                "stderr_tail": "",
            },
            weekly_payload,
        ),
    )
    monkeypatch.setattr(
        healthcheck,
        "_run_check",
        lambda name, command, cwd: {
            "name": name,
            "status": "pass",
            "ok": True,
            "exit_code": 0,
            "duration_seconds": 0.05,
            "command": "python -m ruff check tonesoul",
            "stdout_tail": "",
            "stderr_tail": "",
        },
    )
    monkeypatch.setattr(healthcheck, "_collect_recovery_advice", lambda **kwargs: [])
    monkeypatch.setattr(healthcheck, "_emit", lambda payload: None)
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_repo_healthcheck.py",
            "--repo-root",
            str(tmp_path),
            "--out-dir",
            str(out_dir),
        ],
    )

    exit_code = healthcheck.main()

    assert exit_code == 0
    saved = json.loads((out_dir / healthcheck.JSON_FILENAME).read_text(encoding="utf-8"))
    assert saved["dream_weekly_alignment_line"] == (
        "dream_weekly_alignment | alignment=aligned "
        "weekly=F6_semantic_role_boundary_integrity "
        "dream=F6_semantic_role_boundary_integrity "
        "shared_secondary=F4_execution_contract_integrity,F7_representation_localization_integrity"
    )
    markdown = (out_dir / healthcheck.MARKDOWN_FILENAME).read_text(encoding="utf-8")
    assert "dream_weekly_alignment" in markdown
    assert "alignment=aligned" in markdown


def test_main_mirrors_scribe_status_preview_from_existing_status_artifact(
    monkeypatch,
    tmp_path: Path,
) -> None:
    scribe_payload = {
        "status": "generated",
        "primary_status_line": (
            "generated | mode=template_assist model=gemma3:4b "
            "fallback_mode=observed_history attempts=3 latest=chronicle_pair"
        ),
        "runtime_status_line": (
            "state_document | tensions=1 collisions=0 crystals=0 "
            "posture=pressure_without_counterweight"
        ),
        "anchor_status_line": (
            "anchor | [tension_afbd38eb] tension: High PE valuation in a market pullback..."
        ),
        "problem_route_status_line": (
            "route | family=F1_grounding_evidence_integrity "
            "invariant=observed_history_grounding "
            "repair=anchor_and_boundary_guardrail"
        ),
        "problem_route_secondary_labels": (
            "F6_semantic_role_boundary_integrity,F4_execution_contract_integrity"
        ),
        "artifact_policy_status_line": (
            "artifact_source=chronicle_pair | chronicle=yes companion=yes"
        ),
        "handoff": {
            "queue_shape": "scribe_chronicle_ready",
            "primary_status_line": (
                "generated | mode=template_assist model=gemma3:4b "
                "fallback_mode=observed_history attempts=3 latest=chronicle_pair"
            ),
            "requires_operator_action": False,
        },
    }
    artifact_path = tmp_path / "docs" / "status" / "scribe_status_latest.json"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        json.dumps(scribe_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        healthcheck,
        "_build_check_specs",
        lambda **kwargs: [
            {
                "name": "python_lint",
                "command": ["python", "-m", "ruff", "check", "tonesoul"],
            },
        ],
    )
    monkeypatch.setattr(
        healthcheck,
        "_run_check",
        lambda name, command, cwd: {
            "name": name,
            "status": "pass",
            "ok": True,
            "exit_code": 0,
            "duration_seconds": 0.05,
            "command": "python -m ruff check tonesoul",
            "stdout_tail": "",
            "stderr_tail": "",
        },
    )
    monkeypatch.setattr(healthcheck, "_collect_recovery_advice", lambda **kwargs: [])
    monkeypatch.setattr(healthcheck, "_emit", lambda payload: None)
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_repo_healthcheck.py",
            "--repo-root",
            str(tmp_path),
            "--out-dir",
            str(out_dir),
        ],
    )

    exit_code = healthcheck.main()

    assert exit_code == 0
    saved = json.loads((out_dir / healthcheck.JSON_FILENAME).read_text(encoding="utf-8"))
    assert saved["handoff_previews"] == []
    assert saved["scribe_status_preview"] == {
        "name": "scribe_status",
        "path": "docs/status/scribe_status_latest.json",
        "queue_shape": "scribe_chronicle_ready",
        "primary_status_line": scribe_payload["primary_status_line"],
        "runtime_status_line": scribe_payload["runtime_status_line"],
        "anchor_status_line": scribe_payload["anchor_status_line"],
        "problem_route_status_line": scribe_payload["problem_route_status_line"],
        "problem_route_secondary_labels": scribe_payload["problem_route_secondary_labels"],
        "artifact_policy_status_line": scribe_payload["artifact_policy_status_line"],
        "requires_operator_action": "false",
    }
    markdown = (out_dir / healthcheck.MARKDOWN_FILENAME).read_text(encoding="utf-8")
    assert "scribe_state_document" in markdown
    assert "scribe_state_posture" in markdown
    assert "scribe_lead_anchor" in markdown
    assert "scribe_problem_route_secondary" in markdown
    assert "scribe_artifact_policy" in markdown


def test_main_mirrors_agent_integrity_preview_from_existing_status_artifact(
    monkeypatch,
    tmp_path: Path,
) -> None:
    integrity_payload = {
        "status": "warning",
        "primary_status_line": (
            "agent_integrity_warning | errors=0 warnings=1 " "review_dirs=2 protected_files=3"
        ),
        "runtime_status_line": (
            "integrity_contract | contract=agent_integrity_contract.py "
            "checker=check_agent_integrity.py workflow=agent-integrity-check.yml"
        ),
        "problem_route_status_line": (
            "integrity | family=G1_integrity_contract_drift "
            "invariant=embedded_expected_hash_metadata "
            "repair=protected_file_documentation"
        ),
        "artifact_policy_status_line": (
            "protected_hashes=blocking | hidden_chars=blocking | "
            "embedded_metadata=warning | watched_dirs=review_only"
        ),
        "handoff": {
            "queue_shape": "agent_integrity_guarded",
            "primary_status_line": (
                "agent_integrity_warning | errors=0 warnings=1 " "review_dirs=2 protected_files=3"
            ),
            "requires_operator_action": False,
        },
    }
    artifact_path = tmp_path / "docs" / "status" / "agent_integrity_latest.json"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        json.dumps(integrity_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        healthcheck,
        "_build_check_specs",
        lambda **kwargs: [
            {
                "name": "python_lint",
                "command": ["python", "-m", "ruff", "check", "tonesoul"],
            },
        ],
    )
    monkeypatch.setattr(
        healthcheck,
        "_run_check",
        lambda name, command, cwd: {
            "name": name,
            "status": "pass",
            "ok": True,
            "exit_code": 0,
            "duration_seconds": 0.05,
            "command": "python -m ruff check tonesoul",
            "stdout_tail": "",
            "stderr_tail": "",
        },
    )
    monkeypatch.setattr(healthcheck, "_collect_recovery_advice", lambda **kwargs: [])
    monkeypatch.setattr(healthcheck, "_emit", lambda payload: None)
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_repo_healthcheck.py",
            "--repo-root",
            str(tmp_path),
            "--out-dir",
            str(out_dir),
        ],
    )

    exit_code = healthcheck.main()

    assert exit_code == 0
    saved = json.loads((out_dir / healthcheck.JSON_FILENAME).read_text(encoding="utf-8"))
    assert saved["agent_integrity_preview"] == {
        "name": "agent_integrity",
        "path": "docs/status/agent_integrity_latest.json",
        "queue_shape": "agent_integrity_guarded",
        "primary_status_line": integrity_payload["primary_status_line"],
        "runtime_status_line": integrity_payload["runtime_status_line"],
        "anchor_status_line": "",
        "problem_route_status_line": integrity_payload["problem_route_status_line"],
        "artifact_policy_status_line": integrity_payload["artifact_policy_status_line"],
        "requires_operator_action": "false",
    }
    markdown = (out_dir / healthcheck.MARKDOWN_FILENAME).read_text(encoding="utf-8")
    assert "agent_integrity" in markdown
    assert "agent_integrity_problem_route" in markdown
    assert "## Agent Integrity Mirror" in markdown
