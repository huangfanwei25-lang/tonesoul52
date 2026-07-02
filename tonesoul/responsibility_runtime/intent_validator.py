"""Deterministic intent-form validator for the responsibility runtime.

Phase 1 validates shape only: required fields, allowed intent names, allowed scopes, and
evidence reference presence for memory-write proposals. It deliberately does not judge truth,
evidence sufficiency, user intent, authorization, or memory side effects.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictStr, ValidationError, field_validator

__ts_layer__ = "governance"
__ts_purpose__ = "Deterministic responsibility-runtime intent validator."

USES_LLM = False
DEFAULT_ALLOWED_SCOPES = frozenset({"session_memory", "long_term_memory", "project_memory"})


# L/N/P/S-category code points that nonetheless render blank/filler — a curated denylist.
# This is a BEST-EFFORT denylist, NOT exhaustive: Unicode invisibility is an open adversarial
# surface. The robust long-term fix is a POSITIVE evidence-ref format (a required id/URI shape),
# not an ever-growing denylist. (red-team 2026-06-27: Codex/different-model pass.)
_BLANK_CODE_POINTS = frozenset(
    "⠀"  # BRAILLE PATTERN BLANK (So)
    "ㅤ"  # HANGUL FILLER (Lo)
    "ᅟ"  # HANGUL CHOSEONG FILLER (Lo)
    "ᅠ"  # HANGUL JUNGSEONG FILLER (Lo)
    "ﾠ"  # HALFWIDTH HANGUL FILLER (Lo)
)


def _has_visible_content(text: str) -> bool:
    """True if the string has at least one rendering character.

    A char counts as visible only if its Unicode category is L/N/P/S — which excludes C
    (control/format), Z (separators), AND **all M\\* marks** (combining marks / variation
    selectors like U+FE0F, U+034F, U+180B do not count on their own) — AND it is not a known
    blank/filler in `_BLANK_CODE_POINTS` (braille-blank U+2800, Hangul fillers).

    History: the original `str.strip()` check missed zero-width code points; the first fix
    (categories outside C/Z) STILL missed the non-C/Z invisibles a different-model red-team
    found (VS-16/Mn, CGJ/Mn, braille-blank/So, Hangul-filler/Lo). This category+denylist version
    closes those — but it is best-effort, not a proof (see `_BLANK_CODE_POINTS`). A required
    field made only of invisible/filler code points is effectively empty and must be rejected.
    """
    return any(
        unicodedata.category(ch)[0] in {"L", "N", "P", "S"} and ch not in _BLANK_CODE_POINTS
        for ch in text
    )


IntentName = Literal["memory.write.propose", "memory.read.request"]
RiskLevel = Literal["low", "medium", "high"]
UncertaintyLevel = Literal["low", "medium", "high", "unknown"]


@dataclass(frozen=True)
class IntentValidationIssue:
    """A fail-closed validation issue suitable for trace or reviewer surfaces."""

    code: str
    field: str
    message: str


@dataclass(frozen=True)
class IntentValidationResult:
    """Structured result from deterministic intent validation."""

    accepted: bool
    intent: str | None
    normalized_payload: Mapping[str, Any] | None
    issues: tuple[IntentValidationIssue, ...]

    def __bool__(self) -> bool:
        return self.accepted


class _ScopedIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requested_scope: StrictStr = Field(min_length=1)

    @field_validator("requested_scope")
    @classmethod
    def _non_empty_scope(cls, value: str) -> str:
        if not _has_visible_content(value):
            raise ValueError("requested_scope must have visible content")
        return value.strip()


class MemoryWriteProposal(_ScopedIntent):
    """Form-only schema for a proposed memory write."""

    intent: Literal["memory.write.propose"]
    claim: StrictStr = Field(min_length=1)
    evidence_refs: list[StrictStr] = Field(min_length=1)
    risk: RiskLevel | None = None
    uncertainty: UncertaintyLevel | None = None
    audit_reason: StrictStr | None = None

    @field_validator("claim")
    @classmethod
    def _non_empty_claim(cls, value: str) -> str:
        if not _has_visible_content(value):
            raise ValueError("claim must have visible content")
        return value.strip()

    @field_validator("evidence_refs")
    @classmethod
    def _non_empty_evidence_refs(cls, value: list[str]) -> list[str]:
        if any(not _has_visible_content(ref) for ref in value):
            raise ValueError("evidence_refs must contain refs with visible content")
        return [ref.strip() for ref in value]

    @field_validator("audit_reason")
    @classmethod
    def _empty_reason_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        reason = value.strip()
        return reason or None


class MemoryReadRequest(_ScopedIntent):
    """Form-only schema for a scoped memory read request."""

    intent: Literal["memory.read.request"]
    query: StrictStr = Field(min_length=1)
    reason: StrictStr | None = None

    @field_validator("query")
    @classmethod
    def _non_empty_query(cls, value: str) -> str:
        if not _has_visible_content(value):
            raise ValueError("query must have visible content")
        return value.strip()

    @field_validator("reason")
    @classmethod
    def _empty_reason_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        reason = value.strip()
        return reason or None


_SCHEMAS: dict[str, type[_ScopedIntent]] = {
    "memory.write.propose": MemoryWriteProposal,
    "memory.read.request": MemoryReadRequest,
}


def validate_intent(
    payload: Mapping[str, Any] | Any,
    *,
    allowed_scopes: Iterable[str] | None = None,
) -> IntentValidationResult:
    """Validate an untrusted model intent without LLM calls or side effects."""

    if not isinstance(payload, Mapping):
        return _reject(
            intent=None,
            code="malformed_intent",
            field="payload",
            message="intent payload must be an object",
        )

    raw_intent = payload.get("intent")
    if raw_intent is None:
        return _reject(
            intent=None,
            code="missing_required_field",
            field="intent",
            message="intent is required",
        )
    if not isinstance(raw_intent, str):
        return _reject(
            intent=None,
            code="malformed_intent",
            field="intent",
            message="intent must be a string",
        )

    schema = _SCHEMAS.get(raw_intent)
    if schema is None:
        return _reject(
            intent=raw_intent,
            code="unsupported_intent",
            field="intent",
            message=f"unsupported intent: {raw_intent}",
        )

    try:
        model = schema.model_validate(payload)
    except ValidationError as exc:
        return IntentValidationResult(
            accepted=False,
            intent=raw_intent,
            normalized_payload=None,
            issues=tuple(_issue_from_pydantic_error(error) for error in exc.errors()),
        )

    allowed = DEFAULT_ALLOWED_SCOPES if allowed_scopes is None else frozenset(allowed_scopes)
    if model.requested_scope not in allowed:
        return _reject(
            intent=raw_intent,
            code="scope_not_allowed",
            field="requested_scope",
            message=f"requested_scope is not allowed: {model.requested_scope}",
        )

    return IntentValidationResult(
        accepted=True,
        intent=raw_intent,
        normalized_payload=model.model_dump(exclude_none=True),
        issues=(),
    )


def _reject(
    *,
    intent: str | None,
    code: str,
    field: str,
    message: str,
) -> IntentValidationResult:
    return IntentValidationResult(
        accepted=False,
        intent=intent,
        normalized_payload=None,
        issues=(IntentValidationIssue(code=code, field=field, message=message),),
    )


def _issue_from_pydantic_error(error: dict[str, Any]) -> IntentValidationIssue:
    field = ".".join(str(part) for part in error.get("loc", ())) or "payload"
    error_type = str(error.get("type", "validation_error"))
    code = _map_pydantic_error_code(error_type)
    return IntentValidationIssue(
        code=code,
        field=field,
        message=str(error.get("msg", "validation error")),
    )


def _map_pydantic_error_code(error_type: str) -> str:
    if error_type == "missing":
        return "missing_required_field"
    if error_type in {"extra_forbidden", "model_type", "mapping_type"}:
        return "malformed_intent"
    if "too_short" in error_type:
        return "empty_required_field"
    if "string" in error_type or "literal" in error_type or "list" in error_type:
        return "malformed_intent"
    return "validation_error"
