from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

WORKFLOW_PATH = Path(".github/workflows/repo_healthcheck.yml")
DISPATCH_SCRIPT_PATH = Path("scripts/run_repo_healthcheck_dispatch.py")
SEMANTIC_HEALTH_WORKFLOW_PATH = Path(".github/workflows/semantic_health.yml")


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
