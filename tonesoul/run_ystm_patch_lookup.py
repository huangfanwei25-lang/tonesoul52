import argparse
import json
import os
from typing import Dict, List, Optional

from .ystm.storage import load_nodes_payload


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Lookup YSTM patch history in nodes.")
    parser.add_argument(
        "--nodes",
        default=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "reports", "ystm_demo", "nodes.json")
        ),
        help="Path to nodes.json.",
    )
    parser.add_argument("--node-id", help="Filter by node id.")
    parser.add_argument("--diff-id", help="Filter by diff id.")
    parser.add_argument("--include-empty", action="store_true", help="Include nodes with empty patch history.")
    parser.add_argument("--output", help="Optional output JSON path.")
    return parser


def _node_entry(node_id: str, patch_history: List[str]) -> Dict[str, object]:
    return {
        "node_id": node_id,
        "patch_history": patch_history,
        "patch_count": len(patch_history),
    }


def main() -> Dict[str, str]:
    parser = build_arg_parser()
    args = parser.parse_args()
    nodes, _ = load_nodes_payload(args.nodes)

    if args.node_id and args.diff_id:
        parser.error("Choose either --node-id or --diff-id (not both).")

    results: List[Dict[str, object]] = []
    if args.node_id:
        node = next((item for item in nodes if item.id == args.node_id), None)
        if not node:
            raise SystemExit(f"Node not found: {args.node_id}")
        history = list(getattr(node, "patch_history", []) or [])
        results.append(_node_entry(node.id, history))
    elif args.diff_id:
        for node in nodes:
            history = list(getattr(node, "patch_history", []) or [])
            if args.diff_id in history:
                results.append(_node_entry(node.id, history))
    else:
        for node in nodes:
            history = list(getattr(node, "patch_history", []) or [])
            if history or args.include_empty:
                results.append(_node_entry(node.id, history))

    payload = {
        "nodes_path": os.path.abspath(args.nodes),
        "filters": {"node_id": args.node_id, "diff_id": args.diff_id},
        "result_count": len(results),
        "results": results,
    }

    output_path = args.output
    if output_path:
        output_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
    else:
        print(json.dumps(payload, indent=2))

    return {"patch_lookup": output_path or ""}


if __name__ == "__main__":
    main()
