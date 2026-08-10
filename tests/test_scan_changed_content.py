from __future__ import annotations

from pathlib import Path

from scripts.scan_changed_content import main, scan_paths


def test_scan_reports_kinds_without_leaking_values(tmp_path: Path) -> None:
    sample_address = "person" + "@" + "example.com"
    path = tmp_path / "docs" / "note.md"
    path.parent.mkdir(parents=True)
    path.write_text(f"contact: {sample_address}\n", encoding="utf-8")

    payload = scan_paths(tmp_path, ["docs/note.md"])

    assert payload["ok"] is False
    assert payload["findings"] == [{"path": "docs/note.md", "finding_count": 1, "kinds": ["email"]}]
    assert sample_address not in str(payload)


def test_scan_fails_closed_for_outside_and_unscannable_paths(tmp_path: Path) -> None:
    binary = tmp_path / "opaque.bin"
    binary.write_bytes(b"\xff\xfe\x00")

    payload = scan_paths(tmp_path, ["../outside.txt", "opaque.bin"])

    assert payload["ok"] is False
    assert "path_outside_repo:../outside.txt" in payload["issues"]
    assert "unscannable_text:opaque.bin" in payload["issues"]


def test_strict_cli_returns_nonzero_on_finding(tmp_path: Path) -> None:
    path = tmp_path / "config.txt"
    path.write_text("OPENAI_API_KEY=sk-" + "a" * 40 + "\n", encoding="utf-8")

    assert main(["--repo-root", str(tmp_path), "--changed-file", "config.txt", "--strict"]) == 1
