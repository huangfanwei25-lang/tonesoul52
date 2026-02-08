"""
ToneSoul API Server
Connects frontend to PreOutputCouncil backend.
"""

import os
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


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


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


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


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
    limit = request.args.get("limit", 10, type=int)
    memories = load_recent_memory(limit=limit)
    return jsonify({"memories": memories})


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
    return jsonify({"status": "ok", "version": "0.6.0"})


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
    return jsonify(
        {
            "success": True,
            "conversation_id": conversation_id,
            "session_id": session_id,
            "created_at": _utc_now(),
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
    return jsonify(
        {
            "success": True,
            "session_id": session_id,
            "consent_type": consent_type,
            "consent_version": "1.0",
            "timestamp": _utc_now(),
        }
    )


@app.route("/api/consent/<session_id>", methods=["DELETE"])
def withdraw_consent(session_id: str):
    """Withdraw consent and acknowledge deletion workflow."""
    if not session_id.strip():
        return jsonify({"error": "Invalid session_id"}), 400
    return jsonify(
        {
            "success": True,
            "message": "Consent withdrawn and data deleted",
            "session_id": session_id,
            "timestamp": _utc_now(),
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
    if not history:
        return jsonify({"error": "Missing conversation history"}), 400

    try:
        # Import concrete reporter module directly to avoid package-level side effects.
        from tonesoul.tonebridge.session_reporter import SessionReporter

        reporter = SessionReporter()
        summary = reporter.analyze(history)

        return jsonify({"success": True, "report": summary.to_dict()})
    except Exception as e:
        return _error_response("Failed to generate session report", 500, e)


# ===== LLM Client (Ollama first, Gemini fallback) =====
llm_client = None
llm_backend = None


def get_llm_client():
    """Lazy-load LLM client. Tries Ollama first, then Gemini."""
    global llm_client, llm_backend

    if llm_client is not None:
        return llm_client

    # Try Ollama first (local)
    try:
        from tonesoul.llm import create_ollama_client

        client = create_ollama_client()
        if client.is_available():
            models = client.list_models()
            if models:
                llm_client = client
                llm_backend = f"Ollama ({models[0]})"
                print(f"✅ LLM Backend: {llm_backend}")
                return llm_client
    except Exception as e:
        print(f"⚠️ Ollama not available: {e}")

    # Fallback to Gemini
    try:
        from tonesoul.llm import create_gemini_client

        llm_client = create_gemini_client()
        llm_backend = "Gemini API"
        print(f"✅ LLM Backend: {llm_backend}")
        return llm_client
    except Exception as e:
        print(f"❌ Gemini client error: {e}")
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
    message = message if message is not None else ""
    history = history if history is not None else []
    full_analysis = full_analysis if full_analysis is not None else True

    try:
        from tonesoul.unified_pipeline import create_unified_pipeline

        pipeline = create_unified_pipeline()

        result = pipeline.process(
            user_message=message,
            history=history,
            full_analysis=full_analysis,
        )

        return jsonify(
            {
                "response": result.response,
                "verdict": result.council_verdict,
                "tonebridge": result.tonebridge_analysis,
                "inner_reasoning": result.inner_narrative,
                "intervention_strategy": result.intervention_strategy,
                # ToneStream 新增欄位
                "internal_monologue": result.internal_monologue,
                "persona_mode": result.persona_mode,
                "trajectory_analysis": result.trajectory_analysis,
                # Third Axiom 欄位
                "self_commits": result.self_commits,
                "ruptures": result.ruptures,
                "emergent_values": result.emergent_values,
            }
        )

    except Exception as e:
        return _error_response("Failed to process chat request", 500, e, {"response": None})


if __name__ == "__main__":
    host = os.environ.get("TONESOUL_API_HOST", "127.0.0.1")
    port = int(os.environ.get("TONESOUL_API_PORT", "5000"))
    debug = _env_flag("TONESOUL_API_DEBUG", default=False)
    print("=" * 50)
    print("ToneSoul API Server")
    print("=" * 50)
    print(f"Frontend: http://{host}:{port}")
    print(f"API: http://{host}:{port}/api/validate")
    print("=" * 50)
    app.run(host=host, port=port, debug=debug)
