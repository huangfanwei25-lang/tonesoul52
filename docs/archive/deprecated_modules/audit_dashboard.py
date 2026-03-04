import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

import pandas as pd
import plotly.express as px
import streamlit as st

try:
    from tonesoul52.persona_trace_report import build_report, load_jsonl
except ImportError:  # pragma: no cover - fallback for script execution
    from persona_trace_report import build_report, load_jsonl


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LEDGER_CANDIDATES = [
    os.path.join(REPO_ROOT, "ledger.jsonl"),
    os.path.join(REPO_ROOT, "body", "ledger", "ledger.jsonl"),
]

REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
REGISTRY_PATH = os.path.join(REPORTS_DIR, "persona_registry_extended.json")
YSTM_DIR = os.path.join(REPORTS_DIR, "ystm_demo")
RUN_ROOT = os.path.join(REPO_ROOT, "5.2", "run", "execution")
WORKSPACE_52 = os.path.join(REPO_ROOT, "5.2")
PERSONA_TRACE_PATH = os.path.join(WORKSPACE_52, "memory", "persona_trace.jsonl")
PERSONA_DIMENSION_PATH = os.path.join(WORKSPACE_52, "memory", "persona_dimension_ledger.jsonl")


def _load_ledger(path: str) -> List[Dict[str, object]]:
    entries: List[Dict[str, object]] = []
    if not os.path.exists(path):
        return entries

    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                entries.append({"_raw": line, "_error": "invalid_json"})
    return entries


def load_latest_ledger() -> Optional[str]:
    for path in LEDGER_CANDIDATES:
        if os.path.exists(path):
            return path
    return None


def normalize_entries(entries: List[Dict[str, object]]) -> pd.DataFrame:
    if not entries:
        return pd.DataFrame()

    df = pd.json_normalize(entries)
    for key in ("timestamp", "time", "created_at"):
        if key in df.columns:
            df[key] = pd.to_datetime(df[key], errors="coerce")
    return df


def _collect_dissent_labels(value: object) -> List[str]:
    labels: List[str] = []
    if not isinstance(value, list):
        return labels
    for item in value:
        if isinstance(item, dict):
            label = (
                item.get("role")
                or item.get("persona")
                or item.get("label")
                or item.get("topic")
                or item.get("name")
            )
            if label is None:
                labels.append(json.dumps(item, sort_keys=True))
            else:
                labels.append(str(label))
            continue
        if isinstance(item, str) and item.strip():
            labels.append(item.strip())
    return labels


def build_dissent_hotspots(council_df: pd.DataFrame) -> pd.DataFrame:
    if council_df.empty or "council.dissent" not in council_df.columns:
        return pd.DataFrame()
    labels: List[str] = []
    for value in council_df["council.dissent"].tolist():
        labels.extend(_collect_dissent_labels(value))
    if not labels:
        return pd.DataFrame()
    summary = pd.Series(labels).value_counts().reset_index()
    summary.columns = ["label", "count"]
    return summary


def _parse_timestamp(value: object) -> Optional[datetime]:
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def _intent_status_label(status: Optional[str]) -> str:
    if not status:
        return "unknown"
    status_text = str(status).lower()
    label_map = {
        "achieved": "achieved",
        "failed": "failed",
        "inconclusive": "inconclusive",
    }
    return label_map.get(status_text, status_text)


def _format_ratio(value: Optional[float]) -> str:
    if value is None:
        return "n/a"
    return f"{value:.2f}"


def _latest_entry(entries: List[Dict[str, object]]) -> Optional[Dict[str, object]]:
    if not entries:
        return None
    latest = None
    latest_ts = None
    for entry in entries:
        ts = _parse_timestamp(
            entry.get("timestamp") or entry.get("time") or entry.get("created_at")
        )
        if ts is None:
            continue
        if latest_ts is None or ts > latest_ts:
            latest_ts = ts
            latest = entry
    return latest or entries[-1]


