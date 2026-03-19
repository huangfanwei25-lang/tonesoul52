import json
from datetime import datetime, timezone

from tonesoul.observability.token_meter import TokenMeter


def _today_log_name() -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"token_usage_{today}.jsonl"


def test_get_daily_totals_returns_zero_when_log_file_is_missing(tmp_path) -> None:
    meter = TokenMeter(log_dir=tmp_path)

    assert meter.get_daily_totals() == {
        "calls": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "cost_usd": 0.0,
        "models": {},
    }


def test_get_daily_totals_skips_blank_and_invalid_lines(tmp_path) -> None:
    meter = TokenMeter(log_dir=tmp_path)
    path = tmp_path / _today_log_name()
    valid_one = {
        "model": "gemma3:4b",
        "prompt_tokens": 10,
        "completion_tokens": 5,
        "total_tokens": 15,
        "cost_usd": 0.0,
    }
    valid_two = {
        "model": "gpt-4.1",
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "total_tokens": 150,
        "cost_usd": 1.25,
    }
    path.write_text(
        json.dumps(valid_one) + "\n\n" + "{bad json}\n" + json.dumps(valid_two) + "\n",
        encoding="utf-8",
    )

    totals = meter.get_daily_totals()

    assert totals["calls"] == 2
    assert totals["prompt_tokens"] == 110
    assert totals["completion_tokens"] == 55
    assert totals["total_tokens"] == 165
    assert totals["cost_usd"] == 1.25
    assert totals["models"] == {"gemma3:4b": 1, "gpt-4.1": 1}


def test_record_unknown_model_uses_default_cost_and_preserves_trace_id(tmp_path) -> None:
    meter = TokenMeter(log_dir=tmp_path)

    record = meter.record(
        "unknown-model",
        prompt_tokens=1000,
        completion_tokens=500,
        trace_id="trace-123",
    )

    payload = json.loads((tmp_path / _today_log_name()).read_text(encoding="utf-8").strip())
    assert record.cost_usd == 0.0015
    assert record.trace_id == "trace-123"
    assert payload["model"] == "unknown-model"
    assert payload["cost_usd"] == 0.0015
    assert payload["trace_id"] == "trace-123"


def test_check_budget_allows_exact_limit(tmp_path) -> None:
    meter = TokenMeter(log_dir=tmp_path)
    meter.record("gpt-4.1", prompt_tokens=1000, completion_tokens=500, cost_usd=1.0)

    meter.check_budget(daily_limit_usd=1.0)
