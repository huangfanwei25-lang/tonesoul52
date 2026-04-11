"""
Tier-aligned status panel for the dashboard workspace.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st
from utils.status import build_status_snapshot, load_latest_summary

_REPO_ROOT = Path(__file__).resolve().parents[4]
_SELF_IMPROVEMENT_STATUS_PATH = (
    _REPO_ROOT / "docs" / "status" / "self_improvement_trial_wave_latest.json"
)


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
        "success": "成功",
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
        "pending": "待處理",
        "unknown": "未知",
    }
    return label_map.get(status, status or "未知")


def _truncate(text: object, limit: int = 120) -> str:
    value = str(text or "").strip()
    if len(value) <= limit:
        return value
    return value[:limit].rstrip() + "..."


def _load_self_improvement_result_cue() -> dict[str, Any]:
    default = {
        "present": False,
        "summary_text": "",
        "top_result": "",
        "next_action": "",
        "receiver_rule": "",
        "source_path": "",
        "outcome_counts": {},
    }
    if not _SELF_IMPROVEMENT_STATUS_PATH.exists():
        return default

    try:
        payload = json.loads(_SELF_IMPROVEMENT_STATUS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default

    candidates = list(payload.get("candidates") or [])
    primary = next(
        (
            item
            for item in candidates
            if str(((item.get("analyzer_closeout") or {}).get("status") or "")).strip() == "promote"
        ),
        candidates[0] if candidates else {},
    )
    candidate_record = primary.get("candidate_record") or {}
    closeout = primary.get("analyzer_closeout") or {}
    result_surface = primary.get("result_surface") or {}
    outcome_counts = payload.get("outcome_counts") or {}

    candidate_id = str(candidate_record.get("candidate_id", "")).strip()
    surface_status = str(result_surface.get("surface_status", "")).strip()
    top_result = " / ".join(part for part in [candidate_id, surface_status] if part)
    summary_text = str(payload.get("summary_text", "")).strip()
    if summary_text:
        summary_text += " | status surface only"

    return {
        "present": True,
        "summary_text": summary_text,
        "top_result": top_result,
        "next_action": str(closeout.get("next_action", "")).strip(),
        "receiver_rule": (
            "Secondary only. Open the dedicated self-improvement status surface before treating any trial result as guidance."
        ),
        "source_path": "docs/status/self_improvement_trial_wave_latest.md",
        "outcome_counts": {
            "promote": int(outcome_counts.get("promote", 0) or 0),
            "park": int(outcome_counts.get("park", 0) or 0),
            "retire": int(outcome_counts.get("retire", 0) or 0),
            "blocked": int(outcome_counts.get("blocked", 0) or 0),
        },
    }


def build_status_panel_view_model(
    *,
    snapshot: dict[str, Any],
    summary: dict[str, Any] | None,
    tier0_shell: dict[str, Any] | None,
    tier1_shell: dict[str, Any] | None,
    tier2_drawer: dict[str, Any] | None,
    improvement_cue: dict[str, Any] | None = None,
) -> dict[str, Any]:
    tier0_shell = tier0_shell or {}
    tier1_shell = tier1_shell or {}
    tier2_drawer = tier2_drawer or {}
    conversation = (
        snapshot.get("conversation") if isinstance(snapshot.get("conversation"), dict) else {}
    )
    last_entry = conversation.get("last") if isinstance(conversation.get("last"), dict) else {}
    intent = summary.get("intent") if isinstance((summary or {}).get("intent"), dict) else {}
    control = summary.get("control") if isinstance((summary or {}).get("control"), dict) else {}
    persona = summary.get("persona") if isinstance((summary or {}).get("persona"), dict) else {}

    parity_counts = (
        tier1_shell.get("parity_counts")
        if isinstance(tier1_shell.get("parity_counts"), dict)
        else {}
    )
    observer_shell = (
        tier1_shell.get("observer_shell")
        if isinstance(tier1_shell.get("observer_shell"), dict)
        else {}
    )
    closeout_attention = (
        tier1_shell.get("closeout_attention")
        if isinstance(tier1_shell.get("closeout_attention"), dict)
        else {}
    )
    improvement_cue = improvement_cue or {}

    return {
        "operator_posture": {
            "title": "Tier-aligned Operator Status",
            "note": (
                "先讀 Tier 0 / Tier 1 shell，再決定是否真的需要打開 Tier 2。"
                " 這裡是 operator-facing 狀態板，不是新的控制平面。"
            ),
            "primary_rule": (
                "Status panel summarizes operator truth, but CLI/runtime commands remain the parent action path."
            ),
            "secondary_rule": "Self-improvement posture and telemetry stay secondary.",
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
        "self_improvement": {
            "present": bool(improvement_cue.get("present")),
            "summary_text": str(improvement_cue.get("summary_text", "")).strip(),
            "top_result": str(improvement_cue.get("top_result", "")).strip(),
            "next_action": str(improvement_cue.get("next_action", "")).strip(),
            "receiver_rule": str(improvement_cue.get("receiver_rule", "")).strip(),
            "source_path": str(improvement_cue.get("source_path", "")).strip(),
            "outcome_counts": {
                "promote": int(
                    ((improvement_cue.get("outcome_counts") or {}).get("promote", 0)) or 0
                ),
                "park": int(((improvement_cue.get("outcome_counts") or {}).get("park", 0)) or 0),
                "retire": int(
                    ((improvement_cue.get("outcome_counts") or {}).get("retire", 0)) or 0
                ),
                "blocked": int(
                    ((improvement_cue.get("outcome_counts") or {}).get("blocked", 0)) or 0
                ),
            },
        },
        "telemetry": {
            "conversation_status": _format_conversation_status(last_entry.get("status")),
            "conversation_count": int(conversation.get("count", 0) or 0),
            "conversation_time": _format_timestamp(last_entry.get("timestamp")),
            "intent_status": _format_intent_status(intent.get("status")),
            "control_status": _format_control_status(control.get("status")),
            "persona_id": str(persona.get("id", "")).strip()
            or str(snapshot.get("persona", {}).get("id", "base")),
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
    improvement_cue = _load_self_improvement_result_cue()
    view_model = build_status_panel_view_model(
        snapshot=snapshot,
        summary=summary,
        tier0_shell=tier0_shell,
        tier1_shell=tier1_shell,
        tier2_drawer=tier2_drawer,
        improvement_cue=improvement_cue,
    )

    operator_posture = view_model["operator_posture"]
    tier0 = view_model["tier0"]
    tier1 = view_model["tier1"]
    tier2 = view_model["tier2"]
    self_improvement = view_model["self_improvement"]
    telemetry = view_model["telemetry"]

    st.markdown("### 系統狀態總覽")
    st.caption(operator_posture["note"])
    st.caption(operator_posture["primary_rule"])

    # Tier 0 · Instant Gate
    with st.container(border=True):
        st.markdown("**快速狀態**")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("就緒", tier0["readiness"])
        with col_b:
            st.metric("路徑", tier0["task_track"])
        with col_c:
            st.metric("模式", tier0["deliberation_mode"])

        if tier0["next_followup_command"]:
            st.caption("下一步建議")
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

    # Tier 1 · Orientation Shell
    with st.container(border=True):
        st.markdown("**工作方向**")
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
                ("基線", "baseline"),
                ("Beta 可用", "beta_usable"),
                ("部分完成", "partial"),
                ("延後", "deferred"),
            ],
        ):
            with col:
                st.metric(label, tier1["parity_counts"][key])

        if tier1["source_precedence"]:
            with st.expander("來源優先序", expanded=False):
                st.caption(tier1["source_precedence"])

    if self_improvement["present"]:
        st.caption(operator_posture["secondary_rule"])
        st.caption("自我改善狀態: " + self_improvement["summary_text"])
        with st.expander("自我改善結果", expanded=False):
            st.caption(self_improvement["receiver_rule"])
            if self_improvement["top_result"]:
                st.markdown(f"- 最佳結果: `{self_improvement['top_result']}`")
            counts = self_improvement["outcome_counts"]
            st.markdown(
                "- 結果統計: "
                f"升級={counts['promote']} | 暫存={counts['park']} | "
                f"淘汰={counts['retire']} | 受阻={counts['blocked']}"
            )
            if self_improvement["next_action"]:
                st.markdown(f"- 下一步: `{self_improvement['next_action']}`")
            if self_improvement["source_path"]:
                st.markdown(f"- 來源: `{self_improvement['source_path']}`")

    # Tier 2 · Deep Governance
    with st.container(border=True):
        st.markdown("**深層治理**")
        if tier2["recommended_open"]:
            st.warning(
                "建議開啟: " + ", ".join(tier2["trigger_reasons"])
                if tier2["trigger_reasons"]
                else "僅在需要時開啟。"
            )
        else:
            st.caption("僅手動開啟。深層治理需要明確的操作者指令。")

        if tier2["active_groups"]:
            st.caption("活躍群組: " + " | ".join(tier2["active_groups"]))
        if tier2["summary_text"]:
            st.caption(tier2["summary_text"])
        if tier2["next_pull_commands"]:
            with st.expander("建議的深層指令", expanded=False):
                for command in tier2["next_pull_commands"]:
                    st.code(command, language="bash")

    # Reflex Arc status
    with st.container(border=True):
        st.markdown("**治理反射弧**")
        try:
            from tonesoul.governance.reflex import GovernanceSnapshot, ReflexEvaluator
            from tonesoul.governance.reflex_config import load_reflex_config
            from tonesoul.runtime_adapter import load as load_posture

            reflex_config = load_reflex_config()
            posture = load_posture()
            snapshot = GovernanceSnapshot.from_posture(posture, tension=0.0)
            evaluator = ReflexEvaluator(config=reflex_config)
            decision = evaluator.evaluate(snapshot)
            band = decision.soul_band

            band_name = band.level.value if band else "unknown"
            band_labels = {
                "serene": "平靜",
                "alert": "警覺",
                "strained": "緊繃",
                "critical": "危機",
            }
            band_colors = {
                "serene": "green",
                "alert": "orange",
                "strained": "red",
                "critical": "red",
            }
            mode_label = "硬執行" if reflex_config.vow_enforcement_mode == "hard" else "軟執行"

            rc1, rc2, rc3 = st.columns(3)
            with rc1:
                st.metric("Soul Band", band_labels.get(band_name, band_name))
            with rc2:
                st.metric("Gate 倍率", f"{decision.gate_modifier:.0%}")
            with rc3:
                st.metric("執行模式", mode_label)

            if band and band.force_council:
                st.caption("Council 強制召集中")
            if band and band.max_autonomy is not None:
                st.caption(f"自主權上限: {band.max_autonomy:.0%}")
            if decision.disclaimer:
                st.warning(decision.disclaimer)

            with st.expander("Enforcement Log", expanded=False):
                for entry in decision.enforcement_log:
                    st.caption(str(entry))
        except Exception as exc:
            st.caption(f"反射弧載入失敗: {exc}")

    with st.expander("遙測資料", expanded=False):
        st.markdown(
            f"- 對話: `{telemetry['conversation_status']}`"
            f" | 次數={telemetry['conversation_count']}"
            f" | 最後={telemetry['conversation_time']}"
        )
        st.markdown(
            f"- 意圖 / 控制: `{telemetry['intent_status']}` / `{telemetry['control_status']}`"
        )
        st.markdown(f"- 人格: `{telemetry['persona_id']}` | 執行: `{telemetry['run_id']}`")
        if telemetry["user_message"]:
            st.text_area("最近使用者訊息", telemetry["user_message"], height=70)
        if telemetry["assistant_summary"]:
            st.text_area("最近助手摘要", telemetry["assistant_summary"], height=90)
