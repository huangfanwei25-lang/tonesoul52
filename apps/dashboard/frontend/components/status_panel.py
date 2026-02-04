"""
Workspace status panel for system linkage and summaries.
"""

from __future__ import annotations

import html
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import streamlit as st

from utils.status import build_status_snapshot, load_latest_summary


def _format_timestamp(value: Optional[str]) -> str:
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return value


def _conversation_status_label(status: Optional[str]) -> str:
    if not status:
        return "未知"
    status_text = str(status).lower()
    label_map = {
        "success": "成功",
        "error": "失敗",
        "connection_error": "連線失敗",
        "exception": "例外",
        "empty_response": "空回覆",
    }
    return label_map.get(status_text, status_text)


def _intent_status_label(status: Optional[str]) -> str:
    if not status:
        return "未知"
    status_text = str(status).lower()
    label_map = {
        "achieved": "達成",
        "failed": "失敗",
        "inconclusive": "證據不足",
        "unknown": "未知",
    }
    return label_map.get(status_text, status_text)


def _control_status_label(status: Optional[str]) -> str:
    if not status:
        return "未知"
    status_text = str(status).lower()
    label_map = {
        "success": "成功",
        "failed": "失敗",
        "pending": "處理中",
        "unknown": "未知",
    }
    return label_map.get(status_text, status_text)


def _dimension_status_label(valid: Optional[bool]) -> str:
    if valid is None:
        return "未知"
    return "有效" if valid else "需調整"


def _format_number(value: object) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.2f}"
    if value is None:
        return "n/a"
    return str(value)


def _format_vector(vector: Optional[Dict[str, object]]) -> str:
    if not isinstance(vector, dict):
        return "向量未建立"
    delta_t = _format_number(vector.get("deltaT"))
    delta_s = _format_number(vector.get("deltaS"))
    delta_r = _format_number(vector.get("deltaR"))
    return f"ΔT {delta_t} · ΔS {delta_s} · ΔR {delta_r}"


def _truncate(text: str, limit: int = 140) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def _extract_intent_fields(payload: Optional[Dict[str, object]]) -> Dict[str, object]:
    if not payload:
        return {}
    audit = payload.get("audit") if isinstance(payload.get("audit"), dict) else {}
    status = audit.get("status") or payload.get("status")
    confidence = audit.get("confidence") if audit else payload.get("confidence")
    reason = audit.get("reason") or payload.get("reason")
    return {
        "status": status,
        "confidence": confidence,
        "reason": reason,
        "run_id": payload.get("_run_id"),
    }


def _extract_control_fields(payload: Optional[Dict[str, object]]) -> Dict[str, object]:
    if not payload:
        return {}
    return {
        "status": payload.get("status"),
        "log": payload.get("log"),
        "timestamp": payload.get("timestamp"),
        "screenshot_path": payload.get("screenshot_path"),
    }


def _summary_from_snapshot(snapshot: Dict[str, object]) -> Optional[Dict[str, object]]:
    conversation = snapshot.get("conversation", {})
    last_entry = conversation.get("last") if isinstance(conversation, dict) else None
    if not isinstance(last_entry, dict):
        return None

    context = last_entry.get("context") if isinstance(last_entry.get("context"), dict) else {}
    user_message = context.get("user_message") or last_entry.get("user_message") or ""
    response = last_entry.get("response") or ""

    persona = snapshot.get("persona", {})
    trace = persona.get("trace") if isinstance(persona.get("trace"), dict) else {}
    shadow = trace.get("shadow") if isinstance(trace.get("shadow"), dict) else {}

    return {
        "timestamp": last_entry.get("timestamp"),
        "status": last_entry.get("status"),
        "user_message": user_message,
        "assistant_summary": _truncate(response),
        "persona": {
            "id": persona.get("id"),
            "vector_estimate": shadow.get("vector_estimate"),
            "vector_distance": shadow.get("vector_distance"),
            "profile": persona.get("profile"),
        },
        "intent": _extract_intent_fields(snapshot.get("intent_verification")),
        "control": _extract_control_fields(snapshot.get("control_result")),
        "run_id": snapshot.get("run_id"),
    }


