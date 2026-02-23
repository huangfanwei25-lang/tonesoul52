"""
Red Team Tests: API Fuzzing and Application Bounds.
"""

import pytest

from apps.api.server import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_payload_excessive_length(client):
    # 1MB of 'A's
    large_payload = {"message": "A" * 1024 * 1024}
    response = client.post("/api/chat", json=large_payload)
    # Target should reject early with 413 Payload Too Large or 400 Bad Request, but 500 is defensively acceptable vs crashing.
    assert response.status_code in (400, 413, 500)


def test_payload_deeply_nested_json(client):
    # Construct a highly nested dict
    nested = {"a": "b"}
    for _ in range(100):
        nested = {"nest": nested}

    response = client.post("/api/session-report", json={"history": [nested]})
    assert response.status_code in (400, 500)


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"message": ""},
        {"message": "   "},
        {"message": None},
        {"unknown_field": "test"},
    ],
)
def test_chat_empty_or_invalid_message_handling(client, payload):
    response = client.post("/api/chat", json=payload)
    assert response.status_code in (400, 500)


def test_chat_null_byte_injection(client):
    response = client.post("/api/chat", json={"message": "Safe text \x00 Evil text"})
    # Must not crash interpreter or C extensions
    assert response.status_code in (200, 400, 500)


def test_invalid_unicode_mojibake_handling(client):
    # Random byte string decoded as utf-8 (ignoring errors) to simulate malformed input
    mojibake = "\ud83d\ude00\ud83d".encode("utf-16", "surrogatepass").decode("utf-16", "ignore")
    response = client.post("/api/chat", json={"message": mojibake})
    assert response.status_code in (200, 400, 500)
