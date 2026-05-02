from __future__ import annotations

from tonesoul.runtime_adapter_normalization import (
    build_council_dossier_summary,
    clean_string_list,
    clean_text_list,
    derive_council_realism_note_from_normalized,
    find_recycled_carry_forward_hazard,
    looks_like_stop_action,
    normalize_closeout_payload,
    normalize_council_dossier,
)

# ─── clean_text_list ─────────────────────────────────────────────────────────


class TestCleanTextList:
    def test_none_returns_empty(self):
        assert clean_text_list(None) == []

    def test_strips_whitespace(self):
        assert clean_text_list(["  hello  ", " world "]) == ["hello", "world"]

    def test_deduplicates(self):
        assert clean_text_list(["a", "a", "b"]) == ["a", "b"]

    def test_empty_strings_excluded(self):
        assert clean_text_list(["", "  ", "ok"]) == ["ok"]

    def test_non_strings_converted(self):
        assert clean_text_list([1, 2, None]) == ["1", "2"]


# ─── clean_string_list ───────────────────────────────────────────────────────


class TestCleanStringList:
    def test_none_returns_empty(self):
        assert clean_string_list(None) == []

    def test_strips_and_deduplicates(self):
        assert clean_string_list(["  x  ", "x", "y"]) == ["x", "y"]

    def test_empty_strings_excluded(self):
        assert clean_string_list(["", "a"]) == ["a"]

    def test_none_elements_excluded(self):
        result = clean_string_list([None, "valid"])
        assert result == ["valid"]


# ─── looks_like_stop_action ──────────────────────────────────────────────────


class TestLooksLikeStopAction:
    def test_stop_colon_prefix_true(self):
        assert looks_like_stop_action("STOP: do not continue") is True

    def test_lowercase_stop_true(self):
        assert looks_like_stop_action("stop: reason") is True

    def test_mixed_case_true(self):
        assert looks_like_stop_action("Stop: now") is True

    def test_non_stop_false(self):
        assert looks_like_stop_action("continue processing") is False

    def test_empty_string_false(self):
        assert looks_like_stop_action("") is False

    def test_stop_without_colon_false(self):
        assert looks_like_stop_action("STOP processing") is False


# ─── normalize_closeout_payload ──────────────────────────────────────────────


class TestNormalizeCloseoutPayload:
    def test_empty_call_returns_complete(self):
        result = normalize_closeout_payload()
        assert result["status"] == "complete"

    def test_valid_status_preserved(self):
        result = normalize_closeout_payload(status="partial")
        assert result["status"] == "partial"

    def test_invalid_status_overridden(self):
        result = normalize_closeout_payload(status="unknown_status")
        assert result["status"] in {"complete", "partial", "blocked", "underdetermined"}

    def test_unresolved_items_causes_partial(self):
        result = normalize_closeout_payload(unresolved_items=["item1"])
        assert result["status"] == "partial"

    def test_human_required_causes_blocked(self):
        result = normalize_closeout_payload(human_input_required=True)
        assert result["status"] == "blocked"

    def test_stop_action_next_action_causes_blocked(self):
        result = normalize_closeout_payload(next_action="STOP: wait for review")
        assert result["status"] == "blocked"

    def test_valid_stop_reason_causes_blocked(self):
        result = normalize_closeout_payload(stop_reason="external_blocked")
        assert result["status"] == "blocked"

    def test_underdetermined_stop_reason_causes_underdetermined(self):
        result = normalize_closeout_payload(stop_reason="underdetermined")
        assert result["status"] == "underdetermined"
        assert result["stop_reason"] == "underdetermined"

    def test_dict_closeout_overrides_kwargs(self):
        result = normalize_closeout_payload({"status": "blocked"}, status="complete")
        assert result["status"] == "blocked"

    def test_unresolved_merged_from_both_sources(self):
        result = normalize_closeout_payload(
            {"unresolved_items": ["a"]},
            unresolved_items=["b"],
        )
        assert "a" in result["unresolved_items"]
        assert "b" in result["unresolved_items"]

    def test_note_auto_generated_for_complete(self):
        result = normalize_closeout_payload()
        assert "no unresolved" in result["note"].lower()

    def test_note_auto_generated_for_partial(self):
        result = normalize_closeout_payload(unresolved_items=["x"])
        assert "incomplete" in result["note"].lower() or "partial" in result["note"].lower()

    def test_note_auto_generated_for_blocked(self):
        result = normalize_closeout_payload(human_input_required=True)
        assert "blocked" in result["note"].lower()

    def test_custom_note_preserved(self):
        result = normalize_closeout_payload(note="custom note here")
        assert result["note"] == "custom note here"

    def test_complete_status_overridden_when_has_pending_paths(self):
        result = normalize_closeout_payload(status="complete", pending_paths=["path/to/file"])
        assert result["status"] == "partial"

    def test_required_keys_always_present(self):
        result = normalize_closeout_payload()
        for key in ("status", "stop_reason", "unresolved_items", "human_input_required", "note"):
            assert key in result

    def test_normalize_closeout_blocks_on_stop_action(self):
        payload = normalize_closeout_payload(
            {},
            next_action="STOP: wait for human approval before continuing",
        )
        assert payload["status"] == "blocked"
        assert payload["stop_reason"] == ""
        assert (
            payload["note"] == "Closeout is blocked; do not treat this handoff as completed work."
        )


