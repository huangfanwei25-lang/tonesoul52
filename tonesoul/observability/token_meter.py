"""Token burn-rate metering and budget circuit breaker.

Tracks every LLM call's token usage and cost. Provides session/daily
totals and a budget circuit breaker that raises BudgetExceeded if the
daily spend goes past a configurable threshold.

Usage:
    from tonesoul.observability.token_meter import TokenMeter
    meter = TokenMeter()
    meter.record("gemma3:4b", prompt_tokens=320, completion_tokens=150)
    print(meter.get_session_totals())
    meter.check_budget(daily_limit_usd=1.00)
"""

from __future__ import annotations

import json
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Cost estimation (per 1M tokens, approximate)
# ---------------------------------------------------------------------------

_COST_PER_1M: dict[str, dict[str, float]] = {
    # Local models: effectively free
    "gemma3:4b": {"prompt": 0.0, "completion": 0.0},
    "qwen3.5:4b": {"prompt": 0.0, "completion": 0.0},
    "qwen35-9b-uncensored": {"prompt": 0.0, "completion": 0.0},
    "nomic-embed-text": {"prompt": 0.0, "completion": 0.0},
    # Cloud fallbacks (if ever used)
    "gemini-2.0-flash": {"prompt": 0.10, "completion": 0.40},
    "gemini-2.5-pro": {"prompt": 1.25, "completion": 10.00},
    "gpt-4.1": {"prompt": 2.00, "completion": 8.00},
    "claude-sonnet-4": {"prompt": 3.00, "completion": 15.00},
}

_DEFAULT_COST = {"prompt": 0.50, "completion": 2.00}


def _estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Estimate USD cost for an LLM call."""
    rates = _COST_PER_1M.get(model, _DEFAULT_COST)
    cost = (prompt_tokens / 1_000_000) * rates["prompt"]
    cost += (completion_tokens / 1_000_000) * rates["completion"]
    return round(cost, 6)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class BudgetExceeded(RuntimeError):
    """Raised when the daily token budget is exceeded."""

    def __init__(self, spent: float, limit: float) -> None:
        self.spent = spent
        self.limit = limit
        super().__init__(f"Daily budget exceeded: ${spent:.4f} spent, limit ${limit:.2f}")


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class LLMCallRecord:
    timestamp: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    trace_id: Optional[str] = None


@dataclass
class UsageTotals:
    calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    models: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# TokenMeter
# ---------------------------------------------------------------------------


class TokenMeter:
    """Global token usage tracker and budget circuit breaker."""

    def __init__(self, log_dir: Optional[Path] = None) -> None:
        if log_dir is None:
            log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
        self._log_dir = log_dir
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._session = UsageTotals()

    def record(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: Optional[float] = None,
        trace_id: Optional[str] = None,
    ) -> LLMCallRecord:
        """Record one LLM call and persist to daily JSONL.

        Args:
            model: Model name (e.g. "gemma3:4b").
            prompt_tokens: Number of prompt/input tokens.
            completion_tokens: Number of completion/output tokens.
            cost_usd: Override cost (auto-estimated if None).
            trace_id: Optional trace ID for correlation.

        Returns:
            The recorded LLMCallRecord.
        """
        if cost_usd is None:
            cost_usd = _estimate_cost(model, prompt_tokens, completion_tokens)

        total = prompt_tokens + completion_tokens
        stamp = datetime.now(timezone.utc).isoformat()

        rec = LLMCallRecord(
            timestamp=stamp,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total,
            cost_usd=cost_usd,
            trace_id=trace_id,
        )

        with self._lock:
            self._session.calls += 1
            self._session.prompt_tokens += prompt_tokens
            self._session.completion_tokens += completion_tokens
            self._session.total_tokens += total
            self._session.cost_usd += cost_usd
            self._session.models[model] = self._session.models.get(model, 0) + 1

        # Persist to daily file
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        path = self._log_dir / f"token_usage_{today}.jsonl"
        with open(path, "a", encoding="utf-8") as f:
            json.dump(asdict(rec), f, ensure_ascii=False)
            f.write("\n")

        return rec

    def get_session_totals(self) -> dict:
        """Return accumulated totals for the current session."""
        with self._lock:
            return asdict(self._session)

    def get_daily_totals(self) -> dict:
        """Read all records from today's log file and compute totals."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        path = self._log_dir / f"token_usage_{today}.jsonl"
        if not path.exists():
            return asdict(UsageTotals())

        totals = UsageTotals()
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    totals.calls += 1
                    totals.prompt_tokens += rec.get("prompt_tokens", 0)
                    totals.completion_tokens += rec.get("completion_tokens", 0)
                    totals.total_tokens += rec.get("total_tokens", 0)
                    totals.cost_usd += rec.get("cost_usd", 0.0)
                    m = rec.get("model", "unknown")
                    totals.models[m] = totals.models.get(m, 0) + 1
                except json.JSONDecodeError:
                    continue
        return asdict(totals)

    def check_budget(self, daily_limit_usd: float = 5.00) -> None:
        """Raise BudgetExceeded if today's spend exceeds the limit.

        Args:
            daily_limit_usd: Maximum allowed daily spend in USD.

        Raises:
            BudgetExceeded: If the budget is exceeded.
        """
        totals = self.get_daily_totals()
        spent = totals["cost_usd"]
        if spent > daily_limit_usd:
            raise BudgetExceeded(spent, daily_limit_usd)
