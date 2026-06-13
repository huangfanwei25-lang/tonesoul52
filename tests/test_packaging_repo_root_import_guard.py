"""Packaging guard: tonesoul/ must be importable in pip-only environments.

Failure history (Reality Sync PR1, 2026-06-13): tonesoul shipped to PyPI with
11 module-level imports of the repo-root ``memory`` package, which is not in
the wheel (pyproject packages.find include=["tonesoul*"]). Result: every
pip-only install had a broken council subsystem — ``import
tonesoul.council.types`` raised ModuleNotFoundError, and ``ts council --help``
crashed before argparse. This guard makes that class of regression fail in CI
instead of failing on the first external user.

Rules enforced:
1. No module-level (unconditional, import-time) import of repo-only root
   packages anywhere under tonesoul/.
2. Lazy (function/method-level) imports of repo-only roots are allowed only
   when wrapped in a try/except that handles ImportError, so the call path
   fails with an explicit boundary error rather than a bare
   ModuleNotFoundError.
"""

from __future__ import annotations

import ast
from pathlib import Path

TONESOUL_ROOT = Path(__file__).resolve().parent.parent / "tonesoul"

# Repo-root packages/dirs that are NOT shipped in the tonesoul52 wheel.
REPO_ONLY_ROOTS = frozenset(
    {
        "memory",
        "tools",
        "scripts",
        "apps",
        "api",
        "tests",
        "examples",
        "games",
        "experiments",
        "integrations",
        "extensions",
        "data",
        "knowledge",
        "knowledge_base",
        "memory_base",
        "spec",
    }
)

_IMPORT_ERROR_NAMES = {"ImportError", "ModuleNotFoundError", "Exception", "BaseException"}


def _root_of(node: ast.AST) -> list[str]:
    """Return repo-only root names referenced by an import node."""
    roots: list[str] = []
    if isinstance(node, ast.Import):
        for alias in node.names:
            root = alias.name.split(".")[0]
            if root in REPO_ONLY_ROOTS:
                roots.append(root)
    elif isinstance(node, ast.ImportFrom):
        if node.level == 0 and node.module:  # absolute imports only
            root = node.module.split(".")[0]
            if root in REPO_ONLY_ROOTS:
                roots.append(root)
    return roots


def _handler_catches_import_error(handler: ast.ExceptHandler) -> bool:
    t = handler.type
    if t is None:  # bare except
        return True
    names = t.elts if isinstance(t, ast.Tuple) else [t]
    for name in names:
        if isinstance(name, ast.Name) and name.id in _IMPORT_ERROR_NAMES:
            return True
        if isinstance(name, ast.Attribute) and name.attr in _IMPORT_ERROR_NAMES:
            return True
    return False


def _collect_violations() -> tuple[list[str], list[str]]:
    module_level: list[str] = []
    unguarded_lazy: list[str] = []
    for path in sorted(TONESOUL_ROOT.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        parents: dict[ast.AST, ast.AST] = {}
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                parents[child] = parent
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            roots = _root_of(node)
            if not roots:
                continue
            # climb ancestors: module-level? guarded by try/except ImportError?
            guarded = False
            in_function = False
            cursor: ast.AST | None = node
            while cursor is not None:
                cursor = parents.get(cursor)
                if isinstance(cursor, ast.Try) and any(
                    _handler_catches_import_error(h) for h in cursor.handlers
                ):
                    guarded = True
                if isinstance(cursor, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    in_function = True
            rel = path.relative_to(TONESOUL_ROOT.parent)
            site = f"{rel}:{node.lineno} -> {', '.join(roots)}"
            if not in_function and not guarded:
                module_level.append(site)
            elif in_function and not guarded:
                unguarded_lazy.append(site)
    return module_level, unguarded_lazy


def test_no_module_level_repo_root_imports():
    module_level, _ = _collect_violations()
    assert not module_level, (
        "tonesoul/ has module-level imports of repo-only packages — these break "
        "every pip-only install at import time (the PR1 packaging-truth bug class):\n"
        + "\n".join(module_level)
    )


def test_lazy_repo_root_imports_are_guarded():
    _, unguarded_lazy = _collect_violations()
    assert not unguarded_lazy, (
        "tonesoul/ has lazy imports of repo-only packages without ImportError "
        "guards — these fail with a bare ModuleNotFoundError in pip-only "
        "environments instead of an explicit boundary error:\n" + "\n".join(unguarded_lazy)
    )
