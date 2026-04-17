"""
ToneSoul API Server
Connects frontend to PreOutputCouncil backend.

DEPRECATION NOTICE:
This Flask entrypoint is kept for legacy/local compatibility and is in maintenance mode.
Prefer `api/chat.py` for the active serverless chat entrypoint and
`tonesoul.unified_pipeline.UnifiedPipeline` for runtime orchestration.
"""

import hashlib
import json
import os
import secrets
import sys
import traceback
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flask import Flask, jsonify, request
from flask_cors import CORS

from tonesoul.council import CouncilRequest, CouncilRuntime
from tonesoul.council.self_journal import load_recent_memory
from tonesoul.evolution import ContextDistiller
from tonesoul.memory import consolidate
from tonesoul.memory.crystallizer import MemoryCrystallizer
from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource, SoulDB
from tonesoul.supabase_persistence import SupabasePersistence

app = Flask(__name__, static_folder="../council-playground", static_url_path="")
_DEFAULT_CORS_ORIGINS = "http://localhost:5000,http://127.0.0.1:5000"
_cors_origins = [
    origin.strip()
    for origin in os.environ.get("TONESOUL_CORS_ORIGINS", _DEFAULT_CORS_ORIGINS).split(",")
    if origin.strip()
]
CORS(app, resources={r"/api/*": {"origins": _cors_origins}})

council_runtime = CouncilRuntime()
_MAX_ESCAPE_SEED_ITEMS = 50
_MAX_PAGINATION_LIMIT = 200
_READ_API_TOKEN_ENV = "TONESOUL_READ_API_TOKEN"
_WRITE_API_TOKEN_ENV = "TONESOUL_WRITE_API_TOKEN"
_EVOLUTION_CACHE_PATH_ENV = "TONESOUL_EVOLUTION_CACHE_PATH"
_AUTH_FAIL_CLOSED_ENV = "TONESOUL_AUTH_FAIL_CLOSED"
_RATE_LIMIT_ENABLED_ENV = "TONESOUL_ENABLE_RATE_LIMIT"
_RATE_LIMIT_CHAT_ENV = "TONESOUL_RATE_LIMIT_CHAT_PER_MINUTE"
_RATE_LIMIT_VALIDATE_ENV = "TONESOUL_RATE_LIMIT_VALIDATE_PER_MINUTE"
_RATE_LIMIT_WINDOW_SECONDS_ENV = "TONESOUL_RATE_LIMIT_WINDOW_SECONDS"
_CHAT_CACHE_ENABLED_ENV = "TONESOUL_CHAT_CACHE_ENABLED"
_CHAT_CACHE_TTL_SECONDS_ENV = "TONESOUL_CHAT_CACHE_TTL_SECONDS"
_CHAT_CACHE_MAX_ITEMS_ENV = "TONESOUL_CHAT_CACHE_MAX_ITEMS"
_CHAT_CACHE_SCHEMA_VERSION = "v1"
_MAX_HISTORY_ITEMS = 500
_VTP_CONTEXT_FLAGS = (
    "vtp_force_trigger",
    "vtp_axiom_conflict",
    "vtp_refusal_to_compromise",
    "vtp_user_confirmed",
)
_ALLOWED_COUNCIL_MODES = {"rules", "rules_only", "hybrid", "full_llm"}
_ALLOWED_EXECUTION_PROFILES = {"interactive", "engineering"}
supabase_persistence = SupabasePersistence.from_env()
_context_distiller: ContextDistiller | None = None
_soul_db: SoulDB | None = None
_rate_limit_lock = Lock()
_rate_limit_state: dict[tuple[str, str], list[float]] = {}
_chat_cache_lock = Lock()
_chat_cache_state: dict[str, tuple[float, dict]] = {}
_ALLOWED_HISTORY_ROLES = {"user", "assistant", "system"}


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _read_api_token() -> str:
    value = os.environ.get(_READ_API_TOKEN_ENV)
    if not isinstance(value, str):
        return ""
    return value.strip()


def _read_write_api_token() -> str:
    value = os.environ.get(_WRITE_API_TOKEN_ENV)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return _read_api_token()


def _is_production_env() -> bool:
    if _env_flag("TONESOUL_PRODUCTION", default=False):
        return True
    env_name = (os.environ.get("TONESOUL_ENV") or os.environ.get("FLASK_ENV") or "").strip().lower()
    return env_name == "production"


