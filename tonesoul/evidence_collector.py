import argparse
import json
import os
from typing import Dict, List, Optional, Sequence, Tuple

from .ystm.schema import utc_now


def _load_json(path: str) -> Optional[Dict[str, object]]:
    try:
        with open(path, "r", encoding="utf-8-sig") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _truncate(text: str, limit: int = 120) -> str:
    cleaned = " ".join(str(text).split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: max(0, limit - 3)] + "..."


def _claim_preview(claims: object) -> Tuple[int, List[str]]:
    if not isinstance(claims, list):
        return 0, []
    count = 0
    preview: List[str] = []
    for item in claims:
        text = None
        if isinstance(item, dict):
            text = item.get("text") or item.get("claim") or item.get("statement")
        elif isinstance(item, str):
            text = item
        if text:
            count += 1
            if len(preview) < 2:
                preview.append(_truncate(text, 80))
    return count, preview


def _count_entries(items: object, key: Optional[str] = None) -> int:
    if not isinstance(items, list):
        return 0
    count = 0
    for item in items:
        if isinstance(item, dict):
            if key is None or item.get(key):
                count += 1
        elif isinstance(item, str):
            if item.strip():
                count += 1
    return count


def _tech_trace_digest(normalize_path: Optional[str]) -> List[str]:
    if not normalize_path:
        return []
    payload = _load_json(normalize_path)
    if not payload:
        return []
    lines: List[str] = []
    summary = payload.get("summary")
    if summary:
        lines.append(f"- tech_trace_summary: {_truncate(summary)}")
    claims_count, claims_preview = _claim_preview(payload.get("claims"))
    if claims_count:
        preview_text = " | ".join(claims_preview) if claims_preview else "n/a"
        lines.append(f"- tech_trace_claims: {claims_count} | {preview_text}")
    link_count = _count_entries(payload.get("links"), key="uri")
    if link_count:
        lines.append(f"- tech_trace_links: {link_count}")
    attribution_count = _count_entries(payload.get("attributions"), key="source_ref")
    if attribution_count:
        lines.append(f"- tech_trace_attributions: {attribution_count}")
    return lines


def _intent_verification_digest(intent_path: Optional[str]) -> List[str]:
    if not intent_path:
        return []
    payload = _load_json(intent_path)
    if not payload:
        return []
    audit = payload.get("audit") if isinstance(payload.get("audit"), dict) else {}
    status = audit.get("status") or payload.get("status")
    confidence = audit.get("confidence")
    reason = audit.get("reason")
    lines: List[str] = []
    if status:
        lines.append(f"- intent_status: {status}")
    if isinstance(confidence, (int, float)):
        lines.append(f"- intent_confidence: {confidence:.2f}")
    if reason:
        lines.append(f"- intent_reason: {_truncate(reason)}")
    return lines


def build_evidence_summary(
    context_path: str,
    execution_report_path: Optional[str],
    artifacts: Optional[Dict[str, Optional[str]]] = None,
) -> str:
    lines = []
    lines.append(f"- Run: {context_path}")
    if execution_report_path:
        lines.append(f"- Execution report: {execution_report_path}")
    if artifacts:
        for label in sorted(artifacts.keys()):
            path = artifacts.get(label)
            if path:
                lines.append(f"- {label}: {path}")
        lines.extend(_tech_trace_digest(artifacts.get("tech_trace_normalize")))
        lines.extend(_intent_verification_digest(artifacts.get("intent_verification")))
    lines.append(f"- Collected at: {utc_now()}")
    return "\n".join(lines)


def _entry_offsets(lines: Sequence[str]) -> List[int]:
    return [idx for idx, line in enumerate(lines) if line.startswith("- Run:")]


def _safe_stamp() -> str:
    return utc_now().replace("-", "").replace(":", "")


def _rollover_summary(
    path: str,
    max_entries: int,
    keep_latest: Optional[int],
    archive_dir: Optional[str],
) -> Optional[str]:
    if max_entries <= 0:
        return None
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as handle:
        lines = handle.readlines()
    starts = _entry_offsets(lines)
    if len(starts) <= max_entries:
        return None
    keep_latest = keep_latest or max_entries
    if keep_latest < 1:
        keep_latest = 1
    keep_latest = min(keep_latest, len(starts), max_entries)
    header_end = starts[0] if starts else 0
    keep_start = starts[-keep_latest]
    archive_lines = lines[header_end:keep_start]
    if not archive_lines:
        return None
    archive_dir = archive_dir or os.path.join(os.path.dirname(path), "archive")
    os.makedirs(archive_dir, exist_ok=True)
    archive_path = os.path.join(archive_dir, f"evidence_summary_{_safe_stamp()}.md")
    with open(archive_path, "w", encoding="utf-8") as handle:
        handle.write("# Evidence Summary Archive\n\n")
        handle.write(f"- Source: {path}\n")
        handle.write(f"- Archived at: {utc_now()}\n\n")
        handle.writelines(archive_lines)
    with open(path, "w", encoding="utf-8") as handle:
        handle.writelines(lines[:header_end])
        handle.writelines(lines[keep_start:])
    return archive_path


