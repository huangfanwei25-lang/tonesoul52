from __future__ import annotations

import json
from pathlib import Path

import scripts.run_claim_authority_snapshot as runner


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_report_merges_matrix_and_boundary_lookup(tmp_path: Path) -> None:
    _write(
        tmp_path / runner.MATRIX_PATH,
        """# Claim Authority Matrix

## Matrix: Core Governance

| # | Term | Authority | Status | Source Files | Rely? |
|---|------|-----------|--------|-------------|-------|
| 1 | **Aegis Shield** | runtime | hard runtime | aegis_shield.py, AXIOMS.json | Yes |
| 2 | **YuHun Gate** | law | runtime-adjacent | law/governance_core.md | Only with verification |
| 3 | **Honesty Contract** | law | runtime-adjacent | law/honesty_contract.md, benevolence.py | Only with verification |

## Top 10 Overclaiming Risks

| Risk | Term | What It Sounds Like | What It Actually Is |
|------|------|---------------------|---------------------|
| 1 | **YuHun Gate** | Callable gate | Design concept |
""",
    )
    _write(
        tmp_path / runner.BOUNDARY_PATH,
        """# Boundary Contract

## Decision Table: Quick Lookup

| Term | Category | One-Line Verdict |
|------|----------|-----------------|
| Aegis Shield | 1 | Real runtime surface |
| YuHun Gate | 2 | Design concept, not a callable runtime object |
| Honesty Contract | 1* | Partially implemented in BenevolenceFilter |
""",
    )

    payload = runner.build_report(tmp_path)

    assert payload["metrics"]["term_count"] == 3
    assert payload["metrics"]["high_confusion_term_count"] == 3
    assert payload["metrics"]["top_overclaiming_risk_count"] == 1
    assert payload["safe_reliance_terms"] == ["Aegis Shield"]

    yuhun_gate = next(term for term in payload["terms"] if term["term"] == "YuHun Gate")
    assert yuhun_gate["boundary_category_code"] == "2"
    assert yuhun_gate["boundary_category_label"] == runner.CATEGORY_LABELS["2"]

    honesty_contract = next(term for term in payload["terms"] if term["term"] == "Honesty Contract")
    assert honesty_contract["boundary_partially_implemented"] is True
    assert honesty_contract["source_files"] == ["law/honesty_contract.md", "benevolence.py"]


def test_main_writes_claim_authority_artifacts(tmp_path: Path) -> None:
    _write(
        tmp_path / runner.MATRIX_PATH,
        """# Claim Authority Matrix

## Matrix: Core Governance

| # | Term | Authority | Status | Source Files | Rely? |
|---|------|-----------|--------|-------------|-------|
| 1 | **Aegis Shield** | runtime | hard runtime | aegis_shield.py | Yes |
""",
    )
    _write(
        tmp_path / runner.BOUNDARY_PATH,
        """# Boundary Contract

## Decision Table: Quick Lookup

| Term | Category | One-Line Verdict |
|------|----------|-----------------|
| Aegis Shield | 1 | Real runtime surface |
""",
    )

    exit_code = runner.main(["--repo-root", str(tmp_path), "--out-dir", "docs/status"])

    assert exit_code == 0
    payload = json.loads(
        (tmp_path / "docs" / "status" / runner.JSON_FILENAME).read_text(encoding="utf-8")
    )
    markdown = (tmp_path / "docs" / "status" / runner.MARKDOWN_FILENAME).read_text(encoding="utf-8")

    assert payload["primary_status_line"].startswith("claim_authority_snapshot |")
    assert payload["metrics"]["term_count"] == 1
    assert "# Claim Authority Latest" in markdown
