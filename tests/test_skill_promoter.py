from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

from tonesoul import skill_promoter as module


def _write_json(path: Path, payload: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _write_yaml(path: Path, payload: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")
    return path


def _policy_payload(*, include_archived: bool = True) -> dict[str, object]:
    return {
        "version": "1.2",
        "episode_key": {"fields": ["domain", "mode", "decision_mode", "frame_ids"]},
        "promotion": {
            "include_archived": include_archived,
            "min_support": 2,
            "min_pass_rate": 0.6,
            "max_counterexample_rate": 0.5,
            "min_energy_samples": 2,
            "max_energy_stddev": 0.2,
            "min_recent_runs": 1,
            "recent_window_days": 3,
            "status": "proposed",
        },
        "defaults": {
            "policy_action": "apply_policy",
            "reviewer": "ops",
            "skill_version": "2.0.0",
            "revokable": False,
        },
    }


def _context_payload(
    *,
    task: str = "Audit",
    objective: str = "Protect evidence",
    audience: str = "operators",
    domain: str = "governance",
    mode: str = "assist",
    decision_mode: str = "careful",
) -> dict[str, object]:
    return {
        "context": {
            "task": task,
            "objective": objective,
            "audience": audience,
            "domain": domain,
            "mode": mode,
        },
        "time_island": {"kairos": {"decision_mode": decision_mode}},
    }


def _seed_payload(
    run_id: str,
    created_at: str,
    context_path: Path,
    frame_plan_path: Path,
    *,
    gate_overall: str = "PASS",
    energy: float = 0.5,
    archived: bool = False,
) -> dict[str, object]:
    return {
        "run_id": run_id,
        "created_at": created_at,
        "archived": archived,
        "gate_overall": gate_overall,
        "ystm_stats": {"E_total_mean": energy},
        "pointers": {
            "context": str(context_path),
            "frame_plan": str(frame_plan_path),
        },
    }


class _FixedDateTime(datetime):
    @classmethod
    def now(cls, tz: timezone | None = None) -> "_FixedDateTime":
        return cls(2026, 3, 19, 12, 0, 0, tzinfo=tz or timezone.utc)


def test_build_skill_index_reads_json_only(tmp_path: Path) -> None:
    skills_dir = tmp_path / "memory" / "skills"
    _write_json(
        skills_dir / "skill_a.json",
        {"skill_id": "skill-a", "origin_episode": "ep-a", "status": "approved"},
    )
    _write_json(
        skills_dir / "skill_b.json",
        {"skill_id": "skill-b", "origin_episode": "ep-b", "status": "proposed"},
    )
    (skills_dir / "note.txt").write_text("ignore me", encoding="utf-8")

    index = module._build_skill_index(str(tmp_path / "memory"))

    assert len(index["skills"]) == 2
    assert {item["skill_id"] for item in index["skills"]} == {"skill-a", "skill-b"}
    assert index["generated_at"]


def test_list_seed_paths_returns_sorted_json_files(tmp_path: Path) -> None:
    seeds_dir = tmp_path / "memory" / "seeds"
    _write_json(seeds_dir / "b_seed.json", {"run_id": "run-b"})
    _write_json(seeds_dir / "a_seed.json", {"run_id": "run-a"})
    (seeds_dir / "skip.txt").write_text("skip", encoding="utf-8")

    assert module._list_seed_paths(str(tmp_path / "memory")) == [
        str(seeds_dir / "a_seed.json"),
        str(seeds_dir / "b_seed.json"),
    ]


def test_extract_context_reads_context_and_decision_mode(tmp_path: Path) -> None:
    context_path = _write_yaml(tmp_path / "context.yaml", _context_payload())

    result = module._extract_context({"pointers": {"context": str(context_path)}})

    assert result == {
        "task": "Audit",
        "objective": "Protect evidence",
        "audience": "operators",
        "domain": "governance",
        "mode": "assist",
        "decision_mode": "careful",
    }


def test_extract_frames_returns_sorted_frame_ids(tmp_path: Path) -> None:
    frame_plan_path = _write_json(
        tmp_path / "frame_plan.json",
        {
            "selected_frames": [
                {"id": "frame-b"},
                {"id": "frame-a"},
                {"note": "skip"},
            ]
        },
    )

    assert module._extract_frames({"pointers": {"frame_plan": str(frame_plan_path)}}) == [
        "frame-a",
        "frame-b",
    ]


def test_build_episode_key_uses_policy_fields(tmp_path: Path) -> None:
    context_path = _write_yaml(tmp_path / "context.yaml", _context_payload(domain="ops"))
    frame_plan_path = _write_json(
        tmp_path / "frame_plan.json",
        {"selected_frames": [{"id": "guardian"}, {"id": "critic"}]},
    )
    seed = _seed_payload(
        "run-001",
        "2026-03-18T09:00:00Z",
        context_path,
        frame_plan_path,
    )
    policy = {"episode_key": {"fields": ["domain", "decision_mode", "frame_ids"]}}

    key = module._build_episode_key(seed, policy)

    assert key == {
        "domain": "ops",
        "decision_mode": "careful",
        "frame_ids": ["critic", "guardian"],
    }


def test_build_episodes_groups_runs_and_skips_archived_when_disabled(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(module, "datetime", _FixedDateTime)
    context_path = _write_yaml(tmp_path / "context.yaml", _context_payload())
    frame_plan_path = _write_json(
        tmp_path / "frame_plan.json",
        {"selected_frames": [{"id": "guardian"}]},
    )
    first = _write_json(
        tmp_path / "seeds" / "seed-1.json",
        _seed_payload("run-001", "2026-03-18T09:00:00Z", context_path, frame_plan_path, energy=0.4),
    )
    second = _write_json(
        tmp_path / "seeds" / "seed-2.json",
        _seed_payload("run-002", "2026-03-19T08:00:00Z", context_path, frame_plan_path, energy=0.6),
    )
    archived = _write_json(
        tmp_path / "seeds" / "seed-3.json",
        _seed_payload(
            "run-003",
            "2026-03-19T09:00:00Z",
            context_path,
            frame_plan_path,
            archived=True,
        ),
    )

    episodes = module.build_episodes(
        [str(first), str(second), str(archived)],
        _policy_payload(include_archived=False),
    )

    assert len(episodes) == 1
    episode = episodes[0]
    assert episode["run_count"] == 2
    assert episode["gate_pass_count"] == 2
    assert episode["counterexample_count"] == 0
    assert episode["energy"]["samples"] == 2
    assert episode["energy"]["E_total_mean_mean"] == 0.5
    assert episode["energy"]["E_total_mean_stdev"] == 0.1
    assert episode["recent_run_count"] == 2
    assert episode["first_seen"] == "2026-03-18T09:00:00Z"
    assert episode["last_seen"] == "2026-03-19T08:00:00Z"


def test_eligible_requires_all_thresholds() -> None:
    episode = {
        "run_count": 2,
        "gate_pass_rate": 0.8,
        "counterexample_rate": 0.2,
        "recent_run_count": 1,
        "energy": {"samples": 2, "E_total_mean_stdev": 0.1},
    }

    assert module._eligible(episode, _policy_payload()) is True

    bad_support = {**episode, "run_count": 1}
    bad_pass_rate = {**episode, "gate_pass_rate": 0.5}
    bad_counterexample = {**episode, "counterexample_rate": 0.6}
    bad_energy_samples = {**episode, "energy": {"samples": 1, "E_total_mean_stdev": 0.1}}
    bad_stdev = {**episode, "energy": {"samples": 2, "E_total_mean_stdev": 0.3}}
    bad_recent = {**episode, "recent_run_count": 0}

    assert module._eligible(bad_support, _policy_payload()) is False
    assert module._eligible(bad_pass_rate, _policy_payload()) is False
    assert module._eligible(bad_counterexample, _policy_payload()) is False
    assert module._eligible(bad_energy_samples, _policy_payload()) is False
    assert module._eligible(bad_stdev, _policy_payload()) is False
    assert module._eligible(bad_recent, _policy_payload()) is False


def test_build_skill_includes_thresholds_and_governance_metadata() -> None:
    episode = {
        "episode_id": "ep-001",
        "key": {"domain": "governance"},
        "run_count": 3,
        "gate_pass_rate": 1.0,
        "counterexample_rate": 0.0,
        "recent_run_count": 2,
        "energy": {"samples": 3, "E_total_mean_stdev": 0.05},
    }

    skill = module._build_skill(episode, _policy_payload())

    assert skill["origin_episode"] == "ep-001"
    assert skill["status"] == "proposed"
    assert skill["criteria"]["support_count"] == 3
    assert skill["criteria"]["thresholds"]["recent_window_days"] == 3
    assert skill["policy_template"]["do"] == "apply_policy"
    assert skill["governance"] == {
        "reviewer": "ops",
        "version": "2.0.0",
        "revokable": False,
    }


def test_promote_skills_dry_run_returns_counts_without_writing_files(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(module, "datetime", _FixedDateTime)
    memory_root = tmp_path / "memory"
    context_path = _write_yaml(tmp_path / "context.yaml", _context_payload())
    frame_plan_path = _write_json(
        tmp_path / "frame_plan.json",
        {"selected_frames": [{"id": "guardian"}]},
    )
    seed_paths = [
        str(
            _write_json(
                memory_root / "seeds" / "seed-1.json",
                _seed_payload(
                    "run-001",
                    "2026-03-18T09:00:00Z",
                    context_path,
                    frame_plan_path,
                    energy=0.45,
                ),
            )
        ),
        str(
            _write_json(
                memory_root / "seeds" / "seed-2.json",
                _seed_payload(
                    "run-002",
                    "2026-03-19T09:00:00Z",
                    context_path,
                    frame_plan_path,
                    energy=0.55,
                ),
            )
        ),
    ]
    policy_path = _write_yaml(tmp_path / "policy.yaml", _policy_payload())

    result = module.promote_skills(
        memory_root=str(memory_root),
        policy_path=str(policy_path),
        seed_paths=seed_paths,
        dry_run=True,
    )

    assert result["episode_count"] == 1
    assert result["eligible_count"] == 1
    assert result["skill_count"] == 1
    assert not Path(result["episode_index"]).exists()
    assert not Path(result["skill_index"]).exists()


def test_promote_skills_preserves_existing_non_proposed_skill(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(module, "datetime", _FixedDateTime)
    memory_root = tmp_path / "memory"
    policy = _policy_payload()
    policy_path = _write_yaml(tmp_path / "policy.yaml", policy)
    context_path = _write_yaml(tmp_path / "context.yaml", _context_payload())
    frame_plan_path = _write_json(
        tmp_path / "frame_plan.json",
        {"selected_frames": [{"id": "guardian"}]},
    )
    seed_paths = [
        str(
            _write_json(
                memory_root / "seeds" / "seed-1.json",
                _seed_payload(
                    "run-001",
                    "2026-03-18T09:00:00Z",
                    context_path,
                    frame_plan_path,
                    energy=0.45,
                ),
            )
        ),
        str(
            _write_json(
                memory_root / "seeds" / "seed-2.json",
                _seed_payload(
                    "run-002",
                    "2026-03-19T09:00:00Z",
                    context_path,
                    frame_plan_path,
                    energy=0.55,
                ),
            )
        ),
    ]
    episode = module.build_episodes(seed_paths, policy)[0]
    skill = module._build_skill(episode, policy)
    existing_path = memory_root / "skills" / f"{skill['skill_id']}.json"
    _write_json(existing_path, {**skill, "status": "approved"})

    result = module.promote_skills(
        memory_root=str(memory_root),
        policy_path=str(policy_path),
        seed_paths=seed_paths,
    )

    assert result["skill_count"] == 1
    assert json.loads(existing_path.read_text(encoding="utf-8"))["status"] == "approved"
    index = json.loads((memory_root / "skill_index.json").read_text(encoding="utf-8"))
    assert index["skills"][0]["status"] == "approved"
