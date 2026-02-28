from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

WORKFLOW_PATH = Path(".github/workflows/repo_healthcheck.yml")
DISPATCH_SCRIPT_PATH = Path("scripts/run_repo_healthcheck_dispatch.py")
SEMANTIC_HEALTH_WORKFLOW_PATH = Path(".github/workflows/semantic_health.yml")
PERSONA_SWARM_WORKFLOW_PATH = Path(".github/workflows/persona_swarm.yml")
PERSONA_SWARM_DISPATCH_SCRIPT_PATH = Path("scripts/run_persona_swarm_dispatch.py")
EXTERNAL_SOURCE_WORKFLOW_PATH = Path(".github/workflows/external_source_registry.yml")
PYTEST_CI_WORKFLOW_PATH = Path(".github/workflows/pytest-ci.yml")
DUAL_TRACK_BOUNDARY_WORKFLOW_PATH = Path(".github/workflows/dual_track_boundary.yml")
GIT_HYGIENE_WORKFLOW_PATH = Path(".github/workflows/git_hygiene.yml")
POST_RELEASE_MONITOR_WORKFLOW_PATH = Path(".github/workflows/post_release_monitor.yml")


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _load_workflow() -> dict[str, Any]:
    return _load_yaml(WORKFLOW_PATH)


def _on_section(payload: dict[str, Any]) -> dict[str, Any]:
    # PyYAML treats bare "on" as boolean True under YAML 1.1 rules.
    if "on" in payload:
        value = payload["on"]
    else:
        value = payload.get(True, {})
    assert isinstance(value, dict)
    return value


def _healthcheck_steps(payload: dict[str, Any]) -> list[dict[str, Any]]:
    jobs = payload.get("jobs", {})
    assert isinstance(jobs, dict)
    healthcheck = jobs.get("healthcheck", {})
    assert isinstance(healthcheck, dict)
    steps = healthcheck.get("steps", [])
    assert isinstance(steps, list)
    return [step for step in steps if isinstance(step, dict)]


def _find_step(steps: list[dict[str, Any]], name: str) -> dict[str, Any]:
    for step in steps:
        if step.get("name") == name:
            return step
    raise AssertionError(f"missing step: {name}")


def _job_steps(payload: dict[str, Any], job_name: str) -> list[dict[str, Any]]:
    jobs = payload.get("jobs", {})
    assert isinstance(jobs, dict)
    job = jobs.get(job_name, {})
    assert isinstance(job, dict)
    steps = job.get("steps", [])
    assert isinstance(steps, list)
    return [step for step in steps if isinstance(step, dict)]


def test_repo_healthcheck_workflow_dispatch_inputs_contract() -> None:
    payload = _load_workflow()
    on_section = _on_section(payload)

    assert "workflow_dispatch" in on_section
    dispatch = on_section["workflow_dispatch"]
    assert isinstance(dispatch, dict)

    inputs = dispatch.get("inputs", {})
    assert isinstance(inputs, dict)
    required_inputs = {
        "include_sdh",
        "web_base",
        "api_base",
        "sdh_timeout",
        "check_council_modes",
    }
    assert required_inputs.issubset(inputs.keys())


