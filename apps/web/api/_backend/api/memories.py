"""Same-origin backend alias endpoint."""

from __future__ import annotations

import sys
from pathlib import Path

for _root in Path(__file__).resolve().parents:
    if (_root / "_backend" / "_shared" / "entrypoint.py").is_file():
        if str(_root) not in sys.path:
            sys.path.insert(0, str(_root))
        break

from _backend._shared.entrypoint import app  # noqa: E402,F401

