#!/usr/bin/env python3
"""One-time migration helper: copy file-backed state into Redis.

Usage:
    python scripts/migrate_to_redis.py
    python scripts/migrate_to_redis.py --url redis://localhost:6379/0
    python scripts/migrate_to_redis.py --dry-run

Requires a running Redis server.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import file-backed governance state and traces into Redis.",
    )
    parser.add_argument("--url", default="redis://localhost:6379/0")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def summarize_source(file_store: Any) -> dict[str, Any]:
    state = file_store.get_state()
    traces = file_store.get_traces(n=10000)
    zones = file_store.get_zones()
    return {
        "has_governance_state": bool(state),
        "trace_count": len(traces),
        "has_zones": bool(zones),
    }


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    try:
        import redis

        client = redis.from_url(args.url, socket_connect_timeout=2)
        client.ping()
        print(f"[migrate] Connected to Redis: {args.url}")
    except Exception as exc:
        print(f"[migrate] ERROR: Cannot connect to Redis: {exc}")
        print()
        print("Start Redis first:")
        print("  Windows (Scoop): scoop install redis && redis-server")
        print("  WSL:             sudo service redis-server start")
        sys.exit(1)

    from tonesoul.backends.file_store import FileStore
    from tonesoul.backends.redis_store import RedisStore

    file_store = FileStore()
    redis_store = RedisStore(client)
    summary = summarize_source(file_store)

    print("\n[migrate] Source (JSON files):")
    print(f"  governance state: {'yes' if summary['has_governance_state'] else 'empty'}")
    print(f"  session traces:   {summary['trace_count']} entries")
    print(f"  zones:            {'yes' if summary['has_zones'] else 'empty'}")

    if args.dry_run:
        print("\n[migrate] Dry run; nothing written.")
        return

    result = redis_store.import_from_file_store(file_store)
    print("\n[migrate] Imported to Redis:")
    for key, value in result.items():
        print(f"  {key}: {value}")

    print("\n[migrate] Verifying Redis keys...")
    for key in ["ts:governance", "ts:zones"]:
        exists = client.exists(key)
        print(f"  {key}: {'OK' if exists else 'MISSING'}")
    stream_len = client.xlen("ts:traces") if client.exists("ts:traces") else 0
    print(f"  ts:traces (stream): {stream_len} entries")

    print("\n[migrate] Done. Set TONESOUL_REDIS_URL to use Redis automatically:")
    print(f"  Windows: set TONESOUL_REDIS_URL={args.url}")
    print(f"  Linux:   export TONESOUL_REDIS_URL={args.url}")


if __name__ == "__main__":
    main()
