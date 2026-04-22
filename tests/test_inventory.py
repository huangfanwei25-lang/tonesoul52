"""Tests for tonesoul.inventory — workspace and entrypoint inventory."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from tonesoul import config as config_mod
from tonesoul import inventory as inv_mod


class TestBuildInventory:
    def test_returns_list_of_dicts(self, tmp_path, monkeypatch):
        (tmp_path / "apps").mkdir()
        monkeypatch.setattr(config_mod, "WORKSPACE_ROOT", str(tmp_path))
        monkeypatch.setattr(inv_mod, "list_workspace_dirs", config_mod.list_workspace_dirs)

        result = inv_mod.build_inventory()

        assert isinstance(result, list)
        assert all(isinstance(item, dict) for item in result)

    def test_each_item_has_required_keys(self, tmp_path, monkeypatch):
        (tmp_path / "apps").mkdir()
        monkeypatch.setattr(config_mod, "WORKSPACE_ROOT", str(tmp_path))
        monkeypatch.setattr(inv_mod, "list_workspace_dirs", config_mod.list_workspace_dirs)

        result = inv_mod.build_inventory()

        for item in result:
            for key in ("name", "path", "has_git", "readme", "notes"):
                assert key in item

    def test_tonesoul_directory_gets_note(self, tmp_path, monkeypatch):
        tonesoul_dir = tmp_path / "tonesoul_workspace"
        tonesoul_dir.mkdir()
        monkeypatch.setattr(config_mod, "WORKSPACE_ROOT", str(tmp_path))
        monkeypatch.setattr(inv_mod, "list_workspace_dirs", config_mod.list_workspace_dirs)

        result = inv_mod.build_inventory()
        tonesoul_items = [i for i in result if i["name"].startswith("tonesoul")]
        assert all("ToneSoul-related workspace" in i["notes"] for i in tonesoul_items)

    def test_has_git_true_when_dot_git_exists(self, tmp_path, monkeypatch):
        sub = tmp_path / "myproject"
        sub.mkdir()
        (sub / ".git").mkdir()
        monkeypatch.setattr(config_mod, "WORKSPACE_ROOT", str(tmp_path))
        monkeypatch.setattr(inv_mod, "list_workspace_dirs", config_mod.list_workspace_dirs)

        result = inv_mod.build_inventory()
        myproject = next(i for i in result if i["name"] == "myproject")
        assert myproject["has_git"] is True

    def test_has_git_false_when_no_dot_git(self, tmp_path, monkeypatch):
        sub = tmp_path / "plain"
        sub.mkdir()
        monkeypatch.setattr(config_mod, "WORKSPACE_ROOT", str(tmp_path))
        monkeypatch.setattr(inv_mod, "list_workspace_dirs", config_mod.list_workspace_dirs)

        result = inv_mod.build_inventory()
        plain = next(i for i in result if i["name"] == "plain")
        assert plain["has_git"] is False


class TestEntrypointsStatus:
    def test_returns_one_entry_per_known_entrypoint(self):
        status = inv_mod.entrypoints_status()
        assert len(status) == len(config_mod.KNOWN_ENTRYPOINTS)

    def test_each_entry_has_required_keys(self):
        for entry in inv_mod.entrypoints_status():
            for key in ("name", "path", "exists", "command", "notes"):
                assert key in entry

    def test_exists_is_boolean(self):
        for entry in inv_mod.entrypoints_status():
            assert isinstance(entry["exists"], bool)

    def test_names_match_known_entrypoints(self):
        expected_names = {ep.name for ep in config_mod.KNOWN_ENTRYPOINTS}
        actual_names = {entry["name"] for entry in inv_mod.entrypoints_status()}
        assert expected_names == actual_names


class TestWriteInventoryReport:
    def test_creates_json_and_md_files(self, tmp_path):
        output_dir = str(tmp_path / "report")
        result = inv_mod.write_inventory_report(output_dir)

        assert Path(result["json"]).exists()
        assert Path(result["md"]).exists()

    def test_json_file_is_valid_json(self, tmp_path):
        result = inv_mod.write_inventory_report(str(tmp_path / "report"))
        with open(result["json"], encoding="utf-8") as f:
            data = json.load(f)
        assert "workspace_root" in data
        assert "workspaces" in data
        assert "entrypoints" in data

    def test_md_file_contains_inventory_header(self, tmp_path):
        result = inv_mod.write_inventory_report(str(tmp_path / "report"))
        content = Path(result["md"]).read_text(encoding="utf-8")
        assert "Workspace Inventory" in content
        assert "Entrypoints" in content

    def test_creates_output_dir_if_missing(self, tmp_path):
        nested = str(tmp_path / "deep" / "nested" / "dir")
        assert not os.path.exists(nested)
        inv_mod.write_inventory_report(nested)
        assert os.path.isdir(nested)

    def test_json_workspace_root_matches_constant(self, tmp_path):
        result = inv_mod.write_inventory_report(str(tmp_path / "r"))
        with open(result["json"], encoding="utf-8") as f:
            data = json.load(f)
        assert data["workspace_root"] == config_mod.WORKSPACE_ROOT
