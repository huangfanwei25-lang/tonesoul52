"""
Tests for YUHUN Shadow Document — 影子文件格式驗證
"""

import json

from tonesoul.yuhun.shadow_doc import (
    OutputMode,
    RoutingDecision,
    ShadowDocument,
)


class TestShadowDocCreation:
    def test_create_generates_uuid(self):
        doc = ShadowDocument.create("test input")
        assert len(doc.session_id) > 10

    def test_create_sets_timestamp(self):
        doc = ShadowDocument.create("test")
        assert "T" in doc.session_id or len(doc.timestamp) > 10

    def test_create_preserves_raw_input(self):
        doc = ShadowDocument.create("my raw input")
        assert doc.intent_frame.raw_input == "my raw input"

    def test_lifecycle_defaults(self):
        doc = ShadowDocument.create("test")
        assert doc.lifecycle.kv_cache_flushed is True
        assert doc.lifecycle.retrievable_for_audit is True
        assert doc.lifecycle.archive_id.startswith("COLD-")


class TestShadowDocSerialization:
    def test_to_dict_is_json_serializable(self):
        doc = ShadowDocument.create(
            raw_input="test",
            reconstructed_intent="detailed intent",
            declarative_goal="goal",
            verification_loop="verification",
        )
        d = doc.to_dict()
        # 應該可以被 JSON 序列化
        serialized = json.dumps(d, ensure_ascii=False)
        assert "session_id" in serialized

    def test_to_dict_contains_required_keys(self):
        doc = ShadowDocument.create("test")
        d = doc.to_dict()
        required_keys = [
            "session_id",
            "timestamp",
            "intent_frame",
            "tension_metrics",
            "legal_profile",
            "lifecycle",
        ]
        for key in required_keys:
            assert key in d, f"缺少必要欄位：{key}"

    def test_to_empath_subset(self):
        doc = ShadowDocument.create("test", "intent", "goal", "verify")
        empath = doc.to_empath()
        # empath 格式應包含關鍵欄位
        assert "session_id" in empath
        assert "tension" in empath
        assert "legal_gap" in empath

    def test_enums_serialized_as_strings(self):
        doc = ShadowDocument.create("test")
        doc.tension_metrics.routing_decision = RoutingDecision.COUNCIL_PATH
        doc.tension_metrics.output_mode = OutputMode.DUAL_TRACK
        d = doc.to_dict()
        assert d["tension_metrics"]["routing_decision"] == "COUNCIL_PATH"
        assert d["tension_metrics"]["output_mode"] == "DUAL_TRACK"


class TestShadowDocArchiveId:
    def test_each_doc_has_unique_archive_id(self):
        docs = [ShadowDocument.create("test") for _ in range(5)]
        archive_ids = {doc.lifecycle.archive_id for doc in docs}
        assert len(archive_ids) == 5  # 全部唯一

    def test_archive_id_format(self):
        doc = ShadowDocument.create("test")
        aid = doc.lifecycle.archive_id
        assert aid.startswith("COLD-")
        # COLD- 後面應該有 8 個十六進位字元（大寫）
        suffix = aid[5:]
        assert len(suffix) == 8
        assert suffix == suffix.upper()
