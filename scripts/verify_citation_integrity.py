"""
Citation integrity verifier.

Checks three rules:
1. Philosophy docs can cite arXiv, but must mark preprints as concept-only.
2. Known arXiv ids must match expected paper titles.
3. Mainline governance/architecture docs must avoid direct arXiv citations.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

CONCEPT_MARKER = "Concept / Not peer-reviewed"

DEFAULT_PHILOSOPHY_PATHS = (
    "docs/PHILOSOPHY.md",
    "docs/PHILOSOPHY_EN.md",
)

DEFAULT_MAINLINE_PATHS = (
    "docs/ARCHITECTURE_BOUNDARIES.md",
    "docs/7D_AUDIT_FRAMEWORK.md",
    "docs/7D_EXECUTION_SPEC.md",
    "docs/AUDIT_CONTRACT.md",
    "docs/SECURITY_AUDIT_2025.md",
)

EXPECTED_ARXIV_TITLES = {
    "2512.24601": "Recursive Language Models",
    "2305.19118": "Encouraging Divergent Thinking in Large Language Models through Multi-Agent Debate",
}

ARXIV_ID_RE = re.compile(r"arXiv:(?P<arxiv>\d{4}\.\d{5})", flags=re.IGNORECASE)
ARXIV_REF_RE = re.compile(
    r"\*(?P<title>[^*]+)\*.*?arXiv:(?P<arxiv>\d{4}\.\d{5})",
    flags=re.IGNORECASE,
)


def _read_text(path: Path) -> str:
    data = path.read_bytes()
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace")


def _normalize_title(title: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "", title.lower())
    return normalized


def _relative(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def _extract_arxiv_entries(text: str) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or "arXiv:" not in line:
            continue
        title_match = ARXIV_REF_RE.search(line)
        if title_match:
            entries.append(
                {
                    "line": line_number,
                    "arxiv_id": title_match.group("arxiv"),
                    "title": title_match.group("title").strip(),
                    "line_text": raw_line,
                }
            )
            continue
        id_match = ARXIV_ID_RE.search(line)
        if id_match:
            entries.append(
                {
                    "line": line_number,
                    "arxiv_id": id_match.group("arxiv"),
                    "title": None,
                    "line_text": raw_line,
                }
            )
    return entries


def build_report(
    repo_root: Path,
    *,
    philosophy_paths: Iterable[str],
    mainline_paths: Iterable[str],
) -> dict[str, object]:
    issues: list[str] = []
    warnings: list[str] = []
    scanned_files = 0
    philosophy_entries = 0
    mainline_entries = 0

    for rel_path in philosophy_paths:
        path = repo_root / rel_path
        if not path.exists():
            warnings.append(f"missing philosophy file: {rel_path}")
            continue
        scanned_files += 1
        entries = _extract_arxiv_entries(_read_text(path))
        philosophy_entries += len(entries)
        for entry in entries:
            line_text = str(entry["line_text"])
            arxiv_id = str(entry["arxiv_id"])
            title = entry["title"]
            line_number = int(entry["line"])
            display = f"{_relative(path, repo_root)}:{line_number}"
            is_reference_entry = bool(re.match(r"^\s*\d+\.", line_text)) or isinstance(title, str)

            if is_reference_entry and CONCEPT_MARKER not in line_text:
                issues.append(f"{display} missing '{CONCEPT_MARKER}' marker for arXiv:{arxiv_id}")

            expected_title = EXPECTED_ARXIV_TITLES.get(arxiv_id)
            if expected_title is None:
                continue
            if not is_reference_entry:
                continue
            if not isinstance(title, str) or not title.strip():
                issues.append(f"{display} cannot parse title for arXiv:{arxiv_id}")
                continue
            if _normalize_title(title) != _normalize_title(expected_title):
                issues.append(
                    f"{display} title mismatch for arXiv:{arxiv_id} "
                    f"(expected '{expected_title}', got '{title}')"
                )

    for rel_path in mainline_paths:
        path = repo_root / rel_path
        if not path.exists():
            warnings.append(f"missing mainline file: {rel_path}")
            continue
        scanned_files += 1
        entries = _extract_arxiv_entries(_read_text(path))
        mainline_entries += len(entries)
        for entry in entries:
            line_number = int(entry["line"])
            arxiv_id = str(entry["arxiv_id"])
            display = f"{_relative(path, repo_root)}:{line_number}"
            issues.append(
                f"{display} mainline docs should not directly cite arXiv preprints "
                f"(found arXiv:{arxiv_id})"
            )

    return {
        "overall_ok": len(issues) == 0,
        "metrics": {
            "scanned_files": scanned_files,
            "philosophy_arxiv_entries": philosophy_entries,
            "mainline_arxiv_entries": mainline_entries,
            "issue_count": len(issues),
            "warning_count": len(warnings),
        },
        "issues": issues,
        "warnings": warnings,
        "config": {
            "concept_marker": CONCEPT_MARKER,
            "philosophy_paths": list(philosophy_paths),
            "mainline_paths": list(mainline_paths),
            "known_arxiv_title_count": len(EXPECTED_ARXIV_TITLES),
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify citation integrity rules.")
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when issues are detected.",
    )
    parser.add_argument(
        "--philosophy-path",
        action="append",
        dest="philosophy_paths",
        help="Override/add philosophy paths to check.",
    )
    parser.add_argument(
        "--mainline-path",
        action="append",
        dest="mainline_paths",
        help="Override/add mainline paths to check.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    philosophy_paths = args.philosophy_paths or list(DEFAULT_PHILOSOPHY_PATHS)
    mainline_paths = args.mainline_paths or list(DEFAULT_MAINLINE_PATHS)

    report = build_report(
        repo_root=repo_root,
        philosophy_paths=philosophy_paths,
        mainline_paths=mainline_paths,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.strict and not report["overall_ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
