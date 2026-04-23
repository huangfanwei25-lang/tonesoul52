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


# ─────────────────────────────────────────────
# Extended coverage
# ─────────────────────────────────────────────


class TestOrderUnique:
    def test_empty_list_returns_empty(self):
        assert order_unique([]) == []

    def test_single_item(self):
        assert order_unique(["alpha"]) == ["alpha"]

    def test_all_same_returns_one(self):
        assert order_unique(["x", "x", "x"]) == ["x"]

    def test_order_preserved_not_sorted(self):
        assert order_unique(["c", "a", "b", "a"]) == ["c", "a", "b"]


class TestBuildLevels:
    def test_three_levels_between_zero_and_four(self):
        levels = build_levels(0.0, 4.0, 3)
        assert len(levels) == 3
        assert levels[0] == pytest.approx(1.0)
        assert levels[1] == pytest.approx(2.0)
        assert levels[2] == pytest.approx(3.0)

    def test_one_level_is_midpoint(self):
        levels = build_levels(0.0, 2.0, 1)
        assert levels == pytest.approx([1.0])

    def test_flat_min_equals_max_returns_min(self):
        assert build_levels(3.0, 3.0, 5) == [3.0]


class TestComputePlanePositions:
    def test_empty_nodes_returns_empty(self):
        points, mapping = compute_plane_positions([])
        assert points == []
        assert mapping == {}

    def test_single_node_maps_to_zero_x(self):
        node = _node("analysis", 7)
        points, mapping = compute_plane_positions([node])
        assert points == [(0.0, 7.0)]
        assert mapping == {"analysis": 0}


class TestKdeGrid:
    def test_multiple_points_produce_positive_density(self):
        config = TerrainConfig(grid_width=5, grid_height=4, sigma=1.0)
        points = [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)]
        weights = [1.0, 1.0, 1.0]
        grid, xs, ys, bounds = kde_grid(points, weights, config)
        # At least some cells should have positive density
        flat = [v for row in grid for v in row]
        assert max(flat) > 0.0

    def test_bounds_span_points_with_half_unit_margin(self):
        config = TerrainConfig(grid_width=3, grid_height=3)
        grid, xs, ys, (x_min, x_max, y_min, y_max) = kde_grid([(2.0, 3.0)], [1.0], config)
        assert x_min == pytest.approx(-0.5)
        assert x_max == pytest.approx(2.5)
        assert y_min == pytest.approx(-0.5)
        assert y_max == pytest.approx(3.5)


class TestMarchingSquares:
    def test_all_below_threshold_returns_no_segments(self):
        grid = [[0.0, 0.0], [0.0, 0.0]]
        contours = marching_squares(grid, [0.0, 1.0], [0.0, 1.0], [0.5])
        assert contours[0.5] == []

    def test_all_above_threshold_returns_no_segments(self):
        grid = [[1.0, 1.0], [1.0, 1.0]]
        contours = marching_squares(grid, [0.0, 1.0], [0.0, 1.0], [0.5])
        assert contours[0.5] == []

    def test_empty_levels_returns_empty_dict(self):
        grid = [[1.0, 0.0], [0.0, 1.0]]
        assert marching_squares(grid, [0.0, 1.0], [0.0, 1.0], []) == {}

    def test_each_level_has_key_in_result(self):
        grid = [[1.0, 0.0], [0.0, 1.0]]
        contours = marching_squares(grid, [0.0, 1.0], [0.0, 1.0], [0.3, 0.7])
        assert 0.3 in contours
        assert 0.7 in contours
