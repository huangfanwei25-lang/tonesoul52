import json
import os
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

from .ystm.schema import utc_now


@dataclass
class Intent:
    surface: str
    deep: Optional[str]
    success_criteria: List[str]


@dataclass
class Evidence:
    before_screenshot: Optional[str] = None
    after_screenshot: Optional[str] = None
    diff_score: Optional[float] = None
    ocr_result: Optional[str] = None
    action_log: Optional[str] = None
    timestamp: Optional[str] = None
    status: Optional[str] = None
    intent_achieved: Optional[bool] = None
    actual_result: Optional[str] = None

    def has_signal(self) -> bool:
        return any(
            [
                self.before_screenshot,
                self.after_screenshot,
                self.diff_score is not None,
                self.ocr_result,
                self.action_log,
                self.status,
                self.intent_achieved is not None,
                self.actual_result,
            ]
        )


@dataclass
class AuditResult:
    status: str
    confidence: float
    reason: str
    actual_result: Optional[str] = None


class IntentAnalyzer:
    """Build a minimal intent record from the compiled context."""

    def analyze(self, context: Dict[str, object]) -> Intent:
        ctx = context.get("context", {}) if isinstance(context, dict) else {}
        surface = str(ctx.get("task") or ctx.get("objective") or "").strip()
        deep = str(ctx.get("objective") or ctx.get("task") or "").strip() or None
        criteria = ctx.get("success_criteria")
        if isinstance(criteria, list):
            success_criteria = [str(item).strip() for item in criteria if str(item).strip()]
        else:
            success_criteria = []
        if not success_criteria:
            if deep:
                success_criteria.append(deep)
            elif surface:
                success_criteria.append(surface)
        return Intent(surface=surface, deep=deep, success_criteria=success_criteria)


class EvidenceCollector:
    """Normalize optional evidence payload into a compact structure."""

    def collect(self, payload: Optional[Dict[str, object]]) -> Evidence:
        if not isinstance(payload, dict):
            return Evidence()

        before = payload.get("before_screenshot") or payload.get("before")
        after = (
            payload.get("after_screenshot")
            or payload.get("after")
            or payload.get("screenshot_path")
        )
        diff_score = payload.get("diff_score")
        if diff_score is None:
            diff_detected = payload.get("diff_detected")
            if isinstance(diff_detected, bool):
                diff_score = 1.0 if diff_detected else 0.0
        ocr_result = payload.get("ocr_result") or payload.get("ocr")
        action_log = payload.get("action_log") or payload.get("log") or payload.get("command")
        timestamp = payload.get("timestamp")
        status = payload.get("status")
        intent_achieved = _coerce_bool(payload.get("intent_achieved"))
        if intent_achieved is None and isinstance(status, str):
            lowered = status.lower()
            if lowered in {"success", "succeeded", "ok"}:
                intent_achieved = True
            elif lowered in {"failed", "error"}:
                intent_achieved = False
        actual_result = payload.get("actual_result") or ocr_result

        return Evidence(
            before_screenshot=before,
            after_screenshot=after,
            diff_score=_coerce_float(diff_score),
            ocr_result=_string_or_none(ocr_result),
            action_log=_string_or_none(action_log),
            timestamp=_string_or_none(timestamp),
            status=_string_or_none(status),
            intent_achieved=intent_achieved,
            actual_result=_string_or_none(actual_result),
        )


class SelfAuditor:
    """Evaluate intent achievement based on available evidence."""

    def audit(self, intent: Intent, evidence: Evidence) -> AuditResult:
        if not evidence.has_signal():
            return AuditResult(
                status="inconclusive",
                confidence=0.2,
                reason="no_evidence",
            )

        if evidence.intent_achieved is not None:
            return AuditResult(
                status="achieved" if evidence.intent_achieved else "failed",
                confidence=0.9 if evidence.intent_achieved else 0.6,
                reason="explicit_signal",
                actual_result=evidence.actual_result or evidence.action_log or evidence.ocr_result,
            )

        status = (evidence.status or "").lower()
        if status in {"success", "succeeded", "ok"}:
            return AuditResult(
                status="achieved",
                confidence=0.7,
                reason="status_success",
                actual_result=evidence.actual_result or evidence.action_log or evidence.ocr_result,
            )
        if status in {"failed", "error"}:
            return AuditResult(
                status="failed",
                confidence=0.6,
                reason="status_failed",
                actual_result=evidence.actual_result or evidence.action_log or evidence.ocr_result,
            )

        if intent.success_criteria and _criteria_met(intent.success_criteria, evidence):
            return AuditResult(
                status="achieved",
                confidence=0.6,
                reason="criteria_match",
                actual_result=evidence.actual_result or evidence.action_log or evidence.ocr_result,
            )

        if _contains_failure_signal(evidence):
            return AuditResult(
                status="failed",
                confidence=0.4,
                reason="failure_signal",
                actual_result=evidence.actual_result or evidence.action_log or evidence.ocr_result,
            )

        return AuditResult(
            status="inconclusive",
            confidence=0.3,
            reason="insufficient_evidence",
            actual_result=evidence.actual_result or evidence.action_log or evidence.ocr_result,
        )


def build_intent_verification(
    context_payload: Dict[str, object],
    evidence_path: Optional[str] = None,
) -> Dict[str, object]:
    analyzer = IntentAnalyzer()
    intent = analyzer.analyze(context_payload)

    evidence_payload = _load_json(evidence_path) if evidence_path else None
    evidence = EvidenceCollector().collect(evidence_payload)
    audit = SelfAuditor().audit(intent, evidence)

    payload = {
        "generated_at": utc_now(),
        "intent": asdict(intent),
        "evidence": asdict(evidence),
        "audit": asdict(audit),
    }
    if evidence_path:
        payload["source"] = {"evidence_path": evidence_path}
    return payload


def _load_json(path: Optional[str]) -> Optional[Dict[str, object]]:
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8-sig") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _coerce_bool(value: object) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "1"}:
            return True
        if lowered in {"false", "no", "0"}:
            return False
    return None


def _coerce_float(value: object) -> Optional[float]:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _string_or_none(value: object) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _criteria_met(criteria: List[str], evidence: Evidence) -> bool:
    haystack = " ".join(
        [
            evidence.action_log or "",
            evidence.ocr_result or "",
            evidence.actual_result or "",
        ]
    ).lower()
    for item in criteria:
        if item and item.lower() in haystack:
            return True
    return False


def _contains_failure_signal(evidence: Evidence) -> bool:
    haystack = " ".join(
        [
            evidence.action_log or "",
            evidence.ocr_result or "",
            evidence.actual_result or "",
        ]
    ).lower()
    for token in ("fail", "failed", "error", "exception"):
        if token in haystack:
            return True
    return False
