"""Tests for tonesoul.working_style — style observability and continuity."""

from __future__ import annotations

from tonesoul.working_style import (
    _collect_signal_texts,
    _style_tokens,
    build_working_style_continuity_validation,
    build_working_style_import_limits,
    build_working_style_observability,
    build_working_style_playbook,
)


class TestStyleTokens:
    def test_empty_string_returns_empty_set(self):
        assert _style_tokens("") == set()

    def test_none_returns_empty_set(self):
        assert _style_tokens(None) == set()

    def test_short_tokens_excluded(self):
        # "the", "an", "is" < 4 chars → excluded
        result = _style_tokens("the an is")
        assert result == set()

    def test_stopwords_excluded(self):
        result = _style_tokens("must keep write use")
        assert result == set()

    def test_valid_tokens_included(self):
        result = _style_tokens("evidence driven architecture")
        assert "evidence" in result
        assert "driven" in result
        assert "architecture" in result

    def test_uppercase_normalized_to_lower(self):
        result = _style_tokens("Evidence Architecture")
        assert "evidence" in result
        assert "architecture" in result

    def test_digits_allowed_in_tokens(self):
        result = _style_tokens("phase2 task3a")
        assert "phase2" in result
        assert "task3a" in result


class TestCollectSignalTexts:
    def test_empty_inputs_return_empty_list(self):
        signals = _collect_signal_texts()
        assert signals == []

    def test_carry_forward_items_added(self):
        signals = _collect_signal_texts(carry_forward=["keep evidence discipline"])
        assert len(signals) == 1
        assert signals[0]["source"] == "carry_forward"
        assert signals[0]["text"] == "keep evidence discipline"

    def test_blank_carry_forward_items_skipped(self):
        signals = _collect_signal_texts(carry_forward=["", "  ", "valid text"])
        assert len(signals) == 1

    def test_next_actions_items_added(self):
        signals = _collect_signal_texts(next_actions=["refactor architecture layer"])
        assert signals[0]["source"] == "next_actions"

    def test_routing_summary_text_added(self):
        signals = _collect_signal_texts(
            routing_summary={"summary_text": "architecture scan complete"}
        )
        assert any(s["source"] == "routing_summary" for s in signals)

    def test_routing_summary_recent_events_limited_to_five(self):
        events = [{"summary": f"event {i}"} for i in range(10)]
        signals = _collect_signal_texts(routing_summary={"recent_events": events})
        routing_event_signals = [s for s in signals if s["source"] == "routing_event"]
        assert len(routing_event_signals) == 5

    def test_routing_summary_event_without_summary_skipped(self):
        events = [{"summary": ""}, {"summary": "valid event summary"}]
        signals = _collect_signal_texts(routing_summary={"recent_events": events})
        routing_event_signals = [s for s in signals if s["source"] == "routing_event"]
        assert len(routing_event_signals) == 1


class TestBuildWorkingStyleObservability:
    def test_empty_anchor_returns_empty_dict(self):
        assert build_working_style_observability({}) == {}

    def test_none_anchor_returns_empty_dict(self):
        assert build_working_style_observability(None) == {}

    def test_anchor_with_no_trackable_items_is_not_trackable(self):
        anchor = {"summary": "some summary", "prompt_defaults": []}
        result = build_working_style_observability(anchor)
        assert result["status"] == "not_trackable"
        assert result["drift_risk"] == "medium"
        assert result["trackable_item_count"] == 0

    def test_unreinforced_when_no_signals_match(self):
        anchor = {"decision_preferences": ["use formal evidence chains"]}
        result = build_working_style_observability(anchor)
        # No signals → nothing can match
        assert result["status"] == "unreinforced"
        assert result["drift_risk"] == "high"
        assert result["reinforced_item_count"] == 0

    def test_reinforced_when_carry_forward_echoes_preference(self):
        anchor = {"decision_preferences": ["evidence-driven architecture review"]}
        result = build_working_style_observability(
            anchor, carry_forward=["evidence driven architecture review"]
        )
        assert result["status"] == "reinforced"
        assert result["drift_risk"] == "low"
        assert result["reinforced_item_count"] == 1

    def test_partial_when_only_some_items_matched(self):
        anchor = {
            "decision_preferences": ["evidence architecture"],
            "verified_routines": ["unrelated routine task xyzzy"],
        }
        result = build_working_style_observability(
            anchor, carry_forward=["evidence architecture scan"]
        )
        assert result["status"] == "partial"
        assert result["drift_risk"] == "medium"

    def test_result_contains_required_keys(self):
        anchor = {"decision_preferences": ["evidence tracking"]}
        result = build_working_style_observability(anchor)
        for key in (
            "status",
            "drift_risk",
            "trackable_item_count",
            "reinforced_item_count",
            "signal_count",
            "signal_sources",
            "reinforced_items",
            "unreinforced_items",
            "summary_text",
            "receiver_note",
        ):
            assert key in result

    def test_summary_text_contains_status_and_drift(self):
        anchor = {"decision_preferences": ["evidence tracking"]}
        result = build_working_style_observability(anchor)
        assert result["status"] in result["summary_text"]
        assert result["drift_risk"] in result["summary_text"]


