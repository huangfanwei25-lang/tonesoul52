"""Generate deterministic claim-to-evidence review reports."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .claim_patterns import CLAIM_RULES, ClaimRule, is_negated_scope_statement
from .evidence_levels import get_evidence_level

__ts_layer__ = "surface"
__ts_purpose__ = (
    "Phase 1 claim-to-evidence auditor report generation. Deterministic reviewer aid only."
)

SCHEMA_VERSION = "0.1.0"
SOURCE_DETERMINISTIC_RULE = "deterministic_rule"


@dataclass(frozen=True)
class ClaimFinding:
    """A single candidate claim-to-evidence mismatch."""

    finding_id: str
    line: int
    claim_text: str
    claim_type: str
    evidence_level: str
    risk: str
    reason: str
    suggested_weaker_wording: str
    cannot_verify: List[str]
    source: str = SOURCE_DETERMINISTIC_RULE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "line": self.line,
            "claim_text": self.claim_text,
            "claim_type": self.claim_type,
            "evidence_level": self.evidence_level,
            "risk": self.risk,
            "reason": self.reason,
            "suggested_weaker_wording": self.suggested_weaker_wording,
            "cannot_verify": list(self.cannot_verify),
            "source": self.source,
        }


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _trim_claim_text(line: str, max_len: int = 260) -> str:
    text = " ".join(line.lstrip("\ufeff").strip().split())
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "..."


def _finding_from_rule(rule: ClaimRule, line_no: int, line: str, index: int) -> ClaimFinding:
    # Validate evidence-level ids at construction time instead of silently emitting typos.
    get_evidence_level(rule.evidence_level)
    return ClaimFinding(
        finding_id=f"claim-evidence-{index:03d}",
        line=line_no,
        claim_text=_trim_claim_text(line),
        claim_type=rule.claim_type,
        evidence_level=rule.evidence_level,
        risk=rule.risk,
        reason=rule.reason,
        suggested_weaker_wording=rule.suggested_weaker_wording,
        cannot_verify=list(rule.cannot_verify),
    )


def _is_fence_marker(line: str) -> bool:
    return line.lstrip().startswith("```")


def _is_negative_scope_list_item(line: str, recent_lines: List[str]) -> bool:
    if not line.lstrip().startswith(("-", "*")):
        return False
    context = "\n".join(recent_lines[-5:]).lower()
    return any(
        marker in context
        for marker in (
            "not this",
            "should not be described as",
            "non-goals",
            "not allowed",
            "not asking for",
        )
    )


def _is_meta_commentary(line: str) -> bool:
    lower = line.lower()
    return any(
        marker in lower
        for marker in (
            "meta.not_for",
            "not_for",
            "prohibits",
            "forbidden claim",
            "claim-boundary",
            "example overclaim",
        )
    )


def extract_findings(text: str) -> List[ClaimFinding]:
    """Extract deterministic claim-risk findings from text."""

    findings: List[ClaimFinding] = []
    seen: set[tuple[int, str]] = set()
    recent_lines: List[str] = []
    in_code_fence = False
    for line_no, line in enumerate(text.splitlines(), start=1):
        if _is_fence_marker(line):
            in_code_fence = not in_code_fence
            recent_lines.append(line)
            continue
        if in_code_fence:
            recent_lines.append(line)
            continue
        if not line.strip():
            recent_lines.append(line)
            continue
        if _is_negative_scope_list_item(line, recent_lines) or _is_meta_commentary(line):
            recent_lines.append(line)
            continue
        for rule in CLAIM_RULES:
            for match in rule.iter_matches(line):
                if is_negated_scope_statement(line, match):
                    continue
                key = (line_no, rule.rule_id)
                if key in seen:
                    continue
                seen.add(key)
                findings.append(_finding_from_rule(rule, line_no, line, len(findings) + 1))
                break
        recent_lines.append(line)
    return findings


def review_text(
    text: str,
    source_path: str,
    *,
    generated_at: Optional[str] = None,
) -> Dict[str, Any]:
    """Return a JSON-serializable claim-to-evidence review report."""

    return {
        "schema_version": SCHEMA_VERSION,
        "source_path": source_path,
        "generated_at": generated_at or _utc_now(),
        "findings": [finding.to_dict() for finding in extract_findings(text)],
    }


def review_file(path: Path, *, generated_at: Optional[str] = None) -> Dict[str, Any]:
    """Read a UTF-8 file and return its claim-to-evidence review report."""

    text = path.read_text(encoding="utf-8")
    return review_text(text, str(path), generated_at=generated_at)
