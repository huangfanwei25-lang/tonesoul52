import json
import os
from datetime import datetime, timedelta, timezone
from statistics import mean, pstdev
from typing import Dict, Iterable, List, Optional

import yaml

from .ystm.schema import stable_hash, utc_now


def _workspace_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _default_memory_root() -> str:
    return os.path.join(_workspace_root(), "memory")


def _default_policy_path() -> str:
    return os.path.join(_workspace_root(), "spec", "memory", "memory_policy.yaml")


def _load_json(path: str) -> Dict[str, object]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"JSON payload at {path} must be an object.")
    return payload


def _load_yaml(path: str) -> Dict[str, object]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"YAML payload at {path} must be a mapping.")
    return payload


def _write_json(path: str, payload: Dict[str, object]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def _build_skill_index(memory_root: str) -> Dict[str, object]:
    skills_dir = os.path.join(memory_root, "skills")
    skills = []
    if os.path.isdir(skills_dir):
        for name in os.listdir(skills_dir):
            if not name.endswith(".json"):
                continue
            payload = _load_json(os.path.join(skills_dir, name))
            skills.append(
                {
                    "skill_id": payload.get("skill_id"),
                    "origin_episode": payload.get("origin_episode"),
                    "status": payload.get("status"),
                }
            )
    return {"generated_at": utc_now(), "skills": skills}


def _parse_time(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _format_time(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _list_seed_paths(memory_root: str) -> List[str]:
    seeds_dir = os.path.join(memory_root, "seeds")
    if not os.path.isdir(seeds_dir):
        return []
    seeds = [
        os.path.join(seeds_dir, name) for name in os.listdir(seeds_dir) if name.endswith(".json")
    ]
    return sorted(seeds)


def _extract_context(seed: Dict[str, object]) -> Dict[str, Optional[str]]:
    context_path = (seed.get("pointers") or {}).get("context")
    if not context_path or not os.path.exists(context_path):
        return {"domain": None, "mode": None, "decision_mode": None}
    payload = _load_yaml(context_path)
    context = payload.get("context", {}) if isinstance(payload, dict) else {}
    time_island = payload.get("time_island", {}) if isinstance(payload, dict) else {}
    kairos = time_island.get("kairos", {}) if isinstance(time_island, dict) else {}
    return {
        "task": context.get("task") if isinstance(context, dict) else None,
        "objective": context.get("objective") if isinstance(context, dict) else None,
        "audience": context.get("audience") if isinstance(context, dict) else None,
        "domain": context.get("domain") if isinstance(context, dict) else None,
        "mode": context.get("mode") if isinstance(context, dict) else None,
        "decision_mode": kairos.get("decision_mode") if isinstance(kairos, dict) else None,
    }


def _extract_frames(seed: Dict[str, object]) -> List[str]:
    frame_path = (seed.get("pointers") or {}).get("frame_plan")
    if not frame_path or not os.path.exists(frame_path):
        return []
    payload = _load_json(frame_path)
    frames = payload.get("selected_frames", []) if isinstance(payload, dict) else []
    frame_ids = [frame.get("id") for frame in frames if isinstance(frame, dict) and frame.get("id")]
    return sorted(frame_ids)


def _build_episode_key(seed: Dict[str, object], policy: Dict[str, object]) -> Dict[str, object]:
    fields = (policy.get("episode_key") or {}).get("fields", [])
    context = _extract_context(seed)
    frame_ids = _extract_frames(seed)
    key: Dict[str, object] = {}
    for field in fields:
        if field == "frame_ids":
            key[field] = frame_ids
        else:
            key[field] = context.get(field)
    return key


def _key_has_value(key: Dict[str, object]) -> bool:
    for value in key.values():
        if value not in (None, "", []):
            return True
    return False


def _init_episode(episode_id: str, key: Dict[str, object]) -> Dict[str, object]:
    return {
        "episode_id": episode_id,
        "key": key,
        "runs": [],
        "gate_pass_flags": [],
        "created_at": [],
        "energy_means": [],
    }


def _finalize_episode(
    episode: Dict[str, object],
    policy: Dict[str, object],
) -> Dict[str, object]:
    run_ids = episode["runs"]
    pass_flags = episode["gate_pass_flags"]
    created_at = episode["created_at"]
    energy_means = episode["energy_means"]
    run_count = len(run_ids)
    pass_count = sum(1 for flag in pass_flags if flag)
    pass_rate = pass_count / run_count if run_count else 0.0
    counterexample_count = run_count - pass_count
    counterexample_rate = counterexample_count / run_count if run_count else 0.0

    energy_mean = mean(energy_means) if energy_means else None
    energy_stdev = (
        pstdev(energy_means) if len(energy_means) > 1 else (0.0 if energy_means else None)
    )

    parsed_times = [time for time in (_parse_time(item) for item in created_at) if time]
    first_seen = _format_time(min(parsed_times)) if parsed_times else None
    last_seen = _format_time(max(parsed_times)) if parsed_times else None

    recent_window = (policy.get("promotion") or {}).get("recent_window_days", 0)
    recent_count = 0
    if parsed_times and recent_window:
        cutoff = datetime.now(timezone.utc) - timedelta(days=recent_window)
        recent_count = sum(1 for value in parsed_times if value >= cutoff)

    return {
        "episode_id": episode["episode_id"],
        "key": episode["key"],
        "runs": run_ids,
        "run_count": run_count,
        "gate_pass_count": pass_count,
        "gate_pass_rate": round(pass_rate, 4),
        "counterexample_count": counterexample_count,
        "counterexample_rate": round(counterexample_rate, 4),
        "energy": {
            "E_total_mean_mean": round(energy_mean, 6) if energy_mean is not None else None,
            "E_total_mean_stdev": round(energy_stdev, 6) if energy_stdev is not None else None,
            "samples": len(energy_means),
        },
        "first_seen": first_seen,
        "last_seen": last_seen,
        "recent_run_count": recent_count,
        "generated_at": utc_now(),
    }


def build_episodes(
    seed_paths: Iterable[str],
    policy: Dict[str, object],
) -> List[Dict[str, object]]:
    include_archived = (policy.get("promotion") or {}).get("include_archived", True)
    episodes: Dict[str, Dict[str, object]] = {}
    for seed_path in seed_paths:
        seed = _load_json(seed_path)
        if not include_archived and seed.get("archived"):
            continue
        key = _build_episode_key(seed, policy)
        if not _key_has_value(key):
            continue
        key_hash = stable_hash(json.dumps(key, sort_keys=True))
        episode_id = f"ep_{key_hash}"
        episode = episodes.setdefault(episode_id, _init_episode(episode_id, key))

        run_id = seed.get("run_id")
        if run_id:
            episode["runs"].append(run_id)

        created_at = seed.get("created_at")
        if created_at:
            episode["created_at"].append(created_at)

        gate_pass = seed.get("gate_overall") == "PASS"
        episode["gate_pass_flags"].append(gate_pass)

        ystm_stats = seed.get("ystm_stats", {})
        if isinstance(ystm_stats, dict) and ystm_stats.get("E_total_mean") is not None:
            episode["energy_means"].append(float(ystm_stats["E_total_mean"]))

    return [_finalize_episode(episode, policy) for episode in episodes.values()]


def _eligible(episode: Dict[str, object], policy: Dict[str, object]) -> bool:
    promotion = policy.get("promotion") or {}
    support = episode.get("run_count", 0)
    pass_rate = episode.get("gate_pass_rate", 0.0)
    counterexample_rate = episode.get("counterexample_rate", 0.0)
    energy = episode.get("energy", {}) or {}
    energy_samples = energy.get("samples", 0) or 0
    energy_stdev = energy.get("E_total_mean_stdev")
    recent_runs = episode.get("recent_run_count", 0)

    min_support = promotion.get("min_support", 0)
    min_pass_rate = promotion.get("min_pass_rate", 0.0)
    max_counterexample_rate = promotion.get("max_counterexample_rate", 1.0)
    min_energy_samples = promotion.get("min_energy_samples", 0)
    max_energy_stddev = promotion.get("max_energy_stddev")
    min_recent_runs = promotion.get("min_recent_runs", 0)

    if support < min_support:
        return False
    if pass_rate < min_pass_rate:
        return False
    if counterexample_rate > max_counterexample_rate:
        return False
    if min_energy_samples and energy_samples < min_energy_samples:
        return False
    if max_energy_stddev is not None:
        if energy_stdev is None or energy_stdev > max_energy_stddev:
            return False
    if min_recent_runs and recent_runs < min_recent_runs:
        return False
    return True


def _build_skill(episode: Dict[str, object], policy: Dict[str, object]) -> Dict[str, object]:
    defaults = policy.get("defaults") or {}
    policy_action = defaults.get("policy_action", "apply_governance_baseline")
    skill_seed = f"{episode['episode_id']}:{policy.get('version', '0.1')}"
    skill_id = f"skill_{stable_hash(skill_seed)}"
    thresholds = policy.get("promotion") or {}

    return {
        "skill_id": skill_id,
        "origin_episode": episode["episode_id"],
        "generated_at": utc_now(),
        "status": thresholds.get("status", "proposed"),
        "criteria": {
            "support_count": episode.get("run_count"),
            "pass_rate": episode.get("gate_pass_rate"),
            "counterexample_rate": episode.get("counterexample_rate"),
            "energy_samples": (episode.get("energy") or {}).get("samples"),
            "energy_stdev": (episode.get("energy") or {}).get("E_total_mean_stdev"),
            "recent_run_count": episode.get("recent_run_count"),
            "thresholds": {
                "min_support": thresholds.get("min_support"),
                "min_pass_rate": thresholds.get("min_pass_rate"),
                "max_counterexample_rate": thresholds.get("max_counterexample_rate"),
                "min_energy_samples": thresholds.get("min_energy_samples"),
                "max_energy_stddev": thresholds.get("max_energy_stddev"),
                "min_recent_runs": thresholds.get("min_recent_runs"),
                "recent_window_days": thresholds.get("recent_window_days"),
            },
        },
        "policy_template": {
            "when": episode.get("key"),
            "do": policy_action,
            "notes": "Derived from repeated run patterns under memory promotion policy.",
        },
        "governance": {
            "reviewer": defaults.get("reviewer", "auto"),
            "version": defaults.get("skill_version", "1.0.0"),
            "revokable": defaults.get("revokable", True),
        },
    }


def promote_skills(
    memory_root: Optional[str] = None,
    policy_path: Optional[str] = None,
    seed_paths: Optional[Iterable[str]] = None,
    dry_run: bool = False,
) -> Dict[str, object]:
    memory_root = memory_root or _default_memory_root()
    policy_path = policy_path or _default_policy_path()
    policy = _load_yaml(policy_path)
    seed_paths = list(seed_paths) if seed_paths is not None else _list_seed_paths(memory_root)

    episodes = build_episodes(seed_paths, policy)
    eligible = [episode for episode in episodes if _eligible(episode, policy)]
    skills = [_build_skill(episode, policy) for episode in eligible]

    episode_index = {
        "generated_at": utc_now(),
        "episodes": [
            {
                "episode_id": episode["episode_id"],
                "run_count": episode["run_count"],
                "gate_pass_rate": episode["gate_pass_rate"],
                "counterexample_rate": episode["counterexample_rate"],
                "recent_run_count": episode["recent_run_count"],
                "energy_samples": (episode.get("energy") or {}).get("samples"),
                "key": episode["key"],
            }
            for episode in episodes
        ],
    }
    {
        "generated_at": utc_now(),
        "skills": [
            {
                "skill_id": skill["skill_id"],
                "origin_episode": skill["origin_episode"],
                "status": skill["status"],
            }
            for skill in skills
        ],
    }

    if not dry_run:
        episodes_dir = os.path.join(memory_root, "episodes")
        skills_dir = os.path.join(memory_root, "skills")
        os.makedirs(episodes_dir, exist_ok=True)
        os.makedirs(skills_dir, exist_ok=True)

        for episode in episodes:
            episode_path = os.path.join(episodes_dir, f"{episode['episode_id']}.json")
            _write_json(episode_path, episode)

        for skill in skills:
            skill_path = os.path.join(skills_dir, f"{skill['skill_id']}.json")
            if os.path.exists(skill_path):
                existing = _load_json(skill_path)
                if existing.get("status") and existing.get("status") != "proposed":
                    continue
            _write_json(skill_path, skill)

        _write_json(os.path.join(memory_root, "episode_index.json"), episode_index)
        _write_json(os.path.join(memory_root, "skill_index.json"), _build_skill_index(memory_root))

    return {
        "episode_count": len(episodes),
        "eligible_count": len(eligible),
        "skill_count": len(skills),
        "episode_index": os.path.join(memory_root, "episode_index.json"),
        "skill_index": os.path.join(memory_root, "skill_index.json"),
    }
