#!/usr/bin/env python3
"""Best-effort lexical PII/credential scan for an explicit changed-file set.

This is an auditable warning gate, not a confidentiality proof. It reports only
finding kinds and counts; matched values are never emitted.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.output_redaction import redact  # noqa: E402


def _normalize(value: str) -> str:
    normalized = str(value or "").strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def scan_paths(repo_root: Path, changed_files: list[str]) -> dict[str, Any]:
    root = repo_root.resolve()
    findings: list[dict[str, Any]] = []
    issues: list[str] = []
    scanned = 0

    for raw in changed_files:
        relative = _normalize(raw)
        if not relative:
            continue
        candidate = (root / relative).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            issues.append(f"path_outside_repo:{relative}")
            continue
        if not candidate.exists():
            continue  # deleted paths have no outgoing content to scan
        if not candidate.is_file():
            issues.append(f"not_a_file:{relative}")
            continue
        try:
            content = candidate.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            issues.append(f"unscannable_text:{relative}")
            continue

        scanned += 1
        result = redact(content, include_pii=True)
        if result.findings:
            kinds = sorted({finding.kind for finding in result.findings})
            findings.append(
                {"path": relative, "finding_count": len(result.findings), "kinds": kinds}
            )

    return {
        "contract_version": "changed-content-scan-v0.1",
        "ok": not findings and not issues,
        "scope": "explicit_changed_files",
        "assurance": "best_effort_lexical_not_confidentiality_proof",
        "scanned_file_count": scanned,
        "findings": findings,
        "finding_count": sum(item["finding_count"] for item in findings),
        "issues": issues,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan changed text for known PII/secret shapes.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--changed-file", action="append", default=[])
    parser.add_argument("--strict", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = scan_paths(args.repo_root, list(args.changed_file or []))
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 1 if args.strict and not payload["ok"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
