import argparse
import json
import os
from typing import Dict, List, Optional, Tuple

import yaml

from .council.runtime import build_council_summary
from .ystm.schema import stable_hash, utc_now


def _load_context(path: str) -> Dict[str, object]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Context payload must be a mapping.")
    return payload


def _load_registry(path: str) -> List[Dict[str, object]]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError("Frame registry must be a list of frames.")
    return payload


def _default_role_catalog_path() -> str:
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "spec", "governance", "role_catalog.yaml")
    )


def _load_role_catalog(path: Optional[str]) -> Dict[str, object]:
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return payload if isinstance(payload, dict) else {}


def _role_alignment(
    roles: object,
    catalog: Dict[str, object],
) -> Tuple[List[str], List[str], List[Dict[str, object]]]:
    roles_list = [str(role) for role in roles] if isinstance(roles, list) else []
    operational = catalog.get("operational_roles")
    operational = operational if isinstance(operational, dict) else {}
    governance = catalog.get("governance_roles")
    governance = governance if isinstance(governance, dict) else {}
    governance_roles: List[str] = []
    role_map: List[Dict[str, object]] = []
    for role in roles_list:
        meta = operational.get(role)
        meta = meta if isinstance(meta, dict) else {}
        aligns_to = meta.get("aligns_to")
        level = None
        if aligns_to:
            gov_meta = governance.get(aligns_to)
            if isinstance(gov_meta, dict):
                level = gov_meta.get("level")
        role_map.append(
            {
                "role": role,
                "governance_role": aligns_to or "unknown",
                "governance_level": level,
            }
        )
        if aligns_to and aligns_to not in governance_roles:
            governance_roles.append(aligns_to)
    return roles_list, governance_roles, role_map


def _score_frame(frame: Dict[str, object], context: Dict[str, object]) -> int:
    score = 0
    signals = frame.get("signals", {}) if isinstance(frame.get("signals"), dict) else {}
    ctx = context.get("context", {}) if isinstance(context.get("context"), dict) else {}
    kairos = (
        context.get("time_island", {}).get("kairos", {})
        if isinstance(context.get("time_island"), dict)
        else {}
    )

    domain = str(ctx.get("domain", ""))
    decision_mode = str(kairos.get("decision_mode", ""))
    task = str(ctx.get("task", ""))
    objective = str(ctx.get("objective", ""))
    text = f"{task} {objective}".lower()

    if domain and domain in signals.get("domains", []):
        score += 2
    if decision_mode and decision_mode in signals.get("decision_modes", []):
        score += 1
    for keyword in signals.get("keywords", []):
        if keyword.lower() in text:
            score += 1
    return score


def route_frames(
    context: Dict[str, object],
    registry: List[Dict[str, object]],
    limit: int = 2,
) -> List[Tuple[Dict[str, object], int]]:
    if not registry:
        return []

    scored = []
    for frame in registry:
        scored.append((frame, _score_frame(frame, context)))
    scored.sort(key=lambda item: (-item[1], registry.index(item[0])))
    selected = [item for item in scored if item[1] > 0]
    if not selected:
        fallback = next((frame for frame in registry if frame.get("id") == "analysis"), registry[0])
        selected = [(fallback, 0)]
    return selected[:limit]


def build_frame_plan(
    context: Dict[str, object],
    registry: List[Dict[str, object]],
    role_catalog_path: Optional[str] = None,
) -> Dict[str, object]:
    scored = [(frame, _score_frame(frame, context)) for frame in registry]
    selected = route_frames(context, registry)
    selected_ids = {frame.get("id") for frame, _ in selected if frame.get("id")}
    rejected = []
    for frame, score in scored:
        frame_id = frame.get("id")
        if frame_id in selected_ids:
            continue
        reason = "score=0" if score == 0 else "below_cutoff"
        rejected.append({"id": frame_id, "score": score, "reason": reason})
    role_catalog_path = role_catalog_path or _default_role_catalog_path()
    role_catalog = _load_role_catalog(role_catalog_path)
    role_catalog_version = role_catalog.get("version") if isinstance(role_catalog, dict) else None
    selected_frames = []
    operational_roles: List[str] = []
    governance_roles: List[str] = []
    governance_levels: List[int] = []
    for frame, score in selected:
        roles_list, gov_roles, role_map = _role_alignment(frame.get("roles", []), role_catalog)
        operational_roles.extend(roles_list)
        for gov_role in gov_roles:
            if gov_role not in governance_roles:
                governance_roles.append(gov_role)
        for item in role_map:
            level = item.get("governance_level")
            if isinstance(level, int):
                governance_levels.append(level)
        selected_frames.append(
            {
                "id": frame.get("id"),
                "score": score,
                "roles": roles_list,
                "governance_roles": gov_roles,
                "role_map": role_map,
                "description": frame.get("description"),
            }
        )
    role_summary = None
    if operational_roles or governance_roles:
        role_summary = {
            "operational_roles": sorted(set(operational_roles)),
            "governance_roles": sorted(set(governance_roles)),
            "max_governance_level": max(governance_levels) if governance_levels else None,
        }
    council_summary = build_council_summary(context, selected_frames, role_summary, role_catalog)
    context_hash = stable_hash(json.dumps(context, sort_keys=True))
    plan = {
        "generated_at": utc_now(),
        "router_version": "0.1",
        "input_hash": context_hash,
        "role_catalog": role_catalog_path if role_catalog else None,
        "role_catalog_version": role_catalog_version,
        "role_summary": role_summary,
        "council_summary": council_summary,
        "selected_frames": selected_frames,
        "rejected_frames": rejected,
        "note": "Router is deterministic; same context yields same selection.",
    }
    return plan


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Route frames for YSS M1.")
    parser.add_argument(
        "--context",
        required=True,
        help="Path to context.yaml.",
    )
    parser.add_argument(
        "--registry",
        default=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "spec", "frames", "frame_registry.json")
        ),
        help="Path to frame registry JSON.",
    )
    parser.add_argument(
        "--role-catalog",
        help="Optional governance role catalog (default: spec/governance/role_catalog.yaml).",
    )
    parser.add_argument("--output", help="Output path for frame_plan.json.")
    return parser


def _resolve_output(path: Optional[str], context_path: str) -> str:
    if path:
        return os.path.abspath(path)
    context_dir = os.path.dirname(os.path.abspath(context_path))
    return os.path.join(context_dir, "frame_plan.json")


def main() -> Dict[str, str]:
    parser = build_arg_parser()
    args = parser.parse_args()
    context = _load_context(args.context)
    registry = _load_registry(args.registry)
    plan = build_frame_plan(context, registry, role_catalog_path=args.role_catalog)
    output_path = _resolve_output(args.output, args.context)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(plan, handle, indent=2)
    return {"frame_plan": output_path}


if __name__ == "__main__":
    paths = main()
    print(f"frame_plan.json: {paths['frame_plan']}")
