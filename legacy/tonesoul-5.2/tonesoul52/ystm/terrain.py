from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

import numpy as np

from .schema import Node


@dataclass(frozen=True)
class TerrainConfig:
    grid_width: int = 80
    grid_height: int = 60
    sigma: float = 0.75
    contour_levels: int = 5


def order_unique(values: Sequence[str]) -> List[str]:
    seen = set()
    ordered = []
    for value in values:
        if value not in seen:
            ordered.append(value)
            seen.add(value)
    return ordered


def compute_plane_positions(
    nodes: Sequence[Node],
) -> Tuple[List[Tuple[float, float]], Dict[str, int]]:
    modes = order_unique([node.where.where_field.mode for node in nodes])
    field_to_x = {mode: index for index, mode in enumerate(modes)}
    points = []
    for node in nodes:
        x = field_to_x[node.where.where_field.mode]
        y = node.where.where_time.event_index
        points.append((float(x), float(y)))
    return points, field_to_x


def kde_grid(
    points: Sequence[Tuple[float, float]],
    weights: Sequence[float],
    config: TerrainConfig,
) -> Tuple[List[List[float]], List[float], List[float], Tuple[float, float, float, float]]:
    if not points:
        raise ValueError("No points provided for terrain grid.")
    max_x = max(point[0] for point in points)
    max_y = max(point[1] for point in points)
    x_min, x_max = -0.5, max_x + 0.5
    y_min, y_max = -0.5, max_y + 0.5

    xs = np.linspace(x_min, x_max, config.grid_width)
    ys = np.linspace(y_min, y_max, config.grid_height)
    grid = np.zeros((config.grid_height, config.grid_width), dtype=float)
    sigma2 = 2 * config.sigma * config.sigma
    X, Y = np.meshgrid(xs, ys)

    for (px, py), weight in zip(points, weights):
        dx = X - px
        dy = Y - py
        grid += weight * np.exp(-(dx * dx + dy * dy) / sigma2)

    return grid.tolist(), xs.tolist(), ys.tolist(), (x_min, x_max, y_min, y_max)


def build_levels(min_val: float, max_val: float, count: int) -> List[float]:
    if count <= 0:
        return []
    if max_val <= min_val:
        return [min_val]
    step = (max_val - min_val) / (count + 1)
    return [min_val + step * (index + 1) for index in range(count)]


def marching_squares(
    grid: Sequence[Sequence[float]],
    xs: Sequence[float],
    ys: Sequence[float],
    levels: Sequence[float],
) -> Dict[float, List[Tuple[Tuple[float, float], Tuple[float, float]]]]:
    segments: Dict[float, List[Tuple[Tuple[float, float], Tuple[float, float]]]] = {}
    height = len(grid)
    width = len(grid[0]) if height else 0
    for level in levels:
        level_segments: List[Tuple[Tuple[float, float], Tuple[float, float]]] = []
        for j in range(height - 1):
            for i in range(width - 1):
                v0 = grid[j][i]
                v1 = grid[j][i + 1]
                v2 = grid[j + 1][i + 1]
                v3 = grid[j + 1][i]
                inside = [v0 >= level, v1 >= level, v2 >= level, v3 >= level]
                edges: Dict[int, Tuple[float, float]] = {}
                x0, x1 = xs[i], xs[i + 1]
                y0, y1 = ys[j], ys[j + 1]

                if inside[0] != inside[1]:
                    t = (level - v0) / (v1 - v0) if v1 != v0 else 0.5
                    edges[0] = (x0 + t * (x1 - x0), y0)
                if inside[1] != inside[2]:
                    t = (level - v1) / (v2 - v1) if v2 != v1 else 0.5
                    edges[1] = (x1, y0 + t * (y1 - y0))
                if inside[2] != inside[3]:
                    t = (level - v2) / (v3 - v2) if v3 != v2 else 0.5
                    edges[2] = (x1 + t * (x0 - x1), y1)
                if inside[3] != inside[0]:
                    t = (level - v3) / (v0 - v3) if v0 != v3 else 0.5
                    edges[3] = (x0, y1 + t * (y0 - y1))

                if len(edges) == 2:
                    points = list(edges.values())
                    level_segments.append((points[0], points[1]))
                elif len(edges) == 4:
                    level_segments.append((edges[0], edges[3]))
                    level_segments.append((edges[1], edges[2]))
        segments[level] = level_segments
    return segments
