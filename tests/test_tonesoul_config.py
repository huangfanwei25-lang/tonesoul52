from __future__ import annotations

from pathlib import Path

from tonesoul import config as config_mod
from tonesoul.config import EntryPoint


def test_list_workspace_dirs_filters_ignored_directories(tmp_path, monkeypatch):
    for name in ("apps", "docs", "legacy", ".git", ".venv"):
        (tmp_path / name).mkdir()

    monkeypatch.setattr(config_mod, "WORKSPACE_ROOT", str(tmp_path))

    dirs = config_mod.list_workspace_dirs()

    assert dirs == [str(tmp_path / "apps"), str(tmp_path / "docs"), str(tmp_path / "memory")]


def test_resolve_readme_prefers_standard_files(tmp_path):
    folder = tmp_path / "project"
    folder.mkdir()
    (folder / "HANDOFF.md").write_text("handoff", encoding="utf-8")
    (folder / "README_DEV.md").write_text("dev", encoding="utf-8")
    (folder / "README.md").write_text("readme", encoding="utf-8")

    assert config_mod.resolve_readme(str(folder)) == str(folder / "README.md")
    (folder / "README.md").unlink()
    assert config_mod.resolve_readme(str(folder)) == str(folder / "README_DEV.md")


def test_entrypoints_index_returns_named_entrypoints():
    index = config_mod.entrypoints_index()

    assert isinstance(index["dashboard"], EntryPoint)
    assert "yuhun_cli" in index
    assert index["dashboard"].path.endswith(str(Path("apps") / "dashboard" / "run_dashboard.py"))


# ─────────────────────────────────────────────
# Extended coverage
# ─────────────────────────────────────────────


class TestResolveReadme:
    def test_none_when_no_files(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        assert config_mod.resolve_readme(str(empty)) is None

    def test_handoff_md_is_last_fallback(self, tmp_path):
        folder = tmp_path / "f"
        folder.mkdir()
        (folder / "HANDOFF.md").write_text("h", encoding="utf-8")
        assert config_mod.resolve_readme(str(folder)) == str(folder / "HANDOFF.md")


class TestListWorkspaceDirs:
    def test_returns_sorted_list(self, tmp_path, monkeypatch):
        for name in ("zebra", "alpha", "mango"):
            (tmp_path / name).mkdir()
        monkeypatch.setattr(config_mod, "WORKSPACE_ROOT", str(tmp_path))
        dirs = config_mod.list_workspace_dirs()
        names = [Path(d).name for d in dirs]
        assert names == sorted(names)

    def test_files_not_included(self, tmp_path, monkeypatch):
        (tmp_path / "subdir").mkdir()
        (tmp_path / "file.txt").write_text("x", encoding="utf-8")
        monkeypatch.setattr(config_mod, "WORKSPACE_ROOT", str(tmp_path))
        dirs = config_mod.list_workspace_dirs()
        assert all(Path(d).is_dir() for d in dirs)


class TestEntryPoint:
    def test_frozen_dataclass_rejects_mutation(self):
        ep = EntryPoint(name="test", path="/some/path")
        import pytest
        with pytest.raises((AttributeError, TypeError)):
            ep.name = "changed"

    def test_default_command_is_none(self):
        ep = EntryPoint(name="x", path="/x")
        assert ep.command is None
        assert ep.notes is None

    def test_equality_by_value(self):
        a = EntryPoint(name="x", path="/x", command="cmd")
        b = EntryPoint(name="x", path="/x", command="cmd")
        assert a == b


class TestEntrypointsIndex:
    def test_all_known_entrypoints_present(self):
        index = config_mod.entrypoints_index()
        for ep in config_mod.KNOWN_ENTRYPOINTS:
            assert ep.name in index

    def test_values_are_entrypoint_instances(self):
        for ep in config_mod.entrypoints_index().values():
            assert isinstance(ep, EntryPoint)
