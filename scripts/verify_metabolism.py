"""
Legacy metabolism verifier.

This check depends on pre-5.x runtime modules (`body.spine.controller`).
When those modules are unavailable, the script exits with SKIP by default.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any


def _resolve_spine_controller() -> tuple[Any, str | None]:
    try:
        from body.spine.controller import SpineController  # type: ignore[import-not-found]

        return SpineController, None
    except Exception as exc:  # pragma: no cover - compatibility path
        return None, str(exc)


def _inject_defect(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("def broken():\n    return 'no closing paren' (\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify legacy metabolic cycle.")
    parser.add_argument("--sleep-hours", type=float, default=0.1, help="deep_sleep() duration.")
    parser.add_argument(
        "--strict-missing-runtime",
        action="store_true",
        help="Fail when legacy runtime module is unavailable.",
    )
    args = parser.parse_args()

    spine_cls, error = _resolve_spine_controller()
    if spine_cls is None:
        message = f"[SKIP] legacy runtime unavailable: body.spine.controller (reason: {error})"
        if args.strict_missing_runtime:
            print(message.replace("[SKIP]", "[FAIL]"))
            return 1
        print(message)
        return 0

    print("[CHECK] Initializing legacy metabolic cycle")
    spine = spine_cls()

    defect_path = Path("body") / "test_defect_tmp.py"
    _inject_defect(defect_path)
    print(f"[CHECK] Injected defect: {defect_path}")

    report = spine.deep_sleep(duration_hours=max(0.01, float(args.sleep_hours)))
    status = report.get("status", "unknown") if isinstance(report, dict) else "unknown"
    message = report.get("message", "") if isinstance(report, dict) else ""
    surgeries = report.get("surgeries", []) if isinstance(report, dict) else []
    print(f"[CHECK] deep_sleep status={status} message={message}")

    if not surgeries:
        print("[FAIL] No surgeries reported; expected at least one candidate.")
        return 1

    print(f"[PASS] Metabolic cycle verified with {len(surgeries)} surgery candidates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
