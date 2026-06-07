"""Evidence reducer for execution promises.

This module checks whether externally visible work claims have observable
evidence. It is deliberately small: it does not judge intent or truthfulness,
only whether a declared file/process/command evidence requirement is satisfied.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Literal

EvidenceKind = Literal["file", "command", "process", "artifact"]
PromiseStatus = Literal["fulfilled", "missing_evidence", "empty_evidence", "unverifiable"]

__ts_layer__ = "observability"
__ts_purpose__ = (
    "Execution honesty: evidence reducer that checks whether work claims have observable proof."
)


@dataclass(frozen=True)
class ExecutionPromise:
    """A claim that an AI or agent said it would produce observable evidence for."""

    promise_id: str
    claim: str
    evidence_kind: EvidenceKind
    target: str
    require_non_empty: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionEvidenceResult:
    """Outcome of checking one promise against observable local evidence."""

    promise_id: str
    status: PromiseStatus
    evidence_kind: EvidenceKind
    target: str
    reason: str


def check_promise(promise: ExecutionPromise, *, workspace_root: Path | None = None) -> ExecutionEvidenceResult:
    """Check one promise without mutating repo state or runtime memory."""

    if promise.evidence_kind in {"command", "process"}:
        return ExecutionEvidenceResult(
            promise_id=promise.promise_id,
            status="unverifiable",
            evidence_kind=promise.evidence_kind,
            target=promise.target,
            reason=f"{promise.evidence_kind} evidence requires an explicit event log",
        )

    if promise.evidence_kind not in {"file", "artifact"}:
        return ExecutionEvidenceResult(
            promise_id=promise.promise_id,
            status="unverifiable",
            evidence_kind=promise.evidence_kind,
            target=promise.target,
            reason=f"unsupported evidence kind: {promise.evidence_kind}",
        )

    path = _resolve_target(promise.target, workspace_root=workspace_root)
    if not path.exists():
        return ExecutionEvidenceResult(
            promise_id=promise.promise_id,
            status="missing_evidence",
            evidence_kind=promise.evidence_kind,
            target=str(path),
            reason=f"expected {promise.evidence_kind} does not exist",
        )
    if promise.require_non_empty and path.is_file() and path.stat().st_size == 0:
        return ExecutionEvidenceResult(
            promise_id=promise.promise_id,
            status="empty_evidence",
            evidence_kind=promise.evidence_kind,
            target=str(path),
            reason=f"expected {promise.evidence_kind} is empty",
        )
    return ExecutionEvidenceResult(
        promise_id=promise.promise_id,
        status="fulfilled",
        evidence_kind=promise.evidence_kind,
        target=str(path),
        reason=f"expected {promise.evidence_kind} is present",
    )


def reduce_promises(
    promises: Iterable[ExecutionPromise], *, workspace_root: Path | None = None
) -> dict[str, Any]:
    """Reduce promise checks into a compact status payload."""

    results = [check_promise(promise, workspace_root=workspace_root) for promise in promises]
    status_counts: dict[str, int] = {}
    for result in results:
        status_counts[result.status] = status_counts.get(result.status, 0) + 1

    blocking = [
        result
        for result in results
        if result.status in {"missing_evidence", "empty_evidence", "unverifiable"}
    ]
    return {
        "promise_count": len(results),
        "status_counts": dict(sorted(status_counts.items())),
        "all_fulfilled": not blocking,
        "results": [result.__dict__ for result in results],
    }


def _resolve_target(target: str, *, workspace_root: Path | None) -> Path:
    path = Path(target)
    if path.is_absolute() or workspace_root is None:
        return path
    return workspace_root / path
