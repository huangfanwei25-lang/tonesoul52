from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_script_module():
    module_name = "test_split_task_archive_module"
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "split_task_archive.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _sample_task() -> str:
    return (
        "# Task\n\n"
        "## Phase 569: Legacy Cleanup (2026-03-01)\n"
        "- [x] archive docs\n"
        "**成功標準**: archived\n\n"
        "## Phase 570: Active Runtime Work (2026-03-02)\n"
        "- [ ] keep in task.md\n"
        "**成功標準**: active\n"
    )


def test_parse_phases_extracts_number_title_date_and_body() -> None:
    module = _load_script_module()
    phases = module.parse_phases(_sample_task())

    assert [phase["number"] for phase in phases] == [569, 570]
    assert phases[0]["title"] == "Legacy Cleanup"
    assert phases[1]["date"] == "2026-03-02"
    assert phases[0]["body"].startswith("- [x] archive docs")


def test_archive_label_groups_by_hundred_range() -> None:
    module = _load_script_module()

    assert module.archive_label(1) == "task_archive_phase_001-100.md"
    assert module.archive_label(100) == "task_archive_phase_001-100.md"
    assert module.archive_label(101) == "task_archive_phase_101-200.md"
    assert module.archive_label(570) == "task_archive_phase_501-600.md"


def test_main_dry_run_reports_without_writing(tmp_path: Path, capsys) -> None:
    module = _load_script_module()
    task_file = tmp_path / "task.md"
    chronicles_dir = tmp_path / "docs" / "chronicles"
    task_file.write_text(_sample_task(), encoding="utf-8")

    module.main(["--dry-run"], task_file=task_file, chronicles_dir=chronicles_dir)
    output = capsys.readouterr().out

    assert "Parsed 2 phases" in output
    assert "[dry-run] no files written." in output
    assert not chronicles_dir.exists()


def test_main_writes_archive_and_rewrites_task(tmp_path: Path, capsys) -> None:
    module = _load_script_module()
    task_file = tmp_path / "task.md"
    chronicles_dir = tmp_path / "docs" / "chronicles"
    task_file.write_text(_sample_task(), encoding="utf-8")

    module.main([], task_file=task_file, chronicles_dir=chronicles_dir)
    output = capsys.readouterr().out

    archive_file = chronicles_dir / "task_archive_phase_501-600.md"
    assert archive_file.exists()
    assert "Phase 569-569" in archive_file.read_text(encoding="utf-8")
    rewritten_task = task_file.read_text(encoding="utf-8")
    assert "## Phase 570: Active Runtime Work" in rewritten_task
    assert "## Phase 569: Legacy Cleanup" not in rewritten_task
    assert "Archive Index" in rewritten_task
    assert "Updated: task.md (1 active phases)" in output
