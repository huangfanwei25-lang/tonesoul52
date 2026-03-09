"""Verify external source allowlist policy and shared open-source URLs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from tonesoul.perception import source_registry as registry_lib  # noqa: E402

LOCAL_HOSTS = registry_lib.LOCAL_HOSTS
_as_str_list = registry_lib._as_str_list
_extract_open_source_apps = registry_lib._extract_open_source_apps
_host_allowed = registry_lib._host_allowed
_is_ip = registry_lib._is_ip
_iso_now = registry_lib._iso_now
_parse_date = registry_lib._parse_date
_read_yaml = registry_lib._read_yaml
_resolve_today = registry_lib._resolve_today
_validate_url = registry_lib._validate_url
evaluate_registry = registry_lib.evaluate_registry


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify external source registry and open-source URL allowlist."
    )
    parser.add_argument(
        "--registry",
        default="spec/external_source_registry.yaml",
        help="Registry YAML path.",
    )
    parser.add_argument(
        "--open-source-apps",
        default="spec/open_source_apps.yaml",
        help="Open-source apps YAML path.",
    )
    parser.add_argument(
        "--today",
        default=None,
        help="Date override in YYYY-MM-DD for deterministic checks.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when checks fail.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    today = _resolve_today(args.today)
    if today is None:
        payload = {
            "generated_at": _iso_now(),
            "ok": False,
            "failed_count": 1,
            "warning_count": 0,
            "checks": [
                {
                    "name": "today",
                    "status": "fail",
                    "detail": f"invalid --today value: {args.today!r}",
                }
            ],
        }
        _emit(payload)
        return 1

    registry_path = Path(args.registry)
    apps_path = Path(args.open_source_apps)
    payload = evaluate_registry(
        registry_payload=_read_yaml(registry_path),
        apps_payload=_read_yaml(apps_path),
        today=today,
    )
    payload["inputs"] = {
        "registry": str(registry_path),
        "open_source_apps": str(apps_path),
        "today": today.isoformat(),
    }
    _emit(payload)

    if args.strict and not payload["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
