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


# ── _default_log_dir ──────────────────────────────────────────────────────────


def test_default_log_dir_ends_with_logs():
    path = logger_mod._default_log_dir()
    assert path.name == "logs"
    assert path.is_absolute()


# ── _ensure_log_dir ───────────────────────────────────────────────────────────


def test_ensure_log_dir_creates_directory(tmp_path, reset_logger_state):
    target = tmp_path / "newdir"
    logger_mod._LOG_DIR = target
    result = logger_mod._ensure_log_dir()
    assert result.exists()
    assert result.is_dir()


def test_ensure_log_dir_sets_global_when_none(tmp_path, reset_logger_state):
    logger_mod._LOG_DIR = None
    # Override _default_log_dir to avoid writing into repo
    original = logger_mod._default_log_dir
    logger_mod._default_log_dir = lambda: tmp_path / "override"
    try:
        result = logger_mod._ensure_log_dir()
        assert result == tmp_path / "override"
    finally:
        logger_mod._default_log_dir = original
        logger_mod._LOG_DIR = None


# ── _FallbackBoundLogger levels ───────────────────────────────────────────────


def _make_capture_logger(name: str):
    captured = []

    class _Cap(logging.Handler):
        def emit(self, record):
            captured.append(json.loads(record.getMessage()))

    base = logging.getLogger(name)
    base.handlers = []
    base.propagate = False
    base.setLevel(logging.DEBUG)
    base.addHandler(_Cap())
    return logger_mod._FallbackBoundLogger(base), captured


def test_fallback_debug_emits_correct_level():
    log, captured = _make_capture_logger("tonesoul.test.debug")
    log.debug("debug_event", x=1)
    assert captured[0]["level"] == "debug"
    assert captured[0]["x"] == 1


def test_fallback_info_emits_correct_level():
    log, captured = _make_capture_logger("tonesoul.test.info")
    log.info("info_event")
    assert captured[0]["level"] == "info"


def test_fallback_error_emits_correct_level():
    log, captured = _make_capture_logger("tonesoul.test.error")
    log.error("error_event", code=500)
    assert captured[0]["level"] == "error"
    assert captured[0]["code"] == 500


def test_fallback_critical_emits_correct_level():
    log, captured = _make_capture_logger("tonesoul.test.critical")
    log.critical("crit_event")
    assert captured[0]["level"] == "critical"


def test_fallback_bind_does_not_mutate_original():
    log, _ = _make_capture_logger("tonesoul.test.bind")
    bound = log.bind(session="s1")
    assert "session" not in log._bindings
    assert bound._bindings["session"] == "s1"


# ── _JsonlFileHandler.close ───────────────────────────────────────────────────


def test_jsonl_handler_close_handles_no_file(tmp_path):
    handler = logger_mod._JsonlFileHandler(tmp_path)
    handler.close()  # should not raise when _file is None
