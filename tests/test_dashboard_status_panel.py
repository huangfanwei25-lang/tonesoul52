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
    / "status_panel.py"
)
_FRONTEND_ROOT = _MODULE_PATH.parents[1]
if str(_FRONTEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_FRONTEND_ROOT))
_SPEC = importlib.util.spec_from_file_location("dashboard_status_panel", _MODULE_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
build_status_panel_view_model = _MODULE.build_status_panel_view_model


def test_build_status_panel_view_model_reinforces_tier_model():
    snapshot = {
        "conversation": {"count": 3, "last": {"status": "success", "timestamp": "2026-04-06T12:00:00+00:00"}},
        "persona": {"id": "dashboard-workspace"},
        "run_id": "run-001",
    }
    summary = {
        "intent": {"status": "achieved"},
        "control": {"status": "success"},
        "persona": {"id": "dashboard-workspace"},
        "run_id": "run-001",
        "user_message": "整理目前短板",
        "assistant_summary": "短板是 Phase 774。",
    }
    tier0_shell = {
        "readiness_status": "pass",
        "task_track": "feature_track",
        "deliberation_mode": "lightweight_review",
        "next_followup": {"command": "python scripts/run_shared_edit_preflight.py --path task.md"},
        "receiver_rule": "bounded only",
        "hook_badges": [{"name": "shared_edit_path_overlap", "status": "active"}],
    }
    tier1_shell = {
        "canonical_cards": {
            "short_board": "Phase 774",
            "successor_correction": "closeout overrides smooth compaction prose",
            "source_precedence": "canonical > live > derived",
        },
        "parity_counts": {"baseline": 2, "beta_usable": 1, "partial": 1, "deferred": 0},
        "closeout_attention": {"summary_text": "latest closeout is partial"},
        "observer_shell": {"summary_text": "observer stable=2 contested=1 stale=0"},
    }
    tier2_drawer = {
        "recommended_open": True,
        "trigger_reasons": ["closeout_attention_present", "claim_conflict_visible"],
        "active_group_names": ["Mutation And Closeout", "Contested Continuity"],
        "summary_text": "tier2_drawer=recommended groups=2 triggers=2",
        "next_pull_commands": ["python scripts/run_publish_push_preflight.py --agent dashboard-workspace"],
    }

    result = build_status_panel_view_model(
        snapshot=snapshot,
        summary=summary,
        tier0_shell=tier0_shell,
        tier1_shell=tier1_shell,
        tier2_drawer=tier2_drawer,
    )

    assert result["tier0"]["readiness"] == "pass"
    assert result["tier0"]["next_followup_command"].startswith("python scripts/run_shared_edit_preflight.py")
    assert result["tier1"]["short_board"] == "Phase 774"
    assert result["tier1"]["closeout_attention"] == "latest closeout is partial"
    assert result["tier2"]["recommended_open"] is True
    assert result["tier2"]["active_groups"] == ["Mutation And Closeout", "Contested Continuity"]
    assert result["telemetry"]["conversation_status"] == "可用"
    assert result["telemetry"]["intent_status"] == "達成"
    assert result["telemetry"]["control_status"] == "成功"


def test_build_status_panel_view_model_handles_missing_tier_shells():
    result = build_status_panel_view_model(
        snapshot={"conversation": {"count": 0, "last": {}}},
        summary=None,
        tier0_shell=None,
        tier1_shell=None,
        tier2_drawer=None,
    )

    assert result["tier0"]["readiness"] == "unknown"
    assert result["tier1"]["short_board"] == "current short board not visible"
    assert result["tier2"]["recommended_open"] is False
    assert result["telemetry"]["conversation_count"] == 0
