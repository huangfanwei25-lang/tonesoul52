"""Deterministic cognitive-frame schema for problem exploration.

This module does not infer truth, call an LLM, or read private context. It validates the
shape of an externally supplied problem frame: question, context, facts, unknowns,
hypotheses, constraints, and next probes.

Boundary: evidence checks are presence/form checks only. They do not prove that the
evidence semantically supports the claim.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal, get_args

from pydantic import BaseModel, ConfigDict, Field, StrictStr, ValidationError, field_validator

from tonesoul.responsibility_runtime.intent_validator import _has_visible_content

__ts_layer__ = "semantic"
__ts_purpose__ = "Deterministic cognitive frame contract for auditable problem exploration."

USES_LLM = False
USES_NETWORK = False

ConfidenceLevel = Literal["observed", "derived", "inferred", "unknown"]
IssueSeverity = Literal["error", "warning"]

# The frame is accepted only if every issue is an explicitly non-blocking severity, so an
# unrecognized or mistyped severity fails closed (blocks) instead of silently passing.
_VALID_SEVERITIES: frozenset[str] = frozenset(get_args(IssueSeverity))
_NON_BLOCKING_SEVERITIES: frozenset[str] = frozenset({"warning"})


def _require_single_line(value: str, *, field_label: str) -> str:
    """Reject embedded line breaks so rendered prompt sections cannot be structurally forged.

    ``to_prompt_sections`` renders a line-oriented packet (``[SECTION]`` headers and ``- item``
    lines). Text containing a newline or other line separator could inject a forged section
    header or item line that bypassed lane validation, so multi-line field text fails closed.
    """

    cleaned = value.strip()
    if cleaned.splitlines() != [cleaned]:
        raise ValueError(f"{field_label} must not contain embedded line breaks")
    return cleaned


class FrameItem(BaseModel):
    """One lane item inside a cognitive frame."""

    model_config = ConfigDict(extra="forbid")

    text: StrictStr = Field(min_length=1)
    evidence_refs: tuple[StrictStr, ...] = ()
    confidence: ConfidenceLevel = "unknown"

    @field_validator("text")
    @classmethod
    def _text_has_visible_content(cls, value: str) -> str:
        if not _has_visible_content(value):
            raise ValueError("text must have visible content")
        return _require_single_line(value, field_label="text")

    @field_validator("evidence_refs")
    @classmethod
    def _evidence_refs_have_visible_content(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if any(not _has_visible_content(ref) for ref in value):
            raise ValueError("evidence_refs must contain refs with visible content")
        return tuple(_require_single_line(ref, field_label="evidence_ref") for ref in value)


class CognitiveFrame(BaseModel):
    """A structured, reviewable problem frame.

    Lanes that state factual context (`temporal_context`, `spatial_context`, `actors`,
    `known_facts`, `constraints`) need evidence refs. `unknowns` and `hypotheses` may be
    evidence-light, but they must lead to next probes before the frame is accepted.
    """

    model_config = ConfigDict(extra="forbid")

    question: StrictStr = Field(min_length=1)
    temporal_context: tuple[FrameItem, ...] = ()
    spatial_context: tuple[FrameItem, ...] = ()
    actors: tuple[FrameItem, ...] = ()
    known_facts: tuple[FrameItem, ...] = ()
    hypotheses: tuple[FrameItem, ...] = ()
    unknowns: tuple[FrameItem, ...] = ()
    constraints: tuple[FrameItem, ...] = ()
    next_probes: tuple[FrameItem, ...] = ()

    @field_validator("question")
    @classmethod
    def _question_has_visible_content(cls, value: str) -> str:
        if not _has_visible_content(value):
            raise ValueError("question must have visible content")
        return _require_single_line(value, field_label="question")

    def to_prompt_sections(self) -> list[str]:
        """Render a compact, line-oriented prompt packet without inventing new content.

        Question and item text are validated single-line, so ``[SECTION]`` headers and ``- item``
        lines cannot be forged by embedding line breaks in field text.
        """

        sections = [f"[QUESTION]\n{self.question}"]
        for label, items in (
            ("TEMPORAL CONTEXT", self.temporal_context),
            ("SPATIAL CONTEXT", self.spatial_context),
            ("ACTORS", self.actors),
            ("KNOWN FACTS", self.known_facts),
            ("HYPOTHESES", self.hypotheses),
            ("UNKNOWNS", self.unknowns),
            ("CONSTRAINTS", self.constraints),
            ("NEXT PROBES", self.next_probes),
        ):
            if items:
                sections.append(f"[{label}]\n" + "\n".join(_render_item(item) for item in items))
        return sections


@dataclass(frozen=True)
class CognitiveFrameIssue:
    """A deterministic frame issue suitable for tests, traces, or reviewer surfaces."""

    code: str
    field: str
    severity: IssueSeverity
    message: str

    def __post_init__(self) -> None:
        # Dataclasses do not enforce the Literal at runtime; reject unknown severities loudly at
        # construction so a typo cannot silently become non-blocking in the accept decision.
        if self.severity not in _VALID_SEVERITIES:
            raise ValueError(f"unknown CognitiveFrameIssue severity: {self.severity!r}")


@dataclass(frozen=True)
class CognitiveFrameValidationResult:
    """Validation result for an untrusted cognitive frame payload."""

    accepted: bool
    frame: CognitiveFrame | None
    issues: tuple[CognitiveFrameIssue, ...]

    def __bool__(self) -> bool:
        return self.accepted


_FACTUAL_LANES = (
    "temporal_context",
    "spatial_context",
    "actors",
    "known_facts",
    "constraints",
)


def validate_cognitive_frame(
    payload: Mapping[str, Any] | CognitiveFrame | object,
) -> CognitiveFrameValidationResult:
    """Validate an external cognitive frame without side effects."""

    if isinstance(payload, CognitiveFrame):
        frame = payload
        parse_issues: tuple[CognitiveFrameIssue, ...] = ()
    elif not isinstance(payload, Mapping):
        return _reject(
            code="malformed_frame",
            field="payload",
            message="cognitive frame payload must be an object",
        )
    else:
        try:
            frame = CognitiveFrame.model_validate(payload)
            parse_issues = ()
        except ValidationError as exc:
            return CognitiveFrameValidationResult(
                accepted=False,
                frame=None,
                issues=tuple(_issue_from_pydantic_error(error) for error in exc.errors()),
            )

    semantic_issues = _semantic_issues(frame)
    issues = parse_issues + semantic_issues
    # Fail closed: accept only when every issue is an explicitly non-blocking severity.
    accepted = all(issue.severity in _NON_BLOCKING_SEVERITIES for issue in issues)
    return CognitiveFrameValidationResult(accepted=accepted, frame=frame, issues=issues)


def _semantic_issues(frame: CognitiveFrame) -> tuple[CognitiveFrameIssue, ...]:
    issues: list[CognitiveFrameIssue] = []

    if not any((frame.known_facts, frame.hypotheses, frame.unknowns)):
        issues.append(
            CognitiveFrameIssue(
                code="empty_exploration_frame",
                field="known_facts|hypotheses|unknowns",
                severity="error",
                message="frame must include at least one fact, hypothesis, or unknown",
            )
        )

    if not frame.temporal_context:
        issues.append(
            CognitiveFrameIssue(
                code="missing_temporal_context",
                field="temporal_context",
                severity="warning",
                message="frame has no explicit temporal context",
            )
        )
    if not frame.spatial_context:
        issues.append(
            CognitiveFrameIssue(
                code="missing_spatial_context",
                field="spatial_context",
                severity="warning",
                message="frame has no explicit spatial or system-location context",
            )
        )

    for lane_name in _FACTUAL_LANES:
        items = getattr(frame, lane_name)
        for idx, item in enumerate(items):
            if not item.evidence_refs:
                issues.append(
                    CognitiveFrameIssue(
                        code="missing_evidence_refs",
                        field=f"{lane_name}.{idx}.evidence_refs",
                        severity="error",
                        message="factual frame items require evidence_refs",
                    )
                )
            if item.confidence == "unknown":
                issues.append(
                    CognitiveFrameIssue(
                        code="factual_lane_unknown_confidence",
                        field=f"{lane_name}.{idx}.confidence",
                        severity="error",
                        message="factual lanes must not use unknown confidence",
                    )
                )

    for idx, item in enumerate(frame.hypotheses):
        if item.confidence == "observed":
            issues.append(
                CognitiveFrameIssue(
                    code="hypothesis_overclaimed",
                    field=f"hypotheses.{idx}.confidence",
                    severity="error",
                    message="hypotheses must not be labeled observed",
                )
            )
        if not item.evidence_refs:
            issues.append(
                CognitiveFrameIssue(
                    code="hypothesis_without_evidence",
                    field=f"hypotheses.{idx}.evidence_refs",
                    severity="warning",
                    message="hypothesis has no evidence refs; keep it tentative",
                )
            )

    for idx, item in enumerate(frame.unknowns):
        if item.confidence != "unknown":
            issues.append(
                CognitiveFrameIssue(
                    code="unknown_confidence_mismatch",
                    field=f"unknowns.{idx}.confidence",
                    severity="error",
                    message="unknown lanes must use unknown confidence",
                )
            )

    if (frame.unknowns or frame.hypotheses) and not frame.next_probes:
        issues.append(
            CognitiveFrameIssue(
                code="missing_next_probes",
                field="next_probes",
                severity="error",
                message="unknowns or hypotheses require at least one next probe",
            )
        )

    return tuple(issues)


def _reject(*, code: str, field: str, message: str) -> CognitiveFrameValidationResult:
    return CognitiveFrameValidationResult(
        accepted=False,
        frame=None,
        issues=(CognitiveFrameIssue(code=code, field=field, severity="error", message=message),),
    )


def _issue_from_pydantic_error(error: dict[str, Any]) -> CognitiveFrameIssue:
    field = ".".join(str(part) for part in error.get("loc", ())) or "payload"
    error_type = str(error.get("type", "validation_error"))
    code = _map_pydantic_error_code(error_type)
    return CognitiveFrameIssue(
        code=code,
        field=field,
        severity="error",
        message=str(error.get("msg", "validation error")),
    )


def _map_pydantic_error_code(error_type: str) -> str:
    if error_type == "missing":
        return "missing_required_field"
    if error_type in {"extra_forbidden", "model_type", "mapping_type"}:
        return "malformed_frame"
    if "too_short" in error_type:
        return "empty_required_field"
    if "string" in error_type or "literal" in error_type or "tuple" in error_type:
        return "malformed_frame"
    return "validation_error"


def _render_item(item: FrameItem) -> str:
    refs = ", ".join(item.evidence_refs) if item.evidence_refs else "no evidence_refs"
    return f"- {item.text} (confidence={item.confidence}; evidence={refs})"
