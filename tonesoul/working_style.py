from __future__ import annotations

from typing import Any, Dict, List


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
