import argparse
import os
from typing import Dict, Optional

from .ystm.storage import load_audit_log, load_nodes_payload, node_from_dict, save_nodes_payload


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Replay a YSTM update record.")
    parser.add_argument(
        "--nodes",
        default=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "reports", "ystm_demo", "nodes.json")
        ),
        help="Path to nodes.json.",
    )
    parser.add_argument(
        "--audit",
        default=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "reports", "ystm_demo", "audit_log.json")
        ),
        help="Path to audit_log.json.",
    )
    parser.add_argument("--update-id", required=True, help="UpdateRecord id to replay.")
    parser.add_argument(
        "--mode",
        choices=["before", "after"],
        default="before",
        help="Snapshot to apply from the update record.",
    )
    parser.add_argument("--output-nodes", help="Optional output path for nodes.json.")
    return parser


def _find_update(audit_log, update_id: str):
    for record in audit_log.updates:
        if record.id == update_id:
            return record
    return None


def _find_node_index(nodes, node_id: str) -> Optional[int]:
    for idx, node in enumerate(nodes):
        if node.id == node_id:
            return idx
    return None


def main() -> Dict[str, str]:
    parser = build_arg_parser()
    args = parser.parse_args()
    nodes, metadata = load_nodes_payload(args.nodes)
    audit_log = load_audit_log(args.audit)
    record = _find_update(audit_log, args.update_id)
    if record is None:
        raise SystemExit(f"UpdateRecord not found: {args.update_id}")

    snapshot = record.before if args.mode == "before" else record.after
    if snapshot is None:
        raise SystemExit(f"UpdateRecord {args.update_id} has no {args.mode} snapshot.")

    target_id = record.target
    node_index = _find_node_index(nodes, target_id)
    if node_index is None:
        raise SystemExit(f"Target node not found: {target_id}")

    nodes[node_index] = node_from_dict(snapshot)
    nodes_path = args.output_nodes or args.nodes
    save_nodes_payload(nodes_path, nodes, metadata)
    return {"nodes": nodes_path}


if __name__ == "__main__":
    paths = main()
    print(f"nodes.json: {paths['nodes']}")
