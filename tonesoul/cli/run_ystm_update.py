import argparse
import copy
import json
import os
from typing import Dict, Optional

from ..tech_trace.capture import capture_record, load_text
from ..tech_trace.normalize import normalize_record
from ..ystm.diff import compute_batch_diff
from ..ystm.energy import EnergyConfig, apply_energy_totals
from ..ystm.governance import update_what, update_where
from ..ystm.representation import EmbeddingConfig
from ..ystm.schema import (
    UpdateGate,
    UpdateRecord,
    Where,
    WhereField,
    WhereTask,
    WhereTime,
    as_clean_dict,
    stable_hash,
    utc_now,
)
from ..ystm.storage import load_audit_log, load_nodes_payload, save_audit_log, save_nodes_payload


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Apply WHAT/WHERE updates to YSTM nodes.")
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
    parser.add_argument("--node-id", required=True, help="Target node id.")
    parser.add_argument("--rationale", default="Manual update.")
    parser.add_argument("--reviewer", default=None)
    parser.add_argument("--error-ledger", help="Optional error_ledger.jsonl path.")

    parser.add_argument("--what", help="New text content (WHAT update).")
    parser.add_argument("--embedding-dims", type=int, default=None)
    parser.add_argument("--alpha", type=float, default=1.0)
    parser.add_argument("--beta", type=float, default=0.0)
    parser.add_argument("--gamma", type=float, default=0.0)
    parser.add_argument("--no-normalize-energy", action="store_true")

    parser.add_argument("--where-mode", help="New where_field.mode value.")
    parser.add_argument("--where-domain", help="New where_task.domain value.")
    parser.add_argument("--turn-id", type=int, help="New where_time.turn_id value.")
    parser.add_argument("--event-index", type=int, help="New where_time.event_index value.")
    parser.add_argument("--where-field-confidence", type=float, default=None)
    parser.add_argument("--where-task-confidence", type=float, default=None)
    parser.add_argument("--where-submode", default=None)
    parser.add_argument("--where-subdomain", default=None)

    parser.add_argument("--output-nodes", help="Optional output path for nodes.json.")
    parser.add_argument("--output-audit", help="Optional output path for audit_log.json.")
    parser.add_argument(
        "--write-diff",
        action="store_true",
        help="Write a semantic diff artifact for this update.",
    )
    parser.add_argument("--diff-output", help="Optional output path for semantic diff JSON.")
    parser.add_argument(
        "--source-grade",
        choices=["A", "B", "C"],
        default=None,
        help="Evidence grade for the semantic diff.",
    )
    parser.add_argument(
        "--source-patch-id", default=None, help="Optional source patch id for the diff."
    )
    parser.add_argument(
        "--trace-level",
        choices=["standard", "full"],
        default="standard",
        help="Trace level tag for the semantic diff.",
    )

    parser.add_argument("--trace-input", help="Path to a Tech-Trace source note.")
    parser.add_argument("--trace-text", help="Inline Tech-Trace source note.")
    parser.add_argument("--trace-source-type", default="unknown", help="Trace source type.")
    parser.add_argument("--trace-uri", help="Trace source URI.")
    parser.add_argument("--trace-title", help="Trace source title.")
    parser.add_argument("--trace-grade", choices=["A", "B", "C"], help="Trace evidence grade.")
    parser.add_argument("--trace-retrieved-at", help="Trace retrieval timestamp.")
    parser.add_argument("--trace-verified-by", help="Trace verifier identity.")
    parser.add_argument("--trace-notes", help="Trace notes.")
    parser.add_argument("--trace-summary", help="Optional normalized summary.")
    parser.add_argument("--trace-max-length", type=int, help="Max normalized text length.")
    parser.add_argument("--trace-tag", action="append", help="Trace tag (repeatable).")
    parser.add_argument("--trace-claims", help="JSON list or path for trace claims.")
    parser.add_argument("--trace-links", help="JSON list or path for trace links.")
    parser.add_argument("--trace-attributions", help="JSON list or path for trace attributions.")
    parser.add_argument(
        "--trace-auto-claims",
        action="store_true",
        help="Auto-extract claims from trace text when --trace-claims is omitted.",
    )
    parser.add_argument(
        "--trace-claim-limit",
        type=int,
        default=12,
        help="Max claim count for trace auto-extraction.",
    )
    parser.add_argument(
        "--trace-claim-min-chars",
        type=int,
        default=24,
        help="Minimum characters for trace auto-extracted claims.",
    )
    parser.add_argument(
        "--trace-output-dir",
        help="Output directory for trace capture/normalize artifacts.",
    )
    return parser


