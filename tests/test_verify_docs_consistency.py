from pathlib import Path

import scripts.verify_docs_consistency as docs_consistency


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_repo_healthcheck_workflow(
    path: Path,
    *,
    include_default_runner: bool = True,
    include_dispatch_runner: bool = True,
    include_dispatch_env_bridge: bool = True,
) -> None:
    default_runner = (
        "      - name: Run repository healthcheck (blocking, push/pr default)\n"
        "        if: github.event_name != 'workflow_dispatch'\n"
        "        run: |\n"
        "          python scripts/run_repo_healthcheck.py --strict --allow-missing-discussion\n"
        if include_default_runner
        else ""
    )
    dispatch_env = (
        "        env:\n"
        "          TS_INCLUDE_SDH: ${{ github.event.inputs.include_sdh }}\n"
        "          TS_WEB_BASE: ${{ github.event.inputs.web_base }}\n"
        "          TS_API_BASE: ${{ github.event.inputs.api_base }}\n"
        "          TS_SDH_TIMEOUT: ${{ github.event.inputs.sdh_timeout }}\n"
        "          TS_CHECK_COUNCIL_MODES: ${{ github.event.inputs.check_council_modes }}\n"
        if include_dispatch_env_bridge
        else ""
    )
    dispatch_runner = (
        "      - name: Run repository healthcheck (blocking, workflow_dispatch)\n"
        "        if: github.event_name == 'workflow_dispatch'\n"
        f"{dispatch_env}"
        "        run: python scripts/run_repo_healthcheck_dispatch.py\n"
        if include_dispatch_runner
        else ""
    )
    _write(
        path,
        (
            "on:\n"
            "  workflow_dispatch:\n"
            "    inputs:\n"
            "      include_sdh:\n"
            "      web_base:\n"
            "      api_base:\n"
            "      sdh_timeout:\n"
            "      check_council_modes:\n"
            "jobs:\n"
            "  c:\n"
            "    steps:\n"
            f"{default_runner}"
            f"{dispatch_runner}"
        ),
    )


def _write_repo_healthcheck_dispatch_script(
    path: Path,
    *,
    include_base_command: bool = True,
    include_timeout_validation: bool = True,
    include_ignore_warning: bool = True,
    include_single_side_warnings: bool = True,
) -> None:
    base_command = (
        '    command = ["python", "scripts/run_repo_healthcheck.py", "--strict", "--allow-missing-discussion"]\n'
        if include_base_command
        else '    command = ["python"]\n'
    )
    timeout_validation = (
        "    if config.sdh_timeout:\n"
        "        if not config.sdh_timeout.isdigit() or int(config.sdh_timeout) < 1:\n"
        '            error = "sdh_timeout must be a positive integer"\n'
        if include_timeout_validation
        else ""
    )
    ignore_warning = (
        "        if config.web_base or config.api_base or config.sdh_timeout:\n"
        '            warnings.append("SDH inputs were provided but include_sdh=false")\n'
        if include_ignore_warning
        else ""
    )
    single_side_warnings = (
        "        if config.web_base and not config.api_base:\n"
        '            warnings.append("include_sdh=true and web_base is set but api_base is empty")\n'
        "        if config.api_base and not config.web_base:\n"
        '            warnings.append("include_sdh=true and api_base is set but web_base is empty")\n'
        if include_single_side_warnings
        else ""
    )
    _write(
        path,
        (
            "from dataclasses import dataclass\n\n"
            "@dataclass(frozen=True)\n"
            "class DispatchConfig:\n"
            "    include_sdh: bool\n"
            "    web_base: str\n"
            "    api_base: str\n"
            "    sdh_timeout: str\n"
            "    check_council_modes: bool\n\n"
            "def build_command(config: DispatchConfig):\n"
            f"{base_command}"
            "    warnings = []\n"
            "    error = None\n"
            f"{timeout_validation}"
            "    if config.include_sdh:\n"
            f"{single_side_warnings}"
            "    else:\n"
            f"{ignore_warning}"
            "    return command, warnings, error\n"
        ),
    )


def _write_repo_healthcheck_runner_script(
    path: Path,
    *,
    include_persona_swarm_check: bool = True,
    include_external_source_registry_check: bool = True,
    include_multi_agent_divergence_check: bool = True,
    include_memory_quality_check: bool = True,
    include_true_verification_weekly_check: bool = True,
) -> None:
    persona_swarm_block = (
        "    specs.append(\n"
        "        {\n"
        '            "name": "persona_swarm",\n'
        '            "command": [python_executable, "scripts/run_persona_swarm_framework.py", "--strict"],\n'
        "        }\n"
        "    )\n"
        if include_persona_swarm_check
        else ""
    )
    source_registry_block = (
        "    specs.append(\n"
        "        {\n"
        '            "name": "external_source_registry",\n'
        '            "command": [python_executable, "scripts/verify_external_source_registry.py", "--strict"],\n'
        "        }\n"
        "    )\n"
        if include_external_source_registry_check
        else ""
    )
    divergence_block = (
        "    specs.append(\n"
        "        {\n"
        '            "name": "multi_agent_divergence",\n'
        '            "command": [python_executable, "scripts/run_multi_agent_divergence_report.py", "--strict"],\n'
        "        }\n"
        "    )\n"
        if include_multi_agent_divergence_check
        else ""
    )
    memory_quality_block = (
        "    specs.append(\n"
        "        {\n"
        '            "name": "memory_quality",\n'
        '            "command": [python_executable, "scripts/run_memory_quality_report.py", "--strict"],\n'
        "        }\n"
        "    )\n"
        if include_memory_quality_check
        else ""
    )
    true_verification_weekly_block = (
        "    specs.append(\n"
        "        {\n"
        '            "name": "true_verification_weekly",\n'
        '            "command": [python_executable, "scripts/report_true_verification_task_status.py", "--strict"],\n'
        "        }\n"
        "    )\n"
        if include_true_verification_weekly_check
        else ""
    )
    _write(
        path,
        (
            "from pathlib import Path\n"
            "from typing import Any\n\n"
            "def _build_check_specs(\n"
            "    python_executable: str,\n"
            "    include_sdh: bool,\n"
            "    check_council_modes: bool,\n"
            "    strict_soft_fail: bool,\n"
            "    web_base: str | None,\n"
            "    api_base: str | None,\n"
            "    sdh_timeout: int | None,\n"
            "    allow_missing_discussion: bool,\n"
            "    discussion_path: Path,\n"
            ") -> list[dict[str, Any]]:\n"
            "    specs: list[dict[str, Any]] = []\n"
            f"{persona_swarm_block}"
            f"{source_registry_block}"
            f"{divergence_block}"
            f"{memory_quality_block}"
            f"{true_verification_weekly_block}"
            "    return specs\n"
        ),
    )