def test_repo_healthcheck_workflow_has_default_and_dispatch_runners() -> None:
    payload = _load_workflow()
    steps = _healthcheck_steps(payload)

    default_step = _find_step(steps, "Run repository healthcheck (blocking, push/pr default)")
    assert default_step.get("if") == "github.event_name != 'workflow_dispatch'"
    default_run = default_step.get("run", "")
    assert isinstance(default_run, str)
    assert (
        "python scripts/run_repo_healthcheck.py --strict --allow-missing-discussion" in default_run
    )

    dispatch_step = _find_step(steps, "Run repository healthcheck (blocking, workflow_dispatch)")
    assert dispatch_step.get("if") == "github.event_name == 'workflow_dispatch'"
    dispatch_run = dispatch_step.get("run", "")
    assert isinstance(dispatch_run, str)
    assert dispatch_run == "python scripts/run_repo_healthcheck_dispatch.py"

    dispatch_env = dispatch_step.get("env", {})
    assert isinstance(dispatch_env, dict)
    required_env_keys = {
        "TS_INCLUDE_SDH",
        "TS_WEB_BASE",
        "TS_API_BASE",
        "TS_SDH_TIMEOUT",
        "TS_CHECK_COUNCIL_MODES",
    }
    assert required_env_keys.issubset(dispatch_env.keys())

    artifact_step = _find_step(steps, "Upload healthcheck artifacts")
    artifact_with = artifact_step.get("with", {})
    assert isinstance(artifact_with, dict)
    path_value = artifact_with.get("path", "")
    assert isinstance(path_value, str)
    assert "docs/status/repo_healthcheck_latest.json" in path_value
    assert "docs/status/repo_healthcheck_latest.md" in path_value
    assert "docs/status/persona_swarm_framework_latest.json" in path_value
    assert "docs/status/multi_agent_divergence_latest.json" in path_value
    assert "docs/status/multi_agent_divergence_latest.md" in path_value
    assert "docs/status/memory_quality_latest.json" in path_value
    assert "docs/status/memory_quality_latest.md" in path_value
    assert "docs/status/memory_learning_samples_latest.jsonl" in path_value
    assert "docs/status/memory_governance_contract_latest.json" in path_value
    assert "docs/status/memory_governance_contract_latest.md" in path_value
    assert "docs/status/philosophical_reflection_latest.json" in path_value
    assert "docs/status/philosophical_reflection_latest.md" in path_value
    assert "docs/status/dual_track_boundary_latest.json" in path_value
    assert "docs/status/dual_track_boundary_latest.md" in path_value


def test_repo_healthcheck_workflow_dispatch_validation_guards_present() -> None:
    script_text = DISPATCH_SCRIPT_PATH.read_text(encoding="utf-8")
    assert all(
        token in script_text
        for token in (
            "scripts/run_repo_healthcheck.py",
            "--strict",
            "--allow-missing-discussion",
        )
    )
    assert "::error::sdh_timeout must be a positive integer" in script_text
    assert "SDH inputs were provided but include_sdh=false" in script_text
    assert "include_sdh=true and web_base is set but api_base is empty" in script_text
    assert "include_sdh=true and api_base is set but web_base is empty" in script_text


def test_semantic_health_workflow_is_blocking_and_has_required_dependencies() -> None:
    payload = _load_yaml(SEMANTIC_HEALTH_WORKFLOW_PATH)
    on_section = _on_section(payload)
    assert "push" in on_section
    assert "pull_request" in on_section

    steps = _job_steps(payload, "verify")
    install_step = _find_step(steps, "Install dependencies")
    install_run = install_step.get("run", "")
    assert isinstance(install_run, str)
    assert 'pip install -e ".[dev]"' in install_run

    council_step = _find_step(steps, "Run Council Tests (blocking)")
    council_run = council_step.get("run", "")
    assert isinstance(council_run, str)
    assert "pytest tests/test_pre_output_council.py" in council_run
    assert "semantic_council.log" in council_run
    assert council_step.get("continue-on-error") is not True

    artifact_step = _find_step(steps, "Upload semantic health logs")
    artifact_with = artifact_step.get("with", {})
    assert isinstance(artifact_with, dict)
    assert artifact_with.get("path") == "semantic_council.log"


def test_persona_swarm_workflow_dispatch_inputs_and_triggers() -> None:
    payload = _load_yaml(PERSONA_SWARM_WORKFLOW_PATH)
    on_section = _on_section(payload)
    assert "push" in on_section
    assert "pull_request" in on_section
    assert "workflow_dispatch" in on_section

    dispatch = on_section["workflow_dispatch"]
    assert isinstance(dispatch, dict)
    inputs = dispatch.get("inputs", {})
    assert isinstance(inputs, dict)
    assert {"strict", "input_path"}.issubset(inputs.keys())


