from __future__ import annotations

import json
from pathlib import Path

import scripts.verify_abc_firewall as verifier


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _valid_doctrine() -> str:
    return (
        "# ToneSoul A/B/C Firewall Doctrine\n\n"
        "## Not A Replacement For The Eight-Layer Map\n"
        "text\n\n"
        "## Disclaimer-First Protocol\n"
        "This document contains executable governance components and higher-order interpretations. "
        "The latter explains the former; it does not automatically describe the currently enforced rule.\n\n"
        "## The A/B/C Firewall\n"
        "### A Layer: Mechanism Layer\n"
        "text\n\n"
        "### B Layer: Observable Layer\n"
        "text\n\n"
        "### C Layer: Interpretation Layer\n"
        "text\n\n"
        "## Required Writing Template\n"
        "text\n"
    )


def _write_valid_repo(tmp_path: Path) -> None:
    _write(tmp_path / verifier.DOCTRINE_PATH, _valid_doctrine())
    for relative_path in verifier.ENTRYPOINT_DOCS:
        doctrine_ref = (
            "architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md"
            if relative_path.startswith("docs/")
            else verifier.DOCTRINE_PATH
        )
        _write(
            tmp_path / relative_path,
            f"See `{doctrine_ref}` for the A/B/C firewall doctrine.\n",
        )


def test_build_report_ok_when_doctrine_and_entrypoints_are_present(tmp_path: Path) -> None:
    _write_valid_repo(tmp_path)

    payload = verifier.build_report(tmp_path)

    assert payload["ok"] is True
    assert payload["metrics"]["reference_count"] == len(verifier.ENTRYPOINT_DOCS)
    assert payload["metrics"]["prohibited_claim_count"] == 0
    assert payload["doctrine"]["required_headings"]["## The A/B/C Firewall"] is True


def test_build_report_fails_on_missing_reference_and_latent_claim(tmp_path: Path) -> None:
    _write_valid_repo(tmp_path)
    _write(tmp_path / "README.md", "ToneSoul can modify latent state before output.\n")

    payload = verifier.build_report(tmp_path)

    assert payload["ok"] is False
    assert any(
        "README.md missing A/B/C firewall doctrine reference" in issue
        for issue in payload["issues"]
    )
    assert any(
        "README.md contains 1 observable-shell boundary claim(s)" in issue
        for issue in payload["issues"]
    )
    readme_entry = next(item for item in payload["entrypoints"] if item["path"] == "README.md")
    assert readme_entry["prohibited_claim_count"] == 1


def test_main_writes_abc_firewall_artifacts(monkeypatch, tmp_path: Path) -> None:
    _write_valid_repo(tmp_path)
    monkeypatch.setattr(verifier, "DOCTRINE_PATH", verifier.DOCTRINE_PATH)

    exit_code = verifier.main(
        [
            "--repo-root",
            str(tmp_path),
            "--out-dir",
            "docs/status",
            "--strict",
        ]
    )

    assert exit_code == 0
    payload = json.loads(
        (tmp_path / "docs" / "status" / verifier.JSON_FILENAME).read_text(encoding="utf-8")
    )
    markdown = (tmp_path / "docs" / "status" / verifier.MARKDOWN_FILENAME).read_text(
        encoding="utf-8"
    )
    assert payload["ok"] is True
    assert "# A/B/C Firewall Latest" in markdown