def _read_positive_int_env(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return max(1, int(default))
    try:
        parsed = int(str(raw).strip())
    except (TypeError, ValueError):
        return max(1, int(default))
    return max(1, parsed)


def _is_rate_limit_enabled() -> bool:
    if _RATE_LIMIT_ENABLED_ENV in os.environ:
        return _env_flag(_RATE_LIMIT_ENABLED_ENV, default=False)
    return _is_production_env()


def _client_identifier() -> str:
    forwarded = str(request.headers.get("X-Forwarded-For") or "").strip()
    if forwarded:
        first = forwarded.split(",")[0].strip()
        if first:
            return first
    return str(request.remote_addr or "unknown")


def _rate_limit_for_endpoint(endpoint_name: str) -> int:
    if endpoint_name == "chat":
        return _read_positive_int_env(_RATE_LIMIT_CHAT_ENV, default=60)
    if endpoint_name == "validate":
        return _read_positive_int_env(_RATE_LIMIT_VALIDATE_ENV, default=120)
    return _read_positive_int_env(_RATE_LIMIT_VALIDATE_ENV, default=120)


def _rate_limit_window_seconds() -> int:
    return _read_positive_int_env(_RATE_LIMIT_WINDOW_SECONDS_ENV, default=60)


def _reset_rate_limit_state() -> None:
    with _rate_limit_lock:
        _rate_limit_state.clear()


def _apply_rate_limit(endpoint_name: str):
    if not _is_rate_limit_enabled():
        return None
    if app.config.get("TESTING"):
        return None

    limit = _rate_limit_for_endpoint(endpoint_name)
    window = _rate_limit_window_seconds()
    now = datetime.now(timezone.utc).timestamp()
    client_id = _client_identifier()
    bucket_key = (endpoint_name, client_id)

    with _rate_limit_lock:
        history = _rate_limit_state.get(bucket_key, [])
        threshold = now - float(window)
        history = [ts for ts in history if ts >= threshold]
        if len(history) >= limit:
            retry_after = max(1, int(history[0] + float(window) - now))
            response = jsonify(
                {
                    "error": "Too Many Requests",
                    "endpoint": endpoint_name,
                    "retry_after_seconds": retry_after,
                }
            )
            response.headers["Retry-After"] = str(retry_after)
            _rate_limit_state[bucket_key] = history
            return response, 429
        history.append(now)
        _rate_limit_state[bucket_key] = history
    return None


def _is_chat_cache_enabled() -> bool:
    if _CHAT_CACHE_ENABLED_ENV in os.environ:
        return _env_flag(_CHAT_CACHE_ENABLED_ENV, default=False)
    return not bool(app.config.get("TESTING"))


def _chat_cache_ttl_seconds() -> int:
    return _read_positive_int_env(_CHAT_CACHE_TTL_SECONDS_ENV, default=60)


def _chat_cache_max_items() -> int:
    return _read_positive_int_env(_CHAT_CACHE_MAX_ITEMS_ENV, default=256)


def _build_chat_cache_key(
    *,
    message: str,
    history: list,
    full_analysis: bool,
    execution_profile: str,
    council_mode: str | None,
    perspective_config: dict | None,
    persona_config: dict | None,
    prior_tension: dict | None,
) -> str:
    canonical_payload = {
        "schema_version": _CHAT_CACHE_SCHEMA_VERSION,
        "message": message,
        "history": history,
        "full_analysis": full_analysis,
        "execution_profile": execution_profile,
        "council_mode": council_mode,
        "perspective_config": perspective_config,
        "persona_config": persona_config,
        "prior_tension": prior_tension,
    }
    canonical = json.dumps(
        canonical_payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _prune_chat_cache(now_ts: float) -> None:
    expired_keys = [
        key for key, (expires_at, _) in _chat_cache_state.items() if expires_at <= now_ts
    ]
    for key in expired_keys:
        _chat_cache_state.pop(key, None)

    max_items = _chat_cache_max_items()
    if len(_chat_cache_state) <= max_items:
        return

    overflow = len(_chat_cache_state) - max_items
    eviction_order = sorted(_chat_cache_state.items(), key=lambda item: item[1][0])
    for key, _ in eviction_order[:overflow]:
        _chat_cache_state.pop(key, None)


def _chat_cache_get(cache_key: str) -> dict | None:
    if not _is_chat_cache_enabled():
        return None
    now_ts = datetime.now(timezone.utc).timestamp()
    with _chat_cache_lock:
        _prune_chat_cache(now_ts)
        entry = _chat_cache_state.get(cache_key)
        if entry is None:
            return None
        expires_at, payload = entry
        if expires_at <= now_ts:
            _chat_cache_state.pop(cache_key, None)
            return None
        return deepcopy(payload)


def _chat_cache_set(cache_key: str, payload: dict) -> None:
    if not _is_chat_cache_enabled():
        return
    now_ts = datetime.now(timezone.utc).timestamp()
    expires_at = now_ts + float(_chat_cache_ttl_seconds())
    with _chat_cache_lock:
        _chat_cache_state[cache_key] = (expires_at, deepcopy(payload))
        _prune_chat_cache(now_ts)


def _reset_chat_cache_state() -> None:
    with _chat_cache_lock:
        _chat_cache_state.clear()


def _persist_chat_side_effects(
    *,
    conversation_id: str | None,
    session_id: str | None,
    user_message: str,
    assistant_message: str,
    verdict: dict | None,
    evolution_payload: dict | None = None,
) -> None:
    if not (supabase_persistence.enabled and conversation_id):
        return

    supabase_persistence.record_chat_exchange(
        conversation_id=conversation_id,
        user_message=user_message,
        assistant_message=assistant_message,
        deliberation=verdict if isinstance(verdict, dict) else None,
        session_id=session_id,
    )
    if isinstance(verdict, dict):
        supabase_persistence.record_chat_audit(
            conversation_id=conversation_id,
            verdict=verdict,
        )
    if isinstance(evolution_payload, dict) and evolution_payload:
        record_evolution = getattr(supabase_persistence, "record_evolution_result", None)
        if callable(record_evolution):
            record_evolution(
                conversation_id=conversation_id,
                result_type="chat_semantic_state",
                payload=evolution_payload,
            )


def _extract_bearer_token(authorization_header: str | None) -> str:
    if not isinstance(authorization_header, str):
        return ""
    header = authorization_header.strip()
    if not header:
        return ""
    parts = header.split(" ", 1)
    if len(parts) != 2:
        return ""
    scheme, token = parts
    if scheme.lower() != "bearer":
        return ""
    return token.strip()


def _extract_named_token(*header_names: str) -> str:
    for header_name in header_names:
        value = request.headers.get(header_name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _require_api_auth(
    *,
    required_token: str,
    config_error: str,
    unauthorized_error: str,
    header_names: tuple[str, ...],
):
    fail_closed = _env_flag(_AUTH_FAIL_CLOSED_ENV, default=_is_production_env())
    if not required_token:
        if fail_closed:
            return jsonify({"error": config_error}), 503
        return None

    provided_token = _extract_bearer_token(request.headers.get("Authorization"))
    if not provided_token:
        provided_token = _extract_named_token(*header_names)

    if not provided_token or not secrets.compare_digest(provided_token, required_token):
        return jsonify({"error": unauthorized_error}), 401
    return None


def _require_read_api_auth():
    return _require_api_auth(
        required_token=_read_api_token(),
        config_error="Read API token not configured",
        unauthorized_error="Unauthorized read access",
        header_names=("X-ToneSoul-Read-Token",),
    )


def _require_write_api_auth():
    return _require_api_auth(
        required_token=_read_write_api_token(),
        config_error="Write API token not configured",
        unauthorized_error="Unauthorized write access",
        header_names=("X-ToneSoul-Write-Token", "X-ToneSoul-Read-Token"),
    )


def _json_payload():
    payload = request.get_json(silent=True)
    return payload if isinstance(payload, dict) else None


def _require_optional_string(data: dict, key: str) -> tuple[str | None, tuple | None]:
    value = data.get(key)
    if value is None:
        return None, None
    if isinstance(value, str):
        return value, None
    return None, (jsonify({"error": f"Invalid {key}"}), 400)


def _require_optional_bool(data: dict, key: str) -> tuple[bool | None, tuple | None]:
    value = data.get(key)
    if value is None:
        return None, None
    if isinstance(value, bool):
        return value, None
    return None, (jsonify({"error": f"Invalid {key}"}), 400)


def _require_optional_dict(data: dict, key: str) -> tuple[dict | None, tuple | None]:
    value = data.get(key)
    if value is None:
        return None, None
    if isinstance(value, dict):
        return value, None
    return None, (jsonify({"error": f"Invalid {key}"}), 400)


def _require_optional_council_mode(data: dict, key: str) -> tuple[str | None, tuple | None]:
    value = data.get(key)
    if value is None:
        return None, None
    if not isinstance(value, str):
        return None, (jsonify({"error": f"Invalid {key}"}), 400)
    mode = value.strip().lower()
    if mode not in _ALLOWED_COUNCIL_MODES:
        return None, (jsonify({"error": f"Invalid {key}"}), 400)
    if mode == "rules_only":
        mode = "rules"
    return mode, None


def _require_optional_execution_profile(data: dict, key: str) -> tuple[str | None, tuple | None]:
    value = data.get(key)
    if value is None:
        return None, None
    if not isinstance(value, str):
        return None, (jsonify({"error": f"Invalid {key}"}), 400)
    profile = value.strip().lower()
    if profile not in _ALLOWED_EXECUTION_PROFILES:
        return None, (jsonify({"error": f"Invalid {key}"}), 400)
    return profile, None


def _resolve_execution_profile(data: dict, explicit_profile: str | None) -> str:
    if explicit_profile in _ALLOWED_EXECUTION_PROFILES:
        return explicit_profile

    elisa_context = data.get("elisa_context")
    if isinstance(elisa_context, dict):
        source = elisa_context.get("source")
        if isinstance(source, str) and source.strip().lower() == "elisa_ide":
            return "engineering"

    return "interactive"


def _apply_execution_profile_defaults(
    council_mode: str | None,
    perspective_config: dict | None,
    execution_profile: str,
) -> str | None:
    if perspective_config is not None or council_mode is not None:
        return council_mode
    return "full_llm" if execution_profile == "engineering" else "rules"


def _validate_perspective_config(config: dict) -> tuple[dict | None, tuple | None]:
    for perspective_name, perspective_options in config.items():
        if not isinstance(perspective_name, str) or not perspective_name.strip():
            return None, (jsonify({"error": "Invalid perspective_config"}), 400)
        if not isinstance(perspective_options, dict):
            return None, (jsonify({"error": "Invalid perspective_config"}), 400)
    return config, None


def _validate_persona_config(config: dict) -> tuple[dict | None, tuple | None]:
    scalar_keys = ("name", "style", "risk_sensitivity", "response_length")
    for key in scalar_keys:
        value = config.get(key)
        if value is not None and not isinstance(value, str):
            return None, (jsonify({"error": "Invalid persona"}), 400)

    weights = config.get("weights")
    if weights is not None:
        if not isinstance(weights, dict):
            return None, (jsonify({"error": "Invalid persona"}), 400)
        for key in ("meaning", "practical", "safety"):
            value = weights.get(key)
            if value is not None and not isinstance(value, (int, float)):
                return None, (jsonify({"error": "Invalid persona"}), 400)

    custom_roles = config.get("custom_roles")
    if custom_roles is not None:
        if not isinstance(custom_roles, list) or len(custom_roles) > 8:
            return None, (jsonify({"error": "Invalid persona"}), 400)
        for role in custom_roles:
            if not isinstance(role, dict):
                return None, (jsonify({"error": "Invalid persona"}), 400)
            for key in ("id", "name", "description", "prompt_hint"):
                value = role.get(key)
                if value is not None and not isinstance(value, str):
                    return None, (jsonify({"error": "Invalid persona"}), 400)

            attachments = role.get("attachments")
            if attachments is not None:
                if not isinstance(attachments, list) or len(attachments) > 6:
                    return None, (jsonify({"error": "Invalid persona"}), 400)
                for attachment in attachments:
                    if not isinstance(attachment, dict):
                        return None, (jsonify({"error": "Invalid persona"}), 400)
                    for key in ("id", "label", "path", "note"):
                        value = attachment.get(key)
                        if value is not None and not isinstance(value, str):
                            return None, (jsonify({"error": "Invalid persona"}), 400)

    return config, None


def _require_list(data: dict, key: str) -> tuple[list | None, tuple | None]:
    value = data.get(key)
    if isinstance(value, list):
        return value, None
    return None, (jsonify({"error": f"Invalid {key}"}), 400)


def _require_optional_list(data: dict, key: str) -> tuple[list | None, tuple | None]:
    value = data.get(key)
    if value is None:
        return None, None
    if isinstance(value, list):
        return value, None
    return None, (jsonify({"error": f"Invalid {key}"}), 400)


def _validate_history_entries(history: list, *, field_name: str = "history") -> tuple | None:
    if len(history) > _MAX_HISTORY_ITEMS:
        return jsonify({"error": f"{field_name} too long"}), 400

    for item in history:
        if not isinstance(item, dict):
            return jsonify({"error": f"Invalid {field_name} item"}), 400

        role = item.get("role")
        content = item.get("content")
        if not isinstance(role, str) or role.strip().lower() not in _ALLOWED_HISTORY_ROLES:
            return jsonify({"error": f"Invalid {field_name} item"}), 400
        if not isinstance(content, str) or not content.strip():
            return jsonify({"error": f"Invalid {field_name} item"}), 400
    return None


def _error_response(
    message: str,
    status_code: int,
    exc: Exception | None = None,
    extra: dict | None = None,
):
    error_id = uuid.uuid4().hex[:12]
    if exc is not None:
        traceback.print_exc()
        print(f"[ERROR] id={error_id}: {exc}", file=sys.stderr)
    payload = {"error": message, "error_id": error_id}
    if extra:
        payload.update(extra)
    return jsonify(payload), status_code


def _parse_pagination(default_limit: int = 20) -> tuple[int, int]:
    raw_limit = request.args.get("limit", default_limit, type=int)
    raw_offset = request.args.get("offset", 0, type=int)
    limit = default_limit if raw_limit is None else raw_limit
    offset = 0 if raw_offset is None else raw_offset
    if limit <= 0:
        limit = default_limit
    if limit > _MAX_PAGINATION_LIMIT:
        limit = _MAX_PAGINATION_LIMIT
    if offset < 0:
        offset = 0
    return limit, offset


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _get_context_distiller() -> ContextDistiller:
    global _context_distiller
    cache_path = os.environ.get(_EVOLUTION_CACHE_PATH_ENV)
    if _context_distiller is None or _context_distiller.persistence is not supabase_persistence:
        _context_distiller = ContextDistiller(supabase_persistence, cache_path=cache_path)
    return _context_distiller


def _get_soul_db() -> SoulDB:
    global _soul_db
    if _soul_db is None:
        _soul_db = JsonlSoulDB()
    return _soul_db


def _get_evolution_summary_payload() -> dict:
    try:
        return _get_context_distiller().get_summary()
    except Exception:
        return {
            "total_patterns": 0,
            "conversations_analyzed": 0,
            "last_distilled_at": None,
            "time_range": [None, None],
            "pattern_breakdown": {},
            "summary": "Evolution summary unavailable.",
        }


def _build_prior_tension(conversation_id: str | None) -> dict | None:
    if not supabase_persistence.enabled:
        return None
    external_conversation_id = (conversation_id or "").strip()
    if not external_conversation_id:
        return None

    page = supabase_persistence.list_audit_logs(
        limit=5,
        offset=0,
        conversation_id=external_conversation_id,
    )
    logs = page.get("logs") if isinstance(page, dict) else None
    if not isinstance(logs, list) or not logs:
        return None

    highest_row = None
    highest_delta_t = float("-inf")
    for row in logs:
        if not isinstance(row, dict):
            continue
        raw_delta_t = row.get("delta_t")
        try:
            delta_t = float(raw_delta_t)
        except (TypeError, ValueError):
            continue
        if delta_t > highest_delta_t:
            highest_delta_t = delta_t
            highest_row = row

    if highest_row is None:
        return None

    return {
        "conversation_id": external_conversation_id,
        "delta_t": highest_delta_t,
        "gate_decision": highest_row.get("gate_decision"),
        "rationale": highest_row.get("rationale"),
        "created_at": highest_row.get("created_at"),
    }


def _coerce_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def _as_dict(value) -> dict:
    return value if isinstance(value, dict) else {}


def _as_list(value) -> list:
    return value if isinstance(value, list) else []


def _load_visual_chain_snapshot(max_mermaid_chars: int = 2000) -> dict:
    if app.config.get("TESTING"):
        return {}

    chain_path = Path("data") / "visual_chain.json"
    try:
        raw = json.loads(chain_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError, OSError):
        return {}

    frames = raw.get("frames") if isinstance(raw, dict) else None
    if not isinstance(frames, list) or not frames:
        return {}

    latest = frames[-1]
    if not isinstance(latest, dict):
        return {}

    tags_raw = latest.get("tags")
    tags = [str(tag).strip() for tag in tags_raw] if isinstance(tags_raw, list) else []
    tags = [tag for tag in tags if tag]
    data_payload = latest.get("data")
    mermaid = str(latest.get("mermaid") or "")
    snapshot = {
        "frame_id": str(latest.get("frame_id") or ""),
        "frame_type": str(latest.get("frame_type") or ""),
        "title": str(latest.get("title") or ""),
        "created_at": latest.get("created_at"),
        "branch": str(latest.get("branch") or ""),
        "tags": tags,
        "data": data_payload if isinstance(data_payload, dict) else {},
        "mermaid": mermaid[:max_mermaid_chars],
    }
    if not snapshot["frame_id"] and not snapshot["title"] and not snapshot["mermaid"]:
        return {}
    return snapshot


def _build_chat_evolution_payload(response_payload: dict) -> dict:
    deliberation = _as_dict(response_payload.get("deliberation"))
    return {
        "semantic_contradictions": _as_list(response_payload.get("semantic_contradictions")),
        "semantic_graph_summary": _as_dict(response_payload.get("semantic_graph_summary")),
        "dispatch_trace": _as_dict(response_payload.get("dispatch_trace")),
        "governance_brief": _as_dict(response_payload.get("governance_brief"))
        or _build_governance_brief(response_payload),
        "life_entry_brief": _as_dict(response_payload.get("life_entry_brief"))
        or _build_life_entry_brief(response_payload),
        "visual_chain_snapshot": _as_dict(deliberation.get("visual_chain_snapshot")),
        "captured_at": _utc_now(),
    }


def _summarize_text(value, max_chars: int = 160) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    normalized = " ".join(text.split())
    if len(normalized) <= max_chars:
        return normalized
    return normalized[: max_chars - 3].rstrip() + "..."


def _coerce_optional_float(value) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _build_crystal_freshness_brief() -> dict:
    """Return freshness posture for crystal governance observability."""
    try:
        summary = MemoryCrystallizer().freshness_summary(top_n_stale=3)
        if isinstance(summary, dict):
            return summary
    except Exception:
        pass
    return {
        "total_crystals": 0,
        "active_count": 0,
        "needs_verification_count": 0,
        "stale_count": 0,
        "mean_freshness": 0.0,
        "stale_rules": [],
    }


def _build_governance_brief(response_payload: dict) -> dict:
    verdict = _as_dict(response_payload.get("verdict"))
    deliberation = _as_dict(response_payload.get("deliberation"))
    soul_audit = _as_dict(deliberation.get("soulAudit"))
    decision_matrix = _as_dict(deliberation.get("decision_matrix"))
    divergence_quality = _as_dict(deliberation.get("divergence_quality"))
    next_moves = _as_list(deliberation.get("next_moves"))
    dispatch_trace = _as_dict(response_payload.get("dispatch_trace"))
    contradictions = _as_list(response_payload.get("semantic_contradictions"))

    first_move = ""
    if next_moves:
        first = next_moves[0]
        if isinstance(first, dict):
            first_move = _summarize_text(first.get("text") or first.get("label") or "")
        else:
            first_move = _summarize_text(first)

    coherence = _coerce_optional_float(verdict.get("coherence"))
    if coherence is not None:
        coherence = round(_clamp01(coherence), 3)

    return {
        "verdict": str(verdict.get("verdict") or "unknown"),
        "responsibility_tier": str(verdict.get("responsibility_tier") or "unknown"),
        "uncertainty_band": str(verdict.get("uncertainty_band") or "unknown"),
        "coherence": coherence,
        "soul_passed": bool(soul_audit.get("passed", False)),
        "contradiction_count": len(contradictions),
        "strategy": str(decision_matrix.get("ai_strategy_name") or "direct_response"),
        "divergence_band": str(divergence_quality.get("band") or "unknown"),
        "dispatch_state": str(dispatch_trace.get("state") or ""),
        "next_focus": first_move,
        "crystal_freshness": _build_crystal_freshness_brief(),
    }


def _build_life_entry_brief(response_payload: dict) -> dict:
    response_text = _summarize_text(response_payload.get("response") or "", max_chars=180)
    intervention_strategy = str(response_payload.get("intervention_strategy") or "").strip()
    trajectory = _as_dict(response_payload.get("trajectory_analysis"))
    dispatch_trace = _as_dict(response_payload.get("dispatch_trace"))
    deliberation = _as_dict(response_payload.get("deliberation"))
    decision_matrix = _as_dict(deliberation.get("decision_matrix"))

    trajectory_label = (
        str(trajectory.get("trajectory_mode") or "").strip()
        or str(trajectory.get("state") or "").strip()
        or str(dispatch_trace.get("mode") or "").strip()
    )

    return {
        "response_summary": response_text,
        "inner_intent": _summarize_text(decision_matrix.get("user_hidden_intent") or ""),
        "strategy": intervention_strategy or str(decision_matrix.get("ai_strategy_name") or ""),
        "persona_mode": str(response_payload.get("persona_mode") or ""),
        "trajectory_label": trajectory_label,
        "self_commit_count": len(_as_list(response_payload.get("self_commits"))),
        "rupture_count": len(_as_list(response_payload.get("ruptures"))),
        "emergent_value_count": len(_as_list(response_payload.get("emergent_values"))),
    }


def _map_perspective_to_chamber_role(perspective_name: str) -> str | None:
    normalized = perspective_name.strip().lower()
    if not normalized:
        return None
    if normalized in {"guardian", "aegis"} or "guardian" in normalized:
        return "guardian"
    if normalized in {"analyst", "engineer", "logos", "semantic_analyst"} or any(
        token in normalized for token in ("analyst", "engineer", "semantic")
    ):
        return "engineer"
    if normalized in {"philosopher", "critic", "advocate", "muse"} or any(
        token in normalized for token in ("philosopher", "critic", "advocate", "muse")
    ):
        return "philosopher"
    return None


def _normalize_chamber_role(value: str) -> str | None:
    normalized = value.strip().lower()
    if normalized in {"philosopher", "engineer", "guardian"}:
        return normalized
    return _map_perspective_to_chamber_role(normalized)


def _extract_role_friction(verdict: dict) -> dict[str, str]:
    divergence = _as_dict(verdict.get("divergence_analysis"))
    role_tensions = _as_list(divergence.get("role_tensions"))
    friction: dict[str, str] = {}

    for item in role_tensions:
        if not isinstance(item, dict):
            continue
        source_role = _normalize_chamber_role(str(item.get("from_role") or item.get("from") or ""))
        target_role = _normalize_chamber_role(str(item.get("to_role") or item.get("to") or ""))
        if source_role is None or target_role is None or source_role in friction:
            continue

        reason = str(item.get("reason") or "").strip()
        counter_reason = str(item.get("counter_reason") or "").strip()
        if reason and counter_reason:
            summary = f"{target_role}: {reason[:90]} | counter: {counter_reason[:90]}"
        elif reason:
            summary = f"{target_role}: {reason[:140]}"
        elif counter_reason:
            summary = f"{target_role}: {counter_reason[:140]}"
        else:
            continue
        friction[source_role] = summary

    return friction


def _build_divergence_quality_payload(verdict: dict) -> dict:
    divergence = _as_dict(verdict.get("divergence_analysis"))
    quality = _as_dict(divergence.get("quality"))
    if quality:
        return {
            "score": _clamp01(_coerce_float(quality.get("score"), default=0.0)),
            "band": str(quality.get("band") or "unknown"),
            "conflict_coverage": _clamp01(
                _coerce_float(quality.get("conflict_coverage"), default=0.0)
            ),
            "reasoning_specificity": _clamp01(
                _coerce_float(quality.get("reasoning_specificity"), default=0.0)
            ),
            "evidence_coverage": _clamp01(
                _coerce_float(quality.get("evidence_coverage"), default=0.0)
            ),
            "confidence_balance": _clamp01(
                _coerce_float(quality.get("confidence_balance"), default=0.0)
            ),
            "role_tension_coverage": _clamp01(
                _coerce_float(quality.get("role_tension_coverage"), default=0.0)
            ),
            "core_divergence": str(divergence.get("core_divergence") or ""),
            "role_tensions": _as_list(divergence.get("role_tensions")),
        }

    votes = _as_list(verdict.get("votes"))
    if not votes:
        return {
            "score": 0.0,
            "band": "unknown",
            "conflict_coverage": 0.0,
            "reasoning_specificity": 0.0,
            "evidence_coverage": 0.0,
            "confidence_balance": 0.0,
            "role_tension_coverage": 0.0,
            "core_divergence": str(divergence.get("core_divergence") or ""),
            "role_tensions": [],
        }

    conflicts = 0
    confidences: list[float] = []
    specificity_scores: list[float] = []
    evidence_votes = 0
    for vote in votes:
        if not isinstance(vote, dict):
            continue
        decision = str(vote.get("decision") or "").strip().lower()
        if decision in {"concern", "object", "block", "refine"}:
            conflicts += 1
        confidence = _clamp01(_coerce_float(vote.get("confidence"), default=0.0))
        confidences.append(confidence)
        reasoning = str(vote.get("reasoning") or "").strip()
        if reasoning:
            if " " in reasoning:
                specificity_scores.append(min(1.0, len([w for w in reasoning.split() if w]) / 16.0))
            else:
                specificity_scores.append(min(1.0, len(reasoning) / 48.0))
        evidence = vote.get("evidence")
        if isinstance(evidence, list) and any(str(item).strip() for item in evidence):
            evidence_votes += 1

    total_votes = max(1, len(votes))
    conflict_coverage = conflicts / float(total_votes)
    evidence_coverage = evidence_votes / float(total_votes)
    reasoning_specificity = (
        sum(specificity_scores) / float(len(specificity_scores)) if specificity_scores else 0.0
    )
    if confidences:
        spread = max(confidences) - min(confidences)
        confidence_balance = max(0.0, min(1.0, 1.0 - abs(spread - 0.35) / 0.35))
    else:
        confidence_balance = 0.0

    score = (
        conflict_coverage * 0.4
        + reasoning_specificity * 0.35
        + evidence_coverage * 0.1
        + confidence_balance * 0.15
    )
    if score >= 0.7:
        band = "high"
    elif score >= 0.45:
        band = "medium"
    else:
        band = "low"

    return {
        "score": round(_clamp01(score), 3),
        "band": band,
        "conflict_coverage": round(_clamp01(conflict_coverage), 3),
        "reasoning_specificity": round(_clamp01(reasoning_specificity), 3),
        "evidence_coverage": round(_clamp01(evidence_coverage), 3),
        "confidence_balance": round(_clamp01(confidence_balance), 3),
        "role_tension_coverage": 0.0,
        "core_divergence": str(divergence.get("core_divergence") or ""),
        "role_tensions": [],
    }


def _extract_council_chamber(verdict: dict) -> dict:
    votes = _as_list(verdict.get("votes"))
    summary = str(verdict.get("summary") or "").strip()
    default_stance = summary or "No council rationale available."
    benevolence = _as_dict(verdict.get("benevolence_audit"))
    benevolence_state = (
        str(benevolence.get("final_result") or benevolence.get("result") or "").strip() or "unknown"
    )

    role_friction = _extract_role_friction(verdict)
    role_records: dict[str, dict[str, str]] = {}
    fallback_records: list[dict[str, str]] = []
    for vote in votes:
        if not isinstance(vote, dict):
            continue
        perspective = str(vote.get("perspective") or "").strip()
        mapped_role = _map_perspective_to_chamber_role(perspective)
        decision = str(vote.get("decision") or "").strip().lower()
        reasoning = str(vote.get("reasoning") or "").strip() or default_stance
        entry = {
            "stance": reasoning,
            "conflict_point": "",
            "benevolence_check": "",
        }
        default_conflict = decision if decision in {"concern", "object", "block", "refine"} else ""
        if mapped_role:
            entry["conflict_point"] = role_friction.get(mapped_role, default_conflict)
        else:
            entry["conflict_point"] = default_conflict
        if mapped_role and mapped_role not in role_records:
            role_records[mapped_role] = entry
        fallback_records.append(entry)

    fallback_index = 0

    def _next_fallback() -> dict[str, str]:
        nonlocal fallback_index
        if fallback_index < len(fallback_records):
            candidate = fallback_records[fallback_index]
            fallback_index += 1
            return dict(candidate)
        return {
            "stance": default_stance,
            "conflict_point": "",
            "benevolence_check": "",
        }

    chamber: dict[str, dict[str, str]] = {}
    for role in ("philosopher", "engineer", "guardian"):
        chamber[role] = dict(role_records.get(role) or _next_fallback())
        if role in role_friction and not str(chamber[role].get("conflict_point") or "").strip():
            chamber[role]["conflict_point"] = role_friction[role]

    chamber["guardian"]["benevolence_check"] = benevolence_state
    return chamber


def _build_multiplex_from_votes(verdict: dict, chamber: dict) -> dict:
    votes = _as_list(verdict.get("votes"))
    role_weights = {"philosopher": 0.0, "engineer": 0.0, "guardian": 0.0}
    for vote in votes:
        if not isinstance(vote, dict):
            continue
        role = _map_perspective_to_chamber_role(str(vote.get("perspective") or ""))
        if role is None:
            continue
        role_weights[role] = max(
            role_weights[role],
            _clamp01(_coerce_float(vote.get("confidence"), default=0.0)),
        )

    weight_total = sum(role_weights.values())
    if weight_total <= 0:
        role_weights = {"philosopher": 0.34, "engineer": 0.33, "guardian": 0.33}
        weight_total = 1.0
    normalized = {role: value / weight_total for role, value in role_weights.items()}

    primary_role = max(normalized.items(), key=lambda item: item[1])[0]
    primary_weight = normalized[primary_role]
    primary_reasoning = str(_as_dict(chamber.get(primary_role)).get("stance") or "").strip()
    if not primary_reasoning:
        primary_reasoning = (
            str(verdict.get("summary") or "").strip() or "Derived from council confidence."
        )

    shadows = []
    for role in ("philosopher", "engineer", "guardian"):
        if role == primary_role:
            continue
        role_record = _as_dict(chamber.get(role))
        conflict_reason = str(role_record.get("conflict_point") or "").strip()
        if not conflict_reason:
            conflict_reason = f"{role} concerns differ from {primary_role}."
        shadows.append(
            {
                "source": role,
                "weight": round(normalized[role], 3),
                "conflict_reason": conflict_reason,
                "recovery_condition": "Re-evaluate when new evidence or constraints appear.",
                "collapse_cost": f"Loses {role} perspective detail.",
            }
        )

    if primary_weight > 0.7:
        tension_level = "LOW"
    elif primary_weight >= 0.5:
        tension_level = "MEDIUM"
    else:
        tension_level = "HIGH"

    verdict_name = str(verdict.get("verdict") or "").strip().lower()
    if verdict_name == "approve":
        merge_strategy = "COLLAPSE"
    elif verdict_name == "block":
        merge_strategy = "EXPLICIT_CONFLICT"
    else:
        merge_strategy = "PRESERVE_SHADOWS"

    return {
        "primary_path": {
            "source": primary_role,
            "weight": round(primary_weight, 3),
            "reasoning": primary_reasoning,
        },
        "shadows": shadows,
        "tension": {
            "level": tension_level,
            "formula_ref": "tension = 1 - max(role_weight)",
            "weight_distribution": (
                f"{normalized['philosopher']:.2f} / "
                f"{normalized['engineer']:.2f} / "
                f"{normalized['guardian']:.2f}"
            ),
        },
        "merge_strategy": merge_strategy,
        "merge_note": (
            str(verdict.get("summary") or "").strip()
            or "Synthesized from council vote confidence and coherence."
        ),
    }


def _build_next_moves(verdict: dict, intervention_strategy: str) -> list[dict[str, str]]:
    moves: list[dict[str, str]] = []
    seen_texts: set[str] = set()

    def _add_move(label: str, text: str) -> None:
        normalized = text.strip()
        if not normalized:
            return
        if normalized in seen_texts:
            return
        seen_texts.add(normalized)
        moves.append({"label": label, "text": normalized[:220]})

    for hint in _as_list(verdict.get("refinement_hints")):
        if isinstance(hint, str):
            _add_move("Refine", hint)

    structured_output = _as_dict(verdict.get("structured_output"))
    follow_up = _as_dict(structured_output.get("E"))
    for action in _as_list(follow_up.get("actions")):
        if isinstance(action, str):
            _add_move("Action", action)

    if intervention_strategy.strip():
        _add_move("Strategy", intervention_strategy)

    summary = str(verdict.get("summary") or "").strip()
    if not moves and summary:
        _add_move("Focus", summary)

    return moves[:3]


def _build_deliberation_payload(result) -> dict:
    verdict = _as_dict(getattr(result, "council_verdict", {}))
    tonebridge = _as_dict(getattr(result, "tonebridge_analysis", {}))
    tone_analysis = _as_dict(tonebridge.get("tone_analysis"))
    motive_prediction = _as_dict(tonebridge.get("motive_prediction"))
    collapse_risk = _as_dict(tonebridge.get("collapse_risk"))
    resonance_defense = _as_dict(tonebridge.get("resonance_defense"))
    entropy_source = _as_dict(tonebridge.get("entropy_meter"))

    tone_strength = _clamp01(_coerce_float(tone_analysis.get("tone_strength"), default=0.5))
    entropy_value = _clamp01(_coerce_float(entropy_source.get("value"), default=tone_strength))
    if entropy_value >= 0.7:
        entropy_status = "high_tension"
    elif entropy_value >= 0.3:
        entropy_status = "healthy_friction"
    else:
        entropy_status = "echo_chamber"

    entropy_meter = {
        "value": entropy_value,
        "status": str(entropy_source.get("status") or entropy_status),
        "calculation_note": (
            str(entropy_source.get("calculation_note") or "").strip()
            or f"Derived from tone_strength={tone_strength:.2f}"
        ),
    }

    intervention_strategy = str(getattr(result, "intervention_strategy", "") or "").strip()
    semantic_contradictions = _as_list(getattr(result, "semantic_contradictions", []))
    semantic_graph_summary = _as_dict(getattr(result, "semantic_graph_summary", {}))
    visual_chain_snapshot = _load_visual_chain_snapshot()
    contradiction_count = len(semantic_contradictions)
    verdict_name = str(verdict.get("verdict") or "").strip().lower()

    chamber = _extract_council_chamber(verdict)
    multiplex = _build_multiplex_from_votes(verdict, chamber)
    next_moves = _build_next_moves(verdict, intervention_strategy)

    honesty_score = _clamp01(_coerce_float(verdict.get("coherence"), default=0.0))
    responsibility_parts = []
    responsibility_tier = str(verdict.get("responsibility_tier") or "").strip()
    uncertainty_band = str(verdict.get("uncertainty_band") or "").strip()
    if responsibility_tier:
        responsibility_parts.append(f"tier={responsibility_tier}")
    if uncertainty_band:
        responsibility_parts.append(f"uncertainty={uncertainty_band}")
    if not responsibility_parts:
        responsibility_parts.append("responsibility metadata unavailable")

    audit_verdict = "Pass"
    if verdict_name == "block" or contradiction_count > 0:
        audit_verdict = "Review"

    audit_payload = {
        "honesty_score": honesty_score,
        "responsibility_check": "; ".join(responsibility_parts),
        "audit_verdict": audit_verdict,
    }

    benevolence = _as_dict(verdict.get("benevolence_audit"))
    if benevolence:
        benevolence_status = str(
            benevolence.get("final_result") or benevolence.get("result") or ""
        ).strip()
        flags: list[str] = []
        if benevolence_status and benevolence_status.lower() not in {"pass", "allow", "safe"}:
            flags.append(f"benevolence={benevolence_status}")
        audit_payload["code_validation"] = {
            "code_honesty_score": honesty_score,
            "discrepancy": _clamp01(_coerce_float(verdict.get("uncertainty_level"), default=0.0)),
            "flags": flags,
            "is_valid": len(flags) == 0,
        }

    decision_matrix = {
        "user_hidden_intent": (
            str(motive_prediction.get("likely_motive") or "").strip()
            or str(motive_prediction.get("trigger_context") or "").strip()
            or "Unspecified"
        ),
        "ai_strategy_name": (
            intervention_strategy
            or str(resonance_defense.get("suggested_intervention_strategy") or "").strip()
            or "direct_response"
        ),
        "intended_effect": (
            str(verdict.get("summary") or "").strip()
            or str(collapse_risk.get("collapse_risk_level") or "").strip()
            or "Provide grounded guidance"
        ),
        "tone_tag": str(tone_analysis.get("emotion_prediction") or "neutral"),
    }

    response_text = str(getattr(result, "response", "") or "")
    soul_passed = verdict_name != "block" and contradiction_count == 0
    if verdict_name == "block":
        soul_note = "Council blocked output for safety."
    elif contradiction_count > 0:
        soul_note = f"Detected {contradiction_count} semantic contradiction(s)."
    else:
        soul_note = "No semantic contradictions detected."

    return {
        "council_chamber": chamber,
        "entropy_meter": entropy_meter,
        "divergence_quality": _build_divergence_quality_payload(verdict),
        "decision_matrix": decision_matrix,
        "audit": audit_payload,
        "semantic_contradictions": semantic_contradictions,
        "semantic_graph_summary": semantic_graph_summary,
        "visual_chain_snapshot": visual_chain_snapshot,
        "multiplex_conclusion": multiplex,
        "final_synthesis": {"response_text": response_text},
        "next_moves": next_moves,
        "soulAudit": {
            "passed": soul_passed,
            "honestyScore": honesty_score,
            "violations": contradiction_count + (1 if verdict_name == "block" else 0),
            "auditNote": soul_note,
        },
    }


def _resolve_bind_host() -> str:
    host = os.environ.get("TONESOUL_API_HOST")
    if isinstance(host, str) and host.strip():
        return host.strip()
    # Render and similar platforms provide PORT and expect 0.0.0.0 binding.
    if os.environ.get("PORT"):
        return "0.0.0.0"
    return "127.0.0.1"


def _resolve_bind_port() -> int:
    for var_name in ("TONESOUL_API_PORT", "PORT"):
        raw = os.environ.get(var_name)
        if raw is None:
            continue
        text = str(raw).strip()
        if not text:
            continue
        try:
            port = int(text)
        except ValueError:
            print(
                f"[WARN] Invalid {var_name}={raw!r}; expected integer port",
                file=sys.stderr,
            )
            continue
        if 1 <= port <= 65535:
            return port
        print(
            f"[WARN] Out-of-range {var_name}={raw!r}; expected 1..65535",
            file=sys.stderr,
        )
    return 5000


def _prepare_escape_seed_context(context: dict) -> tuple[dict, tuple | None]:
    """Sanitize external escape-valve seed inputs.

    By default we do not trust client-provided seed history to avoid
    forcing high-uncertainty escape behavior. Trusted mode can be enabled
    explicitly via `TONESOUL_ALLOW_ESCAPE_SEED=1`.
    """

    safe_context = dict(context)
    failures = safe_context.get("escape_valve_failures")
    if failures is None:
        return safe_context, None

    if not isinstance(failures, list):
        return safe_context, (jsonify({"error": "Invalid escape_valve_failures"}), 400)

    if _env_flag("TONESOUL_ALLOW_ESCAPE_SEED", default=False):
        if len(failures) > _MAX_ESCAPE_SEED_ITEMS:
            safe_context["escape_valve_failures"] = failures[-_MAX_ESCAPE_SEED_ITEMS:]
        safe_context["escape_valve_seed_trusted"] = True
        return safe_context, None

    # Ignore untrusted external seed attempts.
    safe_context.pop("escape_valve_failures", None)
    safe_context["escape_valve_seed_trusted"] = False
    safe_context["escape_valve_seed_ignored_reason"] = "untrusted_seed"
    return safe_context, None


def _prepare_vtp_context(context: dict) -> tuple[dict, tuple | None]:
    """Sanitize external VTP trigger controls.

    VTP context flags are intended for controlled testing or trusted
    orchestration paths. By default external request payloads cannot force
    VTP trigger/terminate behavior unless `TONESOUL_ALLOW_VTP_CONTEXT=1`.
    """

    safe_context = dict(context)
    provided_flags: list[str] = []
    for key in _VTP_CONTEXT_FLAGS:
        if key not in safe_context:
            continue
        provided_flags.append(key)
        if not isinstance(safe_context.get(key), bool):
            return safe_context, (jsonify({"error": f"Invalid {key}"}), 400)

    if not provided_flags:
        return safe_context, None

    if _env_flag("TONESOUL_ALLOW_VTP_CONTEXT", default=False):
        safe_context["vtp_context_trusted"] = True
        return safe_context, None

    for key in provided_flags:
        safe_context.pop(key, None)
    safe_context["vtp_context_trusted"] = False
    safe_context["vtp_context_ignored_reason"] = "untrusted_vtp_context"
    return safe_context, None


@app.route("/")
def index():
    """Serve the frontend."""
    return app.send_static_file("index.html")


@app.route("/api/validate", methods=["POST"])
def validate():
    """Run PreOutputCouncil on input text."""
    auth_error = _require_write_api_auth()
    if auth_error is not None:
        return auth_error

    rate_limit_error = _apply_rate_limit("validate")
    if rate_limit_error is not None:
        return rate_limit_error

    try:
        data = _json_payload()
        if data is None:
            return jsonify({"error": "Invalid JSON payload"}), 400
        draft_output, error = _require_optional_string(data, "draft_output")
        if error is not None:
            return error
        context, error = _require_optional_dict(data, "context")
        if error is not None:
            return error
        user_intent, error = _require_optional_string(data, "user_intent")
        if error is not None:
            return error

        draft_output = draft_output if draft_output is not None else ""
        context = context if context is not None else {}
        context, error = _prepare_escape_seed_context(context)
        if error is not None:
            return error
        context, error = _prepare_vtp_context(context)
        if error is not None:
            return error

        council_request = CouncilRequest(
            draft_output=draft_output,
            context=context,
            user_intent=user_intent,
        )
        verdict = council_runtime.deliberate(council_request)

        # Convert to dict for JSON response
        result = verdict.to_dict()

        # Transform votes for frontend compatibility
        if "votes" not in result and hasattr(verdict, "transcript") and verdict.transcript:
            result["votes"] = verdict.transcript.get("votes", [])

        return jsonify(result)
    except Exception as exc:
        return _error_response("Failed to compute validation", 500, exc)


@app.route("/api/memories", methods=["GET"])
def get_memories():
    """Get recent memories from self-journal."""
    auth_error = _require_read_api_auth()
    if auth_error is not None:
        return auth_error
    limit = request.args.get("limit", 10, type=int)
    limit = 10 if limit is None or limit <= 0 else min(limit, _MAX_PAGINATION_LIMIT)
    session_id = request.args.get("session_id", type=str)
    session_id = session_id.strip() if isinstance(session_id, str) and session_id.strip() else None
    if supabase_persistence.enabled:
        memories = supabase_persistence.list_memories(limit=limit, session_id=session_id)
    else:
        memories = load_recent_memory(limit=limit)
    payload = {"memories": memories}
    if session_id:
        payload["session_id"] = session_id
    return jsonify(payload)


@app.route("/api/consolidate", methods=["GET"])
def get_consolidation():
    """Run memory consolidation and return report."""
    auth_error = _require_write_api_auth()
    if auth_error is not None:
        return auth_error
    result = consolidate()
    return jsonify(
        {
            "patterns": result.patterns,
            "meta_reflection": result.meta_reflection,
        }
    )


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    try:
        return jsonify(
            {
                "status": "ok",
                "version": "0.6.0",
                "persistence": supabase_persistence.status_dict(),
            }
        )
    except Exception as exc:
        return _error_response("Health check unavailable", 500, exc)


@app.route("/api/governance_status", methods=["GET"])
def governance_status():
    """Operator-facing governance posture endpoint.

    Returns a compact view of the system's current governance health:
    capability level, pipeline mode, evolution brief, and mirror state.
    No authentication required — this is a transparency surface.
    """
    if llm_backend is None:
        get_llm_client()

    capability = "runtime_ready" if llm_backend and llm_backend != "unavailable" else "mock_only"
    reason = None if capability == "runtime_ready" else "llm_backend_unavailable"

    evolution_brief: dict = {}
    try:
        summary = _get_evolution_summary_payload()
        evolution_brief = {
            "total_patterns": summary.get("total_patterns", 0),
            "conversations_analyzed": summary.get("conversations_analyzed", 0),
            "last_distilled_at": summary.get("last_distilled_at"),
        }
    except Exception:
        pass

    recent_verdicts: list = []
    if supabase_persistence.enabled:
        try:
            page = supabase_persistence.list_audit_logs(limit=5, offset=0)
            logs = page.get("logs") if isinstance(page, dict) else []
            for row in logs or []:
                if not isinstance(row, dict):
                    continue
                recent_verdicts.append(
                    {
                        "gate_decision": row.get("gate_decision"),
                        "delta_t": row.get("delta_t"),
                        "created_at": row.get("created_at"),
                    }
                )
        except Exception:
            pass

    payload: dict = {
        "status": "ok",
        "governance_capability": capability,
        "deliberation_level": "runtime" if capability == "runtime_ready" else "mock",
        "llm_backend": llm_backend or "unavailable",
        "llm_mode": _resolve_llm_mode(),
        "mirror_enabled": True,
        "pipeline_mode": "unified_pipeline",
        "persistence_enabled": supabase_persistence.enabled,
        "evolution": evolution_brief,
        "crystal_freshness": _build_crystal_freshness_brief(),
        "recent_verdicts": recent_verdicts,
        "checked_at": _utc_now(),
    }
    if reason is not None:
        payload["reason"] = reason
    return jsonify(payload)


@app.route("/api/status", methods=["GET"])
def status():
    """System status overview."""
    persistence_status = supabase_persistence.status_dict()
    counts = (
        supabase_persistence.get_counts()
        if supabase_persistence.enabled
        else {
            "memory_count": len(load_recent_memory(limit=50)),
            "conversation_count": 0,
            "audit_log_count": 0,
            "message_count": 0,
        }
    )

    if llm_backend is None:
        get_llm_client()
    return jsonify(
        {
            "persistence": persistence_status,
            "llm_backend": llm_backend or "unavailable",
            "llm_mode": _resolve_llm_mode(),
            "llm_error": llm_last_error,
            "memory_count": counts.get("memory_count", 0),
            "conversation_count": counts.get("conversation_count", 0),
            "audit_log_count": counts.get("audit_log_count", 0),
            "message_count": counts.get("message_count", 0),
            "evolution": _get_evolution_summary_payload(),
            "timestamp": _utc_now(),
        }
    )


@app.route("/api/evolution/distill", methods=["POST"])
def evolution_distill():
    """Run one context-distillation pass."""
    auth_error = _require_write_api_auth()
    if auth_error is not None:
        return auth_error

    data = _json_payload() or {}
    raw_limit = data.get("limit", 100)
    if not isinstance(raw_limit, int):
        return jsonify({"error": "Invalid limit"}), 400
    limit = max(1, min(raw_limit, _MAX_PAGINATION_LIMIT * 5))

    try:
        result = _get_context_distiller().distill(limit=limit)
    except Exception as exc:
        return _error_response("Failed to distill context patterns", 500, exc)

    payload = result.to_dict()
    payload["success"] = True
    payload["limit"] = limit
    if supabase_persistence.enabled:
        record_evolution = getattr(supabase_persistence, "record_evolution_result", None)
        if callable(record_evolution):
            record_evolution(
                conversation_id=None,
                result_type="distillation_summary",
                payload=payload,
            )
    return jsonify(payload)


@app.route("/api/evolution/patterns", methods=["GET"])
def evolution_patterns():
    """List distilled context patterns."""
    auth_error = _require_read_api_auth()
    if auth_error is not None:
        return auth_error

    pattern_type = request.args.get("pattern_type", type=str)
    normalized_type = (
        pattern_type.strip().lower()
        if isinstance(pattern_type, str) and pattern_type.strip()
        else None
    )
    distiller = _get_context_distiller()
    patterns = distiller.get_patterns(pattern_type=normalized_type)
    summary = distiller.get_summary()
    return jsonify(
        {
            "patterns": [pattern.to_dict() for pattern in patterns],
            "total": len(patterns),
            "pattern_type": normalized_type,
            "last_distilled_at": summary.get("last_distilled_at"),
        }
    )


@app.route("/api/evolution/summary", methods=["GET"])
def evolution_summary():
    """Get latest self-evolution summary."""
    auth_error = _require_read_api_auth()
    if auth_error is not None:
        return auth_error
    return jsonify(_get_evolution_summary_payload())


@app.route("/api/conversation", methods=["POST"])
def create_conversation():
    """Create a conversation id for a user session."""
    auth_error = _require_write_api_auth()
    if auth_error is not None:
        return auth_error
    data = _json_payload()
    if data is None:
        return jsonify({"error": "Invalid JSON payload"}), 400
    session_id, error = _require_optional_string(data, "session_id")
    if error is not None:
        return error
    conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
    if supabase_persistence.enabled:
        supabase_persistence.ensure_conversation(conversation_id, session_id=session_id)
    return jsonify(
        {
            "success": True,
            "conversation_id": conversation_id,
            "session_id": session_id,
            "created_at": _utc_now(),
        }
    )


@app.route("/api/conversations", methods=["GET"])
def list_conversations():
    """List conversations with pagination."""
    auth_error = _require_read_api_auth()
    if auth_error is not None:
        return auth_error
    limit, offset = _parse_pagination(default_limit=20)
    session_id = request.args.get("session_id", type=str)
    session_id = session_id.strip() if isinstance(session_id, str) and session_id.strip() else None
    if not supabase_persistence.enabled:
        return jsonify(
            {
                "conversations": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "persistence_enabled": False,
            }
        )
    result = supabase_persistence.list_conversations(
        limit=limit,
        offset=offset,
        session_id=session_id,
    )
    result["limit"] = limit
    result["offset"] = offset
    if session_id:
        result["session_id"] = session_id
    result["persistence_enabled"] = True
    return jsonify(result)


@app.route("/api/conversations/<conversation_id>", methods=["GET"])
def get_conversation(conversation_id: str):
    """Get one conversation and all messages by external conversation id."""
    auth_error = _require_read_api_auth()
    if auth_error is not None:
        return auth_error
    if not conversation_id.strip():
        return jsonify({"error": "Invalid conversation_id"}), 400
    if not supabase_persistence.enabled:
        return jsonify({"error": "Persistence not enabled"}), 503
    conversation = supabase_persistence.get_conversation(conversation_id)
    if conversation is None:
        return jsonify({"error": "Conversation not found"}), 404
    return jsonify({"conversation": conversation})


@app.route("/api/conversations/<conversation_id>", methods=["DELETE"])
def delete_conversation(conversation_id: str):
    """Delete one conversation and cascade related rows."""
    auth_error = _require_write_api_auth()
    if auth_error is not None:
        return auth_error
    if not conversation_id.strip():
        return jsonify({"error": "Invalid conversation_id"}), 400
    if not supabase_persistence.enabled:
        return jsonify({"error": "Persistence not enabled"}), 503
    deleted = supabase_persistence.delete_conversation(conversation_id)
    if deleted is None:
        return jsonify({"error": "Conversation not found"}), 404
    return jsonify(
        {
            "success": bool(deleted),
            "conversation_id": conversation_id,
            "deleted": bool(deleted),
            "timestamp": _utc_now(),
        }
    )


@app.route("/api/consent", methods=["POST"])
def create_consent():
    """Record consent metadata for the current session."""
    auth_error = _require_write_api_auth()
    if auth_error is not None:
        return auth_error
    data = _json_payload()
    if data is None:
        return jsonify({"error": "Invalid JSON payload"}), 400
    consent_type, error = _require_optional_string(data, "consent_type")
    if error is not None:
        return error
    session_id, error = _require_optional_string(data, "session_id")
    if error is not None:
        return error
    consent_type = consent_type if consent_type is not None else "standard"
    session_id = session_id if session_id is not None else f"session_{uuid.uuid4().hex[:12]}"
    if supabase_persistence.enabled:
        supabase_persistence.record_consent(session_id=session_id, consent_type=consent_type)
    return jsonify(
        {
            "success": True,
            "session_id": session_id,
            "consent_type": consent_type,
            "consent_version": "1.0",
            "timestamp": _utc_now(),
        }
    )


@app.route("/api/audit-logs", methods=["GET"])
def list_audit_logs():
    """List audit logs with pagination."""
    auth_error = _require_read_api_auth()
    if auth_error is not None:
        return auth_error
    limit, offset = _parse_pagination(default_limit=20)
    conversation_id = request.args.get("conversation_id", type=str)
    conversation_id = conversation_id.strip() if isinstance(conversation_id, str) else None
    session_id = request.args.get("session_id", type=str)
    session_id = session_id.strip() if isinstance(session_id, str) and session_id.strip() else None
    if not supabase_persistence.enabled:
        return jsonify(
            {
                "logs": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "persistence_enabled": False,
            }
        )
    if conversation_id:
        result = supabase_persistence.list_audit_logs(
            limit=limit,
            offset=offset,
            conversation_id=conversation_id,
        )
    else:
        result = supabase_persistence.list_audit_logs(
            limit=limit,
            offset=offset,
            session_id=session_id,
        )
    result["limit"] = limit
    result["offset"] = offset
    if conversation_id:
        result["conversation_id"] = conversation_id
    if session_id:
        result["session_id"] = session_id
    result["persistence_enabled"] = True
    return jsonify(result)


@app.route("/api/consent/<session_id>", methods=["DELETE"])
def withdraw_consent(session_id: str):
    """Withdraw consent and acknowledge deletion workflow."""
    auth_error = _require_write_api_auth()
    if auth_error is not None:
        return auth_error
    if not session_id.strip():
        return jsonify({"error": "Invalid session_id"}), 400
    deletion_report = None
    if supabase_persistence.enabled:
        deletion_report = supabase_persistence.withdraw_consent(session_id)
    return jsonify(
        {
            "success": True,
            "message": "Consent withdrawn and data deleted",
            "session_id": session_id,
            "timestamp": _utc_now(),
            **({"deletion_report": deletion_report} if deletion_report is not None else {}),
        }
    )


@app.route("/api/session-report", methods=["POST"])
def session_report():
    """Generate a session analysis report."""
    auth_error = _require_write_api_auth()
    if auth_error is not None:
        return auth_error
    data = _json_payload()
    if data is None:
        return jsonify({"error": "Invalid JSON payload"}), 400
    if "history" not in data:
        return jsonify({"error": "Missing conversation history"}), 400
    history, error = _require_list(data, "history")
    if error is not None:
        return error
    conversation_id, error = _require_optional_string(data, "conversation_id")
    if error is not None:
        return error
    if not history:
        return jsonify({"error": "Missing conversation history"}), 400
    history_error = _validate_history_entries(history)
    if history_error is not None:
        return history_error

    try:
        # Import concrete reporter module directly to avoid package-level side effects.
        from tonesoul.tonebridge.session_reporter import SessionReporter

        reporter = SessionReporter()
        summary = reporter.analyze(history)
        summary_dict = summary.to_dict()

        if supabase_persistence.enabled:
            supabase_persistence.record_session_report(
                conversation_id=conversation_id,
                report=summary_dict,
            )

        try:
            cleaned = _get_soul_db().cleanup_decayed(MemorySource.SELF_JOURNAL)
            if cleaned > 0:
                print(f"[INFO] Decay cleanup: {cleaned} memories below threshold")
        except Exception as cleanup_error:
            print(f"[WARN] Decay cleanup error: {cleanup_error}")

        try:
            from tonesoul.memory.consolidator import sleep_consolidate

            soul_db = _get_soul_db()
            if soul_db:
                sleep_result = sleep_consolidate(soul_db, source=MemorySource.SELF_JOURNAL)
                if sleep_result.promoted_count > 0:
                    print(
                        f"[INFO] AI Sleep: promoted {sleep_result.promoted_count}, "
                        f"cleared {sleep_result.cleared_count}"
                    )
        except Exception as sleep_error:
            print(f"[WARN] AI Sleep error: {sleep_error}")

        return jsonify({"success": True, "report": summary_dict})
    except Exception as e:
        return _error_response("Failed to generate session report", 500, e)


# ===== LLM Client (Ollama first, Gemini fallback) =====
llm_client = None
llm_backend = None
llm_last_error = None


def _resolve_llm_mode() -> str:
    """Return the configured LLM mode for frontend display."""
    raw = os.environ.get("LLM_BACKEND")
    if not isinstance(raw, str) or not raw.strip():
        return "auto"
    mode = raw.strip().lower()
    if mode == "gemini":
        return "cloud"
    if mode == "ollama":
        return "local"
    return "auto"


def get_llm_client():
    """Lazy-load LLM client based on LLM_BACKEND env var.

    Supported values:
      - 'gemini'  -> Cloud mode, skip Ollama entirely
      - 'ollama'  -> Local mode, skip Gemini entirely
      - 'auto'    -> (default) Try Ollama first, Gemini fallback
    """
    global llm_client, llm_backend, llm_last_error

    if llm_client is not None:
        return llm_client

    llm_mode = (os.environ.get("LLM_BACKEND") or "auto").strip().lower()

    if llm_mode == "gemini":
        try:
            from tonesoul.llm import create_gemini_client

            llm_client = create_gemini_client()
            llm_backend = "Gemini API"
            llm_last_error = None
            print(f"[INFO] LLM backend: {llm_backend} (cloud mode)")
            return llm_client
        except Exception as e:
            llm_last_error = f"gemini={e.__class__.__name__}: {e}"
            print(f"[ERROR] Gemini client error: {e}")
            return None

    if llm_mode == "ollama":
        try:
            from tonesoul.llm import create_ollama_client

            client = create_ollama_client()
            if client.is_available():
                models = client.list_models()
                if models:
                    llm_client = client
                    llm_backend = f"Ollama ({models[0]})"
                    llm_last_error = None
                    print(f"[INFO] LLM backend: {llm_backend} (local mode)")
                    return llm_client
            llm_last_error = "ollama=not available or no models"
            return None
        except Exception as e:
            llm_last_error = f"ollama={e.__class__.__name__}: {e}"
            print(f"[ERROR] Ollama client error: {e}")
            return None

    # Auto mode: Ollama first, Gemini fallback
    ollama_error = None
    try:
        from tonesoul.llm import create_ollama_client

        client = create_ollama_client()
        if client.is_available():
            models = client.list_models()
            if models:
                llm_client = client
                llm_backend = f"Ollama ({models[0]})"
                llm_last_error = None
                print(f"[INFO] LLM backend: {llm_backend} (auto mode)")
                return llm_client
    except Exception as e:
        ollama_error = f"{e.__class__.__name__}: {e}"
        print(f"[WARN] Ollama not available: {e}")

    try:
        from tonesoul.llm import create_gemini_client

        llm_client = create_gemini_client()
        llm_backend = "Gemini API"
        llm_last_error = None
        print(f"[INFO] LLM backend: {llm_backend} (auto mode)")
        return llm_client
    except Exception as e:
        gemini_error = f"{e.__class__.__name__}: {e}"
        llm_last_error = (
            f"ollama={ollama_error}; gemini={gemini_error}"
            if ollama_error
            else f"gemini={gemini_error}"
        )
        print(f"[ERROR] Gemini client error: {e}")
        return None


@app.route("/api/llm/models", methods=["GET"])
def llm_models():
    """List locally available Ollama models."""
    try:
        from tonesoul.llm import create_ollama_client

        client = create_ollama_client()
        if client.is_available():
            models = client.list_models()
            return jsonify({"available": True, "models": models})
        return jsonify({"available": False, "models": [], "reason": "Ollama not running"})
    except Exception as e:
        return jsonify({"available": False, "models": [], "reason": str(e)})


@app.route("/api/llm/switch", methods=["POST"])
def llm_switch():
    """Switch the active LLM backend at runtime."""
    global llm_client, llm_backend, llm_last_error

    auth_error = _require_write_api_auth()
    if auth_error is not None:
        return auth_error

    data = _json_payload()
    if data is None:
        return jsonify({"error": "Invalid JSON payload"}), 400

    mode = data.get("mode", "").strip().lower()
    if mode not in ("gemini", "ollama"):
        return jsonify({"error": "mode must be 'gemini' or 'ollama'"}), 400

    # Reset current client
    llm_client = None
    llm_backend = None
    llm_last_error = None

    if mode == "gemini":
        try:
            from tonesoul.llm import create_gemini_client

            llm_client = create_gemini_client()
            llm_backend = "Gemini API"
            print(f"[INFO] LLM switched to: {llm_backend}")
        except Exception as e:
            llm_last_error = f"gemini={e.__class__.__name__}: {e}"
            return jsonify(
                {
                    "success": False,
                    "error": llm_last_error,
                    "llm_backend": "unavailable",
                    "llm_mode": "cloud",
                }
            )
    else:
        # Ollama with optional model selection
        model = data.get("model", "").strip() or None
        try:
            from tonesoul.llm import create_ollama_client

            client = create_ollama_client(model=model) if model else create_ollama_client()
            if client.is_available():
                models = client.list_models()
                if models:
                    llm_client = client
                    display_model = model or models[0]
                    llm_backend = f"Ollama ({display_model})"
                    print(f"[INFO] LLM switched to: {llm_backend}")
                else:
                    llm_last_error = "No models available in Ollama"
            else:
                llm_last_error = "Ollama service not running"
        except Exception as e:
            llm_last_error = f"ollama={e.__class__.__name__}: {e}"

        if llm_client is None and llm_last_error:
            return jsonify(
                {
                    "success": False,
                    "error": llm_last_error,
                    "llm_backend": "unavailable",
                    "llm_mode": "local",
                }
            )

    return jsonify(
        {
            "success": True,
            "llm_backend": llm_backend or "unavailable",
            "llm_mode": "cloud" if mode == "gemini" else "local",
        }
    )


def _should_skip_live_chat_pipeline_for_tests(pipeline) -> bool:
    """Avoid flaky external LLM calls when Flask test mode uses the real pipeline."""
    if not app.config.get("TESTING"):
        return False
    if _env_flag("TONESOUL_ALLOW_LIVE_CHAT_PIPELINE_TESTS", default=False):
        return False

    pipeline_cls = getattr(pipeline, "__class__", None)
    if pipeline_cls is None:
        return False
    return (
        getattr(pipeline_cls, "__module__", "") == "tonesoul.unified_pipeline"
        and getattr(pipeline_cls, "__name__", "") == "UnifiedPipeline"
    )


@app.route("/api/chat", methods=["POST"])
def chat():
    """Chat endpoint with ToneBridge + Council (Unified Pipeline)."""
    rate_limit_error = _apply_rate_limit("chat")
    if rate_limit_error is not None:
        return rate_limit_error

    auth_error = _require_write_api_auth()
    if auth_error is not None:
        return auth_error

    data = _json_payload()
    if data is None:
        return jsonify({"error": "Invalid JSON payload"}), 400
    message, error = _require_optional_string(data, "message")
    if error is not None:
        return error
    history, error = _require_optional_list(data, "history")
    if error is not None:
        return error
    full_analysis, error = _require_optional_bool(data, "full_analysis")
    if error is not None:
        return error
    execution_profile, error = _require_optional_execution_profile(data, "execution_profile")
    if error is not None:
        return error
    conversation_id, error = _require_optional_string(data, "conversation_id")
    if error is not None:
        return error
    session_id, error = _require_optional_string(data, "session_id")
    if error is not None:
        return error
    council_mode, error = _require_optional_council_mode(data, "council_mode")
    if error is not None:
        return error
    perspective_config, error = _require_optional_dict(data, "perspective_config")
    if error is not None:
        return error
    if perspective_config is not None:
        perspective_config, error = _validate_perspective_config(perspective_config)
        if error is not None:
            return error
    persona_config, error = _require_optional_dict(data, "persona")
    if error is not None:
        return error
    if persona_config is not None:
        persona_config, error = _validate_persona_config(persona_config)
        if error is not None:
            return error
    execution_profile = _resolve_execution_profile(data, execution_profile)
    council_mode = _apply_execution_profile_defaults(
        council_mode,
        perspective_config,
        execution_profile,
    )
    message = message if message is not None else ""
    history = history if history is not None else []
    full_analysis = (
        full_analysis if full_analysis is not None else execution_profile == "engineering"
    )
    history_error = _validate_history_entries(history)
    if history_error is not None:
        return history_error

    try:
        from tonesoul.unified_pipeline import create_unified_pipeline

        prior_tension = _build_prior_tension(conversation_id)
        cache_key = _build_chat_cache_key(
            message=message,
            history=history,
            full_analysis=full_analysis,
            execution_profile=execution_profile,
            council_mode=council_mode,
            perspective_config=perspective_config,
            persona_config=persona_config,
            prior_tension=prior_tension,
        )
        cached_payload = _chat_cache_get(cache_key)
        if cached_payload is not None:
            cached_payload.setdefault("execution_profile", execution_profile)
            cached_payload.setdefault(
                "governance_brief",
                _build_governance_brief(cached_payload),
            )
            cached_payload.setdefault(
                "life_entry_brief",
                _build_life_entry_brief(cached_payload),
            )
            _persist_chat_side_effects(
                conversation_id=conversation_id,
                session_id=session_id,
                user_message=message,
                assistant_message=str(cached_payload.get("response", "")),
                verdict=(
                    cached_payload.get("verdict")
                    if isinstance(cached_payload.get("verdict"), dict)
                    else None
                ),
                evolution_payload=_build_chat_evolution_payload(cached_payload),
            )
            return jsonify(cached_payload)

        pipeline = create_unified_pipeline()
        if _should_skip_live_chat_pipeline_for_tests(pipeline):
            raise RuntimeError(
                "Live UnifiedPipeline disabled in test mode. "
                "Set TONESOUL_ALLOW_LIVE_CHAT_PIPELINE_TESTS=1 to enable."
            )

        result = pipeline.process(
            user_message=message,
            history=history,
            full_analysis=full_analysis,
            council_mode=council_mode,
            perspective_config=perspective_config,
            prior_tension=prior_tension,
            persona_config=persona_config,
        )

        response_payload = {
            "response": result.response,
            "execution_profile": execution_profile,
            "verdict": result.council_verdict,
            "tonebridge": result.tonebridge_analysis,
            "inner_reasoning": result.inner_narrative,
            "intervention_strategy": result.intervention_strategy,
            # ToneStream fields
            "internal_monologue": result.internal_monologue,
            "persona_mode": result.persona_mode,
            "trajectory_analysis": result.trajectory_analysis,
            # Third Axiom fields
            "self_commits": result.self_commits,
            "ruptures": result.ruptures,
            "emergent_values": result.emergent_values,
            "semantic_contradictions": getattr(result, "semantic_contradictions", []),
            "semantic_graph_summary": getattr(result, "semantic_graph_summary", {}),
            "dispatch_trace": getattr(result, "dispatch_trace", {}),
            "deliberation": _build_deliberation_payload(result),
        }
        response_payload["governance_brief"] = _build_governance_brief(response_payload)
        response_payload["life_entry_brief"] = _build_life_entry_brief(response_payload)
        _persist_chat_side_effects(
            conversation_id=conversation_id,
            session_id=session_id,
            user_message=message,
            assistant_message=result.response,
            verdict=result.council_verdict if isinstance(result.council_verdict, dict) else None,
            evolution_payload=_build_chat_evolution_payload(response_payload),
        )
        _chat_cache_set(cache_key, response_payload)

        return jsonify(response_payload)

    except Exception as e:
        return _error_response("Failed to process chat request", 500, e, {"response": None})


def _resolve_debug_mode() -> bool:
    requested = _env_flag("TONESOUL_API_DEBUG", default=False)
    if requested and _is_production_env():
        print("[WARN] TONESOUL_API_DEBUG ignored in production.", file=sys.stderr)
        return False
    return requested


if __name__ == "__main__":
    host = _resolve_bind_host()
    port = _resolve_bind_port()
    debug = _resolve_debug_mode()
    print("=" * 50)
    print("ToneSoul API Server")
    print("=" * 50)
    print(f"Frontend: http://{host}:{port}")
    print(f"API: http://{host}:{port}/api/validate")
    print("=" * 50)
    app.run(host=host, port=port, debug=debug)
