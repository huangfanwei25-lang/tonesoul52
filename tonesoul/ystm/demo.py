"""YSTM demo surface: end-to-end terrain/field visualization pipeline."""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from .audit import build_audit_log
from .energy import EnergyConfig
from .ingest import normalize_segments
from .projection import compute_pca_positions
from .render import render_html, render_png, render_svg
from .representation import EmbeddingConfig, build_nodes
from .schema import Node, as_clean_dict, utc_now
from .terrain import (
    TerrainConfig,
    build_levels,
    compute_plane_positions,
    kde_grid,
    marching_squares,
)

__ts_layer__ = "surface"
__ts_purpose__ = (
    "End-to-end YSTM demo: ingest segments, build terrain, render HTML/PNG/SVG surfaces."
)

DEFAULT_SEGMENTS = [
    {
        "text": "User asks for an auditable trail of decisions.",
        "mode": "analysis",
        "domain": "governance",
        "turn_id": 1,
        "source_grade": "C",
    },
    {
        "text": "System proposes a ledger entry with trace pointers.",
        "mode": "bridge",
        "domain": "governance",
        "turn_id": 2,
        "source_grade": "C",
    },
    {
        "text": "User wants a minimal demo with visible terrain.",
        "mode": "action",
        "domain": "engineering",
        "turn_id": 3,
        "source_grade": "C",
    },
    {
        "text": "Assistant flags drift risk and calls for caution.",
        "mode": "risk",
        "domain": "safety",
        "turn_id": 4,
        "source_grade": "C",
    },
    {
        "text": "Agreement on P1 plane and decoupled what/where.",
        "mode": "analysis",
        "domain": "engineering",
        "turn_id": 5,
        "source_grade": "C",
    },
    {
        "text": "Audit log captures E definition and visual parameters.",
        "mode": "audit",
        "domain": "governance",
        "turn_id": 6,
        "source_grade": "C",
    },
]


@dataclass(frozen=True)
class DemoConfig:
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    energy: EnergyConfig = field(default_factory=EnergyConfig)
    terrain: TerrainConfig = field(default_factory=TerrainConfig)


def serialize_contours(
    contours: Dict[float, List[Tuple[Tuple[float, float], Tuple[float, float]]]],
) -> Dict[str, List[List[List[float]]]]:
    payload: Dict[str, List[List[List[float]]]] = {}
    for level, segments in contours.items():
        key = f"{level:.6f}"
        payload[key] = [
            [
                [round(float(p1[0]), 6), round(float(p1[1]), 6)],
                [round(float(p2[0]), 6), round(float(p2[1]), 6)],
            ]
            for p1, p2 in segments
        ]
    return payload


def _point_list(point: Tuple[float, float]) -> List[float]:
    return [round(float(point[0]), 6), round(float(point[1]), 6)]


def render_svg_to_png(svg: str, output_path: str, scale: float) -> bool:
    try:
        import cairosvg
    except Exception:
        return False
    if scale <= 0:
        scale = 1.0
    try:
        cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=output_path, scale=scale)
    except Exception:
        return False
    return True


def render_png_fallback(
    output_path: str,
    nodes: Sequence[Node],
    points: Sequence[Tuple[float, float]],
    field_to_x: Dict[str, int],
    contours: Dict[float, List[Tuple[Tuple[float, float], Tuple[float, float]]]],
    bounds: Tuple[float, float, float, float],
    drift_segments: Sequence[Tuple[Tuple[float, float], Tuple[float, float]]],
    axis_labels: Tuple[str, str],
    scale: float,
) -> bool:
    image = render_png(
        nodes,
        points,
        field_to_x,
        contours,
        bounds,
        axis_labels=axis_labels,
        drift_segments=drift_segments,
        scale=scale,
    )
    if image is None:
        return False
    image.save(output_path)
    return True


def build_drift_vectors(
    nodes: Sequence[Node],
    points: Sequence[Tuple[float, float]],
) -> List[Dict[str, object]]:
    id_to_point = {node.id: points[index] for index, node in enumerate(nodes)}
    vectors: List[Dict[str, object]] = []
    for node in nodes:
        drift_ref = node.drift.drift_ref or {}
        from_id = drift_ref.get("from_node_id")
        if not from_id:
            continue
        from_point = id_to_point.get(from_id)
        to_point = id_to_point.get(node.id)
        if from_point is None or to_point is None:
            continue
        dx = float(to_point[0] - from_point[0])
        dy = float(to_point[1] - from_point[1])
        vectors.append(
            {
                "from_node_id": from_id,
                "to_node_id": node.id,
                "from_point": _point_list(from_point),
                "to_point": _point_list(to_point),
                "delta_xy": [round(dx, 6), round(dy, 6)],
                "delta_norm": node.drift.delta_norm,
            }
        )
    return vectors


