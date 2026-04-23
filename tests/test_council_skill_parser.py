"""Tests for tonesoul.council.skill_parser — pure helpers and SkillContractParser."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tonesoul.council.skill_parser import (
    SkillContractParser,
    _as_string_list,
    _normalize_text,
    _split_frontmatter,
)


# ── _as_string_list ───────────────────────────────────────────────────────────

class TestAsStringList:
    def test_list_of_strings_returned(self):
        assert _as_string_list(["a", "b"]) == ["a", "b"]

    def test_strips_whitespace(self):
        assert _as_string_list(["  x  "]) == ["x"]

    def test_filters_empty_strings(self):
        assert _as_string_list(["", "  ", "a"]) == ["a"]

    def test_non_list_gives_empty(self):
        assert _as_string_list("not-a-list") == []
        assert _as_string_list(None) == []
        assert _as_string_list(42) == []

    def test_filters_non_string_items(self):
        result = _as_string_list(["a", 1, None, "b"])
        assert result == ["a", "b"]


# ── _normalize_text ───────────────────────────────────────────────────────────

class TestNormalizeText:
    def test_lowercases(self):
        assert _normalize_text("HELLO") == "hello"

    def test_replaces_special_chars_with_space(self):
        result = _normalize_text("hello-world!")
        assert result == "hello world"

    def test_strips_result(self):
        result = _normalize_text("  hello  ")
        assert result == "hello"

    def test_keeps_numbers(self):
        result = _normalize_text("axiom3")
        assert "axiom" in result
        assert "3" in result

    def test_empty_string_gives_empty(self):
        assert _normalize_text("") == ""


# ── _split_frontmatter ────────────────────────────────────────────────────────

class TestSplitFrontmatter:
    def test_no_frontmatter_returns_empty_dict_and_text(self):
        fm, body = _split_frontmatter("no frontmatter here")
        assert fm == {}
        assert body == "no frontmatter here"

    def test_parses_yaml_frontmatter(self):
        text = "---\nname: my-skill\ntier: trusted\n---\nSkill content here."
        fm, body = _split_frontmatter(text)
        assert fm["name"] == "my-skill"
        assert fm["tier"] == "trusted"
        assert body == "Skill content here."

    def test_body_stripped(self):
        text = "---\nname: x\n---\n\n  Body content.  \n"
        _, body = _split_frontmatter(text)
        assert body == "Body content."

    def test_incomplete_frontmatter_returns_empty_dict(self):
        text = "---\njust one block"
        fm, body = _split_frontmatter(text)
        assert fm == {}

    def test_invalid_yaml_returns_empty_dict(self):
        text = "---\n: invalid: yaml: here:\n---\nbody"
        fm, body = _split_frontmatter(text)
        assert isinstance(fm, dict)


# ── SkillContractParser — registry loading ────────────────────────────────────

def _write_registry(tmp_path: Path, skills: list) -> Path:
    registry = {"skills": skills}
    path = tmp_path / "skills" / "registry.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry), encoding="utf-8")
    return path


def _write_skill_file(tmp_path: Path, filename: str, content: str) -> Path:
    path = tmp_path / "skills" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _make_parser(tmp_path: Path, skills: list, skill_files: dict[str, str] | None = None) -> SkillContractParser:
    registry_path = _write_registry(tmp_path, skills)
    if skill_files:
        for filename, content in skill_files.items():
            _write_skill_file(tmp_path, filename, content)
    return SkillContractParser(repo_root=tmp_path, registry_path=registry_path)


_SKILL_ENTRY = {
    "id": "skill-one",
    "path": "skills/skill-one.md",
    "l1_routing": {
        "name": "Skill One",
        "triggers": ["analyze", "review"],
        "intent": "deep analysis",
    },
    "l2_signature": {
        "trust_tier": "trusted",
        "execution_profile": ["standard", "any"],
        "description": "Analyzes things",
    },
}


class TestSkillContractParserLoadRegistry:
    def test_get_all_l1_routes_returns_skills(self, tmp_path):
        parser = _make_parser(tmp_path, [_SKILL_ENTRY])
        routes = parser.get_all_l1_routes()
        assert len(routes) == 1
        assert routes[0]["id"] == "skill-one"

    def test_routes_include_triggers(self, tmp_path):
        parser = _make_parser(tmp_path, [_SKILL_ENTRY])
        routes = parser.get_all_l1_routes()
        assert "analyze" in routes[0]["triggers"]

    def test_get_l2_signature_returns_dict(self, tmp_path):
        parser = _make_parser(tmp_path, [_SKILL_ENTRY])
        sig = parser.get_l2_signature("skill-one")
        assert sig["trust_tier"] == "trusted"

    def test_get_l2_signature_raises_for_missing_skill(self, tmp_path):
        parser = _make_parser(tmp_path, [_SKILL_ENTRY])
        with pytest.raises(KeyError, match="missing"):
            parser.get_l2_signature("missing")

    def test_get_l2_signature_raises_when_no_l2(self, tmp_path):
        entry = dict(_SKILL_ENTRY)
        del entry["l2_signature"]  # type: ignore
        parser = _make_parser(tmp_path, [entry])
        with pytest.raises(ValueError, match="l2_signature missing"):
            parser.get_l2_signature("skill-one")

    def test_registry_loaded_once(self, tmp_path):
        parser = _make_parser(tmp_path, [_SKILL_ENTRY])
        r1 = parser.get_all_l1_routes()
        r2 = parser.get_all_l1_routes()
        assert r1 == r2  # second call returns same cached data

    def test_skips_entry_without_id(self, tmp_path):
        parser = _make_parser(tmp_path, [{"l1_routing": {}, "l2_signature": {}}])
        assert parser.get_all_l1_routes() == []

    def test_skips_non_dict_entries(self, tmp_path):
        parser = _make_parser(tmp_path, [_SKILL_ENTRY, "not-a-dict", 42])
        routes = parser.get_all_l1_routes()
        assert len(routes) == 1

    def test_invalid_registry_raises_value_error(self, tmp_path):
        path = tmp_path / "skills" / "registry.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('"not-an-object"', encoding="utf-8")
        parser = SkillContractParser(repo_root=tmp_path, registry_path=path)
        with pytest.raises(ValueError, match="must be an object"):
            parser.get_all_l1_routes()

    def test_registry_missing_skills_key_raises(self, tmp_path):
        path = tmp_path / "skills" / "registry.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('{"other": []}', encoding="utf-8")
        parser = SkillContractParser(repo_root=tmp_path, registry_path=path)
        with pytest.raises(ValueError, match="skills must be a list"):
            parser.get_all_l1_routes()


class TestSkillContractParserGetL3:
    def test_get_l3_payload_returns_body(self, tmp_path):
        content = "---\nname: s1\n---\nThis is the skill body."
        parser = _make_parser(
            tmp_path,
            [_SKILL_ENTRY],
            skill_files={"skill-one.md": content},
        )
        payload = parser.get_l3_payload("skill-one")
        assert "This is the skill body." in payload

    def test_get_l3_payload_raises_when_path_missing(self, tmp_path):
        entry = dict(_SKILL_ENTRY)
        entry = {k: v for k, v in entry.items() if k != "path"}
        entry["id"] = "skill-one"
        parser = _make_parser(tmp_path, [entry])
        with pytest.raises(ValueError, match="skill path missing"):
            parser.get_l3_payload("skill-one")


class TestSkillContractParserResolve:
    def test_resolve_returns_matching_skill(self, tmp_path):
        content = "Detailed skill content for analysis."
        parser = _make_parser(
            tmp_path,
            [_SKILL_ENTRY],
            skill_files={"skill-one.md": content},
        )
        results = parser.resolve_for_request(
            query="please analyze this document",
            execution_profile="standard",
        )
        assert len(results) >= 1
        assert results[0]["skill_id"] == "skill-one"

    def test_no_match_when_trigger_absent(self, tmp_path):
        content = "content"
        parser = _make_parser(
            tmp_path,
            [_SKILL_ENTRY],
            skill_files={"skill-one.md": content},
        )
        results = parser.resolve_for_request(
            query="completely unrelated query",
            execution_profile="standard",
        )
        assert len(results) == 0

    def test_trust_tier_filter_applied(self, tmp_path):
        content = "content"
        parser = _make_parser(
            tmp_path,
            [_SKILL_ENTRY],
            skill_files={"skill-one.md": content},
        )
        results = parser.resolve_for_request(
            query="analyze this",
            execution_profile="standard",
            allowed_trust_tiers=["experimental"],  # skill is "trusted"
        )
        assert len(results) == 0

    def test_l3_truncated_when_long(self, tmp_path):
        content = "x" * 2000
        parser = _make_parser(
            tmp_path,
            [_SKILL_ENTRY],
            skill_files={"skill-one.md": content},
        )
        results = parser.resolve_for_request(
            query="analyze this",
            execution_profile="standard",
            l3_char_limit=100,
        )
        if results:
            assert "[truncated]" in results[0]["l3_excerpt"]
