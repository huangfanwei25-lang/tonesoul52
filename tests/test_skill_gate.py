import json
from pathlib import Path

import pytest

from tonesoul.skill_gate import evaluate_skill, list_skill_paths, review_skill, review_skills


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_policy(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_list_skill_paths_returns_sorted_json_only(tmp_path: Path) -> None:
    skills_dir = tmp_path / "skills"
    _write_json(skills_dir / "beta.json", {"skill_id": "beta"})
    _write_json(skills_dir / "alpha.json", {"skill_id": "alpha"})
    (skills_dir / "notes.txt").write_text("ignore", encoding="utf-8")

    paths = list_skill_paths(str(tmp_path))

    assert paths == [
        str(skills_dir / "alpha.json"),
        str(skills_dir / "beta.json"),
    ]


def test_evaluate_skill_aggregates_rule_ids_and_score_ratios() -> None:
    passed, score, rule_ids = evaluate_skill(
        {
            "criteria": {
                "support_count": 3,
                "pass_rate": 0.80,
                "counterexample_rate": 0.10,
                "energy_samples": 5,
                "energy_stdev": 0.25,
                "recent_run_count": 2,
                "thresholds": {
                    "min_support": 4,
                    "min_pass_rate": 0.75,
                    "max_counterexample_rate": 0.20,
                    "min_energy_samples": 4,
                    "max_energy_stddev": 0.50,
                    "min_recent_runs": 3,
                },
            }
        }
    )

    assert passed is False
    assert score == pytest.approx(0.9028)
    assert rule_ids == [
        "min_support",
        "min_pass_rate",
        "max_counterexample_rate",
        "min_energy_samples",
        "max_energy_stddev",
        "min_recent_runs",
    ]


def test_review_skill_auto_approves_and_persists_gate_metadata(tmp_path: Path) -> None:
    skill_path = tmp_path / "memory" / "skills" / "skill.json"
    policy_path = tmp_path / "spec" / "memory" / "memory_policy.yaml"
    _write_json(
        skill_path,
        {
            "skill_id": "skill.alpha",
            "origin_episode": "ep-1",
            "status": "candidate",
            "criteria": {
                "support_count": 5,
                "pass_rate": 0.91,
                "thresholds": {"min_support": 3, "min_pass_rate": 0.80},
            },
        },
    )
    _write_policy(
        policy_path,
        """
review:
  auto_approve: true
  default_reviewer: auto
  default_role: guardian
  require_role: true
  role_levels:
    guardian: 3
  require_role_min_approve: 2
""".strip(),
    )

    result = review_skill(str(skill_path), policy_path=str(policy_path))
    persisted = json.loads(skill_path.read_text(encoding="utf-8"))

    assert result == {
        "skill_id": "skill.alpha",
        "status": "approved",
        "reviewed": True,
        "passed": True,
        "score": 1.0,
    }
    assert persisted["status"] == "approved"
    assert persisted["gate"] == {
        "passed": True,
        "rule_ids": ["min_support", "min_pass_rate"],
        "score": 1.0,
        "role": "guardian",
        "role_level": 3,
    }
    assert persisted["review"]["reviewer"] == "auto"
    assert persisted["review"]["reviewer_role"] == "guardian"
    assert persisted["review"]["auto"] is True


def test_review_skill_forces_reject_when_policy_disallows_override(tmp_path: Path) -> None:
    skill_path = tmp_path / "memory" / "skills" / "skill.json"
    policy_path = tmp_path / "spec" / "memory" / "memory_policy.yaml"
    _write_json(
        skill_path,
        {
            "skill_id": "skill.beta",
            "status": "candidate",
            "criteria": {
                "support_count": 1,
                "thresholds": {"min_support": 3},
            },
        },
    )
    _write_policy(
        policy_path,
        """
review:
  require_reviewer: false
  require_pass: true
  allow_override: false
""".strip(),
    )

    result = review_skill(
        str(skill_path),
        decision="approved",
        policy_path=str(policy_path),
    )
    persisted = json.loads(skill_path.read_text(encoding="utf-8"))

    assert result["status"] == "rejected"
    assert result["passed"] is False
    assert persisted["status"] == "rejected"
    assert persisted["review"]["decision"] == "rejected"


def test_review_skill_dry_run_preserves_file_and_role_thresholds_apply(
    tmp_path: Path,
) -> None:
    skill_path = tmp_path / "memory" / "skills" / "skill.json"
    policy_path = tmp_path / "spec" / "memory" / "memory_policy.yaml"
    payload = {
        "skill_id": "skill.gamma",
        "status": "candidate",
        "criteria": {
            "support_count": 4,
            "thresholds": {"min_support": 3},
        },
    }
    _write_json(skill_path, payload)
    _write_policy(
        policy_path,
        """
review:
  require_role: true
  role_levels:
    guardian: 1
    architect: 2
  require_role_min_approve: 2
""".strip(),
    )

    with pytest.raises(ValueError, match="not sufficient to approve"):
        review_skill(
            str(skill_path),
            decision="approved",
            reviewer="alice",
            reviewer_role="guardian",
            policy_path=str(policy_path),
        )

    result = review_skill(
        str(skill_path),
        decision="approved",
        reviewer="alice",
        reviewer_role="architect",
        policy_path=str(policy_path),
        dry_run=True,
    )

    assert result["status"] == "approved"
    assert json.loads(skill_path.read_text(encoding="utf-8")) == payload


def test_list_skill_paths_returns_empty_when_dir_missing(tmp_path: Path) -> None:
    assert list_skill_paths(str(tmp_path / "no_such_dir")) == []


def test_evaluate_skill_empty_criteria_returns_false_and_zero(tmp_path: Path) -> None:
    passed, score, rule_ids = evaluate_skill({})
    assert passed is False
    assert score == 0.0
    assert rule_ids == []


def test_evaluate_skill_all_thresholds_met_returns_true() -> None:
    passed, score, rule_ids = evaluate_skill(
        {
            "criteria": {
                "support_count": 10,
                "pass_rate": 0.95,
                "thresholds": {
                    "min_support": 5,
                    "min_pass_rate": 0.80,
                },
            }
        }
    )
    assert passed is True
    assert score == pytest.approx(1.0)


def test_review_skill_already_approved_returns_no_review(tmp_path: Path) -> None:
    skill_path = tmp_path / "skills" / "done.json"
    _write_json(
        skill_path,
        {
            "skill_id": "done",
            "status": "approved",
            "criteria": {"support_count": 5, "thresholds": {"min_support": 3}},
        },
    )
    result = review_skill(str(skill_path))
    assert result["reviewed"] is False
    assert result["status"] == "approved"


def test_review_skill_no_decision_no_auto_returns_current_status(tmp_path: Path) -> None:
    skill_path = tmp_path / "skills" / "pending.json"
    _write_json(
        skill_path,
        {
            "skill_id": "pending",
            "status": "candidate",
            "criteria": {"support_count": 5, "thresholds": {"min_support": 3}},
        },
    )
    result = review_skill(str(skill_path))
    assert result["reviewed"] is False
    assert result["status"] == "candidate"


def test_review_skill_raises_when_reviewer_required_but_missing(tmp_path: Path) -> None:
    skill_path = tmp_path / "skills" / "gate.json"
    policy_path = tmp_path / "policy.yaml"
    _write_json(
        skill_path,
        {
            "skill_id": "gate",
            "status": "candidate",
            "criteria": {"support_count": 5, "thresholds": {"min_support": 3}},
        },
    )
    _write_policy(policy_path, "review:\n  require_reviewer: true\n")
    with pytest.raises(ValueError, match="Reviewer is required"):
        review_skill(str(skill_path), decision="approved", policy_path=str(policy_path))


def test_review_skills_dry_run_skips_index(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    skill_path = memory_root / "skills" / "s.json"
    _write_json(
        skill_path,
        {
            "skill_id": "s",
            "status": "candidate",
            "criteria": {"support_count": 5, "thresholds": {"min_support": 3}},
        },
    )
    _write_policy(tmp_path / "policy.yaml", "review:\n  require_reviewer: false\n")

    result = review_skills(
        [str(skill_path)],
        decision="approved",
        memory_root=str(memory_root),
        policy_path=str(tmp_path / "policy.yaml"),
        dry_run=True,
    )
    assert result["skill_index"] == ""
    assert not (memory_root / "skill_index.json").exists()


def test_review_skills_writes_skill_index_when_memory_root_is_provided(tmp_path: Path) -> None:
    memory_root = tmp_path / "memory"
    skills_dir = memory_root / "skills"
    skill_a = skills_dir / "alpha.json"
    skill_b = skills_dir / "beta.json"
    policy_path = tmp_path / "spec" / "memory" / "memory_policy.yaml"
    _write_json(
        skill_a,
        {
            "skill_id": "alpha",
            "origin_episode": "ep-a",
            "status": "candidate",
            "criteria": {"support_count": 5, "thresholds": {"min_support": 3}},
        },
    )
    _write_json(
        skill_b,
        {
            "skill_id": "beta",
            "origin_episode": "ep-b",
            "status": "candidate",
            "criteria": {"support_count": 4, "thresholds": {"min_support": 3}},
        },
    )
    _write_policy(
        policy_path,
        """
review:
  require_role: true
  role_levels:
    guardian: 2
  require_role_min_approve: 2
""".strip(),
    )

    result = review_skills(
        [str(skill_b), str(skill_a)],
        decision="approved",
        reviewer="alice",
        reviewer_role="guardian",
        memory_root=str(memory_root),
        policy_path=str(policy_path),
    )

    index_path = Path(result["skill_index"])
    index_payload = json.loads(index_path.read_text(encoding="utf-8"))
    assert index_path == memory_root / "skill_index.json"
    assert [item["skill_id"] for item in index_payload["skills"]] == ["alpha", "beta"]
    assert [item["status"] for item in index_payload["skills"]] == ["approved", "approved"]
