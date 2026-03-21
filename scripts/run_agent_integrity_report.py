#!/usr/bin/env python3
"""Publish a compact agent-integrity governance artifact."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.agent_integrity_contract import (  # noqa: E402
    EMBEDDED_HASH_METADATA_FILES,
    PROTECTED_FILE_HASHES,
    compute_hash,
    extract_embedded_expected_hash,
)
from scripts.check_agent_integrity import (  # noqa: E402
    UNAUTHORIZED_PATHS,
    WATCHED_DIRS,
    check_embedded_hash_metadata,
    check_hash_integrity,
    check_hidden_characters,
    check_unauthorized_paths,
    check_watched_dirs,
)
from tonesoul.memory.subjectivity_handoff import build_handoff_surface  # noqa: E402

JSON_FILENAME = "agent_integrity_latest.json"
MARKDOWN_FILENAME = "agent_integrity_latest.md"
WORKFLOW_PATH = ".github/workflows/agent-integrity-check.yml"
CHECKER_PATH = "scripts/check_agent_integrity.py"
CONTRACT_PATH = "scripts/agent_integrity_contract.py"


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def _protected_file_snapshot(repo_root: Path) -> list[dict[str, object]]:
    snapshots: list[dict[str, object]] = []
    for relative_path, expected_hash in PROTECTED_FILE_HASHES.items():
        path = repo_root / relative_path
        exists = path.is_file()
        actual_hash = compute_hash(path) if exists else ""
        embedded_hash = (
            extract_embedded_expected_hash(path)
            if relative_path in EMBEDDED_HASH_METADATA_FILES
            else None
        )
        snapshots.append(
            {
                "path": relative_path,
                "exists": exists,
                "expected_hash": expected_hash,
                "actual_hash": actual_hash,
                "hash_ok": exists and actual_hash == expected_hash,
                "embedded_expected_hash": embedded_hash,
                "embedded_metadata_ok": (embedded_hash is None or embedded_hash == expected_hash),
            }
        )
    return snapshots


def _watched_directory_snapshot(repo_root: Path) -> list[dict[str, object]]:
    snapshots: list[dict[str, object]] = []
    for relative_path in WATCHED_DIRS:
        target = repo_root / relative_path
        file_count = (
            sum(1 for item in target.rglob("*") if item.is_file()) if target.is_dir() else 0
        )
        snapshots.append(
            {
                "path": relative_path,
                "exists": target.is_dir(),
                "file_count": file_count,
            }
        )
    return snapshots


def _unauthorized_path_snapshot(repo_root: Path) -> list[dict[str, object]]:
    snapshots: list[dict[str, object]] = []
    for relative_path in UNAUTHORIZED_PATHS:
        target = repo_root / relative_path
        file_count = (
            sum(1 for item in target.rglob("*") if item.is_file()) if target.is_dir() else 0
        )
        snapshots.append(
            {
                "path": relative_path,
                "exists": target.exists(),
                "is_dir": target.is_dir(),
                "file_count": file_count,
            }
        )
    return snapshots


def _problem_route_status_line(
    *,
    hidden_character_errors: list[str],
    unauthorized_path_errors: list[str],
    hash_errors: list[str],
    embedded_metadata_warnings: list[str],
) -> str:
    if hidden_character_errors:
        return (
            "integrity | family=G2_prompt_injection_surface_integrity "
            "invariant=hidden_character_safety "
            "repair=protected_file_contents"
        )
    if unauthorized_path_errors:
        return (
            "integrity | family=G3_agent_scope_boundary_integrity "
            "invariant=authorized_agent_scope "
            "repair=unauthorized_path_cleanup"
        )
    if hash_errors:
        return (
            "integrity | family=G1_integrity_contract_drift "
            "invariant=protected_file_hash_contract "
            "repair=agent_integrity_contract.py"
        )
    if embedded_metadata_warnings:
        return (
            "integrity | family=G1_integrity_contract_drift "
            "invariant=embedded_expected_hash_metadata "
            "repair=protected_file_documentation"
        )
    return ""


def build_report(repo_root: Path) -> dict[str, Any]:
    protected_files = _protected_file_snapshot(repo_root)
    watched_directories = _watched_directory_snapshot(repo_root)
    unauthorized_paths = _unauthorized_path_snapshot(repo_root)

    hash_errors = check_hash_integrity(repo_root)
    hidden_character_errors = check_hidden_characters(repo_root)
    unauthorized_path_errors = check_unauthorized_paths(repo_root)
    embedded_metadata_warnings = check_embedded_hash_metadata(repo_root)
    watched_dir_warnings = check_watched_dirs(repo_root)

    blocking_errors = hash_errors + hidden_character_errors + unauthorized_path_errors
    executable_warning_count = len(embedded_metadata_warnings)
    review_warning_count = len(watched_dir_warnings)

    if blocking_errors:
        status = "fail"
        queue_shape = "agent_integrity_attention"
    elif executable_warning_count:
        status = "warning"
        queue_shape = "agent_integrity_guarded"
    else:
        status = "pass"
        queue_shape = "agent_integrity_guarded"

    problem_route_status_line = _problem_route_status_line(
        hidden_character_errors=hidden_character_errors,
        unauthorized_path_errors=unauthorized_path_errors,
        hash_errors=hash_errors,
        embedded_metadata_warnings=embedded_metadata_warnings,
    )
    primary_status_line = (
        f"agent_integrity_{status} | "
        f"errors={len(blocking_errors)} warnings={executable_warning_count} "
        f"review_dirs={review_warning_count} protected_files={len(protected_files)}"
    )
    runtime_status_line = (
        "integrity_contract | "
        f"contract={Path(CONTRACT_PATH).name} "
        f"checker={Path(CHECKER_PATH).name} "
        f"workflow={Path(WORKFLOW_PATH).name}"
    )
    artifact_policy_status_line = (
        "protected_hashes=blocking | hidden_chars=blocking | "
        "embedded_metadata=warning | watched_dirs=review_only"
    )

    extra_fields: dict[str, object] = {
        "runtime_status_line": runtime_status_line,
        "artifact_policy_status_line": artifact_policy_status_line,
        "path": f"docs/status/{JSON_FILENAME}",
    }
    if problem_route_status_line:
        extra_fields["problem_route_status_line"] = problem_route_status_line

    return {
        "generated_at": _iso_now(),
        "status": status,
        "summary": {
            "protected_file_count": len(protected_files),
            "blocking_error_count": len(blocking_errors),
            "warning_count": executable_warning_count,
            "review_warning_count": review_warning_count,
            "watched_directory_count": len(watched_directories),
            "unauthorized_path_count": sum(
                1 for item in unauthorized_paths if bool(item["exists"])
            ),
        },
        "protected_files": protected_files,
        "watched_directories": watched_directories,
        "unauthorized_paths": unauthorized_paths,
        "errors": blocking_errors,
        "warnings": embedded_metadata_warnings,
        "review_warnings": watched_dir_warnings,
        "primary_status_line": primary_status_line,
        "runtime_status_line": runtime_status_line,
        "artifact_policy_status_line": artifact_policy_status_line,
        "problem_route_status_line": problem_route_status_line,
        "handoff": build_handoff_surface(
            queue_shape=queue_shape,
            requires_operator_action=bool(blocking_errors),
            status_lines=[
                primary_status_line,
                runtime_status_line,
                problem_route_status_line,
                artifact_policy_status_line,
            ],
            extra_fields=extra_fields,
        ),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    handoff = payload.get("handoff") or {}
    lines = [
        "# Agent Integrity Latest",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- status: {payload['status']}",
        f"- primary_status_line: `{payload['primary_status_line']}`",
        f"- runtime_status_line: `{payload['runtime_status_line']}`",
        f"- artifact_policy_status_line: `{payload['artifact_policy_status_line']}`",
    ]
    if str(payload.get("problem_route_status_line") or "").strip():
        lines.append(f"- problem_route_status_line: `{payload['problem_route_status_line']}`")

    lines.extend(
        [
            "",
            "## Summary",
            f"- blocking_error_count: `{payload['summary']['blocking_error_count']}`",
            f"- warning_count: `{payload['summary']['warning_count']}`",
            f"- review_warning_count: `{payload['summary']['review_warning_count']}`",
            f"- protected_file_count: `{payload['summary']['protected_file_count']}`",
            "",
            "## Protected Files",
        ]
    )
    for item in payload["protected_files"]:
        lines.append(
            f"- `{item['path']}` "
            f"(exists=`{str(item['exists']).lower()}` "
            f"hash_ok=`{str(item['hash_ok']).lower()}` "
            f"embedded_metadata_ok=`{str(item['embedded_metadata_ok']).lower()}`)"
        )

    lines.extend(["", "## Watched Directories"])
    for item in payload["watched_directories"]:
        lines.append(
            f"- `{item['path']}` (exists=`{str(item['exists']).lower()}` file_count=`{item['file_count']}`)"
        )

    if payload["errors"]:
        lines.extend(["", "## Errors"])
        for item in payload["errors"]:
            lines.append(f"- {item}")

    if payload["warnings"]:
        lines.extend(["", "## Warnings"])
        for item in payload["warnings"]:
            lines.append(f"- {item}")

    if payload["review_warnings"]:
        lines.extend(["", "## Review Warnings"])
        for item in payload["review_warnings"]:
            lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Handoff",
            f"- queue_shape: `{handoff.get('queue_shape', '')}`",
            "- requires_operator_action: "
            f"`{str(handoff.get('requires_operator_action', False)).lower()}`",
            f"- primary_status_line: `{handoff.get('primary_status_line', '')}`",
        ]
    )
    if str(handoff.get("problem_route_status_line") or "").strip():
        lines.append(
            f"- problem_route_status_line: `{handoff.get('problem_route_status_line', '')}`"
        )
    return "\n".join(lines) + "\n"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(payload), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Publish a compact agent-integrity governance artifact."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--out-dir", default="docs/status", help="Output directory for artifacts.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when blocking integrity issues are found.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo_root).resolve()
    out_dir = (repo_root / args.out_dir).resolve()
    payload = build_report(repo_root)
    _write_json(out_dir / JSON_FILENAME, payload)
    _write_markdown(out_dir / MARKDOWN_FILENAME, payload)
    _emit(payload)
    if args.strict and payload["status"] == "fail":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
