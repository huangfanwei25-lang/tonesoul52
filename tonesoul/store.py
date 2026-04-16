"""ToneSoul Storage Abstraction Layer.

Auto-selects backend:
  - RedisStore  if Redis is reachable at TONESOUL_REDIS_URL (default redis://localhost:6379/0)
  - FileStore   otherwise (JSON files — current behavior, always works)

Usage:
    from tonesoul.store import get_store
    store = get_store()
    state = store.get_state()
    store.set_state(state)
    store.append_trace(trace_dict)

Pub/sub (Redis only — FileStore silently skips):
    store.publish("governance:updated", {"session_count": 5})
    for msg in store.subscribe("governance:updated"):
        print(msg)
"""

from __future__ import annotations

import os
import threading

# ---------------------------------------------------------------------------
# Redis key / channel constants — canonical source: tonesoul.store_keys
# Re-exported here for backward compatibility.
# ---------------------------------------------------------------------------
from tonesoul.store_keys import (  # noqa: F401 — re-export
    CHANNEL_EVENTS,
    CHECKPOINT_PREFIX,
    COMMIT_LOCK_KEY,
    FIELD_KEY,
    KEY_COMPACTED,
    KEY_COUNCIL_VERDICTS,
    KEY_GOVERNANCE,
    KEY_ROUTING_EVENTS,
    KEY_SUBJECT_SNAPSHOTS,
    KEY_ZONES,
    LOCK_PREFIX,
    OBSERVER_CURSOR_PREFIX,
    PERSPECTIVE_PREFIX,
    STREAM_TRACES,
)

# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

_store_singleton = None
_store_lock = threading.Lock()
_DISABLED_REDIS_URL_VALUES = frozenset({"", "0", "off", "disabled", "none", "false", "file"})


def _env_truthy(name: str) -> bool:
    value = str(os.environ.get(name, "")).strip().lower()
    return value in {"1", "true", "yes", "on"}


def _redis_disabled(url: str | None) -> bool:
    if url is None:
        return False
    return str(url).strip().lower() in _DISABLED_REDIS_URL_VALUES


def get_store(redis_url: str | None = None, *, force_file: bool = False):
    """Return the singleton store (auto-detected backend).

    Args:
        redis_url:  Override TONESOUL_REDIS_URL env var.
        force_file: Always use FileStore (useful in tests).
    """
    global _store_singleton
    if _store_singleton is not None:
        return _store_singleton

    with _store_lock:
        # Double-check after acquiring lock
        if _store_singleton is not None:
            return _store_singleton

        if force_file or _env_truthy("TONESOUL_FORCE_FILE_STORE"):
            _store_singleton = _make_file_store()
            return _store_singleton

        url = redis_url or os.environ.get("TONESOUL_REDIS_URL", "redis://localhost:6379/0")
        if _redis_disabled(url):
            _store_singleton = _make_file_store()
            return _store_singleton
        _store_singleton = _try_redis(url) or _make_file_store()
        return _store_singleton


def reset_store() -> None:
    """Reset singleton (for tests)."""
    global _store_singleton
    with _store_lock:
        _store_singleton = None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _try_redis(url: str):
    """Try to connect to Redis. Return RedisStore or None."""
    try:
        import redis as _redis

        client = _redis.from_url(url, socket_connect_timeout=0.5, socket_timeout=0.5)
        client.ping()
    except Exception:
        return None

    try:
        from tonesoul.backends.redis_store import RedisStore

        store = RedisStore(client)
        print(f"[ToneSoul] Storage: Redis ({url})")
        return store
    except Exception:
        return None


def _make_file_store():
    from tonesoul.backends.file_store import FileStore

    print("[ToneSoul] Storage: FileStore (Redis not available)")
    return FileStore()