def _write_status_readme(path: Path, *, include_dispatch_notes: bool = True) -> None:
    if include_dispatch_notes:
        content = (
            "- git_hygiene_latest.json\n"
            "- include_sdh\n"
            "- web_base\n"
            "- api_base\n"
            "- sdh_timeout\n"
            "- check_council_modes\n"
            "- invalid `sdh_timeout`\n"
            "- include_sdh=false\n"
            "- `web_base` / `api_base`\n"
        )
    else:
        content = "- git_hygiene_latest.json\n"
    _write(path, content)


def _write_semantic_health_workflow(
    path: Path,
    *,
    include_pull_request: bool = True,
    blocking_council_tests: bool = True,
) -> None:
    pull_request = (
        "  pull_request:\n    branches: [master, main, dev]\n" if include_pull_request else ""
    )
    continue_on_error = "" if blocking_council_tests else "        continue-on-error: true\n"
    _write(
        path,
        (
            "on:\n"
            "  schedule:\n"
            "    - cron: '0 0 * * 1'\n"
            "  workflow_dispatch:\n"
            "  push:\n"
            "    branches: [master, main, dev]\n"
            f"{pull_request}"
            "jobs:\n"
            "  verify:\n"
            "    steps:\n"
            "      - name: Run Council Tests (blocking)\n"
            f"{continue_on_error}"
            "        run: |\n"
            "          pytest tests/test_pre_output_council.py -v --tb=short\n"
        ),
    )


def _write_repo_structure_doc(path: Path, *, dynamic_reference: bool) -> None:
    test_entry = (
        "dynamic: docs/status/repo_healthcheck_latest.json (python_tests)"
        if dynamic_reference
        else "343+ tests"
    )
    _write(
        path,
        ("## Metrics\n" "| item | value |\n" "| --- | --- |\n" f"| tests | {test_entry} |\n"),
    )


def test_build_report_passes_when_thresholds_and_curated_refs_align(tmp_path: Path) -> None:
    _write(
        tmp_path / "scripts" / "verify_7d.py",
        "RDD_MIN_CASES = 20\nDDD_DISCUSSION_PATH='memory/agent_discussion_curated.jsonl'\n",
    )
    _write(tmp_path / ".github" / "workflows" / "test.yml", "threshold = 20\n")
    _write(
        tmp_path / ".github" / "workflows" / "monthly_consolidation.yml",
        "on:\n  schedule:\n    - cron: '30 3 1 * *'\njobs:\n  c:\n    steps:\n      - run: python scripts/run_monthly_consolidation.py --strict --allow-missing-discussion\n",
    )
    _write(
        tmp_path / ".github" / "workflows" / "git_hygiene.yml",
        (
            "on:\n"
            "  schedule:\n"
            "    - cron: '0 4 * * 1'\n"
            "  push:\n"
            "    branches: [master, dev]\n"
            "  pull_request:\n"
            "    branches: [master, dev]\n"
            "jobs:\n"
            "  g:\n"
            "    steps:\n"
            "      - run: python scripts/verify_git_hygiene.py --strict\n"
            "      - uses: actions/upload-artifact@v4\n"
        ),
    )
    _write_semantic_health_workflow(tmp_path / ".github" / "workflows" / "semantic_health.yml")
    _write_repo_healthcheck_workflow(tmp_path / ".github" / "workflows" / "repo_healthcheck.yml")
    _write_repo_healthcheck_dispatch_script(
        tmp_path / "scripts" / "run_repo_healthcheck_dispatch.py"
    )
    _write_repo_healthcheck_runner_script(tmp_path / "scripts" / "run_repo_healthcheck.py")
    _write(tmp_path / "docs" / "7D_AUDIT_FRAMEWORK.md", "minimum 20 tests\n")
    _write(
        tmp_path / "docs" / "7D_EXECUTION_SPEC.md",
        "at least 20 cases\npython tools/agent_discussion_tool.py audit --path memory/agent_discussion_curated.jsonl\n",
    )
    _write_status_readme(tmp_path / "docs" / "status" / "README.md")
    _write_repo_structure_doc(tmp_path / "docs" / "REPOSITORY_STRUCTURE.md", dynamic_reference=True)
    _write(
        tmp_path / "docs" / "status" / "repo_healthcheck_latest.json",
        '{"checks":[{"name":"python_tests","stdout_tail":"739 passed, 3 xfailed","stderr_tail":""}]}',
    )

    report = docs_consistency.build_report(tmp_path)
    assert report["ok"] is True
    assert report["issues"] == []
    assert report["monthly_consolidation"] == {
        "workflow_exists": True,
        "has_schedule": True,
        "has_runner": True,
        "has_allow_missing_discussion": True,
    }
    assert report["git_hygiene"] == {
        "workflow_exists": True,
        "has_schedule": True,
        "has_runner": True,
        "has_push": True,
        "has_pull_request": True,
        "has_strict_runner": True,
        "has_artifact_upload": True,
        "status_readme_reference": True,
    }
    assert report["semantic_health"] == {
        "workflow_exists": True,
        "has_push": True,
        "has_pull_request": True,
        "has_blocking_council_tests": True,
    }
    assert report["repo_healthcheck_dispatch"] == {
        "workflow_exists": True,
        "has_dispatch": True,
        "has_dispatch_inputs": True,
        "has_default_runner": True,
        "has_dispatch_runner": True,
        "has_dispatch_env_bridge": True,
        "script_exists": True,
        "script_has_base_command": True,
        "script_has_timeout_validation": True,
        "script_has_ignore_warning": True,
        "script_has_single_side_warnings": True,
        "status_readme_inputs": True,
        "status_readme_validation_notes": True,
    }
    assert report["repo_healthcheck_runner"] == {
        "script_exists": True,
        "has_persona_swarm_check": True,
        "has_external_source_registry_check": True,
        "has_multi_agent_divergence_check": True,
        "has_memory_quality_check": True,
        "has_true_verification_weekly_check": True,
    }
    assert report["docs_freshness"] == {
        "repo_structure_exists": True,
        "repo_structure_dynamic_test_reference": True,
        "repo_structure_static_test_counts": [],
        "repo_structure_stale_static_test_count": False,
        "repo_healthcheck_status_exists": True,
        "latest_python_tests_passed": 739,
    }


