"""Tests for tonesoul.unified_pipeline — pure env-reading helpers."""
from __future__ import annotations

import pytest

from tonesoul.unified_pipeline import _read_bool_env, _read_positive_int_env


# ── _read_bool_env ────────────────────────────────────────────────────────────

class TestReadBoolEnv:
    def test_unset_uses_default_false(self, monkeypatch):
        monkeypatch.delenv("TEST_BOOL_VAR", raising=False)
        assert _read_bool_env("TEST_BOOL_VAR") is False

    def test_unset_uses_default_true(self, monkeypatch):
        monkeypatch.delenv("TEST_BOOL_VAR", raising=False)
        assert _read_bool_env("TEST_BOOL_VAR", default=True) is True

    def test_true_values(self, monkeypatch):
        for val in ["1", "true", "yes", "on"]:
            monkeypatch.setenv("TEST_BOOL_VAR", val)
            assert _read_bool_env("TEST_BOOL_VAR") is True

    def test_false_values(self, monkeypatch):
        for val in ["0", "false", "no", "off"]:
            monkeypatch.setenv("TEST_BOOL_VAR", val)
            assert _read_bool_env("TEST_BOOL_VAR") is False

    def test_case_insensitive(self, monkeypatch):
        monkeypatch.setenv("TEST_BOOL_VAR", "TRUE")
        assert _read_bool_env("TEST_BOOL_VAR") is True

    def test_strips_whitespace(self, monkeypatch):
        monkeypatch.setenv("TEST_BOOL_VAR", "  1  ")
        assert _read_bool_env("TEST_BOOL_VAR") is True

    def test_unrecognized_returns_false(self, monkeypatch):
        monkeypatch.setenv("TEST_BOOL_VAR", "maybe")
        assert _read_bool_env("TEST_BOOL_VAR") is False


# ── _read_positive_int_env ────────────────────────────────────────────────────

class TestReadPositiveIntEnv:
    def test_unset_uses_default(self, monkeypatch):
        monkeypatch.delenv("TEST_INT_VAR", raising=False)
        assert _read_positive_int_env("TEST_INT_VAR", default=5) == 5

    def test_valid_int(self, monkeypatch):
        monkeypatch.setenv("TEST_INT_VAR", "10")
        assert _read_positive_int_env("TEST_INT_VAR", default=1) == 10

    def test_invalid_uses_default(self, monkeypatch):
        monkeypatch.setenv("TEST_INT_VAR", "bad")
        assert _read_positive_int_env("TEST_INT_VAR", default=3) == 3

    def test_zero_clamps_to_one(self, monkeypatch):
        monkeypatch.setenv("TEST_INT_VAR", "0")
        assert _read_positive_int_env("TEST_INT_VAR", default=1) == 1

    def test_negative_clamps_to_one(self, monkeypatch):
        monkeypatch.setenv("TEST_INT_VAR", "-5")
        assert _read_positive_int_env("TEST_INT_VAR", default=1) == 1

    def test_default_zero_clamps_to_one(self, monkeypatch):
        monkeypatch.delenv("TEST_INT_VAR", raising=False)
        assert _read_positive_int_env("TEST_INT_VAR", default=0) == 1