class TestBuildWorkingStyleImportLimits:
    def test_empty_anchor_returns_empty_dict(self):
        assert build_working_style_import_limits({}) == {}

    def test_reinforced_status_gives_bounded_default_posture(self):
        anchor = {"decision_preferences": ["evidence tracking"]}
        result = build_working_style_import_limits(
            anchor, observability={"status": "reinforced", "drift_risk": "low"}
        )
        assert result["apply_posture"] == "bounded_default"

    def test_partial_status_gives_explicit_reuse_posture(self):
        anchor = {"decision_preferences": ["evidence tracking"]}
        result = build_working_style_import_limits(
            anchor, observability={"status": "partial", "drift_risk": "medium"}
        )
        assert result["apply_posture"] == "explicit_reuse_only"

    def test_unknown_status_gives_review_before_apply_posture(self):
        anchor = {"decision_preferences": ["evidence tracking"]}
        result = build_working_style_import_limits(anchor, observability={})
        assert result["apply_posture"] == "review_before_apply"

    def test_must_not_import_always_has_four_items(self):
        anchor = {"decision_preferences": ["evidence tracking"]}
        result = build_working_style_import_limits(anchor)
        assert len(result["must_not_import"]) == 4

    def test_high_drift_adds_extra_stop_condition(self):
        anchor = {"decision_preferences": ["evidence tracking"]}
        result_high = build_working_style_import_limits(
            anchor, observability={"drift_risk": "high"}
        )
        result_low = build_working_style_import_limits(anchor, observability={"drift_risk": "low"})
        assert len(result_high["stop_conditions"]) > len(result_low["stop_conditions"])

    def test_decision_preferences_adds_scan_order_safe_apply(self):
        anchor = {"decision_preferences": ["evidence first approach"]}
        result = build_working_style_import_limits(anchor)
        scan_order_items = [s for s in result["safe_apply"] if "scan_order" in s]
        assert len(scan_order_items) >= 1

    def test_result_contains_required_keys(self):
        anchor = {"decision_preferences": ["evidence tracking"]}
        result = build_working_style_import_limits(anchor)
        for key in (
            "apply_posture",
            "safe_apply",
            "must_not_import",
            "stop_conditions",
            "receiver_guidance",
            "summary_text",
        ):
            assert key in result


class TestBuildWorkingStyleContinuityValidation:
    def test_no_anchor_is_insufficient(self):
        result = build_working_style_continuity_validation(
            anchor={}, playbook={}, observability={}, import_limits={}
        )
        assert result["status"] == "insufficient"

    def test_full_context_is_sufficient(self):
        result = build_working_style_continuity_validation(
            anchor={"summary": "test"},
            playbook={"present": True, "non_promotion_rule": "no promo"},
            observability={"status": "reinforced"},
            import_limits={"must_not_import": ["rule1"]},
        )
        assert result["status"] == "sufficient"

    def test_partial_observability_gives_caution(self):
        result = build_working_style_continuity_validation(
            anchor={"summary": "test"},
            playbook={"present": True},
            observability={"status": "partial"},
            import_limits={"must_not_import": ["rule1"]},
        )
        assert result["status"] == "caution"

    def test_unreinforced_observability_gives_caution(self):
        result = build_working_style_continuity_validation(
            anchor={"summary": "test"},
            playbook={"present": True},
            observability={"status": "unreinforced"},
            import_limits={"must_not_import": ["rule1"]},
        )
        assert result["status"] == "caution"

    def test_score_is_fraction_of_passed_checks(self):
        result = build_working_style_continuity_validation(
            anchor={}, playbook={}, observability={}, import_limits={}
        )
        assert 0.0 <= result["score"] <= 1.0

    def test_result_contains_required_keys(self):
        result = build_working_style_continuity_validation(
            anchor={}, playbook={}, observability={}, import_limits={}
        )
        for key in ("status", "score", "checks", "summary_text", "receiver_note"):
            assert key in result

    def test_checks_dict_contains_five_entries(self):
        result = build_working_style_continuity_validation(
            anchor={}, playbook={}, observability={}, import_limits={}
        )
        assert len(result["checks"]) == 5


class TestBuildWorkingStylePlaybook:
    def test_empty_anchor_returns_not_present(self):
        result = build_working_style_playbook({})
        assert result["present"] is False
        assert result["checklist"] == []

    def test_none_anchor_returns_not_present(self):
        result = build_working_style_playbook(None)
        assert result["present"] is False

    def test_anchor_with_preferences_returns_present(self):
        anchor = {"decision_preferences": ["evidence-driven review"]}
        result = build_working_style_playbook(anchor)
        assert result["present"] is True

    def test_checklist_includes_preferences(self):
        anchor = {"decision_preferences": ["evidence-driven review", "test before commit"]}
        result = build_working_style_playbook(anchor)
        pref_items = [item for item in result["checklist"] if item.startswith("Preference:")]
        assert len(pref_items) == 2

    def test_checklist_preferences_capped_at_two(self):
        anchor = {"decision_preferences": ["pref1", "pref2", "pref3", "pref4"]}
        result = build_working_style_playbook(anchor)
        pref_items = [item for item in result["checklist"] if item.startswith("Preference:")]
        assert len(pref_items) == 2

    def test_checklist_includes_verified_routines(self):
        anchor = {"verified_routines": ["start session with boot"]}
        result = build_working_style_playbook(anchor)
        routine_items = [item for item in result["checklist"] if item.startswith("Routine:")]
        assert len(routine_items) == 1

    def test_render_caveat_appears_in_checklist(self):
        anchor = {"render_caveat": "check shell encoding before declaring corruption"}
        result = build_working_style_playbook(anchor)
        caveat_items = [item for item in result["checklist"] if "Render caveat" in item]
        assert len(caveat_items) == 1

    def test_non_promotion_rule_always_present(self):
        anchor = {"decision_preferences": ["evidence tracking"]}
        result = build_working_style_playbook(anchor)
        assert "non_promotion_rule" in result
        assert len(result["non_promotion_rule"]) > 0