def write_demo_outputs(
    output_dir: str,
    segments: Sequence[Dict[str, object]],
    config: DemoConfig = DemoConfig(),
    export_png: bool = False,
    png_scale: float = 2.0,
) -> Dict[str, Optional[str]]:
    os.makedirs(output_dir, exist_ok=True)
    normalized = normalize_segments(segments)
    nodes = build_nodes(normalized, config=config.embedding, energy=config.energy)

    weights = [node.scalar.E_total for node in nodes]

    node_ids = [node.id for node in nodes]
    points_p1, field_to_x = compute_plane_positions(nodes)
    drift_vectors_p1 = build_drift_vectors(nodes, points_p1)
    drift_segments_p1 = [
        (tuple(item["from_point"]), tuple(item["to_point"])) for item in drift_vectors_p1
    ]
    grid_p1, xs_p1, ys_p1, bounds_p1 = kde_grid(points_p1, weights, config=config.terrain)
    min_p1 = min(min(row) for row in grid_p1)
    max_p1 = max(max(row) for row in grid_p1)
    levels_p1 = build_levels(min_p1, max_p1, config.terrain.contour_levels)
    contours_p1 = marching_squares(grid_p1, xs_p1, ys_p1, levels_p1)

    points_p2, projection_meta = compute_pca_positions(nodes)
    drift_vectors_p2 = build_drift_vectors(nodes, points_p2)
    drift_segments_p2 = [
        (tuple(item["from_point"]), tuple(item["to_point"])) for item in drift_vectors_p2
    ]
    grid_p2, xs_p2, ys_p2, bounds_p2 = kde_grid(points_p2, weights, config=config.terrain)
    min_p2 = min(min(row) for row in grid_p2)
    max_p2 = max(max(row) for row in grid_p2)
    levels_p2 = build_levels(min_p2, max_p2, config.terrain.contour_levels)
    contours_p2 = marching_squares(grid_p2, xs_p2, ys_p2, levels_p2)

    def _fmt_weight(value: float) -> str:
        return f"{value:g}"

    energy_formula = (
        f"{_fmt_weight(config.energy.alpha)}*E_energy + "
        f"{_fmt_weight(config.energy.beta)}*E_srsp + "
        f"{_fmt_weight(config.energy.gamma)}*E_risk"
    )
    if config.energy.normalize:
        energy_note = f"E_total = normalize({energy_formula})"
    else:
        energy_note = f"E_total = {energy_formula}"

    visual_params_p1 = {
        "plane": "P1_field_time",
        "note": "Contours show E_total, arrows show drift between adjacent nodes.",
        "energy_note": energy_note,
        "drift_note": "arrows = drift_ref",
        "grid_width": config.terrain.grid_width,
        "grid_height": config.terrain.grid_height,
        "sigma": config.terrain.sigma,
        "contour_levels": config.terrain.contour_levels,
        "axis_labels": ["field", "time"],
        "field_to_x": field_to_x,
        "bounds": {
            "x_min": bounds_p1[0],
            "x_max": bounds_p1[1],
            "y_min": bounds_p1[2],
            "y_max": bounds_p1[3],
        },
    }
    visual_params_p2 = {
        "plane": "P2_pca",
        "note": "PCA projection (observational plane only).",
        "energy_note": energy_note,
        "drift_note": "arrows = drift_ref",
        "grid_width": config.terrain.grid_width,
        "grid_height": config.terrain.grid_height,
        "sigma": config.terrain.sigma,
        "contour_levels": config.terrain.contour_levels,
        "axis_labels": ["PCA1", "PCA2"],
        "bounds": {
            "x_min": bounds_p2[0],
            "x_max": bounds_p2[1],
            "y_min": bounds_p2[2],
            "y_max": bounds_p2[3],
        },
        "projection": projection_meta,
        "governance_note": "Visualization only; do not write back to where or v_sem.",
    }

    e_def = {
        "formula": "alpha*E_energy + beta*E_srsp + gamma*E_risk",
        "alpha": config.energy.alpha,
        "beta": config.energy.beta,
        "gamma": config.energy.gamma,
        "normalize": config.energy.normalize,
    }
    audit_log = build_audit_log(e_def, [visual_params_p1, visual_params_p2])
    update_ids = [update.id for update in audit_log.updates]
    for node in nodes:
        node.audit.updates = update_ids

    nodes_payload = {
        "generated_at": utc_now(),
        "plane": "P1_field_time",
        "nodes": [as_clean_dict(node) for node in nodes],
    }

    terrain_payload_p1 = {
        "generated_at": utc_now(),
        "plane": "P1_field_time",
        "bounds": {
            "x_min": bounds_p1[0],
            "x_max": bounds_p1[1],
            "y_min": bounds_p1[2],
            "y_max": bounds_p1[3],
        },
        "levels": [float(level) for level in levels_p1],
        "contours": serialize_contours(contours_p1),
        "points": [[float(x), float(y)] for x, y in points_p1],
        "node_ids": node_ids,
        "drift_vectors": drift_vectors_p1,
        "axis_labels": ["field", "time"],
        "field_to_x": field_to_x,
    }

    terrain_payload_p2 = {
        "generated_at": utc_now(),
        "plane": "P2_pca",
        "bounds": {
            "x_min": bounds_p2[0],
            "x_max": bounds_p2[1],
            "y_min": bounds_p2[2],
            "y_max": bounds_p2[3],
        },
        "levels": [float(level) for level in levels_p2],
        "contours": serialize_contours(contours_p2),
        "points": [[float(x), float(y)] for x, y in points_p2],
        "node_ids": node_ids,
        "drift_vectors": drift_vectors_p2,
        "axis_labels": ["PCA1", "PCA2"],
        "projection": projection_meta,
    }

    nodes_path = os.path.join(output_dir, "nodes.json")
    audit_path = os.path.join(output_dir, "audit_log.json")
    terrain_path = os.path.join(output_dir, "terrain.html")
    terrain_svg_path = os.path.join(output_dir, "terrain.svg")
    terrain_png_path = os.path.join(output_dir, "terrain.png")
    terrain_json_path = os.path.join(output_dir, "terrain.json")
    terrain_p2_path = os.path.join(output_dir, "terrain_p2.html")
    terrain_p2_svg_path = os.path.join(output_dir, "terrain_p2.svg")
    terrain_p2_png_path = os.path.join(output_dir, "terrain_p2.png")
    terrain_p2_json_path = os.path.join(output_dir, "terrain_p2.json")

    with open(nodes_path, "w", encoding="utf-8") as handle:
        json.dump(nodes_payload, handle, indent=2)

    with open(audit_path, "w", encoding="utf-8") as handle:
        json.dump(as_clean_dict(audit_log), handle, indent=2)

    with open(terrain_json_path, "w", encoding="utf-8") as handle:
        json.dump(terrain_payload_p1, handle, indent=2)

    with open(terrain_p2_json_path, "w", encoding="utf-8") as handle:
        json.dump(terrain_payload_p2, handle, indent=2)

    svg_p1 = render_svg(
        nodes,
        points_p1,
        field_to_x,
        contours_p1,
        bounds_p1,
        axis_labels=("field", "time"),
        drift_segments=drift_segments_p1,
    )
    html_p1 = render_html(svg_p1, visual_params_p1, nodes)
    with open(terrain_path, "w", encoding="utf-8") as handle:
        handle.write(html_p1)
    with open(terrain_svg_path, "w", encoding="utf-8") as handle:
        handle.write(svg_p1)
    terrain_png_created = False
    if export_png:
        terrain_png_created = render_svg_to_png(svg_p1, terrain_png_path, png_scale)
        if not terrain_png_created:
            terrain_png_created = render_png_fallback(
                terrain_png_path,
                nodes,
                points_p1,
                field_to_x,
                contours_p1,
                bounds_p1,
                drift_segments_p1,
                ("field", "time"),
                png_scale,
            )

    svg_p2 = render_svg(
        nodes,
        points_p2,
        {},
        contours_p2,
        bounds_p2,
        axis_labels=("PCA1", "PCA2"),
        drift_segments=drift_segments_p2,
    )
    html_p2 = render_html(svg_p2, visual_params_p2, nodes)
    with open(terrain_p2_path, "w", encoding="utf-8") as handle:
        handle.write(html_p2)
    with open(terrain_p2_svg_path, "w", encoding="utf-8") as handle:
        handle.write(svg_p2)
    terrain_p2_png_created = False
    if export_png:
        terrain_p2_png_created = render_svg_to_png(svg_p2, terrain_p2_png_path, png_scale)
        if not terrain_p2_png_created:
            terrain_p2_png_created = render_png_fallback(
                terrain_p2_png_path,
                nodes,
                points_p2,
                {},
                contours_p2,
                bounds_p2,
                drift_segments_p2,
                ("PCA1", "PCA2"),
                png_scale,
            )

    return {
        "nodes": nodes_path,
        "audit": audit_path,
        "terrain": terrain_path,
        "terrain_svg": terrain_svg_path,
        "terrain_png": terrain_png_path if terrain_png_created else None,
        "terrain_json": terrain_json_path,
        "terrain_p2": terrain_p2_path,
        "terrain_p2_svg": terrain_p2_svg_path,
        "terrain_p2_png": terrain_p2_png_path if terrain_p2_png_created else None,
        "terrain_p2_json": terrain_p2_json_path,
    }
