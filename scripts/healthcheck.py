"""
System healthcheck entrypoint migrated from tonesoul/cli/run_healthcheck.py.
"""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.inventory import build_inventory, entrypoints_status  # noqa: E402
from tonesoul.issue_codes import IssueCode, issue  # noqa: E402
from tonesoul.seed_schema_check import check_seed_schema  # noqa: E402

LEDGER_CANDIDATES = [
    REPO_ROOT / "ledger.jsonl",
    REPO_ROOT / "body" / "ledger" / "ledger.jsonl",
]

IMPORT_TARGETS = [
    "tonesoul.time_island",
    "tonesoul.yss_gates",
    "tonesoul.config",
]


@dataclass
class ImportResult:
    target: str
    ok: bool
    error: Optional[str] = None


def _can_import(name: str) -> ImportResult:
    try:
        importlib.import_module(name)
        return ImportResult(target=name, ok=True)
    except Exception as exc:  # pragma: no cover - healthcheck error path
        return ImportResult(target=name, ok=False, error=str(exc))


def _check_imports() -> List[Dict[str, object]]:
    results = []
    for target in IMPORT_TARGETS:
        res = _can_import(target)
        results.append({"target": res.target, "ok": res.ok, "error": res.error})
    return results


def _python_version() -> str:
    return subprocess.check_output([sys.executable, "-V"], text=True).strip()


def _latest_seed_path(memory_root: str) -> Optional[str]:
    seeds_dir = Path(memory_root) / "seeds"
    if not seeds_dir.is_dir():
        return None
    candidates = [path for path in seeds_dir.iterdir() if path.suffix == ".json"]
    if not candidates:
        return None
    return str(max(candidates, key=lambda path: path.stat().st_mtime))


def _load_ledger(path: str) -> List[Dict[str, object]]:
    entries: List[Dict[str, object]] = []
    file_path = Path(path)
    if not file_path.exists():
        return entries
    with file_path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                entries.append({"_raw": line, "_error": "invalid_json"})
    return entries


def _extract_coverage(entry: Dict[str, object]) -> Optional[float]:
    audit = entry.get("audit")
    if not isinstance(audit, dict):
        return None
    coverage = audit.get("coverage")
    if isinstance(coverage, (int, float)):
        return float(coverage)
    return None


def _find_ledger_path() -> Optional[str]:
    for path in LEDGER_CANDIDATES:
        if path.exists():
            return str(path)
    return None


def _coverage_alert() -> Dict[str, object]:
    ledger_path = _find_ledger_path()
    if not ledger_path:
        return {
            "path": None,
            "total": 0,
            "below_full": 0,
            "missing": 0,
            "average": None,
            "minimum": None,
            "warn": False,
        }

    entries = _load_ledger(ledger_path)
    values = [
        value for value in (_extract_coverage(entry) for entry in entries) if value is not None
    ]
    below_full = sum(1 for value in values if value < 1.0)
    average = sum(values) / len(values) if values else None
    minimum = min(values) if values else None
    return {
        "path": ledger_path,
        "total": len(entries),
        "below_full": below_full,
        "missing": len(entries) - len(values),
        "average": average,
        "minimum": minimum,
        "warn": below_full > 0,
    }


def _seed_schema_status(memory_root: str) -> Dict[str, object]:
    seed_path = _latest_seed_path(memory_root)
    if not seed_path:
        return {
            "path": None,
            "ok": None,
            "issues": [issue(IssueCode.SEED_MISSING)],
        }

    try:
        with open(seed_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception as exc:  # pragma: no cover - healthcheck error path
        return {
            "path": seed_path,
            "ok": False,
            "issues": [issue(IssueCode.SEED_LOAD_FAILED, error=exc.__class__.__name__)],
        }

    issues = (
        check_seed_schema(payload)
        if isinstance(payload, dict)
        else [issue(IssueCode.SEED_PAYLOAD_INVALID)]
    )
    return {
        "path": seed_path,
        "ok": not issues,
        "issues": issues,
    }


def main() -> int:
    memory_root = str(REPO_ROOT / "tonesoul" / "memory")
    seed_schema = _seed_schema_status(memory_root)
    coverage_alert = _coverage_alert()
    report = {
        "workspace_root": str(REPO_ROOT),
        "python": _python_version(),
        "workspaces": build_inventory(),
        "entrypoints": entrypoints_status(),
        "imports": _check_imports(),
        "seed_schema": seed_schema,
        "coverage_alert": coverage_alert,
    }

    output_dir = REPO_ROOT / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "healthcheck.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    failed = [item for item in report["imports"] if not item["ok"]]
    seed_failed = seed_schema.get("ok") is False
    if seed_schema.get("ok") is True:
        print(f"Seed schema: OK ({seed_schema.get('path')})")
    elif seed_schema.get("ok") is False:
        print(f"Seed schema: FAIL ({seed_schema.get('path')})")
        for item in seed_schema.get("issues", []):
            print(f"- {item}")
    else:
        print("Seed schema: SKIP (no seeds found)")

    if coverage_alert.get("warn"):
        print(
            "Coverage alert: "
            f"{coverage_alert.get('below_full')} events below full coverage "
            f"(ledger={coverage_alert.get('path')})."
        )

    if failed or seed_failed:
        print("Healthcheck: FAIL")
        for item in failed:
            print(f"- {item['target']}: {item['error']}")
        print(f"Report: {out_path}")
        return 1

    print("Healthcheck: OK")
    print(f"Report: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