def render_status_panel(workspace: Path) -> None:
    snapshot = build_status_snapshot(workspace)
    summary = load_latest_summary(workspace) or _summary_from_snapshot(snapshot)

    conversation = snapshot.get("conversation", {})
    last_entry = conversation.get("last") if isinstance(conversation, dict) else {}
    conversation_status = _conversation_status_label(
        last_entry.get("status") if isinstance(last_entry, dict) else None
    )
    conversation_time = _format_timestamp(
        last_entry.get("timestamp") if isinstance(last_entry, dict) else None
    )
    conversation_count = conversation.get("count") if isinstance(conversation, dict) else 0

    persona = snapshot.get("persona", {})
    trace = persona.get("trace") if isinstance(persona.get("trace"), dict) else {}
    shadow = trace.get("shadow") if isinstance(trace.get("shadow"), dict) else {}
    vector_text = _format_vector(shadow.get("vector_estimate"))

    dimension = snapshot.get("dimension", {}).get("last") or {}
    dimension_valid = dimension.get("valid") if isinstance(dimension, dict) else None
    dimension_label = _dimension_status_label(dimension_valid)
    reasons = dimension.get("reasons") if isinstance(dimension.get("reasons"), list) else []
    reason_text = " / ".join(str(r) for r in reasons[:2]) if reasons else "無"

    intent_fields = _extract_intent_fields(snapshot.get("intent_verification"))
    intent_label = _intent_status_label(intent_fields.get("status"))
    intent_confidence = intent_fields.get("confidence")
    intent_conf_text = _format_number(intent_confidence) if intent_confidence is not None else "n/a"
    intent_reason = intent_fields.get("reason") or "無"

    control_fields = _extract_control_fields(snapshot.get("control_result"))
    control_label = _control_status_label(control_fields.get("status"))
    control_log = control_fields.get("log") or "無"
    control_time = _format_timestamp(control_fields.get("timestamp"))

    persona_id = persona.get("id") or "base"

    st.markdown('<div class="ts-section-title">功能聯動狀態</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="ts-card">
          <div class="ts-pill">狀態摘要</div>
          <p class="ts-muted">對話記錄: {conversation_count} · {conversation_time or "尚無"} · {conversation_status}</p>
          <p class="ts-muted">人格追蹤: {html.escape(persona_id)} · {html.escape(vector_text)}</p>
          <p class="ts-muted">人格維度: {dimension_label} · {html.escape(reason_text)}</p>
          <p class="ts-muted">意圖驗證: {intent_label} · 信心 {html.escape(intent_conf_text)} · {html.escape(intent_reason)}</p>
          <p class="ts-muted">控制結果: {control_label} · {html.escape(_truncate(control_log, 60))}</p>
          <p class="ts-muted">控制時間: {control_time or "尚無"}</p>
          <p class="ts-muted">摘要記錄: {snapshot.get("summary_count", 0)} 筆</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="ts-section-title">對話摘要</div>', unsafe_allow_html=True)
    if summary:
        summary_time = _format_timestamp(summary.get("timestamp"))
        summary_status = _conversation_status_label(summary.get("status"))
        summary_persona = summary.get("persona") if isinstance(summary.get("persona"), dict) else {}
        summary_intent = summary.get("intent") if isinstance(summary.get("intent"), dict) else {}
        summary_control = summary.get("control") if isinstance(summary.get("control"), dict) else {}

        summary_intent_label = _intent_status_label(summary_intent.get("status"))
        summary_control_label = _control_status_label(summary_control.get("status"))
        run_id = summary.get("run_id") or snapshot.get("run_id") or "n/a"

        st.markdown(
            f"""
            <div class="ts-card">
              <div class="ts-pill">最新摘要</div>
              <p class="ts-muted">時間: {summary_time or "尚無"}</p>
              <p class="ts-muted">狀態: {summary_status}</p>
              <p class="ts-muted">人格: {html.escape(summary_persona.get("id") or persona_id)}</p>
              <p class="ts-muted">意圖: {summary_intent_label} · 控制: {summary_control_label}</p>
              <p class="ts-muted">Run: {html.escape(str(run_id))}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.text_area("使用者摘要", summary.get("user_message") or "", height=70)
        st.text_area("助手摘要", summary.get("assistant_summary") or "", height=90)
    else:
        st.caption("尚無對話摘要，完成一次對話後會自動生成。")

    profile = persona.get("profile") if isinstance(persona.get("profile"), dict) else {}
    with st.expander("人格板模（Architecture B）", expanded=False):
        if not profile:
            st.caption("尚未載入人格檔案。")
            return
        home_vector = (
            profile.get("home_vector") if isinstance(profile.get("home_vector"), dict) else {}
        )
        tolerance = profile.get("tolerance") if isinstance(profile.get("tolerance"), dict) else {}
        council_weights = (
            profile.get("council_weights")
            if isinstance(profile.get("council_weights"), dict)
            else {}
        )
        goal_weights = (
            profile.get("goal_weights") if isinstance(profile.get("goal_weights"), dict) else {}
        )
        vector_estimate = (
            shadow.get("vector_estimate") if isinstance(shadow.get("vector_estimate"), dict) else {}
        )
        vector_distance = (
            shadow.get("vector_distance") if isinstance(shadow.get("vector_distance"), dict) else {}
        )

        st.markdown(
            f"**人格**: {profile.get('name') or persona_id} ({profile.get('id') or persona_id})"
        )
        st.markdown(
            f"- Home Vector: ΔT {_format_number(home_vector.get('deltaT'))} · ΔS {_format_number(home_vector.get('deltaS'))} · ΔR {_format_number(home_vector.get('deltaR'))}"
        )
        st.markdown(
            f"- 容忍區間: ΔT ±{_format_number(tolerance.get('deltaT'))} · ΔS ±{_format_number(tolerance.get('deltaS'))} · ΔR ±{_format_number(tolerance.get('deltaR'))}"
        )
        if council_weights:
            st.markdown(
                "- Council 權重: "
                f"Guardian {council_weights.get('guardian', 'n/a')}, "
                f"Analyst {council_weights.get('analyst', 'n/a')}, "
                f"Critic {council_weights.get('critic', 'n/a')}, "
                f"Advocate {council_weights.get('advocate', 'n/a')}"
            )
        if goal_weights:
            st.markdown(
                "- 目標權重: "
                + ", ".join(
                    f"{key}={_format_number(value)}"
                    for key, value in goal_weights.items()
                    if isinstance(value, (int, float))
                )
            )
        if vector_estimate:
            st.markdown(f"- 最新向量: {_format_vector(vector_estimate)}")
        if vector_distance:
            st.markdown(
                "- 距離量測: "
                f"mean {_format_number(vector_distance.get('mean'))} · "
                f"max {_format_number(vector_distance.get('max'))}"
            )
