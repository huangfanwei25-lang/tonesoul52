from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "apps"
    / "dashboard"
    / "frontend"
    / "components"
    / "memory_panel.py"
)
_FRONTEND_ROOT = _MODULE_PATH.parents[1]
if str(_FRONTEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_FRONTEND_ROOT))

_streamlit_available = importlib.util.find_spec("streamlit") is not None
if not _streamlit_available:
    pytest.skip("streamlit not installed", allow_module_level=True)

_SPEC = importlib.util.spec_from_file_location("dashboard_memory_panel", _MODULE_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
build_memory_panel_view_model = _MODULE.build_memory_panel_view_model


def test_build_memory_panel_view_model_keeps_reference_surface_secondary():
    tier0_shell = {"readiness_status": "pass"}
    tier1_shell = {
        "canonical_cards": {"short_board": "Phase 781"},
        "closeout_attention": {"summary_text": "latest closeout is partial"},
    }

    result = build_memory_panel_view_model(
        tier0_shell=tier0_shell,
        tier1_shell=tier1_shell,
        selected_count=3,
    )

    assert result["tier0_readiness"] == "pass"
    assert result["current_short_board"] == "Phase 781"
    assert result["closeout_attention"] == "latest closeout is partial"
    assert result["selected_count"] == 3
    assert result["reference_boundary_class"] == "auxiliary_only"
    assert result["selected_count_summary"] == "已選 3 份參考資料"
    assert "reference selection" in result["subtitle"]
    assert "Tier 0 / Tier 1" in result["operator_note"]
    assert (
        "must not override Tier 0 / Tier 1 / Tier 2 operator truth" in result["reference_boundary"]
    )
    assert (
        "Do not use reference material to smooth over partial or blocked work."
        in result["selection_caution"]
    )
    assert result["section_labels"]["conversation"] == "對話記錄"


def test_build_memory_panel_view_model_handles_missing_shells():
    result = build_memory_panel_view_model(
        tier0_shell=None,
        tier1_shell=None,
        selected_count=0,
    )

    assert result["tier0_readiness"] == "unknown"
    assert result["current_short_board"] == ""
    assert result["closeout_attention"] == ""
    assert result["reference_boundary_class"] == "auxiliary_only"
    assert result["selection_caution"] == ""
    assert result["selected_count_summary"] == "已選 0 份參考資料"
