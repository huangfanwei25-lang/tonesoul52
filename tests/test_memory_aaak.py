"""Tests for tonesoul.memory.aaak — AAAK session compaction."""

from __future__ import annotations

from tonesoul.memory.aaak import (
    AAAKRecord,
    compress_to_aaak,
    format_handoff_block,
    merge_records,
)

# ── AAAKRecord ────────────────────────────────────────────────────────────────


class TestAAAKRecord:
    def test_is_empty_when_all_quadrants_empty(self):
        record = AAAKRecord(anchors=[], arcs=[], anomalies=[], keys=[])
        assert record.is_empty() is True

    def test_not_empty_when_any_quadrant_has_items(self):
        record = AAAKRecord(anchors=["vow: be honest"], arcs=[], anomalies=[], keys=[])
        assert record.is_empty() is False

    def test_to_dict_has_format_field(self):
        record = AAAKRecord(anchors=[], arcs=[], anomalies=[], keys=[])
        d = record.to_dict()
        assert d["format"] == "aaak_v1"

    def test_to_dict_has_all_quadrants(self):
        record = AAAKRecord(anchors=["a"], arcs=["b"], anomalies=["c"], keys=["d"])
        d = record.to_dict()
        assert d["anchors"] == ["a"]
        assert d["arcs"] == ["b"]
        assert d["anomalies"] == ["c"]
        assert d["keys"] == ["d"]

    def test_session_and_agent_id_propagated(self):
        record = AAAKRecord(
            anchors=[],
            arcs=[],
            anomalies=[],
            keys=[],
            session_id="sess-1",
            agent_id="claude-sonnet-4-6",
        )
        d = record.to_dict()
        assert d["session_id"] == "sess-1"
        assert d["agent_id"] == "claude-sonnet-4-6"

    def test_compressed_at_is_set(self):
        record = AAAKRecord(anchors=[], arcs=[], anomalies=[], keys=[])
        assert record.compressed_at  # non-empty


# ── compress_to_aaak ─────────────────────────────────────────────────────────


class TestCompressToAaak:
    def _data(self, **kwargs):
        base = {
            "session_id": "s1",
            "agent": "test-agent",
        }
        base.update(kwargs)
        return base

    def test_returns_aaak_record(self):
        result = compress_to_aaak({})
        assert isinstance(result, AAAKRecord)

    def test_empty_data_produces_empty_record(self):
        result = compress_to_aaak({})
        assert result.is_empty()

    def test_session_id_extracted_from_data(self):
        result = compress_to_aaak({"session_id": "abc"})
        assert result.session_id == "abc"

    def test_session_id_overridden_by_kwarg(self):
        result = compress_to_aaak({"session_id": "from_data"}, session_id="from_kwarg")
        assert result.session_id == "from_kwarg"

    def test_agent_extracted_from_data(self):
        result = compress_to_aaak({"agent": "my-agent"})
        assert result.agent_id == "my-agent"

    # ── Anchors extraction ──

    def test_anchors_from_active_vows_dict(self):
        data = {"active_vows": [{"text": "do not hallucinate"}]}
        result = compress_to_aaak(data)
        assert any("do not hallucinate" in a for a in result.anchors)

    def test_anchors_from_active_vows_str(self):
        data = {"active_vows": ["be honest"]}
        result = compress_to_aaak(data)
        assert any("be honest" in a for a in result.anchors)

    def test_anchors_from_axioms_invoked(self):
        data = {"axioms_invoked": ["axiom-4"]}
        result = compress_to_aaak(data)
        assert any("axiom-4" in a for a in result.anchors)

    def test_anchors_from_approved_council_verdicts(self):
        data = {"council_verdicts": [{"verdict": "approve"}, {"verdict": "approve"}]}
        result = compress_to_aaak(data)
        assert any("2" in a for a in result.anchors)

    def test_anchors_bounded_at_four(self):
        data = {"active_vows": [{"text": f"vow {i}"} for i in range(10)]}
        result = compress_to_aaak(data)
        assert len(result.anchors) <= 4

    # ── Arcs extraction ──

    def test_arcs_from_key_decisions(self):
        data = {"key_decisions": ["decided to refactor the pipeline"]}
        result = compress_to_aaak(data)
        assert any("refactor" in a for a in result.arcs)

    def test_arcs_from_drift_events_dict(self):
        data = {"drift_events": [{"step": 7, "reason": "high tension in council"}]}
        result = compress_to_aaak(data)
        assert any("step 7" in a for a in result.arcs)

    def test_arcs_from_stance_shift(self):
        data = {"stance_shift": "moved from cautious to engaged"}
        result = compress_to_aaak(data)
        assert any("stance shift" in a for a in result.arcs)

    def test_arcs_bounded_at_four(self):
        data = {"key_decisions": [f"decision {i}" for i in range(10)]}
        result = compress_to_aaak(data)
        assert len(result.arcs) <= 4

    # ── Anomalies extraction ──

    def test_anomalies_from_unresolved_tension_events(self):
        data = {"tension_events": [{"topic": "axiom violation", "severity": 0.8}]}
        result = compress_to_aaak(data)
        assert any("axiom violation" in a for a in result.anomalies)

    def test_resolved_tension_events_not_in_anomalies(self):
        data = {"tension_events": [{"topic": "fixed issue", "resolution": "done", "severity": 0.5}]}
        result = compress_to_aaak(data)
        assert not any("fixed issue" in a for a in result.anomalies)

    def test_anomalies_from_block_verdict(self):
        data = {"council_verdicts": [{"verdict": "block", "summary": "axiom violated"}]}
        result = compress_to_aaak(data)
        assert any("block" in a for a in result.anomalies)

    def test_anomalies_from_carry_forward(self):
        data = {"carry_forward": ["unresolved migration issue"]}
        result = compress_to_aaak(data)
        assert any("unresolved migration" in a for a in result.anomalies)

    def test_anomalies_bounded_at_four(self):
        data = {"tension_events": [{"topic": f"t{i}", "severity": 0.5} for i in range(10)]}
        result = compress_to_aaak(data)
        assert len(result.anomalies) <= 4

    # ── Keys extraction ──

    def test_keys_from_explicit_keys_field(self):
        data = {"keys": ["check the vow system before deploying"]}
        result = compress_to_aaak(data)
        assert any("check the vow system" in k for k in result.keys)

    def test_keys_from_task_track_hint(self):
        data = {"task_track_hint": "implement freshness tracking"}
        result = compress_to_aaak(data)
        assert any("freshness" in k for k in result.keys)

    def test_keys_from_path(self):
        data = {"path": "tonesoul/memory/aaak.py"}
        result = compress_to_aaak(data)
        assert any("tonesoul/memory" in k for k in result.keys)

    def test_keys_from_summary(self):
        data = {"summary": "completed phase 1 of data layer"}
        result = compress_to_aaak(data)
        assert any("phase 1" in k for k in result.keys)

    def test_keys_bounded_at_four(self):
        data = {"keys": [f"key {i}" for i in range(10)]}
        result = compress_to_aaak(data)
        assert len(result.keys) <= 4

    # ── Long text truncation ──

    def test_long_text_items_are_truncated(self):
        long = "x" * 300
        data = {"key_decisions": [long]}
        result = compress_to_aaak(data)
        for arc in result.arcs:
            assert len(arc) <= 125  # 120 + "…"

    def test_duplicate_items_are_deduplicated(self):
        data = {"key_decisions": ["same decision", "same decision", "same decision"]}
        result = compress_to_aaak(data)
        assert result.arcs.count("same decision") == 1