def append_to_summary(path: str, entry: str, retention: Optional[Dict[str, object]] = None) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("# Evidence Summary\n\n")
    with open(path, "a", encoding="utf-8") as handle:
        handle.write("\n")
        handle.write(entry)
        handle.write("\n")
    if retention and retention.get("max_entries") is not None:
        max_entries = int(retention.get("max_entries") or 0)
        keep_latest = retention.get("keep_latest")
        keep_latest = int(keep_latest) if keep_latest is not None else None
        archive_dir = retention.get("archive_dir")
        _rollover_summary(path, max_entries, keep_latest, archive_dir)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect evidence summary for YSS M4.")
    parser.add_argument("--context", required=True, help="Path to context.yaml.")
    parser.add_argument("--execution-report", help="Optional path to execution_report.md.")
    parser.add_argument("--error-ledger", help="Optional path to error_ledger.jsonl.")
    parser.add_argument("--ystm-nodes", help="Optional path to nodes.json.")
    parser.add_argument("--ystm-audit", help="Optional path to audit_log.json.")
    parser.add_argument("--ystm-diff", help="Optional path to semantic_diff.json.")
    parser.add_argument("--ystm-terrain", help="Optional path to terrain.html.")
    parser.add_argument("--ystm-terrain-json", help="Optional path to terrain.json.")
    parser.add_argument("--ystm-terrain-svg", help="Optional path to terrain.svg.")
    parser.add_argument("--ystm-terrain-png", help="Optional path to terrain.png.")
    parser.add_argument("--ystm-terrain-p2", help="Optional path to terrain_p2.html.")
    parser.add_argument("--ystm-terrain-p2-json", help="Optional path to terrain_p2.json.")
    parser.add_argument("--ystm-terrain-p2-svg", help="Optional path to terrain_p2.svg.")
    parser.add_argument("--ystm-terrain-p2-png", help="Optional path to terrain_p2.png.")
    parser.add_argument("--tech-trace-capture", help="Optional path to tech_trace capture JSON.")
    parser.add_argument(
        "--tech-trace-normalize", help="Optional path to tech_trace normalized JSON."
    )
    parser.add_argument("--intent-verification", help="Optional path to intent_verification.json.")
    parser.add_argument("--skills-applied", help="Optional path to skills_applied.json.")
    parser.add_argument("--reflection", help="Optional path to reflection.json.")
    parser.add_argument("--action-set", help="Optional path to action_set.json.")
    parser.add_argument("--mercy-objective", help="Optional path to mercy_objective.json.")
    parser.add_argument("--council-summary", help="Optional path to council_summary.json.")
    parser.add_argument("--tsr-metrics", help="Optional path to tsr_metrics.json.")
    parser.add_argument("--dcs-result", help="Optional path to dcs_result.json.")
    parser.add_argument("--max-entries", type=int, help="Max entries to keep in summary.")
    parser.add_argument("--keep-latest", type=int, help="Entries to keep when rolling summary.")
    parser.add_argument("--archive-dir", help="Archive directory for older summary entries.")
    parser.add_argument(
        "--output",
        default=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "evidence", "summary.md")
        ),
        help="Evidence summary path.",
    )
    return parser


def main() -> Dict[str, str]:
    parser = build_arg_parser()
    args = parser.parse_args()
    artifacts = {
        "action_set": args.action_set,
        "mercy_objective": args.mercy_objective,
        "council_summary": args.council_summary,
        "error_ledger": args.error_ledger,
        "reflection": args.reflection,
        "skills_applied": args.skills_applied,
        "tsr_metrics": args.tsr_metrics,
        "dcs_result": args.dcs_result,
        "ystm_audit": args.ystm_audit,
        "ystm_diff": args.ystm_diff,
        "ystm_nodes": args.ystm_nodes,
        "ystm_terrain": args.ystm_terrain,
        "ystm_terrain_json": args.ystm_terrain_json,
        "ystm_terrain_svg": args.ystm_terrain_svg,
        "ystm_terrain_png": args.ystm_terrain_png,
        "ystm_terrain_p2": args.ystm_terrain_p2,
        "ystm_terrain_p2_json": args.ystm_terrain_p2_json,
        "ystm_terrain_p2_svg": args.ystm_terrain_p2_svg,
        "ystm_terrain_p2_png": args.ystm_terrain_p2_png,
        "tech_trace_capture": args.tech_trace_capture,
        "tech_trace_normalize": args.tech_trace_normalize,
        "intent_verification": args.intent_verification,
    }
    entry = build_evidence_summary(args.context, args.execution_report, artifacts=artifacts)
    retention = None
    if args.max_entries is not None:
        retention = {
            "max_entries": args.max_entries,
            "keep_latest": args.keep_latest,
            "archive_dir": args.archive_dir,
        }
    append_to_summary(args.output, entry, retention=retention)
    return {"evidence_summary": os.path.abspath(args.output)}


if __name__ == "__main__":
    paths = main()
    print(f"evidence_summary.md: {paths['evidence_summary']}")
