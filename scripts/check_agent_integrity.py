#!/usr/bin/env python3
"""Agent file integrity checker for pre-commit and CI use.

Detects unauthorized modifications to agent control files and scans for
hidden prompt-injection characters.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# SHA-256 hashes of trusted files. Update when intentionally modified.
TRUSTED_HASHES = {
    "AGENTS.md": "f01ded6d5ab3f8a00ee047e64b631de0f49afa51ead85489a574b62ece3c7173",
    "HANDOFF.md": "018c888f0864c6b2992674d5bfbcf76e7fdcde9634c216a29d2c583919d67834",
    "SOUL.md": "5b9f13b4fb5a5ac3d1b9618b0073cc33a3edb0f985518144d575dc97eb372a5f",
}

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


def compute_hash(filepath: Path) -> str:
    """Compute SHA-256 hash with normalized line endings for cross-platform stability."""
    payload = filepath.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def check_hash_integrity() -> list[str]:
    """Verify SHA-256 hashes of trusted files."""
    errors: list[str] = []
    for filename, expected_hash in TRUSTED_HASHES.items():
        filepath = REPO_ROOT / filename
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


def check_hidden_characters() -> list[str]:
    """Scan trusted files for hidden Unicode characters."""
    errors: list[str] = []
    files_to_scan = list(TRUSTED_HASHES.keys())

    for filename in files_to_scan:
        filepath = REPO_ROOT / filename
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


def check_unauthorized_paths() -> list[str]:
    """Check for unauthorized agent directories/files."""
    errors: list[str] = []
    for path_name in UNAUTHORIZED_PATHS:
        target = REPO_ROOT / path_name
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


def check_watched_dirs() -> list[str]:
    """List files under watched directories for manual review."""
    warnings: list[str] = []
    for dir_name in WATCHED_DIRS:
        target = REPO_ROOT / dir_name
        if not target.is_dir():
            continue

        files = [item for item in target.rglob("*") if item.is_file()]
        if not files:
            continue

        preview = "\n".join(f"  - {item.relative_to(REPO_ROOT)}" for item in files[:10])
        warnings.append(
            f"WARNING: {dir_name}/ contains {len(files)} file(s)\n{preview}\n"
            "  action: verify files are trusted"
        )
    return warnings


def check_staged_agent_files() -> list[str]:
    """For pre-commit mode: warn when sensitive files are staged."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
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
