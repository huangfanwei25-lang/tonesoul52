"""
Legacy identity heartbeat verification.

This script keeps backward compatibility with older docs/commands while
remaining safe in environments that do not have API keys configured.
"""

from __future__ import annotations

import argparse
import os
from typing import Dict

import requests

DEFAULT_URL = "https://www.moltbook.com/api/v1/heartbeat"
KEY_ENV_MAP = {
    "ToneSoul": "MOLTBOOK_API_KEY_TONESOUL",
    "Advocate": "MOLTBOOK_API_KEY_ADVOCATE",
}


def _load_keys() -> Dict[str, str]:
    keys: Dict[str, str] = {}
    for identity, env_name in KEY_ENV_MAP.items():
        keys[identity] = os.getenv(env_name, "").strip()
    return keys


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify configured Moltbook identities.")
    parser.add_argument("--url", default=DEFAULT_URL, help="Heartbeat API URL.")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout seconds.")
    parser.add_argument(
        "--strict-missing-keys",
        action="store_true",
        help="Fail when no identity keys are configured.",
    )
    args = parser.parse_args()

    keys = _load_keys()
    checked = 0
    failed = 0

    for identity, key in keys.items():
        if not key:
            print(f"[SKIP] {identity}: missing env {KEY_ENV_MAP[identity]}")
            continue
        checked += 1
        print(f"[CHECK] {identity} identity heartbeat")
        try:
            response = requests.get(
                args.url,
                headers={"Authorization": f"Bearer {key}"},
                timeout=max(1, int(args.timeout)),
            )
        except requests.RequestException as exc:
            failed += 1
            print(f"[FAIL] {identity}: request error: {exc}")
            continue

        if response.status_code != 200:
            failed += 1
            body = (response.text or "").strip()
            print(f"[FAIL] {identity}: HTTP {response.status_code} {body}")
            continue

        payload = {}
        try:
            payload = response.json()
        except ValueError:
            pass
        agent_id = payload.get("agent_id", "unknown") if isinstance(payload, dict) else "unknown"
        message = payload.get("message", "") if isinstance(payload, dict) else ""
        print(f"[PASS] {identity}: agent_id={agent_id} message={message}")

    if checked == 0:
        if args.strict_missing_keys:
            print("[FAIL] No identity keys configured.")
            return 1
        print("[SKIP] No identity keys configured; nothing to verify.")
        return 0

    if failed:
        print(f"[FAIL] Identity verification failed: {failed}/{checked}")
        return 1

    print(f"[PASS] Identity verification passed: {checked}/{checked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
