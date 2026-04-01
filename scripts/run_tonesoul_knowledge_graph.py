#!/usr/bin/env python3
"""Generate a passive knowledge graph for the ToneSoul repository."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]

JSON_FILENAME = "tonesoul_knowledge_graph_latest.json"
MARKDOWN_FILENAME = "tonesoul_knowledge_graph_latest.md"
MERMAID_FILENAME = "tonesoul_knowledge_graph_latest.mmd"

SOURCE_DOCS: tuple[str, ...] = (
    "README.md",
    "AI_ONBOARDING.md",
    "MEMORY.md",
    "docs/README.md",
    "docs/terminology.md",
    "docs/system_walkthrough.md",
    "docs/KNOWLEDGE_GRAPH.md",
    "docs/architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md",
    "docs/architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md",
    "docs/plans/tonesoul_knowledge_graph_plan_2026-03-21.md",
    "語魂系統GPTs_v1.1/README.md",
    "語魂系統GPTs_v1.1/01_術語與門檻單一規格.md",
    "語魂系統GPTs_v1.1/02_執行治理規格_Runtime.md",
    "語魂系統GPTs_v1.1/07_六層架構與實作對位.md",
    "語魂系統GPTs_v1.1/08_多視角議會與人格系統.md",
    "語魂系統GPTs_v1.1/10_哲學到程式_可驗證對照表.md",
    "task.md",
)

LANE_SEEDS: tuple[dict[str, Any], ...] = (
    {
        "id": "authority",
        "label": "Authority",
        "summary": "Single-source-of-truth specs and canonical reading order.",
        "members": (
            "README.md",
            "AI_ONBOARDING.md",
            "docs/terminology.md",
            "docs/architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md",
            "docs/architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md",
            "語魂系統GPTs_v1.1/01_術語與門檻單一規格.md",
            "語魂系統GPTs_v1.1/02_執行治理規格_Runtime.md",
            "語魂系統GPTs_v1.1/07_六層架構與實作對位.md",
            "語魂系統GPTs_v1.1/10_哲學到程式_可驗證對照表.md",
            "AXIOMS.json",
        ),
        "neighbors": ("runtime", "governance", "web", "verification"),
    },
    {
        "id": "runtime",
        "label": "Runtime Plane",
        "summary": "Live request path from web entrypoints into ToneSoul orchestration.",
        "members": (
            "apps/web/src/app/api/chat/route.ts",
            "apps/api/server.py",
            "tonesoul/unified_pipeline.py",
            "tonesoul/tension_engine.py",
            "tonesoul/tonebridge/analyzer.py",
        ),
        "neighbors": ("authority", "governance", "memory", "web"),
    },
    {
        "id": "governance",
        "label": "Council + Governance",
        "summary": "Deliberation, gate decisions, and route governance.",
        "members": (
            "tonesoul/council/runtime.py",
            "tonesoul/council/pre_output_council.py",
            "tonesoul/council/verdict.py",
            "tonesoul/governance/kernel.py",
            "tonesoul/yss_gates.py",
            "tonesoul/poav.py",
            "docs/COUNCIL_RUNTIME.md",
        ),
        "neighbors": ("authority", "runtime", "memory", "verification"),
    },
    {
        "id": "memory",
        "label": "Memory Plane",
        "summary": "Semantic graph, crystallization, SoulDB, and boot-time recall.",
        "members": (
            "MEMORY.md",
            "tonesoul/memory/semantic_graph.py",
            "tonesoul/memory/crystallizer.py",
            "tonesoul/memory/soul_db.py",
            "tonesoul/memory/boot.py",
            "docs/ANTIGRAVITY_CONTEXT_MEMORY.md",
        ),
        "neighbors": ("runtime", "governance", "evolution", "verification"),
    },
    {
        "id": "evolution",
        "label": "Evolution Plane",
        "summary": "Offline reflection, wakeup loops, stale-rule verification, and consolidation.",
        "members": (
            "tonesoul/dream_engine.py",
            "tonesoul/wakeup_loop.py",
            "tonesoul/stale_rule_verifier.py",
            "scripts/run_repo_semantic_atlas.py",
            "docs/plans/semantic_memory_architecture.md",
        ),
        "neighbors": ("memory", "verification", "observability"),
    },
    {
        "id": "web",
        "label": "Web Surface",
        "summary": "Front-end transport, fallback, and soul-model rendering helpers.",
        "members": (
            "apps/web/src/app/api/chat/route.ts",
            "apps/web/src/lib/soulEngine.ts",
            "apps/web/src/lib/chatFallback.ts",
            "apps/web/src/lib/soulAuditor.ts",
            "apps/web/src/__tests__/chatFallback.test.ts",
        ),
        "neighbors": ("authority", "runtime", "verification"),
    },
    {
        "id": "verification",
        "label": "Verification",
        "summary": "Tests and current status surfaces that prove the graph against reality.",
        "members": (
            "tests/test_council_runtime.py",
            "tests/test_dream_engine.py",
            "tests/test_exception_trace.py",
            "scripts/run_repo_healthcheck.py",
            "scripts/verify_7d.py",
            "docs/status/README.md",
            "docs/status/repo_healthcheck_latest.md",
            "docs/status/l7_retrieval_contract_latest.md",
            "docs/status/l8_distillation_boundary_latest.md",
        ),
        "neighbors": ("authority", "governance", "memory", "web", "observability"),
    },
    {
        "id": "observability",
        "label": "Observability",
        "summary": "Machine snapshots and passive artifacts that help later agents recover state.",
        "members": (
            "docs/status/README.md",
            "docs/status/repo_healthcheck_latest.md",
            "docs/status/memory_governance_contract_latest.md",
            "docs/status/tonesoul_system_manifesto.md",
            "docs/status/l7_retrieval_contract_latest.md",
            "docs/status/l8_distillation_boundary_latest.md",
            "scripts/run_l7_l8_contract_artifacts.py",
            "scripts/run_repo_semantic_atlas.py",
        ),
        "neighbors": ("verification", "evolution"),
    },
)

CURATED_FLOW_EDGES: tuple[tuple[str, str, str], ...] = (
    ("apps/web/src/app/api/chat/route.ts", "tonesoul/unified_pipeline.py", "flows_to"),
    ("apps/api/server.py", "tonesoul/council/runtime.py", "flows_to"),
    ("tonesoul/unified_pipeline.py", "tonesoul/tension_engine.py", "flows_to"),
    ("tonesoul/unified_pipeline.py", "tonesoul/council/runtime.py", "flows_to"),
    ("tonesoul/unified_pipeline.py", "tonesoul/governance/kernel.py", "flows_to"),
    ("tonesoul/unified_pipeline.py", "tonesoul/memory/semantic_graph.py", "flows_to"),
    ("tonesoul/unified_pipeline.py", "tonesoul/memory/crystallizer.py", "flows_to"),
    ("tonesoul/memory/boot.py", "tonesoul/memory/crystallizer.py", "flows_to"),
    ("tonesoul/wakeup_loop.py", "tonesoul/dream_engine.py", "flows_to"),
)

RETRIEVAL_PROTOCOL: tuple[dict[str, str], ...] = (
    {
        "id": "authority_first",
        "rule": "Open Authority before implementation when semantics or thresholds are unclear.",
    },
    {
        "id": "lane_before_file",
        "rule": "Resolve the lane first, then open concrete files inside that lane.",
    },
    {
        "id": "tests_and_status_after_code",
        "rule": "After reading implementation, confirm behavior via tests or latest status artifacts.",
    },
    {
        "id": "graph_not_database_first",
        "rule": "Use this passive graph as the first recovery surface before considering a graph database.",
    },
)

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
CODE_SPAN_RE = re.compile(r"`([^`\n]+)`")
PATH_TOKEN_RE = re.compile(
    r"(?P<path>"
    r"(?:[A-Za-z0-9_\-\u4e00-\u9fff.]+[\\/])+[A-Za-z0-9_\-\u4e00-\u9fff.\[\]]+/?"
    r"|(?:README|MEMORY|SOUL|AI_ONBOARDING|task|AXIOMS)\.(?:md|json)"
    r")"
)
IMPORT_FROM_RE = re.compile(r"^\s*from\s+([A-Za-z0-9_\.]+)\s+import\s+", re.MULTILINE)
IMPORT_RE = re.compile(r"^\s*import\s+([A-Za-z0-9_\.]+)", re.MULTILINE)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_repo_path(value: str) -> str:
    text = str(value or "").strip().replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    return text


def path_exists(repo_root: Path, repo_path: str) -> bool:
    return (repo_root / repo_path).exists()


def classify_path(repo_path: str, repo_root: Path) -> str:
    target = repo_root / repo_path
    if repo_path.startswith("docs/status/"):
        return "status_surface"
    if repo_path.startswith("語魂系統GPTs_v1.1/"):
        return "authority_doc"
    if repo_path.startswith("docs/plans/"):
        return "plan_doc"
    if repo_path.startswith("docs/"):
        return "doc"
    if repo_path.startswith("tests/"):
        return "test"
    if repo_path.startswith("scripts/"):
        return "script"
    if repo_path.startswith("apps/web/"):
        return "frontend_module"
    if repo_path.startswith("apps/"):
        return "app_module"
    if repo_path.startswith("tonesoul/"):
        return "python_module"
    if repo_path.startswith("spec/"):
        return "spec"
    if repo_path.startswith("law/"):
        return "law"
    if repo_path.startswith("memory/"):
        return "memory_asset"
    if target.is_dir():
        return "collection"
    suffix = target.suffix.lower()
    if suffix == ".py":
        return "python_module"
    if suffix in {".ts", ".tsx"}:
        return "frontend_module"
    if suffix in {".md", ".txt"}:
        return "doc"
    if suffix in {".json", ".yaml", ".yml"}:
        return "data"
    return "asset"


def node_id_for_file(repo_path: str) -> str:
    return f"file:{repo_path}"


def node_id_for_lane(lane_id: str) -> str:
    return f"lane:{lane_id}"


def lane_lookup(lane_seeds: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(seed["id"]): dict(seed) for seed in lane_seeds}


def resolve_path_candidate(candidate: str, source_path: str, repo_root: Path) -> str | None:
    raw = str(candidate or "").strip().strip("\"'()[]{}")
    raw = raw.rstrip(".,;")
    if not raw or raw.startswith(("http://", "https://", "#")):
        return None
    raw = raw.replace("\\", "/")
    if raw.startswith("app://") or raw.startswith("plugin://"):
        return None

    source_file = repo_root / source_path
    attempt_paths = []
    if raw.startswith("../") or raw.startswith("./"):
        attempt_paths.append((source_file.parent / raw).resolve())
    else:
        attempt_paths.append((repo_root / raw).resolve())
        attempt_paths.append((source_file.parent / raw).resolve())

    for resolved in attempt_paths:
        try:
            relative = resolved.relative_to(repo_root.resolve())
        except ValueError:
            continue
        relative_text = normalize_repo_path(relative.as_posix())
        if path_exists(repo_root, relative_text):
            return relative_text
    return None


def extract_existing_paths(text: str, source_path: str, repo_root: Path) -> list[str]:
    matches: list[str] = []
    for regex in (MARKDOWN_LINK_RE, CODE_SPAN_RE, PATH_TOKEN_RE):
        for match in regex.finditer(text):
            candidate = match.group(1) if regex is not PATH_TOKEN_RE else match.group("path")
            resolved = resolve_path_candidate(candidate, source_path, repo_root)
            if resolved:
                matches.append(resolved)

    ordered: list[str] = []
    seen: set[str] = set()
    for item in matches:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def resolve_module_to_repo_path(module_name: str, repo_root: Path) -> str | None:
    parts = [part for part in module_name.split(".") if part]
    if not parts:
        return None

    candidate = Path(*parts)
    file_candidate = normalize_repo_path((candidate.with_suffix(".py")).as_posix())
    init_candidate = normalize_repo_path((candidate / "__init__.py").as_posix())

    for repo_path in (file_candidate, init_candidate):
        if path_exists(repo_root, repo_path):
            return repo_path
    return None


def extract_import_edges(repo_path: str, repo_root: Path) -> list[tuple[str, str, str]]:
    target = repo_root / repo_path
    if target.suffix != ".py" or not target.exists():
        return []
    text = target.read_text(encoding="utf-8")
    modules = set(IMPORT_FROM_RE.findall(text)) | set(IMPORT_RE.findall(text))
    edge_type = "verifies" if repo_path.startswith("tests/") else "imports"
    results: list[tuple[str, str, str]] = []
    for module_name in sorted(modules):
        resolved = resolve_module_to_repo_path(module_name, repo_root)
        if resolved:
            results.append((repo_path, resolved, edge_type))
    return results


def add_file_node(
    nodes: dict[str, dict[str, Any]],
    lane_membership: dict[str, set[str]],
    repo_path: str,
    repo_root: Path,
) -> None:
    repo_path = normalize_repo_path(repo_path)
    if not path_exists(repo_root, repo_path):
        return
    node_id = node_id_for_file(repo_path)
    if node_id not in nodes:
        nodes[node_id] = {
            "id": node_id,
            "label": Path(repo_path).name or repo_path,
            "kind": classify_path(repo_path, repo_root),
            "path": repo_path,
            "lanes": [],
        }
    lanes = sorted(lane_membership.get(repo_path, set()))
    nodes[node_id]["lanes"] = lanes


def add_edge(
    edges: list[dict[str, str]],
    seen: set[tuple[str, str, str]],
    source: str,
    target: str,
    edge_type: str,
) -> None:
    triple = (source, target, edge_type)
    if triple in seen:
        return
    seen.add(triple)
    edges.append({"source": source, "target": target, "type": edge_type})


def build_knowledge_graph(
    *,
    repo_root: Path = REPO_ROOT,
    source_docs: Iterable[str] = SOURCE_DOCS,
    lane_seeds: Iterable[dict[str, Any]] = LANE_SEEDS,
    curated_flow_edges: Iterable[tuple[str, str, str]] = CURATED_FLOW_EDGES,
) -> dict[str, Any]:
    repo_root = Path(repo_root)
    lane_map = lane_lookup(lane_seeds)
    lane_membership: dict[str, set[str]] = defaultdict(set)
    for lane_id, lane in lane_map.items():
        for member in lane.get("members", ()):
            member_path = normalize_repo_path(str(member))
            if path_exists(repo_root, member_path):
                lane_membership[member_path].add(lane_id)

    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, str]] = []
    edge_seen: set[tuple[str, str, str]] = set()

    for lane_id, lane in lane_map.items():
        node_id = node_id_for_lane(lane_id)
        nodes[node_id] = {
            "id": node_id,
            "label": str(lane["label"]),
            "kind": "lane",
            "path": None,
            "summary": str(lane["summary"]),
            "lanes": [lane_id],
        }

    for lane_id, lane in lane_map.items():
        lane_node_id = node_id_for_lane(lane_id)
        for member in lane.get("members", ()):
            member_path = normalize_repo_path(str(member))
            add_file_node(nodes, lane_membership, member_path, repo_root)
            if path_exists(repo_root, member_path):
                add_edge(edges, edge_seen, lane_node_id, node_id_for_file(member_path), "contains")
        for neighbor in lane.get("neighbors", ()):
            if neighbor in lane_map:
                add_edge(
                    edges, edge_seen, lane_node_id, node_id_for_lane(str(neighbor)), "neighbors"
                )

    normalized_source_docs = [normalize_repo_path(str(item)) for item in source_docs]
    for source_path in normalized_source_docs:
        if not path_exists(repo_root, source_path):
            continue
        add_file_node(nodes, lane_membership, source_path, repo_root)
        text = (repo_root / source_path).read_text(encoding="utf-8")
        for referenced in extract_existing_paths(text, source_path, repo_root):
            add_file_node(nodes, lane_membership, referenced, repo_root)
            add_edge(
                edges,
                edge_seen,
                node_id_for_file(source_path),
                node_id_for_file(referenced),
                "references",
            )

    file_paths = [
        node["path"] for node in nodes.values() if node.get("path") and node.get("kind") != "lane"
    ]
    for repo_path in sorted(set(str(path) for path in file_paths)):
        for source, target, edge_type in extract_import_edges(repo_path, repo_root):
            add_file_node(nodes, lane_membership, source, repo_root)
            add_file_node(nodes, lane_membership, target, repo_root)
            add_edge(
                edges,
                edge_seen,
                node_id_for_file(source),
                node_id_for_file(target),
                edge_type,
            )

    for source_path, target_path, edge_type in curated_flow_edges:
        source_norm = normalize_repo_path(source_path)
        target_norm = normalize_repo_path(target_path)
        add_file_node(nodes, lane_membership, source_norm, repo_root)
        add_file_node(nodes, lane_membership, target_norm, repo_root)
        if path_exists(repo_root, source_norm) and path_exists(repo_root, target_norm):
            add_edge(
                edges,
                edge_seen,
                node_id_for_file(source_norm),
                node_id_for_file(target_norm),
                edge_type,
            )

    degree: dict[str, int] = defaultdict(int)
    for edge in edges:
        degree[edge["source"]] += 1
        degree[edge["target"]] += 1

    top_anchors = []
    for node in sorted(nodes.values(), key=lambda item: (-degree[item["id"]], item["id"])):
        if node["kind"] == "lane":
            continue
        top_anchors.append(
            {
                "id": node["id"],
                "path": node.get("path"),
                "label": node["label"],
                "kind": node["kind"],
                "degree": degree[node["id"]],
            }
        )
        if len(top_anchors) >= 12:
            break

    lane_payload = []
    for lane_id, lane in lane_map.items():
        lane_payload.append(
            {
                "id": lane_id,
                "label": lane["label"],
                "summary": lane["summary"],
                "members": [
                    member
                    for member in lane.get("members", ())
                    if path_exists(repo_root, normalize_repo_path(str(member)))
                ],
                "neighbors": [
                    neighbor for neighbor in lane.get("neighbors", ()) if neighbor in lane_map
                ],
            }
        )

    payload = {
        "generated_at": utc_now_iso(),
        "source": "scripts/run_tonesoul_knowledge_graph.py",
        "meta": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "lane_count": len(lane_payload),
            "source_doc_count": sum(
                1 for item in normalized_source_docs if path_exists(repo_root, item)
            ),
        },
        "retrieval_protocol": list(RETRIEVAL_PROTOCOL),
        "source_docs": [item for item in normalized_source_docs if path_exists(repo_root, item)],
        "lanes": lane_payload,
        "nodes": sorted(nodes.values(), key=lambda item: (item["kind"], item["label"])),
        "edges": sorted(edges, key=lambda item: (item["type"], item["source"], item["target"])),
        "top_anchors": top_anchors,
    }
    return payload


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# ToneSoul Knowledge Graph Latest",
        "",
        f"- generated_at: {payload.get('generated_at', 'unknown')}",
        f"- node_count: {payload.get('meta', {}).get('node_count', 0)}",
        f"- edge_count: {payload.get('meta', {}).get('edge_count', 0)}",
        f"- lane_count: {payload.get('meta', {}).get('lane_count', 0)}",
        "",
        "## Retrieval Protocol",
    ]
    for item in payload.get("retrieval_protocol", []):
        lines.append(f"- `{item.get('id', 'unknown')}`: {item.get('rule', '')}")

    lines.extend(["", "## Lanes"])
    for lane in payload.get("lanes", []):
        lines.append(f"### {lane.get('label', 'Unknown Lane')}")
        lines.append(f"- summary: {lane.get('summary', '')}")
        members = lane.get("members", [])
        neighbors = lane.get("neighbors", [])
        if members:
            lines.append("- members:")
            for member in members:
                lines.append(f"  - `{member}`")
        if neighbors:
            lines.append(f"- neighbors: {', '.join(f'`{item}`' for item in neighbors)}")
        lines.append("")

    lines.extend(["## Top Anchors", "| path | kind | degree |", "| --- | --- | ---: |"])
    for anchor in payload.get("top_anchors", []):
        lines.append(
            f"| `{anchor.get('path', '')}` | `{anchor.get('kind', '')}` | {anchor.get('degree', 0)} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def mermaid_safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", value)


def render_mermaid(payload: dict[str, Any]) -> str:
    lines = ["graph TD"]
    lane_map = {lane["id"]: lane for lane in payload.get("lanes", [])}
    node_map = {node["id"]: node for node in payload.get("nodes", [])}
    included_nodes: set[str] = set()

    for lane_id, lane in sorted(lane_map.items()):
        lane_node_id = node_id_for_lane(lane_id)
        lane_mermaid_id = mermaid_safe_id(lane_node_id)
        lines.append(f'    {lane_mermaid_id}["{lane.get("label", lane_id)}"]')
        included_nodes.add(lane_node_id)

        for member in lane.get("members", [])[:4]:
            file_node_id = node_id_for_file(member)
            file_node = node_map.get(file_node_id)
            if not file_node:
                continue
            mermaid_id = mermaid_safe_id(file_node_id)
            label = file_node.get("label", member)
            lines.append(f'    {mermaid_id}["{label}"]')
            lines.append(f"    {lane_mermaid_id} --> {mermaid_id}")
            included_nodes.add(file_node_id)

    for edge in payload.get("edges", []):
        edge_type = edge.get("type")
        source = edge.get("source")
        target = edge.get("target")
        if source not in included_nodes or target not in included_nodes:
            continue
        source_id = mermaid_safe_id(source)
        target_id = mermaid_safe_id(target)
        if edge_type == "neighbors":
            lines.append(f"    {source_id} -.-> {target_id}")
        elif edge_type == "flows_to":
            lines.append(f"    {source_id} --> {target_id}")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(
    payload: dict[str, Any],
    markdown: str,
    mermaid: str,
    *,
    output_dir: Path,
    repo_root: Path = REPO_ROOT,
) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / JSON_FILENAME
    markdown_path = output_dir / MARKDOWN_FILENAME
    mermaid_path = output_dir / MERMAID_FILENAME

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(markdown, encoding="utf-8")
    mermaid_path.write_text(mermaid, encoding="utf-8")

    return {
        "json": normalize_repo_path(str(json_path.relative_to(repo_root))),
        "markdown": normalize_repo_path(str(markdown_path.relative_to(repo_root))),
        "mermaid": normalize_repo_path(str(mermaid_path.relative_to(repo_root))),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the ToneSoul knowledge graph artifact.")
    parser.add_argument(
        "--output-dir",
        default="docs/status",
        help="Directory for graph artifacts (default: docs/status).",
    )
    args = parser.parse_args(argv)

    payload = build_knowledge_graph()
    markdown = render_markdown(payload)
    mermaid = render_mermaid(payload)
    paths = write_outputs(
        payload,
        markdown,
        mermaid,
        output_dir=REPO_ROOT / args.output_dir,
        repo_root=REPO_ROOT,
    )
    print(json.dumps({"ok": True, "artifacts": paths}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
