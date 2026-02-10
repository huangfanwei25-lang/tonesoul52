import pytest

import scripts.run_7d_isolated as run_7d_isolated


def test_parse_base_url_accepts_localhost_with_port():
    host, port = run_7d_isolated._parse_base_url("http://127.0.0.1:5001", "api-base")
    assert host == "127.0.0.1"
    assert port == 5001


def test_parse_base_url_rejects_non_localhost():
    with pytest.raises(ValueError):
        run_7d_isolated._parse_base_url("http://example.com:5001", "api-base")


def test_parse_base_url_requires_explicit_port():
    with pytest.raises(ValueError):
        run_7d_isolated._parse_base_url("http://127.0.0.1", "api-base")


def test_wait_for_url_retries_on_connection_reset(monkeypatch):
    calls = {"count": 0}

    class _Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def _fake_urlopen(url, timeout):  # noqa: ARG001
        calls["count"] += 1
        if calls["count"] == 1:
            raise ConnectionResetError("connection reset")
        return _Response()

    monkeypatch.setattr(run_7d_isolated.urllib.request, "urlopen", _fake_urlopen)
    monkeypatch.setattr(run_7d_isolated.time, "sleep", lambda _: None)

    assert run_7d_isolated._wait_for_url("http://127.0.0.1:3002/", timeout_seconds=2)
    assert calls["count"] == 2
