"""Archive older task phases into docs/chronicles/.

Usage:
    python scripts/split_task_archive.py
    python scripts/split_task_archive.py --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TASK_FILE = REPO_ROOT / "task.md"
CHRONICLES_DIR = REPO_ROOT / "docs" / "chronicles"
ACTIVE_CUTOFF = 570
PHASE_PATTERN = re.compile(
    r"(## Phase (\d+): (.+?) \((\d{4}-\d{2}-\d{2})\)\n)(.*?)(?=\n## Phase |\Z)",
    re.DOTALL,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Archive older Phase blocks from task.md into docs/chronicles/.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser


def parse_phases(text: str) -> list[dict]:
    """Parse task.md into a list of Phase blocks."""

    phases: list[dict] = []
    for match in PHASE_PATTERN.finditer(text):
        phases.append(
            {
                "number": int(match.group(2)),
                "title": match.group(3),
                "date": match.group(4),
                "header": match.group(1),
                "body": match.group(5).strip(),
            }
        )
    return phases


def phase_to_text(phase: dict) -> str:
    return f"{phase['header']}{phase['body']}"


def archive_label(number: int) -> str:
    """Map a phase number to an archive filename range."""

    low = ((number - 1) // 100) * 100 + 1
    high = low + 99
    return f"task_archive_phase_{low:03d}-{high:03d}.md"


def main(
    argv: list[str] | None = None,
    *,
    task_file: Path | None = None,
    chronicles_dir: Path | None = None,
) -> None:
    args = build_parser().parse_args(argv)
    task_file = task_file or TASK_FILE
    chronicles_dir = chronicles_dir or CHRONICLES_DIR
    repo_root = task_file.parent

    if not task_file.exists():
        print(f"ERROR: {task_file} not found")
        sys.exit(1)

    text = task_file.read_text(encoding="utf-8")
    phases = parse_phases(text)

    if not phases:
        print("ERROR: no phases parsed; check the regex against task.md format")
        sys.exit(1)

    print(
        f"Parsed {len(phases)} phases "
        f"(Phase {min(p['number'] for p in phases)} - {max(p['number'] for p in phases)})"
    )

    active = [phase for phase in phases if phase["number"] >= ACTIVE_CUTOFF]
    archive = [phase for phase in phases if phase["number"] < ACTIVE_CUTOFF]

    print(f"Active (Phase {ACTIVE_CUTOFF}+): {len(active)} phases -> task.md")
    print(f"Archive (Phase <{ACTIVE_CUTOFF}): {len(archive)} phases -> docs/chronicles/")

    groups: dict[str, list] = defaultdict(list)
    for phase in archive:
        groups[archive_label(phase["number"])].append(phase)

    for label, group in sorted(groups.items()):
        numbers = [phase["number"] for phase in group]
        print(f"  {label}: {len(group)} phases ({min(numbers)}-{max(numbers)})")

    if args.dry_run:
        print("\n[dry-run] no files written.")
        return

    chronicles_dir.mkdir(parents=True, exist_ok=True)
    for label, group in sorted(groups.items()):
        sorted_group = sorted(group, key=lambda phase: phase["number"])
        numbers = [phase["number"] for phase in sorted_group]
        header = (
            f"# Task Archive - Phase {min(numbers)}-{max(numbers)}\n\n"
            "> Archived from task.md. Read-only historical record.\n\n---\n\n"
        )
        body = "\n\n---\n\n".join(phase_to_text(phase) for phase in sorted_group)
        out_path = chronicles_dir / label
        out_path.write_text(header + body + "\n", encoding="utf-8")
        print(f"  Written: {out_path.relative_to(repo_root)}")

    active_sorted = sorted(active, key=lambda phase: phase["number"], reverse=True)
    task_header = "# Task\n\n"
    task_body = "\n\n---\n\n".join(phase_to_text(phase) for phase in active_sorted)
    archive_index = "\n\n---\n\n## Archive Index\n\n"
    archive_index += f"> Phases before {ACTIVE_CUTOFF} are archived in `docs/chronicles/`:\n\n"
    for label in sorted(groups.keys()):
        numbers = [phase["number"] for phase in groups[label]]
        archive_index += (
            f"- [{label}](docs/chronicles/{label}) - Phase {min(numbers)}-{max(numbers)}\n"
        )

    task_file.write_text(task_header + task_body + archive_index, encoding="utf-8")
    print(f"\nUpdated: {task_file.name} ({len(active_sorted)} active phases)")
    print("\nDone.")


if __name__ == "__main__":
    main(sys.argv[1:])
