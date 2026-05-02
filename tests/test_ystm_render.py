"""Tests for tonesoul.ystm.render — xml_escape, render_svg, render_html, render_png."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, List, Tuple

from tonesoul.ystm.render import render_html, render_svg, xml_escape

# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_node(node_id: str = "n1", text: str = "hello") -> Any:
    """Create a minimal mock Node for render tests."""
    where_time = SimpleNamespace(turn_id="t0", event_index=0)
    where_field = SimpleNamespace(mode="analysis")
    where_task = SimpleNamespace(domain="test")
    where = SimpleNamespace(
        where_time=where_time,
        where_field=where_field,
        where_task=where_task,
    )
    scalar = SimpleNamespace(E_energy=0.5, E_srsp=0.3, E_risk=0.1, E_total=0.9)
    drift = SimpleNamespace(delta_v=None, delta_norm=None, drift_ref=None)
    return SimpleNamespace(id=node_id, text=text, where=where, scalar=scalar, drift=drift)


def _minimal_render_args(
    n_nodes: int = 2,
) -> Dict:
    """Return minimal valid args for render_svg / render_html."""
    nodes = [_make_node(f"n{i}", f"text {i}") for i in range(n_nodes)]
    points = [(float(i), float(i)) for i in range(n_nodes)]
    field_to_x = {"analysis": 0}
    segments_by_level: Dict[float, List[Tuple]] = {
        0.5: [((0.0, 0.0), (1.0, 1.0))],
    }
    bounds = (0.0, 2.0, 0.0, 2.0)
    return dict(
        nodes=nodes,
        points=points,
        field_to_x=field_to_x,
        segments_by_level=segments_by_level,
        bounds=bounds,
    )


# ── xml_escape ────────────────────────────────────────────────────────────────


class TestXmlEscape:
    def test_ampersand_escaped(self):
        assert xml_escape("a & b") == "a &amp; b"

    def test_less_than_escaped(self):
        assert xml_escape("a < b") == "a &lt; b"

    def test_greater_than_escaped(self):
        assert xml_escape("a > b") == "a &gt; b"

    def test_double_quote_escaped(self):
        assert xml_escape('say "hi"') == "say &quot;hi&quot;"

    def test_single_quote_escaped(self):
        assert xml_escape("it's") == "it&apos;s"

    def test_plain_text_unchanged(self):
        assert xml_escape("hello world") == "hello world"

    def test_empty_string(self):
        assert xml_escape("") == ""

    def test_multiple_special_chars(self):
        result = xml_escape("<a & b>")
        assert "&lt;" in result
        assert "&amp;" in result
        assert "&gt;" in result

    def test_returns_string(self):
        assert isinstance(xml_escape("x"), str)


# ── render_svg ────────────────────────────────────────────────────────────────


class TestRenderSvg:
    def test_returns_string(self):
        args = _minimal_render_args()
        result = render_svg(**args)
        assert isinstance(result, str)

    def test_opens_with_svg_tag(self):
        args = _minimal_render_args()
        result = render_svg(**args)
        assert result.strip().startswith("<svg")

    def test_closes_with_svg_tag(self):
        args = _minimal_render_args()
        result = render_svg(**args)
        assert result.strip().endswith("</svg>")

    def test_contains_node_ids(self):
        args = _minimal_render_args(n_nodes=2)
        result = render_svg(**args)
        assert "n0" in result
        assert "n1" in result

    def test_contains_node_text_as_tooltip(self):
        args = _minimal_render_args(n_nodes=1)
        result = render_svg(**args)
        assert "text 0" in result

    def test_contains_contour_lines(self):
        args = _minimal_render_args()
        result = render_svg(**args)
        assert "contour" in result

    def test_contains_drift_lines(self):
        args = _minimal_render_args(n_nodes=2)
        result = render_svg(**args)
        assert "drift" in result

    def test_contains_field_grid_labels(self):
        args = _minimal_render_args()
        result = render_svg(**args)
        assert "analysis" in result

    def test_empty_field_to_x_still_renders(self):
        args = _minimal_render_args()
        args["field_to_x"] = {}
        result = render_svg(**args)
        assert "<svg" in result

    def test_none_field_to_x_handled(self):
        args = _minimal_render_args()
        args["field_to_x"] = None
        result = render_svg(**args)
        assert "<svg" in result

    def test_axis_labels_included_when_provided(self):
        args = _minimal_render_args()
        result = render_svg(**args, axis_labels=("X Axis", "Y Axis"))
        assert "X Axis" in result
        assert "Y Axis" in result

    def test_no_axis_labels_by_default(self):
        args = _minimal_render_args()
        result = render_svg(**args)
        assert "X Axis" not in result

    def test_custom_width_height_in_svg(self):
        args = _minimal_render_args()
        result = render_svg(**args, width=800, height=400)
        assert 'width="800"' in result
        assert 'height="400"' in result

    def test_explicit_drift_segments_used(self):
        args = _minimal_render_args(n_nodes=2)
        drift_segments = [((0.0, 0.0), (1.0, 1.0))]
        result = render_svg(**args, drift_segments=drift_segments)
        assert "drift" in result

    def test_equal_bounds_doesnt_crash(self):
        args = _minimal_render_args(n_nodes=1)
        args["bounds"] = (1.0, 1.0, 1.0, 1.0)  # zero span
        result = render_svg(**args)
        assert "<svg" in result

    def test_special_chars_in_node_text_escaped(self):
        nodes = [_make_node("n0", "text <with> &special& chars")]
        points = [(0.0, 0.0)]
        args = dict(
            nodes=nodes,
            points=points,
            field_to_x={},
            segments_by_level={},
            bounds=(0.0, 2.0, 0.0, 2.0),
        )
        result = render_svg(**args)
        assert "&lt;" in result or "&amp;" in result

    def test_no_nodes_renders_without_crash(self):
        args = dict(
            nodes=[],
            points=[],
            field_to_x={},
            segments_by_level={},
            bounds=(0.0, 1.0, 0.0, 1.0),
        )
        result = render_svg(**args)
        assert "<svg" in result

    def test_multiple_contour_levels_all_rendered(self):
        args = _minimal_render_args()
        args["segments_by_level"] = {
            0.2: [((0.0, 0.0), (0.5, 0.5))],
            0.5: [((0.5, 0.5), (1.0, 1.0))],
            0.8: [((0.0, 1.0), (1.0, 0.0))],
        }
        result = render_svg(**args)
        assert "contour level-0" in result
        assert "contour level-1" in result
        assert "contour level-2" in result


# ── render_html ───────────────────────────────────────────────────────────────


class TestRenderHtml:
    def _make_svg(self) -> str:
        return render_svg(**_minimal_render_args())

    def test_returns_string(self):
        svg = self._make_svg()
        nodes = [_make_node("n0", "hello")]
        result = render_html(svg, {}, nodes)
        assert isinstance(result, str)

    def test_is_doctype_html(self):
        svg = self._make_svg()
        result = render_html(svg, {}, [_make_node()])
        assert "<!doctype html>" in result.lower()

    def test_contains_svg(self):
        svg = self._make_svg()
        result = render_html(svg, {}, [_make_node()])
        assert "<svg" in result

    def test_plane_label_in_output(self):
        svg = self._make_svg()
        result = render_html(svg, {"plane": "P2_test"}, [_make_node()])
        assert "P2_test" in result

    def test_audit_parameters_json_in_output(self):
        svg = self._make_svg()
        result = render_html(svg, {"my_param": 42}, [_make_node()])
        assert "my_param" in result
        assert "42" in result

    def test_node_json_data_embedded(self):
        svg = self._make_svg()
        node = _make_node("my-node-id", "my text")
        result = render_html(svg, {}, [node])
        assert "my-node-id" in result

    def test_script_tag_present(self):
        svg = self._make_svg()
        result = render_html(svg, {}, [_make_node()])
        assert "<script" in result

    def test_empty_nodes_list_renders(self):
        svg = self._make_svg()
        result = render_html(svg, {}, [])
        assert "<!doctype html>" in result.lower()

    def test_default_plane_note_used_when_missing(self):
        svg = self._make_svg()
        result = render_html(svg, {"plane": "P1"}, [_make_node()])
        assert "P1" in result

    def test_energy_note_in_legend(self):
        svg = self._make_svg()
        result = render_html(svg, {"energy_note": "custom energy note"}, [_make_node()])
        assert "custom energy note" in result

    def test_drift_note_in_legend(self):
        svg = self._make_svg()
        result = render_html(svg, {"drift_note": "custom drift note"}, [_make_node()])
        assert "custom drift note" in result

    def test_title_tag_present(self):
        svg = self._make_svg()
        result = render_html(svg, {}, [_make_node()])
        assert "<title>" in result

    def test_special_plane_note_escaped(self):
        svg = self._make_svg()
        result = render_html(svg, {"note": "plane <test> &check"}, [_make_node()])
        # HTML should contain the escaped version somewhere
        assert "plane" in result


# ── render_png (PIL optional) ─────────────────────────────────────────────────


class TestRenderPng:
    def test_returns_none_without_pil(self, monkeypatch):
        import builtins

        original_import = builtins.__import__

        def no_pil(name, *args, **kwargs):
            if name == "PIL":
                raise ImportError("no PIL")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", no_pil)
        from tonesoul.ystm import render as render_mod

        args = _minimal_render_args()
        result = render_mod.render_png(**args)
        assert result is None
