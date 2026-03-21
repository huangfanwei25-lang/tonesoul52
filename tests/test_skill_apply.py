import json

import pytest

from tonesoul.skill_apply import (
    _keyword_matches,
    _matches_when,
    _trigger_summary,
    apply_skills,
    build_context_key,
    format_skill_section,
    load_skills,
)


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