def test_build_report_fails_on_threshold_mismatch(tmp_path: Path) -> None:
    _write(tmp_path / "scripts" / "verify_7d.py", "RDD_MIN_CASES = 20\n")
    _write(tmp_path / ".github" / "workflows" / "test.yml", "threshold = 10\n")
    _write(tmp_path / "docs" / "7D_AUDIT_FRAMEWORK.md", "minimum 10 tests\n")
    _write(tmp_path / "docs" / "7D_EXECUTION_SPEC.md", "at least 10 cases\n")

    report = docs_consistency.build_report(tmp_path)
    assert report["ok"] is False
    assert any("mismatch" in issue for issue in report["issues"])
    assert any(
        "missing .github/workflows/monthly_consolidation.yml" in issue for issue in report["issues"]
    )


def test_build_report_fails_when_monthly_workflow_missing_allow_missing_discussion_flag(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "scripts" / "verify_7d.py",
        "RDD_MIN_CASES = 20\nDDD_DISCUSSION_PATH='memory/agent_discussion_curated.jsonl'\n",
    )
    _write(tmp_path / ".github" / "workflows" / "test.yml", "threshold = 20\n")
    _write(
        tmp_path / ".github" / "workflows" / "monthly_consolidation.yml",
        "on:\n  schedule:\n    - cron: '30 3 1 * *'\njobs:\n  c:\n    steps:\n      - run: python scripts/run_monthly_consolidation.py --strict\n",
    )
    _write(
        tmp_path / ".github" / "workflows" / "git_hygiene.yml",
        "on:\n  schedule:\n    - cron: '0 4 * * 1'\njobs:\n  g:\n    steps:\n      - run: python scripts/verify_git_hygiene.py\n      - uses: actions/upload-artifact@v4\n",
    )
    _write_repo_healthcheck_workflow(tmp_path / ".github" / "workflows" / "repo_healthcheck.yml")
    _write_repo_healthcheck_dispatch_script(
        tmp_path / "scripts" / "run_repo_healthcheck_dispatch.py"
    )
    _write(tmp_path / "docs" / "7D_AUDIT_FRAMEWORK.md", "minimum 20 tests\n")
    _write(
        tmp_path / "docs" / "7D_EXECUTION_SPEC.md",
        "at least 20 cases\npython tools/agent_discussion_tool.py audit --path memory/agent_discussion_curated.jsonl\n",
    )
    _write_status_readme(tmp_path / "docs" / "status" / "README.md")

    report = docs_consistency.build_report(tmp_path)
    assert report["ok"] is False
    assert any("--allow-missing-discussion" in issue for issue in report["issues"])


