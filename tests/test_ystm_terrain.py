from __future__ import annotations

from types import SimpleNamespace

import pytest

from tonesoul.ystm.terrain import (
    TerrainConfig,
    build_levels,
    compute_plane_positions,
    kde_grid,
    marching_squares,
    order_unique,
)


def _node(mode: str, event_index: int):
    return SimpleNamespace(
        where=SimpleNamespace(
            where_field=SimpleNamespace(mode=mode),
            where_time=SimpleNamespace(event_index=event_index),
        )
    )


def test_order_unique_and_compute_plane_positions_preserve_first_seen_modes() -> None:
    values = order_unique(["risk", "analysis", "risk", "action"])
    points, field_to_x = compute_plane_positions(
        [_node("risk", 3), _node("analysis", 1), _node("risk", 4), _node("action", 2)]
    )

    assert values == ["risk", "analysis", "action"]
    assert field_to_x == {"risk": 0, "analysis": 1, "action": 2}
    assert points == [(0.0, 3.0), (1.0, 1.0), (0.0, 4.0), (2.0, 2.0)]


def test_kde_grid_and_build_levels_cover_error_zero_and_flat_cases() -> None:
    config = TerrainConfig(grid_width=4, grid_height=3, sigma=0.5, contour_levels=2)

    with pytest.raises(ValueError, match="No points provided"):
        kde_grid([], [], config)

    grid, xs, ys, bounds = kde_grid([(0.0, 0.0)], [1.0], config)
    assert len(grid) == 3
    assert len(grid[0]) == 4
    assert len(xs) == 4
    assert len(ys) == 3
    assert bounds == (-0.5, 0.5, -0.5, 0.5)
    assert build_levels(1.0, 1.0, 3) == [1.0]
    assert build_levels(0.0, 2.0, 0) == []


def test_marching_squares_returns_two_segments_for_saddle_cell() -> None:
    grid = [
        [1.0, 0.0],
        [0.0, 1.0],
    ]
    xs = [0.0, 1.0]
    ys = [0.0, 1.0]

    contours = marching_squares(grid, xs, ys, [0.5])

    assert 0.5 in contours
    assert len(contours[0.5]) == 2
