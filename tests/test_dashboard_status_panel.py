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
    / "status_panel.py"
)
_FRONTEND_ROOT = _MODULE_PATH.parents[1]
if str(_FRONTEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_FRONTEND_ROOT))

_streamlit_available = importlib.util.find_spec("streamlit") is not None
if not _streamlit_available:
    pytest.skip("streamlit not installed", allow_module_level=True)

_SPEC = importlib.util.spec_from_file_location("dashboard_status_panel", _MODULE_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
build_status_panel_view_model = _MODULE.build_status_panel_view_model


def test_build_status_panel_view_model_reinforces_tier_model() -> None:
    snapshot = {
        "conversation": {
            "count": 3,
            "last": {"status": "success", "timestamp": "2026-04-06T12:00:00+00:00"},
        },
        "persona": {"id": "dashboard-workspace"},
        "run_id": "run-001",
    }
    summary = {
        "intent": {"status": "achieved"},
        "control": {"status": "success"},
        "persona": {"id": "dashboard-workspace"},
        "run_id": "run-001",
        "user_message": "user message",
        "assistant_summary": "assistant summary",
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
        "next_pull_commands": [
            "python scripts/run_publish_push_preflight.py --agent dashboard-workspace"
        ],
    }
    improvement_cue = {
        "present": True,
        "summary_text": "self_improvement_trial_wave promote=1 park=1 | status surface only",
        "top_result": "consumer_parity_packaging_v1 / promoted_result",
        "next_action": "reuse this drift-validation wave whenever shared consumer packaging changes",
        "receiver_rule": "Secondary only. Open the dedicated self-improvement status surface first.",
        "source_path": "docs/status/self_improvement_trial_wave_latest.md",
        "outcome_counts": {"promote": 1, "park": 1, "retire": 0, "blocked": 0},
    }

    result = build_status_panel_view_model(
        snapshot=snapshot,
        summary=summary,
        tier0_shell=tier0_shell,
        tier1_shell=tier1_shell,
        tier2_drawer=tier2_drawer,
        improvement_cue=improvement_cue,
    )

    assert result["tier0"]["readiness"] == "pass"
    assert result["tier0"]["next_followup_command"].startswith(
        "python scripts/run_shared_edit_preflight.py"
    )
    assert result["tier1"]["short_board"] == "Phase 774"
    assert result["tier1"]["closeout_attention"] == "latest closeout is partial"
    assert result["tier2"]["recommended_open"] is True
    assert result["tier2"]["active_groups"] == ["Mutation And Closeout", "Contested Continuity"]
    assert result["self_improvement"]["present"] is True
    assert (
        result["self_improvement"]["top_result"] == "consumer_parity_packaging_v1 / promoted_result"
    )
    assert "Tier 0 / Tier 1" in result["operator_posture"]["note"]
    assert "parent action path" in result["operator_posture"]["primary_rule"]
    assert (
        result["operator_posture"]["secondary_rule"]
        == "Self-improvement posture and telemetry stay secondary."
    )
    assert result["telemetry"]["conversation_status"] == "成功"
    assert result["telemetry"]["intent_status"] == "達成"
    assert result["telemetry"]["control_status"] == "成功"
    assert result["telemetry"]["conversation_count"] == 3


def test_build_status_panel_view_model_handles_missing_tier_shells() -> None:
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
    assert result["self_improvement"]["present"] is False
    assert (
        result["operator_posture"]["secondary_rule"]
        == "Self-improvement posture and telemetry stay secondary."
    )
    assert result["telemetry"]["conversation_count"] == 0
