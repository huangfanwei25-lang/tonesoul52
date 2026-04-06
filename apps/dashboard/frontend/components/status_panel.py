"""
Tier-aligned status panel for the dashboard workspace.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st
from utils.status import build_status_snapshot, load_latest_summary


def _format_timestamp(value: object) -> str:
    if not value:
        return "n/a"
    text = str(value)
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return text


def _format_conversation_status(value: object) -> str:
    status = str(value or "").strip().lower()
    label_map = {
        "success": "可用",
        "error": "錯誤",
        "connection_error": "連線錯誤",
        "exception": "例外",
        "empty_response": "空回應",
    }
    return label_map.get(status, status or "未知")


def _format_intent_status(value: object) -> str:
    status = str(value or "").strip().lower()
    label_map = {
        "achieved": "達成",
        "failed": "失敗",
        "inconclusive": "未定",
        "unknown": "未知",
    }
    return label_map.get(status, status or "未知")


def _format_control_status(value: object) -> str:
    status = str(value or "").strip().lower()
    label_map = {
        "success": "成功",
        "failed": "失敗",
        "pending": "等待中",
        "unknown": "未知",
    }
    return label_map.get(status, status or "未知")


def _truncate(text: object, limit: int = 120) -> str:
    value = str(text or "").strip()
    if len(value) <= limit:
        return value
    return value[:limit].rstrip() + "..."


def build_status_panel_view_model(
    *,
    snapshot: dict[str, Any],
    summary: dict[str, Any] | None,
    tier0_shell: dict[str, Any] | None,
    tier1_shell: dict[str, Any] | None,
    tier2_drawer: dict[str, Any] | None,
) -> dict[str, Any]:
    tier0_shell = tier0_shell or {}
    tier1_shell = tier1_shell or {}
    tier2_drawer = tier2_drawer or {}
    conversation = snapshot.get("conversation") if isinstance(snapshot.get("conversation"), dict) else {}
    last_entry = conversation.get("last") if isinstance(conversation.get("last"), dict) else {}
    intent = summary.get("intent") if isinstance((summary or {}).get("intent"), dict) else {}
    control = summary.get("control") if isinstance((summary or {}).get("control"), dict) else {}
    persona = summary.get("persona") if isinstance((summary or {}).get("persona"), dict) else {}

    parity_counts = tier1_shell.get("parity_counts") if isinstance(tier1_shell.get("parity_counts"), dict) else {}
    observer_shell = tier1_shell.get("observer_shell") if isinstance(tier1_shell.get("observer_shell"), dict) else {}
    closeout_attention = (
        tier1_shell.get("closeout_attention")
        if isinstance(tier1_shell.get("closeout_attention"), dict)
        else {}
    )

    return {
        "operator_posture": {
            "title": "Tier-aligned Operator Status",
            "note": (
                "這個面板只做 tier 狀態對齊。真正的操作真相仍在 Tier 0 / Tier 1 shell，"
                "Tier 2 只在需要時展開。"
            ),
        },
        "tier0": {
            "readiness": str(tier0_shell.get("readiness_status", "")).strip() or "unknown",
            "task_track": str(tier0_shell.get("task_track", "")).strip() or "unclassified",
            "deliberation_mode": str(tier0_shell.get("deliberation_mode", "")).strip() or "unknown",
            "next_followup_command": str(
                (tier0_shell.get("next_followup") or {}).get("command", "")
            ).strip(),
            "receiver_rule": str(tier0_shell.get("receiver_rule", "")).strip(),
            "hook_badges": list(tier0_shell.get("hook_badges") or [])[:3],
        },
        "tier1": {
            "short_board": str(
                ((tier1_shell.get("canonical_cards") or {}).get("short_board", ""))
            ).strip()
            or "current short board not visible",
            "source_precedence": str(
                ((tier1_shell.get("canonical_cards") or {}).get("source_precedence", ""))
            ).strip(),
            "successor_correction": str(
                ((tier1_shell.get("canonical_cards") or {}).get("successor_correction", ""))
            ).strip(),
            "closeout_attention": str(closeout_attention.get("summary_text", "")).strip(),
            "observer_summary": str(observer_shell.get("summary_text", "")).strip(),
            "parity_counts": {
                "baseline": int(parity_counts.get("baseline", 0) or 0),
                "beta_usable": int(parity_counts.get("beta_usable", 0) or 0),
                "partial": int(parity_counts.get("partial", 0) or 0),
                "deferred": int(parity_counts.get("deferred", 0) or 0),
            },
        },
        "tier2": {
            "recommended_open": bool(tier2_drawer.get("recommended_open")),
            "trigger_reasons": list(tier2_drawer.get("trigger_reasons") or [])[:4],
            "active_groups": list(tier2_drawer.get("active_group_names") or [])[:3],
            "summary_text": str(tier2_drawer.get("summary_text", "")).strip(),
            "next_pull_commands": list(tier2_drawer.get("next_pull_commands") or [])[:2],
        },
        "telemetry": {
            "conversation_status": _format_conversation_status(last_entry.get("status")),
            "conversation_count": int(conversation.get("count", 0) or 0),
            "conversation_time": _format_timestamp(last_entry.get("timestamp")),
            "intent_status": _format_intent_status(intent.get("status")),
            "control_status": _format_control_status(control.get("status")),
            "persona_id": str(persona.get("id", "")).strip() or str(snapshot.get("persona", {}).get("id", "base")),
            "run_id": str((summary or {}).get("run_id") or snapshot.get("run_id") or "n/a"),
            "user_message": _truncate((summary or {}).get("user_message", "")),
            "assistant_summary": _truncate((summary or {}).get("assistant_summary", "")),
        },
    }


def render_status_panel(
    workspace: Path,
    *,
    tier0_shell: dict[str, Any] | None = None,
    tier1_shell: dict[str, Any] | None = None,
    tier2_drawer: dict[str, Any] | None = None,
) -> None:
    snapshot = build_status_snapshot(workspace)
    summary = load_latest_summary(workspace)
    view_model = build_status_panel_view_model(
        snapshot=snapshot,
        summary=summary,
        tier0_shell=tier0_shell,
        tier1_shell=tier1_shell,
        tier2_drawer=tier2_drawer,
    )

    operator_posture = view_model["operator_posture"]
    tier0 = view_model["tier0"]
    tier1 = view_model["tier1"]
    tier2 = view_model["tier2"]
    telemetry = view_model["telemetry"]

    st.markdown("### Tier-Aligned Status")
    st.caption(operator_posture["note"])

    with st.container(border=True):
        st.markdown("**Tier 0 · Instant Gate**")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Readiness", tier0["readiness"])
        with col_b:
            st.metric("Track", tier0["task_track"])
        with col_c:
            st.metric("Mode", tier0["deliberation_mode"])

        if tier0["next_followup_command"]:
            st.caption("Next bounded move")
            st.code(tier0["next_followup_command"], language="bash")
        if tier0["receiver_rule"]:
            st.caption(tier0["receiver_rule"])
        if tier0["hook_badges"]:
            st.caption(
                "Hooks: "
                + " | ".join(
                    f"{item.get('name', 'unknown')}:{item.get('status', 'unknown')}"
                    for item in tier0["hook_badges"]
                )
            )

    with st.container(border=True):
        st.markdown("**Tier 1 · Orientation Shell**")
        st.markdown(tier1["short_board"])
        if tier1["successor_correction"]:
            st.caption(tier1["successor_correction"])
        if tier1["closeout_attention"]:
            st.warning(tier1["closeout_attention"])
        elif tier1["observer_summary"]:
            st.caption(tier1["observer_summary"])

        parity_cols = st.columns(4)
        for col, (label, key) in zip(
            parity_cols,
            [
                ("Baseline", "baseline"),
                ("Beta", "beta_usable"),
                ("Partial", "partial"),
                ("Deferred", "deferred"),
            ],
        ):
            with col:
                st.metric(label, tier1["parity_counts"][key])

        if tier1["source_precedence"]:
            with st.expander("Source precedence", expanded=False):
                st.caption(tier1["source_precedence"])

    with st.container(border=True):
        st.markdown("**Tier 2 · Deep Governance**")
        if tier2["recommended_open"]:
            st.warning(
                "Only open when needed: " + ", ".join(tier2["trigger_reasons"])
                if tier2["trigger_reasons"]
                else "Only open when needed."
            )
        else:
            st.caption("Manual only. Keep deep governance behind explicit operator pull.")

        if tier2["active_groups"]:
            st.caption("Active groups: " + " | ".join(tier2["active_groups"]))
        if tier2["summary_text"]:
            st.caption(tier2["summary_text"])
        if tier2["next_pull_commands"]:
            with st.expander("Suggested deep pulls", expanded=False):
                for command in tier2["next_pull_commands"]:
                    st.code(command, language="bash")

    with st.expander("Secondary telemetry", expanded=False):
        st.markdown(
            f"- Conversation: `{telemetry['conversation_status']}`"
            f" | count={telemetry['conversation_count']}"
            f" | last={telemetry['conversation_time']}"
        )
        st.markdown(
            f"- Intent / Control: `{telemetry['intent_status']}` / `{telemetry['control_status']}`"
        )
        st.markdown(f"- Persona: `{telemetry['persona_id']}` | Run: `{telemetry['run_id']}`")
        if telemetry["user_message"]:
            st.text_area("Latest user message", telemetry["user_message"], height=70)
        if telemetry["assistant_summary"]:
            st.text_area("Latest assistant summary", telemetry["assistant_summary"], height=90)
