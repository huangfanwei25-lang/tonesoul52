#!/usr/bin/env python3
"""Run a measurable four-pressure convergence audit for ToneSoul."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

JSON_FILENAME = "tonesoul_convergence_audit_latest.json"
MARKDOWN_FILENAME = "tonesoul_convergence_audit_latest.md"

OVERVIEW_SURFACES = [
    {"path": "README.md", "role": "public_entry"},
    {"path": "README.zh-TW.md", "role": "public_entry"},
    {"path": "AI_ONBOARDING.md", "role": "ai_entry"},
    {"path": "docs/README.md", "role": "docs_gateway"},
    {"path": "docs/INDEX.md", "role": "docs_registry"},
    {"path": "docs/AI_QUICKSTART.md", "role": "ai_operational"},
    {"path": "docs/foundation/README.md", "role": "foundation_packet"},
    {"path": "DESIGN.md", "role": "design_center"},
    {
        "path": "docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md",
        "role": "deep_system_map",
    },
]

PRIMARY_FORMULA_SURFACES = [
    "README.md",
    "docs/GLOSSARY.md",
    "docs/MATH_FOUNDATIONS.md",
]

LOCKED_FORMULA_SURFACES = [
    "AGENTS.md",
]

COMMAND_LIKE_TOKENS = (
    "pytest ",
    "ruff check",
    "pip install",
    "python ",
    "git clone",
    "git ",
    "cd ",
)

FORMULA_LABEL_KEYWORDS = (
    "rigorous",
    "heuristic",
    "conceptual",
    "retired",
    "honesty rating",
    "executable owner",
    "runtime truth",
    "概念模型",
    "非精確計算公式",
    "直覺描述",
    "啟發式",
    "以程式碼為準",
    "用在哪",
    "數學基礎",
    "可靠度",
    "誠實問題",
    "計算責任",
    "驗證方式",
    "公式狀態",
    "讀法契約",
    "引用規則",
)

FORMULA_PATTERN = re.compile(
    r"[A-Za-z_][A-Za-z0-9_()\[\].]*\s*=\s*[^=\n]*(?:[+\-/*×^]|cos\(|max\(|min\(|Σ|∑|Δ|α|β|λ)[^=\n]*",
    re.IGNORECASE,
)
OWNER_PATTERN = re.compile(
    r"[A-Za-z0-9_./-]*[A-Za-z0-9_-]+\.(py|ts|tsx|md|json)",
    re.IGNORECASE,
)

LAYER_FAMILIES = [
    {
        "id": "knowledge",
        "paths": ["knowledge", "knowledge_base", "knowledge/compiled"],
        "contracts": [
            "docs/architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md",
            "docs/architecture/TONESOUL_KNOWLEDGE_LAYER_BOUNDARY_CONTRACT.md",
            "docs/architecture/TONESOUL_COMPILED_KNOWLEDGE_LANDING_ZONE_SPEC.md",
        ],
    },
    {
        "id": "memory",
        "paths": ["memory", "memory_base", "OpenClaw-Memory", "tonesoul/memory"],
        "contracts": [
            "docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md",
            "docs/architecture/PRIVATE_MEMORY_SHADOW_BOUNDARY_MAP.md",
            "docs/architecture/TONESOUL_R_MEMORY_STACK_RECOMMENDATION.md",
        ],
    },
    {
        "id": "paradox",
        "paths": ["PARADOXES", "tests/fixtures/paradoxes"],
        "contracts": [
            "docs/architecture/PARADOX_FIXTURE_OWNERSHIP_MAP.md",
            "docs/architecture/TONESOUL_LAW_RUNTIME_BOUNDARY_CONTRACT.md",
        ],
    },
]


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _count_lines(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        return sum(1 for _ in handle)


def _severity(score: int) -> str:
    if score <= 0:
        return "low"
    if score == 1:
        return "medium"
    if score <= 3:
        return "high"
    return "critical"


def _load_authority_metrics(repo_root: Path) -> dict[str, int]:
    try:
        from scripts import run_doc_authority_structure_map as authority_map
    except ModuleNotFoundError:
        script_dir = Path(__file__).resolve().parent
        repo_dir = script_dir.parent
        if str(repo_dir) not in sys.path:
            sys.path.insert(0, str(repo_dir))
        import run_doc_authority_structure_map as authority_map  # type: ignore[no-redef]
    except Exception:
        return {"group_count": 0, "tracked_file_count": 0}

    try:
        payload = authority_map.build_report(repo_root)
        metrics = payload.get("metrics", {})
        return {
            "group_count": int(metrics.get("group_count", 0)),
            "tracked_file_count": int(metrics.get("tracked_file_count", 0)),
        }
    except Exception:
        group_count = len(getattr(authority_map, "GROUPS", []))
        tracked_file_count = sum(
            len(group.get("files", [])) for group in getattr(authority_map, "GROUPS", [])
        )
        return {
            "group_count": int(group_count),
            "tracked_file_count": int(tracked_file_count),
        }


def _normalize_words(text: str) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9_]{4,}", text.lower())}


def _compute_overlap(left: Path, right: Path) -> float:
    left_words = _normalize_words(_read_text(left))
    right_words = _normalize_words(_read_text(right))
    if not left_words or not right_words:
        return 0.0
    union = left_words | right_words
    if not union:
        return 0.0
    return len(left_words & right_words) / len(union)


def _window(lines: list[str], index: int, radius: int = 6) -> str:
    start = max(0, index - radius)
    end = min(len(lines), index + radius + 1)
    return "\n".join(lines[start:end])


def _looks_like_command(line: str) -> bool:
    lowered = line.lower()
    return any(token in lowered for token in COMMAND_LIKE_TOKENS)


def _build_duplication_area(repo_root: Path) -> dict[str, Any]:
    surfaces: list[dict[str, Any]] = []
    labeled_surface_count = 0

    for surface in OVERVIEW_SURFACES:
        path = repo_root / surface["path"]
        if not path.exists():
            continue
        header = "\n".join(_read_text(path).splitlines()[:20]).lower()
        labeled = any(
            token in header
            for token in (
                "purpose:",
                "status:",
                "guided gateway",
                "full registry",
                "design center",
                "foundation layer",
                "operational",
                "historical",
                "mirror",
            )
        )
        if labeled:
            labeled_surface_count += 1
        surfaces.append(
            {
                "path": surface["path"],
                "role": surface["role"],
                "labeled": labeled,
            }
        )

    overlap_rows = []
    for index, left in enumerate(surfaces):
        left_path = repo_root / left["path"]
        for right in surfaces[index + 1 :]:
            right_path = repo_root / right["path"]
            overlap_rows.append(
                {
                    "pair": [left["path"], right["path"]],
                    "similarity": round(_compute_overlap(left_path, right_path), 3),
                }
            )
    overlap_rows.sort(key=lambda item: item["similarity"], reverse=True)
    top_overlap_pairs = overlap_rows[:3]
    entry_like_count = sum(
        1
        for surface in surfaces
        if surface["role"]
        in {
            "public_entry",
            "ai_entry",
            "docs_gateway",
            "docs_registry",
            "ai_operational",
            "foundation_packet",
        }
    )
    label_coverage = labeled_surface_count / len(surfaces) if surfaces else 1.0
    max_overlap = top_overlap_pairs[0]["similarity"] if top_overlap_pairs else 0.0

    score = 0
    if len(surfaces) >= 9:
        score += 2
    elif len(surfaces) >= 7:
        score += 1
    if entry_like_count >= 6:
        score += 1
    if max_overlap >= 0.3:
        score += 1
    if label_coverage >= 0.85:
        score -= 1

    return {
        "key": "duplication",
        "title": "Duplication",
        "severity_score": score,
        "severity": _severity(score),
        "summary": (
            "Overview and entry surfaces are still structurally numerous, but most of them now "
            "self-label their role instead of silently competing for ownership."
        ),
        "metrics": {
            "overview_surface_count": len(surfaces),
            "entry_like_surface_count": entry_like_count,
            "labeled_surface_count": labeled_surface_count,
            "label_coverage": round(label_coverage, 3),
            "max_pairwise_overlap": round(max_overlap, 3),
        },
        "evidence": [
            f"tracked overview surfaces={len(surfaces)}",
            f"entry-like surfaces={entry_like_count}",
            f"labeled surfaces={labeled_surface_count}",
        ],
        "samples": top_overlap_pairs,
        "next_move": "Keep one owner per overview class and reject new repo-wide explainers unless one old owner is demoted.",
    }


def _build_context_bloat_area(repo_root: Path) -> dict[str, Any]:
    markdown_file_count = sum(1 for _ in (repo_root / "docs").glob("**/*.md"))
    plan_file_count = sum(1 for _ in (repo_root / "docs" / "plans").glob("*.md"))
    authority = _load_authority_metrics(repo_root)

    python_files = list((repo_root / "tonesoul").glob("**/*.py"))
    large_files = [
        {"path": path.relative_to(repo_root).as_posix(), "line_count": _count_lines(path)}
        for path in python_files
    ]
    large_files.sort(key=lambda item: item["line_count"], reverse=True)
    top_large_files = large_files[:5]
    files_over_2000 = sum(1 for item in large_files if item["line_count"] >= 2000)

    score = 0
    if markdown_file_count >= 500:
        score += 2
    if plan_file_count >= 150:
        score += 1
    if authority["group_count"] >= 20:
        score += 1
    if files_over_2000 >= 2:
        score += 1

    return {
        "key": "context_bloat",
        "title": "Context Bloat",
        "severity_score": score,
        "severity": _severity(score),
        "summary": (
            "Context load is objectively high: the repo carries a very large docs surface and at "
            "least two runtime modules now exceed 2000 lines."
        ),
        "metrics": {
            "docs_markdown_file_count": markdown_file_count,
            "docs_plan_file_count": plan_file_count,
            "doc_authority_group_count": authority["group_count"],
            "doc_authority_tracked_file_count": authority["tracked_file_count"],
            "python_files_over_2000_lines": files_over_2000,
        },
        "evidence": [
            f"docs/**/*.md={markdown_file_count}",
            f"docs/plans/*.md={plan_file_count}",
            f"doc authority groups={authority['group_count']}",
            f"python files >=2000 lines={files_over_2000}",
        ],
        "samples": top_large_files,
        "next_move": "Hold the first-hop path fixed and split the largest runtime files only after boundary and entry pressure stay stable.",
    }


def _build_pseudo_formula_area(repo_root: Path) -> dict[str, Any]:
    hits: list[dict[str, Any]] = []
    gap_samples: list[dict[str, Any]] = []
    locked_hits: list[dict[str, Any]] = []

    for rel_path in PRIMARY_FORMULA_SURFACES:
        path = repo_root / rel_path
        if not path.exists():
            continue
        lines = _read_text(path).splitlines()
        for index, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("| ---") or stripped.startswith("```"):
                continue
            if _looks_like_command(stripped):
                continue
            if not FORMULA_PATTERN.search(stripped):
                continue

            window = _window(lines, index)
            window_lower = window.lower()
            labeled = any(keyword in window_lower for keyword in FORMULA_LABEL_KEYWORDS)
            owner_linked = bool(OWNER_PATTERN.search(window))
            hit = {
                "path": rel_path,
                "line": index + 1,
                "labeled": labeled,
                "owner_linked": owner_linked,
                "text": stripped[:160],
            }
            hits.append(hit)
            if not labeled or not owner_linked:
                gap_samples.append(hit)

    for rel_path in LOCKED_FORMULA_SURFACES:
        path = repo_root / rel_path
        if not path.exists():
            continue
        lines = _read_text(path).splitlines()
        for index, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("| ---") or stripped.startswith("```"):
                continue
            if _looks_like_command(stripped):
                continue
            if not FORMULA_PATTERN.search(stripped):
                continue

            window = _window(lines, index)
            locked_hits.append(
                {
                    "path": rel_path,
                    "line": index + 1,
                    "labeled": any(keyword in window.lower() for keyword in FORMULA_LABEL_KEYWORDS),
                    "owner_linked": bool(OWNER_PATTERN.search(window)),
                }
            )

    labeled_count = sum(1 for hit in hits if hit["labeled"])
    owner_linked_count = sum(1 for hit in hits if hit["owner_linked"])
    unlabeled_count = sum(1 for hit in hits if not hit["labeled"])
    owner_gap_count = sum(1 for hit in hits if not hit["owner_linked"])
    total_hits = len(hits)
    unlabeled_ratio = unlabeled_count / total_hits if total_hits else 0.0
    owner_gap_ratio = owner_gap_count / total_hits if total_hits else 0.0

    score = 0
    if unlabeled_ratio >= 0.25:
        score += 1
    if owner_gap_ratio >= 0.5:
        score += 1

    return {
        "key": "pseudo_formulas",
        "title": "Pseudo-Formulas",
        "severity_score": score,
        "severity": _severity(score),
        "summary": (
            "Formula honesty improved in the main entry and glossary surfaces, but some formula "
            "mentions still float without a nearby status label or executable owner reference."
        ),
        "metrics": {
            "formula_hit_count": total_hits,
            "labeled_formula_count": labeled_count,
            "owner_linked_formula_count": owner_linked_count,
            "unlabeled_formula_count": unlabeled_count,
            "owner_gap_count": owner_gap_count,
            "unlabeled_ratio": round(unlabeled_ratio, 3),
            "owner_gap_ratio": round(owner_gap_ratio, 3),
            "locked_instruction_formula_hit_count": len(locked_hits),
            "locked_instruction_owner_gap_count": sum(
                1 for hit in locked_hits if not hit["owner_linked"]
            ),
        },
        "evidence": [
            f"formula hits={total_hits}",
            f"labeled hits={labeled_count}",
            f"owner-linked hits={owner_linked_count}",
            f"locked instruction residual hits={len(locked_hits)} (not scored)",
        ],
        "samples": gap_samples[:5],
        "next_move": "Require status plus owner in the same local formula window before repeating a symbolic equation as runtime truth.",
    }


def _build_layer_confusion_area(repo_root: Path) -> dict[str, Any]:
    family_rows = []
    multi_surface_count = 0
    missing_contract_count = 0
    total_existing_surfaces = 0

    for family in LAYER_FAMILIES:
        existing_paths = [path for path in family["paths"] if (repo_root / path).exists()]
        existing_contracts = [
            contract for contract in family["contracts"] if (repo_root / contract).exists()
        ]
        total_existing_surfaces += len(existing_paths)
        if len(existing_paths) >= 2:
            multi_surface_count += 1
        if existing_paths and not existing_contracts:
            missing_contract_count += 1
        family_rows.append(
            {
                "family": family["id"],
                "surface_count": len(existing_paths),
                "contract_count": len(existing_contracts),
                "surfaces": existing_paths,
            }
        )

    score = 0
    if multi_surface_count >= 2:
        score += 2
    if total_existing_surfaces >= 7:
        score += 1
    if missing_contract_count > 0:
        score += 1

    return {
        "key": "layer_confusion",
        "title": "Layer Confusion",
        "severity_score": score,
        "severity": _severity(score),
        "summary": (
            "Multiple knowledge, memory, and paradox lanes still coexist at the filesystem level. "
            "Boundary contracts exist for the main families, but the hierarchy remains cognitively expensive."
        ),
        "metrics": {
            "family_count": len(family_rows),
            "family_count_with_multiple_surfaces": multi_surface_count,
            "family_count_missing_contracts": missing_contract_count,
            "tracked_layer_surface_count": total_existing_surfaces,
        },
        "evidence": [
            f"layer families={len(family_rows)}",
            f"families with >=2 surfaces={multi_surface_count}",
            f"tracked layer surfaces={total_existing_surfaces}",
        ],
        "samples": family_rows,
        "next_move": "Treat boundary contracts as required companions for any rename, merge, or promotion across knowledge-like lanes.",
    }


def build_report(repo_root: Path) -> dict[str, Any]:
    areas = [
        _build_duplication_area(repo_root),
        _build_context_bloat_area(repo_root),
        _build_pseudo_formula_area(repo_root),
        _build_layer_confusion_area(repo_root),
    ]
    areas.sort(key=lambda area: area["severity_score"], reverse=True)
    top_area = areas[0]["key"] if areas else "none"
    return {
        "generated_at": _iso_now(),
        "source": "scripts/run_tonesoul_convergence_audit.py",
        "summary": {
            "area_count": len(areas),
            "top_risk": top_area,
            "critical_count": sum(1 for area in areas if area["severity"] == "critical"),
            "high_count": sum(1 for area in areas if area["severity"] == "high"),
        },
        "areas": areas,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# ToneSoul Convergence Audit Latest",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- source: `{payload['source']}`",
        f"- top_risk: `{payload['summary']['top_risk']}`",
        f"- critical_count: `{payload['summary']['critical_count']}`",
        f"- high_count: `{payload['summary']['high_count']}`",
        "",
        "| area | severity | summary |",
        "| --- | --- | --- |",
    ]
    for area in payload["areas"]:
        lines.append(f"| {area['key']} | {area['severity'].upper()} | {area['summary']} |")

    for area in payload["areas"]:
        lines.extend(["", f"## {area['title']}", "", f"- severity: `{area['severity']}`"])
        for key, value in area["metrics"].items():
            lines.append(f"- `{key}`: `{value}`")
        lines.append("- evidence:")
        for item in area["evidence"]:
            lines.append(f"  - {item}")
        if area["samples"]:
            lines.append("- samples:")
            for sample in area["samples"]:
                lines.append(f"  - `{json.dumps(sample, ensure_ascii=False)}`")
        lines.append(f"- next_move: {area['next_move']}")

    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the four-pressure convergence audit and write status artifacts."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--out-dir", default="docs/status", help="Artifact output directory.")
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
