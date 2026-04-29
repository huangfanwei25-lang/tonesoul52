"""Tests for tonesoul.yuhun.shadow_doc — YUHUN shadow document."""

from __future__ import annotations

from tonesoul.yuhun.shadow_doc import (
    BlockerSeverity,
    L1Blocker,
    L2Opportunity,
    Lifecycle,
    RoutingDecision,
    SafetyVerdict,
    ShadowDocument,
    TrajectoryDigest,
)


class TestShadowDocumentCreate:
    def test_create_returns_shadow_document(self):
        doc = ShadowDocument.create("test input")
        assert isinstance(doc, ShadowDocument)

    def test_create_sets_raw_input(self):
        doc = ShadowDocument.create("some query")
        assert doc.intent_frame.raw_input == "some query"

    def test_create_assigns_uuid_session_id(self):
        doc = ShadowDocument.create("test")
        assert len(doc.session_id) == 36  # UUID4 format
        assert doc.session_id.count("-") == 4

    def test_create_two_docs_have_different_session_ids(self):
        doc1 = ShadowDocument.create("a")
        doc2 = ShadowDocument.create("b")
        assert doc1.session_id != doc2.session_id

    def test_create_timestamp_is_set(self):
        doc = ShadowDocument.create("test")
        assert "T" in doc.timestamp  # ISO format

    def test_create_council_outputs_is_empty(self):
        doc = ShadowDocument.create("test")
        assert doc.council_outputs == {}

    def test_create_tension_defaults_to_fast_path(self):
        doc = ShadowDocument.create("test")
        assert doc.tension_metrics.routing_decision == RoutingDecision.FAST_PATH
        assert doc.tension_metrics.semantic_distance == 0.0

    def test_create_lifecycle_is_archive_ready(self):
        doc = ShadowDocument.create("test")
        assert doc.lifecycle.retrievable_for_audit is True
        assert doc.lifecycle.archive_id.startswith("COLD-")

    def test_create_with_all_intent_fields(self):
        doc = ShadowDocument.create(
            raw_input="raw",
            reconstructed_intent="intent",
            declarative_goal="goal",
            verification_loop="loop",
        )
        assert doc.intent_frame.reconstructed_intent == "intent"
        assert doc.intent_frame.declarative_goal == "goal"
        assert doc.intent_frame.verification_loop == "loop"


class TestShadowDocumentToDict:
    def test_to_dict_returns_plain_dict(self):
        doc = ShadowDocument.create("test")
        d = doc.to_dict()
        assert isinstance(d, dict)

    def test_to_dict_enums_serialized_as_strings(self):
        doc = ShadowDocument.create("test")
        d = doc.to_dict()
        assert d["tension_metrics"]["routing_decision"] == "FAST_PATH"
        assert d["tension_metrics"]["output_mode"] == "SINGLE_TRACK"

    def test_to_dict_contains_session_id(self):
        doc = ShadowDocument.create("test")
        d = doc.to_dict()
        assert d["session_id"] == doc.session_id

    def test_to_dict_nested_intent_frame(self):
        doc = ShadowDocument.create("my query")
        d = doc.to_dict()
        assert d["intent_frame"]["raw_input"] == "my query"

    def test_to_dict_lifecycle_archive_id_preserved(self):
        doc = ShadowDocument.create("test")
        d = doc.to_dict()
        assert d["lifecycle"]["archive_id"] == doc.lifecycle.archive_id


class TestShadowDocumentToEmpath:
    def test_to_empath_contains_session_id(self):
        doc = ShadowDocument.create("test")
        e = doc.to_empath()
        assert e["session_id"] == doc.session_id

    def test_to_empath_does_not_contain_lifecycle(self):
        doc = ShadowDocument.create("test")
        e = doc.to_empath()
        assert "lifecycle" not in e

    def test_to_empath_contains_tension_fields(self):
        doc = ShadowDocument.create("test")
        e = doc.to_empath()
        assert "semantic_distance" in e["tension"]
        assert "output_mode" in e["tension"]

    def test_to_empath_output_mode_is_string(self):
        doc = ShadowDocument.create("test")
        e = doc.to_empath()
        assert isinstance(e["tension"]["output_mode"], str)

    def test_to_empath_intent_frame_contains_goal_and_loop(self):
        doc = ShadowDocument.create(
            "test", declarative_goal="achieve X", verification_loop="check Y"
        )
        e = doc.to_empath()
        assert e["intent_frame"]["declarative_goal"] == "achieve X"
        assert e["intent_frame"]["verification_loop"] == "check Y"

    def test_to_empath_logician_summary_none_when_absent(self):
        doc = ShadowDocument.create("test")
        e = doc.to_empath()
        assert e["logician_summary"] is None

    def test_to_empath_safety_verdict_none_when_absent(self):
        doc = ShadowDocument.create("test")
        e = doc.to_empath()
        assert e["safety_verdict"] is None

    def test_to_empath_trajectory_contains_step_count(self):
        doc = ShadowDocument.create("test")
        e = doc.to_empath()
        assert e["trajectory"]["step_count"] == 0

    def test_to_empath_legal_gap_is_false_by_default(self):
        doc = ShadowDocument.create("test")
        assert doc.to_empath()["legal_gap"] is False


class TestShadowDocumentSave:
    def test_save_creates_file_in_directory(self, tmp_path):
        doc = ShadowDocument.create("test")
        archive_id = doc.save(cold_storage_dir=str(tmp_path))
        assert archive_id == doc.lifecycle.archive_id
        assert (tmp_path / f"{archive_id}.json").exists()

    def test_save_returns_archive_id(self, tmp_path):
        doc = ShadowDocument.create("test")
        result = doc.save(cold_storage_dir=str(tmp_path))
        assert result.startswith("COLD-")

    def test_saved_file_is_valid_json(self, tmp_path):
        import json

        doc = ShadowDocument.create("test input")
        archive_id = doc.save(cold_storage_dir=str(tmp_path))
        content = json.loads((tmp_path / f"{archive_id}.json").read_text(encoding="utf-8"))
        assert content["session_id"] == doc.session_id


class TestShadowDocumentComponents:
    def test_lifecycle_archive_id_starts_with_cold(self):
        lc = Lifecycle()
        assert lc.archive_id.startswith("COLD-")

    def test_trajectory_digest_defaults(self):
        td = TrajectoryDigest()
        assert td.step_count == 0
        assert td.tool_calls == []
        assert td.key_decisions == []
        assert td.compression_ratio == 0.0

    def test_l1_blocker_hard_severity(self):
        blocker = L1Blocker(
            type="legal",
            description="not allowed",
            source="regulation X",
            severity=BlockerSeverity.HARD,
        )
        assert blocker.severity == BlockerSeverity.HARD

    def test_l2_opportunity_defaults(self):
        opp = L2Opportunity(type="framework_shift", description="change approach")
        assert opp.confidence_level == "L2_THEORETICAL"
        assert opp.prerequisite_changes == []
        assert opp.analogy is None

    def test_safety_verdict_enum_values(self):
        assert SafetyVerdict.PASS.value == "PASS"
        assert SafetyVerdict.FLAG.value == "FLAG"
        assert SafetyVerdict.BLOCK.value == "BLOCK"
