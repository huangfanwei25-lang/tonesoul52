"""
Documentation consistency verifier.

Checks selected source-of-truth values against docs/workflow:
- RDD threshold consistency across `scripts/verify_7d.py`, workflow, and 7D docs.
- Curated discussion path references in DDD documentation and runtime gate.
- Monthly consolidation automation contract.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


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


def _has_curated_reference(text: str) -> bool:
    return "memory/agent_discussion_curated.jsonl" in text


def build_report(repo_root: Path) -> dict[str, Any]:
    verify_7d = repo_root / "scripts" / "verify_7d.py"
    workflow = repo_root / ".github" / "workflows" / "test.yml"
    monthly_workflow = repo_root / ".github" / "workflows" / "monthly_consolidation.yml"
    git_hygiene_workflow = repo_root / ".github" / "workflows" / "git_hygiene.yml"
    repo_healthcheck_workflow = repo_root / ".github" / "workflows" / "repo_healthcheck.yml"
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
        monthly_text = _read(monthly_workflow)
        monthly_has_schedule = "schedule:" in monthly_text
        monthly_has_runner = "scripts/run_monthly_consolidation.py" in monthly_text
        monthly_has_allow_missing_discussion = "--allow-missing-discussion" in monthly_text
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
    if git_hygiene_exists:
        git_hygiene_text = _read(git_hygiene_workflow)
        git_hygiene_has_schedule = "schedule:" in git_hygiene_text
        git_hygiene_has_runner = "scripts/verify_git_hygiene.py" in git_hygiene_text
        git_hygiene_has_artifact_upload = "actions/upload-artifact" in git_hygiene_text
        if not git_hygiene_has_schedule:
            issues.append("git hygiene workflow missing schedule trigger")
        if not git_hygiene_has_runner:
            issues.append("git hygiene workflow missing verify_git_hygiene invocation")
        if not git_hygiene_has_artifact_upload:
            issues.append("git hygiene workflow missing artifact upload step")
    else:
        issues.append("missing .github/workflows/git_hygiene.yml")

    repo_healthcheck_exists = repo_healthcheck_workflow.exists()
    repo_healthcheck_has_dispatch = False
    repo_healthcheck_has_dispatch_inputs = False
    repo_healthcheck_has_default_runner = False
    repo_healthcheck_has_dispatch_runner = False
    repo_healthcheck_has_timeout_validation = False
    repo_healthcheck_has_ignore_warning = False
    repo_healthcheck_has_single_side_warnings = False
    if repo_healthcheck_exists:
        repo_healthcheck_text = _read(repo_healthcheck_workflow)
        repo_healthcheck_has_dispatch = "workflow_dispatch:" in repo_healthcheck_text
        required_input_tokens = (
            "include_sdh:",
            "web_base:",
            "api_base:",
            "sdh_timeout:",
            "check_council_modes:",
        )
        repo_healthcheck_has_dispatch_inputs = all(
            token in repo_healthcheck_text for token in required_input_tokens
        )
        repo_healthcheck_has_default_runner = all(
            token in repo_healthcheck_text
            for token in (
                "Run repository healthcheck (blocking, push/pr default)",
                "github.event_name != 'workflow_dispatch'",
                "python scripts/run_repo_healthcheck.py --strict --allow-missing-discussion",
            )
        )
        repo_healthcheck_has_dispatch_runner = all(
            token in repo_healthcheck_text
            for token in (
                "Run repository healthcheck (blocking, workflow_dispatch)",
                "github.event_name == 'workflow_dispatch'",
                "CMD=(python scripts/run_repo_healthcheck.py --strict --allow-missing-discussion)",
            )
        )
        repo_healthcheck_has_timeout_validation = (
            "::error::sdh_timeout must be a positive integer" in repo_healthcheck_text
        )
        repo_healthcheck_has_ignore_warning = (
            "SDH inputs were provided but include_sdh=false" in repo_healthcheck_text
        )
        repo_healthcheck_has_single_side_warnings = all(
            token in repo_healthcheck_text
            for token in (
                "include_sdh=true and web_base is set but api_base is empty",
                "include_sdh=true and api_base is set but web_base is empty",
            )
        )

        if not repo_healthcheck_has_dispatch:
            issues.append("repo healthcheck workflow missing workflow_dispatch trigger")
        if not repo_healthcheck_has_dispatch_inputs:
            issues.append("repo healthcheck workflow missing dispatch SDH inputs")
        if not repo_healthcheck_has_default_runner:
            issues.append("repo healthcheck workflow missing push/pr default runner")
        if not repo_healthcheck_has_dispatch_runner:
            issues.append("repo healthcheck workflow missing workflow_dispatch runner")
        if not repo_healthcheck_has_timeout_validation:
            issues.append("repo healthcheck workflow missing sdh_timeout validation")
        if not repo_healthcheck_has_ignore_warning:
            issues.append("repo healthcheck workflow missing include_sdh=false warning")
        if not repo_healthcheck_has_single_side_warnings:
            issues.append("repo healthcheck workflow missing single-side endpoint warnings")
    else:
        issues.append("missing .github/workflows/repo_healthcheck.yml")

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
            "has_artifact_upload": git_hygiene_has_artifact_upload,
            "status_readme_reference": status_readme_has_git_hygiene,
        },
        "repo_healthcheck_dispatch": {
            "workflow_exists": repo_healthcheck_exists,
            "has_dispatch": repo_healthcheck_has_dispatch,
            "has_dispatch_inputs": repo_healthcheck_has_dispatch_inputs,
            "has_default_runner": repo_healthcheck_has_default_runner,
            "has_dispatch_runner": repo_healthcheck_has_dispatch_runner,
            "has_timeout_validation": repo_healthcheck_has_timeout_validation,
            "has_ignore_warning": repo_healthcheck_has_ignore_warning,
            "has_single_side_warnings": repo_healthcheck_has_single_side_warnings,
            "status_readme_inputs": status_readme_has_repo_healthcheck_dispatch_inputs,
            "status_readme_validation_notes": status_readme_has_repo_healthcheck_validation_notes,
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
