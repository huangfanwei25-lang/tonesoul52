from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

from .reviewed_promotion import (
    build_reviewed_promotion_decision,
    build_reviewed_promotion_payload,
    infer_subjectivity_layer,
    replay_reviewed_promotion,
)
from .soul_db import JsonlSoulDB, MemorySource, SoulDB
from .stats import average_coherence, count_by_verdict, most_common_divergence
from .subjectivity_reporting import summarize_subjectivity_distribution
from .write_gateway import MemoryWriteGateway, MemoryWriteRejectedError


@dataclass
class ConsolidationResult:
    patterns: Dict[str, object]
    meta_reflection: str


@dataclass
class SleepResult:
    """Result of AI Sleep memory consolidation."""

    promoted_count: int
    cleared_count: int
    patterns: Dict[str, object]
    meta_reflection: str
    layer_summary: Dict[str, int]
    subjectivity_summary: Dict[str, object] = field(default_factory=dict)
    gated_count: int = 0
    gate_failures: Dict[str, int] = field(default_factory=dict)


def _classify_for_promotion(payload: Dict[str, object]) -> str:
    """Classify working memory into factual/experiential/working."""
    text = str(payload.get("text", "") or payload.get("content", "")).lower()
    factual_keywords = ["commit", "promise", "agree", "承諾", "保證", "答應", "name", "prefer"]
    experiential_keywords = ["feel", "emotion", "conflict", "tension", "感覺", "衝突", "張力"]

    for keyword in factual_keywords:
        if keyword in text:
            return "factual"
    for keyword in experiential_keywords:
        if keyword in text:
            return "experiential"
    return "working"


def build_reviewed_vow_payload(
    payload: Dict[str, object],
    *,
    reviewed_by: str,
    review_basis: str,
    reviewed_at: Optional[str] = None,
    source_record_ids: Optional[Sequence[str]] = None,
    promotion_source: str = "manual_review",
) -> Dict[str, object]:
    decision = build_reviewed_promotion_decision(
        payload,
        review_actor={
            "actor_id": reviewed_by,
            "actor_type": "operator",
        },
        review_basis=review_basis,
        reviewed_at=reviewed_at,
        source_record_ids=source_record_ids,
        promotion_source=promotion_source,
        status="reviewed",
    )
    return build_reviewed_promotion_payload(payload, decision=decision)


def promote_reviewed_tension_to_vow(
    soul_db: SoulDB,
    *,
    source: MemorySource,
    payload: Dict[str, object],
    reviewed_by: str,
    review_basis: str,
    reviewed_at: Optional[str] = None,
    source_record_ids: Optional[Sequence[str]] = None,
    promotion_source: str = "manual_review",
) -> str:
    decision = build_reviewed_promotion_decision(
        payload,
        review_actor={
            "actor_id": reviewed_by,
            "actor_type": "operator",
        },
        review_basis=review_basis,
        reviewed_at=reviewed_at,
        source_record_ids=source_record_ids,
        promotion_source=promotion_source,
        status="reviewed",
    )
    return replay_reviewed_promotion(
        soul_db,
        source=source,
        payload=payload,
        decision=decision,
    )


def _load_entries(
    path: Optional[Path] = None,
    soul_db: Optional[SoulDB] = None,
) -> List[dict]:
    db = soul_db
    if db is None:
        if path:
            db = JsonlSoulDB(source_map={MemorySource.SELF_JOURNAL: path})
        else:
            db = JsonlSoulDB()
    records = list(db.stream(MemorySource.SELF_JOURNAL))
    return [record.payload for record in records if isinstance(record.payload, dict)]


def identify_patterns(
    entries: Iterable[dict],
    *,
    layers: Optional[Sequence[str]] = None,
    exclude_promoted: bool = True,
) -> Dict[str, object]:
    allowed_layers = {str(layer).strip().lower() for layer in (layers or []) if str(layer).strip()}
    filtered = []
    for entry in entries:
        if entry.get("is_mine") is False:
            continue
        if exclude_promoted and entry.get("promoted_from") == "working":
            continue
        if allowed_layers:
            layer_name = str(entry.get("layer", "")).strip().lower()
            if layer_name not in allowed_layers:
                continue
        filtered.append(entry)

    verdict_counts = count_by_verdict(filtered)
    common_divergence = most_common_divergence(filtered)
    avg_coherence = average_coherence(filtered)
    total = sum(verdict_counts.values())
    declare_stance = verdict_counts.get("declare_stance", 0)
    block = verdict_counts.get("block", 0)
    genesis_counts: Dict[str, int] = {}
    actor_type_counts: Dict[str, int] = {}

    risk_weights = {"low": 1.0, "medium": 1.5, "high": 2.5, "critical": 4.0}
    total_weighted_tension = 0.0
    weighted_tension_count = 0

    for entry in filtered:
        genesis = entry.get("genesis")
        if not genesis:
            transcript = entry.get("transcript")
            if isinstance(transcript, dict):
                genesis = transcript.get("genesis")
        genesis = genesis or "unknown"
        genesis_counts[genesis] = genesis_counts.get(genesis, 0) + 1

        actor_type = str(entry.get("actor_type", "unknown")).strip().lower()
        actor_type_counts[actor_type] = actor_type_counts.get(actor_type, 0) + 1

        try:
            tension = float(entry.get("tension", 0.0))
        except (TypeError, ValueError):
            tension = 0.0

        risk_level = str(entry.get("risk_level", "low")).strip().lower()
        weight = risk_weights.get(risk_level, 1.0)
        total_weighted_tension += tension * weight
        weighted_tension_count += 1

    avg_weighted_tension = total_weighted_tension / max(1, weighted_tension_count)

    return {
        "total": total,
        "verdict_counts": verdict_counts,
        "declare_stance": declare_stance,
        "block": block,
        "most_common_divergence": common_divergence,
        "average_coherence": avg_coherence,
        "genesis_counts": genesis_counts,
        "actor_type_counts": actor_type_counts,
        "average_weighted_tension": avg_weighted_tension,
    }


