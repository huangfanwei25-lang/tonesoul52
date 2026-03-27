"""Runtime risk posture and project-memory summary helpers.

This module deliberately computes a bounded operational Risk (R) surface from
already-governed runtime signals. It does not implement POAV gating or any
theoretical law/ metric.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


@dataclass(frozen=True)
class RiskAssessment:
    score: float
    level: str
    factors: List[str]
    recommended_action: str
    inputs: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": round(float(self.score), 4),
            "level": self.level,
            "factors": list(self.factors),
            "recommended_action": self.recommended_action,
            "inputs": {key: round(float(value), 4) for key, value in self.inputs.items()},
        }


def compute_runtime_risk(
    *,
    posture: Any,
    recent_traces: List[Dict[str, Any]] | None = None,
    claims: List[Dict[str, Any]] | None = None,
    compactions: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """Compute a bounded runtime Risk (R) posture in [0, 1].

    Inputs are intentionally limited to already-visible governed surfaces:
    recent tensions, recent Aegis vetoes, active claims, and compaction backlog.
    """
    recent_traces = list(recent_traces or [])
    claims = list(claims or [])
    compactions = list(compactions or [])

    tensions = list(getattr(posture, "tension_history", []) or [])[-5:]
    vetoes = list(getattr(posture, "aegis_vetoes", []) or [])[-3:]

    severities = [_coerce_unit(event.get("severity", 0.0)) for event in tensions]
    max_tension = max(severities, default=0.0)
    mean_tension = (sum(severities) / len(severities)) if severities else 0.0
    tension_pressure = min(1.0, 0.65 * max_tension + 0.35 * mean_tension)

    aegis_pressure = min(1.0, len(vetoes) / 2.0)
    coordination_pressure = min(1.0, len(claims) / 4.0)

    pending_paths_total = 0
    for entry in compactions[:5]:
        pending_paths_total += len(entry.get("pending_paths") or [])
    backlog_pressure = min(1.0, pending_paths_total / 8.0)

    trace_tension_total = 0
    for trace in recent_traces[-5:]:
        trace_tension_total += int(trace.get("tension_count", 0) or 0)
    trace_pressure = min(1.0, trace_tension_total / 8.0)

    score = min(
        1.0,
        0.48 * tension_pressure
        + 0.28 * aegis_pressure
        + 0.12 * coordination_pressure
        + 0.07 * backlog_pressure
        + 0.05 * trace_pressure,
    )

    factors: List[str] = []
    if max_tension >= 0.7:
        factors.append("high_recent_tension")
    if vetoes:
        factors.append("recent_aegis_vetoes")
    if len(claims) >= 2:
        factors.append("multi_agent_coordination")
    if pending_paths_total >= 4:
        factors.append("compaction_backlog")
    if trace_tension_total >= 4:
        factors.append("dense_recent_trace_tension")

    if score >= 0.85:
        level = "critical"
        action = "stabilize_before_expansion"
    elif score >= 0.65:
        level = "high"
        action = "review_before_commit"
    elif score >= 0.35:
        level = "caution"
        action = "proceed_with_caution"
    else:
        level = "stable"
        action = "normal_operation"

    return RiskAssessment(
        score=score,
        level=level,
        factors=factors,
        recommended_action=action,
        inputs={
            "tension_pressure": tension_pressure,
            "aegis_pressure": aegis_pressure,
            "coordination_pressure": coordination_pressure,
            "backlog_pressure": backlog_pressure,
            "trace_pressure": trace_pressure,
        },
    ).to_dict()


def build_project_memory_summary(
    *,
    posture: Any,
    recent_traces: List[Dict[str, Any]] | None = None,
    claims: List[Dict[str, Any]] | None = None,
    compactions: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """Build a compact handoff-ready summary of the current project memory."""
    recent_traces = list(recent_traces or [])
    claims = list(claims or [])
    compactions = list(compactions or [])

    topic_counter: Counter[str] = Counter()
    recent_agents: List[str] = []
    for trace in recent_traces[-5:]:
        agent = str(trace.get("agent", "")).strip()
        if agent and agent not in recent_agents:
            recent_agents.append(agent)
        for topic in trace.get("topics") or []:
            normalized = str(topic).strip()
            if normalized:
                topic_counter[normalized] += 1

    pending_paths = _unique_ordered(
        path
        for claim in claims
        for path in (claim.get("paths") or [])
    )
    pending_paths.extend(
        path
        for entry in compactions[:5]
        for path in (entry.get("pending_paths") or [])
        if path not in pending_paths
    )

    carry_forward = _unique_ordered(
        item
        for entry in compactions[:5]
        for item in (entry.get("carry_forward") or [])
    )
    next_actions = _unique_ordered(
        str(entry.get("next_action", "")).strip()
        for entry in compactions[:5]
        if str(entry.get("next_action", "")).strip()
    )

    focus_topics = [topic for topic, _count in topic_counter.most_common(3)]
    if not focus_topics:
        focus_topics = [
            str(event.get("topic", "")).strip()
            for event in list(getattr(posture, "tension_history", []) or [])[-3:]
            if str(event.get("topic", "")).strip()
        ][:3]

    summary_lines: List[str] = []
    if focus_topics:
        summary_lines.append(f"近期焦點：{', '.join(focus_topics)}")
    if claims:
        summary_lines.append(f"活躍任務認領：{len(claims)}")
    if pending_paths:
        summary_lines.append(f"待續路徑：{', '.join(pending_paths[:3])}")
    if next_actions:
        summary_lines.append(f"下一步：{next_actions[0]}")
    if not summary_lines:
        summary_lines.append("目前沒有足夠的共享記憶片段可形成專案摘要。")

    return {
        "focus_topics": focus_topics,
        "recent_agents": recent_agents[:5],
        "active_claim_count": len(claims),
        "pending_paths": pending_paths[:8],
        "carry_forward": carry_forward[:6],
        "next_actions": next_actions[:4],
        "summary_text": " | ".join(summary_lines),
    }


def _coerce_unit(value: Any) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, numeric))


def _unique_ordered(values: Iterable[Any]) -> List[str]:
    result: List[str] = []
    seen = set()
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result
