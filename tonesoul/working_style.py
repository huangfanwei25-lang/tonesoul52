from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List

_STYLE_TOKEN_RE = re.compile(r"[a-z0-9_]+")
_STYLE_STOPWORDS = {
    "about",
    "after",
    "again",
    "before",
    "broad",
    "clear",
    "current",
    "default",
    "defaults",
    "explicit",
    "first",
    "from",
    "guide",
    "habit",
    "habits",
    "into",
    "keep",
    "latest",
    "must",
    "next",
    "only",
    "over",
    "prefer",
    "review",
    "route",
    "should",
    "state",
    "still",
    "that",
    "then",
    "these",
    "this",
    "until",
    "use",
    "when",
    "with",
    "write",
}


def _style_tokens(text: Any) -> set[str]:
    lowered = str(text or "").strip().lower()
    if not lowered:
        return set()
    return {
        token
        for token in _STYLE_TOKEN_RE.findall(lowered)
        if len(token) >= 4 and token not in _STYLE_STOPWORDS
    }


def _collect_signal_texts(
    *,
    carry_forward: Iterable[Any] | None = None,
    next_actions: Iterable[Any] | None = None,
    routing_summary: Dict[str, Any] | None = None,
) -> List[Dict[str, str]]:
    signals: List[Dict[str, str]] = []

    for text in carry_forward or []:
        normalized = str(text or "").strip()
        if normalized:
            signals.append({"source": "carry_forward", "text": normalized})

    for text in next_actions or []:
        normalized = str(text or "").strip()
        if normalized:
            signals.append({"source": "next_actions", "text": normalized})

    routing_summary = dict(routing_summary or {})
    summary_text = str(routing_summary.get("summary_text", "")).strip()
    if summary_text:
        signals.append({"source": "routing_summary", "text": summary_text})
    for event in list(routing_summary.get("recent_events") or [])[:5]:
        normalized = str(event.get("summary", "")).strip()
        if normalized:
            signals.append({"source": "routing_event", "text": normalized})

    return signals


