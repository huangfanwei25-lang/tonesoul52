"""Tests for tonesoul.consumer_contract — cross-agent memory consumer contract."""

from __future__ import annotations

from tonesoul.consumer_contract import build_memory_consumer_contract


class TestBuildMemoryConsumerContract:
    def test_returns_dict_with_present_true(self):
        result = build_memory_consumer_contract()
        assert result["present"] is True

    def test_required_read_order_has_five_steps(self):
        result = build_memory_consumer_contract()
        assert len(result["required_read_order"]) == 5

    def test_steps_numbered_one_through_five(self):
        result = build_memory_consumer_contract()
        steps = [item["step"] for item in result["required_read_order"]]
        assert steps == [1, 2, 3, 4, 5]

    def test_first_step_is_readiness_gate(self):
        result = build_memory_consumer_contract()
        assert result["required_read_order"][0]["surface"] == "readiness"
        assert result["required_read_order"][0]["role"] == "gate"

    def test_misread_guards_has_four_entries(self):
        result = build_memory_consumer_contract()
        assert len(result["misread_guards"]) == 4

    def test_compatible_consumers_is_list(self):
        result = build_memory_consumer_contract()
        assert isinstance(result["compatible_consumers"], list)
        assert len(result["compatible_consumers"]) > 0

    def test_current_context_readiness_defaults_to_unknown(self):
        result = build_memory_consumer_contract()
        assert result["current_context"]["readiness_status"] == "unknown"

    def test_current_context_closeout_defaults_to_complete(self):
        result = build_memory_consumer_contract()
        assert result["current_context"]["closeout_status"] == "complete"

    def test_readiness_pass_reflected_in_current_context(self):
        result = build_memory_consumer_contract(readiness_status="pass")
        assert result["current_context"]["readiness_status"] == "pass"

    def test_readiness_in_summary_text_when_not_unknown(self):
        result = build_memory_consumer_contract(readiness_status="pass")
        assert "readiness=pass" in result["summary_text"]

    def test_incomplete_closeout_in_summary_text(self):
        result = build_memory_consumer_contract(closeout_attention={"status": "pending"})
        assert "closeout=pending" in result["summary_text"]

    def test_short_board_visible_when_present(self):
        result = build_memory_consumer_contract(
            canonical_center={"current_short_board": {"present": True}}
        )
        assert result["current_context"]["short_board_visible"] is True

    def test_short_board_not_visible_by_default(self):
        result = build_memory_consumer_contract()
        assert result["current_context"]["short_board_visible"] is False

    def test_priority_guard_selected_for_incomplete_closeout(self):
        result = build_memory_consumer_contract(closeout_attention={"status": "pending"})
        guard = result["priority_misread_guard"]
        assert guard.get("name") == "compaction_not_completion"
        assert "why_now" in guard

    def test_priority_guard_selected_for_failing_readiness(self):
        # closeout defaults to complete, readiness not pass
        result = build_memory_consumer_contract(readiness_status="fail")
        guard = result["priority_misread_guard"]
        assert guard.get("name") == "observer_stable_not_verified"

    def test_priority_guard_closeout_takes_priority_over_readiness(self):
        # Both closeout incomplete and readiness not pass → closeout wins
        result = build_memory_consumer_contract(
            readiness_status="fail",
            closeout_attention={"status": "incomplete"},
        )
        guard = result["priority_misread_guard"]
        assert guard.get("name") == "compaction_not_completion"

    def test_source_precedence_uses_default_when_not_provided(self):
        result = build_memory_consumer_contract()
        assert "canonical_anchors" in result["source_precedence_summary"]

    def test_custom_source_precedence_propagated(self):
        result = build_memory_consumer_contract(
            canonical_center={"source_precedence_summary": "custom > order"}
        )
        assert result["source_precedence_summary"] == "custom > order"

    def test_next_followup_target_empty_by_default(self):
        result = build_memory_consumer_contract()
        assert result["current_context"]["next_followup_target"] == ""

    def test_next_followup_target_from_mutation_preflight(self):
        result = build_memory_consumer_contract(
            mutation_preflight={"next_followup": {"target": "review PR"}}
        )
        assert result["current_context"]["next_followup_target"] == "review PR"
