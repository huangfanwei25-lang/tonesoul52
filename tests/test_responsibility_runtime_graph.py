"""Tests for Phase 4 — fake responsibility-graph adapter (provenance-bound edges)."""

from __future__ import annotations

import pytest

from tonesoul.responsibility_runtime import (
    EdgeRejected,
    Enforcer,
    FakePolicyEngine,
    FakeResponsibilityGraph,
    InMemoryTraceStore,
    RecordingMemoryAdapter,
    edge_from_enforcement,
    validate_intent,
)


def _graph() -> FakeResponsibilityGraph:
    return FakeResponsibilityGraph()


def _valid_edge_kwargs() -> dict[str, object]:
    return {
        "subject": "user",
        "predicate": "prefers",
        "obj": "繁體中文與誠實優先",
        "proposed_by": "claude-opus-4-8",
        "evidence_refs": ["turn_2026_06_27_001"],
        "policy_id": "fake.responsibility_runtime.v0",
        "trace_id": "rr-deadbeef",
    }


# --- the #207 §6 bar: no evidence => no edge --------------------------------------------------


def test_edge_without_evidence_is_rejected() -> None:
    g = _graph()
    kwargs = _valid_edge_kwargs()
    kwargs["evidence_refs"] = []
    with pytest.raises(EdgeRejected):
        g.add_edge(**kwargs)  # type: ignore[arg-type]
    assert g.edges == ()  # nothing written


def test_edge_with_blank_evidence_is_rejected() -> None:
    g = _graph()
    kwargs = _valid_edge_kwargs()
    kwargs["evidence_refs"] = ["   "]
    with pytest.raises(EdgeRejected):
        g.add_edge(**kwargs)  # type: ignore[arg-type]


def test_edge_without_authorization_is_rejected() -> None:
    # missing policy_id / trace_id == no proof of authorization => fail closed
    for missing in ("policy_id", "trace_id", "proposed_by"):
        g = _graph()
        kwargs = _valid_edge_kwargs()
        kwargs[missing] = ""
        with pytest.raises(EdgeRejected):
            g.add_edge(**kwargs)  # type: ignore[arg-type]


# --- the #207 §6 bar: every edge answers who/why/when/authorized-by/superseded-by -------------


def test_every_edge_answers_provenance() -> None:
    g = _graph()
    edge = g.add_edge(**_valid_edge_kwargs())  # type: ignore[arg-type]
    prov = g.provenance(edge.edge_id)
    assert prov.who == "claude-opus-4-8"
    assert prov.why == ("turn_2026_06_27_001",)
    assert prov.when == edge.created_seq
    assert prov.authorized_by_policy == "fake.responsibility_runtime.v0"
    assert prov.recorded_by_trace == "rr-deadbeef"
    assert prov.superseded_by is None
    assert prov.revoked_at is None


# --- supersession / revocation MARK, never delete ---------------------------------------------


def test_supersession_marks_old_keeps_it_queryable() -> None:
    g = _graph()
    old = g.add_edge(**_valid_edge_kwargs())  # type: ignore[arg-type]
    new_kwargs = _valid_edge_kwargs()
    new_kwargs["obj"] = "繁體中文、誠實、且簡潔"
    new_kwargs["supersedes"] = old.edge_id
    new = g.add_edge(**new_kwargs)  # type: ignore[arg-type]

    assert new.supersedes == old.edge_id
    # old edge is still present and queryable, now marked superseded (not deleted)
    assert g.provenance(old.edge_id).superseded_by == new.edge_id
    assert old.edge_id in {e.edge_id for e in g.edges}
    assert {e.edge_id for e in g.active_edges()} == {new.edge_id}


def test_supersedes_unknown_edge_is_rejected() -> None:
    g = _graph()
    kwargs = _valid_edge_kwargs()
    kwargs["supersedes"] = "re-doesnotexist"
    with pytest.raises(EdgeRejected):
        g.add_edge(**kwargs)  # type: ignore[arg-type]


def test_revocation_marks_revoked_at_keeps_edge() -> None:
    g = _graph()
    edge = g.add_edge(**_valid_edge_kwargs())  # type: ignore[arg-type]
    revoked = g.revoke(edge.edge_id)
    assert revoked.revoked_at is not None
    assert revoked.active is False
    assert edge.edge_id in {e.edge_id for e in g.edges}  # still queryable
    assert g.active_edges() == ()


# --- no-oracle boundary: the graph does not judge whether evidence supports the relation -------


def test_graph_does_not_judge_evidence_sufficiency() -> None:
    g = _graph()
    kwargs = _valid_edge_kwargs()
    kwargs["obj"] = "ToneSoul 已完全解決 AI 問責"  # an absurd relation
    kwargs["evidence_refs"] = ["unrelated_ref"]  # syntactically valid, semantically irrelevant
    edge = g.add_edge(**kwargs)  # type: ignore[arg-type]
    assert edge.edge_id in {e.edge_id for e in g.edges}  # form passes; sufficiency is not checked


# --- integration: edge can only come from an AUTHORIZED execution (Phase 1->4 chain) ----------


def test_edge_from_enforcement_requires_executed_result() -> None:
    # a denied enforcement must not be able to produce an edge
    validation = validate_intent(
        {
            "intent": "memory.write.propose",
            "claim": "不該寫入",
            "evidence_refs": ["turn_x"],
            "requested_scope": "long_term_memory",
        }
    )
    deny_decision = FakePolicyEngine(allowed_scopes={"session_memory"}).decide(validation)
    enforcer = Enforcer(memory_adapter=RecordingMemoryAdapter(), trace_store=InMemoryTraceStore())
    denied = enforcer.enforce(validation, deny_decision)

    g = _graph()
    with pytest.raises(EdgeRejected):
        edge_from_enforcement(
            g, denied, subject="user", predicate="prefers", obj="x", proposed_by="codex"
        )
    assert g.edges == ()


def test_edge_from_enforcement_carries_trace_and_policy() -> None:
    validation = validate_intent(
        {
            "intent": "memory.write.propose",
            "claim": "使用者偏好繁體中文與誠實優先",
            "evidence_refs": ["turn_2026_06_27_001"],
            "requested_scope": "long_term_memory",
        }
    )
    decision = FakePolicyEngine().decide(validation)
    enforcer = Enforcer(memory_adapter=RecordingMemoryAdapter(), trace_store=InMemoryTraceStore())
    executed = enforcer.enforce(validation, decision)

    g = _graph()
    edge = edge_from_enforcement(
        g,
        executed,
        subject="user",
        predicate="prefers",
        obj="繁體中文與誠實優先",
        proposed_by="claude-opus-4-8",
    )
    # the edge's authorization provenance comes from the actual execution, not hand-typed
    assert edge.trace_id == executed.request_id
    assert edge.policy_id == executed.trace_event.policy_decision.policy_id
    assert edge.evidence_refs == executed.trace_event.evidence_refs


def test_edge_id_is_deterministic() -> None:
    g1, g2 = _graph(), _graph()
    e1 = g1.add_edge(**_valid_edge_kwargs())  # type: ignore[arg-type]
    e2 = g2.add_edge(**_valid_edge_kwargs())  # type: ignore[arg-type]
    assert e1.edge_id == e2.edge_id  # same content+trace+seq => same id, no randomness/time
