"""Tests for scripts/analyze_codebase_graph.py — full-AST codebase graph analyzer."""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Import the module under test
# ---------------------------------------------------------------------------
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import analyze_codebase_graph as acg  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture()
def tiny_repo(tmp_path: Path) -> Path:
    """Create a minimal fake package for testing."""
    pkg = tmp_path / "mypkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")

    # core.py — imports utils
    (pkg / "core.py").write_text(
        "from mypkg.utils import helper\n"
        "from mypkg.gate import Gate\n"
        "\n"
        "class Engine:\n"
        "    pass\n"
        "\n"
        "def run():\n"
        "    pass\n"
        "\n"
        "def start():\n"
        "    pass\n",
        encoding="utf-8",
    )

    # utils.py — standalone
    (pkg / "utils.py").write_text(
        "def helper():\n" "    return 42\n",
        encoding="utf-8",
    )

    # gate.py — imports utils (creates cycle potential)
    (pkg / "gate.py").write_text(
        "from mypkg.utils import helper\n" "\n" "class Gate:\n" "    pass\n",
        encoding="utf-8",
    )

    # orphan.py — nobody imports this
    (pkg / "orphan.py").write_text(
        "def unused():\n" "    pass\n",
        encoding="utf-8",
    )

    return tmp_path


@pytest.fixture()
def cycle_repo(tmp_path: Path) -> Path:
    """Create a package with a circular dependency."""
    pkg = tmp_path / "cpkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")

    (pkg / "alpha.py").write_text(
        "from cpkg.beta import b_func\n" "def a_func(): pass\n",
        encoding="utf-8",
    )
    (pkg / "beta.py").write_text(
        "from cpkg.alpha import a_func\n" "def b_func(): pass\n",
        encoding="utf-8",
    )
    return tmp_path