def test_persona_swarm_workflow_is_blocking_and_uploads_artifacts() -> None:
    payload = _load_yaml(PERSONA_SWARM_WORKFLOW_PATH)
    steps = _job_steps(payload, "evaluate")

    install_step = _find_step(steps, "Install dependencies")
    install_run = install_step.get("run", "")
    assert isinstance(install_run, str)
    assert 'pip install -e ".[dev]"' in install_run

    default_step = _find_step(steps, "Run persona swarm (blocking, push/pr default)")
    default_run = default_step.get("run", "")
    assert isinstance(default_run, str)
    assert "python scripts/run_persona_swarm_framework.py --strict" in default_run

    dispatch_step = _find_step(steps, "Run persona swarm (workflow_dispatch)")
    dispatch_env = dispatch_step.get("env", {})
    assert isinstance(dispatch_env, dict)
    assert {"TS_SWARM_STRICT", "TS_SWARM_INPUT_PATH"}.issubset(dispatch_env.keys())
    dispatch_run = dispatch_step.get("run", "")
    assert isinstance(dispatch_run, str)
    assert "python scripts/run_persona_swarm_dispatch.py" in dispatch_run

    artifact_step = _find_step(steps, "Upload persona swarm artifacts")
    artifact_with = artifact_step.get("with", {})
    assert isinstance(artifact_with, dict)
    path_value = artifact_with.get("path", "")
    assert isinstance(path_value, str)
    assert "docs/status/persona_swarm_framework_latest.json" in path_value
    assert "persona_swarm.log" in path_value


def test_persona_swarm_dispatch_validation_guards_present() -> None:
    script_text = PERSONA_SWARM_DISPATCH_SCRIPT_PATH.read_text(encoding="utf-8")
    assert "scripts/run_persona_swarm_framework.py" in script_text
    assert "INPUT_PATH_VALIDATION_ERROR_PREFIX" in script_text
    assert "::error::input_path does not exist" in script_text
    assert "TS_SWARM_STRICT" in script_text
    assert "TS_SWARM_INPUT_PATH" in script_text


def test_external_source_workflow_triggers_and_blocking_runner() -> None:
    payload = _load_yaml(EXTERNAL_SOURCE_WORKFLOW_PATH)
    on_section = _on_section(payload)
    assert "schedule" in on_section
    assert "push" in on_section
    assert "pull_request" in on_section
    assert "workflow_dispatch" in on_section

    steps = _job_steps(payload, "verify")
    run_step = _find_step(steps, "Run external source registry check (blocking)")
    run_cmd = run_step.get("run", "")
    assert isinstance(run_cmd, str)
    assert "python scripts/run_external_source_registry_check.py --strict" in run_cmd


def test_external_source_workflow_uploads_status_artifacts() -> None:
    payload = _load_yaml(EXTERNAL_SOURCE_WORKFLOW_PATH)
    steps = _job_steps(payload, "verify")
    artifact_step = _find_step(steps, "Upload external source artifacts")
    artifact_with = artifact_step.get("with", {})
    assert isinstance(artifact_with, dict)
    path_value = artifact_with.get("path", "")
    assert isinstance(path_value, str)
    assert "docs/status/external_source_registry_latest.json" in path_value
    assert "docs/status/external_source_registry_latest.md" in path_value


def test_pytest_ci_workflow_triggers_and_blocking_runner() -> None:
    payload = _load_yaml(PYTEST_CI_WORKFLOW_PATH)
    on_section = _on_section(payload)
    assert "push" in on_section
    assert "pull_request" in on_section
    assert "workflow_dispatch" in on_section

    steps = _job_steps(payload, "pytest")
    install_step = _find_step(steps, "Install dependencies")
    install_run = install_step.get("run", "")
    assert isinstance(install_run, str)
    assert 'pip install -e ".[dev]"' in install_run

    citation_step = _find_step(steps, "Verify citation integrity (blocking)")
    citation_cmd = citation_step.get("run", "")
    assert isinstance(citation_cmd, str)
    assert "python scripts/verify_citation_integrity.py --strict" in citation_cmd

    run_step = _find_step(steps, "Run pytest (blocking)")
    run_cmd = run_step.get("run", "")
    assert isinstance(run_cmd, str)
    assert "pytest -q --tb=short" in run_cmd
    assert run_step.get("continue-on-error") is not True


