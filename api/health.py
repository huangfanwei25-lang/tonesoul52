from http.server import BaseHTTPRequestHandler
import sys

from pathlib import Path

_api_root = Path(__file__).resolve().parent
if str(_api_root) not in sys.path:
    sys.path.insert(0, str(_api_root))

from _shared.http_utils import send_json_response
from _shared.core import _internal_error_response, supabase_persistence


class handler(BaseHTTPRequestHandler):
    """
    Vercel Serverless Function entrypoint for GET /api/health
    """

    def do_OPTIONS(self):
        send_json_response(self, {}, 200)

    def do_GET(self):
        try:
            status_data = {
                "status": "ok",
                "version": "1.0.0-vercel",
                "persistence": supabase_persistence.status_dict(),
            }
            send_json_response(self, status_data, 200)
        except Exception as e:
            payload, status_code = _internal_error_response(
                "Health check unavailable",
                exc=e,
            )
            send_json_response(self, payload, status_code)
