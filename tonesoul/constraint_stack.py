import argparse
import os
from typing import Dict, List, Optional

import yaml

from .action_set import resolve_action_set
from .mercy_objective import resolve_mercy_objective
from .ystm.schema import stable_hash, utc_now


def _load_context(path: str) -> Dict[str, object]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Context payload must be a mapping.")
    return payload


def _load_constraints_template(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def _merge_constraints(context: Dict[str, object]) -> List[str]:
    constraints = (
        context.get("constraints", []) if isinstance(context.get("constraints"), list) else []
    )
    assumptions = (
        context.get("assumptions", []) if isinstance(context.get("assumptions"), list) else []
    )
    merged = ["Context constraints:"] + [f"- {item}" for item in constraints]
    merged.append("")
    merged.append("Assumptions:")
    merged.extend([f"- {item}" for item in assumptions])
    return merged


def _format_action_set(context: Dict[str, object]) -> List[str]:
    action_set = resolve_action_set(context)
    lines = []
    lines.append("## Action Set")
    lines.append(f"- Decision mode: {action_set.get('decision_mode')}")
    lines.append("- Allowed actions:")
    for action in action_set.get("allowed_actions", []):
        lines.append(f"  - {action}")
    strict_policy = action_set.get("strict_mode_policy")
    if isinstance(strict_policy, dict):
        lines.append("- Strict mode policy:")
        for mode in ("cautious", "lockdown"):
            actions = strict_policy.get(mode)
            if isinstance(actions, list):
                lines.append(f"  - {mode}: {', '.join(actions)}")
    rationale = action_set.get("rationale")
    if rationale:
        lines.append(f"- Rationale: {rationale}")
    return lines


def _format_mercy_objective(
    context: Dict[str, object],
    objective: Optional[Dict[str, object]] = None,
) -> List[str]:
    if objective is None:
        objective = resolve_mercy_objective(context)
    lines = []
    lines.append("## Mercy Objective")
    lines.append(f"- Decision mode: {objective.get('decision_mode')}")
    lines.append(f"- Score: {objective.get('score')}")
    lines.append("- Weights:")
    for key, value in objective.get("weights", {}).items():
        lines.append(f"  - {key}: {value:.3f}")
    lines.append("- Signals:")
    for key, value in objective.get("signals", {}).items():
        lines.append(f"  - {key}: {value:.2f}")
    rationale = objective.get("rationale")
    if rationale:
        lines.append(f"- Rationale: {rationale}")
    return lines


def build_constraints_doc(
    context: Dict[str, object],
    template_text: str,
    frame_plan_path: Optional[str] = None,
    mercy_objective: Optional[Dict[str, object]] = None,
) -> str:
    context_hash = stable_hash(yaml.safe_dump(context, sort_keys=True))
    lines = []
    lines.append("# Constraint Stack")
    lines.append("")
    lines.append(f"- Generated at: {utc_now()}")
    lines.append(f"- Context hash: {context_hash}")
    if frame_plan_path:
        lines.append(f"- Frame plan: {frame_plan_path}")
    lines.append("")
    lines.append("## Template")
    lines.append(template_text.strip())
    lines.append("")
    lines.append("## Context Constraints")
    lines.extend(_merge_constraints(context))
    lines.append("")
    lines.extend(_format_action_set(context))
    lines.append("")
    lines.extend(_format_mercy_objective(context, objective=mercy_objective))
    lines.append("")
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build constraint stack for YSS M2.")
    parser.add_argument("--context", required=True, help="Path to context.yaml.")
    parser.add_argument("--frame-plan", help="Optional path to frame_plan.json.")
    parser.add_argument(
        "--template",
        default=os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "spec", "constraints", "constraints_template.md"
            )
        ),
        help="Constraint template path.",
    )
    parser.add_argument("--output", help="Output path for constraints.md.")
    return parser


def _resolve_output(path: Optional[str], context_path: str) -> str:
    if path:
        return os.path.abspath(path)
    context_dir = os.path.dirname(os.path.abspath(context_path))
    return os.path.join(context_dir, "constraints.md")


def main() -> Dict[str, str]:
    parser = build_arg_parser()
    args = parser.parse_args()
    context = _load_context(args.context)
    template_text = _load_constraints_template(args.template)
    doc = build_constraints_doc(context, template_text, frame_plan_path=args.frame_plan)
    output_path = _resolve_output(args.output, args.context)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(doc)
    return {"constraints": output_path}


if __name__ == "__main__":
    paths = main()
    print(f"constraints.md: {paths['constraints']}")
