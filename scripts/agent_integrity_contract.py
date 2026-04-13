"""Shared integrity contract for protected agent-control files."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

PROTECTED_FILE_HASHES = {
    "AGENTS.md": "7120fc1e31f17d8fb9a0be312ad2035c5c6222bb40b5a003587b3b4d1840b6a2",
    "SOUL.md": "4cbc420dce02a6610275fad686476de758556a3fff67a167375fc53fd697178d",
}

EMBEDDED_HASH_METADATA_FILES = ("AGENTS.md",)
EMBEDDED_HASH_PATTERN = re.compile(
    r"\|\s+\*\*Expected Hash\*\*\s+\|\s+`([0-9a-f]{64})`\s+\|",
    re.IGNORECASE,
)


def compute_hash(filepath: Path) -> str:
    """Compute SHA-256 hash with normalized line endings for cross-platform stability."""
    payload = filepath.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def extract_embedded_expected_hash(filepath: Path) -> str | None:
    """Extract the human-facing embedded expected hash, if present."""
    if not filepath.is_file():
        return None
    match = EMBEDDED_HASH_PATTERN.search(filepath.read_text(encoding="utf-8"))
    if not match:
        return None
    return match.group(1).lower()
