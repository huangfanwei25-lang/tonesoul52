"""
Safe import-only smoke test for YuHun CLI.
- Verifies imports and class initialization.
- Does not enter interactive loop.
"""

import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


def main() -> int:
    try:
        from yuhun_cli import YuHunCLI  # noqa: F401
    except Exception as exc:
        print(f"Import failed: {exc}")
        return 1

    try:
        _cli = YuHunCLI(verbose=False)
    except Exception as exc:
        print(f"Initialization failed: {exc}")
        return 1

    print("YuHun CLI import and init succeeded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
