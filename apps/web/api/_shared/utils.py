import os
import sys
from pathlib import Path

# Add repo root to sys.path so we can import tonesoul
# Vercel deployment structure might vary, so we try multiple paths.
_possible_roots = [
    Path(__file__).resolve().parents[4],  # Local: apps/web/api/_shared/utils.py -> repo root
    Path(__file__).resolve().parents[3],
    Path(os.environ.get("VERCEL_PROJECT_ROOT", "/var/task")),
    Path("/var/task"),
]

for _root in _possible_roots:
    if (_root / "tonesoul").is_dir():
        if str(_root) not in sys.path:
            sys.path.insert(0, str(_root))
        break

import json
from http.server import BaseHTTPRequestHandler

def send_json(handler: BaseHTTPRequestHandler, data: dict, status: int = 200, headers: dict = None):
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    
    # CORS headers
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, DELETE")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-ToneSoul-Read-Token")
    
    if headers:
        for k, v in headers.items():
            handler.send_header(k, v)
    handler.end_headers()
    handler.wfile.write(json.dumps(data).encode("utf-8"))

def send_error(handler: BaseHTTPRequestHandler, message: str, status: int = 400):
    send_json(handler, {"error": message}, status)

def parse_json_body(handler: BaseHTTPRequestHandler) -> dict:
    try:
        content_length = int(handler.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        post_data = handler.rfile.read(content_length)
        return json.loads(post_data.decode("utf-8"))
    except Exception:
        return {}

def env_flag(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

def is_production_env() -> bool:
    if env_flag("TONESOUL_PRODUCTION", default=False):
        return True
    return os.environ.get("VERCEL_ENV") == "production"
