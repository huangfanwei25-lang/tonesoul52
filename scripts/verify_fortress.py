"""
Legacy fortress verifier.

This check depends on pre-5.x runtime modules (`body.surgeon.sandbox`).
When those modules are unavailable, the script exits with SKIP by default.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any


def _resolve_sandbox() -> tuple[Any, str | None]:
    try:
        from body.surgeon.sandbox import Sandbox  # type: ignore[import-not-found]

        return Sandbox, None
    except Exception as exc:  # pragma: no cover - compatibility path
        return None, str(exc)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify legacy fortress sandbox behavior.")
    parser.add_argument(
        "--strict-missing-runtime",
        action="store_true",
        help="Fail when legacy runtime module is unavailable.",
    )
    args = parser.parse_args()

    sandbox_cls, error = _resolve_sandbox()
    if sandbox_cls is None:
        message = f"[SKIP] legacy runtime unavailable: body.surgeon.sandbox (reason: {error})"
        if args.strict_missing_runtime:
            print(message.replace("[SKIP]", "[FAIL]"))
            return 1
        print(message)
        return 0

    print("[CHECK] Initializing fortress stress test")
    sandbox = sandbox_cls()

    target = Path("temp") / "test_file.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("print('Hello from the Fortress')\n", encoding="utf-8")

    sandbox.setup(str(target))
    ok, log = sandbox.verify("python test_file.py")
    print(f"[CHECK] normal execution ok={ok} log={log}")
    if not ok:
        sandbox.teardown()
        print("[FAIL] Normal execution failed in sandbox.")
        return 1

    sandbox.apply_patch(str(Path(sandbox.sandbox_dir) / "test_file.py"), "while True:\n    pass\n")
    timeout_ok, timeout_log = sandbox.verify("python test_file.py", timeout=3)
    print(f"[CHECK] timeout execution ok={timeout_ok} log={timeout_log}")
    sandbox.teardown()

    if timeout_ok:
        print("[FAIL] Timeout scenario unexpectedly succeeded.")
        return 1

    print("[PASS] Fortress timeout enforcement verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
