import json

import pytest

from tonesoul.skill_apply import (
    _constraints_for_action,
    _context_text,
    _directives_for_action,
    _directives_for_provides,
    _extend_unique,
    _keyword_matches,
    _matches_when,
    _trigger_summary,
    apply_skills,
    build_context_key,
    format_skill_section,
    load_skills,
)


# ── _context_text ─────────────────────────────────────────────────────────────

class TestContextText:
    def test_combines_fields(self):
        key = {"task": "audit", "domain": "governance"}
        result = _context_text(key)
        assert "audit" in result
        assert "governance" in result

    def test_lowercase(self):
        key = {"task": "Audit"}
        assert _context_text(key) == "audit"

    def test_skips_none(self):
        key = {"task": None, "domain": "security"}
        result = _context_text(key)
        assert result == "security"

    def test_frame_ids_included(self):
        key = {"frame_ids": ["frame_a", "frame_b"]}
        result = _context_text(key)
        assert "frame_a" in result and "frame_b" in result


# ── _directives_for_action ────────────────────────────────────────────────────

class TestDirectivesForAction:
    def test_governance_baseline_action(self):
        d = _directives_for_action("apply_governance_baseline")
        assert d["force_gates"] is True
        assert d["require_evidence"] is True

    def test_none_returns_empty(self):
        assert _directives_for_action(None) == {}

    def test_unknown_returns_empty(self):
        assert _directives_for_action("custom_action") == {}


# ── _constraints_for_action ───────────────────────────────────────────────────

class TestConstraintsForAction:
    def test_governance_baseline_returns_constraints(self):
        constraints = _constraints_for_action("apply_governance_baseline")
        assert len(constraints) > 0
        assert any("YSS" in c for c in constraints)

    def test_none_returns_empty(self):
        assert _constraints_for_action(None) == []

    def test_unknown_returns_empty(self):
        assert _constraints_for_action("unknown") == []


# ── _directives_for_provides ──────────────────────────────────────────────────

class TestDirectivesForProvides:
    def test_force_gates_in_list(self):
        d = _directives_for_provides(["force_gates"])
        assert d["force_gates"] is True

    def test_string_force_gates(self):
        d = _directives_for_provides("force_gates")
        assert d["force_gates"] is True

    def test_require_evidence(self):
        d = _directives_for_provides(["require_evidence"])
        assert d["require_evidence"] is True

    def test_unknown_provides_empty(self):
        assert _directives_for_provides(["custom"]) == {}

    def test_none_returns_empty(self):
        assert _directives_for_provides(None) == {}


# ── _extend_unique ────────────────────────────────────────────────────────────

class TestExtendUnique:
    def test_appends_new_items(self):
        values = ["a"]
        _extend_unique(values, ["b", "c"])
        assert values == ["a", "b", "c"]

    def test_skips_duplicates(self):
        values = ["a", "b"]
        _extend_unique(values, ["a", "c"])
        assert values == ["a", "b", "c"]

    def test_empty_additions(self):
        values = ["a"]
        _extend_unique(values, [])
        assert values == ["a"]


