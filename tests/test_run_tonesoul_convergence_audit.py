from __future__ import annotations

import json
from pathlib import Path

import scripts.run_tonesoul_convergence_audit as runner


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_lines(path: Path, count: int) -> None:
    _write(path, "\n".join(f"line_{index}" for index in range(count)) + "\n")


def _seed_repo(tmp_path: Path) -> None:
    for rel_path, content in (
        ("README.md", "# Repo\n> Purpose: entry\n> Status: gateway\n"),
        ("README.zh-TW.md", "# Repo ZH\n> Purpose: entry\n> Status: gateway\n"),
        ("AI_ONBOARDING.md", "# AI\n> Purpose: entry\n> Status: operational\n"),
        ("docs/README.md", "# Docs\n> Purpose: guided gateway\n> Status: gateway\n"),
        ("docs/INDEX.md", "# Index\n> Purpose: full registry\n> Status: registry\n"),
        ("docs/AI_QUICKSTART.md", "# Quickstart\n> Purpose: operational\n> Status: ai entry\n"),
        (
            "docs/foundation/README.md",
            "# Foundation\n> Purpose: packet\n> Status: foundation layer\n",
        ),
        ("DESIGN.md", "# Design\n> Purpose: design center\n> Status: design center\n"),
        (
            "docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md",
            "# System Guide\n> Purpose: deep map\n> Status: deep system map\n",
        ),
        (
            "AGENTS.md",
            "# Agents\n張力張量: T = W × (E × D)\n上方為概念模型，非精確計算公式。\n",
        ),
        (
            "docs/GLOSSARY.md",
            "# Glossary\nT = W × (E × D)\n這是概念模型，計算以程式碼為準 `tonesoul/tension_engine.py`\n",
        ),
        (
            "docs/MATH_FOUNDATIONS.md",
            "# Math\n## 讀法契約\nT = base + w_len*f_len\n- **用在哪**：`tonesoul/tsr_metrics.py`\n- **可靠度**：heuristic\nf(t) = f0*e^(-lambda*t)\n",
        ),
    ):
        _write(tmp_path / rel_path, content)

    for directory in (
        "knowledge",
        "knowledge_base",
        "memory",
        "memory_base",
        "OpenClaw-Memory",
        "PARADOXES",
        "tests/fixtures/paradoxes",
        "tonesoul/memory",
    ):
        (tmp_path / directory).mkdir(parents=True, exist_ok=True)

    for rel_path in (
        "docs/architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md",
        "docs/architecture/TONESOUL_KNOWLEDGE_LAYER_BOUNDARY_CONTRACT.md",
        "docs/architecture/TONESOUL_COMPILED_KNOWLEDGE_LANDING_ZONE_SPEC.md",
        "docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md",
        "docs/architecture/PRIVATE_MEMORY_SHADOW_BOUNDARY_MAP.md",
        "docs/architecture/TONESOUL_R_MEMORY_STACK_RECOMMENDATION.md",
        "docs/architecture/PARADOX_FIXTURE_OWNERSHIP_MAP.md",
        "docs/architecture/TONESOUL_LAW_RUNTIME_BOUNDARY_CONTRACT.md",
    ):
        _write(tmp_path / rel_path, "# Contract\n")

    _write_lines(tmp_path / "tonesoul" / "unified_pipeline.py", 2400)
    _write_lines(tmp_path / "tonesoul" / "runtime_adapter.py", 2200)


def test_build_report_quantifies_four_pressure_points(tmp_path: Path, monkeypatch) -> None:
    _seed_repo(tmp_path)
    monkeypatch.setattr(
        runner,
        "_load_authority_metrics",
        lambda repo_root: {"group_count": 25, "tracked_file_count": 103},
    )

    payload = runner.build_report(tmp_path)
    areas = {area["key"]: area for area in payload["areas"]}

    assert areas["duplication"]["metrics"]["overview_surface_count"] >= 8
    assert areas["context_bloat"]["severity"] == "high"
    assert areas["pseudo_formulas"]["metrics"]["formula_hit_count"] >= 2
    assert areas["pseudo_formulas"]["metrics"]["labeled_formula_count"] >= 1
    assert areas["pseudo_formulas"]["metrics"]["owner_linked_formula_count"] >= 2
    assert areas["pseudo_formulas"]["metrics"]["locked_instruction_formula_hit_count"] >= 1
    assert areas["layer_confusion"]["metrics"]["family_count_with_multiple_surfaces"] >= 2


def test_main_writes_convergence_audit_artifacts(tmp_path: Path, monkeypatch) -> None:
    _seed_repo(tmp_path)
    monkeypatch.setattr(
        runner,
        "_load_authority_metrics",
        lambda repo_root: {"group_count": 4, "tracked_file_count": 12},
    )

    exit_code = runner.main(["--repo-root", str(tmp_path), "--out-dir", "docs/status"])

    assert exit_code == 0
    payload = json.loads(
        (tmp_path / "docs" / "status" / runner.JSON_FILENAME).read_text(encoding="utf-8")
    )
    markdown = (tmp_path / "docs" / "status" / runner.MARKDOWN_FILENAME).read_text(encoding="utf-8")

    assert payload["summary"]["area_count"] == 4
    assert "# ToneSoul Convergence Audit Latest" in markdown
    assert "## Context Bloat" in markdown
