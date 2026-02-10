import argparse
import os
from typing import Dict

from ..etcl_lifecycle import load_seed, save_seed, seed_path_for_run, transition


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Apply an ETCL lifecycle transition to a seed.")
    parser.add_argument("--seed-path", help="Path to seed JSON.")
    parser.add_argument("--run-id", help="Run ID to resolve seed path under memory/seeds.")
    parser.add_argument("--memory-root", help="Override memory root (default: 5.2/memory).")
    parser.add_argument("--event", required=True, help="Transition event or target state.")
    parser.add_argument("--actor", help="Actor performing the transition.")
    parser.add_argument("--reason", help="Reason for the transition.")
    parser.add_argument("--allow-same", action="store_true", help="Allow no-op transitions.")
    parser.add_argument("--output", help="Optional output path (default: overwrite seed).")
    return parser


def _resolve_seed_path(args: argparse.Namespace) -> str:
    if args.seed_path:
        return os.path.abspath(args.seed_path)
    if not args.run_id:
        raise ValueError("Provide --seed-path or --run-id.")
    memory_root = args.memory_root
    if memory_root:
        memory_root = os.path.abspath(memory_root)
    return os.path.abspath(seed_path_for_run(args.run_id, memory_root=memory_root))


def main() -> Dict[str, str]:
    parser = build_arg_parser()
    args = parser.parse_args()
    seed_path = _resolve_seed_path(args)
    seed = load_seed(seed_path)
    updated, entry = transition(
        seed,
        event=args.event,
        actor=args.actor,
        reason=args.reason,
        allow_same=args.allow_same,
    )
    output_path = os.path.abspath(args.output) if args.output else seed_path
    save_seed(output_path, updated)
    return {"seed": output_path, "transition": entry.get("event", "")}


if __name__ == "__main__":
    result = main()
    print(f"seed: {result['seed']}")
