import os
import sys
from http.server import BaseHTTPRequestHandler

# Ensure the local root is in the path so we can import _shared and tonesoul
from pathlib import Path

_api_root = Path(__file__).resolve().parent
if str(_api_root) not in sys.path:
    sys.path.insert(0, str(_api_root))

from _shared.http_utils import read_json_body, send_json_response, send_error_response
from _shared.core import (
    _apply_rate_limit,
    _require_optional_string,
    _require_optional_list,
    _require_optional_bool,
    _require_optional_execution_profile,
    _require_optional_council_mode,
    _require_optional_dict,
    _validate_perspective_config,
    _validate_persona_config,
    _resolve_execution_profile,
    _apply_execution_profile_defaults,
    _validate_history_entries,
    _build_prior_tension,
    _build_chat_cache_key,
    _chat_cache_get,
    _chat_cache_set,
    _persist_chat_side_effects,
    _build_chat_evolution_payload,
    _build_deliberation_payload,
    _should_skip_live_chat_pipeline_for_tests,
    _internal_error_response,
    _require_write_api_auth,
)


class handler(BaseHTTPRequestHandler):
    """
    Vercel Serverless Function entrypoint for POST /api/chat
    """

    def do_OPTIONS(self):
        send_json_response(self, {}, 200)

    def do_POST(self):
        try:
            client_id = str(
                self.client_address[0] if getattr(self, "client_address", None) else "unknown"
            )
            forwarded = self.headers.get("X-Forwarded-For")
            if forwarded:
                client_id = forwarded.split(",")[0].strip()

            auth_error, auth_status = _require_write_api_auth(self.headers)
            if auth_error is not None:
                return send_json_response(self, auth_error, auth_status)

            rate_limit_error = _apply_rate_limit("chat", client_id)
            if rate_limit_error is not None:
                return send_json_response(self, rate_limit_error, 429)

            data = read_json_body(self)
            if data is None:
                return send_error_response(self, "Invalid JSON payload", 400)

            message, error = _require_optional_string(data, "message")
            if error is not None:
                return send_json_response(self, error[0], error[1])

            history, error = _require_optional_list(data, "history")
            if error is not None:
                return send_json_response(self, error[0], error[1])

            full_analysis, error = _require_optional_bool(data, "full_analysis")
            if error is not None:
                return send_json_response(self, error[0], error[1])

            execution_profile, error = _require_optional_execution_profile(
                data, "execution_profile"
            )
            if error is not None:
                return send_json_response(self, error[0], error[1])

            conversation_id, error = _require_optional_string(data, "conversation_id")
            if error is not None:
                return send_json_response(self, error[0], error[1])

            session_id, error = _require_optional_string(data, "session_id")
            if error is not None:
                return send_json_response(self, error[0], error[1])

            council_mode, error = _require_optional_council_mode(data, "council_mode")
            if error is not None:
                return send_json_response(self, error[0], error[1])

            perspective_config, error = _require_optional_dict(data, "perspective_config")
            if error is not None:
                return send_json_response(self, error[0], error[1])
            if perspective_config is not None:
                perspective_config, error = _validate_perspective_config(perspective_config)
                if error is not None:
                    return send_json_response(self, error[0], error[1])

            persona_config, error = _require_optional_dict(data, "persona")
            if error is not None:
                return send_json_response(self, error[0], error[1])
            if persona_config is not None:
                persona_config, error = _validate_persona_config(persona_config)
                if error is not None:
                    return send_json_response(self, error[0], error[1])

            execution_profile = _resolve_execution_profile(data, execution_profile)
            council_mode = _apply_execution_profile_defaults(
                council_mode, perspective_config, execution_profile
            )
            message = message if message is not None else ""
            history = history if history is not None else []
            full_analysis = (
                full_analysis if full_analysis is not None else (execution_profile == "engineering")
            )

            history_error = _validate_history_entries(history)
            if history_error is not None:
                return send_json_response(self, history_error[0], history_error[1])

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
                return send_json_response(self, cached_payload, 200)

            # Deferred import to save cold start ms
            from tonesoul.unified_pipeline import create_unified_pipeline

            pipeline = create_unified_pipeline()

            # Since Vercel runs Serverless, we ignore the local mock-test skip entirely
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
                "internal_monologue": result.internal_monologue,
                "persona_mode": result.persona_mode,
                "trajectory_analysis": result.trajectory_analysis,
                "self_commits": result.self_commits,
                "ruptures": result.ruptures,
                "emergent_values": result.emergent_values,
                "semantic_contradictions": getattr(result, "semantic_contradictions", []),
                "semantic_graph_summary": getattr(result, "semantic_graph_summary", {}),
                "dispatch_trace": getattr(result, "dispatch_trace", {}),
                "deliberation": _build_deliberation_payload(result),
            }

            _persist_chat_side_effects(
                conversation_id=conversation_id,
                session_id=session_id,
                user_message=message,
                assistant_message=result.response,
                verdict=(
                    result.council_verdict if isinstance(result.council_verdict, dict) else None
                ),
                evolution_payload=_build_chat_evolution_payload(response_payload),
            )
            _chat_cache_set(cache_key, response_payload)

            send_json_response(self, response_payload, 200)

        except Exception as e:
            payload, status_code = _internal_error_response(
                "Failed to process chat request",
                exc=e,
                extra={"response": None},
            )
            send_json_response(self, payload, status_code)
