from typing import Dict, List, Optional, Any, Union, TYPE_CHECKING
import warnings

if TYPE_CHECKING:
    from tonesoul.council.base import IPerspective
    from tonesoul.council.types import CouncilVerdict, PerspectiveType

STANCE_SCORES = {
    "approve": 1.0,
    "review": 0.5,
    "note": 0.25,
    "hold": 0.0,
    "defer": 0.0,
    "block": -1.0,
}

RISK_ROLES = {"Risk", "Opposition"}
AUDIT_ROLES = {"Audit", "Recorder"}


def _decision_mode(context: Dict[str, object]) -> str:
    time_island = context.get("time_island", {}) if isinstance(context, dict) else {}
    kairos = time_island.get("kairos", {}) if isinstance(time_island, dict) else {}
    return str(kairos.get("decision_mode", "normal"))


def _collect_operational_roles(selected_frames: List[Dict[str, object]]) -> List[str]:
    roles: List[str] = []
    for frame in selected_frames:
        if not isinstance(frame, dict):
            continue
        frame_roles = frame.get("roles")
        if isinstance(frame_roles, list):
            roles.extend(str(role) for role in frame_roles)
    return roles


def _collect_governance_roles(
    selected_frames: List[Dict[str, object]],
    role_summary: Optional[Dict[str, object]],
) -> List[str]:
    if isinstance(role_summary, dict):
        roles = role_summary.get("governance_roles")
        if isinstance(roles, list) and roles:
            return [str(role) for role in roles]
    roles: List[str] = []
    for frame in selected_frames:
        if not isinstance(frame, dict):
            continue
        frame_roles = frame.get("governance_roles")
        if isinstance(frame_roles, list):
            for role in frame_roles:
                if role not in roles:
                    roles.append(str(role))
    return roles


def _governance_level(role: str, catalog: Dict[str, object]) -> int:
    governance = catalog.get("governance_roles")
    governance = governance if isinstance(governance, dict) else {}
    meta = governance.get(role)
    if isinstance(meta, dict):
        level = meta.get("level")
        if isinstance(level, int):
            return level
    return 1


def _stance_for_role(
    role: str,
    decision_mode: str,
    risk_roles: List[str],
    audit_roles: List[str],
) -> str:
    if decision_mode == "lockdown":
        return "hold"
    if risk_roles:
        return "review" if role in ("guardian", "arbiter") else "note"
    if audit_roles:
        return "review" if role in ("guardian", "arbiter") else "approve"
    return "approve"


def _decision_from_score(score: float, decision_mode: str) -> str:
    if decision_mode == "lockdown":
        return "hold"
    if score >= 0.7:
        return "proceed"
    if score >= 0.4:
        return "review"
    return "hold"


def _decision_status(decision: str) -> str:
    mapping = {
        "proceed": "pass",
        "review": "attention",
        "hold": "block",
    }
    return mapping.get(decision, "attention")


def build_council_summary(
    context: Dict[str, object],
    selected_frames: List[Dict[str, object]],
    role_summary: Optional[Dict[str, object]],
    role_catalog: Optional[Dict[str, object]],
) -> Dict[str, object]:
    role_catalog = role_catalog if isinstance(role_catalog, dict) else {}
    operational_roles = _collect_operational_roles(selected_frames)
    risk_roles = sorted({role for role in operational_roles if role in RISK_ROLES})
    audit_roles = sorted({role for role in operational_roles if role in AUDIT_ROLES})
    decision_mode = _decision_mode(context)
    governance_roles = _collect_governance_roles(selected_frames, role_summary)

    votes: List[Dict[str, object]] = []
    total_weight = 0.0
    weighted_score = 0.0
    approval_weight = 0.0

    for role in governance_roles:
        level = _governance_level(role, role_catalog)
        stance = _stance_for_role(role, decision_mode, risk_roles, audit_roles)
        weight = float(level)
        score = STANCE_SCORES.get(stance, 0.0)
        votes.append(
            {
                "governance_role": role,
                "weight": weight,
                "stance": stance,
                "score": round(score, 2),
            }
        )
        total_weight += weight
        weighted_score += weight * score
        if stance == "approve":
            approval_weight += weight

    normalized_score = weighted_score / total_weight if total_weight else 0.0
    dissent_ratio = 1.0 - (approval_weight / total_weight) if total_weight else 1.0
    decision = _decision_from_score(normalized_score, decision_mode)
    decision_status = _decision_status(decision)
    score_round = round(normalized_score, 3)
    dissent_round = round(dissent_ratio, 3)
    decision_summary = (
        f"{decision_status.upper()}: {decision} (score={score_round}, dissent={dissent_round})"
    )

    return {
        "decision": decision,
        "decision_status": decision_status,
        "decision_summary": decision_summary,
        "decision_mode": decision_mode,
        "weighted_score": score_round,
        "dissent_ratio": dissent_round,
        "signals": {
            "risk_roles": risk_roles,
            "audit_roles": audit_roles,
        },
        "votes": votes,
    }


def run_role_council(
    draft_output: str,
    context: Optional[Dict[str, object]] = None,
    user_intent: Optional[str] = None,
    perspectives: Optional[
        Union[
            "IPerspective",
            List[Union["IPerspective", "PerspectiveType", str]],
            Dict[Union["PerspectiveType", str], Dict[str, Any]],
            "PerspectiveType",
            str,
        ]
    ] = None,
    perspective_config: Optional[Dict[Union["PerspectiveType", str], Dict[str, Any]]] = None,
    coherence_threshold: float = 0.6,
    block_threshold: float = 0.3,
    selected_frames: Optional[List[Dict[str, object]]] = None,
    role_summary: Optional[Dict[str, object]] = None,
    role_catalog: Optional[Dict[str, object]] = None,
) -> "CouncilVerdict":
    warnings.warn(
        "tonesoul.role_council.run_role_council is deprecated; use tonesoul.council.runtime.CouncilRuntime",
        DeprecationWarning,
        stacklevel=2,
    )
    from .council.runtime import CouncilRuntime, CouncilRequest

    request = CouncilRequest(
        draft_output=draft_output,
        context=context or {},
        user_intent=user_intent,
        perspectives=perspectives,
        perspective_config=perspective_config,
        coherence_threshold=coherence_threshold,
        block_threshold=block_threshold,
        selected_frames=selected_frames,
        role_summary=role_summary,
        role_catalog=role_catalog,
    )
    return CouncilRuntime().deliberate(request)
