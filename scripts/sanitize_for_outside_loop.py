#!/usr/bin/env python3
"""Sanitize text for outside-loop validation by flagging ToneSoul vocabulary.

The Outside Loop Test pattern (see docs/research/outside_loop_test_protocol_
2026-05-17.md) requires that text sent to a clean-context subagent does not
contain framework-internal vocabulary - otherwise the subagent will mirror
the vocabulary back instead of producing genuinely external evaluation.

This script reads a text file (or stdin), scans for occurrences of ToneSoul
vocabulary terms, and outputs:
  - A flagged version with [FLAG:term] markers
  - A summary count of flag categories
  - Suggestion for rephrasing

Usage:
    python scripts/sanitize_for_outside_loop.py input.txt
    cat input.txt | python scripts/sanitize_for_outside_loop.py -

Exit codes:
    0  no flags found
    1  flags found (text needs sanitization before outside loop test)
    2  error (file not found, etc.)
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

# ToneSoul vocabulary terms to flag.
# Each entry is (pattern, category, suggested_rephrase).
# Patterns are case-insensitive; use \b for word boundaries where applicable.
TONESOUL_VOCABULARY: list[tuple[str, str, str]] = [
    # Core framework names
    (r"\bToneSoul\b", "framework", "the framework"),
    (r"語魂", "framework", "the framework"),
    (r"\btonesoul52\b", "framework", "[repo redacted]"),
    # Substrate stack
    (r"\bSubstrate Stack\b", "theory", "the multi-layer model"),
    (r"\b基底堆疊\b", "theory", "the multi-layer model"),
    (r"\bLayer [1-7]\b", "theory", "[layer N]"),
    # Council / governance
    (r"\bCouncil\b", "internal", "multi-perspective synthesis"),
    (r"\b議會\b", "internal", "multi-perspective synthesis"),
    (r"\bVow\b", "internal", "commitment"),
    (r"\b誓詞\b", "internal", "commitment"),
    (r"\bAXIOMS\b", "internal", "core principles"),
    (r"\b公理\b", "internal", "core principles"),
    # Memory
    (r"\bcrystallizer\b", "internal", "consolidation module"),
    (r"\b結晶\b", "internal", "consolidation"),
    (r"\bhippocampus\b", "internal", "retrieval engine"),
    (r"\bdecay\.py\b", "internal", "decay module"),
    # Coined terms from 2026-05 session
    (r"認知外骨骼", "coined", "framework wrapper"),
    (r"cognitive exoskeleton", "coined", "framework wrapper"),
    (r"Outside Loop Test", "coined", "external comparison test"),
    (r"Phase [A-F]\b", "coined", "[development phase]"),
    (r"Defense Guard", "coined", "auditing component"),
    (r"Reasoning Engine", "coined", "substantive reasoning component"),
    (r"first-person addendum", "coined", "instance-level addendum"),
    (r"Honest Signal", "coined", "honesty marker"),
    (r"Cognitive Field", "coined", "interaction context"),
    (r"Meta-Experiment", "coined", "meta-level experiment"),
    (r"Uniform Noise Floor", "coined", "uniform low scores"),
    (r"Vocabulary Lock-in", "coined", "vocabulary entrenchment"),
    (r"Source Pollution Audit", "coined", "source verification"),
    (r"Vocabulary Projection Back", "coined", "vocabulary echo"),
    # ToneSoul-specific concepts
    (r"forbidden claim class", "concept", "forbidden assertion category"),
    (r"mind-reading boundary", "concept", "intent-inference limit"),
    (r"epistemic defense", "concept", "knowledge-claim defense"),
    (r"認識論防禦", "concept", "knowledge-claim defense"),
    (r"echo chamber", "concept", "feedback loop"),
    (r"迴音(室|迴圈|loop)?", "concept", "feedback loop"),
    # Recent additions
    (r"methodological agnosticism with ontological asymmetry", "coined", "agnostic stance"),
    (r"performative self-intimation", "concept", "self-awareness mechanism"),
    # MEMORY_CLUSTER_CAUTION rules
    (r"MEMORY_CLUSTER_CAUTION", "internal", "cluster verification rules"),
    (r"Rule [1-4]", "internal", "[rule N]"),
]


def scan_text(text: str) -> list[tuple[int, str, str, str]]:
    """Find all vocabulary flags in text.

    Returns list of (position, matched_text, category, suggestion).
    """
    findings: list[tuple[int, str, str, str]] = []
    for pattern, category, suggestion in TONESOUL_VOCABULARY:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            findings.append((match.start(), match.group(), category, suggestion))
    findings.sort(key=lambda x: x[0])
    return findings


def render_flagged_text(text: str, findings: list[tuple[int, str, str, str]]) -> str:
    """Insert [FLAG:term] markers at each finding position."""
    result_parts: list[str] = []
    last_end = 0
    for position, matched, _category, _suggestion in findings:
        result_parts.append(text[last_end:position])
        result_parts.append(f"[FLAG:{matched}]")
        last_end = position + len(matched)
    result_parts.append(text[last_end:])
    return "".join(result_parts)


def render_summary(findings: list[tuple[int, str, str, str]]) -> str:
    """Render summary of findings: category counts + flagged terms + suggestions."""
    if not findings:
        return "No ToneSoul vocabulary detected. Text is sanitized.\n"

    by_category = Counter(category for _, _, category, _ in findings)
    by_term: dict[str, tuple[int, str]] = {}
    for _, matched, _category, suggestion in findings:
        if matched not in by_term:
            by_term[matched] = (0, suggestion)
        count, sug = by_term[matched]
        by_term[matched] = (count + 1, sug)

    lines: list[str] = [
        f"Total flags: {len(findings)}",
        "",
        "By category:",
    ]
    for cat, count in by_category.most_common():
        lines.append(f"  {cat}: {count}")
    lines.append("")
    lines.append("Per term (count, suggestion):")
    for term, (count, suggestion) in sorted(by_term.items(), key=lambda x: -x[1][0]):
        lines.append(f"  {count}x  {term}  ->  {suggestion}")
    lines.append("")
    lines.append("Recommendation: rephrase flagged terms before sending to outside-loop subagent.")
    lines.append("Manual rephrasing preferred over auto-substitution - context matters.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "input",
        help="Input text file, or '-' for stdin",
    )
    parser.add_argument(
        "--flagged-only",
        action="store_true",
        help="Print only the flagged version, skip summary",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print only the summary, skip flagged text",
    )
    args = parser.parse_args()

    if args.input == "-":
        text = sys.stdin.read()
    else:
        path = Path(args.input)
        if not path.exists():
            print(f"Error: file not found: {path}", file=sys.stderr)
            return 2
        text = path.read_text(encoding="utf-8")

    findings = scan_text(text)

    if not args.summary_only:
        print("=== FLAGGED TEXT ===")
        print(render_flagged_text(text, findings))
        print()
    if not args.flagged_only:
        print("=== SUMMARY ===")
        print(render_summary(findings))

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
