import json
import os
from typing import Dict, List, Optional, Tuple

from .ystm.schema import utc_now


def _workspace_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _default_memory_root() -> str:
    return os.path.join(_workspace_root(), "memory")


def _load_json(path: str) -> Dict[str, object]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"JSON payload at {path} must be an object.")
    return payload


def _list_skill_paths(memory_root: str) -> List[str]:
    skills_dir = os.path.join(memory_root, "skills")
    if not os.path.isdir(skills_dir):
        return []
    return sorted(
        os.path.join(skills_dir, name) for name in os.listdir(skills_dir) if name.endswith(".json")
    )


def load_skills(
    memory_root: Optional[str] = None, status: str = "approved"
) -> List[Dict[str, object]]:
    memory_root = memory_root or _default_memory_root()
    skills = []
    for path in _list_skill_paths(memory_root):
        payload = _load_json(path)
        if status and payload.get("status") != status:
            continue
        skills.append(payload)
    return skills


def build_context_key(
    context: Dict[str, object], frame_plan: Optional[Dict[str, object]]
) -> Dict[str, object]:
    context_block = context.get("context", {}) if isinstance(context.get("context"), dict) else {}
    time_island = (
        context.get("time_island", {}) if isinstance(context.get("time_island"), dict) else {}
    )
    kairos = time_island.get("kairos", {}) if isinstance(time_island.get("kairos"), dict) else {}
    frame_ids = []
    if frame_plan and isinstance(frame_plan.get("selected_frames"), list):
        for item in frame_plan["selected_frames"]:
            if isinstance(item, dict) and item.get("id"):
                frame_ids.append(item["id"])
    return {
        "task": context_block.get("task"),
        "objective": context_block.get("objective"),
        "audience": context_block.get("audience"),
        "domain": context_block.get("domain"),
        "mode": context_block.get("mode"),
        "decision_mode": kairos.get("decision_mode"),
        "frame_ids": sorted(frame_ids),
    }


def _matches_when(when: Dict[str, object], context_key: Dict[str, object]) -> bool:
    for key, expected in when.items():
        actual = context_key.get(key)
        if isinstance(expected, list):
            actual_list = actual if isinstance(actual, list) else []
            if not all(item in actual_list for item in expected):
                return False
        else:
            if actual != expected:
                return False
    return True


def _context_text(context_key: Dict[str, object]) -> str:
    parts: List[str] = []
    for key in ("task", "objective", "audience", "domain", "mode", "decision_mode"):
        value = context_key.get(key)
        if isinstance(value, str) and value:
            parts.append(value)
    frame_ids = context_key.get("frame_ids")
    if isinstance(frame_ids, list):
        parts.extend([item for item in frame_ids if isinstance(item, str)])
    return " ".join(parts).lower()


def _keyword_matches(keywords: List[str], context_text: str) -> List[str]:
    matches = []
    for keyword in keywords:
        token = keyword.strip()
        if not token:
            continue
        if token.lower() in context_text:
            matches.append(token)
    return matches


def _trigger_summary(
    trigger_wells: List[Dict[str, object]],
    context_text: str,
) -> List[Dict[str, object]]:
    summary = []
    for well in trigger_wells:
        semantic = well.get("semantic") if isinstance(well.get("semantic"), dict) else {}
        keywords = semantic.get("keywords")
        if not isinstance(keywords, list):
            keywords = []
        strength = well.get("attraction_strength") or 0.0
        try:
            strength = float(strength)
        except (TypeError, ValueError):
            strength = 0.0
        matched = _keyword_matches(
            [item for item in keywords if isinstance(item, str)], context_text
        )
        summary.append(
            {
                "id": well.get("id"),
                "keywords": keywords,
                "matched": matched,
                "strength": strength,
            }
        )
    return summary


def _merge_directive(directives: Dict[str, bool], key: str) -> None:
    directives[key] = directives.get(key, False) or True


def _directives_for_action(action: Optional[str]) -> Dict[str, bool]:
    if action == "apply_governance_baseline":
        return {"force_gates": True, "require_evidence": True}
    return {}


def _directives_for_provides(provides: object) -> Dict[str, bool]:
    directives: Dict[str, bool] = {}
    if isinstance(provides, str):
        provides_list = [provides]
    elif isinstance(provides, list):
        provides_list = [item for item in provides if isinstance(item, str)]
    else:
        provides_list = []
    if "force_gates" in provides_list:
        directives["force_gates"] = True
    if "require_evidence" in provides_list:
        directives["require_evidence"] = True
    return directives