# ---------------------------------------------------------------------------
# Tests: scan_module
# ---------------------------------------------------------------------------
class TestScanModule:
    def test_basic_scan(self, tiny_repo: Path) -> None:
        info = acg.scan_module(tiny_repo / "mypkg" / "core.py", "mypkg", tiny_repo)
        assert info.module_name == "mypkg.core"
        assert info.subpackage == "(root)"
        assert info.classes == 1
        assert info.functions == 2
        assert "mypkg.utils" in info.imports_out
        assert "mypkg.gate" in info.imports_out
        assert info.lines > 0

    def test_root_module_layer_from_curated_map(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Root-level modules (no subpackage) pick up layer from ROOT_MODULE_LAYER."""
        pkg = tmp_path / "mp"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("", encoding="utf-8")
        (pkg / "adaptive_gate.py").write_text("def run(): pass\n", encoding="utf-8")
        (pkg / "runtime_adapter.py").write_text("def run(): pass\n", encoding="utf-8")
        (pkg / "ystm_demo.py").write_text("def run(): pass\n", encoding="utf-8")
        (pkg / "novel_feature.py").write_text("def run(): pass\n", encoding="utf-8")

        monkeypatch.setitem(acg.ROOT_MODULE_LAYER, "adaptive_gate", "governance")
        monkeypatch.setitem(acg.ROOT_MODULE_LAYER, "runtime_adapter", "pipeline")
        monkeypatch.setitem(acg.ROOT_MODULE_LAYER, "ystm_demo", "domain")

        gate_info = acg.scan_module(pkg / "adaptive_gate.py", "mp", tmp_path)
        runtime_info = acg.scan_module(pkg / "runtime_adapter.py", "mp", tmp_path)
        demo_info = acg.scan_module(pkg / "ystm_demo.py", "mp", tmp_path)
        novel_info = acg.scan_module(pkg / "novel_feature.py", "mp", tmp_path)

        assert gate_info.subpackage == "(root)"
        assert gate_info.layer == "governance"
        assert runtime_info.layer == "pipeline"
        assert demo_info.layer == "domain"
        assert novel_info.layer == "uncategorized"  # unmapped → honest gap

    def test_module_layer_override_trumps_subpackage(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Modules in MODULE_LAYER_OVERRIDES use the override even when
        their subpackage would otherwise force a different layer."""
        pkg = tmp_path / "op"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("", encoding="utf-8")
        dom = pkg / "domainish"
        dom.mkdir()
        (dom / "__init__.py").write_text("", encoding="utf-8")
        (dom / "types.py").write_text(
            "from dataclasses import dataclass\n" "@dataclass\n" "class Row:\n" "    x: int\n",
            encoding="utf-8",
        )

        monkeypatch.setitem(acg.LAYER_MAP, "domainish", "domain")
        monkeypatch.setitem(acg.MODULE_LAYER_OVERRIDES, "op.domainish.types", "shared")

        info = acg.scan_module(dom / "types.py", "op", tmp_path)
        assert info.subpackage == "domainish"
        assert info.layer == "shared", (
            "MODULE_LAYER_OVERRIDES must beat LAYER_MAP for modules that are "
            "physically nested in a subpackage but are in fact cross-cutting."
        )

    def test_self_declaration_trumps_everything(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Module-level __ts_layer__ / __ts_purpose__ override every fallback source.

        The self-declared layer must beat MODULE_LAYER_OVERRIDES, LAYER_MAP, and
        ROOT_MODULE_LAYER. layer_source must be 'self_declared' and purpose must
        surface in the scan.
        """
        pkg = tmp_path / "sd"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("", encoding="utf-8")

        sub = pkg / "forced_domain"
        sub.mkdir()
        (sub / "__init__.py").write_text("", encoding="utf-8")
        (sub / "claimer.py").write_text(
            '__ts_layer__ = "governance"\n'
            '__ts_purpose__ = "Claims governance layer despite domain subpackage."\n'
            "def run(): pass\n",
            encoding="utf-8",
        )

        monkeypatch.setitem(acg.LAYER_MAP, "forced_domain", "domain")
        monkeypatch.setitem(acg.MODULE_LAYER_OVERRIDES, "sd.forced_domain.claimer", "shared")

        info = acg.scan_module(sub / "claimer.py", "sd", tmp_path)
        assert info.layer == "governance"
        assert info.layer_source == "self_declared"
        assert "governance layer" in info.purpose

    def test_missing_self_declaration_falls_back(self, tmp_path: Path) -> None:
        """Modules without __ts_layer__ must fall through to the existing chain."""
        pkg = tmp_path / "nd"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("", encoding="utf-8")
        sub = pkg / "council"
        sub.mkdir()
        (sub / "__init__.py").write_text("", encoding="utf-8")
        (sub / "plain.py").write_text("def noop(): pass\n", encoding="utf-8")

        info = acg.scan_module(sub / "plain.py", "nd", tmp_path)
        assert info.layer_source != "self_declared"
        assert info.purpose == ""

    def test_real_tonesoul_root_modules_are_classified(self) -> None:
        """Guard: every shipped tonesoul/*.py root module must live in ROOT_MODULE_LAYER.

        Stops the body map from silently regrowing an 'uncategorized' pile when
        new root modules land without a layer decision.
        """
        repo_root = Path(__file__).resolve().parents[1]
        tonesoul_root = repo_root / "tonesoul"
        if not tonesoul_root.is_dir():
            pytest.skip("tonesoul package not present in this checkout")

        unmapped: list[str] = []
        for path in tonesoul_root.glob("*.py"):
            if path.name == "__init__.py":
                basename = "tonesoul"
            else:
                basename = path.stem
            if basename not in acg.ROOT_MODULE_LAYER:
                unmapped.append(basename)

        assert not unmapped, (
            "New root-level tonesoul modules lack a ROOT_MODULE_LAYER entry: "
            f"{sorted(unmapped)}. Add each to scripts/analyze_codebase_graph.py "
            "so the body map stays honest."
        )

    def test_init_module_name(self, tiny_repo: Path) -> None:
        info = acg.scan_module(tiny_repo / "mypkg" / "__init__.py", "mypkg", tiny_repo)
        assert info.module_name == "mypkg"

    def test_syntax_error_handled(self, tmp_path: Path) -> None:
        pkg = tmp_path / "bad"
        pkg.mkdir()
        (pkg / "broken.py").write_text("def f(\n", encoding="utf-8")
        info = acg.scan_module(pkg / "broken.py", "bad", tmp_path)
        assert info.lines > 0
        assert info.classes == 0
        assert info.functions == 0


# ---------------------------------------------------------------------------
# Tests: scan_all_modules
# ---------------------------------------------------------------------------
class TestScanAllModules:
    def test_discovers_all_files(self, tiny_repo: Path) -> None:
        modules = acg.scan_all_modules("mypkg", tiny_repo)
        names = set(modules.keys())
        assert "mypkg.core" in names
        assert "mypkg.utils" in names
        assert "mypkg.gate" in names
        assert "mypkg.orphan" in names
        assert "mypkg" in names  # __init__.py

    def test_skips_pycache(self, tiny_repo: Path) -> None:
        cache_dir = tiny_repo / "mypkg" / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "junk.py").write_text("x = 1\n", encoding="utf-8")
        modules = acg.scan_all_modules("mypkg", tiny_repo)
        assert not any("pycache" in name for name in modules)


# ---------------------------------------------------------------------------
# Tests: build_edges + degree
# ---------------------------------------------------------------------------
class TestEdgesAndDegree:
    def test_edge_count(self, tiny_repo: Path) -> None:
        modules = acg.scan_all_modules("mypkg", tiny_repo)
        edges = acg.build_edges(modules)
        # core -> utils, core -> gate, gate -> utils = 3 edges
        assert len(edges) == 3

    def test_degree_computation(self, tiny_repo: Path) -> None:
        modules = acg.scan_all_modules("mypkg", tiny_repo)
        edges = acg.build_edges(modules)
        degree = acg.compute_degree(modules, edges)

        # utils: in=2 (core+gate), out=0
        assert degree["mypkg.utils"]["in"] == 2
        assert degree["mypkg.utils"]["out"] == 0

        # core: in=0, out=2
        assert degree["mypkg.core"]["in"] == 0
        assert degree["mypkg.core"]["out"] == 2

        # orphan: in=0, out=0
        assert degree["mypkg.orphan"]["in"] == 0
        assert degree["mypkg.orphan"]["out"] == 0


# ---------------------------------------------------------------------------
# Tests: cycle detection
# ---------------------------------------------------------------------------
class TestCycleDetection:
    def test_no_cycles_in_tiny(self, tiny_repo: Path) -> None:
        modules = acg.scan_all_modules("mypkg", tiny_repo)
        edges = acg.build_edges(modules)
        cycles = acg.find_cycles(edges)
        assert len(cycles) == 0

    def test_finds_cycle(self, cycle_repo: Path) -> None:
        modules = acg.scan_all_modules("cpkg", cycle_repo)
        edges = acg.build_edges(modules)
        cycles = acg.find_cycles(edges)
        assert len(cycles) >= 1
        # The cycle should contain both alpha and beta
        all_in_cycles = set()
        for c in cycles:
            all_in_cycles.update(c.cycle)
        assert "cpkg.alpha" in all_in_cycles
        assert "cpkg.beta" in all_in_cycles


# ---------------------------------------------------------------------------
# Tests: orphan detection
# ---------------------------------------------------------------------------
class TestOrphanDetection:
    def test_finds_orphans(self, tiny_repo: Path) -> None:
        modules = acg.scan_all_modules("mypkg", tiny_repo)
        edges = acg.build_edges(modules)
        degree = acg.compute_degree(modules, edges)
        orphans = acg.find_orphans(modules, degree, root_package="mypkg", repo_root=tiny_repo)
        assert "mypkg.orphan" in orphans
        assert "mypkg.core" in orphans  # nobody imports core either

    def test_non_orphan_excluded(self, tiny_repo: Path) -> None:
        modules = acg.scan_all_modules("mypkg", tiny_repo)
        edges = acg.build_edges(modules)
        degree = acg.compute_degree(modules, edges)
        orphans = acg.find_orphans(modules, degree, root_package="mypkg", repo_root=tiny_repo)
        assert "mypkg.utils" not in orphans  # imported by core and gate

    def test_entry_point_excluded(self, tiny_repo: Path) -> None:
        """CLI entry points (argparse) should not be flagged as orphans."""
        pkg = tiny_repo / "mypkg"
        (pkg / "cli_tool.py").write_text(
            "import argparse\n"
            "def main():\n"
            "    parser = argparse.ArgumentParser()\n"
            "    parser.parse_args()\n"
            'if __name__ == "__main__":\n'
            "    main()\n",
            encoding="utf-8",
        )
        modules = acg.scan_all_modules("mypkg", tiny_repo)
        edges = acg.build_edges(modules)
        degree = acg.compute_degree(modules, edges)
        orphans = acg.find_orphans(modules, degree, root_package="mypkg", repo_root=tiny_repo)
        assert "mypkg.cli_tool" not in orphans

    def test_externally_referenced_excluded(self, tiny_repo: Path) -> None:
        """Modules referenced by tests/ should not be flagged as orphans."""
        tests_dir = tiny_repo / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_orphan.py").write_text(
            "from mypkg.orphan import unused\n",
            encoding="utf-8",
        )
        modules = acg.scan_all_modules("mypkg", tiny_repo)
        edges = acg.build_edges(modules)
        degree = acg.compute_degree(modules, edges)
        orphans = acg.find_orphans(modules, degree, root_package="mypkg", repo_root=tiny_repo)
        assert "mypkg.orphan" not in orphans  # referenced by tests/


# ---------------------------------------------------------------------------
# Tests: subpackage coupling
# ---------------------------------------------------------------------------
class TestSubpackageCoupling:
    def test_coupling_matrix(self, tiny_repo: Path) -> None:
        modules = acg.scan_all_modules("mypkg", tiny_repo)
        edges = acg.build_edges(modules)
        coupling = acg.compute_subpackage_coupling(modules, edges)
        # All modules are in (root), so all edges are internal
        assert "(root)" in coupling
        assert coupling["(root)"]["(root)"] == 3


# ---------------------------------------------------------------------------
# Tests: community detection
# ---------------------------------------------------------------------------
class TestCommunityDetection:
    def test_converges(self, tiny_repo: Path) -> None:
        modules = acg.scan_all_modules("mypkg", tiny_repo)
        edges = acg.build_edges(modules)
        communities = acg.detect_communities(modules, edges)
        assert len(communities) == len(modules)
        # All should converge to same community (single package)
        labels = set(communities.values())
        assert len(labels) == 1


# ---------------------------------------------------------------------------
# Tests: layer violations
# ---------------------------------------------------------------------------
class TestLayerViolations:
    def test_no_violations_in_tiny(self, tiny_repo: Path) -> None:
        """All modules are uncategorized → no violations."""
        modules = acg.scan_all_modules("mypkg", tiny_repo)
        edges = acg.build_edges(modules)
        violations = acg.find_layer_violations(modules, edges)
        assert len(violations) == 0

    def test_detects_violation(self, tmp_path: Path) -> None:
        """Create a scenario where infra imports governance (upward dep)."""
        pkg = tmp_path / "tp"
        pkg.mkdir()
        (pkg / "__init__.py").write_text("", encoding="utf-8")

        infra = pkg / "backends"
        infra.mkdir()
        (infra / "__init__.py").write_text("", encoding="utf-8")
        (infra / "db.py").write_text(
            "from tp.governance.kernel import GovernanceKernel\n",
            encoding="utf-8",
        )

        gov = pkg / "governance"
        gov.mkdir()
        (gov / "__init__.py").write_text("", encoding="utf-8")
        (gov / "kernel.py").write_text(
            "class GovernanceKernel:\n    pass\n",
            encoding="utf-8",
        )

        modules = acg.scan_all_modules("tp", tmp_path)
        edges = acg.build_edges(modules)
        violations = acg.find_layer_violations(modules, edges)
        assert len(violations) == 1
        assert violations[0].source_layer == "infrastructure"
        assert violations[0].target_layer == "governance"


# ---------------------------------------------------------------------------
# Tests: full report
# ---------------------------------------------------------------------------
class TestFullReport:
    def test_report_structure(self, tiny_repo: Path) -> None:
        modules = acg.scan_all_modules("mypkg", tiny_repo)
        edges = acg.build_edges(modules)
        degree = acg.compute_degree(modules, edges)
        cycles = acg.find_cycles(edges)
        violations = acg.find_layer_violations(modules, edges)
        orphans = acg.find_orphans(modules, degree)
        coupling = acg.compute_subpackage_coupling(modules, edges)
        communities = acg.detect_communities(modules, edges)

        report = acg.build_report(
            modules,
            edges,
            degree,
            cycles,
            violations,
            orphans,
            coupling,
            communities,
            "mypkg",
        )

        assert "summary" in report
        assert "god_nodes" in report
        assert "cycles" in report
        assert "orphans" in report
        assert report["summary"]["total_modules"] == 5  # init + 4 files
        assert report["summary"]["total_edges"] == 3
        assert report["summary"]["total_cycles"] == 0

        # JSON serializable
        json.dumps(report, ensure_ascii=False)

    def test_markdown_renders(self, tiny_repo: Path) -> None:
        modules = acg.scan_all_modules("mypkg", tiny_repo)
        edges = acg.build_edges(modules)
        degree = acg.compute_degree(modules, edges)
        cycles = acg.find_cycles(edges)
        violations = acg.find_layer_violations(modules, edges)
        orphans = acg.find_orphans(modules, degree)
        coupling = acg.compute_subpackage_coupling(modules, edges)
        communities = acg.detect_communities(modules, edges)

        report = acg.build_report(
            modules,
            edges,
            degree,
            cycles,
            violations,
            orphans,
            coupling,
            communities,
            "mypkg",
        )
        md = acg.render_markdown(report)
        assert "# ToneSoul Codebase Graph Analysis" in md
        assert "God Nodes" in md
        assert "mypkg.utils" in md or "utils" in md


# ---------------------------------------------------------------------------
# Tests: CLI
# ---------------------------------------------------------------------------
class TestCLI:
    def test_json_only_mode(self, tiny_repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
        ret = acg.main(
            [
                "--root",
                "mypkg",
                "--repo-root",
                str(tiny_repo),
                "--json-only",
            ]
        )
        assert ret == 0
        output = capsys.readouterr().out
        data = json.loads(output)
        assert data["summary"]["total_modules"] == 5

    def test_file_output_mode(self, tiny_repo: Path) -> None:
        out_dir = tiny_repo / "output"
        ret = acg.main(
            [
                "--root",
                "mypkg",
                "--repo-root",
                str(tiny_repo),
                "--output-dir",
                str(out_dir),
            ]
        )
        assert ret == 0
        assert (out_dir / "codebase_graph_latest.json").exists()
        assert (out_dir / "codebase_graph_latest.md").exists()

    def test_empty_package_fails(self, tmp_path: Path) -> None:
        empty = tmp_path / "emptypkg"
        empty.mkdir()
        ret = acg.main(
            [
                "--root",
                "emptypkg",
                "--repo-root",
                str(tmp_path),
                "--json-only",
            ]
        )
        assert ret == 1