def generate_meta_reflection(patterns: Dict[str, object]) -> str:
    patterns.get("verdict_counts", {}) or {}
    block_count = int(patterns.get("block", 0) or 0)
    stance_count = int(patterns.get("declare_stance", 0) or 0)
    common_divergence = patterns.get("most_common_divergence")

    lines = ["Based on my remembered decisions:"]

    if block_count:
        lines.append(f"- I have blocked {block_count} request(s) for safety reasons.")
    else:
        lines.append("- I have not blocked any requests for safety reasons.")

    if stance_count:
        lines.append(
            f"- I have declared stance {stance_count} time(s) due to perspective divergence."
        )
    else:
        lines.append("- I have not needed to declare stance due to divergence.")

    if common_divergence:
        lines.append(f"- The most common source of divergence is: {common_divergence}.")
    else:
        lines.append("- I have not observed a dominant source of divergence yet.")

    if stance_count:
        lines.append("I often face situations where my perspectives diverge.")

    return "\n".join(lines)


def consolidate(
    entries: Optional[Iterable[dict]] = None,
    path: Optional[Path] = None,
    soul_db: Optional[SoulDB] = None,
) -> ConsolidationResult:
    if entries is None:
        entries = _load_entries(path, soul_db=soul_db)
    patterns = identify_patterns(list(entries))
    meta_reflection = generate_meta_reflection(patterns)
    return ConsolidationResult(
        patterns=patterns,
        meta_reflection=meta_reflection,
    )


def sleep_consolidate(
    soul_db: SoulDB,
    *,
    source: MemorySource = MemorySource.SELF_JOURNAL,
) -> SleepResult:
    """Promote selected working memories into long-term layers."""
    try:
        working_records = list(soul_db.query(source, layer="working"))
    except TypeError:
        working_records = []

    promoted = 0
    cleared = 0
    gated = 0
    gate_failures: Dict[str, int] = {}
    gateway = MemoryWriteGateway(soul_db)

    for record in working_records:
        target_layer = _classify_for_promotion(record.payload)
        if target_layer == "working":
            cleared += 1
            continue

        promoted_payload = dict(record.payload)
        promoted_payload["layer"] = target_layer
        promoted_payload["promoted_from"] = "working"
        promoted_payload["promoted_at"] = datetime.now(timezone.utc).isoformat()
        promoted_payload["subjectivity_layer"] = infer_subjectivity_layer(
            promoted_payload,
            target_layer=target_layer,
        )
        if record.record_id:
            promoted_payload["source_record_ids"] = [str(record.record_id)]
        promoted_payload.setdefault(
            "promotion_gate",
            {
                "status": "candidate",
                "source": "sleep_consolidate",
            },
        )
        try:
            gateway.write_payload(source, promoted_payload)
        except MemoryWriteRejectedError as exc:
            gated += 1
            cleared += 1
            for reason in exc.reasons:
                gate_failures[reason] = gate_failures.get(reason, 0) + 1
            continue
        promoted += 1

    all_entries = [
        record.payload for record in soul_db.stream(source) if isinstance(record.payload, dict)
    ]
    patterns = identify_patterns(all_entries) if all_entries else {}
    meta_reflection = generate_meta_reflection(patterns) if patterns else ""

    layer_summary: Dict[str, int] = {"factual": 0, "experiential": 0, "working": 0}
    for record in soul_db.stream(source):
        layer = getattr(record, "layer", "experiential")
        if layer in layer_summary:
            layer_summary[layer] += 1
        else:
            layer_summary[layer] = 1
    subjectivity_summary = summarize_subjectivity_distribution(soul_db, source=source)

    return SleepResult(
        promoted_count=promoted,
        cleared_count=cleared,
        gated_count=gated,
        patterns=patterns,
        meta_reflection=meta_reflection,
        layer_summary=layer_summary,
        subjectivity_summary=subjectivity_summary,
        gate_failures=gate_failures,
    )
