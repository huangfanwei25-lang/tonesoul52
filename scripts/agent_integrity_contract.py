"""Shared integrity contract for protected agent-control files."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

PROTECTED_FILE_HASHES = {
    "AGENTS.md": "ddc2330c75dadc5525de61286237a458adc22cfaa63732a191ad10b9b158e7fa",
    "HANDOFF.md": "d6ac7efc13a181bf2289ab19b82f42b9c2aba7833e6537048837fa0ec47cfeba",
    "SOUL.md": "5b9f13b4fb5a5ac3d1b9618b0073cc33a3edb0f985518144d575dc97eb372a5f",
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