def test_build_report_fails_when_monthly_tokens_only_exist_in_notes(tmp_path: Path) -> None:
    _write(
        tmp_path / "scripts" / "verify_7d.py",
        "RDD_MIN_CASES = 20\nDDD_DISCUSSION_PATH='memory/agent_discussion_curated.jsonl'\n",
    )
    _write(tmp_path / ".github" / "workflows" / "test.yml", "threshold = 20\n")
    _write(
        tmp_path / ".github" / "workflows" / "monthly_consolidation.yml",
        (
            "on:\n"
            "  push:\n"
            "    branches: [master]\n"
            "notes: |\n"
            "  schedule:\n"
            "    - cron: '30 3 1 * *'\n"
            "  python scripts/run_monthly_consolidation.py --strict --allow-missing-discussion\n"
            "jobs:\n"
            "  c:\n"
            "    steps:\n"
            "      - run: echo placeholder\n"
        ),
    )
    _write(
        tmp_path / ".github" / "workflows" / "git_hygiene.yml",
        "on:\n  schedule:\n    - cron: '0 4 * * 1'\njobs:\n  g:\n    steps:\n      - run: python scripts/verify_git_hygiene.py\n      - uses: actions/upload-artifact@v4\n",
    )
    _write_repo_healthcheck_workflow(tmp_path / ".github" / "workflows" / "repo_healthcheck.yml")
    _write_repo_healthcheck_dispatch_script(
        tmp_path / "scripts" / "run_repo_healthcheck_dispatch.py"
    )
    _write(tmp_path / "docs" / "7D_AUDIT_FRAMEWORK.md", "minimum 20 tests\n")
    _write(
        tmp_path / "docs" / "7D_EXECUTION_SPEC.md",
        "at least 20 cases\npython tools/agent_discussion_tool.py audit --path memory/agent_discussion_curated.jsonl\n",
    )
    _write_status_readme(tmp_path / "docs" / "status" / "README.md")

    report = docs_consistency.build_report(tmp_path)
    assert report["ok"] is False
    assert any(
        "monthly consolidation workflow missing schedule trigger" in issue
        for issue in report["issues"]
    )


def test_build_report_fails_when_git_hygiene_readme_reference_missing(tmp_path: Path) -> None:
    _write(
        tmp_path / "scripts" / "verify_7d.py",
        "RDD_MIN_CASES = 20\nDDD_DISCUSSION_PATH='memory/agent_discussion_curated.jsonl'\n",
    )
    _write(tmp_path / ".github" / "workflows" / "test.yml", "threshold = 20\n")
    _write(
        tmp_path / ".github" / "workflows" / "monthly_consolidation.yml",
        "on:\n  schedule:\n    - cron: '30 3 1 * *'\njobs:\n  c:\n    steps:\n      - run: python scripts/run_monthly_consolidation.py --strict --allow-missing-discussion\n",
    )
    _write(
        tmp_path / ".github" / "workflows" / "git_hygiene.yml",
        "on:\n  schedule:\n    - cron: '0 4 * * 1'\njobs:\n  g:\n    steps:\n      - run: python scripts/verify_git_hygiene.py\n      - uses: actions/upload-artifact@v4\n",
    )
    _write_repo_healthcheck_workflow(tmp_path / ".github" / "workflows" / "repo_healthcheck.yml")
    _write_repo_healthcheck_dispatch_script(
        tmp_path / "scripts" / "run_repo_healthcheck_dispatch.py"
    )
    _write(tmp_path / "docs" / "7D_AUDIT_FRAMEWORK.md", "minimum 20 tests\n")
    _write(
        tmp_path / "docs" / "7D_EXECUTION_SPEC.md",
        "at least 20 cases\npython tools/agent_discussion_tool.py audit --path memory/agent_discussion_curated.jsonl\n",
    )
    _write(tmp_path / "docs" / "status" / "README.md", "- repo_healthcheck_latest.json\n")

    report = docs_consistency.build_report(tmp_path)
    assert report["ok"] is False
    assert any("git hygiene artifact reference" in issue for issue in report["issues"])


def test_build_report_fails_when_git_hygiene_tokens_only_exist_in_notes(tmp_path: Path) -> None:
    _write(
        tmp_path / "scripts" / "verify_7d.py",
        "RDD_MIN_CASES = 20\nDDD_DISCUSSION_PATH='memory/agent_discussion_curated.jsonl'\n",
    )
    _write(tmp_path / ".github" / "workflows" / "test.yml", "threshold = 20\n")
    _write(
        tmp_path / ".github" / "workflows" / "monthly_consolidation.yml",
        "on:\n  schedule:\n    - cron: '30 3 1 * *'\njobs:\n  c:\n    steps:\n      - run: python scripts/run_monthly_consolidation.py --strict --allow-missing-discussion\n",
    )
    _write(
        tmp_path / ".github" / "workflows" / "git_hygiene.yml",
        (
            "on:\n"
            "  push:\n"
            "    branches: [master]\n"
            "notes: |\n"
            "  schedule:\n"
            "    - cron: '0 4 * * 1'\n"
            "  python scripts/verify_git_hygiene.py\n"
            "  actions/upload-artifact@v4\n"
            "jobs:\n"
            "  g:\n"
            "    steps:\n"
            "      - run: echo placeholder\n"
        ),
    )
    _write_repo_healthcheck_workflow(tmp_path / ".github" / "workflows" / "repo_healthcheck.yml")
    _write_repo_healthcheck_dispatch_script(
        tmp_path / "scripts" / "run_repo_healthcheck_dispatch.py"
    )
    _write(tmp_path / "docs" / "7D_AUDIT_FRAMEWORK.md", "minimum 20 tests\n")
    _write(
        tmp_path / "docs" / "7D_EXECUTION_SPEC.md",
        "at least 20 cases\npython tools/agent_discussion_tool.py audit --path memory/agent_discussion_curated.jsonl\n",
    )
    _write_status_readme(tmp_path / "docs" / "status" / "README.md")

    report = docs_consistency.build_report(tmp_path)
    assert report["ok"] is False
    assert any(
        "git hygiene workflow missing schedule trigger" in issue for issue in report["issues"]
    )


