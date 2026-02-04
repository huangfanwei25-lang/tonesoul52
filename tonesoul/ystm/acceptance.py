from dataclasses import replace
from typing import Dict, List

from .demo import DEFAULT_SEGMENTS, serialize_contours
from .energy import EnergyConfig
from .governance import update_what, update_where
from .ingest import normalize_segments
from .projection import compute_pca_positions
from .representation import EmbeddingConfig, build_nodes
from .schema import as_clean_dict, round_floats
from .terrain import (
    TerrainConfig,
    build_levels,
    compute_plane_positions,
    kde_grid,
    marching_squares,
)


def test_decoupling() -> None:
    segments = normalize_segments(DEFAULT_SEGMENTS)
    nodes = build_nodes(segments, config=EmbeddingConfig())
    node = nodes[0]
    updated, record = update_what(
        node,
        "Updated text.",
        EmbeddingConfig(),
        EnergyConfig(),
        "Update content only.",
    )
    if as_clean_dict(updated.where) != as_clean_dict(node.where):
        raise AssertionError("WHAT_UPDATE mutated where.")
    if record.change_type != "WHAT_UPDATE":
        raise AssertionError("WHAT_UPDATE record type mismatch.")

    new_where_time = replace(
        node.where.where_time,
        event_index=node.where.where_time.event_index + 1,
    )
    new_where = replace(node.where, where_time=new_where_time)
    updated_where, where_record = update_where(node, new_where, "Shift time index.")
    if where_record.change_type != "WHERE_UPDATE":
        raise AssertionError("WHERE_UPDATE record missing.")
    if where_record.before is None or where_record.after is None:
        raise AssertionError("WHERE_UPDATE missing snapshot.")
    if not where_record.vetoable:
        raise AssertionError("WHERE_UPDATE must be vetoable.")
    if as_clean_dict(updated_where.where) != as_clean_dict(new_where):
        raise AssertionError("WHERE_UPDATE did not apply new where.")


def _terrain_signature(nodes: List[object]) -> Dict[str, object]:
    config = TerrainConfig()
    points, field_to_x = compute_plane_positions(nodes)
    weights = [node.scalar.E_total for node in nodes]
    grid, xs, ys, bounds = kde_grid(points, weights, config=config)
    min_val = min(min(row) for row in grid)
    max_val = max(max(row) for row in grid)
    levels = build_levels(min_val, max_val, config.contour_levels)
    contours = marching_squares(grid, xs, ys, levels)
    payload = {
        "grid": round_floats(grid),
        "levels": round_floats(levels),
        "contours": serialize_contours(contours),
        "bounds": round_floats(list(bounds)),
        "field_to_x": field_to_x,
    }
    return payload


def test_terrain_consistency() -> None:
    segments = normalize_segments(DEFAULT_SEGMENTS)
    nodes = build_nodes(segments, config=EmbeddingConfig())
    sig_a = _terrain_signature(nodes)
    sig_b = _terrain_signature(nodes)
    if sig_a != sig_b:
        raise AssertionError("Terrain output is not deterministic under fixed params.")


def test_drift_readability() -> None:
    segments = normalize_segments(DEFAULT_SEGMENTS)
    nodes = build_nodes(segments, config=EmbeddingConfig())
    ids = {node.id for node in nodes}
    for node in nodes[1:]:
        if node.drift.drift_ref is None:
            raise AssertionError("Drift reference missing.")
        from_id = node.drift.drift_ref.get("from_node_id")
        if from_id not in ids:
            raise AssertionError("Drift reference points to unknown node.")
        if node.drift.delta_norm is None:
            raise AssertionError("Drift magnitude missing.")


def test_p2_projection() -> None:
    segments = normalize_segments(DEFAULT_SEGMENTS)
    nodes = build_nodes(segments, config=EmbeddingConfig())
    points, meta = compute_pca_positions(nodes)
    if len(points) != len(nodes):
        raise AssertionError("P2 projection count mismatch.")
    if not meta.get("components"):
        raise AssertionError("P2 projection components missing.")
    for point in points:
        if len(point) != 2:
            raise AssertionError("P2 projection must be 2D.")


def test_audit_replay() -> None:
    segments = normalize_segments(DEFAULT_SEGMENTS)
    nodes = build_nodes(segments, config=EmbeddingConfig())
    node = nodes[0]
    snapshot = as_clean_dict(node)
    new_where_time = replace(
        node.where.where_time,
        event_index=node.where.where_time.event_index + 1,
    )
    new_where = replace(node.where, where_time=new_where_time)
    updated, record = update_where(node, new_where, "Replay test.")
    if not record.reversible:
        raise AssertionError("UpdateRecord should be reversible.")
    if record.before != snapshot:
        raise AssertionError("Record before snapshot mismatch.")
    if record.after is None:
        raise AssertionError("Record after snapshot missing.")
    restored_where = record.before.get("where")
    if restored_where != snapshot.get("where"):
        raise AssertionError("Replay snapshot mismatch.")
    if as_clean_dict(updated.where) != as_clean_dict(new_where):
        raise AssertionError("Update replay did not move where.")


def run_acceptance() -> List[Dict[str, str]]:
    tests = [
        ("T1_decoupling", test_decoupling),
        ("T2_terrain_consistency", test_terrain_consistency),
        ("T3_drift_readability", test_drift_readability),
        ("T4_p2_projection", test_p2_projection),
        ("T5_audit_replay", test_audit_replay),
    ]
    results: List[Dict[str, str]] = []
    for name, test in tests:
        try:
            test()
            results.append({"test": name, "status": "PASS"})
        except AssertionError as exc:
            results.append({"test": name, "status": "FAIL", "error": str(exc)})
    return results
