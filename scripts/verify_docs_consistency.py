"""
Documentation consistency verifier.

Checks selected source-of-truth values against docs/workflow:
- RDD threshold consistency across `scripts/verify_7d.py`, workflow, and 7D docs.
- Curated discussion path references in DDD documentation and runtime gate.
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
        r"最小\s*(\d+)\s*tests",
        r"至少\s*(\d+)\s*cases",
    )
    values: list[int] = []
    for pattern in patterns:
        values.extend(int(v) for v in re.findall(pattern, text))
    return values


def _has_curated_reference(text: str) -> bool:
    return "memory/agent_discussion_curated.jsonl" in text


def build_report(repo_root: Path) -> dict[str, Any]:
    verify_7d = repo_root / "scripts" / "verify_7d.py"
    workflow = repo_root / ".github" / "workflows" / "test.yml"
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
        "issues": issues,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify documentation consistency with runtime gates.")
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    report = build_report(Path(args.repo_root).resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
