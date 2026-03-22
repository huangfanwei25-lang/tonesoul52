from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from tonesoul.ystm import demo as module
from tonesoul.ystm.demo import DEFAULT_SEGMENTS
from tonesoul.ystm.energy import EnergyConfig
from tonesoul.ystm.representation import EmbeddingConfig, build_nodes
from tonesoul.ystm.schema import NodeAudit, NodeDrift


def test_serialize_contours_and_point_list_round_values() -> None:
    contours = {0.5: [((0.1234567, 1.2345678), (2.3456789, 3.4567891))]}

    payload = module.serialize_contours(contours)

    assert payload == {
        "0.500000": [
            [
                [0.123457, 1.234568],
                [2.345679, 3.456789],
            ]
        ]
    }
    assert module._point_list((1.2345678, 9.8765432)) == [1.234568, 9.876543]


def test_write_demo_outputs_export_png_false_writes_core_artifacts_only(tmp_path: Path) -> None:
    outputs = module.write_demo_outputs(str(tmp_path), DEFAULT_SEGMENTS, export_png=False)

    assert Path(outputs["nodes"]).exists()
    assert Path(outputs["audit"]).exists()
    assert Path(outputs["terrain"]).exists()
    assert Path(outputs["terrain_json"]).exists()
    assert Path(outputs["terrain_p2"]).exists()
    assert Path(outputs["terrain_p2_json"]).exists()
    assert outputs["terrain_png"] is None
    assert outputs["terrain_p2_png"] is None


def test_write_demo_outputs_falls_back_to_render_png_when_svg_conversion_fails(
    tmp_path: Path,
    monkeypatch,
) -> None:
    calls: list[tuple[str, tuple[str, str]]] = []

    monkeypatch.setattr(module, "render_svg_to_png", lambda svg, output_path, scale: False)

    def _fake_render_png_fallback(
        output_path,
        nodes,
        points,
        field_to_x,
        contours,
        bounds,
        drift_segments,
        axis_labels,
        scale,
    ):
        calls.append(("fallback", axis_labels))
        return True

    monkeypatch.setattr(module, "render_png_fallback", _fake_render_png_fallback)

    outputs = module.write_demo_outputs(str(tmp_path), DEFAULT_SEGMENTS, export_png=True)

    assert outputs["terrain_png"] == str(tmp_path / "terrain.png")
    assert outputs["terrain_p2_png"] == str(tmp_path / "terrain_p2.png")
    assert calls == [("fallback", ("field", "time")), ("fallback", ("PCA1", "PCA2"))]


def test_build_drift_vectors_skips_missing_or_unknown_refs() -> None:
    nodes = build_nodes(DEFAULT_SEGMENTS[:2], config=EmbeddingConfig(dims=4), energy=EnergyConfig())
    nodes[0] = replace(nodes[0], drift=NodeDrift())
    nodes[1] = replace(
        nodes[1], drift=NodeDrift(delta_norm=1.5, drift_ref={"from_node_id": "node_999"})
    )
    valid = replace(
        nodes[1],
        id="node_003",
        drift=NodeDrift(delta_norm=1.5, drift_ref={"from_node_id": "node_001"}),
        audit=NodeAudit(created_at=nodes[1].audit.created_at, created_by="test", updates=[]),
    )

    vectors = module.build_drift_vectors(
        [nodes[0], nodes[1], valid],
        [(0.0, 0.0), (1.0, 1.0), (1.5, 2.0)],
    )

    assert vectors == [
        {
            "from_node_id": "node_001",
            "to_node_id": "node_003",
            "from_point": [0.0, 0.0],
            "to_point": [1.5, 2.0],
            "delta_xy": [1.5, 2.0],
            "delta_norm": 1.5,
        }
    ]


def test_render_svg_to_png_returns_false_when_backend_missing(monkeypatch, tmp_path: Path) -> None:
    original_import = __import__

    def _fake_import(name, *args, **kwargs):
        if name == "cairosvg":
            raise ImportError("missing")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", _fake_import)

    assert module.render_svg_to_png("<svg/>", str(tmp_path / "out.png"), scale=2.0) is False
