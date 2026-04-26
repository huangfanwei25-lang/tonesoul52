"""Tests for games/under_the_island/bridge — FileBridgeAdapter + LLM provider."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from games.under_the_island.bridge.event_adapter import FileBridgeAdapter
from games.under_the_island.bridge.llm_provider import (
    DEFAULT_MODELS,
    _check_package,
    call_llm,
    diagnostics,
    resolve_model,
    resolve_provider,
)


# ---------------------------------------------------------------------------
# FileBridgeAdapter — BOM + round-trip
# ---------------------------------------------------------------------------

class TestFileBridgeAdapterBom:
    """PowerShell Set-Content -Encoding utf8 writes a UTF-8 BOM.
    The adapter must handle BOM-prefixed JSON without crashing.
    """

    def _adapter(self, tmp_path: Path) -> tuple[FileBridgeAdapter, Path, Path]:
        ev = tmp_path / "bridge_event.json"
        rp = tmp_path / "bridge_reply.json"
        return FileBridgeAdapter(event_file=ev, reply_file=rp), ev, rp

    def test_reads_bom_prefixed_json(self, tmp_path: Path) -> None:
        adapter, ev, _ = self._adapter(tmp_path)
        payload = {"event": "puzzle_solved", "player_choice": "helped", "scene": "cave"}
        bom_bytes = b"\xef\xbb\xbf" + json.dumps(payload).encode("utf-8")
        ev.write_bytes(bom_bytes)
        events = list(adapter.poll())
        assert len(events) == 1
        assert events[0].event == "puzzle_solved"
        assert events[0].player_choice == "helped"
        assert events[0].scene == "cave"

    def test_reads_plain_utf8_json(self, tmp_path: Path) -> None:
        adapter, ev, _ = self._adapter(tmp_path)
        payload = {"event": "npc_talk", "player_choice": "asked", "scene": "market"}
        ev.write_text(json.dumps(payload), encoding="utf-8")
        events = list(adapter.poll())
        assert len(events) == 1
        assert events[0].event == "npc_talk"

    def test_no_duplicate_read_same_mtime(self, tmp_path: Path) -> None:
        adapter, ev, _ = self._adapter(tmp_path)
        ev.write_text(json.dumps({"event": "e", "player_choice": "c", "scene": "s"}), encoding="utf-8")
        first = list(adapter.poll())
        second = list(adapter.poll())
        assert len(first) == 1
        assert len(second) == 0

    def test_write_reply_produces_valid_json(self, tmp_path: Path) -> None:
        adapter, _, rp = self._adapter(tmp_path)
        adapter.write_reply("你好，旅人。", 0.55)
        assert rp.exists()
        data = json.loads(rp.read_text(encoding="utf-8"))
        assert data["reply"] == "你好，旅人。"
        assert abs(data["trust"] - 0.55) < 0.001

    def test_cleanup_removes_both_files(self, tmp_path: Path) -> None:
        adapter, ev, rp = self._adapter(tmp_path)
        ev.write_text("{}", encoding="utf-8")
        rp.write_text("{}", encoding="utf-8")
        adapter.cleanup()
        assert not ev.exists()
        assert not rp.exists()


# ---------------------------------------------------------------------------
# resolve_provider — auto selection logic
# ---------------------------------------------------------------------------

class TestResolveProvider:
    def _clean_env(self, monkeypatch):
        for k in ("BRIDGE_LLM_PROVIDER", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"):
            monkeypatch.delenv(k, raising=False)

    def test_explicit_anthropic(self, monkeypatch) -> None:
        self._clean_env(monkeypatch)
        assert resolve_provider("anthropic") == "anthropic"

    def test_explicit_gemini(self, monkeypatch) -> None:
        self._clean_env(monkeypatch)
        assert resolve_provider("gemini") == "gemini"

    def test_auto_prefers_bridge_llm_provider_env(self, monkeypatch) -> None:
        self._clean_env(monkeypatch)
        monkeypatch.setenv("BRIDGE_LLM_PROVIDER", "gemini")
        assert resolve_provider("auto") == "gemini"

    def test_auto_bridge_env_anthropic(self, monkeypatch) -> None:
        self._clean_env(monkeypatch)
        monkeypatch.setenv("BRIDGE_LLM_PROVIDER", "anthropic")
        assert resolve_provider("auto") == "anthropic"

    def test_auto_falls_back_to_anthropic_key(self, monkeypatch) -> None:
        self._clean_env(monkeypatch)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        assert resolve_provider("auto") == "anthropic"

    def test_auto_falls_back_to_gemini_key_when_no_anthropic(self, monkeypatch) -> None:
        self._clean_env(monkeypatch)
        monkeypatch.setenv("GEMINI_API_KEY", "gk-test")
        assert resolve_provider("auto") == "gemini"

    def test_auto_prefers_anthropic_key_over_gemini_key(self, monkeypatch) -> None:
        self._clean_env(monkeypatch)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        monkeypatch.setenv("GEMINI_API_KEY", "gk-test")
        assert resolve_provider("auto") == "anthropic"

    def test_auto_no_keys_defaults_to_anthropic(self, monkeypatch) -> None:
        self._clean_env(monkeypatch)
        assert resolve_provider("auto") == "anthropic"

    def test_bridge_env_invalid_value_ignored(self, monkeypatch) -> None:
        self._clean_env(monkeypatch)
        monkeypatch.setenv("BRIDGE_LLM_PROVIDER", "openai")  # not valid
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
        assert resolve_provider("auto") == "anthropic"


# ---------------------------------------------------------------------------
# resolve_model — priority chain
# ---------------------------------------------------------------------------

class TestResolveModel:
    def test_explicit_model_wins(self, monkeypatch) -> None:
        monkeypatch.delenv("BRIDGE_LLM_MODEL", raising=False)
        assert resolve_model("anthropic", "claude-opus-4-6") == "claude-opus-4-6"

    def test_env_var_used_when_no_explicit(self, monkeypatch) -> None:
        monkeypatch.setenv("BRIDGE_LLM_MODEL", "gemini-pro")
        assert resolve_model("anthropic", None) == "gemini-pro"

    def test_default_anthropic_model(self, monkeypatch) -> None:
        monkeypatch.delenv("BRIDGE_LLM_MODEL", raising=False)
        assert resolve_model("anthropic", None) == DEFAULT_MODELS["anthropic"]

    def test_default_gemini_model(self, monkeypatch) -> None:
        monkeypatch.delenv("BRIDGE_LLM_MODEL", raising=False)
        assert resolve_model("gemini", None) == DEFAULT_MODELS["gemini"]
        assert DEFAULT_MODELS["gemini"] == "models/gemini-flash-lite-latest"

    def test_explicit_overrides_env(self, monkeypatch) -> None:
        monkeypatch.setenv("BRIDGE_LLM_MODEL", "env-model")
        assert resolve_model("anthropic", "explicit-model") == "explicit-model"


# ---------------------------------------------------------------------------
# call_llm — package-missing branches return error strings, not exceptions
# ---------------------------------------------------------------------------

class TestCallLlmErrorStrings:
    def test_anthropic_import_error_returns_string(self) -> None:
        with patch.dict("sys.modules", {"anthropic": None}):
            result = call_llm("sys", "msg", "anthropic", "claude-sonnet-4-6")
        assert result.startswith("[")
        assert "anthropic" in result.lower() or "錯誤" in result

    def test_gemini_import_error_returns_string(self) -> None:
        with patch.dict("sys.modules", {"google": None, "google.genai": None}):
            result = call_llm("sys", "msg", "gemini", "gemini-2.0-flash")
        assert result.startswith("[")

    def test_unknown_provider_returns_string(self) -> None:
        result = call_llm("sys", "msg", "openai", "gpt-4")
        assert "未知" in result or "unknown" in result.lower()

    def test_anthropic_api_exception_returns_string(self) -> None:
        try:
            import anthropic  # noqa: F401
        except ImportError:
            pytest.skip("anthropic not installed in this environment")
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = RuntimeError("quota exceeded")
        with patch("anthropic.Anthropic", return_value=mock_client):
            result = call_llm("sys", "msg", "anthropic", "claude-sonnet-4-6")
        assert result.startswith("[")
        assert "quota exceeded" in result


# ---------------------------------------------------------------------------
# diagnostics — structured readiness check
# ---------------------------------------------------------------------------

class TestDiagnostics:
    def _clean(self, monkeypatch):
        for k in ("ANTHROPIC_API_KEY", "GEMINI_API_KEY", "BRIDGE_LLM_PROVIDER", "BRIDGE_LLM_MODEL"):
            monkeypatch.delenv(k, raising=False)

    def test_ready_false_when_anthropic_key_missing(self, monkeypatch) -> None:
        self._clean(monkeypatch)
        diag = diagnostics("anthropic", "claude-sonnet-4-6")
        assert diag["provider"] == "anthropic"
        assert diag["anthropic_key_set"] is False
        assert len(diag["issues"]) > 0

    def test_ready_false_when_gemini_key_missing(self, monkeypatch) -> None:
        self._clean(monkeypatch)
        diag = diagnostics("gemini", "gemini-2.0-flash")
        assert diag["gemini_key_set"] is False
        assert len(diag["issues"]) > 0

    def test_reports_env_vars(self, monkeypatch) -> None:
        self._clean(monkeypatch)
        monkeypatch.setenv("BRIDGE_LLM_MODEL", "test-model")
        diag = diagnostics("anthropic", "test-model")
        assert diag["env_vars"]["BRIDGE_LLM_MODEL"] == "test-model"

    def test_structure_keys_present(self, monkeypatch) -> None:
        self._clean(monkeypatch)
        diag = diagnostics("anthropic", "claude-sonnet-4-6")
        for k in ("provider", "model", "anthropic_key_set", "gemini_key_set",
                   "package_ok", "issues", "ready", "env_vars"):
            assert k in diag, f"missing key: {k}"
