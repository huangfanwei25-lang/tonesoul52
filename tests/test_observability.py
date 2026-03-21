"""Tests for the ToneSoul observability infrastructure."""

from __future__ import annotations

import json

import pytest

# ---------------------------------------------------------------------------
# logger.py
# ---------------------------------------------------------------------------


class TestStructuredLogger:
    def test_get_logger_returns_bound_logger(self):
        from tonesoul.observability.logger import get_logger

        log = get_logger("test.module", layer="test", actor="pytest")
        assert log is not None

    def test_logger_writes_to_file(self, tmp_path):
        """Verify that logging produces a JSONL file."""
        from tonesoul.observability import logger as logger_mod

        # Override log dir
        logger_mod._LOG_DIR = tmp_path
        logger_mod._CONFIGURED = False  # force reconfigure

        log = logger_mod.get_logger("test.file_write", layer="test")
        log.info("hello_test", key="value")

        # Check that at least one .jsonl file was created
        jsonl_files = list(tmp_path.glob("tonesoul_*.jsonl"))
        assert len(jsonl_files) >= 1, f"Expected JSONL files in {tmp_path}"

        # Reset for other tests
        logger_mod._LOG_DIR = None
        logger_mod._CONFIGURED = False


# ---------------------------------------------------------------------------
# token_meter.py
# ---------------------------------------------------------------------------


class TestTokenMeter:
    def test_record_and_session_totals(self, tmp_path):
        from tonesoul.observability.token_meter import TokenMeter

        meter = TokenMeter(log_dir=tmp_path)
        meter.record("gemma3:4b", prompt_tokens=100, completion_tokens=50)
        meter.record("gemma3:4b", prompt_tokens=200, completion_tokens=100)

        totals = meter.get_session_totals()
        assert totals["calls"] == 2
        assert totals["prompt_tokens"] == 300
        assert totals["completion_tokens"] == 150
        assert totals["total_tokens"] == 450

    def test_daily_totals_from_file(self, tmp_path):
        from tonesoul.observability.token_meter import TokenMeter

        meter = TokenMeter(log_dir=tmp_path)
        meter.record("qwen3.5:4b", prompt_tokens=500, completion_tokens=250)

        daily = meter.get_daily_totals()
        assert daily["calls"] == 1
        assert daily["total_tokens"] == 750

    def test_local_models_are_free(self, tmp_path):
        from tonesoul.observability.token_meter import TokenMeter

        meter = TokenMeter(log_dir=tmp_path)
        rec = meter.record("gemma3:4b", prompt_tokens=10000, completion_tokens=5000)
        assert rec.cost_usd == 0.0

    def test_budget_circuit_breaker(self, tmp_path):
        from tonesoul.observability.token_meter import BudgetExceeded, TokenMeter

        meter = TokenMeter(log_dir=tmp_path)
        # Record a cloud model call with explicit cost
        meter.record("gpt-4.1", prompt_tokens=1000, completion_tokens=500, cost_usd=10.0)

        with pytest.raises(BudgetExceeded) as exc_info:
            meter.check_budget(daily_limit_usd=5.00)
        assert exc_info.value.spent == 10.0

    def test_budget_ok_when_under_limit(self, tmp_path):
        from tonesoul.observability.token_meter import TokenMeter

        meter = TokenMeter(log_dir=tmp_path)
        meter.record("gemma3:4b", prompt_tokens=100, completion_tokens=50)
        # Should not raise
        meter.check_budget(daily_limit_usd=5.00)

    def test_jsonl_file_written(self, tmp_path):
        from tonesoul.observability.token_meter import TokenMeter

        meter = TokenMeter(log_dir=tmp_path)
        meter.record("gemma3:4b", prompt_tokens=100, completion_tokens=50)

        files = list(tmp_path.glob("token_usage_*.jsonl"))
        assert len(files) == 1
        content = files[0].read_text(encoding="utf-8").strip()
        record = json.loads(content)
        assert record["model"] == "gemma3:4b"


# ---------------------------------------------------------------------------
# action_audit.py
# ---------------------------------------------------------------------------


class TestActionAuditor:
    def test_log_and_query(self, tmp_path):
        from tonesoul.observability.action_audit import ActionAuditor

        db_path = tmp_path / "test_audit.db"
        auditor = ActionAuditor(db_path=db_path)

        action_id = auditor.log_action(
            actor="antigravity",
            action_type="api_post",
            target="moltbook/m/philosophy",
            detail="Test post",
            approved_by="human",
        )
        assert action_id.startswith("act_")

        results = auditor.query_actions()
        assert len(results) == 1
        assert results[0]["actor"] == "antigravity"
        assert results[0]["action_type"] == "api_post"

    def test_count_actions(self, tmp_path):
        from tonesoul.observability.action_audit import ActionAuditor

        db_path = tmp_path / "test_count.db"
        auditor = ActionAuditor(db_path=db_path)

        for i in range(5):
            auditor.log_action(actor="test", action_type="write", detail=f"action_{i}")

        assert auditor.count_actions() == 5

    def test_filter_by_actor(self, tmp_path):
        from tonesoul.observability.action_audit import ActionAuditor

        db_path = tmp_path / "test_filter.db"
        auditor = ActionAuditor(db_path=db_path)

        auditor.log_action(actor="antigravity", action_type="read", detail="a")
        auditor.log_action(actor="codex", action_type="write", detail="b")
        auditor.log_action(actor="antigravity", action_type="post", detail="c")

        results = auditor.query_actions(actor="antigravity")
        assert len(results) == 2

    def test_metadata_stored_as_json(self, tmp_path):
        from tonesoul.observability.action_audit import ActionAuditor

        db_path = tmp_path / "test_meta.db"
        auditor = ActionAuditor(db_path=db_path)

        auditor.log_action(
            actor="cron",
            action_type="dream_cycle",
            metadata={"friction": 0.73, "lyapunov": 1.2},
        )

        results = auditor.query_actions()
        assert results[0]["metadata"]["friction"] == 0.73


# ---------------------------------------------------------------------------
# env_config.py
# ---------------------------------------------------------------------------


class TestEnvConfig:
    def test_get_env_returns_default(self):
        from tonesoul.observability.env_config import get_env

        # A key that's definitely not set
        val = get_env("TONESOUL_TEST_NONEXISTENT_KEY_12345", default="fallback")
        assert val == "fallback"

    def test_get_env_uses_defaults_dict(self):
        from tonesoul.observability.env_config import get_env

        val = get_env("OLLAMA_HOST")
        assert "localhost" in val

    def test_os_env_overrides(self, monkeypatch):
        from tonesoul.observability.env_config import get_env

        monkeypatch.setenv("OLLAMA_HOST", "http://custom:9999")
        assert get_env("OLLAMA_HOST") == "http://custom:9999"

    def test_is_ci_detection(self, monkeypatch):
        from tonesoul.observability.env_config import is_ci

        monkeypatch.delenv("CI", raising=False)
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        # Should not be CI in test env (unless actually in CI)
        # Just verify it runs without error
        result = is_ci()
        assert isinstance(result, bool)

    def test_get_all_config(self):
        from tonesoul.observability.env_config import get_all_config

        config = get_all_config()
        assert "OLLAMA_HOST" in config
        assert "LOG_LEVEL" in config
