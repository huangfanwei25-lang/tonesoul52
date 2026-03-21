from pathlib import Path

from tonesoul.observability import env_config as env_mod


def test_load_env_uses_existing_custom_path_only_once(monkeypatch, tmp_path):
    calls = []
    env_path = tmp_path / ".env"
    env_path.write_text("OLLAMA_HOST=http://override\n", encoding="utf-8")

    def fake_load(*, dotenv_path, override):
        calls.append((dotenv_path, override))

    monkeypatch.setattr(env_mod, "_dotenv_load", fake_load)
    monkeypatch.setattr(env_mod, "_loaded", False)

    env_mod.load_env(Path(env_path))
    env_mod.load_env(Path(env_path))

    assert calls == [(str(env_path), False)]


def test_load_env_skips_missing_file(monkeypatch, tmp_path):
    calls = []

    def fake_load(*, dotenv_path, override):
        calls.append((dotenv_path, override))

    monkeypatch.setattr(env_mod, "_dotenv_load", fake_load)
    monkeypatch.setattr(env_mod, "_loaded", False)

    env_mod.load_env(tmp_path / "missing.env")

    assert calls == []


def test_is_ci_detects_known_ci_variables(monkeypatch):
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.setenv("GITHUB_ACTIONS", "true")

    assert env_mod.is_ci() is True


def test_is_mock_mode_requires_missing_host_and_api_key(monkeypatch):
    monkeypatch.setattr(env_mod, "_loaded", True)
    monkeypatch.setitem(env_mod._DEFAULTS, "OLLAMA_HOST", "")
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    assert env_mod.is_mock_mode() is True


def test_get_all_config_reflects_env_overrides(monkeypatch):
    monkeypatch.setattr(env_mod, "_loaded", True)
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    config = env_mod.get_all_config()

    assert config["LOG_LEVEL"] == "DEBUG"
    assert "SOUL_DB_PATH" in config
