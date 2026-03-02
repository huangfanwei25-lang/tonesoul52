"""
Ingest AI-to-AI handoff files into SoulDB.

Usage:
    python scripts/ingest_handoffs.py [--since YYYY-MM-DD]
"""

import argparse
from pathlib import Path

from tonesoul.memory.handoff_ingester import HandoffIngester
from tonesoul.memory.soul_db import JsonlSoulDB


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest handoff files into SoulDB")
    parser.add_argument("--since", type=str, default=None, help="Only ingest after this ISO date")
    parser.add_argument("--handoff-dir", type=str, default="memory/handoff")
    parser.add_argument("--sync-md", type=str, default="memory/ANTIGRAVITY_SYNC.md")
    args = parser.parse_args()

    db = JsonlSoulDB()
    ingester = HandoffIngester(db)

    # Ingest handoff dir
    dir_result = ingester.ingest_handoff_dir(
        Path(args.handoff_dir),
        since=args.since,
    )
    print(f"Handoff dir: {dir_result}")

    # Ingest sync md
    sync_path = Path(args.sync_md)
    if sync_path.exists():
        sync_result = ingester.ingest_sync_md(sync_path)
        print(f"Sync MD: {sync_result}")


if __name__ == "__main__":
    main()
