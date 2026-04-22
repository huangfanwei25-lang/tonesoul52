"""Tests for tonesoul.memory.reviewed_promotion — pure helpers and build functions."""
from __future__ import annotations

import pytest

from tonesoul.memory.reviewed_promotion import (
    _merge_source_record_ids,
    _payload_excerpt,
    _utcnow_iso,
    build_reviewed_promotion_decision,
    build_reviewed_promotion_payload,
    infer_subjectivity_layer,
)
from tonesoul.schemas import SubjectivityLayer, SubjectivityPromotionStatus


# ── _utcnow_iso ───────────────────────────────────────────────────────────────

class TestUtcnowIso:
    def test_returns_string(self):
        assert isinstance(_utcnow_iso(), str)

    def test_ends_with_z(self):
        assert _utcnow_iso().endswith("Z")

    def test_parseable(self):
        from datetime import datetime
        ts = _utcnow_iso()
        datetime.fromisoformat(ts.replace("Z", "+00:00"))


# ── _payload_excerpt ──────────────────────────────────────────────────────────

class TestPayloadExcerpt:
    def test_prefers_summary(self):
        assert _payload_excerpt({"summary": "s1", "title": "t1"}) == "s1"

    def test_falls_back_to_title(self):
        assert _payload_excerpt({"title": "T1"}) == "T1"

    def test_falls_back_to_text(self):
        assert _payload_excerpt({"text": "body"}) == "body"

    def test_empty_dict_returns_empty(self):
        assert _payload_excerpt({}) == ""

    def test_truncates_to_160(self):
        result = _payload_excerpt({"summary": "x" * 200})
        assert len(result) == 160

    def test_skips_empty_string_keys(self):
        result = _payload_excerpt({"summary": "", "title": "T"})
        assert result == "T"


# ── _merge_source_record_ids ──────────────────────────────────────────────────

class TestMergeSourceRecordIds:
    def test_merges_both_sources(self):
        result = _merge_source_record_ids(
            source_record_ids=["a", "b"],
            payload_source_ids=["c"],
        )
        assert result == ["a", "b", "c"]

    def test_deduplicates(self):
        result = _merge_source_record_ids(
            source_record_ids=["a", "b"],
            payload_source_ids=["b", "c"],
        )
        assert result == ["a", "b", "c"]

    def test_none_source_record_ids(self):
        result = _merge_source_record_ids(
            source_record_ids=None,
            payload_source_ids=["x"],
        )
        assert result == ["x"]

    def test_non_list_payload_ids_ignored(self):
        result = _merge_source_record_ids(
            source_record_ids=["a"],
            payload_source_ids="not-a-list",
        )
        assert result == ["a"]

    def test_empty_strings_filtered(self):
        result = _merge_source_record_ids(
            source_record_ids=["", "  ", "a"],
            payload_source_ids=[],
        )
        assert result == ["a"]

    def test_both_empty_returns_empty(self):
        result = _merge_source_record_ids(
            source_record_ids=[],
            payload_source_ids=[],
        )
        assert result == []


# ── infer_subjectivity_layer ──────────────────────────────────────────────────

class TestInferSubjectivityLayer:
    def test_existing_layer_passthrough(self):
        result = infer_subjectivity_layer({"subjectivity_layer": "vow"}, target_layer="working")
        assert result == "vow"

    def test_friction_score_gives_tension(self):
        result = infer_subjectivity_layer({"friction_score": 0.8}, target_layer="working")
        assert result == SubjectivityLayer.TENSION.value

    def test_dream_cycle_id_gives_tension(self):
        result = infer_subjectivity_layer({"dream_cycle_id": "d123"}, target_layer="working")
        assert result == SubjectivityLayer.TENSION.value

    def test_council_reason_gives_tension(self):
        result = infer_subjectivity_layer({"council_reason": "disagreement"}, target_layer="working")
        assert result == SubjectivityLayer.TENSION.value

    def test_conflict_keyword_gives_tension(self):
        result = infer_subjectivity_layer({"text": "there was a conflict here"}, target_layer="working")
        assert result == SubjectivityLayer.TENSION.value

    def test_friction_keyword_gives_tension(self):
        result = infer_subjectivity_layer({"summary": "friction between views"}, target_layer="working")
        assert result == SubjectivityLayer.TENSION.value

    def test_experiential_target_gives_meaning(self):
        result = infer_subjectivity_layer({}, target_layer="experiential")
        assert result == SubjectivityLayer.MEANING.value

    def test_default_gives_event(self):
        result = infer_subjectivity_layer({}, target_layer="working")
        assert result == SubjectivityLayer.EVENT.value


# ── build_reviewed_promotion_decision ─────────────────────────────────────────

def _tension_payload(**kw) -> dict:
    defaults = {
        "text": "This reveals a tension",
        "friction_score": 0.7,
        "layer": "working",
    }
    defaults.update(kw)
    return defaults


