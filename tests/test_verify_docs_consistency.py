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
        "CMD=(python scripts/run_repo_healthcheck.py --strict --allow-missing-discussion)\n"
        if include_base_command
        else ""
    )
    timeout_validation = (
        'echo "::error::sdh_timeout must be a positive integer"\n'
        if include_timeout_validation
        else ""
    )
    ignore_warning = (
        'echo "::warning::SDH inputs were provided but include_sdh=false"\n'
        if include_ignore_warning
        else ""
    )
    single_side_warnings = (
        'echo "::warning::include_sdh=true and web_base is set but api_base is empty"\n'
        'echo "::warning::include_sdh=true and api_base is set but web_base is empty"\n'
        if include_single_side_warnings
        else ""
    )
    _write(path, base_command + timeout_validation + ignore_warning + single_side_warnings)


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
        "has_artifact_upload": True,
        "status_readme_reference": True,
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
