import json
from http.server import BaseHTTPRequestHandler

_ALLOWED_CORS_HEADERS = "Content-Type, Authorization, X-ToneSoul-Read-Token, X-ToneSoul-Write-Token"


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
    # Vercel Serverless CORS handled by next.config.js or vercel.json usually,
    # but we can add basic ones here just in case since this is a separate project.
    request_handler.send_header("Access-Control-Allow-Origin", "*")
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
