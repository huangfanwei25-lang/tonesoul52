"""Phase 4 — fake responsibility-graph adapter (NOT Graphiti).

A normal memory edge says "A related_to B". A responsibility edge also records who proposed
it, on what evidence, under which policy, recorded by which trace, and whether it was
superseded or revoked. This is an in-memory FAKE adapter for the contract: it deliberately
does not bind Graphiti, a real graph DB, or any LLM.

Two non-negotiables (#207 §6 bar):
  1. an edge with no evidence cannot be written;
  2. every stored edge can answer: who, why, when, authorized by what, superseded by what.

A write is only allowed from an AUTHORIZED execution: `edge_from_enforcement` consumes a Phase-2
EnforcementResult and refuses unless it actually executed, carrying that execution's trace_id /
policy_id / evidence_refs into the edge. The adapter does NOT judge whether the evidence
supports the claim (no oracle, same boundary as every earlier phase). Supersession and
revocation MARK; they never delete (provenance stays queryable).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

# single source of truth for "what counts as visible content" — the same rule the Phase-1
# validator uses, so the direct graph-write surface cannot drift from it. Red-team #210 finding:
# the graph had the same strip-only invisible-evidence blind spot the validator had (#211).
from .intent_validator import _has_visible_content

__ts_layer__ = "governance"
__ts_purpose__ = "Fake responsibility-graph adapter with provenance-bound edges."

USES_LLM = False
USES_NETWORK = False

if TYPE_CHECKING:
    from .enforcer import EnforcementResult


@dataclass(frozen=True)
class ResponsibilityEdge:
    """A memory edge that carries its own accountability provenance."""

    edge_id: str
    subject: str
    predicate: str
    obj: str
    proposed_by: str
    evidence_refs: tuple[str, ...]
    policy_id: str
    trace_id: str
    created_seq: int
    supersedes: str | None = None
    superseded_by: str | None = None
    revoked_at: int | None = None

    @property
    def active(self) -> bool:
        return self.superseded_by is None and self.revoked_at is None


@dataclass(frozen=True)
class EdgeProvenance:
    """The 'every edge answers' view (#207 §6 success criterion)."""

    who: str
    why: tuple[str, ...]
    when: int
    authorized_by_policy: str
    recorded_by_trace: str
    supersedes: str | None
    superseded_by: str | None
    revoked_at: int | None


class EdgeRejected(ValueError):
    """Raised when an edge fails the fail-closed write checks."""


def _edge_id(subject: str, predicate: str, obj: str, trace_id: str, seq: int) -> str:
    canonical = json.dumps(
        [subject, predicate, obj, trace_id, seq],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return "re-" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


class FakeResponsibilityGraph:
    """In-memory, append-mark (never delete) responsibility graph."""

    def __init__(self) -> None:
        self._edges: dict[str, ResponsibilityEdge] = {}
        self._seq = 0

    def add_edge(
        self,
        *,
        subject: str,
        predicate: str,
        obj: str,
        proposed_by: str,
        evidence_refs: tuple[str, ...] | list[str],
        policy_id: str,
        trace_id: str,
        supersedes: str | None = None,
    ) -> ResponsibilityEdge:
        """Write a provenance-bound edge. Fail-closed: no evidence / no authorization → reject."""

        if not evidence_refs or any(not _has_visible_content(str(r)) for r in evidence_refs):
            raise EdgeRejected("edge requires evidence_refs with visible content")
        refs = tuple(str(r).strip() for r in evidence_refs)
        for name, value in (
            ("subject", subject),
            ("predicate", predicate),
            ("obj", obj),
            ("proposed_by", proposed_by),
            ("policy_id", policy_id),
            ("trace_id", trace_id),
        ):
            if not isinstance(value, str) or not _has_visible_content(value):
                raise EdgeRejected(f"edge requires {name} with visible content")
        if supersedes is not None and supersedes not in self._edges:
            raise EdgeRejected(f"supersedes references unknown edge: {supersedes}")

        self._seq += 1
        edge = ResponsibilityEdge(
            edge_id=_edge_id(subject, predicate, obj, trace_id, self._seq),
            subject=subject.strip(),
            predicate=predicate.strip(),
            obj=obj.strip(),
            proposed_by=proposed_by.strip(),
            evidence_refs=refs,
            policy_id=policy_id.strip(),
            trace_id=trace_id.strip(),
            created_seq=self._seq,
            supersedes=supersedes,
        )
        self._edges[edge.edge_id] = edge
        if supersedes is not None:
            old = self._edges[supersedes]
            self._edges[supersedes] = replace(old, superseded_by=edge.edge_id)
        return edge

    def revoke(self, edge_id: str) -> ResponsibilityEdge:
        """Mark an edge revoked. Never deletes — provenance stays queryable."""
        if edge_id not in self._edges:
            raise EdgeRejected(f"unknown edge: {edge_id}")
        self._seq += 1
        revoked = replace(self._edges[edge_id], revoked_at=self._seq)
        self._edges[edge_id] = revoked
        return revoked

    def provenance(self, edge_id: str) -> EdgeProvenance:
        """Answer who / why / when / authorized-by / superseded-by for an edge."""
        edge = self._edges[edge_id]
        return EdgeProvenance(
            who=edge.proposed_by,
            why=edge.evidence_refs,
            when=edge.created_seq,
            authorized_by_policy=edge.policy_id,
            recorded_by_trace=edge.trace_id,
            supersedes=edge.supersedes,
            superseded_by=edge.superseded_by,
            revoked_at=edge.revoked_at,
        )

    @property
    def edges(self) -> tuple[ResponsibilityEdge, ...]:
        return tuple(self._edges.values())

    def active_edges(self) -> tuple[ResponsibilityEdge, ...]:
        return tuple(e for e in self._edges.values() if e.active)


def edge_from_enforcement(
    graph: FakeResponsibilityGraph,
    result: EnforcementResult,
    *,
    subject: str,
    predicate: str,
    obj: str,
    proposed_by: str,
    supersedes: str | None = None,
) -> ResponsibilityEdge:
    """Bind a memory edge to an AUTHORIZED execution. Refuses if it did not execute.

    This is the only intended write path: the edge's authorization provenance comes from a
    Phase-2 enforcement that actually ran, so an edge cannot exist without a policy decision and
    a trace behind it.
    """
    if not getattr(result, "executed", False):
        raise EdgeRejected("edge_from_enforcement requires an executed enforcement result")
    trace_event = result.trace_event
    return graph.add_edge(
        subject=subject,
        predicate=predicate,
        obj=obj,
        proposed_by=proposed_by,
        evidence_refs=trace_event.evidence_refs,
        policy_id=trace_event.policy_decision.policy_id,
        trace_id=result.request_id,
        supersedes=supersedes,
    )
