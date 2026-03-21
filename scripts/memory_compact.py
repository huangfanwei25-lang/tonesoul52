"""
Memory compaction entrypoint migrated from tonesoul/cli/run_memory_compact.py.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.memory_manager import archive_runs, build_indexes, collect_run_dirs  # noqa: E402


def _workspace_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tonesoul"))


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compact run history and rebuild memory indexes.")
    parser.add_argument(
        "--run-root",
        help="Run directory root to compact (default: 5.2/run/execution).",
    )
    parser.add_argument(
        "--archive-root",
        help="Archive destination for older runs (default: archive/runs).",
    )
    parser.add_argument(
        "--memory-root",
        help="Memory root (default: 5.2/memory).",
    )
    parser.add_argument(
        "--keep-latest",
        type=int,
        default=3,
        help="Number of newest runs to keep in run root.",
    )
    parser.add_argument(
        "--reindex-only",
        action="store_true",
        help="Skip archiving and only rebuild indexes.",
    )
    parser.add_argument(
        "--skip-archive-index",
        action="store_true",
        help="Exclude archived runs from index rebuild.",
    )
    return parser


def main() -> Dict[str, object]:
    parser = build_arg_parser()
    args = parser.parse_args()

    workspace = _workspace_root()
    run_root = os.path.abspath(args.run_root or os.path.join(workspace, "run", "execution"))
    archive_root = os.path.abspath(
        args.archive_root or os.path.join(workspace, "..", "archive", "runs")
    )
    memory_root = os.path.abspath(args.memory_root or os.path.join(workspace, "memory"))

    archived: List[str] = []
    if not args.reindex_only:
        archived = archive_runs(run_root, archive_root, keep_latest=args.keep_latest)

    run_roots = [run_root]
    if not args.skip_archive_index and os.path.isdir(archive_root):
        run_roots.append(archive_root)
    run_dirs = collect_run_dirs(run_roots)

    indexes = build_indexes(
        run_dirs,
        memory_root=memory_root,
        archive_root=archive_root,
    )
    return {
        "archived_count": len(archived),
        "archived_paths": archived,
        "indexed_runs": len(run_dirs),
        **indexes,
    }


if __name__ == "__main__":
    result = main()
    print(f"archived_count: {result['archived_count']}")
    print(f"indexed_runs: {result['indexed_runs']}")
    print(f"graph: {result['graph']}")
    print(f"run_index: {result['run_index']}")
