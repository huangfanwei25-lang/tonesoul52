#!/usr/bin/env python3
"""Agent file integrity checker for pre-commit and CI use.

Detects unauthorized modifications to agent control files and scans for
hidden prompt-injection characters.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

try:
    from scripts.agent_integrity_contract import (
        EMBEDDED_HASH_METADATA_FILES,
        PROTECTED_FILE_HASHES,
        compute_hash,
        extract_embedded_expected_hash,
    )
except ModuleNotFoundError:  # pragma: no cover - direct script execution fallback
    from agent_integrity_contract import (
        EMBEDDED_HASH_METADATA_FILES,
        PROTECTED_FILE_HASHES,
        compute_hash,
        extract_embedded_expected_hash,
    )

REPO_ROOT = Path(__file__).resolve().parents[1]

# Paths that are not allowed unless explicitly authorized.
UNAUTHORIZED_PATHS = [
    ".agents",  # .agent/ is authorized for project workflows.
]

# Directories where new files should be reviewed.
WATCHED_DIRS = [
    "skills",
    ".agent/skills",
]

# Zero-width / bidi controls commonly used in prompt injection.
HIDDEN_CHAR_PATTERN = re.compile(r"[\u200b\u200c\u200d\u200e\u200f\u202a-\u202e\u2060\ufeff]")


def _resolve_repo_root(repo_root: Path | None = None) -> Path:
    return repo_root or REPO_ROOT


def check_hash_integrity(repo_root: Path | None = None) -> list[str]:
    """Verify SHA-256 hashes of trusted files."""
    errors: list[str] = []
    root = _resolve_repo_root(repo_root)
    for filename, expected_hash in PROTECTED_FILE_HASHES.items():
        filepath = root / filename
        if not filepath.is_file():
            errors.append(f"ERROR: {filename} is missing")
            continue
        actual_hash = compute_hash(filepath)
        if actual_hash != expected_hash:
            errors.append(
                f"ERROR: {filename} hash mismatch\n"
                f"  expected: {expected_hash}\n"
                f"  actual:   {actual_hash}\n"
                "  action: verify intentional change and update trusted hash"
            )
    return errors


def check_hidden_characters(repo_root: Path | None = None) -> list[str]:
    """Scan trusted files for hidden Unicode characters."""
    errors: list[str] = []
    files_to_scan = list(PROTECTED_FILE_HASHES.keys())
    root = _resolve_repo_root(repo_root)

    for filename in files_to_scan:
        filepath = root / filename
        if not filepath.is_file():
            continue

        try:
            content = filepath.read_text(encoding="utf-8")
        except Exception:
            continue

        matches = list(HIDDEN_CHAR_PATTERN.finditer(content))
        if not matches:
            continue

        lines_with_hidden: set[tuple[int, str]] = set()
        for match in matches:
            line_number = content[: match.start()].count("\n") + 1
            char_hex = f"U+{ord(match.group()):04X}"
            lines_with_hidden.add((line_number, char_hex))

        detail = "; ".join(f"line {line}: {char}" for line, char in sorted(lines_with_hidden))
        errors.append(
            f"ERROR: hidden characters found in {filename}: {detail}\n"
            "  action: remove hidden characters and re-verify"
        )

    return errors


def check_unauthorized_paths(repo_root: Path | None = None) -> list[str]:
    """Check for unauthorized agent directories/files."""
    errors: list[str] = []
    root = _resolve_repo_root(repo_root)
    for path_name in UNAUTHORIZED_PATHS:
        target = root / path_name
        if not target.exists():
            continue

        if target.is_dir():
            file_count = sum(1 for item in target.rglob("*") if item.is_file())
            errors.append(
                f"ERROR: unauthorized directory {path_name}/ ({file_count} files)\n"
                "  action: remove it or explicitly authorize it"
            )
        else:
            errors.append(
                f"ERROR: unauthorized file {path_name}\n"
                "  action: remove it or include it in trusted scope"
            )
    return errors


def check_watched_dirs(repo_root: Path | None = None) -> list[str]:
    """List files under watched directories for manual review."""
    warnings: list[str] = []
    root = _resolve_repo_root(repo_root)
    for dir_name in WATCHED_DIRS:
        target = root / dir_name
        if not target.is_dir():
            continue

        files = [item for item in target.rglob("*") if item.is_file()]
        if not files:
            continue

        preview = "\n".join(f"  - {item.relative_to(root)}" for item in files[:10])
        warnings.append(
            f"WARNING: {dir_name}/ contains {len(files)} file(s)\n{preview}\n"
            "  action: verify files are trusted"
        )
    return warnings


def check_embedded_hash_metadata(repo_root: Path | None = None) -> list[str]:
    """Warn when in-document expected-hash metadata drifts from the executable contract."""
    warnings: list[str] = []
    root = _resolve_repo_root(repo_root)
    for filename in EMBEDDED_HASH_METADATA_FILES:
        filepath = root / filename
        embedded_hash = extract_embedded_expected_hash(filepath)
        if embedded_hash is None:
            continue
        expected_hash = PROTECTED_FILE_HASHES.get(filename)
        if expected_hash and embedded_hash != expected_hash:
            warnings.append(
                f"WARNING: embedded Expected Hash metadata drift in {filename}\n"
                f"  embedded: {embedded_hash}\n"
                f"  contract: {expected_hash}\n"
                "  action: update the in-document table during the next intentional protected-file edit"
            )
    return warnings


def check_staged_agent_files(repo_root: Path | None = None) -> list[str]:
    """For pre-commit mode: warn when sensitive files are staged."""
    root = _resolve_repo_root(repo_root)
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            cwd=str(root),
            check=False,
        )
        staged = result.stdout.strip().split("\n") if result.stdout.strip() else []
    except Exception:
        return []

    sensitive_patterns = [
        "AGENTS.md",
        "HANDOFF.md",
        "SOUL.md",
        "skills/",
        ".agent/",
        ".agents/",
    ]

    flagged: list[str] = []
    for filename in staged:
        for pattern in sensitive_patterns:
            if filename == pattern.rstrip("/") or filename.startswith(pattern):
                flagged.append(filename)
                break

    if not flagged:
        return []

    return [
        "WARNING: staged sensitive file(s): "
        + ", ".join(flagged)
        + "\n  action: verify intentional change and update trusted hashes if needed"
    ]


def main() -> int:
    pre_commit = "--pre-commit" in sys.argv
    all_errors: list[str] = []
    all_warnings: list[str] = []

    print("Agent Integrity Check")
    print("=" * 50)

    errors = check_hash_integrity()
    all_errors.extend(errors)
    if not errors:
        print("OK: trusted file hashes verified")

    errors = check_hidden_characters()
    all_errors.extend(errors)
    if not errors:
        print("OK: no hidden characters detected")

    errors = check_unauthorized_paths()
    all_errors.extend(errors)
    if not errors:
        print("OK: no unauthorized paths")

    warnings = check_embedded_hash_metadata()
    all_warnings.extend(warnings)
    if not warnings:
        print("OK: embedded hash metadata aligned")

    warnings = check_watched_dirs()
    all_warnings.extend(warnings)
    if not warnings:
        print("OK: watched directories clean")

    if pre_commit:
        warnings = check_staged_agent_files()
        all_warnings.extend(warnings)
        if not warnings:
            print("OK: no sensitive files staged")

    print("=" * 50)

    if all_warnings:
        print("\nWARNINGS:")
        for warning in all_warnings:
            print(f"\n{warning}")

    if all_errors:
        print("\nERRORS:")
        for error in all_errors:
            print(f"\n{error}")
        print(f"\nFAIL: {len(all_errors)} issue(s) found")
        return 1

    print("\nPASS: all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
