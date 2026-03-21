from __future__ import annotations

import contextlib
import importlib.util
import os
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))


def _load_host_tick_module():
    path = repo_root / "scripts" / "run_true_verification_host_tick.py"
    spec = importlib.util.spec_from_file_location(
        "run_true_verification_host_tick_script",
        path,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv: list[str] | None = None) -> int:
    args = list(argv) if argv is not None else list(sys.argv[1:])
    sink_path = Path(os.devnull)
    with sink_path.open("w", encoding="utf-8", errors="replace") as sink:
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            module = _load_host_tick_module()
            return int(module.main(args))


if __name__ == "__main__":
    raise SystemExit(main())
