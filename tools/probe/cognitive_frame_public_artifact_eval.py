"""Evaluate CognitiveFrame fixtures grounded in public repository artifacts.

This probe is deliberately small: it loads public-safe fixture frames, validates the frame
shape, and verifies that every `file:` evidence ref exists under the public repo without using
private-memory paths. It does not check whether the evidence semantically proves the frame text.

Usage:
    python tools/probe/cognitive_frame_public_artifact_eval.py
    python tools/probe/cognitive_frame_public_artifact_eval.py --write-doc
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

from tonesoul.cognition import validate_cognitive_frame  # noqa: E402

FIXTURE_PATH = (
    REPO_ROOT / "tests" / "fixtures" / "cognition" / "public_artifact_frames_2026-06-28.json"
)

FORBIDDEN_PUBLIC_ARTIFACT_PREFIXES = (
    ".archive/",
    "data/chromadb/",
    "docs/chronicles/task_archive",
    "memory/",
    "temp/",
    "tonesoul_evolution/",
)


@dataclass(frozen=True)
class PublicArtifactEvalRow:
    case_id: str
    expected_accepted: bool
    actual_accepted: bool
    artifact_count: int
    missing_refs: tuple[str, ...]
    forbidden_refs: tuple[str, ...]
    issue_codes: tuple[str, ...]
    severities: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return (
            self.expected_accepted == self.actual_accepted
            and not self.missing_refs
            and not self.forbidden_refs
        )


def load_cases(path: Path = FIXTURE_PATH) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    cases = payload.get("cases", [])
    if not isinstance(cases, list):
        raise ValueError("fixture cases must be a list")
    return cases


def evaluate_cases(cases: list[dict[str, Any]]) -> list[PublicArtifactEvalRow]:
    rows: list[PublicArtifactEvalRow] = []
    for case in cases:
        frame = case["frame"]
        result = validate_cognitive_frame(frame)
        refs = _artifact_refs(case)
        missing_refs = tuple(ref for ref in refs if not (REPO_ROOT / ref).is_file())
        forbidden_refs = tuple(ref for ref in refs if _is_forbidden_public_ref(ref))
        rows.append(
            PublicArtifactEvalRow(
                case_id=str(case["id"]),
                expected_accepted=bool(case.get("expected_accepted", True)),
                actual_accepted=result.accepted,
                artifact_count=len(refs),
                missing_refs=missing_refs,
                forbidden_refs=forbidden_refs,
                issue_codes=tuple(issue.code for issue in result.issues),
                severities=tuple(issue.severity for issue in result.issues),
            )
        )
    return rows


def render_report(rows: list[PublicArtifactEvalRow]) -> str:
    failures = [row for row in rows if not row.ok]
    accepted = sum(1 for row in rows if row.actual_accepted)
    warnings = sum(1 for row in rows if "warning" in row.severities)
    artifact_refs = sum(row.artifact_count for row in rows)

    lines: list[str] = []
    lines.append("# Cognitive Frame Public Artifact Eval")
    lines.append("")
    lines.append("Deterministic eval of CognitiveFrame fixtures grounded in public repo artifacts.")
    lines.append("This validates frame shape and public `file:` evidence-ref existence only; it")
    lines.append("does not prove semantic evidence sufficiency or model understanding.")
    lines.append("")
    lines.append(f"- cases: **{len(rows)}**")
    lines.append(f"- accepted frames: **{accepted}/{len(rows)}**")
    lines.append(f"- warning-bearing frames: **{warnings}**")
    lines.append(f"- public artifact refs checked: **{artifact_refs}**")
    lines.append(f"- failures: **{len(failures)}**")
    lines.append("")
    lines.append(
        "| case | expected | actual | refs | missing refs | forbidden refs | issue codes | severities | ok |"
    )
    lines.append("|---|---|---|---:|---|---|---|---|---|")
    for row in rows:
        lines.append(
            f"| {row.case_id} | {_yes_no(row.expected_accepted)} | "
            f"{_yes_no(row.actual_accepted)} | {row.artifact_count} | "
            f"{_join(row.missing_refs)} | {_join(row.forbidden_refs)} | "
            f"{_join(row.issue_codes)} | {_join(row.severities)} | {_yes_no(row.ok)} |"
        )
    return "\n".join(lines)


def _artifact_refs(case: dict[str, Any]) -> tuple[str, ...]:
    refs = set(str(path).replace("\\", "/") for path in case.get("artifact_paths", []))
    _collect_file_refs(case.get("frame", {}), refs)
    return tuple(sorted(refs))


def _collect_file_refs(value: Any, refs: set[str]) -> None:
    if isinstance(value, dict):
        for item in value.values():
            _collect_file_refs(item, refs)
    elif isinstance(value, list):
        for item in value:
            _collect_file_refs(item, refs)
    elif isinstance(value, str) and value.startswith("file:"):
        refs.add(value.removeprefix("file:").replace("\\", "/"))


def _is_forbidden_public_ref(ref: str) -> bool:
    normalized = ref.replace("\\", "/").lstrip("/")
    return any(normalized.startswith(prefix) for prefix in FORBIDDEN_PUBLIC_ARTIFACT_PREFIXES)


def _join(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "-"


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-doc", action="store_true")
    args = parser.parse_args()

    rows = evaluate_cases(load_cases())
    report = render_report(rows)
    sys.stdout.buffer.write((report + "\n").encode("utf-8"))
    if args.write_doc:
        path = REPO_ROOT / "docs" / "status" / "cognitive_frame_public_artifact_eval_2026-06-28.md"
        path.write_text(report + "\n", encoding="utf-8", newline="\n")
        sys.stdout.buffer.write(f"\n[wrote {path.relative_to(REPO_ROOT)}]\n".encode("utf-8"))
    return 1 if any(not row.ok for row in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