class TestBuildReviewedPromotionDecision:
    def test_basic_decision(self):
        decision = build_reviewed_promotion_decision(
            _tension_payload(),
            review_actor={"actor_id": "human-1", "actor_type": "human"},
            review_basis="evidence of sustained tension",
        )
        assert decision.review_basis == "evidence of sustained tension"
        assert decision.status.value == "reviewed"

    def test_string_review_actor_coerced(self):
        decision = build_reviewed_promotion_decision(
            _tension_payload(),
            review_actor="human-operator",
            review_basis="confirmed tension",
        )
        assert decision.review_actor.actor_id == "human-operator"

    def test_non_dict_payload_raises(self):
        with pytest.raises(TypeError, match="expects a dict payload"):
            build_reviewed_promotion_decision(
                "not-a-dict",
                review_actor="human",
                review_basis="reason",
            )

    def test_empty_review_basis_raises(self):
        with pytest.raises(ValueError, match="review_basis is required"):
            build_reviewed_promotion_decision(
                _tension_payload(),
                review_actor="human",
                review_basis="",
            )

    def test_non_tension_payload_raises(self):
        with pytest.raises(ValueError, match="tension candidate"):
            build_reviewed_promotion_decision(
                {"text": "clean stable memory entry"},
                review_actor="human",
                review_basis="reason",
            )

    def test_custom_reviewed_at(self):
        decision = build_reviewed_promotion_decision(
            _tension_payload(),
            review_actor="human",
            review_basis="reason",
            reviewed_at="2026-01-01T00:00:00Z",
        )
        assert decision.reviewed_at == "2026-01-01T00:00:00Z"

    def test_source_record_ids_merged(self):
        decision = build_reviewed_promotion_decision(
            _tension_payload(**{"source_record_ids": ["id-a"]}),
            review_actor="human",
            review_basis="reason",
            source_record_ids=["id-b"],
        )
        ids = list(decision.source_record_ids)
        assert "id-b" in ids
        assert "id-a" in ids

    def test_non_vow_target_raises(self):
        with pytest.raises(ValueError, match="only supports tension -> vow"):
            build_reviewed_promotion_decision(
                _tension_payload(),
                review_actor="human",
                review_basis="reason",
                target_subjectivity_layer="meaning",
            )


# ── build_reviewed_promotion_payload ──────────────────────────────────────────

class TestBuildReviewedPromotionPayload:
    def _decision(self, **kw):
        defaults = {
            "status": "reviewed",
            "promotion_source": "manual_review",
            "review_actor": {"actor_id": "human-1", "actor_type": "human"},
            "source_subjectivity_layer": "tension",
            "target_subjectivity_layer": "vow",
            "reviewed_at": "2026-01-01T00:00:00Z",
            "review_basis": "confirmed tension",
            "source_record_ids": [],
        }
        defaults.update(kw)
        from tonesoul.schemas import ReviewedPromotionDecision
        return ReviewedPromotionDecision.model_validate(defaults)

    def test_sets_layer_to_factual(self):
        payload = build_reviewed_promotion_payload(
            _tension_payload(),
            decision=self._decision(),
        )
        assert payload["layer"] == "factual"

    def test_sets_subjectivity_layer_to_vow(self):
        payload = build_reviewed_promotion_payload(
            _tension_payload(),
            decision=self._decision(),
        )
        assert payload["subjectivity_layer"] == "vow"

    def test_promotion_gate_added(self):
        payload = build_reviewed_promotion_payload(
            _tension_payload(),
            decision=self._decision(),
        )
        assert "promotion_gate" in payload

    def test_review_basis_preserved(self):
        payload = build_reviewed_promotion_payload(
            _tension_payload(),
            decision=self._decision(review_basis="my_reason"),
        )
        assert payload["review_basis"] == "my_reason"

    def test_non_dict_payload_raises(self):
        with pytest.raises(TypeError, match="expects a dict payload"):
            build_reviewed_promotion_payload("not-a-dict", decision=self._decision())

    def test_rejected_status_raises(self):
        from tonesoul.schemas import ReviewedPromotionDecision
        decision = ReviewedPromotionDecision.model_validate({
            "status": "rejected",
            "promotion_source": "manual_review",
            "review_actor": {"actor_id": "h", "actor_type": "human"},
            "source_subjectivity_layer": "tension",
            "target_subjectivity_layer": "vow",
            "reviewed_at": "2026-01-01T00:00:00Z",
            "review_basis": "reject it",
            "source_record_ids": [],
        })
        with pytest.raises(ValueError, match="non-approved"):
            build_reviewed_promotion_payload(_tension_payload(), decision=decision)

    def test_accepts_dict_decision(self):
        decision_dict = {
            "status": "reviewed",
            "promotion_source": "manual_review",
            "review_actor": {"actor_id": "h", "actor_type": "human"},
            "source_subjectivity_layer": "tension",
            "target_subjectivity_layer": "vow",
            "reviewed_at": "2026-01-01T00:00:00Z",
            "review_basis": "reason",
            "source_record_ids": [],
        }
        payload = build_reviewed_promotion_payload(_tension_payload(), decision=decision_dict)
        assert payload["layer"] == "factual"
