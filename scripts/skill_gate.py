"""
Skill gate entrypoint migrated from tonesoul/cli/run_skill_gate.py.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.skill_gate import list_skill_paths, review_skills  # noqa: E402


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Review and promote skills.")
    parser.add_argument("--memory-root", help="Override memory root.")
    parser.add_argument("--policy", help="Override memory policy YAML.")
    parser.add_argument("--skill-id", help="Review a specific skill id.")
    parser.add_argument("--skill-path", help="Review a specific skill path.")
    parser.add_argument("--all", action="store_true", help="Review all skills.")
    parser.add_argument("--approve", action="store_true", help="Approve skills.")
    parser.add_argument("--reject", action="store_true", help="Reject skills.")
    parser.add_argument("--reviewer", help="Reviewer name (required by policy).")
    parser.add_argument("--reviewer-role", help="Reviewer role (required by policy).")
    parser.add_argument("--note", help="Optional review note.")
    parser.add_argument("--dry-run", action="store_true", help="Do not write updates.")
    return parser


def _default_memory_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tonesoul", "memory"))


def _resolve_memory_root(path: Optional[str]) -> str:
    if not path:
        return _default_memory_root()
    if os.path.isabs(path):
        return path
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tonesoul"))
    candidate = os.path.abspath(os.path.join(workspace_root, path))
    if os.path.exists(candidate):
        return candidate
    repo_root = os.path.abspath(os.path.join(workspace_root, ".."))
    return os.path.abspath(os.path.join(repo_root, path))


def _resolve_skill_paths(memory_root: str, skill_id: str) -> str:
    skills_dir = os.path.join(memory_root, "skills")
    return os.path.join(skills_dir, f"{skill_id}.json")


def main() -> Dict[str, object]:
    parser = build_arg_parser()
    args = parser.parse_args()

    memory_root = _resolve_memory_root(args.memory_root)
    decision = None
    if args.approve:
        decision = "approved"
    if args.reject:
        if decision:
            raise ValueError("Choose only one of --approve or --reject.")
        decision = "rejected"

    if args.skill_path:
        skill_paths = [args.skill_path]
    elif args.skill_id:
        if not memory_root:
            raise ValueError("--memory-root is required when using --skill-id.")
        skill_paths = [_resolve_skill_paths(memory_root, args.skill_id)]
    elif args.all:
        skill_paths = list_skill_paths(memory_root)
    else:
        raise ValueError("Provide --skill-path, --skill-id, or --all.")

    return review_skills(
        skill_paths,
        decision=decision,
        reviewer=args.reviewer,
        reviewer_role=args.reviewer_role,
        note=args.note,
        memory_root=memory_root,
        policy_path=args.policy,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    result = main()
    print(f"reviewed: {len(result['results'])}")
    if result.get("skill_index"):
        print(f"skill_index: {result['skill_index']}")
