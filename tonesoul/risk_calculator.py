"""Runtime risk posture and project-memory summary helpers.

This module computes bounded operational signals from already-governed runtime
surfaces. It does not implement law/ theory metrics or hidden governance rules.
"""

from __future__ import annotations

import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List

from tonesoul.working_style import (
    build_working_style_import_limits,
    build_working_style_observability,
)

_PROMPT_STYLE_DEFAULTS = [
    "state the goal function before long transfer or extraction prompts",
    "keep P0/P1/P2 explicit when constraints may conflict",
    "mark [資料不足] instead of filling gaps with unsupported guesses",
]
_RENDER_BOUNDARY_CAVEAT = "Treat shell `??` or garbled CJK as render-layer noise until a UTF-8 file read proves real corruption."


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
    """Compute a bounded runtime Risk (R) posture in [0, 1]."""
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
    subject_snapshots: List[Dict[str, Any]] | None = None,
    routing_summary: Dict[str, Any] | None = None,
    repo_root: str | Path | None = None,
) -> Dict[str, Any]:
    """Build a compact handoff-ready summary of the current project memory."""
    recent_traces = list(recent_traces or [])
    claims = list(claims or [])
    compactions = list(compactions or [])
    subject_snapshots = list(subject_snapshots or [])
    routing_summary = dict(routing_summary or {})

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

    pending_paths = _unique_ordered(path for claim in claims for path in (claim.get("paths") or []))
    pending_paths.extend(
        path
        for entry in compactions[:5]
        for path in (entry.get("pending_paths") or [])
        if path not in pending_paths
    )

    carry_forward = _unique_ordered(
        item for entry in compactions[:5] for item in (entry.get("carry_forward") or [])
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

    repo_progress = _build_repo_progress_snapshot(repo_root=repo_root)
    latest_subject_snapshot = subject_snapshots[0] if subject_snapshots else {}
    subject_anchor = _build_subject_anchor(latest_subject_snapshot)
    working_style_anchor = _build_working_style_anchor(latest_subject_snapshot)
    evidence_readout_posture = _build_evidence_readout_posture()
    working_style_observability = build_working_style_observability(
        working_style_anchor,
        carry_forward=carry_forward,
        next_actions=next_actions,
        routing_summary=routing_summary,
    )
    working_style_import_limits = build_working_style_import_limits(
        working_style_anchor,
        observability=working_style_observability,
    )

    summary_lines: List[str] = []
    if focus_topics:
        summary_lines.append(f"focus={', '.join(focus_topics)}")
    if subject_anchor.get("summary"):
        summary_lines.append(f"subject={subject_anchor['summary']}")
    if claims:
        summary_lines.append(f"claims={len(claims)}")
    if pending_paths:
        summary_lines.append(f"pending={', '.join(pending_paths[:3])}")
    if next_actions:
        summary_lines.append(f"next={next_actions[0]}")
    if repo_progress.get("available"):
        summary_lines.append(
            "repo="
            f"{repo_progress.get('branch', 'unknown')}@{repo_progress.get('head', 'unknown')}"
            f" dirty={int(repo_progress.get('dirty_count', 0) or 0)}"
        )
    if int(routing_summary.get("total_events", 0) or 0) > 0:
        summary_lines.append(str(routing_summary.get("summary_text", "")).strip())
    if (
        working_style_observability
        and str(working_style_observability.get("status", "")) != "reinforced"
    ):
        summary_lines.append(str(working_style_observability.get("summary_text", "")).strip())
    if evidence_readout_posture:
        summary_lines.append(str(evidence_readout_posture.get("summary_text", "")).strip())
    if not summary_lines:
        summary_lines.append("No active carry-forward surface is visible yet.")

    result = {
        "focus_topics": focus_topics,
        "recent_agents": recent_agents[:5],
        "active_claim_count": len(claims),
        "pending_paths": pending_paths[:8],
        "carry_forward": carry_forward[:6],
        "next_actions": next_actions[:4],
        "repo_progress": repo_progress,
        "summary_text": " | ".join(summary_lines),
    }
    if subject_anchor:
        result["subject_anchor"] = subject_anchor
    if working_style_anchor:
        result["working_style_anchor"] = working_style_anchor
    if working_style_observability:
        result["working_style_observability"] = working_style_observability
    if working_style_import_limits:
        result["working_style_import_limits"] = working_style_import_limits
    if evidence_readout_posture:
        result["evidence_readout_posture"] = evidence_readout_posture
    if routing_summary:
        result["routing_summary"] = routing_summary
    return result


def _build_evidence_readout_posture() -> Dict[str, Any]:
    lanes = [
        {
            "lane": "session_control_and_handoff",
            "classification": "tested",
            "receiver_use": "safe_workflow_assumption",
            "note": (
                "Session-start/session-end, packet, delta, readiness, and receiver guards are regression-backed enough "
                "to reuse as current workflow discipline."
            ),
        },
        {
            "lane": "continuity_effectiveness",
            "classification": "runtime_present",
            "receiver_use": "bounded_continuity_help",
            "note": (
                "Claims, checkpoints, compactions, and subject/working-style surfaces are live and partially tested, "
                "but broader cross-session effectiveness is still a bounded runtime claim rather than a proven quality guarantee."
            ),
        },
        {
            "lane": "council_mechanics",
            "classification": "tested",
            "receiver_use": "safe_mechanism_assumption",
            "note": (
                "Council mechanics, dossier extraction, and suppression visibility are backed well enough to trust the mechanism shape."
            ),
        },
        {
            "lane": "council_decision_quality",
            "classification": "descriptive_only",
            "receiver_use": "context_only",
            "note": (
                "Agreement, coherence, and confidence posture still describe internal review context, not calibrated correctness."
            ),
        },
        {
            "lane": "axiom_and_theory_claims",
            "classification": "document_backed",
            "receiver_use": "intent_and_boundary_only",
            "note": (
                "Higher-order axioms and philosophical claims remain important, but they are not uniformly runtime-hard or regression-backed."
            ),
        },
    ]
    counts = Counter(str(entry["classification"]) for entry in lanes)
    return {
        "summary_text": (
            "evidence=tested(session_control_and_handoff,council_mechanics) "
            "runtime_present(continuity_effectiveness) "
            "descriptive_only(council_decision_quality) "
            "document_backed(axiom_and_theory_claims)"
        ),
        "classification_counts": {
            "tested": int(counts.get("tested", 0)),
            "runtime_present": int(counts.get("runtime_present", 0)),
            "descriptive_only": int(counts.get("descriptive_only", 0)),
            "document_backed": int(counts.get("document_backed", 0)),
        },
        "lanes": lanes,
        "receiver_rule": (
            "Use tested lanes for current workflow assumptions, runtime_present lanes as bounded mechanism presence, "
            "descriptive_only lanes as context not proof, and document_backed lanes as intent/boundary rather than runtime fact."
        ),
    }


def _build_subject_anchor(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    if not snapshot:
        return {}
    return {
        "summary": str(snapshot.get("summary", "")).strip(),
        "stable_vows": _slice_strings(snapshot.get("stable_vows"), 4),
        "durable_boundaries": _slice_strings(snapshot.get("durable_boundaries"), 4),
        "decision_preferences": _slice_strings(snapshot.get("decision_preferences"), 4),
        "verified_routines": _slice_strings(snapshot.get("verified_routines"), 4),
        "active_threads": _slice_strings(snapshot.get("active_threads"), 4),
    }


def _build_working_style_anchor(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    if not snapshot:
        return {}

    decision_preferences = _slice_strings(snapshot.get("decision_preferences"), 4)
    verified_routines = _slice_strings(snapshot.get("verified_routines"), 4)
    guardrail_boundaries = _slice_strings(snapshot.get("durable_boundaries"), 3)
    base_summary = str(snapshot.get("summary", "")).strip()

    if not any((decision_preferences, verified_routines, guardrail_boundaries, base_summary)):
        return {}

    summary_parts: List[str] = []
    if decision_preferences:
        summary_parts.append(f"prefs={'; '.join(decision_preferences[:2])}")
    if verified_routines:
        summary_parts.append(f"routines={'; '.join(verified_routines[:2])}")
    if not summary_parts and base_summary:
        summary_parts.append(base_summary)

    return {
        "summary": " | ".join(summary_parts) if summary_parts else base_summary,
        "decision_preferences": decision_preferences,
        "verified_routines": verified_routines,
        "guardrail_boundaries": guardrail_boundaries,
        "receiver_posture": "advisory_apply_not_promote",
        "prompt_defaults": list(_PROMPT_STYLE_DEFAULTS),
        "render_caveat": _RENDER_BOUNDARY_CAVEAT,
    }


def _build_repo_progress_snapshot(repo_root: str | Path | None = None) -> Dict[str, Any]:
    repo_path = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[1]
    branch = _run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_path)
    head = _run_git_command(["git", "rev-parse", "--short", "HEAD"], cwd=repo_path)
    status_output = _run_git_command(["git", "status", "--short"], cwd=repo_path)

    if not branch or not head or status_output is None:
        return {
            "available": False,
            "branch": "",
            "head": "",
            "staged_count": 0,
            "modified_count": 0,
            "untracked_count": 0,
            "dirty_count": 0,
            "path_preview": [],
        }

    staged_count = 0
    modified_count = 0
    untracked_count = 0
    path_preview: List[str] = []

    for raw_line in status_output.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if line.startswith("??"):
            untracked_count += 1
        else:
            index_state = line[0] if len(line) > 0 else " "
            worktree_state = line[1] if len(line) > 1 else " "
            if index_state not in {" ", "?"}:
                staged_count += 1
            if worktree_state not in {" ", "?"}:
                modified_count += 1
        path_text = line[3:].strip() if len(line) >= 4 else line.strip()
        if path_text and path_text not in path_preview and len(path_preview) < 5:
            path_preview.append(path_text)

    dirty_count = staged_count + modified_count + untracked_count
    return {
        "available": True,
        "branch": branch,
        "head": head,
        "staged_count": staged_count,
        "modified_count": modified_count,
        "untracked_count": untracked_count,
        "dirty_count": dirty_count,
        "path_preview": path_preview,
    }


def _run_git_command(command: List[str], *, cwd: Path) -> str | None:
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except (FileNotFoundError, OSError):
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.rstrip("\r\n")


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


def _slice_strings(values: Iterable[Any] | None, limit: int) -> List[str]:
    return _unique_ordered(values or [])[: max(0, int(limit))]
