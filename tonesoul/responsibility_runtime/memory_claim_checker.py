"""Check whether memory claims in output are backed by runtime trace.

This is deliberately not a consent or truth classifier. It only asks a narrow, auditable
question: if the output asserts that a memory write already happened, does the current trace
contain an executed `memory.write.propose` event?

The claim detector is conservative and lexical on purpose. False negatives are acceptable here;
false positives would re-create the #215 memory-consent-detector failure mode.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

from .trace import TraceEvent

__ts_layer__ = "governance"
__ts_purpose__ = "Deterministic trace support checker for output memory claims."

USES_LLM = False
USES_NETWORK = False

MemoryClaimStatus = Literal["no_memory_claim", "backed_by_trace", "unbacked_memory_claim"]


@dataclass(frozen=True)
class MemoryClaimTraceCheck:
    """Result of checking an output memory claim against current runtime trace."""

    status: MemoryClaimStatus
    claim_detected: bool
    backed_by_trace: bool
    matched_phrase: str | None
    executed_request_ids: tuple[str, ...]
    reason: str


_EN_MEMORY_CLAIM_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"\b(?:i\s+(?:have\s+|have\s+already\s+|already\s+)|i've\s+|we\s+have\s+)"
        r"(?:saved|stored|recorded|remembered|retained)\s+"
        r"(?:this|that|it|your\b|your\s+(?:preference|preferences|data|personal\s+data|profile))",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:i|we)\s+(?:permanently|persistently|long[- ]term)\s+"
        r"(?:saved|stored|remembered|retained)\s+"
        r"(?:this|that|it|your\b|your\s+(?:preference|preferences|data|personal\s+data|profile))",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:i|we)\s+will\s+(?:remember|retain|store|save)\s+"
        r"(?:this|that|it|your\b|your\s+(?:preference|preferences|data|personal\s+data|profile))"
        r".{0,80}\b(?:future\s+sessions|all\s+sessions|across\s+sessions|long[- ]term|permanent)",
        re.IGNORECASE,
    ),
)

_ZH_MEMORY_CLAIM_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"(?:我|我們|我们|系統|系统|本系統|本系统|ai).{0,8}"
        r"(?:已|已經|已经|已經永久|已经永久|永久).{0,14}"
        r"(?:記住|记住|儲存|储存|保存|保留|存下).{0,14}"
        r"(?:你|妳|使用者|用户|偏好|資料|资料|這個|这个)"
    ),
    re.compile(
        r"(?:我|我們|我们|系統|系统|本系統|本系统|ai).{0,8}"
        r"(?:會|会).{0,14}(?:跨.*(?:session|對話|会话)|長期|长期|永久).{0,14}"
        r"(?:記住|记住|儲存|储存|保存|保留)"
    ),
)

_EN_NON_ASSERTIVE_MARKERS = (
    "whether",
    "should i",
    "should we",
    "should an ai",
    "what if",
    "imagine",
    "example:",
    "for example",
    "said the",
    "our policy forbids",
    "policy forbids",
    "do not retain",
    "don't retain",
)
_ZH_NON_ASSERTIVE_MARKERS = (
    "是否",
    "應不應該",
    "应不应该",
    "要不要",
    "可不可以",
    "如果",
    "假設",
    "假设",
    "想像",
    "例如",
    "政策禁止",
)
_EN_NEGATION_MARKERS = (
    "not",
    "never",
    "no",
    "do not",
    "don't",
    "will not",
    "won't",
    "cannot",
    "can't",
)
_ZH_NEGATION_MARKERS = ("不", "不會", "不会", "沒有", "没有", "未", "無", "无", "才不")


def check_memory_claim_trace(
    output_text: str,
    trace_events: Iterable[TraceEvent],
) -> MemoryClaimTraceCheck:
    """Check whether output memory claims are backed by an executed memory-write trace.

    This checks only the existence of an executed memory-write trace. It does not decide whether
    that trace semantically supports the exact claim, whether consent is valid, or whether the
    underlying memory store really persisted data.
    """

    executed_request_ids = tuple(
        event.request_id
        for event in trace_events
        if event.intent == "memory.write.propose" and event.enforcer_result == "executed"
    )
    matched = detect_memory_write_claim(output_text)
    if matched is None:
        return MemoryClaimTraceCheck(
            status="no_memory_claim",
            claim_detected=False,
            backed_by_trace=False,
            matched_phrase=None,
            executed_request_ids=executed_request_ids,
            reason="no supported memory-write claim shape detected",
        )
    if executed_request_ids:
        return MemoryClaimTraceCheck(
            status="backed_by_trace",
            claim_detected=True,
            backed_by_trace=True,
            matched_phrase=matched,
            executed_request_ids=executed_request_ids,
            reason="memory-write claim has at least one executed memory.write.propose trace",
        )
    return MemoryClaimTraceCheck(
        status="unbacked_memory_claim",
        claim_detected=True,
        backed_by_trace=False,
        matched_phrase=matched,
        executed_request_ids=(),
        reason="memory-write claim has no executed memory.write.propose trace in current turn",
    )


def detect_memory_write_claim(output_text: str) -> str | None:
    """Return the matched memory-write claim phrase, or None.

    Conservative by design: it avoids questions, quoted examples, policy statements, and local
    negations. It is not a semantic paraphrase detector.
    """

    normalized = _normalize(output_text)
    if not normalized:
        return None
    if _is_non_assertive_context(normalized):
        return None
    for pattern in (*_EN_MEMORY_CLAIM_PATTERNS, *_ZH_MEMORY_CLAIM_PATTERNS):
        match = pattern.search(normalized)
        if match and not _has_local_negation(normalized, match.start(), match.end()):
            return match.group(0)
    return None


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text or "").lower()
    return re.sub(r"\s+", " ", normalized).strip()


def _is_non_assertive_context(normalized: str) -> bool:
    if normalized.endswith("?") or normalized.endswith("？"):
        return True
    if any(marker in normalized for marker in _EN_NON_ASSERTIVE_MARKERS):
        return True
    return any(marker in normalized for marker in _ZH_NON_ASSERTIVE_MARKERS)


def _has_local_negation(normalized: str, start: int, end: int) -> bool:
    window = normalized[max(0, start - 32) : min(len(normalized), end + 20)]
    if any(re.search(rf"\b{re.escape(marker)}\b", window) for marker in _EN_NEGATION_MARKERS):
        return True
    return any(marker in window for marker in _ZH_NEGATION_MARKERS)
