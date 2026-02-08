from pathlib import Path

import scripts.verify_layer_boundaries as boundaries


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_find_violations_detects_forbidden_apps_import(tmp_path: Path) -> None:
    _write(tmp_path / "tonesoul" / "bad_module.py", "from apps.api.server import app\n")

    violations = boundaries.find_violations(
        project_root=tmp_path,
        roots=["tonesoul"],
        forbidden_prefixes=["apps"],
    )

    assert len(violations) == 1
    assert violations[0].path == "tonesoul/bad_module.py"
    assert violations[0].import_path == "apps.api.server"


def test_find_violations_ignores_apps_layer_files(tmp_path: Path) -> None:
    _write(
        tmp_path / "apps" / "api" / "server.py",
        "from tonesoul.council.runtime import CouncilRuntime\n",
    )

    violations = boundaries.find_violations(
        project_root=tmp_path,
        roots=["tonesoul", "tools", "memory"],
        forbidden_prefixes=["apps"],
    )

    assert violations == []


def test_find_violations_respects_allowed_import_exceptions(tmp_path: Path) -> None:
    _write(
        tmp_path / "memory" / "contradiction_detector.py",
        "from apps.core.memory_semantic_search import SemanticMemorySearch\n",
    )

    violations = boundaries.find_violations(
        project_root=tmp_path,
        roots=["memory"],
        forbidden_prefixes=["apps"],
        allowed_imports={("memory/contradiction_detector.py", "apps.core.memory_semantic_search")},
    )

    assert violations == []
