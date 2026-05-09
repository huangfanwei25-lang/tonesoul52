import json
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlsplit

_ALLOWED_CORS_HEADERS = "Content-Type, Authorization, X-ToneSoul-Read-Token, X-ToneSoul-Write-Token"
_DEFAULT_CORS_ORIGINS = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
)


def _normalize_origin(value: str | None) -> str:
    if not isinstance(value, str):
        return ""
    parsed = urlsplit(value.strip())
    if not parsed.scheme or not parsed.netloc:
        return ""
    return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}"


def _configured_cors_origins() -> tuple[str, ...]:
    raw = os.environ.get("TONESOUL_CORS_ORIGINS")
    if raw is None:
        return _DEFAULT_CORS_ORIGINS
    origins = []
    for part in raw.split(","):
        value = part.strip()
        if value == "*":
            origins.append("*")
            continue
        origins.append(_normalize_origin(value))
    return tuple(origin for origin in origins if origin)


def _request_origin(request_handler: BaseHTTPRequestHandler) -> str:
    return _normalize_origin(request_handler.headers.get("Origin"))


def _request_host_origin(request_handler: BaseHTTPRequestHandler) -> str:
    host = (
        request_handler.headers.get("Host") or request_handler.headers.get("X-Forwarded-Host") or ""
    ).strip()
    if not host:
        return ""
    host = host.split(",", 1)[0].strip()

    forwarded_proto = (
        request_handler.headers.get("X-Forwarded-Proto")
        or request_handler.headers.get("X-Forwarded-Protocol")
        or ""
    ).strip()
    scheme = forwarded_proto.split(",", 1)[0].strip().lower()
    if scheme not in {"http", "https"}:
        scheme = "http" if host.startswith(("localhost", "127.0.0.1")) else "https"
    return _normalize_origin(f"{scheme}://{host}")


def _resolve_cors_allow_origin(request_handler: BaseHTTPRequestHandler) -> str:
    origin = _request_origin(request_handler)
    if not origin:
        return ""
    allowed_origins = _configured_cors_origins()
    if "*" in allowed_origins:
        return "*"
    if origin in allowed_origins or origin == _request_host_origin(request_handler):
        return origin
    return ""


def read_json_body(request_handler: BaseHTTPRequestHandler) -> dict | None:
    try:
        content_length = int(request_handler.headers.get("Content-Length", 0))
        if content_length > 0:
            post_data = request_handler.rfile.read(content_length)
            payload = json.loads(post_data.decode("utf-8"))
            if isinstance(payload, dict):
                return payload
    except Exception:
        pass
    return None


def send_json_response(
    request_handler: BaseHTTPRequestHandler,
    payload: dict,
    status_code: int = 200,
    extra_headers: dict = None,
):
    request_handler.send_response(status_code)
    request_handler.send_header("Content-Type", "application/json")
    allow_origin = _resolve_cors_allow_origin(request_handler)
    if allow_origin:
        request_handler.send_header("Access-Control-Allow-Origin", allow_origin)
        request_handler.send_header("Vary", "Origin")
    request_handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, DELETE")
    request_handler.send_header("Access-Control-Allow-Headers", _ALLOWED_CORS_HEADERS)

    if extra_headers:
        for k, v in extra_headers.items():
            request_handler.send_header(k, str(v))

    request_handler.end_headers()
    request_handler.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))


def send_error_response(
    request_handler: BaseHTTPRequestHandler, message: str, status_code: int = 400
):
    send_json_response(request_handler, {"error": message}, status_code)