def test_build_report_fails_when_repo_healthcheck_missing_timeout_validation(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "scripts" / "verify_7d.py",
        "RDD_MIN_CASES = 20\nDDD_DISCUSSION_PATH='memory/agent_discussion_curated.jsonl'\n",
    )
    _write(tmp_path / ".github" / "workflows" / "test.yml", "threshold = 20\n")
    _write(
        tmp_path / ".github" / "workflows" / "monthly_consolidation.yml",
        "on:\n  schedule:\n    - cron: '30 3 1 * *'\njobs:\n  c:\n    steps:\n      - run: python scripts/run_monthly_consolidation.py --strict --allow-missing-discussion\n",
    )
    _write(
        tmp_path / ".github" / "workflows" / "git_hygiene.yml",
        "on:\n  schedule:\n    - cron: '0 4 * * 1'\njobs:\n  g:\n    steps:\n      - run: python scripts/verify_git_hygiene.py\n      - uses: actions/upload-artifact@v4\n",
    )
    _write_repo_healthcheck_workflow(tmp_path / ".github" / "workflows" / "repo_healthcheck.yml")
    _write_repo_healthcheck_dispatch_script(
        tmp_path / "scripts" / "run_repo_healthcheck_dispatch.py",
        include_timeout_validation=False,
    )
    _write(tmp_path / "docs" / "7D_AUDIT_FRAMEWORK.md", "minimum 20 tests\n")
    _write(
        tmp_path / "docs" / "7D_EXECUTION_SPEC.md",
        "at least 20 cases\npython tools/agent_discussion_tool.py audit --path memory/agent_discussion_curated.jsonl\n",
    )
    _write_status_readme(tmp_path / "docs" / "status" / "README.md")

    report = docs_consistency.build_report(tmp_path)
    assert report["ok"] is False
    assert any("sdh_timeout validation" in issue for issue in report["issues"])


def test_build_report_fails_when_repo_healthcheck_missing_default_runner(tmp_path: Path) -> None:
    _write(
        tmp_path / "scripts" / "verify_7d.py",
        "RDD_MIN_CASES = 20\nDDD_DISCUSSION_PATH='memory/agent_discussion_curated.jsonl'\n",
    )
    _write(tmp_path / ".github" / "workflows" / "test.yml", "threshold = 20\n")
    _write(
        tmp_path / ".github" / "workflows" / "monthly_consolidation.yml",
        "on:\n  schedule:\n    - cron: '30 3 1 * *'\njobs:\n  c:\n    steps:\n      - run: python scripts/run_monthly_consolidation.py --strict --allow-missing-discussion\n",
    )
    _write(
        tmp_path / ".github" / "workflows" / "git_hygiene.yml",
        "on:\n  schedule:\n    - cron: '0 4 * * 1'\njobs:\n  g:\n    steps:\n      - run: python scripts/verify_git_hygiene.py\n      - uses: actions/upload-artifact@v4\n",
    )
    _write_repo_healthcheck_workflow(
        tmp_path / ".github" / "workflows" / "repo_healthcheck.yml",
        include_default_runner=False,
    )
    _write_repo_healthcheck_dispatch_script(
        tmp_path / "scripts" / "run_repo_healthcheck_dispatch.py"
    )
    _write(tmp_path / "docs" / "7D_AUDIT_FRAMEWORK.md", "minimum 20 tests\n")
    _write(
        tmp_path / "docs" / "7D_EXECUTION_SPEC.md",
        "at least 20 cases\npython tools/agent_discussion_tool.py audit --path memory/agent_discussion_curated.jsonl\n",
    )
    _write_status_readme(tmp_path / "docs" / "status" / "README.md")

    report = docs_consistency.build_report(tmp_path)
    assert report["ok"] is False
    assert any("push/pr default runner" in issue for issue in report["issues"])


def test_build_report_fails_when_repo_healthcheck_runner_missing_persona_swarm_check(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "scripts" / "verify_7d.py",
        "RDD_MIN_CASES = 20\nDDD_DISCUSSION_PATH='memory/agent_discussion_curated.jsonl'\n",
    )
    _write(tmp_path / ".github" / "workflows" / "test.yml", "threshold = 20\n")
    _write(
        tmp_path / ".github" / "workflows" / "monthly_consolidation.yml",
        "on:\n  schedule:\n    - cron: '30 3 1 * *'\njobs:\n  c:\n    steps:\n      - run: python scripts/run_monthly_consolidation.py --strict --allow-missing-discussion\n",
    )
    _write(
        tmp_path / ".github" / "workflows" / "git_hygiene.yml",
        "on:\n  schedule:\n    - cron: '0 4 * * 1'\njobs:\n  g:\n    steps:\n      - run: python scripts/verify_git_hygiene.py\n      - uses: actions/upload-artifact@v4\n",
    )
    _write_repo_healthcheck_workflow(tmp_path / ".github" / "workflows" / "repo_healthcheck.yml")
    _write_repo_healthcheck_dispatch_script(
        tmp_path / "scripts" / "run_repo_healthcheck_dispatch.py"
    )
    _write_repo_healthcheck_runner_script(
        tmp_path / "scripts" / "run_repo_healthcheck.py",
        include_persona_swarm_check=False,
    )
    _write(tmp_path / "docs" / "7D_AUDIT_FRAMEWORK.md", "minimum 20 tests\n")
    _write(
        tmp_path / "docs" / "7D_EXECUTION_SPEC.md",
        "at least 20 cases\npython tools/agent_discussion_tool.py audit --path memory/agent_discussion_curated.jsonl\n",
    )
    _write_status_readme(tmp_path / "docs" / "status" / "README.md")

    report = docs_consistency.build_report(tmp_path)
    assert report["ok"] is False
    assert any("runner missing persona swarm check" in issue for issue in report["issues"])


