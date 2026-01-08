import importlib
import os
import sys
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ImportResult:
    target: str
    ok: bool
    error: Optional[str] = None


WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

IMPORT_TARGETS = [
    "body.dashboard.app",
    "body.spine.controller",
    "yuhun_cli",
    "body.llm_bridge",
    "body.rag_engine",
]


def _can_import(name: str) -> ImportResult:
    try:
        importlib.import_module(name)
        return ImportResult(target=name, ok=True)
    except Exception as exc:
        return ImportResult(target=name, ok=False, error=str(exc))


def main() -> int:
    results: List[ImportResult] = []
    for target in IMPORT_TARGETS:
        results.append(_can_import(target))

    failed = [r for r in results if not r.ok]
    for result in results:
        status = "OK" if result.ok else "FAIL"
        if result.ok:
            print(f"{status}: {result.target}")
        else:
            print(f"{status}: {result.target} -> {result.error}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
