#!/usr/bin/env python3
"""Report the active-vs-shadow posture for nested private-memory index lanes."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

JSON_FILENAME = "private_memory_shadow_latest.json"
MARKDOWN_FILENAME = "private_memory_shadow_latest.md"

ACTIVE_ROOT = Path("memory/.hierarchical_index")
SHADOW_ROOT = Path("memory/memory/.hierarchical_index")
REGISTRY_PATH = Path("spec/governance/basename_divergence_registry_v1.json")
TRACKED_BASENAME = "vows_meta.json"


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _iter_files(root: Path) -> dict[str, Path]:
    if not root.exists():
        return {}
    return {
        path.relative_to(root).as_posix(): path
        for path in sorted(path for path in root.rglob("*") if path.is_file())
    }


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _load_json_summary(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    payload = json.loads(text)
    first_item = payload[0] if isinstance(payload, list) and payload else {}
    return {
        "item_count": len(payload) if isinstance(payload, list) else None,
        "first_item_keys": sorted(first_item.keys()) if isinstance(first_item, dict) else [],
        "similarity_source": text,
    }


def _read_registry_entry(repo_root: Path) -> dict[str, Any] | None:
    registry_path = repo_root / REGISTRY_PATH
    if not registry_path.exists():
        return None
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    for entry in registry.get("entries", []):
        if str(entry.get("basename")) == TRACKED_BASENAME:
            return entry
    return None


def build_report(repo_root: Path) -> dict[str, Any]:
    active_root = repo_root / ACTIVE_ROOT
    shadow_root = repo_root / SHADOW_ROOT

    active_files = _iter_files(active_root)
    shadow_files = _iter_files(shadow_root)
    relative_paths = sorted(set(active_files) | set(shadow_files))

    pairs: list[dict[str, Any]] = []
    issues: list[str] = []

    for rel_path in relative_paths:
        active_path = active_files.get(rel_path)
        shadow_path = shadow_files.get(rel_path)

        active_bytes = active_path.read_bytes() if active_path else b""
        shadow_bytes = shadow_path.read_bytes() if shadow_path else b""
        exact_match = bool(active_path and shadow_path and active_bytes == shadow_bytes)
        missing_side = None
        if active_path is None:
            missing_side = "active_missing"
        elif shadow_path is None:
            missing_side = "shadow_missing"

        pair: dict[str, Any] = {
            "relative_path": rel_path,
            "active_path": active_path.relative_to(repo_root).as_posix() if active_path else None,
            "shadow_path": shadow_path.relative_to(repo_root).as_posix() if shadow_path else None,
            "comparison_mode": "binary_hash_compare",
            "policy": "defer_private_cleanup",
            "exact_match": exact_match,
            "needs_review": missing_side is not None,
            "missing_side": missing_side,
            "active_size": len(active_bytes) if active_path else None,
            "shadow_size": len(shadow_bytes) if shadow_path else None,
            "active_sha256": _sha256_bytes(active_bytes) if active_path else None,
            "shadow_sha256": _sha256_bytes(shadow_bytes) if shadow_path else None,
        }

        if rel_path.endswith(".json") and active_path and shadow_path:
            active_json = _load_json_summary(active_path)
            shadow_json = _load_json_summary(shadow_path)
            similarity = difflib.SequenceMatcher(
                None,
                str(active_json["similarity_source"]),
                str(shadow_json["similarity_source"]),
            ).ratio()
            pair["comparison_mode"] = "json_structural_compare"
            pair["similarity"] = round(similarity, 3)
            pair["active_item_count"] = active_json["item_count"]
            pair["shadow_item_count"] = shadow_json["item_count"]
            pair["active_first_item_keys"] = active_json["first_item_keys"]
            pair["shadow_first_item_keys"] = shadow_json["first_item_keys"]
            pair["key_shape_match"] = (
                active_json["first_item_keys"] == shadow_json["first_item_keys"]
            )

        pairs.append(pair)

        if missing_side is not None:
            issues.append(f"{missing_side}:{rel_path}")

    registry_entry = _read_registry_entry(repo_root)
    registry_paths = set(registry_entry.get("paths", [])) if registry_entry else set()
    expected_paths = {
        ACTIVE_ROOT.joinpath(TRACKED_BASENAME).as_posix(),
        SHADOW_ROOT.joinpath(TRACKED_BASENAME).as_posix(),
    }
    registry_alignment = {
        "entry_present": registry_entry is not None,
        "tracked_basename": TRACKED_BASENAME,
        "paths_match_expected": registry_paths == expected_paths if registry_entry else False,
        "missing_paths": (
            sorted(expected_paths - registry_paths) if registry_entry else sorted(expected_paths)
        ),
        "extra_paths": sorted(registry_paths - expected_paths) if registry_entry else [],
    }

    divergent_count = sum(1 for pair in pairs if not pair["exact_match"])
    review_count = sum(1 for pair in pairs if pair["needs_review"])
    primary_status_line = (
        "private_memory_shadow_contract | "
        f"pairs={len(pairs)} divergent={divergent_count} missing={review_count} registry_entry="
        f"{int(registry_alignment['entry_present'])}"
    )
    runtime_status_line = (
        "active_root=memory/.hierarchical_index | shadow_root=memory/memory/.hierarchical_index "
        f"defer_mutation=1 review={review_count}"
    )
    artifact_policy_status_line = (
        "shadow_policy=observe_report_do_not_mutate | cleanup_scope=private_memory_phase_only"
    )

    return {
        "generated_at": _iso_now(),
        "contract": {
            "active_root": ACTIVE_ROOT.as_posix(),
            "shadow_root": SHADOW_ROOT.as_posix(),
            "source_of_truth_rule": "Prefer memory/.hierarchical_index as the active lane in public convergence work.",
            "public_cleanup_rule": "Do not mutate either lane during public document convergence; report only.",
            "deferred_cleanup_phase": "private_memory_lane_cleanup",
        },
        "metrics": {
            "active_file_count": len(active_files),
            "shadow_file_count": len(shadow_files),
            "pair_count": len(pairs),
            "divergent_pair_count": divergent_count,
            "exact_match_count": sum(1 for pair in pairs if pair["exact_match"]),
            "needs_review_count": review_count,
        },
        "registry_alignment": registry_alignment,
        "pairs": pairs,
        "issues": issues,
        "primary_status_line": primary_status_line,
        "runtime_status_line": runtime_status_line,
        "artifact_policy_status_line": artifact_policy_status_line,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Private Memory Shadow Latest",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- primary_status_line: `{payload['primary_status_line']}`",
        f"- runtime_status_line: `{payload['runtime_status_line']}`",
        f"- artifact_policy_status_line: `{payload['artifact_policy_status_line']}`",
        "",
        "## Contract",
        f"- active_root: `{payload['contract']['active_root']}`",
        f"- shadow_root: `{payload['contract']['shadow_root']}`",
        f"- source_of_truth_rule: `{payload['contract']['source_of_truth_rule']}`",
        f"- public_cleanup_rule: `{payload['contract']['public_cleanup_rule']}`",
        f"- deferred_cleanup_phase: `{payload['contract']['deferred_cleanup_phase']}`",
        "",
        "## Metrics",
    ]
    for key, value in payload["metrics"].items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(["", "## Registry Alignment"])
    for key, value in payload["registry_alignment"].items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(["", "## Pairs"])
    for pair in payload["pairs"]:
        lines.append(
            f"- `{pair['relative_path']}` mode=`{pair['comparison_mode']}` "
            f"exact=`{str(pair['exact_match']).lower()}` "
            f"needs_review=`{str(pair['needs_review']).lower()}`"
        )
        lines.append(f"  - active: `{pair['active_path']}`")
        lines.append(f"  - shadow: `{pair['shadow_path']}`")
        lines.append(f"  - policy: `{pair['policy']}`")
        lines.append(f"  - sizes: active=`{pair['active_size']}` shadow=`{pair['shadow_size']}`")
        if pair["comparison_mode"] == "json_structural_compare":
            lines.append(
                f"  - item_counts: active=`{pair['active_item_count']}` shadow=`{pair['shadow_item_count']}`"
            )
            lines.append(
                f"  - key_shape_match: `{str(pair['key_shape_match']).lower()}` similarity=`{pair['similarity']}`"
            )

    lines.extend(["", "## Issues"])
    for issue in payload["issues"]:
        lines.append(f"- `{issue}`")

    return "\n".join(lines) + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Report nested private-memory shadow posture.")
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
