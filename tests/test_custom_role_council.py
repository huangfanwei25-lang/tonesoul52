"""Tests for Custom Role Council (Team Simulator mode).

Verifies that user-defined custom roles can enter the council
via PerspectiveFactory, producing valid LLMPerspective instances
with correct system prompts.
"""

from __future__ import annotations

from tonesoul.council.perspective_factory import (
    LLMPerspective,
    PerspectiveFactory,
)

# ── create_from_custom_role ──────────────────────────────────


class TestCreateFromCustomRole:
    def test_basic_role(self):
        role = {"name": "財務長", "description": "保守型，重視 ROI"}
        perspective = PerspectiveFactory.create_from_custom_role(role)
        assert isinstance(perspective, LLMPerspective)
        assert perspective.name == "財務長"
        assert "財務長" in perspective.system_prompt
        assert "保守型" in perspective.system_prompt

    def test_role_with_prompt_hint(self):
        role = {
            "name": "工程主管",
            "description": "務實型",
            "prompt_hint": "拒絕超過 6 個月回本的專案",
        }
        perspective = PerspectiveFactory.create_from_custom_role(role)
        assert "拒絕超過 6 個月回本的專案" in perspective.system_prompt

    def test_role_minimal_name_only(self):
        role = {"name": "CEO"}
        perspective = PerspectiveFactory.create_from_custom_role(role)
        assert isinstance(perspective, LLMPerspective)
        assert perspective.name == "ceo"  # normalized to lowercase

    def test_role_empty_name_defaults_to_custom(self):
        role = {"name": ""}
        perspective = PerspectiveFactory.create_from_custom_role(role)
        assert perspective.name == "custom"

    def test_role_missing_name_defaults_to_custom(self):
        role = {"description": "some role"}
        perspective = PerspectiveFactory.create_from_custom_role(role)
        assert perspective.name == "custom"

    def test_system_prompt_contains_json_format(self):
        role = {"name": "測試角色"}
        perspective = PerspectiveFactory.create_from_custom_role(role)
        assert "APPROVE" in perspective.system_prompt
        assert "CONCERN" in perspective.system_prompt
        assert "OBJECT" in perspective.system_prompt
        assert "JSON" in perspective.system_prompt

    def test_model_override(self):
        role = {"name": "分析師"}
        perspective = PerspectiveFactory.create_from_custom_role(role, model="qwen2.5:7b")
        assert perspective.model == "qwen2.5:7b"

    def test_fallback_is_none(self):
        """Custom roles have no rules-based fallback (no predefined rules)."""
        role = {"name": "自訂角色"}
        perspective = PerspectiveFactory.create_from_custom_role(role)
        assert perspective.fallback is None


# ── create_custom_council ────────────────────────────────────


class TestCreateCustomCouncil:
    def test_creates_multiple_perspectives(self):
        roles = [
            {"name": "財務長", "description": "保守型"},
            {"name": "工程主管", "description": "務實型"},
            {"name": "CEO", "description": "策略型"},
        ]
        perspectives = PerspectiveFactory.create_custom_council(roles)
        assert len(perspectives) == 3
        names = [p.name for p in perspectives]
        assert "財務長" in names
        assert "工程主管" in names
        assert "ceo" in names

    def test_empty_roles_falls_back_to_default(self):
        perspectives = PerspectiveFactory.create_custom_council([])
        assert len(perspectives) == 5  # default council size

    def test_none_roles_falls_back_to_default(self):
        perspectives = PerspectiveFactory.create_custom_council(None)
        assert len(perspectives) == 5

    def test_skips_non_dict_entries(self):
        roles = [
            {"name": "OK"},
            "not_a_dict",
            42,
            {"name": "也 OK"},
        ]
        perspectives = PerspectiveFactory.create_custom_council(roles)
        assert len(perspectives) == 2

    def test_all_invalid_entries_falls_back(self):
        roles = ["bad", 42, None]
        perspectives = PerspectiveFactory.create_custom_council(roles)
        assert len(perspectives) == 5  # fallback to default

    def test_model_override_applies_to_all(self):
        roles = [
            {"name": "A"},
            {"name": "B"},
        ]
        perspectives = PerspectiveFactory.create_custom_council(roles, model="custom-model")
        for p in perspectives:
            assert p.model == "custom-model"

    def test_single_role_council(self):
        """Even a single role should work (degenerate council)."""
        roles = [{"name": "Solo"}]
        perspectives = PerspectiveFactory.create_custom_council(roles)
        assert len(perspectives) == 1


# ── PerspectiveFactory.create with unknown name ──────────────


class TestCreateUnknownName:
    def test_unknown_name_creates_llm_perspective(self):
        """Unknown names should create LLMPerspective instead of raising."""
        perspective = PerspectiveFactory.create(name="爸爸", mode="llm")
        assert isinstance(perspective, LLMPerspective)
        assert perspective.name == "爸爸"

    def test_unknown_name_with_system_prompt(self):
        perspective = PerspectiveFactory.create(
            name="老闆",
            mode="llm",
            system_prompt="你是公司 CEO，重視長期價值。",
        )
        assert isinstance(perspective, LLMPerspective)
        assert "長期價值" in perspective.system_prompt

    def test_known_names_still_work(self):
        """Existing perspective names should still resolve to rules-based."""
        perspective = PerspectiveFactory.create(name="guardian", mode="rules")
        assert not isinstance(perspective, LLMPerspective)


# ── Integration: custom roles produce valid votes ────────────


class TestCustomRoleEvaluation:
    def test_custom_role_evaluate_without_llm(self):
        """Without LLM credentials, custom roles return CONCERN vote."""
        role = {"name": "測試", "description": "測試角色"}
        perspective = PerspectiveFactory.create_from_custom_role(role)
        vote = perspective.evaluate(
            draft_output="測試文字",
            context={"language": "zh"},
            user_intent="測試意圖",
        )
        # Without Gemini credentials, should fall back to CONCERN
        assert vote.perspective == "測試"
        assert vote.decision is not None
        assert 0.0 <= vote.confidence <= 1.0
