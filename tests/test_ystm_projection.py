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