def _where_update_requested(args: argparse.Namespace) -> bool:
    return any(
        value is not None
        for value in (
            args.where_mode,
            args.where_domain,
            args.turn_id,
            args.event_index,
            args.where_field_confidence,
            args.where_task_confidence,
            args.where_submode,
            args.where_subdomain,
        )
    )


def _find_node_index(nodes, node_id: str) -> Optional[int]:
    for idx, node in enumerate(nodes):
        if node.id == node_id:
            return idx
    return None


def _energy_def_payload(energy: EnergyConfig) -> Dict[str, object]:
    return {
        "formula": "alpha*E_energy + beta*E_srsp + gamma*E_risk",
        "alpha": energy.alpha,
        "beta": energy.beta,
        "gamma": energy.gamma,
        "normalize": energy.normalize,
    }


def _latest_e_def(audit_log) -> Optional[Dict[str, object]]:
    for record in reversed(audit_log.updates):
        if record.change_type == "E_DEF_UPDATE":
            return record.after if isinstance(record.after, dict) else None
    return None


def _build_e_def_update(e_def: Dict[str, object]) -> UpdateRecord:
    timestamp = utc_now()
    update_id = f"update_e_def_{stable_hash(timestamp)}"
    return UpdateRecord(
        id=update_id,
        target="system",
        change_type="E_DEF_UPDATE",
        before=None,
        after=e_def,
        rationale="Energy definition updated during manual change.",
        gate=UpdateGate(passed=True, rule_ids=["R1", "R3"]),
        timestamp=timestamp,
        reversible=True,
        vetoable=True,
    )


def _default_diff_path(audit_path: str, diff_id: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(audit_path))
    return os.path.join(base_dir, f"semantic_diff_{diff_id}.json")


def _workspace_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _apply_patch_history(nodes, diff_id: str, changes) -> None:
    if not diff_id or not changes:
        return
    node_map = {node.id: node for node in nodes}
    for change in changes:
        change_type = getattr(change, "type", None)
        if change_type not in {"NODE_UPDATE", "NODE_ADD"}:
            continue
        target = node_map.get(change.target_id)
        if not target:
            continue
        history = list(getattr(target, "patch_history", []) or [])
        if diff_id not in history:
            history.append(diff_id)
            target.patch_history = history


def _trace_requested(args: argparse.Namespace) -> bool:
    return bool(args.trace_input or args.trace_text)


