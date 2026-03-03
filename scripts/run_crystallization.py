"""
Run memory crystallization on real journal data.

Steps:
1. Force consolidation (episodic -> semantic)
2. Crystallize patterns into decision rules
3. Compare crystals against Three Axioms
4. Write report

Usage:
    python scripts/run_crystallization.py [--min-frequency 2]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from memory.consolidator import MemoryConsolidator, force_consolidate  # noqa: E402
from tonesoul.memory.crystallizer import Crystal, MemoryCrystallizer  # noqa: E402
from tonesoul.memory.soul_db import JsonlSoulDB, MemorySource  # noqa: E402

THREE_AXIOMS = [
    "Resonance: respond to user semantic field without faking human emotion",
    "Commitment: every output is a semantic vow, track consistency",
    "Binding Force: outputs constrain future semantic field",
]

AXIOM_TAG_HINTS: Dict[str, List[str]] = {
    "Resonance": ["prefer", "stability", "attention", "autonomous"],
    "Commitment": ["verdict", "avoid", "approve", "block"],
    "Binding Force": ["critical", "collapse_warning", "safety"],
}


class _NoOpHippocampus:
    def memorize(self, **_kwargs: object) -> None:
        return None


def _configure_utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def _count_nonempty_lines(path: Path) -> int:
    if not path.exists() or not path.is_file():
        return 0
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for line in handle if line.strip())


def _load_all_journal_payloads() -> List[Dict[str, Any]]:
    db = JsonlSoulDB()
    payloads: List[Dict[str, Any]] = []
    for record in db.stream(MemorySource.SELF_JOURNAL, limit=None):
        if isinstance(record.payload, dict):
            payloads.append(record.payload)
    return payloads


def _extract_patterns_from_full_journal(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    consolidator = MemoryConsolidator(hippocampus=_NoOpHippocampus())
    return consolidator._extract_patterns(entries)  # noqa: SLF001 - explicit offline report use


def _align_axioms(crystals: Iterable[Crystal]) -> Dict[str, List[Crystal]]:
    result: Dict[str, List[Crystal]] = {axiom: [] for axiom in THREE_AXIOMS}
    crystal_list = list(crystals)
    for axiom in THREE_AXIOMS:
        head = axiom.split(":", 1)[0].strip()
        hints = AXIOM_TAG_HINTS.get(head, [])
        for crystal in crystal_list:
            tags_lower = [t.lower() for t in crystal.tags]
            if any(h in tags_lower for h in hints):
                result[axiom].append(crystal)
    return result


def _compact_json(payload: Any, limit: int = 1200) -> str:
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    return text if len(text) <= limit else f"{text[:limit]}..."


def _run_consolidation() -> tuple[Dict[str, Any], str, str | None]:
    try:
        result = force_consolidate()
        return (result if isinstance(result, dict) else {}), "force_consolidate", None
    except Exception as exc:  # pragma: no cover - runtime fallback for local data issues
        fallback = MemoryConsolidator(hippocampus=_NoOpHippocampus())
        result = fallback.consolidate(force=True)
        return (
            result if isinstance(result, dict) else {},
            "fallback_noop_hippocampus",
            f"{type(exc).__name__}: {exc}",
        )


def main() -> None:
    _configure_utf8_stdio()
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-frequency", type=int, default=2)
    parser.add_argument("--output", type=str, default="docs/status/crystallization_report.md")
    args = parser.parse_args()

    started_at = (
        datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )
    journal_path = Path("memory/self_journal.jsonl")
    journal_entries = _count_nonempty_lines(journal_path)

    print("Running memory consolidation...")
    consolidation_result, consolidation_mode, consolidation_error = _run_consolidation()
    print(f"Consolidation done. mode={consolidation_mode}")
    if consolidation_error:
        print(f"  Force consolidation failed, fallback used: {consolidation_error}")

    print("Extracting full-journal patterns...")
    full_entries = _load_all_journal_payloads()
    full_patterns = _extract_patterns_from_full_journal(full_entries)
    print(f"  Loaded journal payloads: {len(full_entries)}")

    print("Running crystallization...")
    crystallizer = MemoryCrystallizer(min_frequency=args.min_frequency)
    crystals = crystallizer.crystallize(full_patterns)
    print(f"  Crystals generated this run: {len(crystals)}")
    for crystal in crystals:
        print(f"    [{','.join(crystal.tags)}] {crystal.rule} (w={crystal.weight:.2f})")

    all_crystals = crystallizer.load_crystals()
    print(f"Total crystals in store: {len(all_crystals)}")

    alignment = _align_axioms(crystals if crystals else all_crystals)

    report_path = Path(args.output)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []
    lines.append("# Crystallization Report")
    lines.append("")
    lines.append(f"- Date (UTC): {started_at}")
    lines.append(f"- Journal entries scanned: {journal_entries}")
    lines.append(f"- Journal payloads parsed by SoulDB: {len(full_entries)}")
    lines.append(f"- Min frequency: {args.min_frequency}")
    lines.append("")
    lines.append("## Consolidation")
    lines.append("- Type: `force_consolidate()`")
    lines.append(f"- Mode used: `{consolidation_mode}`")
    if consolidation_error:
        lines.append(f"- Force-consolidate error: `{consolidation_error}`")
    lines.append(f"- Result snapshot:\n```json\n{_compact_json(consolidation_result)}\n```")
    lines.append("")
    lines.append(f"## Crystals Generated This Run: {len(crystals)}")
    if crystals:
        for crystal in crystals:
            lines.append(f"- **[{crystal.weight:.2f}]** {crystal.rule}")
            lines.append(f"  - Source: `{crystal.source_pattern}`")
            lines.append(f"  - Tags: {', '.join(crystal.tags) if crystal.tags else '(none)'}")
    else:
        lines.append("- No new crystals generated in this run.")
    lines.append("")
    lines.append("## Three Axioms Alignment Check")
    for axiom in THREE_AXIOMS:
        lines.append(f"- {axiom}")
        matched = alignment.get(axiom, [])
        if matched:
            for crystal in matched:
                lines.append(f"  - PASS: {crystal.rule}")
        else:
            lines.append("  - WARN: No crystal directly aligned")
    lines.append("")
    lines.append(f"## Total Crystal Store: {len(all_crystals)}")
    if all_crystals:
        top = sorted(all_crystals, key=lambda c: (c.weight, c.access_count), reverse=True)[:5]
        lines.append("### Top Crystal Rules")
        for crystal in top:
            lines.append(f"- [{crystal.weight:.2f}] {crystal.rule}")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report written to {report_path}")


if __name__ == "__main__":
    main()