def test_build_report_fails_when_repo_healthcheck_runner_missing_external_source_registry_check(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "scripts" / "verify_7d.py",
        "RDD_MIN_CASES = 20\nDDD_DISCUSSION_PATH='memory/agent_discussion_curated.jsonl'\n",
    )
    _write(tmp_path / ".github" / "workflows" / "test.yml", "threshold = 20\n")
    _write(
        tmp_path / ".github" / "workflows" / "monthly_consolidation.yml",
        "on:\n  schedule:\n    - cron: '30 3 1 * *'\njobs:\n  c:\n    steps:\n      - run: python scripts/run_monthly_consolidation.py --strict --allow-missing-discussion\n",
    )
    _write(
        tmp_path / ".github" / "workflows" / "git_hygiene.yml",
        "on:\n  schedule:\n    - cron: '0 4 * * 1'\njobs:\n  g:\n    steps:\n      - run: python scripts/verify_git_hygiene.py\n      - uses: actions/upload-artifact@v4\n",
    )
    _write_repo_healthcheck_workflow(tmp_path / ".github" / "workflows" / "repo_healthcheck.yml")
    _write_repo_healthcheck_dispatch_script(
        tmp_path / "scripts" / "run_repo_healthcheck_dispatch.py"
    )
    _write_repo_healthcheck_runner_script(
        tmp_path / "scripts" / "run_repo_healthcheck.py",
        include_external_source_registry_check=False,
    )
    _write(tmp_path / "docs" / "7D_AUDIT_FRAMEWORK.md", "minimum 20 tests\n")
    _write(
        tmp_path / "docs" / "7D_EXECUTION_SPEC.md",
        "at least 20 cases\npython tools/agent_discussion_tool.py audit --path memory/agent_discussion_curated.jsonl\n",
    )
    _write_status_readme(tmp_path / "docs" / "status" / "README.md")

    report = docs_consistency.build_report(tmp_path)
    assert report["ok"] is False
    assert any(
        "runner missing external source registry check" in issue for issue in report["issues"]
    )


def test_build_report_fails_when_repo_healthcheck_runner_missing_multi_agent_divergence_check(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "scripts" / "verify_7d.py",
        "RDD_MIN_CASES = 20\nDDD_DISCUSSION_PATH='memory/agent_discussion_curated.jsonl'\n",
    )
    _write(tmp_path / ".github" / "workflows" / "test.yml", "threshold = 20\n")
    _write(
        tmp_path / ".github" / "workflows" / "monthly_consolidation.yml",
        "on:\n  schedule:\n    - cron: '30 3 1 * *'\njobs:\n  c:\n    steps:\n      - run: python scripts/run_monthly_consolidation.py --strict --allow-missing-discussion\n",
    )
    _write(
        tmp_path / ".github" / "workflows" / "git_hygiene.yml",
        "on:\n  schedule:\n    - cron: '0 4 * * 1'\njobs:\n  g:\n    steps:\n      - run: python scripts/verify_git_hygiene.py\n      - uses: actions/upload-artifact@v4\n",
    )
    _write_repo_healthcheck_workflow(tmp_path / ".github" / "workflows" / "repo_healthcheck.yml")
    _write_repo_healthcheck_dispatch_script(
        tmp_path / "scripts" / "run_repo_healthcheck_dispatch.py"
    )
    _write_repo_healthcheck_runner_script(
        tmp_path / "scripts" / "run_repo_healthcheck.py",
        include_multi_agent_divergence_check=False,
    )
    _write(tmp_path / "docs" / "7D_AUDIT_FRAMEWORK.md", "minimum 20 tests\n")
    _write(
        tmp_path / "docs" / "7D_EXECUTION_SPEC.md",
        "at least 20 cases\npython tools/agent_discussion_tool.py audit --path memory/agent_discussion_curated.jsonl\n",
    )
    _write_status_readme(tmp_path / "docs" / "status" / "README.md")

    report = docs_consistency.build_report(tmp_path)
    assert report["ok"] is False
    assert any("runner missing multi-agent divergence check" in issue for issue in report["issues"])


def test_build_report_fails_when_repo_healthcheck_runner_missing_memory_quality_check(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "scripts" / "verify_7d.py",
        "RDD_MIN_CASES = 20\nDDD_DISCUSSION_PATH='memory/agent_discussion_curated.jsonl'\n",
    )
    _write(tmp_path / ".github" / "workflows" / "test.yml", "threshold = 20\n")
    _write(
        tmp_path / ".github" / "workflows" / "monthly_consolidation.yml",
        "on:\n  schedule:\n    - cron: '30 3 1 * *'\njobs:\n  c:\n    steps:\n      - run: python scripts/run_monthly_consolidation.py --strict --allow-missing-discussion\n",
    )
    _write(
        tmp_path / ".github" / "workflows" / "git_hygiene.yml",
        "on:\n  schedule:\n    - cron: '0 4 * * 1'\njobs:\n  g:\n    steps:\n      - run: python scripts/verify_git_hygiene.py\n      - uses: actions/upload-artifact@v4\n",
    )
    _write_repo_healthcheck_workflow(tmp_path / ".github" / "workflows" / "repo_healthcheck.yml")
    _write_repo_healthcheck_dispatch_script(
        tmp_path / "scripts" / "run_repo_healthcheck_dispatch.py"
    )
    _write_repo_healthcheck_runner_script(
        tmp_path / "scripts" / "run_repo_healthcheck.py",
        include_memory_quality_check=False,
    )
    _write(tmp_path / "docs" / "7D_AUDIT_FRAMEWORK.md", "minimum 20 tests\n")
    _write(
        tmp_path / "docs" / "7D_EXECUTION_SPEC.md",
        "at least 20 cases\npython tools/agent_discussion_tool.py audit --path memory/agent_discussion_curated.jsonl\n",
    )
    _write_status_readme(tmp_path / "docs" / "status" / "README.md")

    report = docs_consistency.build_report(tmp_path)
    assert report["ok"] is False
    assert any("runner missing memory quality check" in issue for issue in report["issues"])