def _write_skill(memory_root, name: str, payload: dict[str, object]) -> None:
    skills_dir = memory_root / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    (skills_dir / f"{name}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_load_skills_handles_missing_dir_and_empty_status_filter(tmp_path) -> None:
    assert load_skills(str(tmp_path)) == []

    _write_skill(
        tmp_path,
        "approved",
        {"skill_id": "approved", "status": "approved"},
    )
    _write_skill(
        tmp_path,
        "rejected",
        {"skill_id": "rejected", "status": "rejected"},
    )

    assert [item["skill_id"] for item in load_skills(str(tmp_path), status="")] == [
        "approved",
        "rejected",
    ]


def test_load_skills_raises_when_json_payload_is_not_an_object(tmp_path) -> None:
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    (skills_dir / "broken.json").write_text('["not", "an", "object"]', encoding="utf-8")

    with pytest.raises(ValueError, match="must be an object"):
        load_skills(str(tmp_path))


def test_build_context_key_and_matches_when_ignore_invalid_shapes() -> None:
    context_key = build_context_key(
        {"context": "bad", "time_island": {"kairos": "bad"}},
        {"selected_frames": [{"id": "b"}, "skip", {"id": "a"}, {"other": 1}]},
    )

    assert context_key == {
        "task": None,
        "objective": None,
        "audience": None,
        "domain": None,
        "mode": None,
        "decision_mode": None,
        "frame_ids": ["a", "b"],
    }
    assert _matches_when({"frame_ids": ["a"]}, context_key) is True
    assert _matches_when({"task": "audit"}, context_key) is False


def test_keyword_and_trigger_helpers_normalize_matches_and_bad_strength() -> None:
    matches = _keyword_matches([" Alpha ", " ", "BETA"], "alpha beta gamma")
    summary = _trigger_summary(
        [
            {
                "id": "trigger-1",
                "semantic": {"keywords": [" Alpha ", "", "BETA"]},
                "attraction_strength": "not-a-number",
            }
        ],
        "alpha beta gamma",
    )

    assert matches == ["Alpha", "BETA"]
    assert summary == [
        {
            "id": "trigger-1",
            "keywords": [" Alpha ", "", "BETA"],
            "matched": ["Alpha", "BETA"],
            "strength": 0.0,
        }
    ]


def test_apply_skills_trigger_only_policy_and_strength_threshold(tmp_path) -> None:
    _write_skill(
        tmp_path,
        "trigger_only",
        {
            "skill_id": "trigger.only",
            "origin_episode": "ep-1",
            "status": "approved",
            "policy_template": {"notes": "trigger only"},
            "gravity_wells": [
                {
                    "id": "trigger-1",
                    "type": "trigger",
                    "semantic": {"keywords": ["Audit"]},
                    "attraction_strength": 0.4,
                }
            ],
        },
    )
    context = {
        "context": {"task": "Audit request", "objective": "verify"},
        "time_island": {"kairos": {"decision_mode": "strict"}},
    }

    _, applied_default, _, _ = apply_skills(context, None, memory_root=str(tmp_path))
    _, applied_strong, _, _ = apply_skills(
        context,
        None,
        memory_root=str(tmp_path),
        matching_policy={"allow_trigger_only": True, "min_trigger_strength": 0.5},
    )
    _, applied_fallback, _, _ = apply_skills(
        context,
        None,
        memory_root=str(tmp_path),
        matching_policy={"allow_trigger_only": True, "min_trigger_strength": "bad"},
    )

    assert applied_default == []
    assert applied_strong == []
    assert [item["skill_id"] for item in applied_fallback] == ["trigger.only"]


def test_apply_skills_merges_actions_applies_when_only_skills_and_ignores_invalid_shapes(
    tmp_path,
) -> None:
    _write_skill(
        tmp_path,
        "baseline",
        {
            "skill_id": "baseline",
            "origin_episode": "ep-a",
            "status": "approved",
            "policy_template": {
                "when": {"task": "audit"},
                "do": "apply_governance_baseline",
                "notes": "baseline note",
            },
            "gravity_wells": [
                {
                    "id": "action-1",
                    "type": "action",
                    "action": "apply_governance_baseline",
                    "provides": ["force_gates", "require_evidence"],
                }
            ],
        },
    )
    _write_skill(
        tmp_path,
        "when_only",
        {
            "skill_id": "when.only",
            "origin_episode": "ep-b",
            "status": "approved",
            "policy_template": {"when": {"task": "audit"}, "notes": "when only"},
            "gravity_wells": "bad-shape",
        },
    )
    _write_skill(
        tmp_path,
        "invalid",
        {
            "skill_id": "invalid",
            "origin_episode": "ep-c",
            "status": "approved",
            "policy_template": "bad-shape",
            "gravity_wells": "bad-shape",
        },
    )
    context = {
        "context": {"task": "audit", "objective": "verify", "mode": "strict"},
        "time_island": {"kairos": {"decision_mode": "council"}},
    }

    payload, applied, directives, constraints = apply_skills(
        context,
        None,
        memory_root=str(tmp_path),
    )

    assert [item["skill_id"] for item in applied] == ["baseline", "when.only"]
    assert payload["skills"] == applied
    assert directives == {"force_gates": True, "require_evidence": True}
    assert len(constraints) == 4
    assert len(set(constraints)) == 4
    assert applied[0]["gravity_wells"]["actions"] == [
        {
            "id": "action-1",
            "action": "apply_governance_baseline",
            "provides": ["force_gates", "require_evidence"],
        }
    ]


def test_format_skill_section_handles_empty_and_truthy_directives() -> None:
    assert format_skill_section([]) == ""

    rendered = format_skill_section(
        [{"skill_id": "skill.one", "action": None}],
        directives={"force_gates": True, "require_evidence": False},
    )

    assert "## Applied Skills" in rendered
    assert "- skill.one -> n/a" in rendered
    assert "- Directives: force_gates" in rendered
    assert "require_evidence" not in rendered
