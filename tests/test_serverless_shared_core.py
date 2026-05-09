from __future__ import annotations

import io
import json
import re

from api._shared import core as shared_core
from api._shared.http_utils import read_json_body, send_json_response


class _FakeHandler:
    def __init__(self, *, body: bytes = b"", headers: dict | None = None) -> None:
        self.headers = headers or {}
        self.rfile = io.BytesIO(body)
        self.wfile = io.BytesIO()
        self.status_code: int | None = None
        self.sent_headers: dict[str, str] = {}

    def send_response(self, status_code: int) -> None:
        self.status_code = status_code

    def send_header(self, key: str, value: str) -> None:
        self.sent_headers[key] = value

    def end_headers(self) -> None:
        return None


def test_read_json_body_rejects_array_payload() -> None:
    body = b'[{"draft_output": "x"}]'
    handler = _FakeHandler(
        body=body,
        headers={"Content-Length": str(len(body))},
    )

    assert read_json_body(handler) is None


def test_send_json_response_allows_write_token_cors_header() -> None:
    handler = _FakeHandler()

    send_json_response(handler, {"ok": True}, 200)

    assert handler.status_code == 200
    allowed_headers = handler.sent_headers["Access-Control-Allow-Headers"]
    assert "X-ToneSoul-Write-Token" in allowed_headers


def test_send_json_response_reflects_same_origin(monkeypatch) -> None:
    monkeypatch.delenv("TONESOUL_CORS_ORIGINS", raising=False)
    handler = _FakeHandler(
        headers={
            "Origin": "https://tonesoul52.vercel.app",
            "Host": "tonesoul52.vercel.app",
            "X-Forwarded-Proto": "https",
        }
    )

    send_json_response(handler, {"ok": True}, 200)

    assert handler.sent_headers["Access-Control-Allow-Origin"] == "https://tonesoul52.vercel.app"
    assert handler.sent_headers["Vary"] == "Origin"


def test_send_json_response_blocks_untrusted_cross_origin(monkeypatch) -> None:
    monkeypatch.delenv("TONESOUL_CORS_ORIGINS", raising=False)
    handler = _FakeHandler(
        headers={
            "Origin": "https://evil.example",
            "Host": "tonesoul52.vercel.app",
            "X-Forwarded-Proto": "https",
        }
    )

    send_json_response(handler, {"ok": True}, 200)

    assert "Access-Control-Allow-Origin" not in handler.sent_headers


def test_send_json_response_does_not_trust_forwarded_host_over_host(monkeypatch) -> None:
    monkeypatch.delenv("TONESOUL_CORS_ORIGINS", raising=False)
    handler = _FakeHandler(
        headers={
            "Origin": "https://evil.example",
            "Host": "tonesoul52.vercel.app",
            "X-Forwarded-Host": "evil.example",
            "X-Forwarded-Proto": "https",
        }
    )

    send_json_response(handler, {"ok": True}, 200)

    assert "Access-Control-Allow-Origin" not in handler.sent_headers


def test_send_json_response_allows_configured_origin(monkeypatch) -> None:
    monkeypatch.setenv("TONESOUL_CORS_ORIGINS", "https://app.example.com")
    handler = _FakeHandler(headers={"Origin": "https://app.example.com"})

    send_json_response(handler, {"ok": True}, 200)

    assert handler.sent_headers["Access-Control-Allow-Origin"] == "https://app.example.com"


def test_send_json_response_allows_explicit_wildcard_origin(monkeypatch) -> None:
    monkeypatch.setenv("TONESOUL_CORS_ORIGINS", "*")
    handler = _FakeHandler(headers={"Origin": "https://app.example.com"})

    send_json_response(handler, {"ok": True}, 200)

    assert handler.sent_headers["Access-Control-Allow-Origin"] == "*"


def test_serverless_production_env_honors_flask_env(monkeypatch) -> None:
    monkeypatch.delenv("TONESOUL_PRODUCTION", raising=False)
    monkeypatch.delenv("TONESOUL_ENV", raising=False)
    monkeypatch.setenv("FLASK_ENV", "production")

    assert shared_core._is_production_env() is True


def test_serverless_production_env_honors_node_env(monkeypatch) -> None:
    monkeypatch.delenv("TONESOUL_PRODUCTION", raising=False)
    monkeypatch.delenv("TONESOUL_ENV", raising=False)
    monkeypatch.delenv("FLASK_ENV", raising=False)
    monkeypatch.setenv("NODE_ENV", "production")

    assert shared_core._is_production_env() is True


def test_serverless_production_env_honors_vercel_preview(monkeypatch) -> None:
    monkeypatch.delenv("TONESOUL_PRODUCTION", raising=False)
    monkeypatch.delenv("TONESOUL_ENV", raising=False)
    monkeypatch.delenv("FLASK_ENV", raising=False)
    monkeypatch.delenv("NODE_ENV", raising=False)
    monkeypatch.setenv("VERCEL_ENV", "preview")

    assert shared_core._is_production_env() is True


def test_internal_error_response_redacts_exception_text() -> None:
    payload, status_code = shared_core._internal_error_response(
        "Failed to process chat request",
        exc=RuntimeError("SECRET_WRITE_TOKEN_999"),
        extra={"response": None},
    )

    assert status_code == 500
    assert payload["error"] == "Failed to process chat request"
    assert payload["response"] is None
    assert re.fullmatch(r"[0-9a-f]{12}", payload["error_id"])
    assert "SECRET_WRITE_TOKEN_999" not in json.dumps(payload, ensure_ascii=False)
