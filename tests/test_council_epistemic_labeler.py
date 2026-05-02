"""Tests for tonesoul.council.epistemic_labeler — pure helpers and EpistemicLabeler."""

from __future__ import annotations

import pytest

from tonesoul.council.epistemic_labeler import (
    EpistemicLabel,
    EpistemicLabeler,
    _contains_any,
    _extract_evidence_refs,
    _normalize_for_match,
)

# ── _normalize_for_match ──────────────────────────────────────────────────────


class TestNormalizeForMatch:
    def test_lowercases_ascii(self):
        assert _normalize_for_match("HELLO WORLD") == "hello world"

    def test_nfkc_normalization(self):
        # Full-width "Ａ" → "A" → lowered "a"
        assert _normalize_for_match("Ａ") == "a"

    def test_preserves_chinese(self):
        result = _normalize_for_match("自由意志")
        assert "自由意志" in result

    def test_empty_string(self):
        assert _normalize_for_match("") == ""


# ── _contains_any ─────────────────────────────────────────────────────────────


class TestContainsAny:
    def test_returns_true_when_marker_present(self):
        assert _contains_any("hello world", ["world", "foo"]) is True

    def test_returns_false_when_no_marker(self):
        assert _contains_any("hello", ["xyz", "abc"]) is False

    def test_empty_markers(self):
        assert _contains_any("hello", []) is False

    def test_empty_text(self):
        assert _contains_any("", ["x"]) is False


# ── _extract_evidence_refs ────────────────────────────────────────────────────


class TestExtractEvidenceRefs:
    def test_string_value(self):
        refs = _extract_evidence_refs({"evidence_refs": "doc:123"})
        assert "doc:123" in refs

    def test_list_of_strings(self):
        refs = _extract_evidence_refs({"retrieval_hits": ["ref1", "ref2"]})
        assert "ref1" in refs
        assert "ref2" in refs

    def test_list_of_dicts_with_id(self):
        refs = _extract_evidence_refs({"tool_calls": [{"id": "tool-001"}]})
        assert "tool-001" in refs

    def test_list_of_dicts_with_ref(self):
        refs = _extract_evidence_refs({"citations": [{"ref": "cite-001"}]})
        assert "cite-001" in refs

    def test_dict_value(self):
        refs = _extract_evidence_refs({"rag_results": {"id": "rag-001"}})
        assert "rag-001" in refs

    def test_empty_context(self):
        assert _extract_evidence_refs({}) == []

    def test_none_value_skipped(self):
        refs = _extract_evidence_refs({"evidence_refs": None})
        assert refs == []

    def test_multiple_keys_combined(self):
        refs = _extract_evidence_refs(
            {
                "evidence_refs": "ref1",
                "citations": ["cite1"],
            }
        )
        assert len(refs) == 2


# ── EpistemicLabel validation ─────────────────────────────────────────────────


class TestEpistemicLabel:
    def _make(self, **kw) -> EpistemicLabel:
        defaults = {
            "status": "generated",
            "source_weight": "inferred",
            "confidence_band": "low",
            "refusal_eligible": False,
            "framing_required": False,
            "framing_present": None,
        }
        defaults.update(kw)
        return EpistemicLabel(**defaults)

    def test_valid_label_created(self):
        label = self._make()
        assert label.status == "generated"

    def test_invalid_status_raises(self):
        with pytest.raises(ValueError, match="status must be"):
            self._make(status="unknown_status")

    def test_invalid_source_weight_raises(self):
        with pytest.raises(ValueError, match="source_weight must be"):
            self._make(source_weight="super_primary")

    def test_invalid_confidence_band_raises(self):
        with pytest.raises(ValueError, match="confidence_band must be"):
            self._make(confidence_band="very_high")

    def test_framing_required_but_none_raises(self):
        with pytest.raises(ValueError, match="framing_present must be bool"):
            self._make(
                status="speculative_metaphysical",
                framing_required=True,
                framing_present=None,
            )

    def test_framing_not_required_framing_present_none_ok(self):
        label = self._make(framing_required=False, framing_present=None)
        assert label.framing_present is None

    def test_to_dict_has_all_keys(self):
        d = self._make().to_dict()
        assert set(d.keys()) == {
            "status",
            "source_weight",
            "confidence_band",
            "refusal_eligible",
            "framing_required",
            "framing_present",
            "evidence_refs",
            "notes",
        }

    def test_to_dict_evidence_refs_is_list(self):
        label = self._make()
        label.evidence_refs = ["ref1"]
        d = label.to_dict()
        assert d["evidence_refs"] == ["ref1"]


# ── EpistemicLabeler static helpers ───────────────────────────────────────────


class TestIsMetaphysical:
    def test_detects_english_marker(self):
        assert EpistemicLabeler._is_metaphysical("what is the meaning of life?", "") is True

    def test_detects_chinese_marker(self):
        assert EpistemicLabeler._is_metaphysical("談談自由意志的問題", "") is True

    def test_in_intent_also_detected(self):
        assert EpistemicLabeler._is_metaphysical("", "does god exist") is True

    def test_plain_text_not_metaphysical(self):
        assert EpistemicLabeler._is_metaphysical("the weather is nice today", "") is False

    def test_free_will_detected(self):
        assert EpistemicLabeler._is_metaphysical("discussing free will", "") is True


