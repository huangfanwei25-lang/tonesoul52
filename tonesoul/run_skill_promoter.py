import argparse
from typing import Dict

from .skill_promoter import promote_skills


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Promote memory episodes into skills.")
    parser.add_argument("--memory-root", help="Override memory root.")
    parser.add_argument("--policy", help="Override memory policy YAML.")
    parser.add_argument("--dry-run", action="store_true", help="Skip writing episode/skill files.")
    return parser


def main() -> Dict[str, object]:
    parser = build_arg_parser()
    args = parser.parse_args()
    return promote_skills(
        memory_root=args.memory_root,
        policy_path=args.policy,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    result = main()
    print(f"episode_count: {result['episode_count']}")
    print(f"eligible_count: {result['eligible_count']}")
    print(f"skill_count: {result['skill_count']}")
    print(f"episode_index: {result['episode_index']}")
    print(f"skill_index: {result['skill_index']}")
