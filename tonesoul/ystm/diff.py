"""
YSTM Semantic Diff Module
語義差分模組

Computes semantic differences between node states for patch tracking.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional

from .schema import Node, as_clean_dict, stable_hash, utc_now

# Source grades for evidence tracking
SourceGrade = Literal["A", "B", "C"]
# Trace level for retention behavior
TraceLevel = Literal["standard", "full"]


@dataclass
class DiffEntry:
    """Single change entry in a semantic diff."""

    type: Literal["NODE_ADD", "NODE_UPDATE", "NODE_DELETE", "EDGE_ADD", "EDGE_DELETE"]
    target_id: str
    before: Optional[Dict[str, Any]]
    after: Optional[Dict[str, Any]]
    rationale: str
    source_grade: SourceGrade


@dataclass
class SemanticDiff:
    """Complete semantic diff between two states, tagged with trace level."""

    id: str
    created_at: str
    source_patch_id: Optional[str]
    changes: List[DiffEntry]
    trace_level: TraceLevel = "standard"


@dataclass
class Rollback:
    """Rollback request for a patch."""

    id: str
    target_patch_id: str
    requested_by: str
    rationale: str
    timestamp: str
    status: Literal["pending", "applied", "rejected"]


def compute_node_diff(
    before: Optional[Node],
    after: Optional[Node],
    rationale: str = "",
    source_grade: SourceGrade = "C",
) -> Optional[DiffEntry]:
    """
    Compute diff between two node states.

    Returns None if nodes are identical.
    """
    if before is None and after is None:
        return None

    if before is None and after is not None:
        return DiffEntry(
            type="NODE_ADD",
            target_id=after.id,
            before=None,
            after=as_clean_dict(after),
            rationale=rationale,
            source_grade=source_grade,
        )

    if before is not None and after is None:
        return DiffEntry(
            type="NODE_DELETE",
            target_id=before.id,
            before=as_clean_dict(before),
            after=None,
            rationale=rationale,
            source_grade=source_grade,
        )

    # Both exist - check if different
    before_dict = as_clean_dict(before)
    after_dict = as_clean_dict(after)

    if before_dict == after_dict:
        return None

    return DiffEntry(
        type="NODE_UPDATE",
        target_id=before.id,  # type: ignore
        before=before_dict,
        after=after_dict,
        rationale=rationale,
        source_grade=source_grade,
    )


def compute_batch_diff(
    before_nodes: Dict[str, Node],
    after_nodes: Dict[str, Node],
    rationale: str = "",
    source_grade: SourceGrade = "C",
    source_patch_id: Optional[str] = None,
    trace_level: TraceLevel = "standard",
) -> SemanticDiff:
    """
    Compute diff between two sets of nodes.

    Args:
        before_nodes: Dict of node_id -> Node (before state)
        after_nodes: Dict of node_id -> Node (after state)
        rationale: Overall rationale for the change
        source_grade: Evidence grade (A/B/C)
        source_patch_id: Optional ID of the source patch
        trace_level: Retention tier (standard/full)

    Returns:
        SemanticDiff with all changes
    """
    changes: List[DiffEntry] = []
    all_ids = set(before_nodes.keys()) | set(after_nodes.keys())

    for node_id in sorted(all_ids):
        before = before_nodes.get(node_id)
        after = after_nodes.get(node_id)

        entry = compute_node_diff(before, after, rationale, source_grade)
        if entry:
            changes.append(entry)

    diff_id = f"diff_{stable_hash(f'{utc_now()}:{len(changes)}')}"

    return SemanticDiff(
        id=diff_id,
        created_at=utc_now(),
        source_patch_id=source_patch_id,
        trace_level=trace_level,
        changes=changes,
    )


def create_rollback_request(
    target_patch_id: str,
    requested_by: str,
    rationale: str,
) -> Rollback:
    """Create a rollback request for a patch."""
    rollback_id = f"rollback_{stable_hash(f'{target_patch_id}:{utc_now()}')}"

    return Rollback(
        id=rollback_id,
        target_patch_id=target_patch_id,
        requested_by=requested_by,
        rationale=rationale,
        timestamp=utc_now(),
        status="pending",
    )


def summarize_diff(diff: SemanticDiff) -> Dict[str, Any]:
    """
    Generate a human-readable summary of a diff.

    Returns a dict with:
        - total_changes: int
        - by_type: Dict[str, int]
        - by_grade: Dict[str, int]
        - affected_nodes: List[str]
        - trace_level: str
    """
    by_type: Dict[str, int] = {}
    by_grade: Dict[str, int] = {}
    affected_nodes: List[str] = []

    for entry in diff.changes:
        by_type[entry.type] = by_type.get(entry.type, 0) + 1
        by_grade[entry.source_grade] = by_grade.get(entry.source_grade, 0) + 1
        affected_nodes.append(entry.target_id)

    return {
        "diff_id": diff.id,
        "created_at": diff.created_at,
        "source_patch_id": diff.source_patch_id,
        "trace_level": diff.trace_level,
        "total_changes": len(diff.changes),
        "by_type": by_type,
        "by_grade": by_grade,
        "affected_nodes": affected_nodes,
    }
