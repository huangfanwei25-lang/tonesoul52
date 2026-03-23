#!/usr/bin/env python3
"""Inventory authored document surfaces, basename collisions, and metadata drift."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

JSON_FILENAME = "doc_convergence_inventory_latest.json"
MARKDOWN_FILENAME = "doc_convergence_inventory_latest.md"
MERMAID_FILENAME = "doc_convergence_inventory_latest.mmd"
HISTORICAL_LANE_POLICY = Path("docs/architecture/HISTORICAL_DOC_LANE_POLICY.md")
HISTORICAL_LANE_STATUS = Path("docs/status/historical_doc_lane_latest.json")
HISTORICAL_CHRONICLE_README = Path("docs/chronicles/README.md")

INCLUDE_ROOTS = {
    "docs",
    "spec",
    "law",
    "constitution",
    "reports",
    "knowledge",
    "knowledge_base",
    "PARADOXES",
    "memory",
    "tests",
}
ROOT_AUTHORED_FILES = {
    "README.md",
    "README.zh-TW.md",
    "AI_ONBOARDING.md",
    "SOUL.md",
    "MGGI_SPEC.md",
    "TAE-01_Architecture_Spec.md",
    "AXIOMS.json",
    "task.md",
    "AGENTS.md",
    "HANDOFF.md",
    "MEMORY.md",
    "PHILOSOPHY.md",
    "WHITEPAPER.md",
}
DOC_EXTENSIONS = {".md", ".json", ".yaml", ".yml", ".txt"}
EXCLUDE_PARTS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".next",
    ".archive",
    "temp",
    ".hypothesis",
    ".ruff_cache",
    ".pytest_cache",
    "htmlcov",
    "dist",
    "build",
    "coverage",
    "obsidian-vault",
    "tonesoul_evolution",
    ".agent",
    ".agents",
}
EXCLUDE_PREFIXES = (
    "docs/status/probe_",
    "docs/status/true_verification_weekly/probe_",
    "memory/autonomous/probe_",
)
PURPOSE_PATTERNS = (
    re.compile(
        r"^\s*>?\s*\*{0,2}\s*(?:Document Purpose|Purpose|用途|Scope)\s*\*{0,2}\s*:\s*(.+?)\s*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*>?\s*\*{0,2}\s*(?:說明用途|文件定位聲明)\s*\*{0,2}\s*[:：]?\s*(.+?)\s*$",
        re.IGNORECASE,
    ),
)
STATUS_PATTERN = re.compile(r"^\s*>\s*Status\s*:\s*(.+?)\s*$", re.IGNORECASE)
DATE_PATTERNS = (
    re.compile(r"(20\d{2}-\d{2}-\d{2})"),
    re.compile(r"(20\d{2}/\d{2}/\d{2})"),
)


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_path(value: str) -> str:
    normalized = str(value or "").strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _is_included(path: Path, repo_root: Path) -> bool:
    rel = _normalize_path(path.relative_to(repo_root).as_posix())
    if not rel:
        return False
    parts = set(path.relative_to(repo_root).parts)
    if parts & EXCLUDE_PARTS:
        return False
    if any(rel.startswith(prefix) for prefix in EXCLUDE_PREFIXES):
        return False
    if path.suffix.lower() not in DOC_EXTENSIONS:
        return False
    if rel in ROOT_AUTHORED_FILES:
        return True
    return rel.split("/", 1)[0] in INCLUDE_ROOTS


def _iter_authored_docs(repo_root: Path) -> list[Path]:
    return sorted(
        path for path in repo_root.rglob("*") if path.is_file() and _is_included(path, repo_root)
    )


def _extract_title(path: str, text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return Path(path).stem


def _extract_purpose(text: str) -> str:
    for line in text.splitlines()[:40]:
        for pattern in PURPOSE_PATTERNS:
            match = pattern.match(line)
            if match:
                value = match.group(1).strip()
                value = re.sub(r"^\*+\s*", "", value)
                value = re.sub(r"\s*\*+$", "", value)
                return value.strip()
    return ""


def _extract_status(text: str) -> str:
    for line in text.splitlines()[:25]:
        match = STATUS_PATTERN.match(line)
        if match:
            return match.group(1).strip()
    return ""


def _extract_date(path: str, text: str) -> str:
    for pattern in DATE_PATTERNS:
        match = pattern.search(path)
        if match:
            return match.group(1)
    for line in text.splitlines()[:40]:
        lowered = line.lower()
        if "last updated" in lowered or "最後更新" in line or "status:" in lowered:
            for pattern in DATE_PATTERNS:
                match = pattern.search(line)
                if match:
                    return match.group(1)
    return ""


def _canonical_text(path: Path, text: str) -> str:
    if path.suffix.lower() == ".json":
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            pass
        else:
            return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def _surface_type(rel_path: str) -> str:
    if rel_path in ROOT_AUTHORED_FILES:
        return "root_entrypoint"
    if rel_path.startswith("docs/architecture/"):
        return "architecture_doc"
    if rel_path.startswith("docs/archive/"):
        return "archive_doc"
    if rel_path.startswith("docs/chronicles/"):
        return "chronicle_doc"
    if rel_path.startswith("docs/status/"):
        if "_latest." in rel_path:
            return "generated_status_artifact"
        return "status_doc"
    if rel_path.startswith("docs/research/"):
        return "research_doc"
    if rel_path.startswith("docs/plans/"):
        return "plan_doc"
    if rel_path.startswith("docs/philosophy/"):
        return "philosophy_doc"
    if rel_path.startswith("docs/engineering/"):
        return "docs_engineering_mirror"
    if rel_path.startswith("docs/"):
        return "general_doc"
    if rel_path.startswith("law/engineering/"):
        return "law_engineering_mirror"
    if rel_path.startswith("law/"):
        return "law_doc"
    if rel_path.startswith("spec/"):
        return "spec_doc"
    if rel_path.startswith("constitution/"):
        return "constitution_doc"
    if rel_path.startswith("reports/"):
        return "report_doc"
    if rel_path.startswith("knowledge_base/"):
        return "knowledge_base_doc"
    if rel_path.startswith("knowledge/"):
        return "knowledge_doc"
    if rel_path.startswith("PARADOXES/"):
        return "paradox_fixture"
    if rel_path.startswith("tests/fixtures/paradoxes/"):
        return "paradox_test_fixture"
    if rel_path.startswith("memory/"):
        return "memory_doc_or_data"
    if rel_path.startswith("tests/"):
        return "test_doc_or_fixture"
    return "other"


def _historical_doc_lane_managed(repo_root: Path) -> bool:
    return (
        (repo_root / HISTORICAL_LANE_POLICY).exists()
        and (repo_root / HISTORICAL_LANE_STATUS).exists()
        and (repo_root / HISTORICAL_CHRONICLE_README).exists()
    )


def _metadata_priority_types() -> set[str]:
    return {
        "root_entrypoint",
        "architecture_doc",
        "archive_doc",
        "chronicle_doc",
        "general_doc",
        "research_doc",
        "plan_doc",
        "law_doc",
        "spec_doc",
        "constitution_doc",
        "report_doc",
    }


def _requires_metadata(entry: dict[str, Any], field_name: str, repo_root: Path) -> bool:
    if entry["extension"] not in {".md", ".txt"}:
        return False
    surface_type = str(entry["surface_type"])
    if surface_type not in _metadata_priority_types():
        return False
    if str(entry.get(field_name) or "").strip():
        return False
    if surface_type in {"archive_doc", "chronicle_doc"} and _historical_doc_lane_managed(repo_root):
        return False
    return True


def _load_entries(repo_root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in _iter_authored_docs(repo_root):
        rel_path = _normalize_path(path.relative_to(repo_root).as_posix())
        text = path.read_text(encoding="utf-8", errors="replace")
        canonical = _canonical_text(path, text)
        entries.append(
            {
                "path": rel_path,
                "basename": path.name,
                "extension": path.suffix.lower(),
                "surface_type": _surface_type(rel_path),
                "size_bytes": path.stat().st_size,
                "title": (
                    _extract_title(rel_path, text)
                    if path.suffix.lower() in {".md", ".txt"}
                    else path.name
                ),
                "purpose": _extract_purpose(text) if path.suffix.lower() in {".md", ".txt"} else "",
                "status": _extract_status(text) if path.suffix.lower() in {".md", ".txt"} else "",
                "date_hint": (
                    _extract_date(rel_path, text)
                    if path.suffix.lower() in {".md", ".txt"}
                    else _extract_date(rel_path, "")
                ),
                "content_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
                "canonical_text": canonical,
            }
        )
    return entries


def _collision_family(paths: list[str]) -> str:
    if all(
        path.startswith("docs/engineering/") or path.startswith("law/engineering/")
        for path in paths
    ):
        return "docs_law_engineering_mirror"
    if any(path.startswith("PARADOXES/") for path in paths) and any(
        path.startswith("tests/fixtures/paradoxes/") for path in paths
    ):
        return "paradox_fixture_mirror"
    if any(path.startswith("scripts/legacy/") for path in paths) and any(
        path.startswith("scripts/") and not path.startswith("scripts/legacy/") for path in paths
    ):
        return "legacy_shadow"
    if (
        paths
        and all(path.startswith("docs/status/") for path in paths)
        and any("/probe_" in path for path in paths)
    ):
        return "probe_status_series"
    if (
        paths
        and all(path.startswith("memory/autonomous/") for path in paths)
        and any("/probe_" in path for path in paths)
    ):
        return "probe_memory_series"
    if any(path == "README.md" for path in paths):
        return "readme_family"
    return "manual_review"


def _collision_recommendation(family: str, exact_match: bool, divergent: bool) -> str:
    if family == "docs_law_engineering_mirror":
        return "declare one canonical mirror owner or merge the duplicated engineering texts"
    if family == "paradox_fixture_mirror":
        return "keep as test mirror but document source-of-truth and sync direction"
    if family == "legacy_shadow":
        return "prefer non-legacy script and mark the legacy twin as deprecated or remove later"
    if family in {"probe_status_series", "probe_memory_series"}:
        return "treat as generated probe family; exclude from manual naming cleanup"
    if family == "readme_family":
        return "keep only when scope is clearly distinct and each README states its surface"
    if exact_match:
        return "candidate for dedupe or canonical-owner annotation"
    if divergent:
        return "manual merge review required; same basename now carries different content"
    return "review path scopes and rename if the semantic surface is ambiguous"


def _build_collisions(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_basename: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        by_basename[str(entry["basename"])].append(entry)

    collisions: list[dict[str, Any]] = []
    for basename, group in sorted(by_basename.items()):
        if len(group) < 2:
            continue
        hashes = {str(item["content_sha256"]) for item in group}
        exact_match = len(hashes) == 1
        similarities: list[float] = []
        for index, left in enumerate(group):
            for right in group[index + 1 :]:
                similarities.append(
                    difflib.SequenceMatcher(
                        None,
                        str(left["canonical_text"]),
                        str(right["canonical_text"]),
                    ).ratio()
                )
        max_similarity = max(similarities) if similarities else 1.0
        min_similarity = min(similarities) if similarities else 1.0
        divergent = not exact_match and max_similarity < 0.9
        family = _collision_family([str(item["path"]) for item in group])
        collisions.append(
            {
                "basename": basename,
                "path_count": len(group),
                "paths": [str(item["path"]) for item in group],
                "surface_types": sorted({str(item["surface_type"]) for item in group}),
                "family": family,
                "exact_match": exact_match,
                "divergent": divergent,
                "max_similarity": round(max_similarity, 3),
                "min_similarity": round(min_similarity, 3),
                "recommendation": _collision_recommendation(family, exact_match, divergent),
            }
        )
    return collisions


def _top_missing_metadata(
    entries: list[dict[str, Any]], field_name: str, repo_root: Path, limit: int = 40
) -> list[str]:
    candidates = [
        str(entry["path"]) for entry in entries if _requires_metadata(entry, field_name, repo_root)
    ]
    return sorted(candidates)[:limit]


def _count_missing_metadata(entries: list[dict[str, Any]], field_name: str, repo_root: Path) -> int:
    return sum(1 for entry in entries if _requires_metadata(entry, field_name, repo_root))


def _build_priority_actions(
    repo_root: Path,
    entries: list[dict[str, Any]],
    collisions: list[dict[str, Any]],
    missing_purpose: list[str],
    missing_date: list[str],
) -> list[dict[str, Any]]:
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for collision in collisions:
        by_family[str(collision["family"])].append(collision)

    actions: list[dict[str, Any]] = []

    engineering_mirrors = by_family.get("docs_law_engineering_mirror", [])
    if engineering_mirrors:
        ownership_map_exists = (
            repo_root / "docs/architecture/ENGINEERING_MIRROR_OWNERSHIP_MAP.md"
        ).exists()
        ownership_report = repo_root / "docs/status/engineering_mirror_ownership_latest.json"
        ownership_payload: dict[str, Any] | None = None
        if ownership_report.exists():
            try:
                ownership_payload = json.loads(ownership_report.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                ownership_payload = None
        sync_needed_count = (
            int(ownership_payload.get("metrics", {}).get("sync_needed_count", 0))
            if ownership_payload
            else None
        )
        if ownership_map_exists and ownership_payload is not None:
            summary = "Maintain the explicit engineering mirror contract and keep the mirror lane synchronized."
            why = (
                f"{len(engineering_mirrors)} basename collisions still exist by design, but the repo now has "
                f"an ownership contract; current sync_needed_count={sync_needed_count}."
            )
            action_id = "engineering_mirror_contract_maintenance"
        else:
            summary = "Declare one canonical owner for duplicated docs/law engineering texts."
            why = (
                f"{len(engineering_mirrors)} basename collisions still split across "
                "docs/engineering and law/engineering, and most are exact or near-exact mirrors."
            )
            action_id = "engineering_mirror_owner"
        actions.append(
            {
                "id": action_id,
                "priority": "high",
                "summary": summary,
                "why": why,
                "evidence": [str(item["basename"]) for item in engineering_mirrors[:8]],
            }
        )

    manual_review = by_family.get("manual_review", [])
    if manual_review:
        divergence_registry = repo_root / "spec/governance/basename_divergence_registry_v1.json"
        registry_payload: dict[str, Any] | None = None
        if divergence_registry.exists():
            try:
                registry_payload = json.loads(divergence_registry.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                registry_payload = None
        manual_review_basenames = {str(item["basename"]) for item in manual_review}
        registry_basenames = (
            {
                str(item.get("basename"))
                for item in registry_payload.get("entries", [])
                if str(item.get("basename") or "").strip()
            }
            if registry_payload
            else set()
        )
        registry_covers_manual_review = bool(registry_payload) and manual_review_basenames.issubset(
            registry_basenames
        )
        unresolved_count = (
            sum(
                1
                for item in registry_payload.get("entries", [])
                if str(item.get("status")) == "unresolved_private_shadow"
            )
            if registry_payload
            else 0
        )
        if registry_covers_manual_review:
            action_id = "basename_divergence_registry_maintenance"
            summary = "Maintain the curated basename-divergence registry instead of re-triaging the same files."
            why = (
                f"{len(manual_review)} manual-review collisions are now classified in the divergence registry; "
                f"unresolved_private_shadow={unresolved_count}."
            )
        else:
            action_id = "same_basename_divergence_review"
            summary = "Review same-basename files whose content is no longer acting like a mirror."
            why = (
                f"{len(manual_review)} basename collisions now carry materially different content, "
                "so they need explicit role separation, renaming, or documented source-of-truth."
            )
        actions.append(
            {
                "id": action_id,
                "priority": "high",
                "summary": summary,
                "why": why,
                "evidence": [str(item["basename"]) for item in manual_review[:8]],
            }
        )

        unresolved_private_shadow_entries = (
            [
                item
                for item in registry_payload.get("entries", [])
                if str(item.get("status")) == "unresolved_private_shadow"
            ]
            if registry_payload
            else []
        )
        if unresolved_private_shadow_entries:
            private_shadow_map_exists = (
                repo_root / "docs/architecture/PRIVATE_MEMORY_SHADOW_BOUNDARY_MAP.md"
            ).exists()
            private_shadow_report = repo_root / "docs/status/private_memory_shadow_latest.json"
            private_shadow_payload: dict[str, Any] | None = None
            if private_shadow_report.exists():
                try:
                    private_shadow_payload = json.loads(
                        private_shadow_report.read_text(encoding="utf-8")
                    )
                except json.JSONDecodeError:
                    private_shadow_payload = None
            pair_count = (
                int(private_shadow_payload.get("metrics", {}).get("pair_count", 0))
                if private_shadow_payload
                else None
            )
            if private_shadow_map_exists and private_shadow_payload is not None:
                action_id = "private_memory_shadow_contract_maintenance"
                summary = (
                    "Maintain the dedicated private-memory shadow contract and keep nested memory lanes "
                    "out of public cleanup."
                )
                why = (
                    f"{len(unresolved_private_shadow_entries)} deferred private-shadow basename collision is now "
                    f"governed by a dedicated shadow contract; current pair_count={pair_count}."
                )
            else:
                action_id = "private_memory_shadow_boundary"
                summary = "Create a dedicated private-memory shadow boundary before touching nested memory lanes."
                why = (
                    f"{len(unresolved_private_shadow_entries)} same-basename collision still points at a nested "
                    "memory shadow inside protected memory territory."
                )
            actions.append(
                {
                    "id": action_id,
                    "priority": "high",
                    "summary": summary,
                    "why": why,
                    "evidence": [
                        str(item.get("basename")) for item in unresolved_private_shadow_entries[:8]
                    ],
                }
            )

    root_entrypoint_gaps = sorted(
        path for path in (set(missing_purpose) | set(missing_date)) if path in ROOT_AUTHORED_FILES
    )
    if root_entrypoint_gaps:
        actions.append(
            {
                "id": "root_entrypoint_metadata_backfill",
                "priority": "high",
                "summary": "Backfill Purpose and Last Updated metadata on public entrypoint documents.",
                "why": (
                    f"{len(root_entrypoint_gaps)} root entrypoints are still missing Purpose and/or date hints, "
                    "which makes retrieval agents infer scope from prose instead of metadata."
                ),
                "evidence": root_entrypoint_gaps[:8],
            }
        )

    historical_entries = [
        str(entry["path"])
        for entry in entries
        if str(entry["surface_type"]) in {"archive_doc", "chronicle_doc"}
    ]
    if historical_entries:
        historical_report_path = repo_root / HISTORICAL_LANE_STATUS
        historical_payload: dict[str, Any] | None = None
        if historical_report_path.exists():
            try:
                historical_payload = json.loads(historical_report_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                historical_payload = None
        policy_exists = (repo_root / HISTORICAL_LANE_POLICY).exists()
        chronicle_readme_exists = (repo_root / HISTORICAL_CHRONICLE_README).exists()
        chronicle_count = (
            int(historical_payload.get("metrics", {}).get("chronicle_markdown_count", 0))
            if historical_payload
            else None
        )
        if policy_exists and chronicle_readme_exists and historical_payload is not None:
            action_id = "historical_doc_lane_contract_maintenance"
            summary = (
                "Maintain the historical document lane contract so archive and chronicle surfaces "
                "stay governed without per-file manual metadata backfill."
            )
            why = (
                f"{len(historical_entries)} historical-lane docs are now governed by a dedicated policy "
                f"and report; current chronicle_markdown_count={chronicle_count}."
            )
        else:
            action_id = "historical_doc_lane_contract"
            summary = (
                "Create one historical document lane contract for archive and chronicle surfaces "
                "before treating generated historical files as a manual metadata backlog."
            )
            why = (
                f"{len(historical_entries)} docs live under docs/archive or docs/chronicles, "
                "but generated historical files still look like ordinary metadata gaps."
            )
        actions.append(
            {
                "id": action_id,
                "priority": "medium",
                "summary": summary,
                "why": why,
                "evidence": historical_entries[:8],
            }
        )

    paradox_mirrors = by_family.get("paradox_fixture_mirror", [])
    if paradox_mirrors:
        paradox_map_exists = (
            repo_root / "docs/architecture/PARADOX_FIXTURE_OWNERSHIP_MAP.md"
        ).exists()
        paradox_report = repo_root / "docs/status/paradox_fixture_ownership_latest.json"
        paradox_payload: dict[str, Any] | None = None
        if paradox_report.exists():
            try:
                paradox_payload = json.loads(paradox_report.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                paradox_payload = None
        needs_review_count = (
            int(paradox_payload.get("metrics", {}).get("needs_review_count", 0))
            if paradox_payload
            else None
        )
        if paradox_map_exists and paradox_payload is not None:
            action_id = "paradox_fixture_contract_maintenance"
            summary = "Maintain the paradox casebook-to-fixture contract instead of treating all fixture drift as duplication."
            why = (
                f"{len(paradox_mirrors)} paradox fixture basename collisions are now governed by an ownership map; "
                f"current needs_review_count={needs_review_count}."
            )
        else:
            action_id = "paradox_fixture_source_of_truth"
            summary = "Document source-of-truth and sync direction for paradox fixture mirrors."
            why = (
                f"{len(paradox_mirrors)} paradox fixtures exist both in PARADOXES/ and test fixtures; "
                "the repo should state which side is authoritative and whether divergence is intentional."
            )
        actions.append(
            {
                "id": action_id,
                "priority": "medium",
                "summary": summary,
                "why": why,
                "evidence": [str(item["basename"]) for item in paradox_mirrors[:8]],
            }
        )

    return actions


def build_report(repo_root: Path) -> dict[str, Any]:
    entries = _load_entries(repo_root)
    collisions = _build_collisions(entries)
    category_counts = Counter(str(entry["surface_type"]) for entry in entries)
    collision_family_counts = Counter(str(item["family"]) for item in collisions)
    missing_metadata_sample_limit = 40
    missing_purpose = _top_missing_metadata(
        entries, "purpose", repo_root, limit=missing_metadata_sample_limit
    )
    missing_date = _top_missing_metadata(
        entries, "date_hint", repo_root, limit=missing_metadata_sample_limit
    )
    missing_purpose_total = _count_missing_metadata(entries, "purpose", repo_root)
    missing_date_total = _count_missing_metadata(entries, "date_hint", repo_root)
    priority_actions = _build_priority_actions(
        repo_root, entries, collisions, missing_purpose, missing_date
    )

    primary_status_line = (
        "doc_convergence_ready | "
        f"authored_files={len(entries)} collisions={len(collisions)} "
        f"missing_purpose={missing_purpose_total} missing_date={missing_date_total}"
    )
    runtime_status_line = (
        "entrypoints | "
        "doc_inventory=doc_convergence_inventory_latest.json "
        f"largest_family={collision_family_counts.most_common(1)[0][0] if collision_family_counts else 'none'} "
        f"architecture_docs={category_counts.get('architecture_doc', 0)}"
    )
    artifact_policy_status_line = (
        "doc_scope=authored_only | " "content_check=hash_plus_similarity generated_noise=excluded"
    )

    trimmed_entries = [
        {key: value for key, value in entry.items() if key != "canonical_text"} for entry in entries
    ]

    return {
        "generated_at": _iso_now(),
        "scope": {
            "include_roots": sorted(INCLUDE_ROOTS),
            "root_authored_files": sorted(ROOT_AUTHORED_FILES),
            "doc_extensions": sorted(DOC_EXTENSIONS),
            "exclude_parts": sorted(EXCLUDE_PARTS),
            "exclude_prefixes": list(EXCLUDE_PREFIXES),
        },
        "metrics": {
            "authored_file_count": len(entries),
            "collision_count": len(collisions),
            "exact_match_collision_count": sum(1 for item in collisions if item["exact_match"]),
            "divergent_collision_count": sum(1 for item in collisions if item["divergent"]),
            "missing_purpose_count": missing_purpose_total,
            "missing_date_count": missing_date_total,
            "missing_purpose_sample_count": len(missing_purpose),
            "missing_date_sample_count": len(missing_date),
            "missing_metadata_sample_limit": missing_metadata_sample_limit,
        },
        "category_counts": dict(sorted(category_counts.items())),
        "collision_family_counts": dict(sorted(collision_family_counts.items())),
        "missing_metadata": {
            "purpose": missing_purpose,
            "date_hint": missing_date,
        },
        "priority_actions": priority_actions,
        "collisions": collisions,
        "entries": trimmed_entries,
        "primary_status_line": primary_status_line,
        "runtime_status_line": runtime_status_line,
        "artifact_policy_status_line": artifact_policy_status_line,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Document Convergence Inventory Latest",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- primary_status_line: `{payload['primary_status_line']}`",
        f"- runtime_status_line: `{payload['runtime_status_line']}`",
        f"- artifact_policy_status_line: `{payload['artifact_policy_status_line']}`",
        "",
        "## Metrics",
    ]
    for key, value in payload["metrics"].items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(["", "## Category Counts"])
    for key, value in payload["category_counts"].items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(["", "## Collision Families"])
    for key, value in payload["collision_family_counts"].items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(["", "## Priority Actions"])
    for action in payload["priority_actions"]:
        lines.append(f"- `{action['id']}` [`{action['priority']}`] {action['summary']}")
        lines.append(f"  - why: {action['why']}")
        for item in action["evidence"]:
            lines.append(f"  - evidence: `{item}`")

    lines.extend(["", "## Top Missing Purpose Metadata"])
    for path in payload["missing_metadata"]["purpose"]:
        lines.append(f"- `{path}`")

    lines.extend(["", "## Top Missing Date Metadata"])
    for path in payload["missing_metadata"]["date_hint"]:
        lines.append(f"- `{path}`")

    lines.extend(["", "## Basename Collisions"])
    for collision in payload["collisions"][:40]:
        lines.append(
            f"- `{collision['basename']}` [{collision['family']}] "
            f"exact=`{str(collision['exact_match']).lower()}` "
            f"divergent=`{str(collision['divergent']).lower()}` "
            f"max_similarity=`{collision['max_similarity']}`"
        )
        lines.append(f"  - recommendation: {collision['recommendation']}")
        for path in collision["paths"][:8]:
            lines.append(f"  - `{path}`")

    return "\n".join(lines) + "\n"


def render_mermaid(payload: dict[str, Any]) -> str:
    lines = ["graph TD", '    root["Authored Doc Surfaces"]']
    for category, count in sorted(payload["category_counts"].items()):
        node_id = re.sub(r"[^A-Za-z0-9_]", "_", f"category_{category}")
        label = f"{category} ({count})"
        lines.append(f'    {node_id}["{label}"]')
        lines.append(f"    root --> {node_id}")

    lines.append('    collisions["Basename Collisions"]')
    lines.append("    root --> collisions")
    for family, count in sorted(payload["collision_family_counts"].items()):
        node_id = re.sub(r"[^A-Za-z0-9_]", "_", f"family_{family}")
        label = f"{family} ({count})"
        lines.append(f'    {node_id}["{label}"]')
        lines.append(f"    collisions --> {node_id}")
    if payload["priority_actions"]:
        lines.append('    priorities["Priority Actions"]')
        lines.append("    root --> priorities")
        for action in payload["priority_actions"]:
            node_id = re.sub(r"[^A-Za-z0-9_]", "_", f"priority_{action['id']}")
            label = f"{action['id']} ({action['priority']})"
            lines.append(f'    {node_id}["{label}"]')
            lines.append(f"    priorities --> {node_id}")
    return "\n".join(lines) + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inventory authored docs and convergence hotspots."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument(
        "--out-dir", default="docs/status", help="Output directory for generated artifacts."
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    out_dir = (repo_root / args.out_dir).resolve()
    payload = build_report(repo_root)
    _write(out_dir / JSON_FILENAME, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    _write(out_dir / MARKDOWN_FILENAME, render_markdown(payload))
    _write(out_dir / MERMAID_FILENAME, render_mermaid(payload))
    print(
        json.dumps(
            {
                "ok": True,
                "artifacts": {
                    "json": f"{args.out_dir}/{JSON_FILENAME}",
                    "markdown": f"{args.out_dir}/{MARKDOWN_FILENAME}",
                    "mermaid": f"{args.out_dir}/{MERMAID_FILENAME}",
                },
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
