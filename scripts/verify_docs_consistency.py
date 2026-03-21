"""
Documentation consistency verifier.

Checks selected source-of-truth values against docs/workflow:
- RDD threshold consistency across `scripts/verify_7d.py`, workflow, and 7D docs.
- Curated discussion path references in DDD documentation and runtime gate.
- Monthly consolidation automation contract.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _extract_single_int(pattern: str, text: str) -> int | None:
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        return None
    return int(match.group(1))


def _extract_doc_thresholds(text: str) -> list[int]:
    patterns = (
        r"(\d+)\s*tests?",
        r"(\d+)\s*cases?",
    )
    values: list[int] = []
    for pattern in patterns:
        values.extend(int(v) for v in re.findall(pattern, text, flags=re.IGNORECASE))
    return values


def _extract_test_count_mentions(text: str) -> list[int]:
    values = re.findall(r"(\d+)\s*\+?\s*tests?\b", text, flags=re.IGNORECASE)
    return [int(value) for value in values]


def _extract_python_tests_passed(status_payload: dict[str, Any]) -> int | None:
    checks = status_payload.get("checks", [])
    if not isinstance(checks, list):
        return None

    for check in checks:
        if not isinstance(check, dict):
            continue
        if check.get("name") != "python_tests":
            continue
        stdout_tail = check.get("stdout_tail", "")
        stderr_tail = check.get("stderr_tail", "")
        if not isinstance(stdout_tail, str):
            stdout_tail = ""
        if not isinstance(stderr_tail, str):
            stderr_tail = ""
        summary = f"{stdout_tail}\n{stderr_tail}"
        match = re.search(r"(\d+)\s+passed\b", summary)
        if match:
            return int(match.group(1))
    return None


def _has_curated_reference(text: str) -> bool:
    return "memory/agent_discussion_curated.jsonl" in text


def _load_yaml_mapping(path: Path) -> dict[str, Any] | None:
    try:
        payload = yaml.safe_load(_read(path))
    except yaml.YAMLError:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def _workflow_on_section(payload: dict[str, Any]) -> dict[str, Any]:
    # PyYAML under YAML 1.1 may parse bare "on" as boolean True.
    if "on" in payload:
        value = payload["on"]
    else:
        value = payload.get(True, {})
    if not isinstance(value, dict):
        return {}
    return value


def _workflow_steps(payload: dict[str, Any]) -> list[dict[str, Any]]:
    jobs = payload.get("jobs", {})
    if not isinstance(jobs, dict):
        return []

    steps: list[dict[str, Any]] = []
    for job in jobs.values():
        if not isinstance(job, dict):
            continue
        job_steps = job.get("steps", [])
        if not isinstance(job_steps, list):
            continue
        for step in job_steps:
            if isinstance(step, dict):
                steps.append(step)
    return steps


def _find_step_by_name(steps: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    for step in steps:
        if step.get("name") == name:
            return step
    return None


def _load_python_module(path: Path, module_name: str) -> Any | None:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        return None
    return module


def _evaluate_dispatch_script_contract(script_path: Path) -> dict[str, bool]:
    result = {
        "has_base_command": False,
        "has_timeout_validation": False,
        "has_ignore_warning": False,
        "has_single_side_warnings": False,
    }

    module = _load_python_module(
        script_path,
        f"_docs_consistency_dispatch_{abs(hash(str(script_path.resolve())))}",
    )
    if module is None:
        return result

    dispatch_config = getattr(module, "DispatchConfig", None)
    build_command = getattr(module, "build_command", None)
    if dispatch_config is None or not callable(build_command):
        return result

    def _call(
        *,
        include_sdh: bool,
        web_base: str,
        api_base: str,
        sdh_timeout: str,
        check_council_modes: bool,
    ) -> tuple[list[str], list[str], str | None] | None:
        try:
            config = dispatch_config(
                include_sdh=include_sdh,
                web_base=web_base,
                api_base=api_base,
                sdh_timeout=sdh_timeout,
                check_council_modes=check_council_modes,
            )
        except Exception:
            return None

        try:
            output = build_command(config)
        except Exception:
            return None

        if not isinstance(output, tuple) or len(output) != 3:
            return None
        command, warnings, error = output

        if not isinstance(command, list) or not all(isinstance(token, str) for token in command):
            return None
        if not isinstance(warnings, list) or not all(isinstance(item, str) for item in warnings):
            return None
        if error is not None and not isinstance(error, str):
            return None
        return command, warnings, error

    base_output = _call(
        include_sdh=False,
        web_base="",
        api_base="",
        sdh_timeout="",
        check_council_modes=True,
    )
    if base_output is not None:
        command, _, error = base_output
        result["has_base_command"] = (
            command[:2] == ["python", "scripts/run_repo_healthcheck.py"]
            and "--strict" in command
            and "--allow-missing-discussion" in command
            and error is None
        )

    timeout_output = _call(
        include_sdh=True,
        web_base="http://127.0.0.1:3002",
        api_base="http://127.0.0.1:5001",
        sdh_timeout="0",
        check_council_modes=True,
    )
    if timeout_output is not None:
        _, _, error = timeout_output
        result["has_timeout_validation"] = isinstance(error, str) and (
            "sdh_timeout" in error and "positive integer" in error
        )

    ignore_output = _call(
        include_sdh=False,
        web_base="http://127.0.0.1:3002",
        api_base="",
        sdh_timeout="40",
        check_council_modes=True,
    )
    if ignore_output is not None:
        _, warnings, error = ignore_output
        result["has_ignore_warning"] = error is None and any(
            "include_sdh=false" in warning for warning in warnings
        )

    left_output = _call(
        include_sdh=True,
        web_base="http://127.0.0.1:3002",
        api_base="",
        sdh_timeout="",
        check_council_modes=True,
    )
    right_output = _call(
        include_sdh=True,
        web_base="",
        api_base="http://127.0.0.1:5001",
        sdh_timeout="",
        check_council_modes=True,
    )
    left_ok = False
    right_ok = False
    if left_output is not None:
        _, warnings, error = left_output
        left_ok = error is None and any(
            "web_base is set but api_base is empty" in warning for warning in warnings
        )
    if right_output is not None:
        _, warnings, error = right_output
        right_ok = error is None and any(
            "api_base is set but web_base is empty" in warning for warning in warnings
        )
    result["has_single_side_warnings"] = left_ok and right_ok

    return result


def _evaluate_repo_healthcheck_runner_contract(script_path: Path) -> dict[str, bool]:
    result = {
        "has_persona_swarm_check": False,
        "has_external_source_registry_check": False,
        "has_multi_agent_divergence_check": False,
        "has_memory_quality_check": False,
        "has_true_verification_weekly_check": False,
    }

    module = _load_python_module(
        script_path,
        f"_docs_consistency_healthcheck_runner_{abs(hash(str(script_path.resolve())))}",
    )
    if module is None:
        return result

    build_check_specs = getattr(module, "_build_check_specs", None)
    if not callable(build_check_specs):
        return result

    try:
        specs = build_check_specs(
            python_executable="python",
            include_sdh=False,
            check_council_modes=True,
            strict_soft_fail=False,
            web_base=None,
            api_base=None,
            sdh_timeout=None,
            allow_missing_discussion=False,
            discussion_path=Path("memory/agent_discussion_curated.jsonl"),
        )
    except Exception:
        return result

    if not isinstance(specs, list):
        return result

    for spec in specs:
        if not isinstance(spec, dict):
            continue
        command = spec.get("command")
        if not isinstance(command, list) or not all(isinstance(token, str) for token in command):
            continue
        if spec.get("name") == "persona_swarm":
            result["has_persona_swarm_check"] = (
                command[:2] == ["python", "scripts/run_persona_swarm_framework.py"]
                and "--strict" in command
            )
        if spec.get("name") == "external_source_registry":
            result["has_external_source_registry_check"] = (
                command[:2] == ["python", "scripts/verify_external_source_registry.py"]
                and "--strict" in command
            )
        if spec.get("name") == "multi_agent_divergence":
            result["has_multi_agent_divergence_check"] = (
                command[:2] == ["python", "scripts/run_multi_agent_divergence_report.py"]
                and "--strict" in command
            )
        if spec.get("name") == "memory_quality":
            result["has_memory_quality_check"] = (
                command[:2] == ["python", "scripts/run_memory_quality_report.py"]
                and "--strict" in command
            )
        if spec.get("name") == "true_verification_weekly":
            result["has_true_verification_weekly_check"] = (
                command[:2] == ["python", "scripts/report_true_verification_task_status.py"]
                and "--strict" in command
            )

    return result


def build_report(repo_root: Path) -> dict[str, Any]:
    verify_7d = repo_root / "scripts" / "verify_7d.py"
    workflow = repo_root / ".github" / "workflows" / "test.yml"
    semantic_health_workflow = repo_root / ".github" / "workflows" / "semantic_health.yml"
    monthly_workflow = repo_root / ".github" / "workflows" / "monthly_consolidation.yml"
    git_hygiene_workflow = repo_root / ".github" / "workflows" / "git_hygiene.yml"
    repo_healthcheck_workflow = repo_root / ".github" / "workflows" / "repo_healthcheck.yml"
    repo_healthcheck_dispatch_script = repo_root / "scripts" / "run_repo_healthcheck_dispatch.py"
    repo_healthcheck_runner_script = repo_root / "scripts" / "run_repo_healthcheck.py"
    repo_healthcheck_status = repo_root / "docs" / "status" / "repo_healthcheck_latest.json"
    repo_structure_doc = repo_root / "docs" / "REPOSITORY_STRUCTURE.md"
    status_readme = repo_root / "docs" / "status" / "README.md"
    framework_doc = repo_root / "docs" / "7D_AUDIT_FRAMEWORK.md"
    exec_doc = repo_root / "docs" / "7D_EXECUTION_SPEC.md"

    issues: list[str] = []

    verify_7d_text = _read(verify_7d)
    workflow_text = _read(workflow)
    framework_text = _read(framework_doc)
    exec_text = _read(exec_doc)

    rdd_runtime = _extract_single_int(r"RDD_MIN_CASES\s*=\s*(\d+)", verify_7d_text)
    rdd_workflow = _extract_single_int(r"threshold\s*=\s*(\d+)", workflow_text)
    framework_thresholds = _extract_doc_thresholds(framework_text)
    exec_thresholds = _extract_doc_thresholds(exec_text)
    doc_thresholds = framework_thresholds + exec_thresholds

    if rdd_runtime is None:
        issues.append("missing RDD_MIN_CASES in scripts/verify_7d.py")
    if rdd_workflow is None:
        issues.append("missing workflow threshold in .github/workflows/test.yml")
    if not doc_thresholds:
        issues.append("no RDD threshold phrase found in 7D docs")

    if rdd_runtime is not None and rdd_workflow is not None and rdd_runtime != rdd_workflow:
        issues.append(f"RDD threshold mismatch: runtime={rdd_runtime}, workflow={rdd_workflow}")

    if rdd_runtime is not None:
        mismatched_docs = [v for v in doc_thresholds if v != rdd_runtime]
        if mismatched_docs:
            issues.append(
                f"RDD threshold mismatch in docs: runtime={rdd_runtime}, docs={sorted(set(mismatched_docs))}"
            )

    if not _has_curated_reference(verify_7d_text):
        issues.append("verify_7d is not using curated discussion path")
    if not _has_curated_reference(exec_text):
        issues.append("7D execution spec missing curated discussion path reference")

    monthly_exists = monthly_workflow.exists()
    monthly_has_schedule = False
    monthly_has_runner = False
    monthly_has_allow_missing_discussion = False
    if monthly_exists:
        monthly_payload = _load_yaml_mapping(monthly_workflow)
        if monthly_payload is not None:
            monthly_on_section = _workflow_on_section(monthly_payload)
            monthly_schedule = monthly_on_section.get("schedule")
            monthly_has_schedule = isinstance(monthly_schedule, list) and bool(monthly_schedule)

            monthly_steps = _workflow_steps(monthly_payload)
            monthly_run_commands = [
                run_text for step in monthly_steps if isinstance((run_text := step.get("run")), str)
            ]
            monthly_has_runner = any(
                "python scripts/run_monthly_consolidation.py" in run_text
                for run_text in monthly_run_commands
            )
            monthly_has_allow_missing_discussion = any(
                "--allow-missing-discussion" in run_text for run_text in monthly_run_commands
            )
        if not monthly_has_schedule:
            issues.append("monthly consolidation workflow missing schedule trigger")
        if not monthly_has_runner:
            issues.append(
                "monthly consolidation workflow missing run_monthly_consolidation invocation"
            )
        if not monthly_has_allow_missing_discussion:
            issues.append("monthly consolidation workflow missing --allow-missing-discussion")
    else:
        issues.append("missing .github/workflows/monthly_consolidation.yml")

    git_hygiene_exists = git_hygiene_workflow.exists()
    git_hygiene_has_schedule = False
    git_hygiene_has_runner = False
    git_hygiene_has_artifact_upload = False
    git_hygiene_has_push = False
    git_hygiene_has_pull_request = False
    git_hygiene_has_strict_runner = False
    if git_hygiene_exists:
        git_hygiene_payload = _load_yaml_mapping(git_hygiene_workflow)
        if git_hygiene_payload is not None:
            git_hygiene_on_section = _workflow_on_section(git_hygiene_payload)
            git_hygiene_schedule = git_hygiene_on_section.get("schedule")
            git_hygiene_has_schedule = isinstance(git_hygiene_schedule, list) and bool(
                git_hygiene_schedule
            )
            git_hygiene_has_push = "push" in git_hygiene_on_section
            git_hygiene_has_pull_request = "pull_request" in git_hygiene_on_section

            git_hygiene_steps = _workflow_steps(git_hygiene_payload)
            git_hygiene_run_commands = [
                run_text
                for step in git_hygiene_steps
                if isinstance((run_text := step.get("run")), str)
            ]
            git_hygiene_has_runner = any(
                "python scripts/verify_git_hygiene.py" in run_text
                for run_text in git_hygiene_run_commands
            )
            git_hygiene_has_strict_runner = any(
                "python scripts/verify_git_hygiene.py" in run_text and "--strict" in run_text
                for run_text in git_hygiene_run_commands
            )
            git_hygiene_has_artifact_upload = any(
                isinstance(step.get("uses"), str)
                and step["uses"].startswith("actions/upload-artifact@")
                for step in git_hygiene_steps
            )
        if not git_hygiene_has_schedule:
            issues.append("git hygiene workflow missing schedule trigger")
        if not git_hygiene_has_runner:
            issues.append("git hygiene workflow missing verify_git_hygiene invocation")
        if not git_hygiene_has_artifact_upload:
            issues.append("git hygiene workflow missing artifact upload step")
        if not git_hygiene_has_push:
            issues.append("git hygiene workflow missing push trigger")
        if not git_hygiene_has_pull_request:
            issues.append("git hygiene workflow missing pull_request trigger")
        if not git_hygiene_has_strict_runner:
            issues.append("git hygiene workflow missing strict runner (--strict)")
    else:
        issues.append("missing .github/workflows/git_hygiene.yml")

    semantic_health_exists = semantic_health_workflow.exists()
    semantic_health_has_push = False
    semantic_health_has_pull_request = False
    semantic_health_has_blocking_council_tests = False
    if semantic_health_exists:
        semantic_health_payload = _load_yaml_mapping(semantic_health_workflow)
        if semantic_health_payload is not None:
            semantic_health_on_section = _workflow_on_section(semantic_health_payload)
            semantic_health_has_push = "push" in semantic_health_on_section
            semantic_health_has_pull_request = "pull_request" in semantic_health_on_section

            semantic_steps = _workflow_steps(semantic_health_payload)
            council_step = None
            for step in semantic_steps:
                name = step.get("name")
                if isinstance(name, str) and "Run Council Tests" in name:
                    council_step = step
                    break
            council_run = council_step.get("run", "") if council_step else ""
            semantic_health_has_blocking_council_tests = bool(
                council_step is not None
                and council_step.get("continue-on-error") is not True
                and isinstance(council_run, str)
                and "pytest" in council_run
            )
        if not semantic_health_has_push:
            issues.append("semantic health workflow missing push trigger")
        if not semantic_health_has_pull_request:
            issues.append("semantic health workflow missing pull_request trigger")
        if not semantic_health_has_blocking_council_tests:
            issues.append("semantic health workflow council tests are not blocking")
    else:
        issues.append("missing .github/workflows/semantic_health.yml")

    repo_healthcheck_exists = repo_healthcheck_workflow.exists()
    repo_healthcheck_has_dispatch = False
    repo_healthcheck_has_dispatch_inputs = False
    repo_healthcheck_has_default_runner = False
    repo_healthcheck_has_dispatch_runner = False
    repo_healthcheck_has_dispatch_env_bridge = False
    repo_healthcheck_script_exists = repo_healthcheck_dispatch_script.exists()
    repo_healthcheck_script_has_base_command = False
    repo_healthcheck_script_has_timeout_validation = False
    repo_healthcheck_script_has_ignore_warning = False
    repo_healthcheck_script_has_single_side_warnings = False
    repo_healthcheck_runner_exists = repo_healthcheck_runner_script.exists()
    repo_healthcheck_runner_has_persona_swarm_check = False
    repo_healthcheck_runner_has_external_source_registry_check = False
    repo_healthcheck_runner_has_multi_agent_divergence_check = False
    repo_healthcheck_runner_has_memory_quality_check = False
    repo_healthcheck_runner_has_true_verification_weekly_check = False
    if repo_healthcheck_exists:
        repo_healthcheck_payload = _load_yaml_mapping(repo_healthcheck_workflow)
        if repo_healthcheck_payload is not None:
            on_section = _workflow_on_section(repo_healthcheck_payload)
            repo_healthcheck_has_dispatch = "workflow_dispatch" in on_section

            dispatch_section = on_section.get("workflow_dispatch", {})
            dispatch_inputs: dict[str, Any] = {}
            if isinstance(dispatch_section, dict):
                maybe_inputs = dispatch_section.get("inputs", {})
                if isinstance(maybe_inputs, dict):
                    dispatch_inputs = maybe_inputs
            required_input_names = {
                "include_sdh",
                "web_base",
                "api_base",
                "sdh_timeout",
                "check_council_modes",
            }
            repo_healthcheck_has_dispatch_inputs = required_input_names.issubset(
                dispatch_inputs.keys()
            )

            steps = _workflow_steps(repo_healthcheck_payload)

            default_step = _find_step_by_name(
                steps, "Run repository healthcheck (blocking, push/pr default)"
            )
            default_run = default_step.get("run", "") if default_step else ""
            repo_healthcheck_has_default_runner = bool(
                default_step is not None
                and default_step.get("if") == "github.event_name != 'workflow_dispatch'"
                and isinstance(default_run, str)
                and "python scripts/run_repo_healthcheck.py --strict --allow-missing-discussion"
                in default_run
            )

            dispatch_step = _find_step_by_name(
                steps, "Run repository healthcheck (blocking, workflow_dispatch)"
            )
            dispatch_run = dispatch_step.get("run", "") if dispatch_step else ""
            repo_healthcheck_has_dispatch_runner = bool(
                dispatch_step is not None
                and dispatch_step.get("if") == "github.event_name == 'workflow_dispatch'"
                and isinstance(dispatch_run, str)
                and dispatch_run.strip() == "python scripts/run_repo_healthcheck_dispatch.py"
            )

            dispatch_env = dispatch_step.get("env", {}) if dispatch_step else {}
            required_env_names = {
                "TS_INCLUDE_SDH",
                "TS_WEB_BASE",
                "TS_API_BASE",
                "TS_SDH_TIMEOUT",
                "TS_CHECK_COUNCIL_MODES",
            }
            repo_healthcheck_has_dispatch_env_bridge = isinstance(dispatch_env, dict) and (
                required_env_names.issubset(dispatch_env.keys())
            )

        if not repo_healthcheck_has_dispatch:
            issues.append("repo healthcheck workflow missing workflow_dispatch trigger")
        if not repo_healthcheck_has_dispatch_inputs:
            issues.append("repo healthcheck workflow missing dispatch SDH inputs")
        if not repo_healthcheck_has_default_runner:
            issues.append("repo healthcheck workflow missing push/pr default runner")
        if not repo_healthcheck_has_dispatch_runner:
            issues.append("repo healthcheck workflow missing workflow_dispatch runner")
        if not repo_healthcheck_has_dispatch_env_bridge:
            issues.append("repo healthcheck workflow missing dispatch env bridge")
    else:
        issues.append("missing .github/workflows/repo_healthcheck.yml")

    if repo_healthcheck_script_exists:
        script_contract = _evaluate_dispatch_script_contract(repo_healthcheck_dispatch_script)
        repo_healthcheck_script_has_base_command = script_contract["has_base_command"]
        repo_healthcheck_script_has_timeout_validation = script_contract["has_timeout_validation"]
        repo_healthcheck_script_has_ignore_warning = script_contract["has_ignore_warning"]
        repo_healthcheck_script_has_single_side_warnings = script_contract[
            "has_single_side_warnings"
        ]
        if not repo_healthcheck_script_has_base_command:
            issues.append("repo healthcheck dispatch script missing base command")
        if not repo_healthcheck_script_has_timeout_validation:
            issues.append("repo healthcheck dispatch script missing sdh_timeout validation")
        if not repo_healthcheck_script_has_ignore_warning:
            issues.append("repo healthcheck dispatch script missing include_sdh=false warning")
        if not repo_healthcheck_script_has_single_side_warnings:
            issues.append("repo healthcheck dispatch script missing single-side endpoint warnings")
    else:
        issues.append("missing scripts/run_repo_healthcheck_dispatch.py")

    if repo_healthcheck_runner_exists:
        runner_contract = _evaluate_repo_healthcheck_runner_contract(repo_healthcheck_runner_script)
        repo_healthcheck_runner_has_persona_swarm_check = runner_contract["has_persona_swarm_check"]
        repo_healthcheck_runner_has_external_source_registry_check = runner_contract[
            "has_external_source_registry_check"
        ]
        repo_healthcheck_runner_has_multi_agent_divergence_check = runner_contract[
            "has_multi_agent_divergence_check"
        ]
        repo_healthcheck_runner_has_memory_quality_check = runner_contract[
            "has_memory_quality_check"
        ]
        repo_healthcheck_runner_has_true_verification_weekly_check = runner_contract[
            "has_true_verification_weekly_check"
        ]
        if not repo_healthcheck_runner_has_persona_swarm_check:
            issues.append("repo healthcheck runner missing persona swarm check")
        if not repo_healthcheck_runner_has_external_source_registry_check:
            issues.append("repo healthcheck runner missing external source registry check")
        if not repo_healthcheck_runner_has_multi_agent_divergence_check:
            issues.append("repo healthcheck runner missing multi-agent divergence check")
        if not repo_healthcheck_runner_has_memory_quality_check:
            issues.append("repo healthcheck runner missing memory quality check")
        if not repo_healthcheck_runner_has_true_verification_weekly_check:
            issues.append("repo healthcheck runner missing weekly true verification check")
    else:
        issues.append("missing scripts/run_repo_healthcheck.py")

    status_readme_has_git_hygiene = False
    status_readme_has_repo_healthcheck_dispatch_inputs = False
    status_readme_has_repo_healthcheck_validation_notes = False
    if status_readme.exists():
        status_readme_text = _read(status_readme)
        status_readme_has_git_hygiene = "git_hygiene_latest.json" in status_readme_text
        if not status_readme_has_git_hygiene:
            issues.append("docs/status/README.md missing git hygiene artifact reference")
        status_readme_has_repo_healthcheck_dispatch_inputs = all(
            token in status_readme_text
            for token in (
                "include_sdh",
                "web_base",
                "api_base",
                "sdh_timeout",
                "check_council_modes",
            )
        )
        status_readme_has_repo_healthcheck_validation_notes = all(
            token in status_readme_text
            for token in (
                "invalid `sdh_timeout`",
                "include_sdh=false",
                "`web_base` / `api_base`",
            )
        )
        if not status_readme_has_repo_healthcheck_dispatch_inputs:
            issues.append("docs/status/README.md missing repo healthcheck dispatch inputs")
        if not status_readme_has_repo_healthcheck_validation_notes:
            issues.append(
                "docs/status/README.md missing repo healthcheck dispatch validation notes"
            )
    else:
        issues.append("missing docs/status/README.md")

    repo_structure_exists = repo_structure_doc.exists()
    repo_structure_has_dynamic_tests_reference = False
    repo_structure_static_test_counts: list[int] = []
    repo_structure_has_stale_static_test_count = False
    repo_healthcheck_status_exists = repo_healthcheck_status.exists()
    latest_python_tests_passed = None

    if repo_healthcheck_status_exists:
        try:
            status_payload = json.loads(_read(repo_healthcheck_status))
        except json.JSONDecodeError:
            issues.append("docs/status/repo_healthcheck_latest.json is invalid JSON")
        else:
            if isinstance(status_payload, dict):
                latest_python_tests_passed = _extract_python_tests_passed(status_payload)

    if repo_structure_exists:
        repo_structure_text = _read(repo_structure_doc)
        repo_structure_has_dynamic_tests_reference = all(
            token in repo_structure_text
            for token in ("docs/status/repo_healthcheck_latest.json", "python_tests")
        )
        repo_structure_static_test_counts = _extract_test_count_mentions(repo_structure_text)
        if not repo_structure_has_dynamic_tests_reference:
            issues.append("docs/REPOSITORY_STRUCTURE.md missing dynamic python test reference")
        if (
            not repo_structure_has_dynamic_tests_reference
            and latest_python_tests_passed is not None
            and repo_structure_static_test_counts
            and max(repo_structure_static_test_counts) < latest_python_tests_passed
        ):
            repo_structure_has_stale_static_test_count = True
            issues.append(
                "docs/REPOSITORY_STRUCTURE.md has stale static test count "
                f"(max={max(repo_structure_static_test_counts)}, "
                f"latest_python_tests={latest_python_tests_passed})"
            )

    return {
        "ok": len(issues) == 0,
        "rdd_thresholds": {
            "runtime": rdd_runtime,
            "workflow": rdd_workflow,
            "docs": doc_thresholds,
        },
        "curated_reference": {
            "verify_7d": _has_curated_reference(verify_7d_text),
            "execution_spec": _has_curated_reference(exec_text),
        },
        "monthly_consolidation": {
            "workflow_exists": monthly_exists,
            "has_schedule": monthly_has_schedule,
            "has_runner": monthly_has_runner,
            "has_allow_missing_discussion": monthly_has_allow_missing_discussion,
        },
        "git_hygiene": {
            "workflow_exists": git_hygiene_exists,
            "has_schedule": git_hygiene_has_schedule,
            "has_runner": git_hygiene_has_runner,
            "has_push": git_hygiene_has_push,
            "has_pull_request": git_hygiene_has_pull_request,
            "has_strict_runner": git_hygiene_has_strict_runner,
            "has_artifact_upload": git_hygiene_has_artifact_upload,
            "status_readme_reference": status_readme_has_git_hygiene,
        },
        "semantic_health": {
            "workflow_exists": semantic_health_exists,
            "has_push": semantic_health_has_push,
            "has_pull_request": semantic_health_has_pull_request,
            "has_blocking_council_tests": semantic_health_has_blocking_council_tests,
        },
        "repo_healthcheck_dispatch": {
            "workflow_exists": repo_healthcheck_exists,
            "has_dispatch": repo_healthcheck_has_dispatch,
            "has_dispatch_inputs": repo_healthcheck_has_dispatch_inputs,
            "has_default_runner": repo_healthcheck_has_default_runner,
            "has_dispatch_runner": repo_healthcheck_has_dispatch_runner,
            "has_dispatch_env_bridge": repo_healthcheck_has_dispatch_env_bridge,
            "script_exists": repo_healthcheck_script_exists,
            "script_has_base_command": repo_healthcheck_script_has_base_command,
            "script_has_timeout_validation": repo_healthcheck_script_has_timeout_validation,
            "script_has_ignore_warning": repo_healthcheck_script_has_ignore_warning,
            "script_has_single_side_warnings": repo_healthcheck_script_has_single_side_warnings,
            "status_readme_inputs": status_readme_has_repo_healthcheck_dispatch_inputs,
            "status_readme_validation_notes": status_readme_has_repo_healthcheck_validation_notes,
        },
        "repo_healthcheck_runner": {
            "script_exists": repo_healthcheck_runner_exists,
            "has_persona_swarm_check": repo_healthcheck_runner_has_persona_swarm_check,
            "has_external_source_registry_check": (
                repo_healthcheck_runner_has_external_source_registry_check
            ),
            "has_multi_agent_divergence_check": (
                repo_healthcheck_runner_has_multi_agent_divergence_check
            ),
            "has_memory_quality_check": repo_healthcheck_runner_has_memory_quality_check,
            "has_true_verification_weekly_check": (
                repo_healthcheck_runner_has_true_verification_weekly_check
            ),
        },
        "docs_freshness": {
            "repo_structure_exists": repo_structure_exists,
            "repo_structure_dynamic_test_reference": repo_structure_has_dynamic_tests_reference,
            "repo_structure_static_test_counts": repo_structure_static_test_counts,
            "repo_structure_stale_static_test_count": repo_structure_has_stale_static_test_count,
            "repo_healthcheck_status_exists": repo_healthcheck_status_exists,
            "latest_python_tests_passed": latest_python_tests_passed,
        },
        "issues": issues,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify documentation consistency with runtime gates."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    report = build_report(Path(args.repo_root).resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
