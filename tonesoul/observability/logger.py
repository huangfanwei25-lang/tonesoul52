"""Structured logging for ToneSoul.

Uses structlog to produce JSON-formatted logs written to both
console (colorized for dev) and daily JSONL files under logs/.

Usage:
    from tonesoul.observability.logger import get_logger
    log = get_logger("governance.kernel")
    log.info("tension_computed", friction=0.73, layer="governance")
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

try:
    import structlog
except ModuleNotFoundError:  # pragma: no cover - exercised in environments without structlog
    structlog = None

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_LOG_DIR: Optional[Path] = None
_CONFIGURED = False


def _default_log_dir() -> Path:
    """Return <repo_root>/logs/ as the default log directory."""
    repo = Path(__file__).resolve().parent.parent.parent
    return repo / "logs"


def _ensure_log_dir() -> Path:
    global _LOG_DIR
    if _LOG_DIR is None:
        _LOG_DIR = _default_log_dir()
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    return _LOG_DIR


# ---------------------------------------------------------------------------
# JSONL file handler
# ---------------------------------------------------------------------------


class _JsonlFileHandler(logging.Handler):
    """Logging handler that appends JSON lines to a daily file."""

    def __init__(self, log_dir: Path) -> None:
        super().__init__()
        self._log_dir = log_dir
        self._current_date: Optional[str] = None
        self._file = None

    def _rotate_if_needed(self) -> None:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if today != self._current_date:
            if self._file:
                self._file.close()
            self._current_date = today
            path = self._log_dir / f"tonesoul_{today}.jsonl"
            self._file = open(path, "a", encoding="utf-8")

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._rotate_if_needed()
            # structlog renders the message as a JSON string
            msg = self.format(record)
            if self._file:
                self._file.write(msg + "\n")
                self._file.flush()
        except Exception:
            self.handleError(record)

    def close(self) -> None:
        if self._file:
            self._file.close()
        super().close()


# ---------------------------------------------------------------------------
# stdlib fallback (used when structlog is unavailable)
# ---------------------------------------------------------------------------


class _FallbackBoundLogger:
    """Small structlog-like adapter backed by stdlib logging."""

    _LEVELS = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    def __init__(self, logger: logging.Logger, bindings: Optional[dict[str, Any]] = None) -> None:
        self._logger = logger
        self._bindings = dict(bindings or {})

    def bind(self, **kwargs: Any) -> "_FallbackBoundLogger":
        merged = dict(self._bindings)
        merged.update(kwargs)
        return _FallbackBoundLogger(self._logger, merged)

    def _emit(self, level: str, event: str, **kwargs: Any) -> None:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "logger": self._logger.name,
            "event": event,
        }
        payload.update(self._bindings)
        payload.update(kwargs)
        self._logger.log(self._LEVELS[level], json.dumps(payload, ensure_ascii=False, default=str))

    def debug(self, event: str, **kwargs: Any) -> None:
        self._emit("debug", event, **kwargs)

    def info(self, event: str, **kwargs: Any) -> None:
        self._emit("info", event, **kwargs)

    def warning(self, event: str, **kwargs: Any) -> None:
        self._emit("warning", event, **kwargs)

    def error(self, event: str, **kwargs: Any) -> None:
        self._emit("error", event, **kwargs)

    def critical(self, event: str, **kwargs: Any) -> None:
        self._emit("critical", event, **kwargs)

    def exception(self, event: str, **kwargs: Any) -> None:
        kwargs.setdefault("exc_info", True)
        self._emit("error", event, **kwargs)


# ---------------------------------------------------------------------------
# structlog configuration (called once)
# ---------------------------------------------------------------------------


def _configure_structlog() -> None:
    """Configure logging once, with structlog when available."""
    global _CONFIGURED
    if _CONFIGURED:
        return
    _CONFIGURED = True

    log_dir = _ensure_log_dir()

    # stdlib logging setup
    root_logger = logging.getLogger("tonesoul")
    root_logger.setLevel(logging.DEBUG)

    # Console handler (human-readable)
    console = logging.StreamHandler(sys.stderr)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(console)

    # JSONL file handler
    jsonl_handler = _JsonlFileHandler(log_dir)
    jsonl_handler.setLevel(logging.DEBUG)
    jsonl_handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(jsonl_handler)

    if structlog is None:
        return

    # structlog processors
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_logger(
    name: str,
    *,
    layer: Optional[str] = None,
    actor: Optional[str] = None,
) -> Any:
    """Get a structured logger bound with optional layer and actor context.

    Args:
        name: Logger name (e.g. "governance.kernel", "llm.router").
        layer: System layer (governance, llm, perception, memory, observability).
        actor: Who is performing the action (antigravity, codex, human, cron).

    Returns:
        A structlog BoundLogger instance.

    Example:
        log = get_logger("governance.kernel", layer="governance", actor="antigravity")
        log.info("circuit_breaker_triggered", friction=0.95)
    """
    _configure_structlog()
    if structlog is None:
        logger: Any = _FallbackBoundLogger(logging.getLogger(f"tonesoul.{name}"))
    else:
        logger = structlog.get_logger(f"tonesoul.{name}")
    bindings: dict[str, Any] = {}
    if layer:
        bindings["layer"] = layer
    if actor:
        bindings["actor"] = actor
    if bindings:
        logger = logger.bind(**bindings)
    return logger
