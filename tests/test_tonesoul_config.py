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
