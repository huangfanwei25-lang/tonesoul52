import sys
from http.server import BaseHTTPRequestHandler

# Ensure the local root is in the path
from pathlib import Path

_api_root = Path(__file__).resolve().parent
if str(_api_root) not in sys.path:
    sys.path.insert(0, str(_api_root))

from _shared.http_utils import read_json_body, send_json_response, send_error_response
from _shared.core import (
    _apply_rate_limit,
    _require_optional_string,
    _require_optional_dict,
    _internal_error_response,
    _prepare_escape_seed_context,
    _prepare_vtp_context,
    _require_write_api_auth,
    council_runtime,
)
from tonesoul.council import CouncilRequest


class handler(BaseHTTPRequestHandler):
    """
    Vercel Serverless Function entrypoint for POST /api/validate
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

            rate_limit_error = _apply_rate_limit("validate", client_id)
            if rate_limit_error is not None:
                return send_json_response(self, rate_limit_error, 429)

            data = read_json_body(self)
            if data is None:
                return send_error_response(self, "Invalid JSON payload", 400)

            draft_output, error = _require_optional_string(data, "draft_output")
            if error is not None:
                return send_json_response(self, error[0], error[1])

            context, error = _require_optional_dict(data, "context")
            if error is not None:
                return send_json_response(self, error[0], error[1])

            user_intent, error = _require_optional_string(data, "user_intent")
            if error is not None:
                return send_json_response(self, error[0], error[1])

            draft_output = draft_output if draft_output is not None else ""
            context = context if context is not None else {}

            context, error = _prepare_escape_seed_context(context)
            if error is not None:
                return send_json_response(self, error[0], error[1])

            context, error = _prepare_vtp_context(context)
            if error is not None:
                return send_json_response(self, error[0], error[1])

            council_request = CouncilRequest(
                draft_output=draft_output,
                context=context,
                user_intent=user_intent,
            )
            verdict = council_runtime.deliberate(council_request)

            result = verdict.to_dict()
            if "votes" not in result and hasattr(verdict, "transcript") and verdict.transcript:
                result["votes"] = verdict.transcript.get("votes", [])

            send_json_response(self, result, 200)

        except Exception as e:
            payload, status_code = _internal_error_response(
                "Failed to compute validation",
                exc=e,
            )
            send_json_response(self, payload, status_code)