def test_build_report_fails_when_repo_healthcheck_runner_missing_true_verification_weekly_check(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "scripts" / "verify_7d.py",
        "RDD_MIN_CASES = 20\nDDD_DISCUSSION_PATH='memory/agent_discussion_curated.jsonl'\n",
    )
    _write(tmp_path / ".github" / "workflows" / "test.yml", "threshold = 20\n")
    _write(
        tmp_path / ".github" / "workflows" / "monthly_consolidation.yml",
        "on:\n  schedule:\n    - cron: '30 3 1 * *'\njobs:\n  c:\n    steps:\n      - run: python scripts/run_monthly_consolidation.py --strict --allow-missing-discussion\n",
    )
    _write(
        tmp_path / ".github" / "workflows" / "git_hygiene.yml",
        "on:\n  schedule:\n    - cron: '0 4 * * 1'\njobs:\n  g:\n    steps:\n      - run: python scripts/verify_git_hygiene.py\n      - uses: actions/upload-artifact@v4\n",
    )
    _write_repo_healthcheck_workflow(tmp_path / ".github" / "workflows" / "repo_healthcheck.yml")
    _write_repo_healthcheck_dispatch_script(
        tmp_path / "scripts" / "run_repo_healthcheck_dispatch.py"
    )
    _write_repo_healthcheck_runner_script(
        tmp_path / "scripts" / "run_repo_healthcheck.py",
        include_true_verification_weekly_check=False,
    )
    _write(tmp_path / "docs" / "7D_AUDIT_FRAMEWORK.md", "minimum 20 tests\n")
    _write(
        tmp_path / "docs" / "7D_EXECUTION_SPEC.md",
        "at least 20 cases\npython tools/agent_discussion_tool.py audit --path memory/agent_discussion_curated.jsonl\n",
    )
    _write_status_readme(tmp_path / "docs" / "status" / "README.md")

    report = docs_consistency.build_report(tmp_path)
    assert report["ok"] is False
    assert any(
        "runner missing weekly true verification check" in issue for issue in report["issues"]
    )


def test_build_report_fails_when_repo_healthcheck_tokens_only_exist_in_notes(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "scripts" / "verify_7d.py",
        "RDD_MIN_CASES = 20\nDDD_DISCUSSION_PATH='memory/agent_discussion_curated.jsonl'\n",
    )
    _write(tmp_path / ".github" / "workflows" / "test.yml", "threshold = 20\n")
    _write(
        tmp_path / ".github" / "workflows" / "monthly_consolidation.yml",
        "on:\n  schedule:\n    - cron: '30 3 1 * *'\njobs:\n  c:\n    steps:\n      - run: python scripts/run_monthly_consolidation.py --strict --allow-missing-discussion\n",
    )
    _write(
        tmp_path / ".github" / "workflows" / "git_hygiene.yml",
        "on:\n  schedule:\n    - cron: '0 4 * * 1'\njobs:\n  g:\n    steps:\n      - run: python scripts/verify_git_hygiene.py\n      - uses: actions/upload-artifact@v4\n",
    )
    _write(
        tmp_path / ".github" / "workflows" / "repo_healthcheck.yml",
        (
            "on:\n"
            "  push:\n"
            "    branches: [master]\n"
            "notes: |\n"
            "  workflow_dispatch:\n"
            "    inputs:\n"
            "      include_sdh:\n"
            "      web_base:\n"
            "      api_base:\n"
            "      sdh_timeout:\n"
            "      check_council_modes:\n"
            "  Run repository healthcheck (blocking, push/pr default)\n"
            "  github.event_name != 'workflow_dispatch'\n"
            "  python scripts/run_repo_healthcheck.py --strict --allow-missing-discussion\n"
            "  Run repository healthcheck (blocking, workflow_dispatch)\n"
            "  github.event_name == 'workflow_dispatch'\n"
            "  python scripts/run_repo_healthcheck_dispatch.py\n"
            "  TS_INCLUDE_SDH:\n"
            "  TS_WEB_BASE:\n"
            "  TS_API_BASE:\n"
            "  TS_SDH_TIMEOUT:\n"
            "  TS_CHECK_COUNCIL_MODES:\n"
            "jobs:\n"
            "  c:\n"
            "    steps:\n"
            "      - run: echo placeholder\n"
        ),
    )
    _write_repo_healthcheck_dispatch_script(
        tmp_path / "scripts" / "run_repo_healthcheck_dispatch.py"
    )
    _write(tmp_path / "docs" / "7D_AUDIT_FRAMEWORK.md", "minimum 20 tests\n")
    _write(
        tmp_path / "docs" / "7D_EXECUTION_SPEC.md",
        "at least 20 cases\npython tools/agent_discussion_tool.py audit --path memory/agent_discussion_curated.jsonl\n",
    )
    _write_status_readme(tmp_path / "docs" / "status" / "README.md")

    report = docs_consistency.build_report(tmp_path)
    assert report["ok"] is False
    assert any(
        "repo healthcheck workflow missing workflow_dispatch trigger" in i for i in report["issues"]
    )


