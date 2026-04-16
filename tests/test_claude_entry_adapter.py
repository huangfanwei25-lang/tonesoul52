from __future__ import annotations

from tonesoul.claude_entry_adapter import build_claude_entry_adapter


def test_build_claude_entry_adapter_preserves_first_hop_order() -> None:
    adapter = build_claude_entry_adapter(
        session_start_payload={
            "tier": 1,
            "readiness": {"status": "pass"},
            "deliberation_mode_hint": {"suggested_mode": "lightweight_review"},
            "canonical_center": {
                "current_short_board": {
                    "present": True,
                    "summary_text": "Phase 774: dashboard status panel tier alignment",
                }
            },
            "closeout_attention": {
                "status": "partial",
                "source_family": "bounded_handoff_closeout",
                "operator_action": "Review unresolved items before treating the handoff as resumable work.",
                "attention_pressures": ["status=partial", "unresolved=1"],
                "why_now": "latest compaction closeout is partial",
            },
            "mutation_preflight": {
                "next_followup": {"target": "shared_code_edit.path_overlap_preflight"}
            },
            "subsystem_parity": {
                "next_focus": {
                    "resolved_to": "task_board_governance.parking_preflight",
                    "source_family": "mutation_preflight_hooks",
                    "operator_action": "Run task-board parking review first.",
                    "focus_pressures": ["readiness=pass", "task_track=feature_track"],
                }
            },
            "next_pull": {
                "receiver_rule": "Pull the full Tier-2 bundle only when shared mutation or contested governance detail is required.",
                "recommended_commands": [
                    "python scripts/start_agent_session.py --agent claude-shell --tier 2"
                ],
            },
            "consumer_contract": {
                "receiver_rule": "Recover parent truth before widening context.",
                "required_read_order": [
                    {"surface": "readiness", "receiver_rule": "gate first"},
                    {"surface": "canonical_center", "receiver_rule": "read parent truth"},
                    {
                        "surface": "closeout_attention",
                        "receiver_rule": "read closeout before summary",
                    },
                    {
                        "surface": "mutation_preflight",
                        "receiver_rule": "check side effects before action",
                    },
                ],
                "misread_guards": [
                    {
                        "name": "compaction_not_completion",
                        "rule": "Compaction summaries remain subordinate to closeout status.",
                        "trigger_surface": "closeout_attention + compaction summary",
                        "operator_action": "read closeout first",
                    }
                ],
                "priority_misread_guard": {
                    "name": "compaction_not_completion",
                    "rule": "Compaction summaries remain subordinate to closeout status.",
                    "trigger_surface": "closeout_attention + compaction summary",
                    "operator_action": "read closeout first",
                    "why_now": "latest closeout is partial",
                },
            },
        }
    )

    assert adapter["present"] is True
    assert adapter["shell"] == "claude_style_shell"
    assert adapter["source_bundle_tier"] == 1
    assert adapter["first_hop_order"] == [
        "readiness",
        "canonical_center",
        "closeout_attention",
        "mutation_preflight",
    ]
    assert adapter["must_read_now"][0]["surface"] == "readiness"
    assert adapter["must_not_assume"][0]["name"] == "compaction_not_completion"
    assert adapter["must_correct_first"]["name"] == "compaction_not_completion"
    assert (
        adapter["must_correct_first"]["trigger_surface"]
        == "closeout_attention + compaction summary"
    )
    assert adapter["must_correct_first"]["operator_action"] == "read closeout first"
    assert adapter["priority_correction"]["name"] == "compaction_not_completion"
    assert adapter["priority_correction"]["blocked_assumption"] == (
        "Compaction summaries remain subordinate to closeout status."
    )
    assert adapter["priority_correction"]["re_read_now"] == [
        "readiness",
        "canonical_center",
        "closeout_attention",
        "mutation_preflight",
    ]
    assert (
        adapter["priority_correction"]["bounded_next_step_target"]
        == "shared_code_edit.path_overlap_preflight"
    )
    assert adapter["current_context"]["closeout_status"] == "partial"
    assert adapter["closeout_focus"]["source_family"] == "bounded_handoff_closeout"
    assert adapter["closeout_focus"]["attention_pressures"] == [
        "status=partial",
        "unresolved=1",
    ]
    assert adapter["current_context"]["short_board"] == (
        "Phase 774: dashboard status panel tier alignment"
    )
    assert adapter["next_focus"]["source_family"] == "mutation_preflight_hooks"
    assert adapter["surface_versioning"]["present"] is True
    assert adapter["surface_versioning"]["consumer_shells"][2]["consumer"] == "claude_style_shell"
    assert adapter["bounded_pulls"]["observe_first"] is True
