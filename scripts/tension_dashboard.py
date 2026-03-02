"""
ToneSoul Tension Dashboard - CLI observability tool.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.memory.crystallizer import MemoryCrystallizer
from tonesoul.work_classifier import WorkCategory, get_profile


def _count_lines(path: Path) -> int:
    if not path.exists() or not path.is_file():
        return 0
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for _ in handle)


def _count_files(path: Path) -> int:
    if not path.exists() or not path.is_dir():
        return 0
    return sum(1 for p in path.rglob("*") if p.is_file())


def _load_calibration_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists() or not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _to_float(value: object) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _gamma_range(rows: Iterable[Dict[str, str]]) -> Tuple[Optional[float], Optional[float]]:
    values = []
    for row in rows:
        gamma = _to_float(row.get("gamma_eff"))
        if gamma is not None:
            values.append(gamma)
    if not values:
        return None, None
    return min(values), max(values)


def _find_compression(
    rows: Iterable[Dict[str, str]],
    *,
    category: str,
    zone: str,
    lambda_state: str,
    trend: str,
) -> Optional[float]:
    for row in rows:
        if (
            str(row.get("category", "")).strip().lower() == category
            and str(row.get("zone", "")).strip().lower() == zone
            and str(row.get("lambda", "")).strip().lower() == lambda_state
            and str(row.get("trend", "")).strip().lower() == trend
        ):
            return _to_float(row.get("compression_ratio"))
    return None


def _box_line(text: str, width: int = 55) -> str:
    clipped = text[: width - 4]
    return f"| {clipped.ljust(width - 4)} |"


def _render_dashboard(work_category: WorkCategory) -> str:
    profile = get_profile(work_category)
    crystals = MemoryCrystallizer().top_crystals(n=5)
    journal_count = _count_lines(Path("memory/self_journal.jsonl"))
    handoff_count = _count_files(Path("memory/handoff"))
    crystals_count = len(crystals)

    calibration_rows = _load_calibration_rows(Path("docs/status/rfc013_calibration.csv"))
    gamma_min, gamma_max = _gamma_range(calibration_rows)
    freeform_safe = _find_compression(
        calibration_rows,
        category="freeform",
        zone="safe",
        lambda_state="convergent",
        trend="stable",
    )
    debug_danger_chaotic = _find_compression(
        calibration_rows,
        category="debug",
        zone="danger",
        lambda_state="chaotic",
        trend="chaotic",
    )

    lines = []
    lines.append("+" + "-" * 55 + "+")
    lines.append(_box_line("ToneSoul Tension Dashboard"))
    lines.append("+" + "-" * 55 + "+")
    lines.append(
        _box_line(
            f"Work Category: {work_category.value.upper()} (gamma={profile.gamma_base:.1f})"
        )
    )
    lines.append(_box_line(f"Active Crystals: {crystals_count}"))
    for crystal in crystals[:3]:
        tag = crystal.tags[0] if crystal.tags else "rule"
        lines.append(_box_line(f"  - {tag}: {crystal.rule[:28]} (w={crystal.weight:.2f})"))
    if not crystals:
        lines.append(_box_line("  - none"))
    lines.append(_box_line("Memory Stats:"))
    lines.append(_box_line(f"  journal: {journal_count:,} entries"))
    lines.append(_box_line(f"  handoffs: {handoff_count:,} files"))
    lines.append(_box_line(f"  crystals: {crystals_count} active rules"))
    lines.append(_box_line("Calibration Matrix:"))
    if gamma_min is not None and gamma_max is not None:
        lines.append(_box_line(f"  current gamma_eff range: [{gamma_min:.2f}, {gamma_max:.2f}]"))
    else:
        lines.append(_box_line("  current gamma_eff range: [n/a, n/a]"))
    lines.append(
        _box_line(
            "  freeform safe: "
            + (f"{freeform_safe:.2f}" if freeform_safe is not None else "n/a")
        )
    )
    lines.append(
        _box_line(
            "  debug danger chaotic: "
            + (f"{debug_danger_chaotic:.2f}" if debug_danger_chaotic is not None else "n/a")
        )
    )
    lines.append("+" + "-" * 55 + "+")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="ToneSoul Tension Dashboard")
    parser.add_argument(
        "--work-category",
        type=str,
        default=WorkCategory.ENGINEERING.value,
        choices=[c.value for c in WorkCategory],
        help="Work category profile used for dashboard summary.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit summary as JSON instead of ASCII dashboard.",
    )
    args = parser.parse_args()

    category = WorkCategory(args.work_category.strip().lower())
    if args.json:
        payload = {"work_category": category.value, "dashboard": _render_dashboard(category)}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print(_render_dashboard(category))


if __name__ == "__main__":
    main()