def test_build_report_fails_when_semantic_health_council_tests_are_non_blocking(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "scripts" / "verify_7d.py",
        "RDD_MIN_CASES = 20\nDDD_DISCUSSION_PATH='memory/agent_discussion_curated.jsonl'\n",
    )
    _write(tmp_path / ".github" / "workflows" / "test.yml", "threshold = 20\n")
    _write(
        tmp_path / ".github" / "workflows" / "monthly_consolidation.yml",
        "on:\n  schedule:\n    - cron: '30 3 1 * *'\njobs:\n  c:\n    steps:\n      - run: python scripts/run_monthly_consolidation.py --strict --allow-missing-discussion\n",
    )
    _write(
        tmp_path / ".github" / "workflows" / "git_hygiene.yml",
        (
            "on:\n"
            "  schedule:\n"
            "    - cron: '0 4 * * 1'\n"
            "  push:\n"
            "    branches: [master, dev]\n"
            "  pull_request:\n"
            "    branches: [master, dev]\n"
            "jobs:\n"
            "  g:\n"
            "    steps:\n"
            "      - run: python scripts/verify_git_hygiene.py --strict\n"
            "      - uses: actions/upload-artifact@v4\n"
        ),
    )
    _write_semantic_health_workflow(
        tmp_path / ".github" / "workflows" / "semantic_health.yml",
        blocking_council_tests=False,
    )
    _write_repo_healthcheck_workflow(tmp_path / ".github" / "workflows" / "repo_healthcheck.yml")
    _write_repo_healthcheck_dispatch_script(
        tmp_path / "scripts" / "run_repo_healthcheck_dispatch.py"
    )
    _write(tmp_path / "docs" / "7D_AUDIT_FRAMEWORK.md", "minimum 20 tests\n")
    _write(
        tmp_path / "docs" / "7D_EXECUTION_SPEC.md",
        "at least 20 cases\npython tools/agent_discussion_tool.py audit --path memory/agent_discussion_curated.jsonl\n",
    )
    _write_status_readme(tmp_path / "docs" / "status" / "README.md")
    _write_repo_structure_doc(tmp_path / "docs" / "REPOSITORY_STRUCTURE.md", dynamic_reference=True)

    report = docs_consistency.build_report(tmp_path)
    assert report["ok"] is False
    assert any(
        "semantic health workflow council tests are not blocking" in i for i in report["issues"]
    )


def test_build_report_fails_when_repo_structure_has_stale_static_test_count(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "scripts" / "verify_7d.py",
        "RDD_MIN_CASES = 20\nDDD_DISCUSSION_PATH='memory/agent_discussion_curated.jsonl'\n",
    )
    _write(tmp_path / ".github" / "workflows" / "test.yml", "threshold = 20\n")
    _write(
        tmp_path / ".github" / "workflows" / "monthly_consolidation.yml",
        "on:\n  schedule:\n    - cron: '30 3 1 * *'\njobs:\n  c:\n    steps:\n      - run: python scripts/run_monthly_consolidation.py --strict --allow-missing-discussion\n",
    )
    _write(
        tmp_path / ".github" / "workflows" / "git_hygiene.yml",
        (
            "on:\n"
            "  schedule:\n"
            "    - cron: '0 4 * * 1'\n"
            "  push:\n"
            "    branches: [master, dev]\n"
            "  pull_request:\n"
            "    branches: [master, dev]\n"
            "jobs:\n"
            "  g:\n"
            "    steps:\n"
            "      - run: python scripts/verify_git_hygiene.py --strict\n"
            "      - uses: actions/upload-artifact@v4\n"
        ),
    )
    _write_semantic_health_workflow(tmp_path / ".github" / "workflows" / "semantic_health.yml")
    _write_repo_healthcheck_workflow(tmp_path / ".github" / "workflows" / "repo_healthcheck.yml")
    _write_repo_healthcheck_dispatch_script(
        tmp_path / "scripts" / "run_repo_healthcheck_dispatch.py"
    )
    _write(tmp_path / "docs" / "7D_AUDIT_FRAMEWORK.md", "minimum 20 tests\n")
    _write(
        tmp_path / "docs" / "7D_EXECUTION_SPEC.md",
        "at least 20 cases\npython tools/agent_discussion_tool.py audit --path memory/agent_discussion_curated.jsonl\n",
    )
    _write_status_readme(tmp_path / "docs" / "status" / "README.md")
    _write_repo_structure_doc(
        tmp_path / "docs" / "REPOSITORY_STRUCTURE.md", dynamic_reference=False
    )
    _write(
        tmp_path / "docs" / "status" / "repo_healthcheck_latest.json",
        '{"checks":[{"name":"python_tests","stdout_tail":"739 passed, 3 xfailed","stderr_tail":""}]}',
    )

    report = docs_consistency.build_report(tmp_path)
    assert report["ok"] is False
    assert any("missing dynamic python test reference" in i for i in report["issues"])
    assert any("stale static test count" in i for i in report["issues"])
