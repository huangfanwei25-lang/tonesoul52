import json
import os
import subprocess
import sys
from dataclasses import asdict
from typing import Dict, List, Optional

from .inventory import build_inventory, entrypoints_status
from .issue_codes import IssueCode, issue
from .run_import_check import IMPORT_TARGETS, _can_import
from .seed_schema_check import check_seed_schema


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LEDGER_CANDIDATES = [
    os.path.join(REPO_ROOT, "ledger.jsonl"),
    os.path.join(REPO_ROOT, "body", "ledger", "ledger.jsonl"),
]


def _check_imports() -> List[Dict[str, object]]:
    results = []
    for target in IMPORT_TARGETS:
        res = _can_import(target)
        results.append({"target": res.target, "ok": res.ok, "error": res.error})
    return results


def _python_version() -> str:
    # Use sys.executable for security (B607 fix)
    return subprocess.check_output([sys.executable, "-V"], text=True).strip()


def _latest_seed_path(memory_root: str) -> Optional[str]:
    seeds_dir = os.path.join(memory_root, "seeds")
    if not os.path.isdir(seeds_dir):
        return None
    candidates = [
        os.path.join(seeds_dir, name)
        for name in os.listdir(seeds_dir)
        if name.endswith(".json")
    ]
    if not candidates:
        return None
    return max(candidates, key=os.path.getmtime)


def _load_ledger(path: str) -> List[Dict[str, object]]:
    entries: List[Dict[str, object]] = []
    if not path or not os.path.exists(path):
        return entries
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                entries.append({"_raw": line, "_error": "invalid_json"})
    return entries


def _extract_coverage(entry: Dict[str, object]) -> Optional[float]:
    if not isinstance(entry, dict):
        return None
    audit = entry.get("audit")
    if not isinstance(audit, dict):
        return None
    coverage = audit.get("coverage")
    if isinstance(coverage, (int, float)):
        return float(coverage)
    return None


def _find_ledger_path() -> Optional[str]:
    for path in LEDGER_CANDIDATES:
        if os.path.exists(path):
            return path
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
    values = [value for value in (_extract_coverage(entry) for entry in entries) if value is not None]
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
    except Exception as exc:
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
    memory_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "memory"))
    seed_schema = _seed_schema_status(memory_root)
    coverage_alert = _coverage_alert()
    report = {
        "workspace_root": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
        "python": _python_version(),
        "workspaces": build_inventory(),
        "entrypoints": entrypoints_status(),
        "imports": _check_imports(),
        "seed_schema": seed_schema,
        "coverage_alert": coverage_alert,
    }

    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "healthcheck.json")
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    failed = [item for item in report["imports"] if not item["ok"]]
    seed_failed = seed_schema.get("ok") is False
    if seed_schema.get("ok") is True:
        print(f"Seed schema: OK ({seed_schema.get('path')})")
    elif seed_schema.get("ok") is False:
        print(f"Seed schema: FAIL ({seed_schema.get('path')})")
        for issue in seed_schema.get("issues", []):
            print(f"- {issue}")
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
