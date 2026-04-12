"""Tests for visualization components — robustness checks."""

import importlib
import importlib.util
import sys
from pathlib import Path

import pytest

# Add the dashboard frontend to sys.path so component modules can find 'utils'
_frontend_dir = str(Path(__file__).resolve().parents[1] / "apps" / "dashboard" / "frontend")
if _frontend_dir not in sys.path:
    sys.path.insert(0, _frontend_dir)

# Skip entire module when streamlit is not installed (CI environment)
pytest.importorskip("streamlit", reason="streamlit not installed — skip dashboard component tests")


def _import_module(name: str, filepath: str):
    spec = importlib.util.spec_from_file_location(name, filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_components = Path(__file__).resolve().parents[1] / "apps" / "dashboard" / "frontend" / "components"

council_timeline = _import_module("council_timeline", str(_components / "council_timeline.py"))
session_journal = _import_module("session_journal", str(_components / "session_journal.py"))
soul_band_gauge = _import_module("soul_band_gauge", str(_components / "soul_band_gauge.py"))
tension_chart = _import_module("tension_chart", str(_components / "tension_chart.py"))
drift_radar = _import_module("drift_radar", str(_components / "drift_radar.py"))
vow_cards = _import_module("vow_cards", str(_components / "vow_cards.py"))
explainer = _import_module("explainer", str(_components / "explainer.py"))


# ── Council Timeline ──────────────────────────────────────────────────


def test_role_colors_has_expected_roles():
    for role in ("guardian", "analyst", "critic", "advocate"):
        assert role in council_timeline._ROLE_COLORS
        assert council_timeline._ROLE_COLORS[role].startswith("#")


def test_council_timeline_callable():
    assert callable(council_timeline.render_council_timeline)


# ── Session Journal ───────────────────────────────────────────────────


def test_session_journal_callable():
    assert callable(session_journal.render_session_journal)


# ── Soul Band Gauge ───────────────────────────────────────────────────


def test_soul_band_gauge_callable():
    assert callable(soul_band_gauge.render_soul_band_gauge)


# ── Tension Chart ─────────────────────────────────────────────────────


def test_tension_chart_callable():
    assert callable(tension_chart.render_tension_chart)


# ── Drift Radar ───────────────────────────────────────────────────────


def test_drift_radar_callable():
    assert callable(drift_radar.render_drift_radar)


# ── Vow Cards ─────────────────────────────────────────────────────────


def test_vow_cards_callable():
    assert callable(vow_cards.render_vow_cards)


# ── Explainer ─────────────────────────────────────────────────────────


def test_explainer_has_all_concepts():
    expected = {"soul_integral", "soul_band", "tension", "drift", "vow", "council"}
    assert expected.issubset(set(explainer._EXPLANATIONS.keys()))


def test_explainer_entries_have_required_fields():
    for key, info in explainer._EXPLANATIONS.items():
        assert "title" in info, f"{key} missing title"
        assert "simple" in info, f"{key} missing simple"
        assert "detail" in info, f"{key} missing detail"
        assert len(info["simple"]) > 10, f"{key} simple too short"
        assert len(info["detail"]) > 20, f"{key} detail too short"


def test_explainer_callable():
    assert callable(explainer.render_explainer)
