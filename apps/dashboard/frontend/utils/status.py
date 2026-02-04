"""
System status helpers for workspace panels.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import yaml


def get_workspace_root() -> Path:
    return Path(__file__).parent.parent.parent


def _memory_root(workspace: Path) -> Path:
    return workspace / "memory"


def _conversation_ledger_path(workspace: Path) -> Path:
    return _memory_root(workspace) / "conversation_ledger.jsonl"


def _summary_ledger_path(workspace: Path) -> Path:
    return _memory_root(workspace) / "conversation_summary.jsonl"


def _persona_trace_path(workspace: Path) -> Path:
    return _memory_root(workspace) / "persona_trace.jsonl"


def _persona_dimension_path(workspace: Path) -> Path:
    return _memory_root(workspace) / "persona_dimension_ledger.jsonl"


def _read_json(path: Path) -> Optional[Dict[str, object]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _read_jsonl(path: Path) -> List[Dict[str, object]]:
    if not path.exists():
        return []
    entries: List[Dict[str, object]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(payload, dict):
                    entries.append(payload)
    except Exception:
        return []
    return entries


def _read_last_jsonl(path: Path) -> Optional[Dict[str, object]]:
    entries = _read_jsonl(path)
    return entries[-1] if entries else None


def _count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    count += 1
    except Exception:
        return 0
    return count


def _resolve_runtime_dir(workspace: Path) -> Path:
    env_dir = os.getenv("TS_RUNTIME_DIR")
    if env_dir:
        return Path(env_dir).expanduser()
    return workspace / "runtime"


def _latest_run_dir(workspace: Path) -> Optional[Path]:
    run_root = workspace / "run" / "execution"
    if not run_root.exists():
        return None
    runs = [p for p in run_root.iterdir() if p.is_dir()]
    if not runs:
        return None
    return max(runs, key=lambda p: p.stat().st_mtime)


def load_latest_intent_verification(workspace: Path) -> Optional[Dict[str, object]]:
    run_dir = _latest_run_dir(workspace)
    if not run_dir:
        return None
    payload = _read_json(run_dir / "intent_verification.json")
    if not payload:
        return None
    payload["_run_id"] = run_dir.name
    return payload


def load_latest_control_result(workspace: Path) -> Optional[Dict[str, object]]:
    runtime_dir = _resolve_runtime_dir(workspace)
    return _read_json(runtime_dir / "control_result.json")


def _load_persona_profile(workspace: Path, persona_id: str) -> Optional[Dict[str, object]]:
    if not persona_id:
        return None
    path = workspace / "memory" / "personas" / f"{persona_id}.yaml"
    if not path.exists():
        return None
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    return {
        "id": payload.get("id") or persona_id,
        "name": payload.get("name"),
        "home_vector": payload.get("home_vector"),
        "tolerance": payload.get("tolerance"),
        "council_weights": payload.get("council_weights"),
        "goal_weights": payload.get("goal_weights"),
    }


def build_status_snapshot(workspace: Path) -> Dict[str, object]:
    conversation_path = _conversation_ledger_path(workspace)
    summary_path = _summary_ledger_path(workspace)
    persona_trace_path = _persona_trace_path(workspace)
    persona_dimension_path = _persona_dimension_path(workspace)

    conversation_last = _read_last_jsonl(conversation_path)
    persona_trace_last = _read_last_jsonl(persona_trace_path)
    persona_dimension_last = _read_last_jsonl(persona_dimension_path)

    run_dir = _latest_run_dir(workspace)
    intent_verification = load_latest_intent_verification(workspace)
    control_result = load_latest_control_result(workspace)

    persona_id = (
        (persona_trace_last or {}).get("persona_id") or os.getenv("TS_PERSONA_ID") or "base"
    )
    persona_profile = _load_persona_profile(workspace, persona_id)

    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "conversation": {
            "count": _count_jsonl(conversation_path),
            "last": conversation_last,
        },
        "persona": {
            "id": persona_id,
            "trace": persona_trace_last,
            "profile": persona_profile,
        },
        "dimension": {"last": persona_dimension_last},
        "intent_verification": intent_verification,
        "control_result": control_result,
        "run_id": run_dir.name if run_dir else None,
        "summary_count": _count_jsonl(summary_path),
    }


def _find_conversation_entry(workspace: Path, record_id: str) -> Optional[Dict[str, object]]:
    ledger_path = _conversation_ledger_path(workspace)
    if not ledger_path.exists():
        return None
    if not record_id:
        return _read_last_jsonl(ledger_path)
    for entry in _read_jsonl(ledger_path):
        if entry.get("record_id") == record_id:
            return entry
    return None


def _conversation_fields(entry: Dict[str, object]) -> Dict[str, str]:
    context = entry.get("context") if isinstance(entry.get("context"), dict) else {}
    user_message = context.get("user_message") or entry.get("user_message") or ""
    response = entry.get("response") or ""
    return {
        "record_id": entry.get("record_id") or "",
        "timestamp": entry.get("timestamp") or "",
        "status": entry.get("status") or "",
        "user_message": user_message,
        "response": response,
    }


def _truncate(text: str, limit: int = 180) -> str:
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


def build_conversation_summary(
    workspace: Path,
    record_id: str,
    persona_id: Optional[str] = None,
    trace_record_id: Optional[str] = None,
) -> Optional[Dict[str, object]]:
    snapshot = build_status_snapshot(workspace)
    entry = _find_conversation_entry(workspace, record_id) or snapshot.get("conversation", {}).get(
        "last"
    )
    if not entry:
        return None

    convo = _conversation_fields(entry)
    persona_snapshot = snapshot.get("persona", {})
    persona_trace = (
        persona_snapshot.get("trace") if isinstance(persona_snapshot.get("trace"), dict) else {}
    )
    shadow = persona_trace.get("shadow") if isinstance(persona_trace.get("shadow"), dict) else {}

    summary = {
        "summary_id": datetime.now().strftime("summary_%Y%m%d%H%M%S"),
        "record_id": convo["record_id"] or record_id,
        "timestamp": convo["timestamp"] or snapshot.get("timestamp"),
        "status": convo["status"],
        "user_message": convo["user_message"],
        "assistant_summary": _truncate(convo["response"]),
        "persona": {
            "id": persona_id or persona_snapshot.get("id"),
            "trace_record_id": trace_record_id,
            "vector_estimate": shadow.get("vector_estimate"),
            "vector_distance": shadow.get("vector_distance"),
            "profile": persona_snapshot.get("profile"),
        },
        "intent": _extract_intent_fields(snapshot.get("intent_verification")),
        "control": _extract_control_fields(snapshot.get("control_result")),
        "run_id": snapshot.get("run_id"),
    }
    return summary


def log_conversation_summary(
    record_id: str,
    persona_id: Optional[str] = None,
    trace_record_id: Optional[str] = None,
) -> Optional[str]:
    workspace = get_workspace_root()
    summary = build_conversation_summary(workspace, record_id, persona_id, trace_record_id)
    if not summary:
        return None
    path = _summary_ledger_path(workspace)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(summary, ensure_ascii=False) + "\n")
    except Exception:
        return None
    return summary.get("summary_id")


def load_latest_summary(workspace: Path) -> Optional[Dict[str, object]]:
    return _read_last_jsonl(_summary_ledger_path(workspace))
