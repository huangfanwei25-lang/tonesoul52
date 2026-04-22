from __future__ import annotations

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


# ─────────────────────────────────────────────
# Extended coverage
# ─────────────────────────────────────────────


class TestGetEnv:
    def test_os_env_overrides_defaults(self, monkeypatch):
        monkeypatch.setattr(env_mod, "_loaded", True)
        monkeypatch.setenv("LOG_LEVEL", "ERROR")
        assert env_mod.get_env("LOG_LEVEL") == "ERROR"

    def test_default_from_defaults_dict(self, monkeypatch):
        monkeypatch.setattr(env_mod, "_loaded", True)
        monkeypatch.delenv("LOG_FORMAT", raising=False)
        assert env_mod.get_env("LOG_FORMAT") == "json"

    def test_explicit_default_used_when_key_unknown(self, monkeypatch):
        monkeypatch.setattr(env_mod, "_loaded", True)
        monkeypatch.delenv("UNKNOWN_KEY_XYZ", raising=False)
        assert env_mod.get_env("UNKNOWN_KEY_XYZ", default="fallback") == "fallback"

    def test_empty_string_returned_for_fully_unknown_key(self, monkeypatch):
        monkeypatch.setattr(env_mod, "_loaded", True)
        monkeypatch.delenv("TOTALLY_MISSING_VAR", raising=False)
        assert env_mod.get_env("TOTALLY_MISSING_VAR") == ""


class TestIsCI:
    def test_ci_env_var_detected(self, monkeypatch):
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.setenv("CI", "1")
        assert env_mod.is_ci() is True

    def test_gitlab_ci_detected(self, monkeypatch):
        for v in ("CI", "GITHUB_ACTIONS", "TRAVIS", "CIRCLECI"):
            monkeypatch.delenv(v, raising=False)
        monkeypatch.setenv("GITLAB_CI", "true")
        assert env_mod.is_ci() is True

    def test_no_ci_vars_returns_false(self, monkeypatch):
        for v in ("CI", "GITHUB_ACTIONS", "GITLAB_CI", "CIRCLECI", "TRAVIS"):
            monkeypatch.delenv(v, raising=False)
        assert env_mod.is_ci() is False


class TestIsMockMode:
    def test_gemini_key_present_is_not_mock(self, monkeypatch):
        monkeypatch.setattr(env_mod, "_loaded", True)
        monkeypatch.setenv("GEMINI_API_KEY", "real-key")
        assert env_mod.is_mock_mode() is False

    def test_ollama_host_present_is_not_mock(self, monkeypatch):
        monkeypatch.setattr(env_mod, "_loaded", True)
        monkeypatch.setitem(env_mod._DEFAULTS, "OLLAMA_HOST", "http://real-host")
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        assert env_mod.is_mock_mode() is False


class TestGetAllConfig:
    def test_all_defaults_keys_present(self, monkeypatch):
        monkeypatch.setattr(env_mod, "_loaded", True)
        config = env_mod.get_all_config()
        for key in env_mod._DEFAULTS:
            assert key in config

    def test_returns_dict_type(self, monkeypatch):
        monkeypatch.setattr(env_mod, "_loaded", True)
        assert isinstance(env_mod.get_all_config(), dict)
