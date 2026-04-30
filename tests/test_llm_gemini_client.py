"""Tests for tonesoul.llm.gemini_client — pure helpers."""

from __future__ import annotations

from tonesoul.llm.gemini_client import (
    _build_narrative_reasoning_prompt,
    _resolve_api_key,
)

# ── _resolve_api_key ──────────────────────────────────────────────────────────


class TestResolveApiKey:
    def test_explicit_key_returned(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        assert _resolve_api_key("my-key") == "my-key"

    def test_strips_whitespace(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        assert _resolve_api_key("  key123  ") == "key123"

    def test_env_gemini_used_when_no_arg(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "env-key")
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        assert _resolve_api_key(None) == "env-key"

    def test_env_google_fallback(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.setenv("GOOGLE_API_KEY", "google-key")
        assert _resolve_api_key(None) == "google-key"

    def test_explicit_beats_env(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "env-key")
        assert _resolve_api_key("explicit") == "explicit"

    def test_none_and_no_env_returns_none(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        assert _resolve_api_key(None) is None

    def test_empty_string_skipped(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        assert _resolve_api_key("") is None

    def test_whitespace_only_skipped(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        assert _resolve_api_key("   ") is None


# ── _build_narrative_reasoning_prompt ─────────────────────────────────────────


class TestBuildNarrativeReasoningPrompt:
    def _base_verdict(self, **kw):
        d = {
            "verdict": "approve",
            "coherence": {"overall": 0.8},
            "votes": [{"perspective": "guardian", "decision": "approve"}],
            "divergence_analysis": {"core_divergence": "none"},
        }
        d.update(kw)
        return d

    def test_contains_verdict(self):
        prompt = _build_narrative_reasoning_prompt(self._base_verdict())
        assert "approve" in prompt

    def test_contains_coherence_percent(self):
        prompt = _build_narrative_reasoning_prompt(self._base_verdict())
        assert "80%" in prompt

    def test_contains_vote_perspective(self):
        prompt = _build_narrative_reasoning_prompt(self._base_verdict())
        assert "guardian" in prompt

    def test_empty_votes_placeholder(self):
        verdict = self._base_verdict(votes=[])
        prompt = _build_narrative_reasoning_prompt(verdict)
        assert "[資料不足]" in prompt

    def test_missing_coherence_defaults(self):
        verdict = {"verdict": "block"}
        prompt = _build_narrative_reasoning_prompt(verdict)
        assert "50%" in prompt

    def test_divergence_included(self):
        verdict = self._base_verdict(divergence_analysis={"core_divergence": "strong"})
        prompt = _build_narrative_reasoning_prompt(verdict)
        assert "strong" in prompt

    def test_returns_string(self):
        prompt = _build_narrative_reasoning_prompt(self._base_verdict())
        assert isinstance(prompt, str)

    def test_chinese_instructions_present(self):
        prompt = _build_narrative_reasoning_prompt(self._base_verdict())
        assert "Chinese" in prompt or "中文" in prompt or "Chinese only" in prompt
