#!/usr/bin/env python3
"""Publish a compact semantic atlas for remembering the ToneSoul repo."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.memory.subjectivity_handoff import build_handoff_surface  # noqa: E402

JSON_FILENAME = "repo_semantic_atlas_latest.json"
MARKDOWN_FILENAME = "repo_semantic_atlas_latest.md"
MERMAID_FILENAME = "repo_semantic_atlas_latest.mmd"

STATUS_SURFACES: dict[str, str] = {
    "repo_healthcheck": "docs/status/repo_healthcheck_latest.json",
    "dream_observability": "docs/status/dream_observability_latest.json",
    "weekly_host": "docs/status/true_verification_weekly/true_verification_task_status_latest.json",
    "scribe_status": "docs/status/scribe_status_latest.json",
    "subjectivity_review": "docs/status/subjectivity_review_batch_latest.json",
    "repo_governance_settlement": "docs/status/repo_governance_settlement_latest.json",
    "agent_integrity": "docs/status/agent_integrity_latest.json",
    "runtime_source_change_groups": "docs/status/runtime_source_change_groups_latest.json",
}

ALIAS_SEEDS: tuple[dict[str, str], ...] = (
    {
        "alias": "ToneSoul Chronicles",
        "kind": "chronicle_collection",
        "path": "docs/chronicles/",
        "memory_hook": "chronicle_root",
        "reason": "Chronicle lane for internal-state documents and Scribe output.",
    },
    {
        "alias": "ToneSoul Scribe",
        "kind": "scribe_runtime",
        "path": "tonesoul/scribe/",
        "memory_hook": "chronicle_writer",
        "reason": "Chronicle generation, grounding guardrails, and status surface.",
    },
    {
        "alias": "Wakeup Dream Loop",
        "kind": "wakeup_runtime",
        "path": "tonesoul/wakeup_loop.py",
        "memory_hook": "wake_dream_consolidate_report",
        "reason": "Autonomous wakeup cadence, consolidation, and Scribe trigger gate.",
    },
    {
        "alias": "Weekly True Verification",
        "kind": "weekly_governance",
        "path": "docs/status/true_verification_weekly/true_verification_task_status_latest.json",
        "memory_hook": "host_facing_weekly_posture",
        "reason": "Weekly runtime posture, handoff summary, and host-facing governance line.",
    },
    {
        "alias": "Subjectivity Review",
        "kind": "subjectivity_governance",
        "path": "docs/status/subjectivity_review_batch_latest.json",
        "memory_hook": "subjectivity_focus",
        "reason": "Admissibility, operator review posture, and review grouping surface.",
    },
    {
        "alias": "Market Mirror",
        "kind": "market_mirror",
        "path": "tonesoul/market/world_model.py",
        "memory_hook": "parallel_lane_not_core",
        "reason": "Plurality-style market world model kept outside ToneSoul core ontology.",
    },
)

NEIGHBORHOOD_SEEDS: tuple[dict[str, object], ...] = (
    {
        "id": "wakeup_dream",
        "label": "Wakeup / Dream Loop",
        "memory_hook": "wake_dream_consolidate_report",
        "canonical_paths": [
            "tonesoul/wakeup_loop.py",
            "tonesoul/autonomous_cycle.py",
            "tonesoul/dream_observability.py",
        ],
        "status_surfaces": [
            STATUS_SURFACES["dream_observability"],
            STATUS_SURFACES["repo_healthcheck"],
        ],
        "neighbors": ["scribe_chronicle", "weekly_host", "repo_governance"],
    },
    {
        "id": "scribe_chronicle",
        "label": "Scribe / Chronicle",
        "memory_hook": "internal_state_documents",
        "canonical_paths": [
            "tonesoul/scribe/scribe_engine.py",
            "tonesoul/scribe/narrative_builder.py",
            "docs/chronicles/",
        ],
        "status_surfaces": [
            STATUS_SURFACES["scribe_status"],
            STATUS_SURFACES["dream_observability"],
        ],
        "neighbors": ["wakeup_dream", "weekly_host", "subjectivity_review"],
    },
    {
        "id": "weekly_host",
        "label": "True Verification Weekly",
        "memory_hook": "host_facing_weekly_posture",
        "canonical_paths": [
            "tonesoul/true_verification_summary.py",
            "scripts/report_true_verification_task_status.py",
            "docs/status/true_verification_weekly/",
        ],
        "status_surfaces": [
            STATUS_SURFACES["weekly_host"],
            STATUS_SURFACES["repo_healthcheck"],
        ],
        "neighbors": [
            "wakeup_dream",
            "scribe_chronicle",
            "subjectivity_review",
            "repo_governance",
        ],
    },
    {
        "id": "subjectivity_review",
        "label": "Subjectivity Review",
        "memory_hook": "reviewable_subjectivity",
        "canonical_paths": [
            "scripts/run_subjectivity_review_batch.py",
            "tonesoul/memory/subjectivity_handoff.py",
            "docs/status/subjectivity_review_batch_latest.json",
        ],
        "status_surfaces": [
            STATUS_SURFACES["subjectivity_review"],
            STATUS_SURFACES["repo_healthcheck"],
        ],
        "neighbors": ["weekly_host", "scribe_chronicle", "repo_governance"],
    },
    {
        "id": "repo_governance",
        "label": "Repo Governance",
        "memory_hook": "integrated_governance_surface",
        "canonical_paths": [
            "scripts/run_repo_healthcheck.py",
            "scripts/run_repo_governance_settlement_report.py",
            "scripts/run_repo_intelligence_report.py",
        ],
        "status_surfaces": [
            STATUS_SURFACES["repo_healthcheck"],
            STATUS_SURFACES["repo_governance_settlement"],
            STATUS_SURFACES["agent_integrity"],
            STATUS_SURFACES["runtime_source_change_groups"],
        ],
        "neighbors": [
            "weekly_host",
            "wakeup_dream",
            "subjectivity_review",
            "market_mirror",
        ],
    },
    {
        "id": "market_mirror",
        "label": "Market Mirror",
        "memory_hook": "parallel_lane_not_core",
        "canonical_paths": [
            "tonesoul/market/world_model.py",
            "tests/test_market_world_model.py",
            "docs/plans/tonesoul_market_boundary_subjecthood_note_2026-03-12.md",
        ],
        "status_surfaces": [
            STATUS_SURFACES["repo_healthcheck"],
        ],
        "neighbors": ["repo_governance"],
    },
)

BIOLOGY_BASIS: tuple[dict[str, str], ...] = (
    {
        "principle": "hippocampal_indexing",
        "source": "Goode et al., 2020, Neuron",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC7486247/",
        "takeaway": "Memory recall works through compact indices that route back to richer distributed traces.",
    },
    {
        "principle": "encoding_retrieval_match",
        "source": "Ritchey et al., 2013, Cerebral Cortex",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC3827709/",
        "takeaway": "Recall succeeds when retrieval cues match the structure of the original encoding.",
    },
    {
        "principle": "replay_prioritizes_weak_traces",
        "source": "Schapiro et al., 2018, Nature Communications",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6156217/",
        "takeaway": "Replay preferentially strengthens weakly learned memories instead of only the strongest ones.",
    },
)

AI_RETRIEVAL_BASIS: tuple[dict[str, str], ...] = (
    {
        "principle": "parametric_plus_non_parametric_memory",
        "source": "Lewis et al., 2020, RAG",
        "url": "https://arxiv.org/abs/2005.11401",
        "takeaway": "Good retrieval systems combine internal model knowledge with explicit external memory.",
    },
    {
        "principle": "dense_semantic_retrieval",
        "source": "Karpukhin et al., 2020, DPR",
        "url": "https://arxiv.org/abs/2004.04906",
        "takeaway": "Dense retrieval is useful when the query and the target share semantics more than exact keywords.",
    },
    {
        "principle": "late_interaction_detail_preservation",
        "source": "Khattab and Zaharia, 2020, ColBERT",
        "url": "https://arxiv.org/abs/2004.12832",
        "takeaway": "Retain detail after retrieval instead of collapsing all evidence into one coarse score too early.",
    },
    {
        "principle": "hierarchical_summary_retrieval",
        "source": "Sarthi et al., 2024, RAPTOR",
        "url": "https://arxiv.org/abs/2401.18059",
        "takeaway": "Long repositories benefit from layered retrieval, not only flat chunk search.",
    },
    {
        "principle": "retriever_pretraining_and_modularity",
        "source": "Guu et al., 2020, REALM",
        "url": "https://arxiv.org/abs/2002.08909",
        "takeaway": "Retrieval should stay modular and inspectable instead of disappearing entirely inside weights.",
    },
    {
        "principle": "protocol_recognition_seam",
        "source": "Sia et al., 2024, NeurIPS",
        "url": "https://proceedings.neurips.cc/paper_files/paper/2024/file/3979818cdc7bc8dbeec87170c11ee340-Paper-Conference.pdf",
        "takeaway": "A structured protocol can become an internal routing seam, after which later computation may rely less on replaying the full context.",
    },
)

MEMORY_LAYERS: tuple[dict[str, str], ...] = (
    {
        "layer": "episodic_recent",
        "description": "Timestamped chronicles, wakeup outputs, and run-specific state.",
        "repo_examples": "docs/chronicles/, docs/status/dream_observability_latest.json",
    },
    {
        "layer": "semantic_stable",
        "description": "Canonical entrypoints, lane identities, and long-lived architectural meaning.",
        "repo_examples": "repo_semantic_atlas_latest.json, docs/status/README.md, docs/plans/*",
    },
    {
        "layer": "governance_index",
        "description": "Compact latest surfaces that bridge stable meaning and current posture.",
        "repo_examples": "repo_healthcheck_latest.json, scribe_status_latest.json, agent_integrity_latest.json",
    },
)

RETRIEVAL_PROTOCOL: tuple[dict[str, str], ...] = (
    {
        "id": "alias_first",
        "rule": "Resolve remembered phrases or metaphors to semantic aliases before raw file search.",
        "why": "Biological recall begins with an index or cue, not a brute-force scan.",
    },
    {
        "id": "neighborhood_before_file",
        "rule": "Select the semantic neighborhood before opening individual files.",
        "why": "The lane provides context, role, and likely neighboring files.",
    },
    {
        "id": "status_surface_before_source",
        "rule": "Prefer source-declared latest status artifacts before reopening raw implementation files.",
        "why": "Current posture should come from the designated surface, not from re-inference.",
    },
    {
        "id": "encoding_retrieval_match",
        "rule": "Match the query to lane, role, and time horizon before relying on keywords alone.",
        "why": "Retrieval works better when its cues resemble the original encoding structure.",
    },
    {
        "id": "one_hop_expansion",
        "rule": "Expand only one hop through semantic neighbors before broader graph or grep expansion.",
        "why": "Controlled expansion keeps recall relevant and avoids graph sprawl.",
    },
    {
        "id": "weak_trace_promotion",
        "rule": "If humans repeatedly recall a fuzzy phrase, promote it into a stable alias or memory hook.",
        "why": "Replay should strengthen weak but important traces.",
    },
    {
        "id": "episodic_semantic_split",
        "rule": "Keep recent episodic artifacts separate from stable semantic entrypoints.",
        "why": "Do not confuse the latest run with the lasting identity of the lane.",
    },
    {
        "id": "reconsolidate_after_success",
        "rule": "After successful retrieval, update the atlas or note structure instead of relying on conversation memory alone.",
        "why": "Successful retrieval should harden the next retrieval path.",
    },
)

NAMING_RULES: tuple[dict[str, str], ...] = (
    {
        "id": "stable_lane_name",
        "rule": "Every major lane should have one stable, human-rememberable alias.",
    },
    {
        "id": "canonical_entrypoint",
        "rule": "Every lane should identify one canonical path and one latest status surface.",
    },
    {
        "id": "memory_hook",
        "rule": "Every alias should include a short memory hook explaining why it matters.",
    },
    {
        "id": "neighbor_contract",
        "rule": "Every lane should declare its closest semantic neighbors.",
    },
)

DOCUMENT_SUFFIXES = {".md", ".json", ".mmd", ".jsonl", ".html"}
NEIGHBORHOOD_KEYWORDS: dict[str, tuple[str, ...]] = {
    "wakeup_dream": ("wakeup", "dream", "autonomous", "registry_schedule"),
    "scribe_chronicle": ("scribe", "chronicle"),
    "weekly_host": ("true_verification", "weekly", "host_tick"),
    "subjectivity_review": ("subjectivity", "admissibility"),
    "repo_governance": (
        "repo_healthcheck",
        "repo_governance",
        "repo_intelligence",
        "refreshable",
        "agent_integrity",
    ),
    "market_mirror": ("market", "world_model", "plurality"),
}


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def _extract_markdown_title(path: Path) -> str:
    try:
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if line.startswith("# "):
                return line[2:].strip()
    except OSError:
        return path.stem
    return path.stem


def _chronicle_entries(repo_root: Path) -> list[dict[str, str]]:
    chronicle_dir = repo_root / "docs" / "chronicles"
    if not chronicle_dir.exists():
        return []
    entries: list[dict[str, str]] = []
    for path in sorted(chronicle_dir.glob("*.md")):
        entries.append(
            {
                "path": str(path.relative_to(repo_root)).replace("\\", "/"),
                "title": _extract_markdown_title(path),
                "stem": path.stem,
            }
        )
    return entries


def _normalize_document_stem(path: Path) -> str:
    stem = path.stem
    stem = re.sub(r"_\d{8}_\d{6}$", "", stem)
    stem = re.sub(r"_\d{4}-\d{2}-\d{2}$", "", stem)
    stem = re.sub(r"_latest$", "", stem)
    stem = re.sub(r"_addendum$", "", stem)
    parent = path.parent.name
    if parent not in {"docs", "plans", "status", "chronicles"}:
        stem = f"{parent}_{stem}"
    return stem


def _linked_neighborhoods(semantic_key: str) -> list[str]:
    linked: list[str] = []
    for neighborhood_id, keywords in NEIGHBORHOOD_KEYWORDS.items():
        if any(keyword in semantic_key for keyword in keywords):
            linked.append(neighborhood_id)
    return linked


def _document_threads(repo_root: Path) -> list[dict[str, object]]:
    docs_root = repo_root / "docs"
    if not docs_root.exists():
        return []
    grouped: dict[str, dict[str, object]] = {}
    semantic_index: dict[str, list[str]] = {}
    for path in sorted(docs_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in DOCUMENT_SUFFIXES:
            continue
        rel_path = str(path.relative_to(repo_root)).replace("\\", "/")
        doc_relative_parts = path.relative_to(docs_root).parts
        if not doc_relative_parts or len(doc_relative_parts) == 1:
            category = "docs"
        else:
            category = doc_relative_parts[0]
        semantic_key = _normalize_document_stem(path)
        thread_id = f"{category}/{semantic_key}"
        if thread_id not in grouped:
            grouped[thread_id] = {
                "thread_id": thread_id,
                "category": category,
                "semantic_key": semantic_key,
                "linked_neighborhoods": _linked_neighborhoods(semantic_key),
                "paths": [],
            }
        grouped[thread_id]["paths"].append(rel_path)
        semantic_index.setdefault(semantic_key, []).append(thread_id)

    threads: list[dict[str, object]] = []
    for thread_id in sorted(grouped):
        item = grouped[thread_id]
        cross_directory_threads = sorted(
            sibling
            for sibling in semantic_index.get(str(item["semantic_key"]), [])
            if sibling != thread_id
        )
        threads.append(
            {
                "thread_id": thread_id,
                "category": item["category"],
                "semantic_key": item["semantic_key"],
                "path_count": len(item["paths"]),
                "paths": item["paths"],
                "linked_neighborhoods": item["linked_neighborhoods"],
                "cross_directory_threads": cross_directory_threads,
            }
        )
    return threads


def _semantic_aliases(
    repo_root: Path, chronicle_entries: list[dict[str, str]]
) -> list[dict[str, object]]:
    aliases: list[dict[str, object]] = [dict(item) for item in ALIAS_SEEDS]
    if chronicle_entries:
        first = chronicle_entries[0]
        latest = chronicle_entries[-1]
        aliases[0]["first_title"] = first["title"]
        aliases[0]["first_path"] = first["path"]
        aliases[0]["latest_title"] = latest["title"]
        aliases[0]["latest_path"] = latest["path"]
        aliases[0]["entry_count"] = len(chronicle_entries)
        aliases.append(
            {
                "alias": first["title"],
                "kind": "specific_chronicle",
                "path": first["path"],
                "memory_hook": "first_tonesoul_chronicle",
                "reason": "Earliest chronicle title currently present in docs/chronicles.",
            }
        )
    for alias in aliases:
        alias["available"] = (repo_root / str(alias["path"])).exists()
    return aliases


def _semantic_neighborhoods(repo_root: Path) -> list[dict[str, object]]:
    neighborhoods: list[dict[str, object]] = []
    for seed in NEIGHBORHOOD_SEEDS:
        canonical_paths = [str(path) for path in seed["canonical_paths"]]
        status_surfaces = [str(path) for path in seed["status_surfaces"]]
        neighborhoods.append(
            {
                "id": seed["id"],
                "label": seed["label"],
                "memory_hook": seed["memory_hook"],
                "canonical_paths": canonical_paths,
                "available_path_count": sum(
                    (repo_root / path).exists() for path in canonical_paths
                ),
                "status_surfaces": status_surfaces,
                "available_surface_count": sum(
                    (repo_root / path).exists() for path in status_surfaces
                ),
                "neighbors": list(seed["neighbors"]),
            }
        )
    return neighborhoods


def _graph_edges() -> list[dict[str, str]]:
    return [
        {
            "source": "wakeup_dream",
            "target": "scribe_chronicle",
            "relation": "writes_internal_state",
        },
        {
            "source": "wakeup_dream",
            "target": "weekly_host",
            "relation": "feeds_weekly_handoff",
        },
        {
            "source": "scribe_chronicle",
            "target": "weekly_host",
            "relation": "mirrors_chronicle_posture",
        },
        {
            "source": "weekly_host",
            "target": "repo_governance",
            "relation": "feeds_governance_summary",
        },
        {
            "source": "subjectivity_review",
            "target": "weekly_host",
            "relation": "adds_admissibility_context",
        },
        {
            "source": "subjectivity_review",
            "target": "repo_governance",
            "relation": "feeds_review_governance",
        },
        {
            "source": "market_mirror",
            "target": "repo_governance",
            "relation": "parallel_lane_not_core",
        },
    ]


def build_report(repo_root: Path) -> dict[str, Any]:
    chronicle_entries = _chronicle_entries(repo_root)
    document_threads = _document_threads(repo_root)
    aliases = _semantic_aliases(repo_root, chronicle_entries)
    neighborhoods = _semantic_neighborhoods(repo_root)
    graph_edges = _graph_edges()
    latest_title = chronicle_entries[-1]["title"] if chronicle_entries else ""
    search_contract = {
        "version": "2026-03-16",
        "objective": "backend_agnostic_repo_retrieval",
        "memory_layers": [dict(item) for item in MEMORY_LAYERS],
        "naming_rules": [dict(item) for item in NAMING_RULES],
        "retrieval_protocol": [dict(item) for item in RETRIEVAL_PROTOCOL],
    }
    primary_status_line = (
        "repo_semantic_atlas_ready | "
        f"aliases={len(aliases)} neighborhoods={len(neighborhoods)} "
        f"chronicles={len(chronicle_entries)} doc_threads={len(document_threads)} "
        f"rules={len(RETRIEVAL_PROTOCOL)} "
        f"graph_edges={len(graph_edges)}"
    )
    runtime_status_line = (
        "entrypoints | "
        "atlas=repo_semantic_atlas_latest.json "
        "repo=repo_healthcheck_latest.json "
        "dream=dream_observability_latest.json "
        "weekly=true_verification_task_status_latest.json "
        "scribe=scribe_status_latest.json "
        "protocol=alias_first"
    )
    artifact_policy_status_line = (
        "semantic_map=domain_level | aliases=source_declared "
        "graph=passive_no_reparse protocol=backend_agnostic"
    )
    return {
        "generated_at": _iso_now(),
        "status": "ready",
        "chronicle_memory": {
            "collection_path": "docs/chronicles/",
            "entry_count": len(chronicle_entries),
            "first_entry": chronicle_entries[0] if chronicle_entries else None,
            "latest_entry": chronicle_entries[-1] if chronicle_entries else None,
            "recent_entries": chronicle_entries[-5:],
        },
        "biology_basis": [dict(item) for item in BIOLOGY_BASIS],
        "ai_retrieval_basis": [dict(item) for item in AI_RETRIEVAL_BASIS],
        "search_contract": search_contract,
        "semantic_aliases": aliases,
        "semantic_neighborhoods": neighborhoods,
        "document_threads": document_threads,
        "graph_edges": graph_edges,
        "summary": {
            "alias_count": len(aliases),
            "neighborhood_count": len(neighborhoods),
            "chronicle_entry_count": len(chronicle_entries),
            "document_thread_count": len(document_threads),
            "graph_edge_count": len(graph_edges),
            "retrieval_rule_count": len(RETRIEVAL_PROTOCOL),
            "latest_chronicle_title": latest_title,
        },
        "primary_status_line": primary_status_line,
        "runtime_status_line": runtime_status_line,
        "artifact_policy_status_line": artifact_policy_status_line,
        "handoff": build_handoff_surface(
            queue_shape="repo_semantic_atlas_ready",
            requires_operator_action=False,
            status_lines=[
                primary_status_line,
                runtime_status_line,
                artifact_policy_status_line,
            ],
            extra_fields={
                "preferred_first_neighborhood": "repo_governance",
                "chronicle_collection_path": "docs/chronicles/",
                "retrieval_protocol": "alias_first",
            },
        ),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    chronicle_memory = payload["chronicle_memory"]
    handoff = payload.get("handoff") or {}
    lines = [
        "# Repo Semantic Atlas Latest",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- status: {payload['status']}",
        f"- primary_status_line: `{payload['primary_status_line']}`",
        f"- runtime_status_line: `{payload['runtime_status_line']}`",
        f"- artifact_policy_status_line: `{payload['artifact_policy_status_line']}`",
        "",
        "## Chronicle Memory",
        f"- collection_path: `{chronicle_memory['collection_path']}`",
        f"- entry_count: `{chronicle_memory['entry_count']}`",
    ]
    first_entry = chronicle_memory.get("first_entry")
    latest_entry = chronicle_memory.get("latest_entry")
    if isinstance(first_entry, dict):
        lines.append(
            f"- first_entry: `{first_entry.get('title', '')}` -> `{first_entry.get('path', '')}`"
        )
    if isinstance(latest_entry, dict):
        lines.append(
            f"- latest_entry: `{latest_entry.get('title', '')}` -> `{latest_entry.get('path', '')}`"
        )

    lines.extend(["", "## Search Contract"])
    for item in payload["search_contract"]["retrieval_protocol"]:
        lines.append(f"- `{item['id']}`: {item['rule']}")
        lines.append(f"  - why: {item['why']}")

    lines.extend(["", "## Memory Layers"])
    for item in payload["search_contract"]["memory_layers"]:
        lines.append(f"- `{item['layer']}`: {item['description']}")
        lines.append(f"  - repo_examples: `{item['repo_examples']}`")

    lines.extend(["", "## Naming Rules"])
    for item in payload["search_contract"]["naming_rules"]:
        lines.append(f"- `{item['id']}`: {item['rule']}")

    lines.extend(["", "## Biology Basis"])
    for item in payload["biology_basis"]:
        lines.append(f"- `{item['principle']}`: {item['takeaway']}")
        lines.append(f"  - source: {item['source']} <{item['url']}>")

    lines.extend(["", "## AI Retrieval Basis"])
    for item in payload["ai_retrieval_basis"]:
        lines.append(f"- `{item['principle']}`: {item['takeaway']}")
        lines.append(f"  - source: {item['source']} <{item['url']}>")

    lines.extend(["", "## Semantic Aliases"])
    for alias in payload["semantic_aliases"]:
        lines.extend(
            [
                f"- `{alias['alias']}`",
                f"  - kind: `{alias['kind']}`",
                f"  - path: `{alias['path']}`",
                f"  - memory_hook: `{alias['memory_hook']}`",
                f"  - available: `{str(alias['available']).lower()}`",
                f"  - reason: {alias['reason']}",
            ]
        )
        if alias.get("first_title"):
            lines.append(f"  - first_title: {alias['first_title']}")
        if alias.get("latest_title"):
            lines.append(f"  - latest_title: {alias['latest_title']}")

    lines.extend(["", "## Semantic Neighborhoods"])
    for item in payload["semantic_neighborhoods"]:
        lines.extend(
            [
                f"- `{item['label']}`",
                f"  - id: `{item['id']}`",
                f"  - memory_hook: `{item['memory_hook']}`",
                "  - canonical_paths: "
                + ", ".join(f"`{path}`" for path in item["canonical_paths"]),
                "  - status_surfaces: "
                + ", ".join(f"`{path}`" for path in item["status_surfaces"]),
                "  - neighbors: " + ", ".join(f"`{name}`" for name in item["neighbors"]),
            ]
        )

    lines.extend(["", "## Document Threads"])
    for item in payload["document_threads"]:
        lines.extend(
            [
                f"- `{item['thread_id']}`",
                f"  - semantic_key: `{item['semantic_key']}`",
                f"  - path_count: `{item['path_count']}`",
                "  - linked_neighborhoods: "
                + ", ".join(f"`{name}`" for name in item["linked_neighborhoods"]),
            ]
        )
        if item["cross_directory_threads"]:
            lines.append(
                "  - cross_directory_threads: "
                + ", ".join(f"`{name}`" for name in item["cross_directory_threads"])
            )
        lines.append("  - paths: " + ", ".join(f"`{path}`" for path in item["paths"]))

    lines.extend(["", "## Graph Edges"])
    for edge in payload["graph_edges"]:
        lines.append(f"- `{edge['source']}` -> `{edge['target']}` ({edge['relation']})")

    lines.extend(
        [
            "",
            "## Handoff",
            f"- queue_shape: `{handoff.get('queue_shape', '')}`",
            "- requires_operator_action: "
            f"`{str(handoff.get('requires_operator_action', False)).lower()}`",
            f"- preferred_first_neighborhood: `{handoff.get('preferred_first_neighborhood', '')}`",
            f"- chronicle_collection_path: `{handoff.get('chronicle_collection_path', '')}`",
            f"- retrieval_protocol: `{handoff.get('retrieval_protocol', '')}`",
            f"- primary_status_line: `{handoff.get('primary_status_line', '')}`",
        ]
    )
    return "\n".join(lines) + "\n"


def render_mermaid(payload: dict[str, Any]) -> str:
    label_by_id = {
        item["id"]: f"{item['label']}\\n{item['memory_hook']}"
        for item in payload["semantic_neighborhoods"]
    }
    lines = ["graph TD"]
    for node_id, label in label_by_id.items():
        lines.append(f'    {node_id}["{label}"]')
    for edge in payload["graph_edges"]:
        relation = edge["relation"].replace("_", " ")
        lines.append(f"    {edge['source']} -->|{relation}| {edge['target']}")
    return "\n".join(lines) + "\n"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--out-dir", type=Path, default=REPO_ROOT / "docs" / "status")
    args = parser.parse_args()

    payload = build_report(args.repo_root.resolve())
    _emit(payload)
    _write_json(args.out_dir / JSON_FILENAME, payload)
    _write_text(args.out_dir / MARKDOWN_FILENAME, render_markdown(payload))
    _write_text(args.out_dir / MERMAID_FILENAME, render_mermaid(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
