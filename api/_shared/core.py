"""
ToneSoul Shared Core for Vercel Serverless
Contains shared state, helper functions, and database configurations.
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

# Enable relative paths to find the tonesoul package in the monorepo root
_api_root = Path(__file__).resolve().parents[2]
if str(_api_root) not in sys.path:
    sys.path.insert(0, str(_api_root))

from tonesoul.council import CouncilRuntime
from tonesoul.evolution import ContextDistiller
from tonesoul.memory.soul_db import JsonlSoulDB, SoulDB
from tonesoul.supabase_persistence import SupabasePersistence


# Provide a mock Flask app interface to make migration easier, since we are not using Flask in Vercel.
# Some legacy code might expect `app.config.get("TESTING")`.
class DummyAppConfig(dict):
    pass


# ---------------------------------------------------------
# Payload Extraction Helpers for Vercel Serverless Formats
# ---------------------------------------------------------


def _require_optional_string(data: dict, key: str) -> tuple[str | None, tuple | None]:
    value = data.get(key)
    if value is None:
        return None, None
    if isinstance(value, str):
        return value, None
    return None, ({"error": f"Invalid {key}"}, 400)


def _require_optional_bool(data: dict, key: str) -> tuple[bool | None, tuple | None]:
    value = data.get(key)
    if value is None:
        return None, None
    if isinstance(value, bool):
        return value, None
    return None, ({"error": f"Invalid {key}"}, 400)


def _require_optional_dict(data: dict, key: str) -> tuple[dict | None, tuple | None]:
    value = data.get(key)
    if value is None:
        return None, None
    if isinstance(value, dict):
        return value, None
    return None, ({"error": f"Invalid {key}"}, 400)


def _require_list(data: dict, key: str) -> tuple[list | None, tuple | None]:
    value = data.get(key)
    if isinstance(value, list):
        return value, None
    return None, ({"error": f"Invalid {key}"}, 400)


def _require_optional_list(data: dict, key: str) -> tuple[list | None, tuple | None]:
    value = data.get(key)
    if value is None:
        return None, None
    if isinstance(value, list):
        return value, None
    return None, ({"error": f"Invalid {key}"}, 400)


def _validate_perspective_config(config: dict) -> tuple[dict | None, tuple | None]:
    for perspective_name, perspective_options in config.items():
        if not isinstance(perspective_name, str) or not perspective_name.strip():
            return None, ({"error": "Invalid perspective_config"}, 400)
        if not isinstance(perspective_options, dict):
            return None, ({"error": "Invalid perspective_config"}, 400)
    return config, None


def _validate_persona_config(config: dict) -> tuple[dict | None, tuple | None]:
    scalar_keys = ("name", "style", "risk_sensitivity", "response_length")
    for key in scalar_keys:
        value = config.get(key)
        if value is not None and not isinstance(value, str):
            return None, ({"error": "Invalid persona"}, 400)

    weights = config.get("weights")
    if weights is not None:
        if not isinstance(weights, dict):
            return None, ({"error": "Invalid persona"}, 400)
        for key in ("meaning", "practical", "safety"):
            value = weights.get(key)
            if value is not None and not isinstance(value, (int, float)):
                return None, ({"error": "Invalid persona"}, 400)

    custom_roles = config.get("custom_roles")
    if custom_roles is not None:
        if not isinstance(custom_roles, list) or len(custom_roles) > 8:
            return None, ({"error": "Invalid persona"}, 400)
        for role in custom_roles:
            if not isinstance(role, dict):
                return None, ({"error": "Invalid persona"}, 400)
            for key in ("id", "name", "description", "prompt_hint"):
                value = role.get(key)
                if value is not None and not isinstance(value, str):
                    return None, ({"error": "Invalid persona"}, 400)

            attachments = role.get("attachments")
            if attachments is not None:
                if not isinstance(attachments, list) or len(attachments) > 6:
                    return None, ({"error": "Invalid persona"}, 400)
                for attachment in attachments:
                    if not isinstance(attachment, dict):
                        return None, ({"error": "Invalid persona"}, 400)
                    for key in ("id", "label", "path", "note"):
                        value = attachment.get(key)
                        if value is not None and not isinstance(value, str):
                            return None, ({"error": "Invalid persona"}, 400)

    return config, None


_ALLOWED_HISTORY_ROLES = {"user", "assistant", "system"}
_MAX_HISTORY_ITEMS = 500


def _validate_history_entries(history: list, *, field_name: str = "history") -> tuple | None:
    if len(history) > _MAX_HISTORY_ITEMS:
        return ({"error": f"{field_name} too long"}, 400)

    for item in history:
        if not isinstance(item, dict):
            return ({"error": f"Invalid {field_name} item"}, 400)

        role = item.get("role")
        content = item.get("content")
        if not isinstance(role, str) or role.strip().lower() not in _ALLOWED_HISTORY_ROLES:
            return ({"error": f"Invalid {field_name} item"}, 400)
        if not isinstance(content, str) or not content.strip():
            return ({"error": f"Invalid {field_name} item"}, 400)
    return None


_ALLOWED_COUNCIL_MODES = {"rules", "rules_only", "hybrid", "full_llm"}


def _require_optional_council_mode(data: dict, key: str) -> tuple[str | None, tuple | None]:
    value = data.get(key)
    if value is None:
        return None, None
    if not isinstance(value, str):
        return None, ({"error": f"Invalid {key}"}, 400)
    mode = value.strip().lower()
    if mode not in _ALLOWED_COUNCIL_MODES:
        return None, ({"error": f"Invalid {key}"}, 400)
    if mode == "rules_only":
        mode = "rules"
    return mode, None


_ALLOWED_EXECUTION_PROFILES = {"interactive", "engineering"}


def _require_optional_execution_profile(data: dict, key: str) -> tuple[str | None, tuple | None]:
    value = data.get(key)
    if value is None:
        return None, None
    if not isinstance(value, str):
        return None, ({"error": f"Invalid {key}"}, 400)
    profile = value.strip().lower()
    if profile not in _ALLOWED_EXECUTION_PROFILES:
        return None, ({"error": f"Invalid {key}"}, 400)
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


def _build_deliberation_payload(result) -> dict:
    from tonesoul.utils.payload_helpers import _as_dict, _coerce_float, _clamp01

    verdict = _as_dict(getattr(result, "council_verdict", {}))
    tonebridge = _as_dict(getattr(result, "tonebridge_analysis", {}))
    tone_analysis = _as_dict(tonebridge.get("tone_analysis"))
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
    }

    return {"entropy_meter": entropy_meter}


class DummyApp:
    config = DummyAppConfig()


app = DummyApp()

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
_ALLOWED_HISTORY_ROLES = {"user", "assistant", "system"}

supabase_persistence = SupabasePersistence.from_env()
_context_distiller: ContextDistiller | None = None
_soul_db: SoulDB | None = None

_rate_limit_lock = Lock()
_rate_limit_state: dict[tuple[str, str], list[float]] = {}
_chat_cache_lock = Lock()
_chat_cache_state: dict[str, tuple[float, dict]] = {}


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


def _rate_limit_for_endpoint(endpoint_name: str) -> int:
    if endpoint_name == "chat":
        return _read_positive_int_env(_RATE_LIMIT_CHAT_ENV, default=60)
    if endpoint_name == "validate":
        return _read_positive_int_env(_RATE_LIMIT_VALIDATE_ENV, default=120)
    return _read_positive_int_env(_RATE_LIMIT_VALIDATE_ENV, default=120)


def _rate_limit_window_seconds() -> int:
    return _read_positive_int_env(_RATE_LIMIT_WINDOW_SECONDS_ENV, default=60)


def _apply_rate_limit(endpoint_name: str, client_id: str):
    if not _is_rate_limit_enabled():
        return None
    limit = _rate_limit_for_endpoint(endpoint_name)
    window = _rate_limit_window_seconds()
    now = datetime.now(timezone.utc).timestamp()
    bucket_key = (endpoint_name, client_id)

    with _rate_limit_lock:
        history = _rate_limit_state.get(bucket_key, [])
        threshold = now - float(window)
        history = [ts for ts in history if ts >= threshold]
        if len(history) >= limit:
            retry_after = max(1, int(history[0] + float(window) - now))
            _rate_limit_state[bucket_key] = history
            return {
                "error": "Too Many Requests",
                "endpoint": endpoint_name,
                "retry_after_seconds": retry_after,
            }
        history.append(now)
        _rate_limit_state[bucket_key] = history
    return None


def _is_chat_cache_enabled() -> bool:
    if _CHAT_CACHE_ENABLED_ENV in os.environ:
        return _env_flag(_CHAT_CACHE_ENABLED_ENV, default=False)
    return True


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
        canonical_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
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


def _extract_named_token(headers: dict, *header_names: str) -> str:
    for header_name in header_names:
        value = headers.get(header_name, headers.get(header_name.lower()))
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _require_api_auth(
    headers: dict,
    *,
    required_token: str,
    config_error: str,
    unauthorized_error: str,
    header_names: tuple[str, ...],
):
    fail_closed = _env_flag(_AUTH_FAIL_CLOSED_ENV, default=_is_production_env())
    if not required_token:
        if fail_closed:
            return {"error": config_error}, 503
        return None, 200

    provided_token = _extract_bearer_token(
        headers.get("Authorization", headers.get("authorization"))
    )
    if not provided_token:
        provided_token = _extract_named_token(headers, *header_names)

    if not provided_token or not secrets.compare_digest(provided_token, required_token):
        return {"error": unauthorized_error}, 401
    return None, 200


def _require_read_api_auth(headers: dict):
    return _require_api_auth(
        headers,
        required_token=_read_api_token(),
        config_error="Read API token not configured",
        unauthorized_error="Unauthorized read access",
        header_names=("X-ToneSoul-Read-Token",),
    )


def _require_write_api_auth(headers: dict):
    return _require_api_auth(
        headers,
        required_token=_read_write_api_token(),
        config_error="Write API token not configured",
        unauthorized_error="Unauthorized write access",
        header_names=("X-ToneSoul-Write-Token", "X-ToneSoul-Read-Token"),
    )


def _internal_error_response(
    message: str,
    *,
    exc: Exception | None = None,
    extra: dict | None = None,
    status_code: int = 500,
) -> tuple[dict, int]:
    error_id = uuid.uuid4().hex[:12]
    if exc is not None:
        traceback.print_exc()
        print(f"[ERROR] id={error_id}: {exc}", file=sys.stderr)
    payload = {"error": message, "error_id": error_id}
    if extra:
        payload.update(extra)
    return payload, status_code


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


def _build_chat_evolution_payload(response_payload: dict) -> dict:
    def _as_dict(value):
        return value if isinstance(value, dict) else {}

    def _as_list(value):
        return value if isinstance(value, list) else []

    deliberation = _as_dict(response_payload.get("deliberation"))
    return {
        "semantic_contradictions": _as_list(response_payload.get("semantic_contradictions")),
        "semantic_graph_summary": _as_dict(response_payload.get("semantic_graph_summary")),
        "dispatch_trace": _as_dict(response_payload.get("dispatch_trace")),
        "visual_chain_snapshot": _as_dict(deliberation.get("visual_chain_snapshot")),
        "captured_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def _should_skip_live_chat_pipeline_for_tests(pipeline) -> bool:
    return False
