import apps.api.server as api_server


def _clear_bind_env(monkeypatch):
    monkeypatch.delenv("TONESOUL_API_HOST", raising=False)
    monkeypatch.delenv("TONESOUL_API_PORT", raising=False)
    monkeypatch.delenv("PORT", raising=False)


def test_resolve_bind_defaults(monkeypatch):
    _clear_bind_env(monkeypatch)

    assert api_server._resolve_bind_host() == "127.0.0.1"
    assert api_server._resolve_bind_port() == 5000


def test_resolve_bind_uses_render_port_when_tonesoul_port_missing(monkeypatch):
    _clear_bind_env(monkeypatch)
    monkeypatch.setenv("PORT", "10000")

    assert api_server._resolve_bind_host() == "0.0.0.0"
    assert api_server._resolve_bind_port() == 10000


def test_resolve_bind_tonesoul_port_overrides_render_port(monkeypatch):
    _clear_bind_env(monkeypatch)
    monkeypatch.setenv("PORT", "10000")
    monkeypatch.setenv("TONESOUL_API_PORT", "5001")

    assert api_server._resolve_bind_port() == 5001


def test_resolve_bind_prefers_explicit_host(monkeypatch):
    _clear_bind_env(monkeypatch)
    monkeypatch.setenv("PORT", "10000")
    monkeypatch.setenv("TONESOUL_API_HOST", "0.0.0.0")

    assert api_server._resolve_bind_host() == "0.0.0.0"


def test_resolve_bind_invalid_port_falls_back(monkeypatch):
    _clear_bind_env(monkeypatch)
    monkeypatch.setenv("PORT", "not-a-number")

    assert api_server._resolve_bind_port() == 5000