# ── format_handoff_block ─────────────────────────────────────────────────────


class TestFormatHandoffBlock:
    def _record(self):
        return AAAKRecord(
            anchors=["vow: be honest"],
            arcs=["decided to refactor"],
            anomalies=["tension: axiom-4 invocation"],
            keys=["next: run tests"],
            session_id="s1",
            agent_id="claude",
        )

    def test_output_is_string(self):
        assert isinstance(format_handoff_block(self._record()), str)

    def test_output_has_five_lines(self):
        block = format_handoff_block(self._record())
        assert len(block.splitlines()) == 5

    def test_first_line_contains_aaak_marker(self):
        block = format_handoff_block(self._record())
        assert "[AAAK]" in block.splitlines()[0]

    def test_first_line_contains_agent_id(self):
        block = format_handoff_block(self._record())
        assert "claude" in block.splitlines()[0]

    def test_anchors_line_present(self):
        block = format_handoff_block(self._record())
        assert "vow: be honest" in block

    def test_empty_quadrant_shows_dash(self):
        record = AAAKRecord(anchors=[], arcs=[], anomalies=[], keys=["something"])
        block = format_handoff_block(record)
        lines = block.splitlines()
        assert "—" in lines[1]  # anchors line

    def test_multiple_items_separated_by_dot(self):
        record = AAAKRecord(anchors=["a1", "a2"], arcs=[], anomalies=[], keys=[])
        block = format_handoff_block(record)
        assert "a1 · a2" in block


# ── merge_records ─────────────────────────────────────────────────────────────


class TestMergeRecords:
    def test_merged_anchors_contain_items_from_both(self):
        older = AAAKRecord(anchors=["a1"], arcs=[], anomalies=[], keys=[])
        newer = AAAKRecord(anchors=["a2"], arcs=[], anomalies=[], keys=[])
        merged = merge_records(older, newer)
        assert "a1" in merged.anchors
        assert "a2" in merged.anchors

    def test_merged_session_id_is_from_newer(self):
        older = AAAKRecord(anchors=[], arcs=[], anomalies=[], keys=[], session_id="old")
        newer = AAAKRecord(anchors=[], arcs=[], anomalies=[], keys=[], session_id="new")
        merged = merge_records(older, newer)
        assert merged.session_id == "new"

    def test_merged_items_bounded_at_four(self):
        older = AAAKRecord(anchors=["a", "b", "c"], arcs=[], anomalies=[], keys=[])
        newer = AAAKRecord(anchors=["d", "e", "f"], arcs=[], anomalies=[], keys=[])
        merged = merge_records(older, newer)
        assert len(merged.anchors) <= 4

    def test_merge_deduplicates_items(self):
        older = AAAKRecord(anchors=["shared"], arcs=[], anomalies=[], keys=[])
        newer = AAAKRecord(anchors=["shared"], arcs=[], anomalies=[], keys=[])
        merged = merge_records(older, newer)
        assert merged.anchors.count("shared") == 1

    def test_older_session_id_used_when_newer_is_empty(self):
        older = AAAKRecord(anchors=[], arcs=[], anomalies=[], keys=[], session_id="old")
        newer = AAAKRecord(anchors=[], arcs=[], anomalies=[], keys=[], session_id="")
        merged = merge_records(older, newer)
        assert merged.session_id == "old"
