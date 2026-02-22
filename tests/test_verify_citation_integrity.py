from __future__ import annotations

from pathlib import Path

import scripts.verify_citation_integrity as citation


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_default_mainline_docs(repo_root: Path) -> None:
    for rel in citation.DEFAULT_MAINLINE_PATHS:
        _write(repo_root / rel, "# placeholder\n")


def test_extract_arxiv_entries_parses_markdown_reference() -> None:
    text = (
        "1. Zhang, A. L. (2025). *Recursive Language Models*. "
        "arXiv:2512.24601. [Concept / Not peer-reviewed]\n"
    )
    entries = citation._extract_arxiv_entries(text)
    assert len(entries) == 1
    assert entries[0]["arxiv_id"] == "2512.24601"
    assert entries[0]["title"] == "Recursive Language Models"


def test_build_report_passes_with_markers_and_known_titles(tmp_path: Path) -> None:
    _write(
        tmp_path / "docs" / "PHILOSOPHY.md",
        (
            "1. Zhang (2025). *Recursive Language Models*. arXiv:2512.24601. "
            "[Concept / Not peer-reviewed]\n"
            "2. Liang (2024). *Encouraging Divergent Thinking in Large Language Models through "
            "Multi-Agent Debate*. arXiv:2305.19118. [Concept / Not peer-reviewed]\n"
        ),
    )
    _write(
        tmp_path / "docs" / "PHILOSOPHY_EN.md",
        (
            "1. Zhang (2025). *Recursive Language Models*. arXiv:2512.24601. "
            "[Concept / Not peer-reviewed]\n"
        ),
    )
    _write_default_mainline_docs(tmp_path)

    report = citation.build_report(
        repo_root=tmp_path,
        philosophy_paths=citation.DEFAULT_PHILOSOPHY_PATHS,
        mainline_paths=citation.DEFAULT_MAINLINE_PATHS,
    )

    assert report["overall_ok"] is True
    assert report["metrics"]["issue_count"] == 0


def test_build_report_fails_when_concept_marker_missing(tmp_path: Path) -> None:
    _write(
        tmp_path / "docs" / "PHILOSOPHY.md",
        "1. Zhang (2025). *Recursive Language Models*. arXiv:2512.24601.\n",
    )
    _write(tmp_path / "docs" / "PHILOSOPHY_EN.md", "# placeholder\n")
    _write_default_mainline_docs(tmp_path)

    report = citation.build_report(
        repo_root=tmp_path,
        philosophy_paths=citation.DEFAULT_PHILOSOPHY_PATHS,
        mainline_paths=citation.DEFAULT_MAINLINE_PATHS,
    )

    assert report["overall_ok"] is False
    assert any("missing 'Concept / Not peer-reviewed'" in issue for issue in report["issues"])


def test_build_report_fails_on_known_arxiv_title_mismatch(tmp_path: Path) -> None:
    _write(
        tmp_path / "docs" / "PHILOSOPHY.md",
        (
            "1. Example (2025). *Wrong Paper Title*. arXiv:2512.24601. "
            "[Concept / Not peer-reviewed]\n"
        ),
    )
    _write(tmp_path / "docs" / "PHILOSOPHY_EN.md", "# placeholder\n")
    _write_default_mainline_docs(tmp_path)

    report = citation.build_report(
        repo_root=tmp_path,
        philosophy_paths=citation.DEFAULT_PHILOSOPHY_PATHS,
        mainline_paths=citation.DEFAULT_MAINLINE_PATHS,
    )

    assert report["overall_ok"] is False
    assert any("title mismatch for arXiv:2512.24601" in issue for issue in report["issues"])


def test_build_report_fails_when_mainline_contains_arxiv(tmp_path: Path) -> None:
    _write(tmp_path / "docs" / "PHILOSOPHY.md", "# placeholder\n")
    _write(tmp_path / "docs" / "PHILOSOPHY_EN.md", "# placeholder\n")
    _write_default_mainline_docs(tmp_path)
    _write(
        tmp_path / "docs" / "ARCHITECTURE_BOUNDARIES.md",
        "Mainline reference arXiv:2512.24601 should fail.\n",
    )

    report = citation.build_report(
        repo_root=tmp_path,
        philosophy_paths=citation.DEFAULT_PHILOSOPHY_PATHS,
        mainline_paths=citation.DEFAULT_MAINLINE_PATHS,
    )

    assert report["overall_ok"] is False
    assert any(
        "mainline docs should not directly cite arXiv preprints" in issue
        for issue in report["issues"]
    )
