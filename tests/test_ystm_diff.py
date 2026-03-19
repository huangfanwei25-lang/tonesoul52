from __future__ import annotations

from dataclasses import replace

from tonesoul.ystm.diff import (
    compute_batch_diff,
    compute_node_diff,
    create_rollback_request,
    summarize_diff,
)
from tonesoul.ystm.representation import EmbeddingConfig, build_nodes


def _nodes():
    segments = [
        {"text": "alpha", "mode": "analysis", "domain": "governance", "turn_id": 1},
        {"text": "beta", "mode": "action", "domain": "engineering", "turn_id": 2},
    ]
    built = build_nodes(segments, config=EmbeddingConfig(dims=4))
    return built[0], built[1]


def test_compute_node_diff_handles_add_delete_update_and_noop() -> None:
    before, after = _nodes()

    assert compute_node_diff(None, None) is None
    assert compute_node_diff(None, after).type == "NODE_ADD"
    assert compute_node_diff(before, None).type == "NODE_DELETE"
    assert compute_node_diff(before, before) is None

    updated = build_nodes(
        [{"text": "alpha updated", "mode": "analysis", "domain": "governance", "turn_id": 1}],
        config=EmbeddingConfig(dims=4),
    )[0]
    diff = compute_node_diff(before, updated, rationale="edit", source_grade="A")
    assert diff is not None
    assert diff.type == "NODE_UPDATE"
    assert diff.target_id == before.id
    assert diff.rationale == "edit"
    assert diff.source_grade == "A"


def test_compute_batch_diff_and_summarize_diff_preserve_sorted_targets() -> None:
    node_a, node_b = _nodes()
    node_a_updated = build_nodes(
        [{"text": "alpha changed", "mode": "analysis", "domain": "governance", "turn_id": 1}],
        config=EmbeddingConfig(dims=4),
    )[0]
    node_c = build_nodes(
        [{"text": "gamma", "mode": "risk", "domain": "safety", "turn_id": 3}],
        config=EmbeddingConfig(dims=4),
    )[0]
    node_c = replace(node_c, id="node_003")
    diff = compute_batch_diff(
        {"node_b": node_b, "node_a": node_a},
        {"node_c": node_c, "node_a": node_a_updated},
        rationale="batch",
        source_grade="B",
        source_patch_id="patch-1",
        trace_level="full",
    )
    summary = summarize_diff(diff)

    assert [entry.target_id for entry in diff.changes] == ["node_001", "node_002", "node_003"]
    assert diff.source_patch_id == "patch-1"
    assert diff.trace_level == "full"
    assert summary["total_changes"] == 3
    assert summary["by_type"] == {"NODE_UPDATE": 1, "NODE_DELETE": 1, "NODE_ADD": 1}
    assert summary["by_grade"] == {"B": 3}
    assert summary["affected_nodes"] == ["node_001", "node_002", "node_003"]


def test_create_rollback_request_defaults_to_pending_status() -> None:
    rollback = create_rollback_request("patch-7", "operator", "revert")

    assert rollback.target_patch_id == "patch-7"
    assert rollback.requested_by == "operator"
    assert rollback.status == "pending"
