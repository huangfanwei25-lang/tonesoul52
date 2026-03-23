#!/usr/bin/env python3
"""Report canonical ownership and mirror hygiene for engineering docs."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

JSON_FILENAME = "engineering_mirror_ownership_latest.json"
MARKDOWN_FILENAME = "engineering_mirror_ownership_latest.md"

CANONICAL_ROOT = Path("docs/engineering")
MIRROR_ROOT = Path("law/engineering")
PAIR_POLICIES: dict[str, dict[str, Any]] = {
    "README.md": {
        "mode": "role_scoped",
        "expected_posture": "role-scoped pair",
        "min_similarity": 0.85,
    }
}


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_text(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.splitlines()).strip()


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _iter_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file())


def build_report(repo_root: Path) -> dict[str, Any]:
    canonical_root = repo_root / CANONICAL_ROOT
    mirror_root = repo_root / MIRROR_ROOT

    canonical_files = _iter_files(canonical_root)
    mirror_files = _iter_files(mirror_root)
    mirror_index = {path.relative_to(mirror_root).as_posix(): path for path in mirror_files}

    pairs: list[dict[str, Any]] = []
    canonical_only: list[str] = []
    for canonical_path in canonical_files:
        rel_path = canonical_path.relative_to(canonical_root).as_posix()
        mirror_path = mirror_index.pop(rel_path, None)
        if mirror_path is None:
            canonical_only.append(rel_path)
            continue
        canonical_text = _normalize_text(_load_text(canonical_path))
        mirror_text = _normalize_text(_load_text(mirror_path))
        exact_match = canonical_text == mirror_text
        similarity = difflib.SequenceMatcher(None, canonical_text, mirror_text).ratio()
        policy = PAIR_POLICIES.get(
            rel_path,
            {
                "mode": "exact_mirror",
                "expected_posture": "exact mirror",
                "min_similarity": 1.0,
            },
        )
        needs_sync = (
            not exact_match
            if policy["mode"] == "exact_mirror"
            else similarity < float(policy["min_similarity"])
        )
        pairs.append(
            {
                "relative_path": rel_path,
                "canonical_path": canonical_path.relative_to(repo_root).as_posix(),
                "mirror_path": mirror_path.relative_to(repo_root).as_posix(),
                "policy_mode": policy["mode"],
                "expected_posture": policy["expected_posture"],
                "exact_match": exact_match,
                "needs_sync": needs_sync,
                "similarity": round(similarity, 3),
                "canonical_sha256": _hash_text(canonical_text),
                "mirror_sha256": _hash_text(mirror_text),
            }
        )

    mirror_only = sorted(mirror_index.keys())

    sync_needed = [pair["relative_path"] for pair in pairs if pair["needs_sync"]]
    primary_status_line = (
        "engineering_mirror_contract | "
        f"pairs={len(pairs)} exact={sum(1 for pair in pairs if pair['exact_match'])} "
        f"sync_needed={len(sync_needed)} canonical_only={len(canonical_only)} mirror_only={len(mirror_only)}"
    )
    runtime_status_line = (
        "owner=docs/engineering | "
        f"mirror=law/engineering sync_direction=canonical_to_mirror drift={len(sync_needed)}"
    )
    artifact_policy_status_line = (
        "mirror_policy=explicit_owner | comparison=normalized_hash_plus_similarity"
    )

    return {
        "generated_at": _iso_now(),
        "contract": {
            "canonical_root": CANONICAL_ROOT.as_posix(),
            "mirror_root": MIRROR_ROOT.as_posix(),
            "sync_direction": "docs/engineering -> law/engineering",
            "owner_rule": "prefer canonical owner when canonical and mirror disagree",
        },
        "metrics": {
            "pair_count": len(pairs),
            "exact_match_count": sum(1 for pair in pairs if pair["exact_match"]),
            "sync_needed_count": len(sync_needed),
            "canonical_only_count": len(canonical_only),
            "mirror_only_count": len(mirror_only),
        },
        "pairs": pairs,
        "sync_needed": sync_needed,
        "canonical_only": canonical_only,
        "mirror_only": mirror_only,
        "primary_status_line": primary_status_line,
        "runtime_status_line": runtime_status_line,
        "artifact_policy_status_line": artifact_policy_status_line,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Engineering Mirror Ownership Latest",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- primary_status_line: `{payload['primary_status_line']}`",
        f"- runtime_status_line: `{payload['runtime_status_line']}`",
        f"- artifact_policy_status_line: `{payload['artifact_policy_status_line']}`",
        "",
        "## Contract",
        f"- canonical_root: `{payload['contract']['canonical_root']}`",
        f"- mirror_root: `{payload['contract']['mirror_root']}`",
        f"- sync_direction: `{payload['contract']['sync_direction']}`",
        f"- owner_rule: `{payload['contract']['owner_rule']}`",
        "",
        "## Metrics",
    ]
    for key, value in payload["metrics"].items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(["", "## Pairs"])
    for pair in payload["pairs"]:
        lines.append(
            f"- `{pair['relative_path']}` exact=`{str(pair['exact_match']).lower()}` "
            f"needs_sync=`{str(pair['needs_sync']).lower()}` similarity=`{pair['similarity']}` "
            f"policy=`{pair['policy_mode']}`"
        )
        lines.append(f"  - canonical: `{pair['canonical_path']}`")
        lines.append(f"  - mirror: `{pair['mirror_path']}`")
        lines.append(f"  - expected_posture: `{pair['expected_posture']}`")

    lines.extend(["", "## Canonical Only"])
    for rel_path in payload["canonical_only"]:
        lines.append(f"- `{rel_path}`")

    lines.extend(["", "## Mirror Only"])
    for rel_path in payload["mirror_only"]:
        lines.append(f"- `{rel_path}`")

    return "\n".join(lines) + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Report canonical ownership and sync posture for engineering mirror docs."
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
