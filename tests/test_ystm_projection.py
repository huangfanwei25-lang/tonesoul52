from __future__ import annotations

from types import SimpleNamespace

from tonesoul.ystm.projection import compute_pca_positions


def _node(values: list[float]):
    return SimpleNamespace(what=SimpleNamespace(v_sem=values))


def test_compute_pca_positions_handles_empty_input() -> None:
    points, meta = compute_pca_positions([])

    assert points == []
    assert meta["components"] == []
    assert meta["explained_variance_ratio"] == []


def test_compute_pca_positions_pads_single_node_components_and_variance() -> None:
    points, meta = compute_pca_positions([_node([1.0, 2.0, 3.0])])

    assert len(points) == 1
    assert len(points[0]) == 2
    assert len(meta["components"]) == 2
    assert len(meta["explained_variance"]) == 2
    assert meta["note"].startswith("P2 projection")


def test_compute_pca_positions_handles_zero_dimensional_vectors() -> None:
    points, meta = compute_pca_positions([_node([])])

    assert points == []
    assert meta == {
        "mean": [],
        "components": [],
        "explained_variance": [],
        "explained_variance_ratio": [],
    }


# ─────────────────────────────────────────────
# Extended coverage
# ─────────────────────────────────────────────


class TestMultipleNodes:
    def test_returns_one_point_per_node(self):
        nodes = [_node([1.0, 0.0, 0.0]), _node([0.0, 1.0, 0.0]), _node([0.0, 0.0, 1.0])]
        points, _ = compute_pca_positions(nodes)
        assert len(points) == 3

    def test_points_are_two_tuples_of_floats(self):
        nodes = [_node([1.0, 2.0]), _node([3.0, 4.0])]
        points, _ = compute_pca_positions(nodes)
        for pt in points:
            assert len(pt) == 2
            assert isinstance(pt[0], float)
            assert isinstance(pt[1], float)

    def test_metadata_has_all_required_keys(self):
        nodes = [_node([1.0, 0.0]), _node([0.0, 1.0])]
        _, meta = compute_pca_positions(nodes)
        for key in ("mean", "components", "explained_variance", "explained_variance_ratio"):
            assert key in meta

    def test_metadata_components_is_2x2(self):
        nodes = [_node([1.0, 0.0]), _node([0.0, 1.0]), _node([1.0, 1.0])]
        _, meta = compute_pca_positions(nodes)
        assert len(meta["components"]) == 2
        assert len(meta["components"][0]) == 2

    def test_explained_variance_ratio_sums_to_one_or_less(self):
        nodes = [_node([float(i), float(i * 2)]) for i in range(5)]
        _, meta = compute_pca_positions(nodes)
        total = sum(meta["explained_variance_ratio"])
        assert total <= 1.0 + 1e-9

    def test_note_in_metadata_for_multi_node(self):
        nodes = [_node([1.0, 0.0]), _node([0.0, 1.0])]
        _, meta = compute_pca_positions(nodes)
        assert "note" in meta
        assert "observational" in meta["note"]
