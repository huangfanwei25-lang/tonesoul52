"""Tests for tonesoul.ystm.governance — YSTM governance update validation."""

from __future__ import annotations

from tonesoul.ystm.governance import validate_where_update
from tonesoul.ystm.representation import EmbeddingConfig, build_nodes
from tonesoul.ystm.schema import Where, WhereField, WhereTask, WhereTime


def _where(
    event_index: int = 5,
    mode: str = "analysis",
    domain: str = "governance",
    field_confidence: float = 0.9,
    task_confidence: float = 0.8,
) -> Where:
    return Where(
        where_time=WhereTime(turn_id=1, event_index=event_index),
        where_field=WhereField(mode=mode, submode=None, confidence=field_confidence),
        where_task=WhereTask(domain=domain, subdomain=None, confidence=task_confidence),
    )


def _node():
    return build_nodes(
        [{"text": "hello", "mode": "analysis", "domain": "governance", "turn_id": 1}],
        config=EmbeddingConfig(dims=4),
    )[0]


class TestValidateWhereUpdate:
    def test_valid_update_passes_all_rules(self):
        current = _where(event_index=3)
        proposed = _where(event_index=5)
        gate = validate_where_update(current, proposed)
        assert gate.passed is True
        assert gate.score == 1.0

    def test_decreasing_event_index_fails(self):
        current = _where(event_index=10)
        proposed = _where(event_index=5)
        gate = validate_where_update(current, proposed)
        assert gate.passed is False
        assert "chronos_non_decreasing_fail" in gate.rule_ids

    def test_same_event_index_passes_chronos(self):
        current = _where(event_index=5)
        proposed = _where(event_index=5)
        gate = validate_where_update(current, proposed)
        assert "chronos_non_decreasing" in gate.rule_ids
        assert "chronos_non_decreasing_fail" not in gate.rule_ids

    def test_out_of_range_field_confidence_fails(self):
        current = _where()
        proposed = _where(field_confidence=1.5)
        gate = validate_where_update(current, proposed)
        assert gate.passed is False
        assert "field_confidence_range_fail" in gate.rule_ids

    def test_negative_task_confidence_fails(self):
        current = _where()
        proposed = _where(task_confidence=-0.1)
        gate = validate_where_update(current, proposed)
        assert gate.passed is False
        assert "task_confidence_range_fail" in gate.rule_ids

    def test_missing_mode_fails(self):
        current = _where()
        proposed = _where(mode="")
        gate = validate_where_update(current, proposed)
        assert gate.passed is False
        assert "field_mode_missing" in gate.rule_ids

    def test_missing_domain_fails(self):
        current = _where()
        proposed = _where(domain="")
        gate = validate_where_update(current, proposed)
        assert gate.passed is False
        assert "task_domain_missing" in gate.rule_ids

    def test_score_reflects_fraction_of_failures(self):
        current = _where(event_index=5)
        # Only chronos rule fails (1 of 5 rules)
        proposed = _where(event_index=3)
        gate = validate_where_update(current, proposed)
        assert gate.score == 0.8  # 4/5 rules pass

    def test_multiple_failures_lower_score(self):
        current = _where(event_index=5)
        # Two failures: chronos + field_confidence
        proposed = _where(event_index=3, field_confidence=1.5)
        gate = validate_where_update(current, proposed)
        assert gate.score < 0.8

    def test_all_five_rules_produce_five_rule_ids(self):
        current = _where()
        proposed = _where(event_index=6)
        gate = validate_where_update(current, proposed)
        assert len(gate.rule_ids) == 5


class TestUpdateWhere:
    def test_valid_update_appends_to_audit(self):
        from tonesoul.ystm.governance import update_where

        node = _node()
        new_where = _where(event_index=10)
        updated, record = update_where(node, new_where, rationale="test update")
        assert record.change_type == "WHERE_UPDATE"
        assert record.target == node.id
        assert len(updated.audit.updates) == 1

    def test_invalid_update_does_not_change_where(self):
        from tonesoul.ystm.governance import update_where

        node = _node()
        invalid_where = _where(event_index=0, mode="")
        updated, record = update_where(node, invalid_where, rationale="bad update")
        assert record.gate.passed is False
        # Node where should not have changed (kept original)
        assert updated.where == node.where

    def test_update_record_is_reversible_and_vetoable(self):
        from tonesoul.ystm.governance import update_where

        node = _node()
        new_where = _where(event_index=10)
        _, record = update_where(node, new_where, rationale="any")
        assert record.reversible is True
        assert record.vetoable is True
