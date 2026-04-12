"""
內在會議顯示元件 - 人性化內在會議討論
"""

from typing import Dict

import streamlit as st


def render_council(council: Dict[str, str]):
    """
    渲染 Council 討論

    Args:
        council: 字典，包含 guardian, analyst, critic, advocate, decision
    """

    personas = [
        ("守", "守門者", "guardian", "#2a9d8f"),
        ("析", "分析者", "analyst", "#e9c46a"),
        ("批", "批評者", "critic", "#e76f51"),
        ("倡", "倡議者", "advocate", "#264653"),
    ]

    for icon, name, key, color in personas:
        message = council.get(key, "")
        if message:
            st.markdown(
                f"""
                <div class="ts-card" style="
                    border-left: 4px solid {color};
                    margin-bottom: 10px;
                ">
                    <div class="ts-pill">{icon} {name}</div>
                    <div style="margin-top: 8px;">{message}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # 最終決議
    decision = council.get("decision", "")
    if decision:
        st.markdown("---")
        decision_label = "通過" if "批准" in decision or "通過" in decision else "注意"
        if "阻擋" in decision or "拒絕" in decision:
            decision_label = "阻擋"
        st.markdown(f"**決議（{decision_label}）**: {decision}")


def parse_council_response(response: str) -> tuple[Dict[str, str], str]:
    """
    從 LLM 回應中解析 Council 討論

    Args:
        response: LLM 的完整回應

    Returns:
        (council_dict, actual_response)
    """

    council = {
        "guardian": "",
        "analyst": "",
        "critic": "",
        "advocate": "",
        "decision": "",
    }

    lines = response.strip().split("\n")
    actual_response_lines = []
    current_key = None
    in_council = False

    for line in lines:
        line_lower = line.lower().strip()

        if "guardian:" in line_lower:
            current_key = "guardian"
            council[current_key] = line.split(":", 1)[-1].strip()
            in_council = True
        elif "analyst:" in line_lower:
            current_key = "analyst"
            council[current_key] = line.split(":", 1)[-1].strip()
            in_council = True
        elif "critic:" in line_lower:
            current_key = "critic"
            council[current_key] = line.split(":", 1)[-1].strip()
            in_council = True
        elif "advocate:" in line_lower:
            current_key = "advocate"
            council[current_key] = line.split(":", 1)[-1].strip()
            in_council = True
        elif "決議:" in line or "decision:" in line_lower:
            current_key = "decision"
            council[current_key] = line.split(":", 1)[-1].strip()
            in_council = False
        elif "回覆:" in line or "response:" in line_lower:
            in_council = False
            current_key = None
        elif not in_council:
            actual_response_lines.append(line)

    actual_response = "\n".join(actual_response_lines).strip()

    if not actual_response:
        fallback_lines = []
        for line in lines:
            line_lower = line.lower().strip()
            if line_lower.startswith(
                ("guardian:", "analyst:", "critic:", "advocate:", "decision:")
            ):
                continue
            if line.strip().startswith("決議:") or line_lower.startswith("response:"):
                continue
            if "回覆:" in line:
                continue
            if line.strip():
                fallback_lines.append(line)
        actual_response = "\n".join(fallback_lines).strip()

    if not actual_response:
        actual_response = response.strip()

    return council, actual_response
