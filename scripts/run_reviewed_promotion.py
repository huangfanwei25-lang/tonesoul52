"""Apply an explicit reviewed-promotion decision to one tension record."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tonesoul.memory.reviewed_promotion import (
    apply_reviewed_promotion,
    build_reviewed_promotion_decision,
)
from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB
from tonesoul.memory.subjectivity_reporting import (
    list_subjectivity_records,
    summarize_subjectivity_distribution,
)
from tonesoul.schemas import SubjectivityPromotionStatus

_REVIEWED_STATUSES = {"reviewed", "human_reviewed", "governance_reviewed", "approved"}


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


def _resolve_record(
    soul_db: SqliteSoulDB,
    *,
    record_id: str,
    source: MemorySource | None,
) -> dict[str, object] | None:
    detail_rows = soul_db.detail([record_id])
    if not detail_rows:
        return None
    row = detail_rows[0]
    current_source = str(row.get("source") or "").strip().lower()
    if source is not None and current_source != source.value:
        return None
    return row


def _reviewed_vow_count(soul_db: SqliteSoulDB, *, source: MemorySource) -> int:
    rows = list_subjectivity_records(
        soul_db,
        source=source,
        subjectivity_layer="vow",
        limit=None,
    )
    return sum(1 for row in rows if str(row.get("promotion_status") or "") in _REVIEWED_STATUSES)


def build_receipt(
    db_path: Path,
    *,
    record_id: str,
    source_name: str | None = None,
    review_actor: str,
    actor_type: str = "operator",
    display_name: str | None = None,
    status: str = SubjectivityPromotionStatus.APPROVED.value,
    review_basis: str,
    notes: str | None = None,
    promotion_source: str = "manual_review",
) -> dict[str, Any]:
    warnings: list[str] = []
    issues: list[str] = []
    db_exists = db_path.exists()
    source_filter = _resolve_source(source_name)
    soul_db = SqliteSoulDB(db_path=db_path)
    record_key = str(record_id or "").strip()

    if not db_exists:
        warnings.append(f"soul db path did not exist before review run: {db_path.as_posix()}")

    if not record_key:
        issues.append("record_id is required")
        return {
            "generated_at": _iso_now(),
            "overall_ok": False,
            "source": "scripts/run_reviewed_promotion.py",
            "inputs": {
                "db_path": db_path.as_posix(),
                "record_id": record_key,
                "source_filter": source_filter.value if source_filter is not None else "all",
                "review_actor": review_actor,
                "actor_type": actor_type,
                "display_name": display_name,
                "status": status,
                "review_basis": review_basis,
                "notes": notes,
                "promotion_source": promotion_source,
            },
            "record": None,
            "result": None,
            "metrics": {},
            "issues": issues,
            "warnings": warnings,
        }

    record = _resolve_record(soul_db, record_id=record_key, source=source_filter)
    if record is None:
        issues.append(f"subjectivity review target not found: {record_key}")
        return {
            "generated_at": _iso_now(),
            "overall_ok": False,
            "source": "scripts/run_reviewed_promotion.py",
            "inputs": {
                "db_path": db_path.as_posix(),
                "record_id": record_key,
                "source_filter": source_filter.value if source_filter is not None else "all",
                "review_actor": review_actor,
                "actor_type": actor_type,
                "display_name": display_name,
                "status": status,
                "review_basis": review_basis,
                "notes": notes,
                "promotion_source": promotion_source,
            },
            "record": None,
            "result": None,
            "metrics": {},
            "issues": issues,
            "warnings": warnings,
        }

    payload = record.get("payload")
    payload_dict = payload if isinstance(payload, dict) else {}
    record_source = MemorySource(str(record.get("source") or "").strip().lower())

    unresolved_before = {
        str(row.get("record_id") or "")
        for row in list_subjectivity_records(
            soul_db,
            source=record_source,
            unresolved_only=True,
            limit=None,
        )
    }
    if record_key not in unresolved_before:
        warnings.append(
            "target record was not pending in the unresolved tension queue before review"
        )

    result: dict[str, Any] | None = None
    try:
        decision = build_reviewed_promotion_decision(
            payload_dict,
            review_actor={
                "actor_id": review_actor,
                "actor_type": actor_type,
                "display_name": display_name,
            },
            review_basis=review_basis,
            reviewed_record_id=record_key,
            status=status,
            promotion_source=promotion_source,
            notes=notes,
        )
        result = apply_reviewed_promotion(
            soul_db,
            source=record_source,
            payload=payload_dict,
            decision=decision,
        )
    except Exception as exc:
        issues.append(str(exc))

    unresolved_after = {
        str(row.get("record_id") or "")
        for row in list_subjectivity_records(
            soul_db,
            source=record_source,
            unresolved_only=True,
            limit=None,
        )
    }
    summary = summarize_subjectivity_distribution(soul_db, source=record_source)

    overall_ok = not issues and result is not None and bool(result.get("review_log_id"))
    if (
        overall_ok
        and str(status or "").strip().lower() in _REVIEWED_STATUSES
        and not result.get("promoted_record_id")
    ):
        overall_ok = False
        issues.append("reviewed promotion did not produce a vow record")

    return {
        "generated_at": _iso_now(),
        "overall_ok": overall_ok,
        "source": "scripts/run_reviewed_promotion.py",
        "inputs": {
            "db_path": db_path.as_posix(),
            "record_id": record_key,
            "source_filter": source_filter.value if source_filter is not None else "all",
            "review_actor": review_actor,
            "actor_type": actor_type,
            "display_name": display_name,
            "status": status,
            "review_basis": review_basis,
            "notes": notes,
            "promotion_source": promotion_source,
        },
        "record": {
            "record_id": record_key,
            "source": record_source.value,
            "timestamp": record.get("timestamp"),
            "layer": record.get("layer"),
            "subjectivity_layer": payload_dict.get("subjectivity_layer"),
            "summary": str(
                payload_dict.get("summary")
                or payload_dict.get("title")
                or payload_dict.get("text")
                or payload_dict.get("content")
                or ""
            )[:160],
            "source_record_ids": list(payload_dict.get("source_record_ids") or []),
        },
        "result": (
            {
                **(result or {}),
                "pre_review_unresolved": record_key in unresolved_before,
                "post_review_unresolved": record_key in unresolved_after,
            }
            if result is not None
            else None
        ),
        "metrics": {
            "unresolved_tension_count": int(summary.get("unresolved_tension_count") or 0),
            "settled_tension_count": int(summary.get("settled_tension_count") or 0),
            "reviewed_vow_count": _reviewed_vow_count(soul_db, source=record_source),
        },
        "issues": issues,
        "warnings": warnings,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Apply an explicit reviewed-promotion decision to one tension record."
    )
    parser.add_argument("record_id", help="Concrete tension record id to review.")
    parser.add_argument("--db-path", default="memory/soul.db", help="Path to soul.db.")
    parser.add_argument(
        "--source",
        choices=[source.value for source in MemorySource],
        default=None,
        help="Optional source filter for the record lookup.",
    )
    parser.add_argument("--review-actor", required=True, help="Reviewer actor id.")
    parser.add_argument("--actor-type", default="operator", help="Reviewer actor type.")
    parser.add_argument("--display-name", default=None, help="Optional reviewer display name.")
    parser.add_argument(
        "--status",
        choices=[
            SubjectivityPromotionStatus.REVIEWED.value,
            SubjectivityPromotionStatus.HUMAN_REVIEWED.value,
            SubjectivityPromotionStatus.GOVERNANCE_REVIEWED.value,
            SubjectivityPromotionStatus.APPROVED.value,
            SubjectivityPromotionStatus.DEFERRED.value,
            SubjectivityPromotionStatus.REJECTED.value,
        ],
        default=SubjectivityPromotionStatus.APPROVED.value,
        help="Review decision status to record.",
    )
    parser.add_argument("--review-basis", required=True, help="Why this review decision was made.")
    parser.add_argument("--notes", default=None, help="Optional review notes.")
    parser.add_argument(
        "--promotion-source",
        default="manual_review",
        help="Promotion source label stored on the review decision.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = build_receipt(
        Path(args.db_path).resolve(),
        record_id=args.record_id,
        source_name=args.source,
        review_actor=args.review_actor,
        actor_type=args.actor_type,
        display_name=args.display_name,
        status=args.status,
        review_basis=args.review_basis,
        notes=args.notes,
        promotion_source=args.promotion_source,
    )
    _emit(payload)
    if not payload["overall_ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