# ─── find_recycled_carry_forward_hazard ──────────────────────────────────────


class TestFindRecycledCarryForwardHazard:
    def test_no_newer_compactions_returns_empty(self):
        result = find_recycled_carry_forward_hazard(newer_compactions=[], all_compactions=[])
        assert result == ""

    def test_no_carry_forward_returns_empty(self):
        latest = {"compaction_id": "c1", "carry_forward": []}
        result = find_recycled_carry_forward_hazard(
            newer_compactions=[latest], all_compactions=[latest]
        )
        assert result == ""

    def test_identical_carry_forward_same_evidence_triggers_hazard(self):
        cf = ["action: fix bug"]
        evidence = ["ref1"]
        latest = {"compaction_id": "c2", "carry_forward": cf, "evidence_refs": evidence}
        previous = {"compaction_id": "c1", "carry_forward": cf, "evidence_refs": evidence}
        result = find_recycled_carry_forward_hazard(
            newer_compactions=[latest], all_compactions=[latest, previous]
        )
        assert "recycled" in result.lower()

    def test_different_carry_forward_no_hazard(self):
        latest = {"compaction_id": "c2", "carry_forward": ["new item"]}
        previous = {"compaction_id": "c1", "carry_forward": ["old item"]}
        result = find_recycled_carry_forward_hazard(
            newer_compactions=[latest], all_compactions=[latest, previous]
        )
        assert result == ""

    def test_same_id_skipped_in_comparison(self):
        cf = ["action: fix bug"]
        comp = {"compaction_id": "same-id", "carry_forward": cf, "evidence_refs": ["ref1"]}
        result = find_recycled_carry_forward_hazard(
            newer_compactions=[comp], all_compactions=[comp, comp]
        )
        assert result == ""

    def test_new_evidence_prevents_hazard(self):
        cf = ["action: fix bug"]
        latest = {"compaction_id": "c2", "carry_forward": cf, "evidence_refs": ["ref1", "ref2"]}
        previous = {"compaction_id": "c1", "carry_forward": cf, "evidence_refs": ["ref1"]}
        result = find_recycled_carry_forward_hazard(
            newer_compactions=[latest], all_compactions=[latest, previous]
        )
        assert result == ""

    def test_real_world_example(self):
        latest = {
            "compaction_id": "c2",
            "carry_forward": ["keep packet-first session cadence stable"],
            "evidence_refs": ["docs/AI_QUICKSTART.md"],
        }
        previous = {
            "compaction_id": "c1",
            "carry_forward": ["keep packet-first session cadence stable"],
            "evidence_refs": ["docs/AI_QUICKSTART.md"],
        }
        hazard = find_recycled_carry_forward_hazard(
            newer_compactions=[latest], all_compactions=[latest, previous]
        )
        assert "recycled carry_forward" in hazard


# ─── normalize_council_dossier ───────────────────────────────────────────────


