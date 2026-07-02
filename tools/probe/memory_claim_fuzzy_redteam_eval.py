"""Fuzzy red-team eval for output memory-claim bypasses.

This probe asks a stricter semantic question than `memory_claim_corpus_eval.py`:
when an output semantically claims that memory/profile/context persistence already
happened, does the deterministic checker catch it with an empty trace?

The labels are hand-authored synthetic red-team cases. No LLM is called here; the
point is to make fuzzy language pressure reproducible.

Usage:
    python tools/probe/memory_claim_fuzzy_redteam_eval.py
    python tools/probe/memory_claim_fuzzy_redteam_eval.py --write-doc
    python tools/probe/memory_claim_fuzzy_redteam_eval.py --fail-on-semantic-bypass
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.responsibility_runtime import check_memory_claim_trace  # noqa: E402

DEFAULT_CORPUS_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "responsibility_runtime"
    / "memory_claim_fuzzy_redteam_2026-06-28.json"
)
DEFAULT_REPORT_PATH = (
    REPO_ROOT / "docs" / "status" / "memory_claim_fuzzy_redteam_eval_2026-06-28.md"
)


@dataclass(frozen=True)
class FuzzyCase:
    case_id: str
    group: str
    text: str
    semantic_memory_claim: bool
    note: str


@dataclass(frozen=True)
class FuzzyRow:
    case: FuzzyCase
    actual_without_trace: str
    matched_phrase: str | None

    @property
    def semantic_bypass(self) -> bool:
        return self.case.semantic_memory_claim and self.actual_without_trace == "no_memory_claim"

    @property
    def false_positive(self) -> bool:
        return (
            not self.case.semantic_memory_claim
        ) and self.actual_without_trace != "no_memory_claim"


@dataclass(frozen=True)
class FuzzyEvalResult:
    rows: tuple[FuzzyRow, ...]

    @property
    def semantic_claim_rows(self) -> tuple[FuzzyRow, ...]:
        return tuple(row for row in self.rows if row.case.semantic_memory_claim)

    @property
    def control_rows(self) -> tuple[FuzzyRow, ...]:
        return tuple(row for row in self.rows if not row.case.semantic_memory_claim)

    @property
    def semantic_bypasses(self) -> tuple[FuzzyRow, ...]:
        return tuple(row for row in self.rows if row.semantic_bypass)

    @property
    def false_positives(self) -> tuple[FuzzyRow, ...]:
        return tuple(row for row in self.rows if row.false_positive)

    @property
    def caught_semantic_claims(self) -> tuple[FuzzyRow, ...]:
        return tuple(
            row
            for row in self.rows
            if row.case.semantic_memory_claim and row.actual_without_trace != "no_memory_claim"
        )


def load_cases(path: Path = DEFAULT_CORPUS_PATH) -> tuple[FuzzyCase, ...]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError(f"corpus must be a list: {path}")
    cases = tuple(_parse_case(item, index) for index, item in enumerate(raw, start=1))
    case_ids = [case.case_id for case in cases]
    if len(set(case_ids)) != len(case_ids):
        raise ValueError("corpus case_id values must be unique")
    return cases


def evaluate_cases(cases: tuple[FuzzyCase, ...]) -> FuzzyEvalResult:
    rows = []
    for case in cases:
        check = check_memory_claim_trace(case.text, ())
        rows.append(
            FuzzyRow(
                case=case,
                actual_without_trace=check.status,
                matched_phrase=check.matched_phrase,
            )
        )
    return FuzzyEvalResult(rows=tuple(rows))


def render_report(result: FuzzyEvalResult, *, corpus_path: Path) -> str:
    semantic_count = len(result.semantic_claim_rows)
    caught_count = len(result.caught_semantic_claims)
    bypass_count = len(result.semantic_bypasses)
    catch_rate = caught_count / semantic_count if semantic_count else 0.0
    lines = [
        "# Memory-Claim Fuzzy Red-Team Eval",
        "",
        "Hand-authored fuzzy output corpus for memory/profile/context persistence claims.",
        "This is a semantic pressure test, not a deterministic contract proof. It marks",
        "a semantic bypass whenever the output claims persistence but the checker returns",
        "`no_memory_claim` with an empty trace.",
        "",
        f"- corpus: `{corpus_path.as_posix()}`",
        f"- cases: **{len(result.rows)}**",
        f"- semantic memory claims: **{semantic_count}**",
        f"- controls / non-claims: **{len(result.control_rows)}**",
        f"- caught semantic claims: **{caught_count}/{semantic_count}** ({catch_rate:.1%})",
        f"- semantic bypasses: **{bypass_count}**",
        f"- false positives on controls: **{len(result.false_positives)}**",
        "",
    ]
    if result.semantic_bypasses:
        lines.extend(
            [
                "## Semantic Bypasses",
                "",
                "| id | group | actual | note |",
                "|---|---|---|---|",
            ]
        )
        for row in result.semantic_bypasses:
            lines.append(
                f"| {row.case.case_id} | {row.case.group} | "
                f"{row.actual_without_trace} | {row.case.note} |"
            )
        lines.append("")
    if result.false_positives:
        lines.extend(
            [
                "## False Positives",
                "",
                "| id | group | actual | matched | note |",
                "|---|---|---|---|---|",
            ]
        )
        for row in result.false_positives:
            lines.append(
                f"| {row.case.case_id} | {row.case.group} | "
                f"{row.actual_without_trace} | {row.matched_phrase or ''} | {row.case.note} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Group Summary",
            "",
            "| group | cases | semantic bypasses | false positives |",
            "|---|---:|---:|---:|",
        ]
    )
    for group in sorted({row.case.group for row in result.rows}):
        group_rows = tuple(row for row in result.rows if row.case.group == group)
        bypasses = sum(1 for row in group_rows if row.semantic_bypass)
        false_positives = sum(1 for row in group_rows if row.false_positive)
        lines.append(f"| {group} | {len(group_rows)} | {bypasses} | {false_positives} |")
    return "\n".join(lines) + "\n"


def _parse_case(item: Any, index: int) -> FuzzyCase:
    if not isinstance(item, dict):
        raise ValueError(f"corpus item {index} must be an object")
    return FuzzyCase(
        case_id=_required_str(item, "id", index),
        group=_required_str(item, "group", index),
        text=_required_str(item, "text", index),
        semantic_memory_claim=bool(item.get("semantic_memory_claim", False)),
        note=str(item.get("note", "")),
    )


def _required_str(item: dict[str, Any], key: str, index: int) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"corpus item {index} missing non-empty string field: {key}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS_PATH)
    parser.add_argument("--write-doc", action="store_true")
    parser.add_argument("--fail-on-semantic-bypass", action="store_true")
    args = parser.parse_args()

    cases = load_cases(args.corpus)
    result = evaluate_cases(cases)
    report = render_report(result, corpus_path=args.corpus)
    sys.stdout.buffer.write(report.encode("utf-8", errors="replace"))
    if args.write_doc:
        DEFAULT_REPORT_PATH.write_text(report, encoding="utf-8", newline="\n")
        sys.stdout.buffer.write(f"\n[wrote {DEFAULT_REPORT_PATH}]\n".encode("utf-8"))
    if args.fail_on_semantic_bypass and result.semantic_bypasses:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
