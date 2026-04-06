from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

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
    assert "reference selection" in result["subtitle"]
    assert "Tier 0 / Tier 1" in result["operator_note"]


def test_build_memory_panel_view_model_handles_missing_shells():
    result = build_memory_panel_view_model(
        tier0_shell=None,
        tier1_shell=None,
        selected_count=0,
    )

    assert result["tier0_readiness"] == "unknown"
    assert result["current_short_board"] == ""
    assert result["closeout_attention"] == ""
