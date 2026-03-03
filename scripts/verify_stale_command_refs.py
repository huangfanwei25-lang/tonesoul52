"""
Detect stale command references left behind after CLI wrapper cleanup.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

JSON_FILENAME = "stale_command_refs_latest.json"
MARKDOWN_FILENAME = "stale_command_refs_latest.md"

DEFAULT_SCAN_TARGETS = (
    "tonesoul",
    "scripts",
    "apps",
    ".github/workflows",
    "pyproject.toml",
)
DEFAULT_EXTENSIONS = (".py", ".yml", ".yaml", ".toml")
DEFAULT_EXCLUDES = ("scripts/verify_stale_command_refs.py",)


@dataclass(frozen=True)
class PatternSpec:
    id: str
    regex: str
    description: str


DEFAULT_PATTERNS = (
    PatternSpec(
        id="legacy_cli_wrapper_module",
        regex=r"\btonesoul\.cli\.run_[A-Za-z0-9_]+\b",
        description="Removed tonesoul.cli run_ wrapper module reference",
    ),
    PatternSpec(
        id="legacy_tonesoul52_ystm_acceptance",
        regex=r"\btonesoul52\.run_ystm_acceptance\b",
        description="Legacy ystm acceptance module reference",
    ),
    PatternSpec(
        id="legacy_tonesoul52_ystm_demo",
        regex=r"\btonesoul52\.run_ystm_demo\b",
        description="Legacy ystm demo module reference",
    ),
)


@dataclass(frozen=True)
class Match:
    path: str
    line: int
    pattern_id: str
    description: str
    snippet: str


def _iter_files(
    repo_root: Path,
    scan_targets: Sequence[str],
    extensions: Sequence[str],
    excludes: set[str],
) -> Iterable[Path]:
    ext_set = {ext.lower() for ext in extensions}
    seen: set[Path] = set()
    for target in scan_targets:
        path = (repo_root / target).resolve()
        if not path.exists():
            continue
        if path.is_file():
            rel = path.relative_to(repo_root).as_posix()
            if rel in excludes:
                continue
            if path.suffix.lower() in ext_set:
                yield path
            continue
        for file_path in path.rglob("*"):
            if not file_path.is_file():
                continue
            rel = file_path.relative_to(repo_root).as_posix()
            if rel in excludes:
                continue
            if file_path.suffix.lower() in ext_set:
                if file_path in seen:
                    continue
                seen.add(file_path)
                yield file_path


def find_matches(
    repo_root: Path,
    pattern_specs: Sequence[PatternSpec] = DEFAULT_PATTERNS,
    scan_targets: Sequence[str] = DEFAULT_SCAN_TARGETS,
    extensions: Sequence[str] = DEFAULT_EXTENSIONS,
    excludes: Sequence[str] = DEFAULT_EXCLUDES,
) -> list[Match]:
    compiled = [(spec, re.compile(spec.regex)) for spec in pattern_specs]
    exclude_set = {Path(item).as_posix() for item in excludes}
    hits: list[Match] = []
    for file_path in _iter_files(repo_root, scan_targets, extensions, exclude_set):
        relative = file_path.relative_to(repo_root).as_posix()
        source = file_path.read_text(encoding="utf-8-sig", errors="replace")
        for lineno, line in enumerate(source.splitlines(), start=1):
            for spec, pattern in compiled:
                if pattern.search(line):
                    hits.append(
                        Match(
                            path=relative,
                            line=lineno,
                            pattern_id=spec.id,
                            description=spec.description,
                            snippet=line.strip(),
                        )
                    )
    return hits


def build_report(
    repo_root: Path,
    pattern_specs: Sequence[PatternSpec] = DEFAULT_PATTERNS,
    scan_targets: Sequence[str] = DEFAULT_SCAN_TARGETS,
    extensions: Sequence[str] = DEFAULT_EXTENSIONS,
    excludes: Sequence[str] = DEFAULT_EXCLUDES,
) -> dict[str, object]:
    matches = find_matches(
        repo_root=repo_root,
        pattern_specs=pattern_specs,
        scan_targets=scan_targets,
        extensions=extensions,
        excludes=excludes,
    )
    return {
        "overall_ok": len(matches) == 0,
        "repo_root": str(repo_root),
        "scan_targets": list(scan_targets),
        "patterns": [asdict(spec) for spec in pattern_specs],
        "match_count": len(matches),
        "matches": [asdict(match) for match in matches],
    }


def _render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Stale Command References Latest",
        "",
        f"- overall_ok: {str(payload['overall_ok']).lower()}",
        f"- match_count: {payload['match_count']}",
        "",
    ]
    if payload["match_count"] == 0:
        lines.append("## Matches")
        lines.append("- None")
        return "\n".join(lines) + "\n"

    lines.append("## Matches")
    for item in payload["matches"]:
        lines.append(
            f"- `{item['path']}:{item['line']}` [{item['pattern_id']}] "
            f"{item['description']} -> `{item['snippet']}`"
        )
    return "\n".join(lines) + "\n"


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_markdown(payload), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify stale command references are removed.")
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--out-dir", default="docs/status", help="Output directory for artifacts.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when stale references are found.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo_root).resolve()
    out_dir = (repo_root / args.out_dir).resolve()
    payload = build_report(repo_root=repo_root)
    _write_json(out_dir / JSON_FILENAME, payload)
    _write_markdown(out_dir / MARKDOWN_FILENAME, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.strict and not payload["overall_ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
