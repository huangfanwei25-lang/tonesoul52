"""Run external source registry verification and publish status artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

JSON_FILENAME = "external_source_registry_latest.json"
MARKDOWN_FILENAME = "external_source_registry_latest.md"


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@lru_cache(maxsize=1)
def _load_verifier() -> Any:
    try:
        from scripts import verify_external_source_registry as module

        return module
    except ModuleNotFoundError:
        script_dir = Path(__file__).resolve().parent
        if str(script_dir) not in sys.path:
            sys.path.insert(0, str(script_dir))
        import verify_external_source_registry as module

        return module


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _render_markdown(payload: dict[str, Any]) -> str:
    checks = payload.get("checks", [])
    if not isinstance(checks, list):
        checks = []

    lines = [
        "# External Source Registry Latest",
        "",
        f"- generated_at: {payload.get('generated_at', '')}",
        f"- ok: {str(bool(payload.get('ok', False))).lower()}",
        f"- failed_count: {int(payload.get('failed_count', 0) or 0)}",
        f"- warning_count: {int(payload.get('warning_count', 0) or 0)}",
        "",
        "| check | status | detail |",
        "| --- | --- | --- |",
    ]
    for check in checks:
        if not isinstance(check, dict):
            continue
        name = str(check.get("name", "")).replace("|", r"\|")
        status = str(check.get("status", "")).upper().replace("|", r"\|")
        detail = str(check.get("detail", "")).replace("|", r"\|")
        lines.append(f"| {name} | {status} | {detail} |")

    failed = [
        check
        for check in checks
        if isinstance(check, dict) and str(check.get("status", "")).lower() == "fail"
    ]
    if failed:
        lines.append("")
        lines.append("## Failures")
        for item in failed:
            lines.append(f"- `{item.get('name', '')}`: {item.get('detail', '')}")

    warnings = [
        check
        for check in checks
        if isinstance(check, dict) and str(check.get("status", "")).lower() == "warn"
    ]
    if warnings:
        lines.append("")
        lines.append("## Warnings")
        for item in warnings:
            lines.append(f"- `{item.get('name', '')}`: {item.get('detail', '')}")

    return "\n".join(lines) + "\n"


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_markdown(payload), encoding="utf-8")


def run_check(
    *,
    repo_root: Path,
    registry_relpath: str,
    open_source_apps_relpath: str,
    today_override: str | None,
) -> dict[str, Any]:
    verifier = _load_verifier()
    registry_path = (repo_root / registry_relpath).resolve()
    open_source_apps_path = (repo_root / open_source_apps_relpath).resolve()

    today = verifier._resolve_today(today_override)
    if today is None:
        return {
            "generated_at": _iso_now(),
            "source": "scripts/run_external_source_registry_check.py",
            "ok": False,
            "failed_count": 1,
            "warning_count": 0,
            "checks": [
                {
                    "name": "today",
                    "status": "fail",
                    "detail": f"invalid --today value: {today_override!r}",
                }
            ],
            "inputs": {
                "registry": registry_relpath,
                "open_source_apps": open_source_apps_relpath,
                "today": today_override,
            },
        }

    payload = verifier.evaluate_registry(
        registry_payload=verifier._read_yaml(registry_path),
        apps_payload=verifier._read_yaml(open_source_apps_path),
        today=today,
    )
    payload["source"] = "scripts/run_external_source_registry_check.py"
    payload["inputs"] = {
        "registry": registry_relpath,
        "open_source_apps": open_source_apps_relpath,
        "today": today.isoformat(),
    }
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run external source registry verification and write status artifacts."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument(
        "--out-dir",
        default="docs/status",
        help="Output directory for status artifacts.",
    )
    parser.add_argument(
        "--registry",
        default="spec/external_source_registry.yaml",
        help="External source registry YAML path.",
    )
    parser.add_argument(
        "--open-source-apps",
        default="spec/open_source_apps.yaml",
        help="Open-source app list YAML path.",
    )
    parser.add_argument(
        "--today",
        default=None,
        help="Date override in YYYY-MM-DD for deterministic checks.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when validation fails.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo_root).resolve()
    out_dir = (repo_root / args.out_dir).resolve()

    payload = run_check(
        repo_root=repo_root,
        registry_relpath=args.registry,
        open_source_apps_relpath=args.open_source_apps,
        today_override=args.today,
    )

    _write_json(out_dir / JSON_FILENAME, payload)
    _write_markdown(out_dir / MARKDOWN_FILENAME, payload)
    _emit(payload)

    if args.strict and not payload.get("ok", False):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
