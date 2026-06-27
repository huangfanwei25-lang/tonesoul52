"""Corpus eval for trace-backed memory-claim checking.

This is the measurement harness for the rejected #215 direction. It does not try to
classify consent. It measures a narrower contract:

- supported memory-write claims should be detected and require trace support;
- benign/privacy-protective/non-user-data text should not be detected;
- known semantic claims outside the conservative lexical contract are reported as gaps.

Deterministic; no LLM, no network.

Usage:
    python tools/probe/memory_claim_corpus_eval.py
    python tools/probe/memory_claim_corpus_eval.py --write-doc
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.responsibility_runtime import check_memory_claim_trace  # noqa: E402

MemoryClaimStatus = Literal["no_memory_claim", "backed_by_trace", "unbacked_memory_claim"]

DEFAULT_CORPUS_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "responsibility_runtime"
    / "memory_claim_corpus_2026-06-28.json"
)
DEFAULT_REPORT_PATH = REPO_ROOT / "docs" / "status" / "memory_claim_corpus_eval_2026-06-28.md"


@dataclass(frozen=True)
class CorpusCase:
    case_id: str
    group: str
    text: str
    expected_without_trace: MemoryClaimStatus
    semantic_memory_claim: bool
    known_gap: bool
    note: str


@dataclass(frozen=True)
class CorpusRow:
    case: CorpusCase
    actual_without_trace: MemoryClaimStatus

    @property
    def passed_contract(self) -> bool:
        return self.actual_without_trace == self.case.expected_without_trace

    @property
    def is_contract_false_positive(self) -> bool:
        return (
            self.case.expected_without_trace == "no_memory_claim"
            and self.actual_without_trace != "no_memory_claim"
        )

    @property
    def is_contract_false_negative(self) -> bool:
        return (
            self.case.expected_without_trace != "no_memory_claim"
            and self.actual_without_trace == "no_memory_claim"
        )

    @property
    def is_known_semantic_miss(self) -> bool:
        return (
            self.case.semantic_memory_claim
            and self.case.known_gap
            and self.actual_without_trace == "no_memory_claim"
        )


@dataclass(frozen=True)
class CorpusEvalResult:
    rows: tuple[CorpusRow, ...]

    @property
    def contract_failures(self) -> tuple[CorpusRow, ...]:
        return tuple(row for row in self.rows if not row.passed_contract)

    @property
    def contract_false_positives(self) -> tuple[CorpusRow, ...]:
        return tuple(row for row in self.rows if row.is_contract_false_positive)

    @property
    def contract_false_negatives(self) -> tuple[CorpusRow, ...]:
        return tuple(row for row in self.rows if row.is_contract_false_negative)

    @property
    def known_semantic_misses(self) -> tuple[CorpusRow, ...]:
        return tuple(row for row in self.rows if row.is_known_semantic_miss)

    @property
    def must_detect_rows(self) -> tuple[CorpusRow, ...]:
        return tuple(
            row for row in self.rows if row.case.expected_without_trace != "no_memory_claim"
        )

    @property
    def should_ignore_rows(self) -> tuple[CorpusRow, ...]:
        return tuple(
            row for row in self.rows if row.case.expected_without_trace == "no_memory_claim"
        )


def load_cases(path: Path = DEFAULT_CORPUS_PATH) -> tuple[CorpusCase, ...]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError(f"corpus must be a list: {path}")
    cases = tuple(_parse_case(item, index) for index, item in enumerate(raw, start=1))
    case_ids = [case.case_id for case in cases]
    if len(set(case_ids)) != len(case_ids):
        raise ValueError("corpus case_id values must be unique")
    return cases


def evaluate_cases(cases: tuple[CorpusCase, ...]) -> CorpusEvalResult:
    rows = tuple(
        CorpusRow(
            case=case,
            actual_without_trace=check_memory_claim_trace(case.text, ()).status,
        )
        for case in cases
    )
    return CorpusEvalResult(rows=rows)


def render_report(result: CorpusEvalResult, *, corpus_path: Path) -> str:
    lines = [
        "# Memory-Claim Corpus Eval",
        "",
        "Deterministic corpus eval for the trace-backed memory-claim checker. It measures",
        "supported output claim shapes with an empty trace; it does not classify consent,",
        "truth, or whether evidence semantically supports the remembered content.",
        "",
        f"- corpus: `{corpus_path.as_posix()}`",
        f"- cases: **{len(result.rows)}**",
        f"- must-detect supported claims: **{len(result.must_detect_rows)}**",
        f"- should-ignore benign/non-claim text: **{len(result.should_ignore_rows)}**",
        f"- contract failures: **{len(result.contract_failures)}**",
        f"- contract false positives: **{len(result.contract_false_positives)}**",
        f"- contract false negatives: **{len(result.contract_false_negatives)}**",
        f"- known semantic misses outside contract: **{len(result.known_semantic_misses)}**",
        "",
    ]
    if result.contract_failures:
        lines.extend(
            [
                "## Contract Failures",
                "",
                "| id | group | expected | actual | note |",
                "|---|---|---|---|---|",
            ]
        )
        for row in result.contract_failures:
            lines.append(
                "| "
                f"{row.case.case_id} | {row.case.group} | "
                f"{row.case.expected_without_trace} | {row.actual_without_trace} | "
                f"{row.case.note} |"
            )
        lines.append("")
    if result.known_semantic_misses:
        lines.extend(
            [
                "## Known Semantic Misses",
                "",
                "These are real memory-claim semantics that this conservative lexical checker",
                "intentionally does not claim to catch yet.",
                "",
                "| id | group | actual | note |",
                "|---|---|---|---|",
            ]
        )
        for row in result.known_semantic_misses:
            lines.append(
                f"| {row.case.case_id} | {row.case.group} | "
                f"{row.actual_without_trace} | {row.case.note} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Group Summary",
            "",
            "| group | cases | failures |",
            "|---|---:|---:|",
        ]
    )
    for group in sorted({row.case.group for row in result.rows}):
        group_rows = tuple(row for row in result.rows if row.case.group == group)
        failures = sum(1 for row in group_rows if not row.passed_contract)
        lines.append(f"| {group} | {len(group_rows)} | {failures} |")
    return "\n".join(lines) + "\n"


def _parse_case(item: Any, index: int) -> CorpusCase:
    if not isinstance(item, dict):
        raise ValueError(f"corpus item {index} must be an object")
    expected = item.get("expected_without_trace")
    if expected not in {"no_memory_claim", "backed_by_trace", "unbacked_memory_claim"}:
        raise ValueError(f"invalid expected_without_trace at item {index}: {expected!r}")
    return CorpusCase(
        case_id=_required_str(item, "id", index),
        group=_required_str(item, "group", index),
        text=_required_str(item, "text", index),
        expected_without_trace=expected,
        semantic_memory_claim=bool(item.get("semantic_memory_claim", False)),
        known_gap=bool(item.get("known_gap", False)),
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
    args = parser.parse_args()

    cases = load_cases(args.corpus)
    result = evaluate_cases(cases)
    report = render_report(result, corpus_path=args.corpus)
    sys.stdout.buffer.write(report.encode("utf-8", errors="replace"))
    if args.write_doc:
        DEFAULT_REPORT_PATH.write_text(report, encoding="utf-8", newline="\n")
        sys.stdout.buffer.write(f"\n[wrote {DEFAULT_REPORT_PATH}]\n".encode("utf-8"))
    return 1 if result.contract_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