def build_working_style_observability(
    anchor: Dict[str, Any],
    *,
    carry_forward: Iterable[Any] | None = None,
    next_actions: Iterable[Any] | None = None,
    routing_summary: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    if not anchor:
        return {}

    signals = _collect_signal_texts(
        carry_forward=carry_forward,
        next_actions=next_actions,
        routing_summary=routing_summary,
    )
    signal_sources = sorted({signal["source"] for signal in signals})

    trackable_items: List[tuple[str, str]] = []
    for field in ("decision_preferences", "verified_routines"):
        for value in list(anchor.get(field) or []):
            normalized = str(value or "").strip()
            if normalized:
                trackable_items.append((field, normalized))

    if not trackable_items:
        return {
            "status": "not_trackable",
            "drift_risk": "medium",
            "trackable_item_count": 0,
            "reinforced_item_count": 0,
            "signal_count": len(signals),
            "signal_sources": signal_sources,
            "reinforced_items": [],
            "unreinforced_items": [],
            "summary_text": "working_style=not_trackable reinforced=0/0 drift=medium",
            "receiver_note": (
                "A working-style anchor is visible, but no decision preferences or verified routines are structured enough to track for reinforcement yet."
            ),
        }

    reinforced_items: List[str] = []
    unreinforced_items: List[str] = []
    for field, value in trackable_items:
        item_tokens = _style_tokens(value)
        matched = False
        for signal in signals:
            signal_tokens = _style_tokens(signal["text"])
            if item_tokens and signal_tokens and item_tokens & signal_tokens:
                matched = True
                break
        labeled = f"{field}: {value}"
        if matched:
            reinforced_items.append(labeled)
        else:
            unreinforced_items.append(labeled)

    trackable_count = len(trackable_items)
    reinforced_count = len(reinforced_items)
    if reinforced_count == 0:
        status = "unreinforced"
        drift_risk = "high"
        receiver_note = "No recent handoff surface re-echoes the shared working style. Apply the playbook explicitly if it still fits, and expect model-native drift unless new evidence appears."
    elif reinforced_count < trackable_count:
        status = "partial"
        drift_risk = "medium"
        receiver_note = "Only part of the shared working style is echoed by recent handoff surfaces. Keep the playbook visible instead of assuming full continuity."
    else:
        status = "reinforced"
        drift_risk = "low"
        receiver_note = "Recent handoff surfaces re-echo the shared working style. Apply it as a bounded workflow habit, but do not promote it into policy or identity."

    return {
        "status": status,
        "drift_risk": drift_risk,
        "trackable_item_count": trackable_count,
        "reinforced_item_count": reinforced_count,
        "signal_count": len(signals),
        "signal_sources": signal_sources,
        "reinforced_items": reinforced_items,
        "unreinforced_items": unreinforced_items,
        "summary_text": (
            f"working_style={status} reinforced={reinforced_count}/{trackable_count} "
            f"signals={len(signals)} drift={drift_risk}"
        ),
        "receiver_note": receiver_note,
    }


def build_working_style_import_limits(
    anchor: Dict[str, Any],
    *,
    observability: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    if not anchor:
        return {}

    observability = dict(observability or {})
    status = str(observability.get("status", "")).strip() or "unknown"
    drift_risk = str(observability.get("drift_risk", "")).strip() or "medium"

    safe_apply: List[str] = []
    if list(anchor.get("decision_preferences") or []):
        safe_apply.append(
            "scan_order: use shared packet/claim surfaces before widening the repo scan when they still fit the task."
        )
        safe_apply.append(
            "evidence_handling: keep the shared evidence discipline instead of replacing it with model-native guessing."
        )
    if list(anchor.get("prompt_defaults") or []):
        safe_apply.append(
            "prompt_shape: keep goal function and P0/P1/P2 explicit when a prompt is doing transfer, extraction, or bounded review work."
        )
    if list(anchor.get("verified_routines") or []):
        safe_apply.append(
            "session_cadence: preserve the shared start/end rhythm when collaborative work is actually happening."
        )
    if str(anchor.get("render_caveat", "")).strip():
        safe_apply.append(
            "render_interpretation: treat shell mojibake as a render-layer suspicion before declaring the file itself corrupted."
        )

    safe_apply = safe_apply[:5]

    must_not_import = [
        "vows_or_permissions: working style must not rewrite what the system is allowed to do.",
        "canonical_governance_truth: habits must not become runtime law, axiom enforcement, or authority truth.",
        "durable_identity: style continuity must not silently become stable selfhood or subject promotion.",
        "task_scope_or_success_criteria: inherited habits must not override the current task's objective or human-given scope.",
    ]

    if status == "reinforced":
        apply_posture = "bounded_default"
        receiver_guidance = "Recent handoff surfaces still echo this style, so it may be used as the default working rhythm for the current session."
    elif status == "partial":
        apply_posture = "explicit_reuse_only"
        receiver_guidance = "Only part of the shared style is still echoed. Reuse it deliberately and keep checking task-local evidence instead of assuming full continuity."
    else:
        apply_posture = "review_before_apply"
        receiver_guidance = "Recent shared surfaces no longer echo this style strongly enough. Review it first; only reuse the parts that still fit the current task."

    stop_conditions = [
        "current task or human instruction conflicts with the inherited habit",
        "shared surfaces show recycled carry-forward without new evidence",
        "a newer subject snapshot or compaction points to a different routine",
    ]
    if drift_risk == "high":
        stop_conditions.append(
            "working-style observability is high-drift or unreinforced, so habits must not be assumed silently"
        )

    return {
        "apply_posture": apply_posture,
        "safe_apply": safe_apply,
        "must_not_import": must_not_import,
        "stop_conditions": stop_conditions,
        "receiver_guidance": receiver_guidance,
        "summary_text": (
            f"working_style_import={apply_posture} safe={len(safe_apply)} "
            f"blocked={len(must_not_import)} drift={drift_risk}"
        ),
    }


def build_working_style_continuity_validation(
    *,
    anchor: Dict[str, Any],
    playbook: Dict[str, Any],
    observability: Dict[str, Any] | None = None,
    import_limits: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    observability = dict(observability or {})
    import_limits = dict(import_limits or {})

    checks = {
        "anchor_visible": bool(anchor),
        "playbook_visible": bool(playbook.get("present")),
        "observability_visible": bool(observability),
        "import_limits_visible": bool(import_limits),
        "non_promotion_guard_visible": bool(playbook.get("non_promotion_rule"))
        or bool(import_limits.get("must_not_import")),
    }
    passed = sum(1 for value in checks.values() if value)
    total = len(checks)
    score = round(passed / total, 2) if total else 0.0

    status = "insufficient"
    if checks["anchor_visible"] and checks["playbook_visible"] and checks["import_limits_visible"]:
        status = "sufficient"
        if str(observability.get("status", "")).strip() in {"partial", "unreinforced"}:
            status = "caution"

    if not checks["anchor_visible"]:
        receiver_note = "No shared working-style anchor is visible yet. This session can still proceed, but style continuity cannot be validated."
    elif status == "sufficient":
        receiver_note = "A fresh agent has enough shared style material to inherit bounded operating habits without confusing them with policy or identity."
    elif status == "caution":
        receiver_note = "A fresh agent can inherit bounded working style, but recent shared surfaces do not fully reinforce it, so explicit reuse beats assumption."
    else:
        receiver_note = "Shared working-style continuity is incomplete. The agent should fall back to repo-level discipline rather than improvising from partial residue."

    return {
        "status": status,
        "score": score,
        "checks": checks,
        "summary_text": f"working_style_validation={status} score={score:.2f} checks={passed}/{total}",
        "receiver_note": receiver_note,
    }


def build_working_style_playbook(anchor: Dict[str, Any]) -> Dict[str, Any]:
    if not anchor:
        return {
            "present": False,
            "summary_text": "",
            "checklist": [],
            "application_rule": (
                "No shared working-style anchor is visible; default to repo-level prompt discipline and current task constraints."
            ),
            "non_promotion_rule": (
                "Without a visible working-style anchor, do not infer habits into durable identity or governance truth."
            ),
        }

    checklist: List[str] = []
    for preference in list(anchor.get("decision_preferences") or [])[:2]:
        text = str(preference or "").strip()
        if text:
            checklist.append(f"Preference: {text}")
    for routine in list(anchor.get("verified_routines") or [])[:2]:
        text = str(routine or "").strip()
        if text:
            checklist.append(f"Routine: {text}")
    for prompt_default in list(anchor.get("prompt_defaults") or [])[:2]:
        text = str(prompt_default or "").strip()
        if text:
            checklist.append(f"Prompt default: {text}")

    render_caveat = str(anchor.get("render_caveat", "")).strip()
    if render_caveat:
        checklist.append(f"Render caveat: {render_caveat}")

    summary_text = str(anchor.get("summary", "")).strip()
    if not summary_text and checklist:
        summary_text = " | ".join(checklist[:2])

    return {
        "present": True,
        "summary_text": summary_text,
        "checklist": checklist,
        "application_rule": (
            "Apply these items as bounded operating habits for scan order, evidence handling, and prompt shape."
        ),
        "non_promotion_rule": (
            "Do not promote this playbook into vows, canonical rules, or durable identity without fresh evidence and explicit review."
        ),
    }
