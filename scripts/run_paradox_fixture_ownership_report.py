#!/usr/bin/env python3
"""Report source-of-truth posture for paradox casebook and test fixtures."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

JSON_FILENAME = "paradox_fixture_ownership_latest.json"
MARKDOWN_FILENAME = "paradox_fixture_ownership_latest.md"

CANONICAL_ROOT = Path("PARADOXES")
FIXTURE_ROOT = Path("tests/fixtures/paradoxes")
ALLOWED_REDUCED_PROJECTIONS = {
    "paradox_003.json",
    "paradox_004.json",
    "paradox_005.json",
    "paradox_006.json",
    "paradox_007.json",
}
ROLE_SCOPED_FILES = {"README.md"}


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _iter_fixture_files(root: Path) -> list[Path]:
    candidates = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() == ".json" or path.name in ROLE_SCOPED_FILES:
            candidates.append(path)
    return sorted(candidates)


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace").strip()


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_report(repo_root: Path) -> dict[str, Any]:
    canonical_root = repo_root / CANONICAL_ROOT
    fixture_root = repo_root / FIXTURE_ROOT

    canonical_files = _iter_fixture_files(canonical_root)
    fixture_index = {
        path.relative_to(fixture_root).as_posix(): path
        for path in _iter_fixture_files(fixture_root)
    }

    pairs: list[dict[str, Any]] = []
    canonical_only: list[str] = []
    for canonical_path in canonical_files:
        rel_path = canonical_path.relative_to(canonical_root).as_posix()
        fixture_path = fixture_index.pop(rel_path, None)
        if fixture_path is None:
            canonical_only.append(rel_path)
            continue
        canonical_text = _load_text(canonical_path)
        fixture_text = _load_text(fixture_path)
        exact_match = canonical_text == fixture_text
        similarity = difflib.SequenceMatcher(None, canonical_text, fixture_text).ratio()
        if rel_path in ROLE_SCOPED_FILES:
            projection_mode = "role_scoped"
            needs_review = False
        else:
            projection_mode = (
                "reduced_projection"
                if rel_path in ALLOWED_REDUCED_PROJECTIONS
                else "exact_or_raise"
            )
            needs_review = not exact_match and projection_mode == "exact_or_raise"
        pairs.append(
            {
                "relative_path": rel_path,
                "canonical_path": canonical_path.relative_to(repo_root).as_posix(),
                "fixture_path": fixture_path.relative_to(repo_root).as_posix(),
                "projection_mode": projection_mode,
                "exact_match": exact_match,
                "needs_review": needs_review,
                "similarity": round(similarity, 3),
                "canonical_sha256": _hash_text(canonical_text),
                "fixture_sha256": _hash_text(fixture_text),
            }
        )

    fixture_only = sorted(fixture_index.keys())
    needs_review = [pair["relative_path"] for pair in pairs if pair["needs_review"]]
    primary_status_line = (
        "paradox_fixture_contract | "
        f"pairs={len(pairs)} exact={sum(1 for pair in pairs if pair['exact_match'])} "
        f"reduced={sum(1 for pair in pairs if pair['projection_mode'] == 'reduced_projection')} "
        f"needs_review={len(needs_review)}"
    )
    runtime_status_line = (
        "owner=PARADOXES | fixture_lane=tests/fixtures/paradoxes "
        f"sync_direction=canonical_to_fixture review={len(needs_review)}"
    )
    artifact_policy_status_line = (
        "fixture_policy=casebook_to_projection | exact_or_reduced_projection_allowed"
    )

    return {
        "generated_at": _iso_now(),
        "contract": {
            "canonical_root": CANONICAL_ROOT.as_posix(),
            "fixture_root": FIXTURE_ROOT.as_posix(),
            "sync_direction": "PARADOXES -> tests/fixtures/paradoxes",
            "source_of_truth_rule": "prefer canonical casebook when canonical and fixture diverge",
        },
        "metrics": {
            "pair_count": len(pairs),
            "exact_match_count": sum(1 for pair in pairs if pair["exact_match"]),
            "reduced_projection_count": sum(
                1 for pair in pairs if pair["projection_mode"] == "reduced_projection"
            ),
            "needs_review_count": len(needs_review),
            "canonical_only_count": len(canonical_only),
            "fixture_only_count": len(fixture_only),
        },
        "pairs": pairs,
        "needs_review": needs_review,
        "canonical_only": canonical_only,
        "fixture_only": fixture_only,
        "primary_status_line": primary_status_line,
        "runtime_status_line": runtime_status_line,
        "artifact_policy_status_line": artifact_policy_status_line,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Paradox Fixture Ownership Latest",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- primary_status_line: `{payload['primary_status_line']}`",
        f"- runtime_status_line: `{payload['runtime_status_line']}`",
        f"- artifact_policy_status_line: `{payload['artifact_policy_status_line']}`",
        "",
        "## Contract",
        f"- canonical_root: `{payload['contract']['canonical_root']}`",
        f"- fixture_root: `{payload['contract']['fixture_root']}`",
        f"- sync_direction: `{payload['contract']['sync_direction']}`",
        f"- source_of_truth_rule: `{payload['contract']['source_of_truth_rule']}`",
        "",
        "## Metrics",
    ]
    for key, value in payload["metrics"].items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(["", "## Pairs"])
    for pair in payload["pairs"]:
        lines.append(
            f"- `{pair['relative_path']}` exact=`{str(pair['exact_match']).lower()}` "
            f"projection_mode=`{pair['projection_mode']}` needs_review=`{str(pair['needs_review']).lower()}` "
            f"similarity=`{pair['similarity']}`"
        )
        lines.append(f"  - canonical: `{pair['canonical_path']}`")
        lines.append(f"  - fixture: `{pair['fixture_path']}`")

    lines.extend(["", "## Canonical Only"])
    for rel_path in payload["canonical_only"]:
        lines.append(f"- `{rel_path}`")

    lines.extend(["", "## Fixture Only"])
    for rel_path in payload["fixture_only"]:
        lines.append(f"- `{rel_path}`")

    lines.extend(["", "## Needs Review"])
    for rel_path in payload["needs_review"]:
        lines.append(f"- `{rel_path}`")

    return "\n".join(lines) + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Report ownership and projection posture for paradox fixtures."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--out-dir", default="docs/status", help="Output directory.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    out_dir = (repo_root / args.out_dir).resolve()
    payload = build_report(repo_root)
    _write(out_dir / JSON_FILENAME, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    _write(out_dir / MARKDOWN_FILENAME, render_markdown(payload))
    print(
        json.dumps(
            {
                "ok": True,
                "artifacts": {
                    "json": f"{args.out_dir}/{JSON_FILENAME}",
                    "markdown": f"{args.out_dir}/{MARKDOWN_FILENAME}",
                },
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