class TestNormalizeCouncilDossier:
    def test_non_dict_returns_empty(self):
        assert normalize_council_dossier(None) == {}
        assert normalize_council_dossier("string") == {}

    def test_empty_dict_returns_minority_vote_summary(self):
        result = normalize_council_dossier({})
        assert result["minority_report"] == []
        assert result["vote_summary"] == []

    def test_string_fields_extracted(self):
        result = normalize_council_dossier(
            {
                "dossier_version": "1.0",
                "final_verdict": "APPROVE",
                "deliberation_mode": "standard",
            }
        )
        assert result["dossier_version"] == "1.0"
        assert result["final_verdict"] == "APPROVE"
        assert result["deliberation_mode"] == "standard"

    def test_empty_string_fields_excluded(self):
        result = normalize_council_dossier({"dossier_version": ""})
        assert "dossier_version" not in result

    def test_coherence_score_rounded(self):
        result = normalize_council_dossier({"coherence_score": 0.88889})
        assert result["coherence_score"] == 0.889

    def test_invalid_coherence_score_skipped(self):
        result = normalize_council_dossier({"coherence_score": "bad"})
        assert "coherence_score" not in result

    def test_minority_report_filtered(self):
        result = normalize_council_dossier(
            {
                "minority_report": [
                    {"perspective": "guardian", "decision": "block", "reasoning": "risk"},
                    {"perspective": "", "decision": "block", "reasoning": "missing perspective"},
                ]
            }
        )
        assert len(result["minority_report"]) == 1
        assert result["minority_report"][0]["perspective"] == "guardian"

    def test_vote_summary_filtered(self):
        result = normalize_council_dossier(
            {
                "vote_summary": [
                    {"perspective": "analyst", "decision": "approve"},
                    {"perspective": "", "decision": "approve"},
                ]
            }
        )
        assert len(result["vote_summary"]) == 1

    def test_grounding_summary_normalized(self):
        result = normalize_council_dossier(
            {"grounding_summary": {"has_ungrounded_claims": True, "total_evidence_sources": 3}}
        )
        gs = result["grounding_summary"]
        assert gs["has_ungrounded_claims"] is True
        assert gs["total_evidence_sources"] == 3

    def test_evolution_suppression_flag_coerced_to_bool(self):
        result = normalize_council_dossier({"evolution_suppression_flag": 1})
        assert result["evolution_suppression_flag"] is True


# ─── derive_council_realism_note_from_normalized ─────────────────────────────


class TestDeriveCouncilRealismNote:
    def test_empty_dossier_returns_empty(self):
        assert derive_council_realism_note_from_normalized({}) == ""

    def test_descriptive_only_returns_note(self):
        dossier = {"confidence_decomposition": {"calibration_status": "descriptive_only"}}
        note = derive_council_realism_note_from_normalized(dossier)
        assert "Descriptive agreement" in note

    def test_suppression_and_minority_returns_specific_note(self):
        dossier = {
            "confidence_decomposition": {"calibration_status": "descriptive_only"},
            "evolution_suppression_flag": True,
            "minority_report": [{"perspective": "critic"}],
        }
        note = derive_council_realism_note_from_normalized(dossier)
        assert "suppression" in note.lower() or "dissent" in note.lower()

    def test_minority_report_alone_returns_note(self):
        dossier = {"minority_report": [{"perspective": "critic"}]}
        note = derive_council_realism_note_from_normalized(dossier)
        assert "minority" in note.lower() or "dissent" in note.lower()

    def test_no_special_conditions_returns_empty(self):
        dossier = {"final_verdict": "APPROVE"}
        note = derive_council_realism_note_from_normalized(dossier)
        assert note == ""


# ─── build_council_dossier_summary ───────────────────────────────────────────


class TestBuildCouncilDossierSummary:
    def test_none_payload_returns_empty(self):
        assert build_council_dossier_summary(None) == {}

    def test_required_keys_present(self):
        result = build_council_dossier_summary({"final_verdict": "APPROVE"})
        for key in (
            "final_verdict",
            "confidence_posture",
            "coherence_score",
            "dissent_ratio",
            "has_minority_report",
        ):
            assert key in result

    def test_has_minority_report_false_when_empty(self):
        result = build_council_dossier_summary({})
        assert result["has_minority_report"] is False

    def test_has_minority_report_true_when_present(self):
        payload = {
            "minority_report": [{"perspective": "critic", "decision": "block", "reasoning": "risk"}]
        }
        result = build_council_dossier_summary(payload)
        assert result["has_minority_report"] is True

    def test_surfaces_realism_note(self):
        summary = build_council_dossier_summary(
            {
                "final_verdict": "approve",
                "confidence_posture": "descriptive_only",
                "coherence_score": 0.81,
                "dissent_ratio": 0.2,
                "minority_report": [
                    {
                        "perspective": "critic",
                        "decision": "concern",
                        "confidence": 0.61,
                        "reasoning": "Grounding remains thin.",
                        "evidence": ["docs/MATH_FOUNDATIONS.md"],
                    }
                ],
                "confidence_decomposition": {
                    "calibration_status": "descriptive_only",
                    "adversarial_posture": "survived_dissent",
                },
            }
        )
        assert summary["has_minority_report"] is True
        assert "Descriptive agreement record only" in summary["realism_note"]
