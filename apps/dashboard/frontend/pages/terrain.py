"""
語義地圖頁面 - YSTM 視覺化
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st


def _load_json(path: Path) -> Optional[Dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _summarize_nodes(nodes: List[Dict]) -> Dict[str, object]:
    if not nodes:
        return {"count": 0, "avg_energy": 0.0, "grade_counts": {}}

    avg_energy = sum(node.get("scalar", {}).get("E_total", 0) for node in nodes) / len(nodes)
    grade_counts: Dict[str, int] = {}
    for node in nodes:
        grade = node.get("source_grade", "unknown")
        grade_counts[grade] = grade_counts.get(grade, 0) + 1

    heights = [
        node.get("math_coords", {}).get("height") for node in nodes if node.get("math_coords")
    ]
    avg_height = sum(heights) / len(heights) if heights else None
    return {
        "count": len(nodes),
        "avg_energy": avg_energy,
        "grade_counts": grade_counts,
        "avg_height": avg_height,
    }


def _grade_label(grade: Optional[str]) -> str:
    if not grade:
        return "未知"
    grade_text = str(grade).upper()
    if grade_text in {"A", "B", "C"}:
        return grade_text
    if grade_text == "UNKNOWN":
        return "未知"
    return str(grade)


def _mode_label(mode: Optional[str]) -> str:
    if not mode:
        return "未知"
    label_map = {
        "analysis": "分析",
        "bridge": "橋接",
        "action": "行動",
        "risk": "風險",
        "audit": "稽核",
    }
    return label_map.get(str(mode).lower(), str(mode))


def _domain_label(domain: Optional[str]) -> str:
    if not domain:
        return "未知"
    label_map = {
        "governance": "治理",
        "engineering": "工程",
        "safety": "安全",
        "research": "研究",
        "product": "產品",
    }
    return label_map.get(str(domain).lower(), str(domain))


def _format_percent(value: Optional[float]) -> str:
    if value is None:
        return "無"
    try:
        return f"{float(value) * 100:.0f}%"
    except (TypeError, ValueError):
        return str(value)


def _format_float(value: Optional[float]) -> str:
    if value is None:
        return "無"
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return str(value)


def _build_summary(node: Dict) -> List[str]:
    summary: List[str] = []

    source_label = _grade_label(node.get("source_grade"))
    summary.append(f"來源可信度: {source_label}")

    scalar = node.get("scalar", {})
    summary.append(f"熟悉度: {_format_percent(scalar.get('E_total'))}")

    risk_value = scalar.get("E_risk")
    if risk_value not in (None, 0, 0.0):
        summary.append(f"風險係數: {_format_percent(risk_value)}")

    where = node.get("where", {})
    where_field = where.get("where_field", {})
    where_task = where.get("where_task", {})
    where_time = where.get("where_time", {})

    summary.append(f"話題模式: {_mode_label(where_field.get('mode'))}")
    summary.append(f"任務領域: {_domain_label(where_task.get('domain'))}")

    turn_id = where_time.get("turn_id")
    if turn_id is not None:
        summary.append(f"出現於對話第 {turn_id} 輪")

    what = node.get("what", {})
    if "mu" in what:
        summary.append(f"話題特徵強度: {_format_float(what.get('mu'))}")
    if isinstance(what.get("v_sem"), list):
        summary.append(f"特徵維度: {len(what.get('v_sem'))}")

    drift = node.get("drift", {})
    drift_norm = drift.get("delta_norm")
    if drift_norm not in (None, 0, 0.0):
        summary.append(f"近期變動幅度: {_format_float(drift_norm)}")

    patch_history = node.get("patch_history") or []
    if patch_history:
        summary.append(f"修改記錄: {len(patch_history)} 次")

    return summary


def render():
    """渲染語義地圖頁面"""

    st.markdown(
        """
        <div class="ts-hero">
          <h1>語義地圖</h1>
          <p>AI 怎麼理解你們的對話？每個話題在它腦中有位置、有距離、有高低。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 說明區塊
    with st.expander("這個地圖在說什麼？", expanded=False):
        st.markdown(
            "語義地圖把 AI 在對話中遇到的每個「話題」放到一張地形圖上。\n\n"
            "- **位置** — 相近的話題會靠在一起\n"
            "- **高度** — 越抽象/越難的話題越高\n"
            "- **亮度** — AI 越熟悉的話題越亮\n"
            "- **來源可信度 (A/B/C)** — A 最可信（直接引用），C 最模糊（推測）\n\n"
            "你可以把它想像成 AI 的「知識地形」——\n"
            "平坦的地方是舒適區，崎嶇的地方是還沒搞懂的領域。"
        )

    dataset = st.radio(
        "資料來源",
        ["ystm_demo", "ystm_demo_math"],
        format_func=lambda x: "基礎版" if x == "ystm_demo" else "數學擴展版",
        horizontal=True,
    )

    workspace = Path(__file__).parent.parent.parent
    ystm_dir = workspace / "reports" / dataset
    terrain_html = ystm_dir / "terrain_p2.html"
    nodes_json = ystm_dir / "nodes.json"

    if terrain_html.exists():
        html_content = terrain_html.read_text(encoding="utf-8")
        st.components.v1.html(html_content, height=520, scrolling=True)
    else:
        st.warning("語義地圖尚未生成。請先執行 `python -m tonesoul.ystm_demo`")

    if not nodes_json.exists():
        st.info("尚未找到節點資料，請先產生 `reports/ystm_demo/nodes.json`")
        return

    nodes_payload = _load_json(nodes_json)
    nodes = nodes_payload.get("nodes", []) if nodes_payload else []
    if not nodes:
        st.info("尚未找到節點資料，請先執行 `python -m tonesoul.ystm_demo`")
        return

    summary = _summarize_nodes(nodes)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("話題數量", summary["count"])
    with col2:
        st.metric("平均熟悉度", _format_percent(summary["avg_energy"]))
    with col3:
        grade_text = (
            ", ".join(f"{_grade_label(k)}:{v}" for k, v in summary["grade_counts"].items()) or "無"
        )
        st.metric("來源分級", grade_text)
    with col4:
        avg_height = summary.get("avg_height")
        st.metric("平均高度", f"{avg_height:.2f}" if avg_height is not None else "無")

    st.markdown('<div class="ts-section-title">你現在在這裡</div>', unsafe_allow_html=True)

    node_labels = [f"{node.get('id')} - {node.get('text', '')[:28]}" for node in nodes]
    selected = st.selectbox(
        "目前話題", list(range(len(nodes))), format_func=lambda i: node_labels[i]
    )
    node = nodes[selected]

    detail_col, meta_col = st.columns([1.4, 1], gap="large")
    with detail_col:
        st.markdown(
            f"""
            <div class="ts-card">
              <div class="ts-pill">話題內容</div>
              <h3>{node.get('text', '')}</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="ts-section-title">話題摘要</div>', unsafe_allow_html=True)
        summary_lines = _build_summary(node)
        st.markdown("\n".join(f"- {line}" for line in summary_lines))
        st.caption("熟悉度代表系統對此話題的熟悉程度；來源可信度為 A/B/C 分級。")

    with meta_col:
        e_total = node.get("scalar", {}).get("E_total", 0)
        source_label = _grade_label(node.get("source_grade"))
        st.markdown(
            f"""
            <div class="ts-card">
              <div class="ts-pill">來源與熟悉度</div>
              <p class="ts-muted">來源可信度: {source_label}</p>
              <p class="ts-muted">熟悉度: {_format_percent(e_total)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        math_coords = node.get("math_coords") or {}
        if math_coords:
            st.markdown('<div class="ts-section-title">抽象程度</div>', unsafe_allow_html=True)
            details = []
            if math_coords.get("height") is not None:
                details.append(f"‧ 難度: {_format_percent(math_coords.get('height'))}")
            if math_coords.get("geology"):
                details.append(f"‧ 型態: {math_coords.get('geology')}")
            if math_coords.get("ruggedness") is not None:
                details.append(f"‧ 複雜度: {_format_percent(math_coords.get('ruggedness'))}")
            if details:
                st.markdown("\n".join(details))

        with st.expander("詳細資訊"):
            st.json(
                {
                    "where": node.get("where", {}),
                    "what": node.get("what", {}),
                    "scalar": node.get("scalar", {}),
                    "drift": node.get("drift", {}),
                    "patch_history": node.get("patch_history", []),
                }
            )

    neighbors = [n for n in nodes if n.get("id") != node.get("id")]
    neighbors = sorted(neighbors, key=lambda n: n.get("scalar", {}).get("E_total", 0), reverse=True)
    if neighbors:
        st.markdown('<div class="ts-section-title">附近的話題</div>', unsafe_allow_html=True)
        for neighbor in neighbors[:5]:
            label = neighbor.get("text", "")
            label = label if len(label) <= 40 else label[:40] + "..."
            score = neighbor.get("scalar", {}).get("E_total", 0)
            st.markdown(f"‧ {label} ({_format_percent(score)})")
