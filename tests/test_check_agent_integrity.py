from __future__ import annotations

from pathlib import Path

import scripts.agent_integrity_contract as contract
import scripts.check_agent_integrity as integrity


def test_protected_hashes_match_current_normalized_files() -> None:
    for filename, expected_hash in contract.PROTECTED_FILE_HASHES.items():
        filepath = contract.REPO_ROOT / filename
        assert contract.compute_hash(filepath) == expected_hash


def test_embedded_hash_metadata_drift_is_warning_not_error(monkeypatch, tmp_path: Path) -> None:
    repo_root = tmp_path
    monkeypatch.setattr(integrity, "REPO_ROOT", repo_root)
    monkeypatch.setattr(contract, "REPO_ROOT", repo_root)
    monkeypatch.setattr(
        contract,
        "PROTECTED_FILE_HASHES",
        {
            "AGENTS.md": "b" * 64,
            "HANDOFF.md": "c" * 64,
            "SOUL.md": "d" * 64,
        },
    )
    monkeypatch.setattr(integrity, "PROTECTED_FILE_HASHES", contract.PROTECTED_FILE_HASHES)

    (repo_root / "AGENTS.md").write_text(
        "| **Expected Hash** | `" + "a" * 64 + "` |\n",
        encoding="utf-8",
    )

    warnings = integrity.check_embedded_hash_metadata()

    assert len(warnings) == 1
    assert "embedded Expected Hash metadata drift in AGENTS.md" in warnings[0]
    assert "embedded: " + "a" * 64 in warnings[0]
    assert "contract: " + "b" * 64 in warnings[0]