def _write_trace_artifacts(
    args: argparse.Namespace,
) -> Dict[str, Optional[str]]:
    raw_text = load_text(args.trace_input, args.trace_text)
    if not raw_text:
        raise SystemExit("Trace requested but no content found.")
    capture_payload = capture_record(
        raw_text=raw_text,
        source_type=args.trace_source_type,
        uri=args.trace_uri,
        title=args.trace_title,
        grade=args.trace_grade,
        retrieved_at=args.trace_retrieved_at,
        verified_by=args.trace_verified_by,
        notes=args.trace_notes,
        tags=args.trace_tag,
    )
    source = capture_payload.get("source", {}) if isinstance(capture_payload, dict) else {}

    def _load_trace_json(value: Optional[str], label: str) -> Optional[object]:
        if value is None:
            return None
        try:
            if os.path.exists(value):
                with open(value, "r", encoding="utf-8-sig") as handle:
                    payload = json.load(handle)
            else:
                payload = json.loads(value)
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"{label} must be JSON or a JSON file path: {exc}") from exc
        return payload

    claims = _load_trace_json(args.trace_claims, "--trace-claims")
    links = _load_trace_json(args.trace_links, "--trace-links")
    attributions = _load_trace_json(args.trace_attributions, "--trace-attributions")
    try:
        normalize_payload = normalize_record(
            raw_text=raw_text,
            capture_id=(
                capture_payload.get("capture_id") if isinstance(capture_payload, dict) else None
            ),
            source=source if isinstance(source, dict) else {},
            source_grade=args.trace_grade,
            summary=args.trace_summary,
            notes=args.trace_notes,
            tags=args.trace_tag,
            max_length=args.trace_max_length,
            claims=claims,
            links=links,
            attributions=attributions,
            auto_claims=args.trace_auto_claims,
            auto_claim_limit=args.trace_claim_limit,
            auto_claim_min_chars=args.trace_claim_min_chars,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    output_dir = args.trace_output_dir or os.path.join(_workspace_root(), "generated", "tech_trace")
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    capture_id = capture_payload.get("capture_id") if isinstance(capture_payload, dict) else None
    normalize_id = (
        normalize_payload.get("normalize_id") if isinstance(normalize_payload, dict) else None
    )
    capture_path = os.path.join(output_dir, f"{capture_id}.json") if capture_id else None
    normalize_path = os.path.join(output_dir, f"{normalize_id}.json") if normalize_id else None
    if capture_path:
        with open(capture_path, "w", encoding="utf-8") as handle:
            json.dump(capture_payload, handle, indent=2)
    if normalize_path:
        with open(normalize_path, "w", encoding="utf-8") as handle:
            json.dump(normalize_payload, handle, indent=2)
    return {
        "capture_path": capture_path,
        "normalize_path": normalize_path,
        "normalize_id": normalize_id,
        "source_grade": (
            normalize_payload.get("source_grade") if isinstance(normalize_payload, dict) else None
        ),
    }


def main() -> Dict[str, str]:
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.what and _where_update_requested(args):
        parser.error("Choose either --what or --where-* in a single run.")
    if not args.what and not _where_update_requested(args):
        parser.error("No update specified. Provide --what or --where-* arguments.")

    nodes, metadata = load_nodes_payload(args.nodes)
    before_nodes = {node.id: copy.deepcopy(node) for node in nodes}
    audit_log = load_audit_log(args.audit)
    error_ledger_path = args.error_ledger
    if error_ledger_path is None:
        error_ledger_path = os.path.join(
            os.path.dirname(os.path.abspath(args.audit)), "error_ledger.jsonl"
        )
    node_index = _find_node_index(nodes, args.node_id)
    if node_index is None:
        raise SystemExit(f"Node not found: {args.node_id}")

    energy = EnergyConfig(
        alpha=args.alpha,
        beta=args.beta,
        gamma=args.gamma,
        normalize=not args.no_normalize_energy,
    )
    e_def = _energy_def_payload(energy)
    last_e_def = _latest_e_def(audit_log)
    if last_e_def != e_def:
        audit_log.updates.append(_build_e_def_update(e_def))

    if args.what:
        dims = args.embedding_dims or len(nodes[node_index].what.v_sem)
        config = EmbeddingConfig(dims=dims)
        updated_node, record = update_what(
            nodes[node_index],
            args.what,
            config=config,
            energy=energy,
            rationale=args.rationale,
        )
        nodes[node_index] = updated_node
        nodes = apply_energy_totals(nodes, energy)
        record.after = as_clean_dict(nodes[node_index])
        audit_log.updates.append(record)
    else:
        current = nodes[node_index]
        new_time = WhereTime(
            turn_id=args.turn_id if args.turn_id is not None else current.where.where_time.turn_id,
            event_index=(
                args.event_index
                if args.event_index is not None
                else current.where.where_time.event_index
            ),
            timestamp=current.where.where_time.timestamp,
            version_id=current.where.where_time.version_id,
        )
        new_field = WhereField(
            mode=args.where_mode if args.where_mode is not None else current.where.where_field.mode,
            submode=(
                args.where_submode
                if args.where_submode is not None
                else current.where.where_field.submode
            ),
            confidence=(
                args.where_field_confidence
                if args.where_field_confidence is not None
                else current.where.where_field.confidence
            ),
        )
        new_task = WhereTask(
            domain=(
                args.where_domain
                if args.where_domain is not None
                else current.where.where_task.domain
            ),
            subdomain=(
                args.where_subdomain
                if args.where_subdomain is not None
                else current.where.where_task.subdomain
            ),
            confidence=(
                args.where_task_confidence
                if args.where_task_confidence is not None
                else current.where.where_task.confidence
            ),
        )
        new_where = Where(where_time=new_time, where_field=new_field, where_task=new_task)
        updated_node, record = update_where(
            current,
            new_where,
            rationale=args.rationale,
            reviewer=args.reviewer,
            error_ledger_path=error_ledger_path,
        )
        nodes[node_index] = updated_node
        audit_log.updates.append(record)

    nodes_path = args.output_nodes or args.nodes
    audit_path = args.output_audit or args.audit
    if os.path.dirname(nodes_path):
        os.makedirs(os.path.dirname(nodes_path), exist_ok=True)
    if os.path.dirname(audit_path):
        os.makedirs(os.path.dirname(audit_path), exist_ok=True)
    trace_capture_path = None
    trace_normalize_path = None
    trace_normalize_id = None
    trace_source_grade = None
    if _trace_requested(args):
        trace_result = _write_trace_artifacts(args)
        trace_capture_path = trace_result.get("capture_path")
        trace_normalize_path = trace_result.get("normalize_path")
        trace_normalize_id = trace_result.get("normalize_id")
        trace_source_grade = trace_result.get("source_grade")
    diff_path = None
    should_write_diff = bool(args.write_diff or args.diff_output or _trace_requested(args))
    if should_write_diff:
        after_nodes = {node.id: node for node in nodes}
        diff_source_patch_id = args.source_patch_id or trace_normalize_id
        diff_source_grade = args.source_grade or trace_source_grade or "C"
        diff = compute_batch_diff(
            before_nodes,
            after_nodes,
            rationale=args.rationale,
            source_grade=diff_source_grade,
            source_patch_id=diff_source_patch_id,
            trace_level=args.trace_level,
        )
        diff_payload = as_clean_dict(diff)
        diff_path = args.diff_output or _default_diff_path(audit_path, diff.id)
        os.makedirs(os.path.dirname(diff_path), exist_ok=True)
        with open(diff_path, "w", encoding="utf-8") as handle:
            json.dump(diff_payload, handle, indent=2)
        _apply_patch_history(nodes, diff.id, diff.changes)
    save_nodes_payload(nodes_path, nodes, metadata)
    save_audit_log(audit_path, audit_log)
    return {
        "nodes": nodes_path,
        "audit": audit_path,
        "diff": diff_path,
        "trace_capture": trace_capture_path,
        "trace_normalized": trace_normalize_path,
    }


if __name__ == "__main__":
    paths = main()
    print(f"nodes.json: {paths['nodes']}")
    print(f"audit_log.json: {paths['audit']}")
    if paths.get("diff"):
        print(f"semantic_diff.json: {paths['diff']}")
    if paths.get("trace_capture"):
        print(f"trace_capture.json: {paths['trace_capture']}")
    if paths.get("trace_normalized"):
        print(f"trace_normalized.json: {paths['trace_normalized']}")