class TestHasFraming:
    def test_english_framing_marker(self):
        assert EpistemicLabeler._has_framing("this is one of several possibilities") is True

    def test_chinese_framing_marker(self):
        assert EpistemicLabeler._has_framing("這是其中一種可能的解釋") is True

    def test_no_framing_returns_false(self):
        assert EpistemicLabeler._has_framing("definitely the answer is X") is False

    def test_not_a_discovered_fact_marker(self):
        assert EpistemicLabeler._has_framing("this is not a discovered fact") is True


class TestLooksDistilled:
    def test_number_triggers_distilled(self):
        assert EpistemicLabeler._looks_distilled("there are 42 known species") is True

    def test_according_to_marker(self):
        assert EpistemicLabeler._looks_distilled("according to research...") is True

    def test_pure_creative_text_not_distilled(self):
        assert EpistemicLabeler._looks_distilled("the dragon soared through mystic clouds") is False

    def test_study_keyword(self):
        assert EpistemicLabeler._looks_distilled("a recent study showed that...") is True

    def test_chinese_research_marker(self):
        assert EpistemicLabeler._looks_distilled("根據最新的研究結果") is True


class TestIsRefusalEligible:
    def test_speculative_without_framing_eligible(self):
        assert (
            EpistemicLabeler._is_refusal_eligible(
                status="speculative_metaphysical",
                framing_present=False,
                normalized_intent="",
            )
            is True
        )

    def test_speculative_with_framing_not_eligible(self):
        assert (
            EpistemicLabeler._is_refusal_eligible(
                status="speculative_metaphysical",
                framing_present=True,
                normalized_intent="",
            )
            is False
        )

    def test_generated_medical_intent_eligible(self):
        assert (
            EpistemicLabeler._is_refusal_eligible(
                status="generated",
                framing_present=None,
                normalized_intent="diagnose my condition please",
            )
            is True
        )

    def test_generated_legal_intent_eligible(self):
        assert (
            EpistemicLabeler._is_refusal_eligible(
                status="generated",
                framing_present=None,
                normalized_intent="legal advice for my lawsuit",
            )
            is True
        )

    def test_retrieved_not_eligible(self):
        assert (
            EpistemicLabeler._is_refusal_eligible(
                status="retrieved",
                framing_present=None,
                normalized_intent="what is the weather",
            )
            is False
        )

    def test_distilled_normal_intent_not_eligible(self):
        assert (
            EpistemicLabeler._is_refusal_eligible(
                status="distilled",
                framing_present=None,
                normalized_intent="tell me about history",
            )
            is False
        )


# ── EpistemicLabeler.label integration ───────────────────────────────────────


class TestEpistemicLabelerLabel:
    def setup_method(self):
        self.labeler = EpistemicLabeler()

    def test_retrieved_when_evidence_present(self):
        label = self.labeler.label(
            "Here is the answer.",
            context={"evidence_refs": ["doc:1", "doc:2"]},
        )
        assert label.status == "retrieved"
        assert label.source_weight == "primary"
        assert label.confidence_band == "high"
        assert len(label.evidence_refs) == 2

    def test_speculative_metaphysical_wins_over_evidence(self):
        label = self.labeler.label(
            "The meaning of life is subjective.",
            context={"evidence_refs": ["doc:1"]},
        )
        assert label.status == "speculative_metaphysical"
        assert label.framing_required is True
        assert isinstance(label.framing_present, bool)

    def test_speculative_metaphysical_with_framing_present(self):
        label = self.labeler.label(
            "This is one of several structurally plausible possibilities, not a discovered fact.",
            user_intent="what is the meaning of consciousness",
        )
        assert label.status == "speculative_metaphysical"
        assert label.framing_present is True
        assert label.refusal_eligible is False

    def test_speculative_without_framing_refusal_eligible(self):
        label = self.labeler.label(
            "The soul is eternal and exists after death.",
            user_intent="what happens after death",
        )
        assert label.status == "speculative_metaphysical"
        assert label.framing_present is False
        assert label.refusal_eligible is True

    def test_distilled_with_numbers(self):
        label = self.labeler.label("According to research in 2022, 75% of users prefer X.")
        assert label.status == "distilled"
        assert label.source_weight == "secondary"
        assert label.confidence_band == "medium"

    def test_generated_without_evidence_or_facts(self):
        label = self.labeler.label("Here is a creative story about dragons and magic.")
        assert label.status == "generated"
        assert label.source_weight == "inferred"
        assert label.confidence_band == "low"

    def test_generated_high_stakes_medical_refusal_eligible(self):
        label = self.labeler.label(
            "You should take medication X.",
            user_intent="please diagnose my symptoms",
        )
        assert label.status == "generated"
        assert label.refusal_eligible is True

    def test_empty_draft_returns_generated(self):
        label = self.labeler.label("")
        assert label.status == "generated"

    def test_notes_populated(self):
        label = self.labeler.label("Simple statement.")
        assert isinstance(label.notes, str)
        assert len(label.notes) > 0
