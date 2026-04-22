"""Tests for tonesoul.ystm.audit — YSTM governance audit log builder."""

from __future__ import annotations

from tonesoul.ystm.audit import _slug, build_audit_log
from tonesoul.ystm.schema import UpdateGate, UpdateRecord


class TestSlug:
    def test_alphanumeric_unchanged(self):
        assert _slug("hello") == "hello"

    def test_spaces_replaced_with_underscores(self):
        assert _slug("hello world") == "hello_world"

    def test_special_chars_replaced(self):
        assert _slug("hello-world!plane") == "hello_world_plane"

    def test_uppercase_lowercased(self):
        assert _slug("HelloWorld") == "helloworld"

    def test_empty_string_returns_visual(self):
        assert _slug("") == "visual"

    def test_all_special_chars_returns_visual(self):
        assert _slug("!!!") == "visual"

    def test_leading_trailing_underscores_stripped(self):
        result = _slug("_hello_world_")
        assert not result.startswith("_")
        assert not result.endswith("_")


class TestBuildAuditLog:
    def test_always_includes_e_def_record(self):
        log = build_audit_log({"key": "value"}, [])
        assert len(log.updates) >= 1
        ids = [r.id for r in log.updates]
        assert "update_e_def" in ids

    def test_one_record_per_visual_param(self):
        params = [{"plane": "xy"}, {"plane": "zx"}]
        log = build_audit_log({}, params)
        assert len(log.updates) == 3  # e_def + 2 visual params

    def test_visual_param_id_derived_from_plane(self):
        log = build_audit_log({}, [{"plane": "xy plane"}])
        ids = [r.id for r in log.updates]
        assert any("xy_plane" in id for id in ids)

    def test_visual_param_without_plane_uses_visual(self):
        log = build_audit_log({}, [{"other": "value"}])
        ids = [r.id for r in log.updates]
        assert any("visual" in id for id in ids)

    def test_node_updates_appended(self):
        node_update = UpdateRecord(
            id="node_update_1",
            target="node-001",
            change_type="WHAT_UPDATE",
            before=None,
            after={"text": "new"},
            rationale="test",
            gate=UpdateGate(passed=True, rule_ids=["R1"]),
            timestamp="2026-01-01T00:00:00Z",
            reversible=True,
            vetoable=True,
        )
        log = build_audit_log({}, [], node_updates=[node_update])
        ids = [r.id for r in log.updates]
        assert "node_update_1" in ids

    def test_duplicate_node_update_ids_not_added_twice(self):
        node_update = UpdateRecord(
            id="update_e_def",  # same as the built-in e_def record
            target="node-001",
            change_type="WHAT_UPDATE",
            before=None,
            after={"text": "new"},
            rationale="test",
            gate=UpdateGate(passed=True, rule_ids=["R1"]),
            timestamp="2026-01-01T00:00:00Z",
            reversible=True,
            vetoable=True,
        )
        log = build_audit_log({}, [], node_updates=[node_update])
        # Should only have one record with id "update_e_def"
        count = sum(1 for r in log.updates if r.id == "update_e_def")
        assert count == 1

    def test_generated_at_ends_with_z(self):
        log = build_audit_log({}, [])
        assert log.generated_at.endswith("Z")

    def test_all_records_have_same_timestamp(self):
        params = [{"plane": "xy"}, {"plane": "yz"}]
        log = build_audit_log({"key": 1}, params)
        timestamps = {r.timestamp for r in log.updates}
        assert len(timestamps) == 1

    def test_e_def_record_reversible_and_vetoable(self):
        log = build_audit_log({"key": "val"}, [])
        e_def_records = [r for r in log.updates if r.id == "update_e_def"]
        assert len(e_def_records) == 1
        assert e_def_records[0].reversible is True
        assert e_def_records[0].vetoable is True