def _constraints_for_action(action: Optional[str]) -> List[str]:
    if action == "apply_governance_baseline":
        return [
            "- Execute YSS M0-M5 pipeline.",
            "- Enforce gate checks (context lint, router replay, constraint consistency, build/test, evidence completeness).",
            "- Evidence summary must be generated and referenced.",
            "- Audit request must include skills_applied.json when available.",
        ]
    return []


def _extend_unique(values: List[str], additions: List[str]) -> None:
    existing = set(values)
    for item in additions:
        if item not in existing:
            values.append(item)
            existing.add(item)


def apply_skills(
    context: Dict[str, object],
    frame_plan: Optional[Dict[str, object]],
    memory_root: Optional[str] = None,
    matching_policy: Optional[Dict[str, object]] = None,
) -> Tuple[Dict[str, object], List[Dict[str, object]], Dict[str, bool], List[str]]:
    context_key = build_context_key(context, frame_plan)
    context_text = _context_text(context_key)
    matching_policy = matching_policy or {}
    allow_trigger_only = bool(matching_policy.get("allow_trigger_only", False))
    min_trigger_strength = matching_policy.get("min_trigger_strength", 0.0)
    try:
        min_trigger_strength = float(min_trigger_strength)
    except (TypeError, ValueError):
        min_trigger_strength = 0.0
    applied = []
    directives: Dict[str, bool] = {"force_gates": False, "require_evidence": False}
    constraints_append: List[str] = []
    for skill in load_skills(memory_root):
        policy = (
            skill.get("policy_template", {})
            if isinstance(skill.get("policy_template"), dict)
            else {}
        )
        when = policy.get("when", {}) if isinstance(policy.get("when"), dict) else {}
        has_when = bool(when)
        if has_when and not _matches_when(when, context_key):
            continue
        if not has_when and not allow_trigger_only:
            continue
        action = policy.get("do")
        gravity_wells = (
            skill.get("gravity_wells", []) if isinstance(skill.get("gravity_wells"), list) else []
        )
        action_wells = [
            well
            for well in gravity_wells
            if isinstance(well, dict) and well.get("type") == "action" and well.get("action")
        ]
        actions = {action} if action else set()
        for well in action_wells:
            actions.add(well.get("action"))
            for key in _directives_for_provides(well.get("provides")):
                _merge_directive(directives, key)
        for action_id in actions:
            for key in _directives_for_action(action_id):
                _merge_directive(directives, key)
            _extend_unique(constraints_append, _constraints_for_action(action_id))
        trigger_wells = [
            well
            for well in gravity_wells
            if isinstance(well, dict) and well.get("type") == "trigger" and well.get("id")
        ]
        if trigger_wells:
            trigger_summary = _trigger_summary(trigger_wells, context_text)
            eligible_triggers = [item for item in trigger_summary if item["matched"]]
            if min_trigger_strength > 0:
                eligible_triggers = [
                    item for item in eligible_triggers if item["strength"] >= min_trigger_strength
                ]
            if not eligible_triggers:
                continue
        else:
            trigger_summary = []
            if not has_when:
                continue
        gravity_summary = {}
        if action_wells:
            gravity_summary["actions"] = [
                {
                    "id": well.get("id"),
                    "action": well.get("action"),
                    "provides": well.get("provides"),
                }
                for well in action_wells
            ]
        if trigger_wells:
            gravity_summary["triggers"] = trigger_summary
        applied.append(
            {
                "skill_id": skill.get("skill_id"),
                "origin_episode": skill.get("origin_episode"),
                "action": action,
                "note": policy.get("notes"),
                "when": when,
                "status": skill.get("status"),
                **({"gravity_wells": gravity_summary} if gravity_summary else {}),
            }
        )
    payload = {
        "generated_at": utc_now(),
        "context_key": context_key,
        "skills": applied,
        "directives": directives,
        "constraints_append": constraints_append,
        "note": "Approved skills applied without modifying model weights.",
    }
    return payload, applied, directives, constraints_append


def format_skill_section(
    applied: List[Dict[str, object]],
    directives: Optional[Dict[str, bool]] = None,
) -> str:
    if not applied:
        return ""
    lines = []
    lines.append("## Applied Skills")
    for skill in applied:
        action = skill.get("action") or "n/a"
        lines.append(f"- {skill.get('skill_id')} -> {action}")
    if directives:
        enabled = [key for key, value in directives.items() if value]
        if enabled:
            lines.append(f"- Directives: {', '.join(enabled)}")
    lines.append("")
    return "\n".join(lines)
