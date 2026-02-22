"""Shared WSGI entrypoint for same-origin backend aliases."""

from __future__ import annotations

import sys
from pathlib import Path

_api_root = Path(__file__).resolve().parents[2]
if str(_api_root) not in sys.path:
    sys.path.insert(0, str(_api_root))

from _shared.core import app as _core_app  # noqa: E402

_PREFIX = "/api/_backend"


class _PrefixStripMiddleware:
    def __init__(self, wsgi_app, prefix: str):
        self._wsgi_app = wsgi_app
        self._prefix = prefix

    def __call__(self, environ, start_response):
        path = str(environ.get("PATH_INFO") or "")
        if path.startswith(self._prefix):
            stripped = path[len(self._prefix) :]
            environ["PATH_INFO"] = stripped if stripped else "/"
        return self._wsgi_app(environ, start_response)


if not getattr(_core_app, "_tonesoul_same_origin_prefix_wrapped", False):
    _core_app.wsgi_app = _PrefixStripMiddleware(_core_app.wsgi_app, _PREFIX)
    setattr(_core_app, "_tonesoul_same_origin_prefix_wrapped", True)

app = _core_app

