import json
import os
from typing import Dict, Iterable, List, Optional, Tuple

import yaml

from .ystm.schema import utc_now


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


def _write_json(path: str, payload: Dict[str, object]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def _load_policy(path: Optional[str]) -> Dict[str, object]:
    policy_path = path or _default_policy_path()
    if not os.path.exists(policy_path):
        return {}
    with open(policy_path, "r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return payload if isinstance(payload, dict) else {}


def ensure_episodes_current(
    memory_root: Optional[str] = None,
    policy_path: Optional[str] = None,
) -> Dict[str, object]:
    """Re-aggregate episodes and promote eligible skills before gating.

    Calls skill_promoter.promote_skills() so that skill JSONs are up-to-date
    before evaluate_skill() or review_skill() runs.
    """
    from .skill_promoter import promote_skills

    return promote_skills(
        memory_root=memory_root,
        policy_path=policy_path,
        dry_run=False,
    )


def list_skill_paths(memory_root: Optional[str] = None) -> List[str]:
    memory_root = memory_root or _default_memory_root()
    skills_dir = os.path.join(memory_root, "skills")
    if not os.path.isdir(skills_dir):
        return []
    return sorted(
        os.path.join(skills_dir, name) for name in os.listdir(skills_dir) if name.endswith(".json")
    )


def _score_ratio(
    actual: Optional[float], threshold: Optional[float], higher_is_better: bool
) -> Optional[float]:
    if threshold is None:
        return None
    if actual is None:
        return 0.0
    if higher_is_better:
        if threshold <= 0:
            return 1.0
        return min(1.0, actual / threshold)
    if actual <= 0:
        return 0.0
    return min(1.0, threshold / actual)


def _role_level(role: Optional[str], levels: Dict[str, int]) -> int:
    if not role or not levels:
        return 0
    return int(levels.get(role, 0))


def evaluate_skill(skill: Dict[str, object]) -> Tuple[bool, float, List[str]]:
    criteria = skill.get("criteria", {}) if isinstance(skill.get("criteria"), dict) else {}
    thresholds = (
        criteria.get("thresholds", {}) if isinstance(criteria.get("thresholds"), dict) else {}
    )

    rules: List[Tuple[str, bool]] = []
    scores: List[float] = []

    support = criteria.get("support_count")
    min_support = thresholds.get("min_support")
    if min_support is not None:
        rules.append(("min_support", support is not None and support >= min_support))
        ratio = _score_ratio(support, min_support, higher_is_better=True)
        if ratio is not None:
            scores.append(ratio)

    pass_rate = criteria.get("pass_rate")
    min_pass_rate = thresholds.get("min_pass_rate")
    if min_pass_rate is not None:
        rules.append(("min_pass_rate", pass_rate is not None and pass_rate >= min_pass_rate))
        ratio = _score_ratio(pass_rate, min_pass_rate, higher_is_better=True)
        if ratio is not None:
            scores.append(ratio)

    counterexample_rate = criteria.get("counterexample_rate")
    max_counterexample_rate = thresholds.get("max_counterexample_rate")
    if max_counterexample_rate is not None:
        rules.append(
            (
                "max_counterexample_rate",
                counterexample_rate is not None and counterexample_rate <= max_counterexample_rate,
            )
        )
        ratio = _score_ratio(counterexample_rate, max_counterexample_rate, higher_is_better=False)
        if ratio is not None:
            scores.append(ratio)

    energy_samples = criteria.get("energy_samples")
    min_energy_samples = thresholds.get("min_energy_samples")
    if min_energy_samples is not None:
        rules.append(
            (
                "min_energy_samples",
                energy_samples is not None and energy_samples >= min_energy_samples,
            )
        )
        ratio = _score_ratio(energy_samples, min_energy_samples, higher_is_better=True)
        if ratio is not None:
            scores.append(ratio)

    energy_stdev = criteria.get("energy_stdev")
    max_energy_stddev = thresholds.get("max_energy_stddev")
    if max_energy_stddev is not None:
        rules.append(
            ("max_energy_stddev", energy_stdev is not None and energy_stdev <= max_energy_stddev)
        )
        ratio = _score_ratio(energy_stdev, max_energy_stddev, higher_is_better=False)
        if ratio is not None:
            scores.append(ratio)

    recent_runs = criteria.get("recent_run_count")
    min_recent_runs = thresholds.get("min_recent_runs")
    if min_recent_runs is not None:
        rules.append(
            ("min_recent_runs", recent_runs is not None and recent_runs >= min_recent_runs)
        )
        ratio = _score_ratio(recent_runs, min_recent_runs, higher_is_better=True)
        if ratio is not None:
            scores.append(ratio)

    passed = all(passed for _, passed in rules) if rules else False
    score = sum(scores) / len(scores) if scores else (1.0 if passed else 0.0)
    return passed, round(score, 4), [rule_id for rule_id, _ in rules]


def _write_skill_index(memory_root: str) -> str:
    skills = []
    for path in list_skill_paths(memory_root):
        payload = _load_json(path)
        skills.append(
            {
                "skill_id": payload.get("skill_id"),
                "origin_episode": payload.get("origin_episode"),
                "status": payload.get("status"),
            }
        )
    index = {"generated_at": utc_now(), "skills": skills}
    index_path = os.path.join(memory_root, "skill_index.json")
    _write_json(index_path, index)
    return index_path


def review_skill(
    skill_path: str,
    decision: Optional[str] = None,
    reviewer: Optional[str] = None,
    reviewer_role: Optional[str] = None,
    note: Optional[str] = None,
    policy_path: Optional[str] = None,
    dry_run: bool = False,
) -> Dict[str, object]:
    policy = _load_policy(policy_path)
    review_policy = policy.get("review", {}) if isinstance(policy.get("review"), dict) else {}
    require_reviewer = review_policy.get("require_reviewer", True)
    require_role = review_policy.get("require_role", False)
    role_levels = (
        review_policy.get("role_levels", {})
        if isinstance(review_policy.get("role_levels"), dict)
        else {}
    )
    default_role = review_policy.get("default_role")
    min_role_approve = review_policy.get("require_role_min_approve")
    min_role_reject = review_policy.get("require_role_min_reject")
    require_pass = review_policy.get("require_pass", True)
    allow_override = review_policy.get("allow_override", False)
    auto_approve = review_policy.get("auto_approve", False)
    approve_status = review_policy.get("approve_status", "approved")
    reject_status = review_policy.get("reject_status", "rejected")
    default_reviewer = review_policy.get("default_reviewer", "auto")

    payload = _load_json(skill_path)
    passed, score, rule_ids = evaluate_skill(payload)
    current_status = payload.get("status")

    resolved_decision = decision
    if not resolved_decision and auto_approve:
        resolved_decision = approve_status
        reviewer = reviewer or default_reviewer
        reviewer_role = reviewer_role or default_role

    if not resolved_decision and current_status in {approve_status, reject_status}:
        return {
            "skill_id": payload.get("skill_id"),
            "status": current_status,
            "reviewed": False,
            "passed": passed,
            "score": score,
        }

    if not resolved_decision:
        return {
            "skill_id": payload.get("skill_id"),
            "status": payload.get("status"),
            "reviewed": False,
            "passed": passed,
            "score": score,
        }

    if require_reviewer and not reviewer:
        raise ValueError("Reviewer is required by policy.")
    if require_role and not reviewer_role:
        raise ValueError("Reviewer role is required by policy.")

    if require_pass and not passed and not allow_override:
        resolved_decision = reject_status

    if resolved_decision not in {approve_status, reject_status}:
        raise ValueError(f"Decision must be '{approve_status}' or '{reject_status}'.")

    reviewer_role = reviewer_role or default_role
    role_level = _role_level(reviewer_role, role_levels)
    if resolved_decision == approve_status and min_role_approve is not None:
        if role_level < int(min_role_approve):
            raise ValueError("Reviewer role is not sufficient to approve.")
    if resolved_decision == reject_status and min_role_reject is not None:
        if role_level < int(min_role_reject):
            raise ValueError("Reviewer role is not sufficient to reject.")

    payload["status"] = resolved_decision
    payload["gate"] = {
        "passed": passed,
        "rule_ids": rule_ids,
        "score": score,
        "role": reviewer_role,
        "role_level": role_level,
    }
    payload["review"] = {
        "decision": resolved_decision,
        "reviewer": reviewer,
        "reviewer_role": reviewer_role,
        "reviewed_at": utc_now(),
        "note": note,
        "auto": auto_approve and resolved_decision == approve_status,
    }

    if not dry_run:
        _write_json(skill_path, payload)

    return {
        "skill_id": payload.get("skill_id"),
        "status": resolved_decision,
        "reviewed": True,
        "passed": passed,
        "score": score,
    }


def review_skills(
    skill_paths: Iterable[str],
    decision: Optional[str] = None,
    reviewer: Optional[str] = None,
    reviewer_role: Optional[str] = None,
    note: Optional[str] = None,
    memory_root: Optional[str] = None,
    policy_path: Optional[str] = None,
    dry_run: bool = False,
) -> Dict[str, object]:
    results = []
    for path in skill_paths:
        results.append(
            review_skill(
                path,
                decision=decision,
                reviewer=reviewer,
                reviewer_role=reviewer_role,
                note=note,
                policy_path=policy_path,
                dry_run=dry_run,
            )
        )
    index_path = ""
    if not dry_run and memory_root:
        index_path = _write_skill_index(memory_root)
    return {"results": results, "skill_index": index_path}
