"""
ToneSoul API Server
Connects frontend to PreOutputCouncil backend.
"""

import os
import secrets
import sys
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from flask import Flask, jsonify, request
from flask_cors import CORS

from tonesoul.council import CouncilRequest, CouncilRuntime
from tonesoul.council.self_journal import load_recent_memory
from tonesoul.memory import consolidate
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
_VTP_CONTEXT_FLAGS = (
    "vtp_force_trigger",
    "vtp_axiom_conflict",
    "vtp_refusal_to_compromise",
    "vtp_user_confirmed",
)
_ALLOWED_COUNCIL_MODES = {"rules", "rules_only", "hybrid", "full_llm"}
supabase_persistence = SupabasePersistence.from_env()


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


def _require_read_api_auth():
    required_token = _read_api_token()
    if not required_token:
        return None

    provided_token = _extract_bearer_token(request.headers.get("Authorization"))
    if not provided_token:
        provided_token = str(request.headers.get("X-ToneSoul-Read-Token") or "").strip()

    if not provided_token or not secrets.compare_digest(provided_token, required_token):
        return jsonify({"error": "Unauthorized read access"}), 401
    return None


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


def _validate_perspective_config(config: dict) -> tuple[dict | None, tuple | None]:
    for perspective_name, perspective_options in config.items():
        if not isinstance(perspective_name, str) or not perspective_name.strip():
            return None, (jsonify({"error": "Invalid perspective_config"}), 400)
        if not isinstance(perspective_options, dict):
            return None, (jsonify({"error": "Invalid perspective_config"}), 400)
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


@app.route("/chat")
def chat_page():
    """Serve the chat frontend."""
    return app.send_static_file("chat.html")


@app.route("/api/validate", methods=["POST"])
def validate():
    """Run PreOutputCouncil on input text."""
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
    return jsonify(
        {
            "status": "ok",
            "version": "0.6.0",
            "persistence": supabase_persistence.status_dict(),
        }
    )


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
            "llm_error": llm_last_error,
            "memory_count": counts.get("memory_count", 0),
            "conversation_count": counts.get("conversation_count", 0),
            "audit_log_count": counts.get("audit_log_count", 0),
            "message_count": counts.get("message_count", 0),
            "timestamp": _utc_now(),
        }
    )


@app.route("/api/conversation", methods=["POST"])
def create_conversation():
    """Create a conversation id for a user session."""
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
    auth_error = _require_read_api_auth()
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
    session_id = session_id.strip() if isinstance(session_id, str) else None
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

        return jsonify({"success": True, "report": summary_dict})
    except Exception as e:
        return _error_response("Failed to generate session report", 500, e)


# ===== LLM Client (Ollama first, Gemini fallback) =====
llm_client = None
llm_backend = None
llm_last_error = None


def get_llm_client():
    """Lazy-load LLM client. Tries Ollama first, then Gemini."""
    global llm_client, llm_backend, llm_last_error

    if llm_client is not None:
        return llm_client

    ollama_error = None

    # Try Ollama first (local)
    try:
        from tonesoul.llm import create_ollama_client

        client = create_ollama_client()
        if client.is_available():
            models = client.list_models()
            if models:
                llm_client = client
                llm_backend = f"Ollama ({models[0]})"
                llm_last_error = None
                print(f"[INFO] LLM backend: {llm_backend}")
                return llm_client
    except Exception as e:
        ollama_error = f"{e.__class__.__name__}: {e}"
        print(f"[WARN] Ollama not available: {e}")

    # Fallback to Gemini
    try:
        from tonesoul.llm import create_gemini_client

        llm_client = create_gemini_client()
        llm_backend = "Gemini API"
        llm_last_error = None
        print(f"[INFO] LLM backend: {llm_backend}")
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


@app.route("/api/chat", methods=["POST"])
def chat():
    """Chat endpoint with ToneBridge + Council (Unified Pipeline)."""
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
    message = message if message is not None else ""
    history = history if history is not None else []
    full_analysis = full_analysis if full_analysis is not None else True

    try:
        from tonesoul.unified_pipeline import create_unified_pipeline

        pipeline = create_unified_pipeline()
        prior_tension = _build_prior_tension(conversation_id)

        result = pipeline.process(
            user_message=message,
            history=history,
            full_analysis=full_analysis,
            council_mode=council_mode,
            perspective_config=perspective_config,
            prior_tension=prior_tension,
        )

        if supabase_persistence.enabled and conversation_id:
            supabase_persistence.record_chat_exchange(
                conversation_id=conversation_id,
                user_message=message,
                assistant_message=result.response,
                deliberation=(
                    result.council_verdict if isinstance(result.council_verdict, dict) else None
                ),
                session_id=session_id,
            )
            if isinstance(result.council_verdict, dict):
                supabase_persistence.record_chat_audit(
                    conversation_id=conversation_id,
                    verdict=result.council_verdict,
                )

        return jsonify(
            {
                "response": result.response,
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
            }
        )

    except Exception as e:
        return _error_response("Failed to process chat request", 500, e, {"response": None})


if __name__ == "__main__":
    host = _resolve_bind_host()
    port = _resolve_bind_port()
    debug = _env_flag("TONESOUL_API_DEBUG", default=False)
    print("=" * 50)
    print("ToneSoul API Server")
    print("=" * 50)
    print(f"Frontend: http://{host}:{port}")
    print(f"API: http://{host}:{port}/api/validate")
    print("=" * 50)
    app.run(host=host, port=port, debug=debug)
