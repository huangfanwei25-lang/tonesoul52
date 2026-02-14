"""
Legacy shim.

For backward compatibility, this entrypoint forwards to scripts/verify_fortress.py.
"""

from __future__ import annotations

import runpy
from pathlib import Path

if __name__ == "__main__":
    target = Path(__file__).resolve().parents[1] / "verify_fortress.py"
    runpy.run_path(str(target), run_name="__main__")