def audit_summary(df: pd.DataFrame) -> Dict[str, object]:
    if df.empty:
        return {
            "count": 0,
            "event_types": 0,
            "latest": None,
            "coverage": 0.0,
            "missing_timestamp": 0,
        }

    timestamp_col = None
    for key in ("timestamp", "time", "created_at"):
        if key in df.columns:
            timestamp_col = key
            break

    latest = None
    if timestamp_col:
        latest = df[timestamp_col].max()
        if isinstance(latest, pd.Timestamp):
            latest = latest.to_pydatetime()

    required_fields = [col for col in ("event_type", "content", timestamp_col) if col]
    if required_fields:
        filled = df[required_fields].notna().all(axis=1).mean()
    else:
        filled = 0.0

    missing_timestamp = 0
    if timestamp_col:
        missing_timestamp = df[timestamp_col].isna().sum()

    event_types = 0
    if "event_type" in df.columns:
        event_types = df["event_type"].nunique(dropna=True)

    return {
        "count": len(df),
        "event_types": event_types,
        "latest": latest,
        "coverage": float(filled),
        "missing_timestamp": int(missing_timestamp),
    }


def render_header(summary: Dict[str, object]) -> None:
    st.markdown(
        """
        <style>
            :root {
                --bg-1: #0b1020;
                --bg-2: #121d2d;
                --accent: #ffb000;
                --accent-2: #66d9ef;
                --text: #f6f4ef;
                --muted: #a3b0c2;
            }
            .app-shell {
                background: linear-gradient(160deg, var(--bg-1), var(--bg-2));
                padding: 24px;
                border-radius: 18px;
                border: 1px solid rgba(255,255,255,0.08);
            }
            .headline {
                font-family: "Space Grotesk", "IBM Plex Sans", sans-serif;
                font-size: 36px;
                color: var(--text);
                margin-bottom: 8px;
                letter-spacing: 0.5px;
            }
            .subhead {
                font-family: "IBM Plex Mono", monospace;
                color: var(--muted);
                font-size: 14px;
            }
            .metric-card {
                background: rgba(10, 14, 26, 0.8);
                border: 1px solid rgba(255,255,255,0.08);
                padding: 16px;
                border-radius: 14px;
            }
            .metric-title {
                font-family: "IBM Plex Mono", monospace;
                color: var(--muted);
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .metric-value {
                font-family: "Space Grotesk", "IBM Plex Sans", sans-serif;
                color: var(--text);
                font-size: 26px;
                margin-top: 6px;
            }
        </style>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600&family=IBM+Plex+Mono:wght@400;600&display=swap" rel="stylesheet">
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='app-shell'>", unsafe_allow_html=True)
    st.markdown("<div class='headline'>ToneSoul Audit Console</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='subhead'>Governance-visible telemetry, ledger integrity, and trace coverage at a glance.</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"<div class='metric-card'><div class='metric-title'>Ledger Entries</div><div class='metric-value'>{summary['count']}</div></div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"<div class='metric-card'><div class='metric-title'>Event Types</div><div class='metric-value'>{summary['event_types']}</div></div>",
            unsafe_allow_html=True,
        )
    with col3:
        coverage = f"{summary['coverage'] * 100:.1f}%"
        st.markdown(
            f"<div class='metric-card'><div class='metric-title'>Trace Coverage</div><div class='metric-value'>{coverage}</div></div>",
            unsafe_allow_html=True,
        )
    with col4:
        last_seen = summary["latest"]
        if isinstance(last_seen, datetime):
            last_seen = last_seen.strftime("%Y-%m-%d %H:%M")
        st.markdown(
            f"<div class='metric-card'><div class='metric-title'>Last Trace</div><div class='metric-value'>{last_seen or 'N/A'}</div></div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def render_audit_panel(df: pd.DataFrame) -> None:
    st.markdown("## Audit Lens")
    if df.empty:
        st.info("No ledger data found. Add entries to ledger.jsonl to populate audit views.")
        return

    timestamp_col = next((c for c in ("timestamp", "time", "created_at") if c in df.columns), None)

    col1, col2 = st.columns([0.65, 0.35])
    with col1:
        if timestamp_col:
            chart_df = df[[timestamp_col]].copy()
            chart_df["count"] = 1
            chart_df = chart_df.dropna(subset=[timestamp_col])
            chart_df = chart_df.groupby(pd.Grouper(key=timestamp_col, freq="H")).sum().reset_index()
            fig = px.area(
                chart_df,
                x=timestamp_col,
                y="count",
                title="Ledger Activity",
                color_discrete_sequence=["#ffb000"],
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f6f4ef"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No timestamp field detected; activity chart hidden.")

    with col2:
        missing = 0
        if timestamp_col:
            missing = int(df[timestamp_col].isna().sum())
        st.metric("Missing timestamps", missing)
        if "event_type" in df.columns:
            top = df["event_type"].value_counts().head(6).reset_index()
            top.columns = ["event_type", "count"]
            st.dataframe(top, use_container_width=True, height=220)
        else:
            st.info("No event_type column detected.")

    st.divider()
    st.markdown("## Latest Trace Samples")
    st.dataframe(df.tail(12), use_container_width=True, height=320)


def render_governance_summary() -> None:
    st.markdown("## Governance Signals")
    col1, col2, col3 = st.columns(3)
    col1.metric("P0 Non-Harm", "Active")
    col2.metric("P1 Context Integrity", "Active")
    col3.metric("P2 Cognitive Honesty", "Active")
    st.caption(
        "These states are based on governance intent; wire in live telemetry for real-time gating."
    )


def render_council_panel(df: pd.DataFrame) -> None:
    if df.empty or "event_type" not in df.columns:
        return

    council_df = df[df["event_type"] == "persona_council"].copy()
    if council_df.empty:
        return

    st.markdown("## Council Audit")
    coverage_col = "audit.coverage"
    if coverage_col in council_df.columns:
        if (council_df[coverage_col].dropna() < 1.0).any():
            st.warning("Some council events have incomplete coverage.")
        show_low = st.checkbox("Show only low coverage", value=False, key="council_low")
        if show_low:
            council_df = council_df[council_df[coverage_col] < 1.0]
            if council_df.empty:
                st.info("No low-coverage events.")
                return

    coverage_avg = None
    if coverage_col in council_df.columns:
        coverage_avg = council_df[coverage_col].dropna().mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("Council Events", len(council_df))
    if "persona.active" in council_df.columns:
        col2.metric("Active Personas", council_df["persona.active"].nunique(dropna=True))
    if coverage_avg is not None:
        col3.metric("Avg Coverage", f"{coverage_avg * 100:.1f}%")

    st.dataframe(council_df.tail(8), use_container_width=True, height=260)

    if "council.integration" in council_df.columns:
        latest = council_df.dropna(subset=["council.integration"]).tail(1)
        if not latest.empty:
            st.caption("Latest integration summary")
            st.write(str(latest.iloc[0]["council.integration"]))

    st.divider()
    st.markdown("## Dissent Hotspots")
    dissent_df = build_dissent_hotspots(council_df)
    if dissent_df.empty:
        st.info("No dissent entries recorded.")
    else:
        fig = px.bar(
            dissent_df.head(10),
            x="label",
            y="count",
            title="Top dissent signals",
            color_discrete_sequence=["#66d9ef"],
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f6f4ef"),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("## Role Weight Distribution")
    run_dir = _latest_run_dir(RUN_ROOT)
    if not run_dir:
        st.info("No run artifacts found for role weights.")
        return
    council_summary = _load_json(os.path.join(run_dir, "council_summary.json"))
    votes = council_summary.get("votes") if isinstance(council_summary, dict) else None
    if not isinstance(votes, list) or not votes:
        st.info("No council votes found in council_summary.json.")
        return
    weight_df = pd.DataFrame(votes)
    if "governance_role" not in weight_df.columns or "weight" not in weight_df.columns:
        st.info("Council votes missing governance_role or weight fields.")
        return
    weight_df = weight_df[["governance_role", "weight"]].copy()
    weight_df["weight"] = pd.to_numeric(weight_df["weight"], errors="coerce")
    weight_df = weight_df.dropna(subset=["weight"])
    if weight_df.empty:
        st.info("No valid weights available.")
        return
    weight_df = weight_df.groupby("governance_role", as_index=False)["weight"].sum()
    fig = px.bar(
        weight_df,
        x="governance_role",
        y="weight",
        title="Governance role weights",
        color_discrete_sequence=["#ffb000"],
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f6f4ef"),
    )
    st.plotly_chart(fig, use_container_width=True)


def load_persona_registry() -> pd.DataFrame:
    if not os.path.exists(REGISTRY_PATH):
        return pd.DataFrame()

    with open(REGISTRY_PATH, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    registry = payload.get("registry", [])
    if not registry:
        return pd.DataFrame()
    return pd.DataFrame(registry)


def render_persona_registry_panel(registry_df: pd.DataFrame) -> None:
    st.markdown("## Persona Registry")
    if registry_df.empty:
        st.info("No persona registry found. Run persona registry builder to generate it.")
        return

    total = len(registry_df)
    unique_names = (
        registry_df["name"].nunique(dropna=True) if "name" in registry_df.columns else total
    )
    encoding_flags = 0
    if "notes" in registry_df.columns:
        encoding_flags = int((registry_df["notes"] == "encoding_suspect").sum())
    unknown_roles = 0
    if "role" in registry_df.columns:
        unknown_roles = int((registry_df["role"] == "unknown").sum())

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Registry Entries", total)
    col2.metric("Unique Names", unique_names)
    col3.metric("Encoding Flags", encoding_flags)
    col4.metric("Unknown Roles", unknown_roles)

    if "role" in registry_df.columns:
        role_counts = registry_df["role"].value_counts().reset_index()
        role_counts.columns = ["role", "count"]
        st.dataframe(role_counts, use_container_width=True, height=220)

    if "notes" in registry_df.columns:
        flagged = registry_df[registry_df["notes"] == "encoding_suspect"].head(8)
        if not flagged.empty:
            st.caption("Encoding-flagged entries")
            st.dataframe(flagged, use_container_width=True, height=220)


def render_persona_trace_panel() -> None:
    st.markdown("## Persona Trace")
    trace_entries = load_jsonl(PERSONA_TRACE_PATH)
    dimension_entries = load_jsonl(PERSONA_DIMENSION_PATH)
    if not trace_entries and not dimension_entries:
        st.info("No persona trace logs found.")
        return

    report = build_report(trace_entries, dimension_entries)
    trace_stats = report.get("trace", {}).get("stats", {})
    dimension_stats = report.get("dimension", {}).get("stats", {})

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Trace Entries", report.get("trace", {}).get("count", 0))
    with col2:
        st.metric("Changed Ratio", _format_ratio(trace_stats.get("changed_ratio")))
    with col3:
        avg_delta = trace_stats.get("avg_delta_len")
        st.metric(
            "Avg Delta Len", f"{avg_delta:.2f}" if isinstance(avg_delta, (int, float)) else "n/a"
        )
    with col4:
        avg_max = trace_stats.get("avg_distance_max")
        st.metric(
            "Avg Distance Max", f"{avg_max:.3f}" if isinstance(avg_max, (int, float)) else "n/a"
        )

    if trace_entries:
        st.markdown("Trace Samples")
        rows = []
        for entry in trace_entries[-12:]:
            diff = entry.get("diff") if isinstance(entry.get("diff"), dict) else {}
            shadow = entry.get("shadow") if isinstance(entry.get("shadow"), dict) else {}
            distance = (
                shadow.get("vector_distance")
                if isinstance(shadow.get("vector_distance"), dict)
                else {}
            )
            ts = _parse_timestamp(entry.get("timestamp")) if entry.get("timestamp") else None
            rows.append(
                {
                    "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S") if ts else entry.get("timestamp"),
                    "persona": entry.get("persona_id") or "base",
                    "changed": diff.get("changed"),
                    "delta_len": diff.get("delta_len"),
                    "distance_max": distance.get("max"),
                }
            )
        st.dataframe(rows, use_container_width=True, height=260)

    if dimension_entries:
        st.markdown("Dimension Ledger")
        valid_ratio = dimension_stats.get("valid_ratio")
        if valid_ratio is not None:
            st.metric("Valid Ratio", f"{valid_ratio:.2f}")
        reasons = dimension_stats.get("reason_counts") or {}
        if reasons:
            st.caption(
                "Top reasons: " + ", ".join(f"{k}={v}" for k, v in list(reasons.items())[:5])
            )


def _load_json(path: str) -> Dict[str, object]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else {}


def _latest_run_dir(run_root: str) -> Optional[str]:
    if not os.path.isdir(run_root):
        return None
    candidates = []
    for name in os.listdir(run_root):
        path = os.path.join(run_root, name)
        if not os.path.isdir(path):
            continue
        if os.path.exists(os.path.join(path, "context.yaml")):
            candidates.append(path)
    if not candidates:
        return None
    return max(candidates, key=os.path.getmtime)


def render_policy_snapshot() -> None:
    st.markdown("## Policy Snapshot")
    run_dir = _latest_run_dir(RUN_ROOT)
    if not run_dir:
        st.info("No run artifacts found. Generate a run to populate policy snapshots.")
        return

    run_id = os.path.basename(run_dir)
    st.caption(f"Latest run: {run_id}")

    action_set = _load_json(os.path.join(run_dir, "action_set.json"))
    mercy_objective = _load_json(os.path.join(run_dir, "mercy_objective.json"))
    council_summary = _load_json(os.path.join(run_dir, "council_summary.json"))
    intent_verification = _load_json(os.path.join(run_dir, "intent_verification.json"))
    error_ledger_path = os.path.join(run_dir, "error_ledger.jsonl")
    error_entries = _load_ledger(error_ledger_path) if os.path.exists(error_ledger_path) else []

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("Action Set")
        if action_set:
            st.write(f"Mode: {action_set.get('decision_mode')}")
            allowed = action_set.get("allowed_actions") or []
            st.write("Allowed: " + ", ".join(allowed))
        else:
            st.caption("No action_set.json found.")

    with col2:
        st.markdown("Mercy Objective")
        if mercy_objective:
            st.metric("Score", mercy_objective.get("score", "n/a"))
            weights = mercy_objective.get("weights", {})
            if isinstance(weights, dict):
                benefit = weights.get("benefit")
                harm = weights.get("harm")
                if isinstance(benefit, (int, float)) and isinstance(harm, (int, float)):
                    st.caption(f"Benefit={benefit:.3f} | Harm={harm:.3f}")
                else:
                    st.caption(f"Weights: {weights}")
        else:
            st.caption("No mercy_objective.json found.")

    with col3:
        st.markdown("Council Summary")
        if council_summary:
            st.write(f"Decision: {council_summary.get('decision')}")
            st.write(f"Dissent: {council_summary.get('dissent_ratio')}")
        else:
            st.caption("No council_summary.json found.")

    with col4:
        st.markdown("Error Ledger")
        if error_entries:
            st.metric("Events", len(error_entries))
            latest = _latest_entry(error_entries)
            if latest:
                event_id = latest.get("event_id") or "n/a"
                behavior_type = latest.get("behavior_type") or "n/a"
                ts = _parse_timestamp(
                    latest.get("timestamp") or latest.get("time") or latest.get("created_at")
                )
                ts_label = ts.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M") if ts else "n/a"
                st.caption(f"{event_id} | {behavior_type} | {ts_label}")
                behavior = latest.get("behavior") or ""
                if behavior:
                    snippet = behavior[:160] + ("..." if len(behavior) > 160 else "")
                    st.write(snippet)
        else:
            st.caption("No error_ledger.jsonl found.")

    st.markdown("Intent Verification")
    if intent_verification:
        audit_payload = (
            intent_verification.get("audit")
            if isinstance(intent_verification.get("audit"), dict)
            else {}
        )
        status = audit_payload.get("status") or intent_verification.get("status") or "unknown"
        confidence = audit_payload.get("confidence")
        reason = audit_payload.get("reason")
        confidence_text = (
            f"{float(confidence):.2f}" if isinstance(confidence, (int, float)) else "n/a"
        )
        st.write(f"Status: {_intent_status_label(status)}")
        st.write(f"Confidence: {confidence_text}")
        if reason:
            st.caption(f"Reason: {reason}")
    else:
        st.caption("No intent_verification.json found.")


def render_tsr_dcs_snapshot() -> None:
    st.markdown("## TSR / DCS Snapshot")
    run_dir = _latest_run_dir(RUN_ROOT)
    if not run_dir:
        st.info("No run artifacts found for TSR/DCS.")
        return

    tsr_payload = _load_json(os.path.join(run_dir, "tsr_metrics.json"))
    dcs_payload = _load_json(os.path.join(run_dir, "dcs_result.json"))

    if not tsr_payload and not dcs_payload:
        st.info("No tsr_metrics.json or dcs_result.json found.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("TSR Metrics")
        tsr = tsr_payload.get("tsr", {}) if isinstance(tsr_payload, dict) else {}
        if isinstance(tsr, dict) and tsr:
            st.write(f"T={tsr.get('T')} | S={tsr.get('S')} | R={tsr.get('R')}")
            st.caption(f"Energy radius: {tsr.get('energy_radius')}")
        else:
            st.caption("No TSR metrics available.")

    with col2:
        st.markdown("TSR Delta")
        delta = tsr_payload.get("delta", {}) if isinstance(tsr_payload, dict) else {}
        if isinstance(delta, dict) and delta:
            st.write(f"Available: {delta.get('available')}")
            st.write(f"Delta norm: {delta.get('delta_norm')}")
            if delta.get("baseline_run_id"):
                st.caption(f"Baseline: {delta.get('baseline_run_id')}")
        else:
            st.caption("No TSR delta available.")

    with col3:
        st.markdown("DCS Decision")
        if isinstance(dcs_payload, dict) and dcs_payload:
            st.write(f"State: {dcs_payload.get('state')}")
            st.write(f"Decision: {dcs_payload.get('decision')}")
            reasons = dcs_payload.get("reasons")
            if isinstance(reasons, list) and reasons:
                st.caption("Reasons: " + ", ".join(str(item) for item in reasons[:4]))
        else:
            st.caption("No DCS result available.")

    if isinstance(dcs_payload, dict) and dcs_payload:
        with st.expander("DCS Rules"):
            thresholds = dcs_payload.get("thresholds")
            rules = dcs_payload.get("rules")
            if thresholds:
                st.write("Thresholds", thresholds)
            if rules:
                st.write("Rules", rules)


def render_ystm_panel() -> None:
    st.markdown("## YSTM Demo Outputs")
    nodes_path = os.path.join(YSTM_DIR, "nodes.json")
    audit_path = os.path.join(YSTM_DIR, "audit_log.json")
    terrain_png = os.path.join(YSTM_DIR, "terrain.png")
    terrain_p2_png = os.path.join(YSTM_DIR, "terrain_p2.png")

    if not os.path.exists(nodes_path):
        st.info("No YSTM outputs found. Run `python -m tonesoul.ystm_demo` to generate.")
        return

    nodes_payload = _load_json(nodes_path)
    audit_payload = _load_json(audit_path)
    nodes = nodes_payload.get("nodes", []) if isinstance(nodes_payload.get("nodes"), list) else []
    updates = (
        audit_payload.get("updates", []) if isinstance(audit_payload.get("updates"), list) else []
    )

    max_e_total = None
    max_node = None
    if nodes:
        totals = [node.get("scalar", {}).get("E_total", 0.0) for node in nodes]
        if totals:
            max_index = max(range(len(totals)), key=lambda idx: totals[idx])
            max_e_total = totals[max_index]
            max_node = nodes[max_index].get("id")

    col1, col2, col3 = st.columns(3)
    col1.metric("Nodes", len(nodes))
    col2.metric("Audit Updates", len(updates))
    if max_e_total is not None:
        col3.metric("Max E_total", f"{max_e_total:.3f}", f"{max_node}")
    else:
        col3.metric("Max E_total", "N/A")

    img_cols = st.columns(2)
    with img_cols[0]:
        if os.path.exists(terrain_png):
            st.image(terrain_png, caption="P1 Terrain (PNG)", use_container_width=True)
        else:
            st.caption("P1 PNG not found (run with --export-png).")
    with img_cols[1]:
        if os.path.exists(terrain_p2_png):
            st.image(terrain_p2_png, caption="P2 Terrain (PNG)", use_container_width=True)
        else:
            st.caption("P2 PNG not found (run with --export-png).")

    with st.expander("Output Paths"):
        st.code("\n".join([nodes_path, audit_path, terrain_png, terrain_p2_png]))


def main() -> None:
    st.set_page_config(page_title="ToneSoul Audit Console", layout="wide")

    ledger_path = load_latest_ledger()
    entries = _load_ledger(ledger_path) if ledger_path else []
    df = normalize_entries(entries)
    summary = audit_summary(df)

    render_header(summary)
    st.write("")
    render_governance_summary()
    st.write("")
    render_policy_snapshot()
    st.write("")
    render_tsr_dcs_snapshot()
    st.write("")
    render_audit_panel(df)
    st.write("")
    render_council_panel(df)
    st.write("")
    render_persona_registry_panel(load_persona_registry())
    st.write("")
    render_persona_trace_panel()
    st.write("")
    render_ystm_panel()


if __name__ == "__main__":
    main()
