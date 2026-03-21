"""Apply one reviewed decision to every unresolved tension in a semantic group."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import scripts.run_reviewed_promotion as reviewed_runner  # noqa: E402
from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB  # noqa: E402
from tonesoul.memory.subjectivity_reporting import (  # noqa: E402
    summarize_subjectivity_distribution,
)
from tonesoul.memory.subjectivity_review_batch import (  # noqa: E402
    build_subjectivity_review_batch_report,
)
from tonesoul.memory.subjectivity_triage import (  # noqa: E402
    build_subjectivity_tension_group_report,
    build_subjectivity_tension_rows,
)
from tonesoul.schemas import SubjectivityPromotionStatus  # noqa: E402

_ALLOWED_BATCH_REVIEW_STATUSES = {
    SubjectivityPromotionStatus.DEFERRED.value,
    SubjectivityPromotionStatus.REJECTED.value,
}
_ALLOWED_PENDING_STATUSES = {
    "candidate",
    "deferred",
}


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def _resolve_source(value: str | None) -> MemorySource | None:
    if value is None:
        return None
    normalized = str(value or "").strip().lower()
    if not normalized:
        return None
    return MemorySource(normalized)


def _select_groups(
    groups: list[dict[str, Any]],
    *,
    group_key: str | None,
    topic: str | None,
    direction: str | None,
    friction_band: str | None,
) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for group in groups:
        if group_key and str(group.get("group_key") or "") != group_key:
            continue
        if topic and str(group.get("topic") or "") != topic:
            continue
        if direction and str(group.get("direction") or "") != direction:
            continue
        if friction_band and str(group.get("friction_band") or "") != friction_band:
            continue
        matches.append(group)
    return matches


def build_receipt(
    db_path: Path,
    *,
    group_key: str | None = None,
    topic: str | None = None,
    direction: str | None = None,
    friction_band: str | None = None,
    source_name: str | None = None,
    review_actor: str,
    actor_type: str = "operator",
    display_name: str | None = None,
    status: str | None = None,
    review_basis: str | None = None,
    notes: str | None = None,
    promotion_source: str = "group_review",
    pending_status: str | None = None,
    reuse_latest_decision: bool = False,
    apply: bool = False,
) -> dict[str, Any]:
    warnings: list[str] = []
    issues: list[str] = []
    db_exists = db_path.exists()
    source = _resolve_source(source_name)

    if not db_exists:
        warnings.append(f"soul db path did not exist before group review run: {db_path.as_posix()}")
    pending_status_filter = str(pending_status or "").strip().lower() or None
    if pending_status_filter is not None and pending_status_filter not in _ALLOWED_PENDING_STATUSES:
        issues.append(
            f"pending_status must be one of {sorted(_ALLOWED_PENDING_STATUSES)} when provided"
        )
    if reuse_latest_decision and any(value is not None for value in (status, review_basis, notes)):
        issues.append(
            "reuse_latest_decision cannot be combined with explicit status/review_basis/notes"
        )

    soul_db = SqliteSoulDB(db_path=db_path)
    report = build_subjectivity_tension_group_report(soul_db, source=source)
    matches = _select_groups(
        list(report.get("semantic_groups") or []),
        group_key=group_key,
        topic=topic,
        direction=direction,
        friction_band=friction_band,
    )
    if not matches:
        issues.append("no semantic group matched the requested selector")
    elif len(matches) > 1:
        issues.append(f"group selector matched {len(matches)} semantic groups; refine the selector")

    group = matches[0] if len(matches) == 1 else None
    batch_group: dict[str, Any] | None = None
    if group is not None and reuse_latest_decision:
        batch_report = build_subjectivity_review_batch_report(soul_db, source=source)
        batch_matches = _select_groups(
            list(batch_report.get("review_groups") or []),
            group_key=group_key,
            topic=topic,
            direction=direction,
            friction_band=friction_band,
        )
        if not batch_matches:
            issues.append(
                "reuse_latest_decision requested but no review-batch group matched the selector"
            )
        elif len(batch_matches) > 1:
            issues.append(
                f"reuse_latest_decision matched {len(batch_matches)} review-batch groups; refine the selector"
            )
        else:
            batch_group = batch_matches[0]
    resolved_status = str(status or SubjectivityPromotionStatus.REJECTED.value).strip()
    resolved_review_basis = str(review_basis or "").strip()
    resolved_notes = notes
    decision_source = "explicit_args"
    if batch_group is not None and reuse_latest_decision:
        resolved_status = str(batch_group.get("latest_review_status") or "").strip()
        resolved_review_basis = str(batch_group.get("latest_review_basis") or "").strip()
        resolved_notes = str(batch_group.get("latest_review_notes") or "").strip() or None
        decision_source = "latest_matched_review"
        if not resolved_status:
            issues.append(
                "reuse_latest_decision requested but the matched group had no latest review status"
            )
        if not resolved_review_basis:
            issues.append(
                "reuse_latest_decision requested but the matched group had no latest review basis"
            )
    batch_status_allowed = resolved_status in _ALLOWED_BATCH_REVIEW_STATUSES
    if not batch_status_allowed:
        issues.append(
            "group review only supports deferred/rejected settlement; use single-record review for vow promotion"
        )
    if not reuse_latest_decision and not resolved_review_basis:
        issues.append("review_basis is required unless reuse_latest_decision is enabled")

    record_ids = list(group.get("record_ids") or []) if isinstance(group, dict) else []
    selected_record_ids = list(record_ids)
    selected_pending_status_counts: dict[str, int] = {}
    if group is not None and pending_status_filter is not None:
        unresolved_rows = build_subjectivity_tension_rows(
            soul_db,
            source=source,
            unresolved_only=True,
        )
        row_by_record_id = {
            str(row.get("record_id") or ""): row
            for row in unresolved_rows
            if str(row.get("record_id") or "")
        }
        filtered_rows = [
            row_by_record_id[record_id]
            for record_id in record_ids
            if record_id in row_by_record_id
            and str(row_by_record_id[record_id].get("pending_status") or "").strip().lower()
            == pending_status_filter
        ]
        selected_record_ids = [str(row.get("record_id") or "") for row in filtered_rows]
        selected_pending_status_counts = (
            {pending_status_filter: len(selected_record_ids)} if selected_record_ids else {}
        )
    receipts: list[dict[str, Any]] = []

    if group is not None and not record_ids:
        warnings.append("selected semantic group contained no record ids")
    if group is not None and pending_status_filter is not None and not selected_record_ids:
        warnings.append(
            f"selected semantic group contained no rows with pending_status={pending_status_filter}"
        )

    if apply and group is not None and batch_status_allowed:
        for record_id in selected_record_ids:
            receipt = reviewed_runner.build_receipt(
                db_path,
                record_id=record_id,
                source_name=source.value if source is not None else None,
                review_actor=review_actor,
                actor_type=actor_type,
                display_name=display_name,
                status=resolved_status,
                review_basis=resolved_review_basis,
                notes=resolved_notes,
                promotion_source=promotion_source,
            )
            receipts.append(
                {
                    "record_id": record_id,
                    "overall_ok": bool(receipt.get("overall_ok")),
                    "review_log_id": (receipt.get("result") or {}).get("review_log_id"),
                    "promoted_record_id": (receipt.get("result") or {}).get("promoted_record_id"),
                    "settled": bool((receipt.get("result") or {}).get("settled")),
                    "post_review_unresolved": bool(
                        (receipt.get("result") or {}).get("post_review_unresolved")
                    ),
                    "issues": list(receipt.get("issues") or []),
                    "warnings": list(receipt.get("warnings") or []),
                }
            )
        for receipt in receipts:
            if receipt["issues"]:
                issues.extend(str(item) for item in receipt["issues"])
    elif group is not None:
        receipts = [
            {
                "record_id": record_id,
                "planned_status": resolved_status,
            }
            for record_id in selected_record_ids
        ]

    post_summary = summarize_subjectivity_distribution(SqliteSoulDB(db_path=db_path), source=source)
    successful_receipts = sum(1 for item in receipts if bool(item.get("overall_ok", not apply)))
    applied_count = sum(1 for item in receipts if item.get("review_log_id"))
    promoted_count = sum(1 for item in receipts if item.get("promoted_record_id"))
    settled_count = sum(1 for item in receipts if bool(item.get("settled")))
    overall_ok = (
        not issues and group is not None and (not apply or successful_receipts == len(receipts))
    )

    return {
        "generated_at": _iso_now(),
        "overall_ok": overall_ok,
        "source": "scripts/run_subjectivity_group_review.py",
        "inputs": {
            "db_path": db_path.as_posix(),
            "source": source.value if source is not None else "all",
            "group_key": group_key,
            "topic": topic,
            "direction": direction,
            "friction_band": friction_band,
            "review_actor": review_actor,
            "actor_type": actor_type,
            "display_name": display_name,
            "status": status,
            "review_basis": review_basis,
            "notes": notes,
            "promotion_source": promotion_source,
            "pending_status": pending_status_filter,
            "reuse_latest_decision": reuse_latest_decision,
            "apply": apply,
        },
        "resolved_decision": {
            "status": resolved_status,
            "review_basis": resolved_review_basis,
            "notes": resolved_notes,
            "decision_source": decision_source,
        },
        "selection": (
            {
                "group_key": group.get("group_key"),
                "topic": group.get("topic"),
                "direction": group.get("direction"),
                "friction_band": group.get("friction_band"),
                "record_count": group.get("record_count"),
                "lineage_count": group.get("lineage_count"),
                "cycle_count": group.get("cycle_count"),
                "source_url_count": group.get("source_url_count"),
                "triage_recommendation": group.get("triage_recommendation"),
                "record_ids": selected_record_ids,
                "group_record_count": len(record_ids),
                "selected_record_count": len(selected_record_ids),
                "pending_status_filter": pending_status_filter,
                "selected_pending_status_counts": selected_pending_status_counts,
            }
            if group is not None
            else None
        ),
        "results": {
            "successful_receipt_count": successful_receipts,
            "applied_count": applied_count,
            "promoted_count": promoted_count,
            "settled_count": settled_count,
            "receipt_count": len(receipts),
        },
        "receipts": receipts,
        "metrics": {
            "unresolved_tension_count": int(post_summary.get("unresolved_tension_count") or 0),
            "settled_tension_count": int(post_summary.get("settled_tension_count") or 0),
            "reviewed_vow_count": int(post_summary.get("reviewed_vow_count") or 0),
        },
        "issues": issues,
        "warnings": warnings,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Apply one reviewed decision to every unresolved tension in a semantic group."
    )
    parser.add_argument("--db-path", default="memory/soul.db", help="Path to soul.db.")
    parser.add_argument(
        "--source",
        choices=[source.value for source in MemorySource],
        default=None,
        help="Optional source filter.",
    )
    parser.add_argument("--group-key", default=None, help="Exact semantic group key to review.")
    parser.add_argument("--topic", default=None, help="Topic selector when group_key is unknown.")
    parser.add_argument("--direction", default=None, help="Direction selector.")
    parser.add_argument(
        "--friction-band",
        choices=["low", "medium", "high"],
        default=None,
        help="Friction band selector.",
    )
    parser.add_argument("--review-actor", required=True, help="Reviewer actor id.")
    parser.add_argument("--actor-type", default="operator", help="Reviewer actor type.")
    parser.add_argument("--display-name", default=None, help="Optional reviewer display name.")
    parser.add_argument(
        "--status",
        choices=sorted(_ALLOWED_BATCH_REVIEW_STATUSES),
        default=None,
        help="Batch settlement status to apply to every record in the selected group.",
    )
    parser.add_argument(
        "--review-basis", default=None, help="Why this group review decision was made."
    )
    parser.add_argument("--notes", default=None, help="Optional review notes.")
    parser.add_argument(
        "--reuse-latest-decision",
        action="store_true",
        help="Reuse the matched group's latest review status/basis/notes instead of passing them explicitly.",
    )
    parser.add_argument(
        "--promotion-source",
        default="group_review",
        help="Promotion source label stored on each review decision.",
    )
    parser.add_argument(
        "--pending-status",
        choices=sorted(_ALLOWED_PENDING_STATUSES),
        default=None,
        help="Optional unresolved pending status filter inside the selected semantic group.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually write review decisions. Without this flag the command is dry-run only.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_receipt(
        Path(args.db_path).resolve(),
        group_key=args.group_key,
        topic=args.topic,
        direction=args.direction,
        friction_band=args.friction_band,
        source_name=args.source,
        review_actor=args.review_actor,
        actor_type=args.actor_type,
        display_name=args.display_name,
        status=args.status,
        review_basis=args.review_basis,
        notes=args.notes,
        promotion_source=args.promotion_source,
        pending_status=args.pending_status,
        reuse_latest_decision=args.reuse_latest_decision,
        apply=args.apply,
    )
    _emit(payload)
    if not payload["overall_ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