def test_pytest_ci_workflow_uploads_logs() -> None:
    payload = _load_yaml(PYTEST_CI_WORKFLOW_PATH)
    steps = _job_steps(payload, "pytest")
    artifact_step = _find_step(steps, "Upload pytest logs")
    artifact_with = artifact_step.get("with", {})
    assert isinstance(artifact_with, dict)
    assert artifact_with.get("path") == "pytest_ci.log"


def test_dual_track_boundary_workflow_triggers_and_blocking_runner() -> None:
    payload = _load_yaml(DUAL_TRACK_BOUNDARY_WORKFLOW_PATH)
    on_section = _on_section(payload)
    assert "push" in on_section
    assert "pull_request" in on_section
    assert "workflow_dispatch" in on_section

    steps = _job_steps(payload, "verify")
    resolve_step = _find_step(steps, "Resolve changed files")
    resolve_cmd = resolve_step.get("run", "")
    assert isinstance(resolve_cmd, str)
    assert "core.quotepath=off diff --name-status --diff-filter=ACMRD" in resolve_cmd
    assert "changed_files.txt" in resolve_cmd

    run_step = _find_step(steps, "Run dual-track boundary check (blocking)")
    run_cmd = run_step.get("run", "")
    assert isinstance(run_cmd, str)
    assert (
        "python scripts/verify_dual_track_boundary.py --strict --changed-file-list changed_files.txt"
        in run_cmd
    )


def test_dual_track_boundary_workflow_uploads_artifacts() -> None:
    payload = _load_yaml(DUAL_TRACK_BOUNDARY_WORKFLOW_PATH)
    steps = _job_steps(payload, "verify")
    artifact_step = _find_step(steps, "Upload dual-track artifacts")
    artifact_with = artifact_step.get("with", {})
    assert isinstance(artifact_with, dict)
    path_value = artifact_with.get("path", "")
    assert isinstance(path_value, str)
    assert "changed_files.txt" in path_value
    assert "docs/status/dual_track_boundary_latest.json" in path_value
    assert "docs/status/dual_track_boundary_latest.md" in path_value


def test_git_hygiene_workflow_uses_strict_threshold_28() -> None:
    payload = _load_yaml(GIT_HYGIENE_WORKFLOW_PATH)
    steps = _job_steps(payload, "hygiene")
    run_step = _find_step(steps, "Run git hygiene snapshot (blocking)")
    run_cmd = run_step.get("run", "")
    assert isinstance(run_cmd, str)
    assert "python scripts/verify_git_hygiene.py --strict --max-tracked-ignored 28" in run_cmd


def test_post_release_monitor_workflow_triggers_and_checks() -> None:
    payload = _load_yaml(POST_RELEASE_MONITOR_WORKFLOW_PATH)
    on_section = _on_section(payload)
    assert "schedule" in on_section
    assert "workflow_dispatch" in on_section

    steps = _job_steps(payload, "monitor")
    smoke_step = _find_step(steps, "Run web/API same-origin smoke (Elisa scenario)")
    smoke_cmd = smoke_step.get("run", "")
    assert isinstance(smoke_cmd, str)
    assert "python scripts/verify_web_api.py" in smoke_cmd
    assert "--same-origin" in smoke_cmd
    assert "--elisa-scenario" in smoke_cmd

    preflight_step = _find_step(steps, "Run governance preflight probe")
    preflight_cmd = preflight_step.get("run", "")
    assert isinstance(preflight_cmd, str)
    assert "python scripts/verify_vercel_preflight.py" in preflight_cmd
    assert "--strict" in preflight_cmd
    assert "--same-origin" in preflight_cmd
    assert "--probe-governance-status" in preflight_cmd


def test_post_release_monitor_workflow_uploads_logs() -> None:
    payload = _load_yaml(POST_RELEASE_MONITOR_WORKFLOW_PATH)
    steps = _job_steps(payload, "monitor")
    artifact_step = _find_step(steps, "Upload monitor logs")
    artifact_with = artifact_step.get("with", {})
    assert isinstance(artifact_with, dict)
    path_value = artifact_with.get("path", "")
    assert isinstance(path_value, str)
    assert "post_release_web_api.log" in path_value
    assert "post_release_preflight.log" in path_value
