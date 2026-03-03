from pathlib import Path

import scripts.verify_stale_command_refs as verify_stale_command_refs


def test_build_report_detects_removed_cli_wrapper_reference(tmp_path: Path) -> None:
    source_path = tmp_path / "tonesoul" / "sample.py"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text(
        "from tonesoul.cli.run_audit import main\n",
        encoding="utf-8",
    )

    payload = verify_stale_command_refs.build_report(
        repo_root=tmp_path,
        scan_targets=("tonesoul",),
        extensions=(".py",),
        excludes=(),
    )

    assert payload["overall_ok"] is False
    assert payload["match_count"] == 1
    assert payload["matches"][0]["pattern_id"] == "legacy_cli_wrapper_module"


def test_build_report_ignores_markdown_by_default_extension_filter(tmp_path: Path) -> None:
    doc_path = tmp_path / "tonesoul" / "notes.md"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(
        "legacy command python -m tonesoul52.run_ystm_demo\n",
        encoding="utf-8",
    )

    payload = verify_stale_command_refs.build_report(
        repo_root=tmp_path,
        scan_targets=("tonesoul",),
        excludes=(),
    )

    assert payload["overall_ok"] is True
    assert payload["match_count"] == 0
