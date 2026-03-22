import json
import logging

import pytest

from tonesoul.observability import logger as logger_mod


@pytest.fixture
def reset_logger_state():
    tonesoul_logger = logging.getLogger("tonesoul")
    for handler in list(tonesoul_logger.handlers):
        tonesoul_logger.removeHandler(handler)
        handler.close()
    logger_mod._LOG_DIR = None
    logger_mod._CONFIGURED = False
    yield
    tonesoul_logger = logging.getLogger("tonesoul")
    for handler in list(tonesoul_logger.handlers):
        tonesoul_logger.removeHandler(handler)
        handler.close()
    logger_mod._LOG_DIR = None
    logger_mod._CONFIGURED = False


def test_jsonl_file_handler_writes_formatted_record(tmp_path):
    handler = logger_mod._JsonlFileHandler(tmp_path)
    handler.setFormatter(logging.Formatter("%(message)s"))
    record = logging.LogRecord(
        name="tonesoul.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg='{"event":"hello","value":3}',
        args=(),
        exc_info=None,
    )

    handler.emit(record)
    files = list(tmp_path.glob("tonesoul_*.jsonl"))

    assert len(files) == 1
    assert json.loads(files[0].read_text(encoding="utf-8").strip()) == {
        "event": "hello",
        "value": 3,
    }
    handler.close()


def test_fallback_bound_logger_bind_and_exception_emit():
    captured = []

    class _CaptureHandler(logging.Handler):
        def emit(self, record):
            captured.append(json.loads(record.getMessage()))

    base_logger = logging.getLogger("tonesoul.fallback.capture")
    base_logger.handlers = []
    base_logger.propagate = False
    base_logger.setLevel(logging.DEBUG)
    base_logger.addHandler(_CaptureHandler())

    log = logger_mod._FallbackBoundLogger(base_logger).bind(request_id="req-1")
    log.warning("warning_event", count=2)
    log.exception("exception_event", reason="boom")

    assert captured[0]["event"] == "warning_event"
    assert captured[0]["request_id"] == "req-1"
    assert captured[0]["count"] == 2
    assert captured[1]["event"] == "exception_event"
    assert captured[1]["reason"] == "boom"
    assert captured[1]["exc_info"] is True


def test_get_logger_uses_fallback_when_structlog_missing(monkeypatch, tmp_path, reset_logger_state):
    monkeypatch.setattr(logger_mod, "structlog", None)
    logger_mod._LOG_DIR = tmp_path

    log = logger_mod.get_logger("fallback.mode", layer="obs", actor="pytest")
    log.info("fallback_event", value=7)

    files = list(tmp_path.glob("tonesoul_*.jsonl"))
    saved = json.loads(files[0].read_text(encoding="utf-8").strip())

    assert isinstance(log, logger_mod._FallbackBoundLogger)
    assert saved["event"] == "fallback_event"
    assert saved["layer"] == "obs"
    assert saved["actor"] == "pytest"
    assert saved["value"] == 7


def test_configure_structlog_is_idempotent(tmp_path, reset_logger_state):
    logger_mod._LOG_DIR = tmp_path

    logger_mod._configure_structlog()
    first_handler_count = len(logging.getLogger("tonesoul").handlers)
    logger_mod._configure_structlog()
    second_handler_count = len(logging.getLogger("tonesoul").handlers)

    assert first_handler_count == 2
    assert second_handler_count == 2
