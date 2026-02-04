import argparse
import json
import os
from typing import Dict, List, Optional

import yaml

from .error_event import ErrorEvent, ErrorLedger
from .ystm.schema import stable_hash, utc_now


def _load_context(path: str) -> Dict[str, object]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Context payload must be a mapping.")
    return payload


def _load_frame_plan(path: Optional[str]) -> Optional[Dict[str, object]]:
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("Frame plan must be a mapping.")
    return payload


def _load_constraints(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def _load_skills(path: Optional[str]) -> Optional[List[Dict[str, object]]]:
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict):
        skills = payload.get("skills")
        if isinstance(skills, list):
            return skills
    return None


def build_execution_report(
    context: Dict[str, object],
    frame_plan: Optional[Dict[str, object]],
    constraints: Optional[str],
    error_event_id: Optional[str] = None,
    skills_applied: Optional[List[Dict[str, object]]] = None,
) -> str:
    context_hash = stable_hash(yaml.safe_dump(context, sort_keys=True))
    lines = []
    lines.append("# Execution Report (M3)")
    lines.append("")
    lines.append(f"- Generated at: {utc_now()}")
    lines.append(f"- Context hash: {context_hash}")
    if frame_plan:
        lines.append(f"- Frame plan: {frame_plan.get('input_hash', 'n/a')}")
    lines.append("")
    lines.append("## Summary")
    lines.append("This report records execution metadata and pointers only.")
    lines.append("")
    lines.append("## Inputs")
    lines.append(f"- Task: {context.get('context', {}).get('task')}")
    lines.append(f"- Objective: {context.get('context', {}).get('objective')}")
    lines.append("")
    if frame_plan:
        lines.append("## Selected Frames")
        for item in frame_plan.get("selected_frames", []):
            line = f"- {item.get('id')} (score={item.get('score')}) roles={item.get('roles')}"
            gov_roles = item.get("governance_roles")
            if gov_roles:
                line = f"{line} gov_roles={gov_roles}"
            lines.append(line)
        lines.append("")
        rejected = frame_plan.get("rejected_frames", [])
        if isinstance(rejected, list) and rejected:
            lines.append("## Rejected Frames")
            for item in rejected:
                if not isinstance(item, dict):
                    continue
                lines.append(
                    f"- {item.get('id')} (score={item.get('score')}, reason={item.get('reason')})"
                )
            lines.append("")
        role_summary = frame_plan.get("role_summary")
        if isinstance(role_summary, dict) and role_summary:
            lines.append("## Role Summary")
            lines.append(f"- Operational roles: {role_summary.get('operational_roles')}")
            lines.append(f"- Governance roles: {role_summary.get('governance_roles')}")
            if role_summary.get("max_governance_level") is not None:
                lines.append(f"- Max governance level: {role_summary.get('max_governance_level')}")
            lines.append("")
        council_summary = frame_plan.get("council_summary")
        if isinstance(council_summary, dict) and council_summary:
            lines.append("## Council Summary")
            lines.append(
                f"- Decision: {council_summary.get('decision')} "
                f"(mode={council_summary.get('decision_mode')})"
            )
            lines.append(
                f"- Weighted score: {council_summary.get('weighted_score')} | "
                f"Dissent ratio: {council_summary.get('dissent_ratio')}"
            )
            signals = council_summary.get("signals")
            if isinstance(signals, dict):
                lines.append(
                    f"- Risk roles: {signals.get('risk_roles')} | Audit roles: {signals.get('audit_roles')}"
                )
            votes = council_summary.get("votes")
            if isinstance(votes, list) and votes:
                lines.append("Votes:")
                for vote in votes:
                    if not isinstance(vote, dict):
                        continue
                    lines.append(
                        f"- {vote.get('governance_role')} "
                        f"weight={vote.get('weight')} stance={vote.get('stance')} "
                        f"score={vote.get('score')}"
                    )
            lines.append("")
    if constraints:
        lines.append("## Constraint Stack Snapshot")
        lines.append("```")
        lines.append(constraints.strip())
        lines.append("```")
        lines.append("")
    if skills_applied and (not constraints or "## Applied Skills" not in constraints):
        lines.append("## Applied Skills")
        for skill in skills_applied:
            lines.append(f"- {skill.get('skill_id')} -> {skill.get('action')}")
        lines.append("")
    lines.append("## Outputs")
    lines.append("- Placeholder: no generation performed in M3 skeleton.")
    if error_event_id:
        lines.append(f"- ErrorEvent recorded: {error_event_id}")
    lines.append("")
    lines.append("## Audit Hooks")
    lines.append("- Provide pointers to YSTM nodes/audit logs when available.")
    lines.append("")
    return "\n".join(lines)


def record_error_event(error_event_path: str, ledger_path: str) -> str:
    with open(error_event_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    event = ErrorEvent(**payload)
    ledger = ErrorLedger(ledger_path)
    return ledger.record(event)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate execution report for YSS M3.")
    parser.add_argument("--context", required=True, help="Path to context.yaml.")
    parser.add_argument("--frame-plan", help="Optional path to frame_plan.json.")
    parser.add_argument("--constraints", help="Optional path to constraints.md.")
    parser.add_argument("--skills-applied", help="Optional path to skills_applied.json.")
    parser.add_argument("--output", help="Output path for execution_report.md.")
    parser.add_argument("--error-event", help="Optional ErrorEvent JSON to record.")
    parser.add_argument("--error-ledger", help="Optional error_ledger.jsonl path.")
    return parser


def _resolve_output(path: Optional[str], context_path: str) -> str:
    if path:
        return os.path.abspath(path)
    context_dir = os.path.dirname(os.path.abspath(context_path))
    return os.path.join(context_dir, "execution_report.md")


def main() -> Dict[str, str]:
    parser = build_arg_parser()
    args = parser.parse_args()
    context = _load_context(args.context)
    frame_plan = _load_frame_plan(args.frame_plan)
    constraints = _load_constraints(args.constraints)
    skills_applied = _load_skills(args.skills_applied)
    error_event_id = None
    if args.error_event:
        ledger_path = args.error_ledger
        if not ledger_path:
            ledger_path = os.path.join(
                os.path.dirname(os.path.abspath(args.context)), "error_ledger.jsonl"
            )
        error_event_id = record_error_event(args.error_event, ledger_path)
    report = build_execution_report(
        context,
        frame_plan,
        constraints,
        error_event_id=error_event_id,
        skills_applied=skills_applied,
    )
    output_path = _resolve_output(args.output, args.context)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(report)
    return {"execution_report": output_path}


if __name__ == "__main__":
    paths = main()
    print(f"execution_report.md: {paths['execution_report']}")
