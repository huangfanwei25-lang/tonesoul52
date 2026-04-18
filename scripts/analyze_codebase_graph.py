#!/usr/bin/env python3
"""Full-AST codebase graph analyzer for ToneSoul.

Scans every .py file under a root package, builds a complete import/call graph,
and outputs structural health metrics:

- God node ranking (highest in-degree + out-degree)
- Circular dependency detection
- Layer boundary violation detection
- Orphan module detection (nobody imports them)
- Subpackage coupling matrix
- Module community clustering (label propagation, no external deps)

Usage:
    python scripts/analyze_codebase_graph.py [--root tonesoul] [--output-dir docs/status]
    python scripts/analyze_codebase_graph.py --json-only   # stdout JSON, no files
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Layer definitions — used for boundary violation detection
# ---------------------------------------------------------------------------
LAYER_MAP: dict[str, str] = {
    "governance": "governance",
    "council": "governance",
    "deliberation": "governance",
    "gates": "governance",
    "pipeline": "pipeline",
    "llm": "infrastructure",
    "backends": "infrastructure",
    "gateway": "infrastructure",
    "store": "infrastructure",
    "memory": "memory",
    "evolution": "evolution",
    "corpus": "evolution",
    "perception": "perception",
    "semantic": "semantic",
    "observability": "observability",
    "tech_trace": "observability",
    "cli": "surface",
    "tonebridge": "surface",
    "inter_soul": "surface",
    "market": "domain",
    "ystm": "domain",
    "scribe": "domain",
    "yuhun": "semantic",
    "loop": "orchestration",
    "shared": "shared",
    "_legacy": "legacy",
}

# Root-level module → layer.
# tonesoul/*.py files sit outside the subpackage taxonomy. Without this map
# they all collapse to "uncategorized", which hides real architectural shape.
# Entries here are curated high-confidence classifications; anything not listed
# stays uncategorized so gaps surface honestly rather than being papered over.
ROOT_MODULE_LAYER: dict[str, str] = {
    # governance — gates, preflight, vows, drift, constraints, contracts
    "adaptive_gate": "governance",
    "skill_gate": "governance",
    "skill_apply": "governance",
    "skill_promoter": "governance",
    "yss_gates": "governance",
    "mutation_preflight": "governance",
    "publish_push_preflight": "governance",
    "shared_edit_preflight": "governance",
    "task_board_preflight": "governance",
    "vow_inventory": "governance",
    "vow_system": "governance",
    "constraint_stack": "governance",
    "tension_engine": "governance",
    "risk_calculator": "governance",
    "drift_monitor": "governance",
    "drift_tracker": "governance",
    "stale_rule_verifier": "governance",
    "seed_schema_check": "governance",
    "intent_verification": "governance",
    "escalation": "governance",
    "alert_escalation": "governance",
    "escape_valve": "governance",
    "consumer_contract": "governance",
    "semantic_control": "governance",
    "receiver_posture": "governance",
    "council_capability": "governance",
    "work_classifier": "governance",
    "grounding_check": "governance",
    "contract_observer": "governance",
    # infrastructure — stores, servers, persistence, low-level services
    "store": "infrastructure",
    "store_keys": "infrastructure",
    "soul_persistence": "infrastructure",
    "supabase_persistence": "infrastructure",
    "local_llm": "infrastructure",
    "mcp_server": "infrastructure",
    "service_manager": "infrastructure",
    "hook_chain": "infrastructure",
    "aegis_shield": "infrastructure",
    "zone_registry": "infrastructure",
    # pipeline — runtime adapter, unified pipeline, frame routing
    "runtime_adapter": "pipeline",
    "runtime_adapter_normalization": "pipeline",
    "runtime_adapter_routing": "pipeline",
    "runtime_adapter_subject_refresh": "pipeline",
    "unified_pipeline": "pipeline",
    "unified_controller": "pipeline",
    "yss_pipeline": "pipeline",
    "yss_unified_adapter": "pipeline",
    "generation_orch": "pipeline",
    "frame_router": "pipeline",
    "action_set": "pipeline",
    "context_compiler": "pipeline",
    # memory — hot caches, managers, archival islands, inventory
    "hot_memory": "memory",
    "memory_manager": "memory",
    "time_island": "memory",
    "inventory": "memory",
    # evolution — self-improvement, dream, mirror, reflection, persona
    "self_improvement_trial_wave": "evolution",
    "dream_engine": "evolution",
    "dream_observability": "evolution",
    "mirror": "evolution",
    "reflection": "evolution",
    "resonance": "evolution",
    "resistance": "evolution",
    "benevolence": "evolution",
    "mercy_objective": "evolution",
    "persona_dimension": "evolution",
    "working_style": "evolution",
    "subsystem_parity": "evolution",
    # observability — monitors, trackers, auditors, metrics, status
    "observer_window": "observability",
    "jump_monitor": "observability",
    "heartbeat": "observability",
    "evidence_collector": "observability",
    "exception_trace": "observability",
    "error_event": "observability",
    "audit_interface": "observability",
    "openclaw_auditor": "observability",
    "status_alignment": "observability",
    "true_verification_summary": "observability",
    "tsr_metrics": "observability",
    "surface_versioning": "observability",
    "issue_codes": "observability",
    "repo_state_awareness": "observability",
    "poav": "observability",
    # orchestration — autonomous cycles, schedules, wakeup loops
    "autonomous_cycle": "orchestration",
    "autonomous_schedule": "orchestration",
    "wakeup_loop": "orchestration",
    "schedule_profile": "orchestration",
    # surface — operator-facing entry adapters, diagnostics
    "diagnose": "surface",
    "claude_entry_adapter": "surface",
    # domain — semantic field modellers, predictors, variance
    "ystm_demo": "domain",
    "variance_compressor": "domain",
    "nonlinear_predictor": "domain",
    "dcs": "domain",
    # shared — config, schemas, parsing primitives
    "tonesoul": "shared",
    "config": "shared",
    "soul_config": "shared",
    "schemas": "shared",
    "safe_parse": "shared",
}

# Per-module layer overrides that trump subpackage classification.
# Some modules are physically nested in a domain subpackage but are in fact
# pure type primitives or cross-cutting utilities used everywhere. Listing
# them here makes the body map honest without forcing a physical relocation.
MODULE_LAYER_OVERRIDES: dict[str, str] = {
    # ystm.schema is a pure @dataclass type module imported by governance,
    # observability, memory, evolution — it has become the shared type
    # vocabulary, regardless of living inside the ystm subpackage.
    "tonesoul.ystm.schema": "shared",
}

# Allowed downward dependencies (layer A may import layer B)
ALLOWED_DEPS: dict[str, set[str]] = {
    "surface": {
        "pipeline",
        "orchestration",
        "governance",
        "memory",
        "infrastructure",
        "shared",
        "domain",
        "semantic",
        "perception",
        "observability",
        "evolution",
    },
    "orchestration": {
        "pipeline",
        "governance",
        "memory",
        "infrastructure",
        "shared",
        "domain",
        "semantic",
        "observability",
        "evolution",
        "perception",
    },
    "pipeline": {
        "governance",
        "memory",
        "infrastructure",
        "shared",
        "semantic",
        "perception",
        "observability",
        "evolution",
        "domain",
    },
    "domain": {"governance", "memory", "infrastructure", "shared", "semantic", "observability"},
    "governance": {"memory", "infrastructure", "shared", "observability", "semantic"},
    "memory": {"infrastructure", "shared"},
    "evolution": {"memory", "infrastructure", "shared", "governance", "observability"},
    "semantic": {"infrastructure", "shared", "memory", "governance", "observability"},
    "perception": {"infrastructure", "shared", "memory", "semantic"},
    "observability": {
        "infrastructure",
        "shared",
        "memory",
        "governance",
        "domain",
        "evolution",
        "semantic",
        "perception",
    },
    "infrastructure": {"shared"},
    "shared": set(),
    "legacy": {"shared", "infrastructure", "governance", "memory", "pipeline", "domain"},
}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------
@dataclass
class ModuleInfo:
    """Parsed information about a single Python module."""

    repo_path: str  # e.g. "tonesoul/governance/kernel.py"
    module_name: str  # e.g. "tonesoul.governance.kernel"
    subpackage: str  # e.g. "governance" or "(root)"
    layer: str  # e.g. "governance"
    purpose: str = ""  # one-line description from __ts_purpose__
    layer_source: str = (
        "fallback"  # "self_declared" | "override" | "root_map" | "subpackage" | "fallback"
    )
    lines: int = 0
    classes: int = 0
    functions: int = 0
    imports_out: list[str] = field(default_factory=list)  # modules this file imports
    imported_by: list[str] = field(default_factory=list)  # modules that import this


@dataclass
class CycleInfo:
    """A detected import cycle."""

    cycle: list[str]
    length: int


@dataclass
class LayerViolation:
    """A detected layer boundary violation."""

    source_module: str
    source_layer: str
    target_module: str
    target_layer: str


# ---------------------------------------------------------------------------
# AST scanning
# ---------------------------------------------------------------------------
# Module-level self-declaration constants. A module can declare its own layer
# and purpose at the top of its file:
#
#     __ts_layer__ = "governance"
#     __ts_purpose__ = "One-line description of what this module does."
#
# The analyzer reads these via AST and takes them as the source of truth —
# no central dict edit required. Fallback to the legacy dict maps keeps the
# body map working during the annotation migration.
SELF_DECL_LAYER_NAME = "__ts_layer__"
SELF_DECL_PURPOSE_NAME = "__ts_purpose__"


def _extract_self_declarations(tree: ast.Module) -> tuple[str, str]:
    """Return (declared_layer, declared_purpose) from top-level constant assigns."""
    declared_layer = ""
    declared_purpose = ""
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            continue
        target_name = node.targets[0].id
        if not isinstance(node.value, ast.Constant) or not isinstance(node.value.value, str):
            continue
        if target_name == SELF_DECL_LAYER_NAME:
            declared_layer = node.value.value
        elif target_name == SELF_DECL_PURPOSE_NAME:
            declared_purpose = node.value.value
    return declared_layer, declared_purpose


def _classify_fallback(module_name: str, subpackage: str) -> tuple[str, str]:
    """Return (layer, source_tag) from the legacy fallback tables."""
    if module_name in MODULE_LAYER_OVERRIDES:
        return MODULE_LAYER_OVERRIDES[module_name], "override"
    if subpackage == "(root)":
        basename = module_name.rsplit(".", 1)[-1]
        return ROOT_MODULE_LAYER.get(basename, "uncategorized"), "root_map"
    return LAYER_MAP.get(subpackage, "uncategorized"), "subpackage"


def scan_module(file_path: Path, root_package: str, repo_root: Path) -> ModuleInfo:
    """Parse a single .py file and extract structural information."""
    repo_path = str(file_path.relative_to(repo_root)).replace("\\", "/")
    module_name = repo_path.replace("/", ".").removesuffix(".py")
    if module_name.endswith(".__init__"):
        module_name = module_name.removesuffix(".__init__")

    # Determine subpackage
    parts = repo_path.split("/")
    if len(parts) >= 3 and parts[0] == root_package:
        subpackage = parts[1]
    else:
        subpackage = "(root)"

    layer, layer_source = _classify_fallback(module_name, subpackage)

    try:
        source = file_path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return ModuleInfo(
            repo_path=repo_path,
            module_name=module_name,
            subpackage=subpackage,
            layer=layer,
        )

    line_count = source.count("\n") + (1 if source and not source.endswith("\n") else 0)

    try:
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError:
        return ModuleInfo(
            repo_path=repo_path,
            module_name=module_name,
            subpackage=subpackage,
            layer=layer,
            lines=line_count,
        )

    # Collect line ranges of `if TYPE_CHECKING:` blocks to skip
    type_checking_lines: set[int] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.If)
            and isinstance(node.test, ast.Name)
            and node.test.id == "TYPE_CHECKING"
        ):
            for child in ast.walk(node):
                if hasattr(child, "lineno"):
                    type_checking_lines.add(child.lineno)

    declared_layer, declared_purpose = _extract_self_declarations(tree)
    if declared_layer:
        layer = declared_layer
        layer_source = "self_declared"

    class_count = 0
    func_count = 0
    imports_out: list[str] = []

    # Compute package for relative import resolution
    # e.g. "tonesoul.council.runtime" → "tonesoul.council"
    # e.g. "tonesoul.skill_gate" → "tonesoul"
    if module_name.endswith(".__init__") or repo_path.endswith("__init__.py"):
        _current_package = module_name
    else:
        _current_package = module_name.rsplit(".", 1)[0] if "." in module_name else ""

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_count += 1
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            func_count += 1
        elif isinstance(node, ast.ImportFrom):
            if node.lineno in type_checking_lines:
                continue
            resolved = node.module or ""
            if node.level and node.level > 0 and _current_package:
                # Resolve relative import: from .foo → package.foo
                pkg = _current_package
                for _ in range(node.level - 1):
                    pkg = pkg.rsplit(".", 1)[0] if "." in pkg else ""
                resolved = f"{pkg}.{resolved}" if resolved else pkg
            if resolved.startswith(root_package):
                imports_out.append(resolved)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith(root_package):
                    if node.lineno not in type_checking_lines:
                        imports_out.append(alias.name)

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_imports: list[str] = []
    for imp in imports_out:
        if imp not in seen:
            seen.add(imp)
            unique_imports.append(imp)

    return ModuleInfo(
        repo_path=repo_path,
        module_name=module_name,
        subpackage=subpackage,
        layer=layer,
        purpose=declared_purpose,
        layer_source=layer_source,
        lines=line_count,
        classes=class_count,
        functions=func_count,
        imports_out=unique_imports,
    )


def scan_all_modules(root_package: str, repo_root: Path) -> dict[str, ModuleInfo]:
    """Scan all .py files under the root package."""
    package_dir = repo_root / root_package
    modules: dict[str, ModuleInfo] = {}

    for py_file in sorted(package_dir.rglob("*.py")):
        # Skip __pycache__ and _legacy
        rel = py_file.relative_to(package_dir)
        parts = rel.parts
        if any(p.startswith("__pycache__") for p in parts):
            continue
        if any(p == "_legacy" for p in parts):
            continue

        info = scan_module(py_file, root_package, repo_root)
        modules[info.module_name] = info

    return modules


# ---------------------------------------------------------------------------
# Graph analysis
# ---------------------------------------------------------------------------
def resolve_import_target(import_name: str, modules: dict[str, ModuleInfo]) -> str | None:
    """Resolve an import name to an actual module in our graph."""
    if import_name in modules:
        return import_name
    # Try as package (might be importing from __init__)
    # e.g., "tonesoul.governance" -> "tonesoul.governance" (the __init__)
    parts = import_name.split(".")
    for i in range(len(parts), 0, -1):
        candidate = ".".join(parts[:i])
        if candidate in modules:
            return candidate
    return None


def build_edges(
    modules: dict[str, ModuleInfo],
) -> list[tuple[str, str]]:
    """Build directed edges (source imports target)."""
    edges: list[tuple[str, str]] = []
    for mod_name, info in modules.items():
        for imp in info.imports_out:
            target = resolve_import_target(imp, modules)
            if target and target != mod_name:
                edges.append((mod_name, target))
                if mod_name not in modules[target].imported_by:
                    modules[target].imported_by.append(mod_name)
    return edges


def compute_degree(
    modules: dict[str, ModuleInfo], edges: list[tuple[str, str]]
) -> dict[str, dict[str, int]]:
    """Compute in-degree, out-degree, and total degree for each module."""
    in_deg: dict[str, int] = defaultdict(int)
    out_deg: dict[str, int] = defaultdict(int)

    for src, tgt in edges:
        out_deg[src] += 1
        in_deg[tgt] += 1

    result: dict[str, dict[str, int]] = {}
    for mod_name in modules:
        result[mod_name] = {
            "in": in_deg.get(mod_name, 0),
            "out": out_deg.get(mod_name, 0),
            "total": in_deg.get(mod_name, 0) + out_deg.get(mod_name, 0),
        }
    return result


def find_cycles(edges: list[tuple[str, str]]) -> list[CycleInfo]:
    """Find all unique cycles using DFS-based cycle detection."""
    graph: dict[str, list[str]] = defaultdict(list)
    for src, tgt in edges:
        graph[src].append(tgt)

    all_nodes = set()
    for src, tgt in edges:
        all_nodes.add(src)
        all_nodes.add(tgt)

    visited: set[str] = set()
    on_stack: set[str] = set()
    path: list[str] = []
    cycles: list[list[str]] = []

    def dfs(node: str) -> None:
        visited.add(node)
        on_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor)
            elif neighbor in on_stack:
                # Found a cycle
                idx = path.index(neighbor)
                cycle = path[idx:] + [neighbor]
                cycles.append(cycle)

        path.pop()
        on_stack.discard(node)

    for node in sorted(all_nodes):
        if node not in visited:
            dfs(node)

    # Deduplicate: normalize cycles by rotating to start with smallest element
    unique: dict[tuple[str, ...], list[str]] = {}
    for cycle in cycles:
        loop = cycle[:-1]  # remove the repeated end node
        if not loop:
            continue
        min_idx = loop.index(min(loop))
        rotated = tuple(loop[min_idx:] + loop[:min_idx])
        if rotated not in unique:
            unique[rotated] = list(rotated)

    return [
        CycleInfo(cycle=c, length=len(c))
        for c in sorted(unique.values(), key=lambda x: (len(x), x))
    ]


def find_layer_violations(
    modules: dict[str, ModuleInfo], edges: list[tuple[str, str]]
) -> list[LayerViolation]:
    """Find imports that cross layer boundaries in disallowed directions."""
    violations: list[LayerViolation] = []

    for src, tgt in edges:
        src_info = modules.get(src)
        tgt_info = modules.get(tgt)
        if not src_info or not tgt_info:
            continue

        src_layer = src_info.layer
        tgt_layer = tgt_info.layer

        # Same layer is always OK
        if src_layer == tgt_layer:
            continue
        # Uncategorized modules get a pass
        if src_layer == "uncategorized" or tgt_layer == "uncategorized":
            continue

        allowed = ALLOWED_DEPS.get(src_layer, set())
        if tgt_layer not in allowed:
            violations.append(
                LayerViolation(
                    source_module=src,
                    source_layer=src_layer,
                    target_module=tgt,
                    target_layer=tgt_layer,
                )
            )

    return violations


def _is_entry_point(info: ModuleInfo, repo_root: Path) -> bool:
    """Detect whether a module is a CLI entry point or externally referenced."""
    # Has argparse → CLI tool
    try:
        source = (repo_root / info.repo_path).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return False

    if "argparse" in source and ("__main__" in source or "parse_args" in source):
        return True

    # Has `if __name__ == "__main__":` block
    if "if __name__ ==" in source:
        return True

    return False


def _is_externally_referenced(mod_name: str, root_package: str, repo_root: Path) -> bool:
    """Check if a module is imported by scripts/, tests/, apps/, or __init__.py."""
    import re as _re

    short = mod_name.removeprefix(root_package + ".")
    # Build patterns to search for
    patterns = [
        _re.escape(mod_name),
        _re.escape(f"from {mod_name}"),
    ]
    combined = "|".join(patterns)

    for search_dir in ("scripts", "tests", "apps"):
        dir_path = repo_root / search_dir
        if not dir_path.is_dir():
            continue
        for py_file in dir_path.rglob("*.py"):
            try:
                text = py_file.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeDecodeError):
                continue
            if _re.search(combined, text):
                return True

    # Check __init__.py re-exports within the package
    for init_file in (repo_root / root_package).rglob("__init__.py"):
        try:
            text = init_file.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            continue
        if short in text or mod_name in text:
            return True

    return False


def find_orphans(
    modules: dict[str, ModuleInfo],
    degree: dict[str, dict[str, int]],
    root_package: str = "tonesoul",
    repo_root: Path = REPO_ROOT,
) -> list[str]:
    """Find modules with zero in-degree (nobody imports them).

    Excludes:
    - __init__.py packages
    - CLI entry points (argparse / __main__)
    - Modules referenced by scripts/, tests/, apps/, or __init__.py
    """
    orphans: list[str] = []
    for mod_name, info in sorted(modules.items()):
        if degree[mod_name]["in"] == 0:
            if info.repo_path.endswith("__init__.py"):
                continue
            if _is_entry_point(info, repo_root):
                continue
            if _is_externally_referenced(mod_name, root_package, repo_root):
                continue
            orphans.append(mod_name)
    return orphans


def compute_subpackage_coupling(
    modules: dict[str, ModuleInfo], edges: list[tuple[str, str]]
) -> dict[str, dict[str, int]]:
    """Build a coupling matrix: subpackage_A -> subpackage_B -> edge_count."""
    matrix: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for src, tgt in edges:
        src_info = modules.get(src)
        tgt_info = modules.get(tgt)
        if not src_info or not tgt_info:
            continue
        matrix[src_info.subpackage][tgt_info.subpackage] += 1

    return {k: dict(v) for k, v in sorted(matrix.items())}


def detect_communities(
    modules: dict[str, ModuleInfo], edges: list[tuple[str, str]], iterations: int = 20
) -> dict[str, str]:
    """Simple label propagation for community detection.

    Initializes each module with its subpackage label, then propagates.
    Modules that are more tightly coupled to another subpackage will migrate.
    """
    # Initialize labels
    labels: dict[str, str] = {name: info.subpackage for name, info in modules.items()}

    # Build adjacency (undirected)
    adj: dict[str, list[str]] = defaultdict(list)
    for src, tgt in edges:
        adj[src].append(tgt)
        adj[tgt].append(src)

    for _ in range(iterations):
        changed = False
        for node in sorted(modules.keys()):
            neighbors = adj.get(node, [])
            if not neighbors:
                continue
            # Count neighbor labels
            counts: dict[str, int] = defaultdict(int)
            for nb in neighbors:
                counts[labels.get(nb, "(root)")] += 1
            # Pick most common (tie-break: keep current)
            best_label = max(counts, key=lambda k: (counts[k], k == labels[node]))
            if best_label != labels[node]:
                labels[node] = best_label
                changed = True
        if not changed:
            break

    return labels


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------
def build_report(
    modules: dict[str, ModuleInfo],
    edges: list[tuple[str, str]],
    degree: dict[str, dict[str, int]],
    cycles: list[CycleInfo],
    violations: list[LayerViolation],
    orphans: list[str],
    coupling: dict[str, dict[str, int]],
    communities: dict[str, str],
    root_package: str,
) -> dict[str, Any]:
    """Build the JSON report payload."""

    # God nodes: top 20 by total degree
    god_nodes = sorted(
        [
            {
                "module": name,
                "path": modules[name].repo_path,
                "in_degree": degree[name]["in"],
                "out_degree": degree[name]["out"],
                "total_degree": degree[name]["total"],
                "lines": modules[name].lines,
                "classes": modules[name].classes,
                "functions": modules[name].functions,
                "layer": modules[name].layer,
                "layer_source": modules[name].layer_source,
                "purpose": modules[name].purpose,
            }
            for name in modules
        ],
        key=lambda x: (-x["total_degree"], x["module"]),
    )[:20]

    # Self-declaration coverage: share of modules that declared their own layer.
    self_declared = sum(1 for m in modules.values() if m.layer_source == "self_declared")
    with_purpose = sum(1 for m in modules.values() if m.purpose)
    annotation_coverage = {
        "self_declared_layer_count": self_declared,
        "self_declared_layer_ratio": (round(self_declared / len(modules), 4) if modules else 0.0),
        "purpose_count": with_purpose,
        "purpose_ratio": round(with_purpose / len(modules), 4) if modules else 0.0,
    }

    # Subpackage stats
    pkg_stats: dict[str, dict[str, int]] = defaultdict(
        lambda: {"files": 0, "lines": 0, "classes": 0, "functions": 0}
    )
    for info in modules.values():
        stats = pkg_stats[info.subpackage]
        stats["files"] += 1
        stats["lines"] += info.lines
        stats["classes"] += info.classes
        stats["functions"] += info.functions

    # Community drift: modules whose community label != their directory
    drifted = [
        {"module": name, "directory": modules[name].subpackage, "community": communities[name]}
        for name in sorted(modules)
        if communities[name] != modules[name].subpackage
    ]

    return {
        "generated_at": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "source": "scripts/analyze_codebase_graph.py",
        "root_package": root_package,
        "summary": {
            "total_modules": len(modules),
            "total_lines": sum(m.lines for m in modules.values()),
            "total_classes": sum(m.classes for m in modules.values()),
            "total_functions": sum(m.functions for m in modules.values()),
            "total_edges": len(edges),
            "total_cycles": len(cycles),
            "total_layer_violations": len(violations),
            "total_orphans": len(orphans),
            "total_community_drifts": len(drifted),
            "self_declared_layer_count": self_declared,
            "self_declared_layer_ratio": annotation_coverage["self_declared_layer_ratio"],
            "purpose_count": with_purpose,
            "purpose_ratio": annotation_coverage["purpose_ratio"],
        },
        "annotation_coverage": annotation_coverage,
        "god_nodes": god_nodes,
        "cycles": [{"cycle": c.cycle, "length": c.length} for c in cycles[:30]],  # cap at 30
        "layer_violations": [
            {
                "source": v.source_module,
                "source_layer": v.source_layer,
                "target": v.target_module,
                "target_layer": v.target_layer,
            }
            for v in violations
        ],
        "orphans": orphans[:50],
        "subpackage_stats": {k: dict(v) for k, v in sorted(pkg_stats.items())},
        "subpackage_coupling": coupling,
        "community_drifts": drifted[:30],
    }


def render_markdown(report: dict[str, Any]) -> str:
    """Render the report as a human-readable markdown document."""
    lines: list[str] = []
    s = report["summary"]

    lines.append("# ToneSoul Codebase Graph Analysis")
    lines.append("")
    lines.append(f"Generated: {report['generated_at']}")
    lines.append(f"Package: `{report['root_package']}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"| --- | ---: |")
    lines.append(f"| Modules | {s['total_modules']} |")
    lines.append(f"| Lines | {s['total_lines']:,} |")
    lines.append(f"| Classes | {s['total_classes']} |")
    lines.append(f"| Functions | {s['total_functions']:,} |")
    lines.append(f"| Import edges | {s['total_edges']} |")
    lines.append(f"| Circular deps | {s['total_cycles']} |")
    lines.append(f"| Layer violations | {s['total_layer_violations']} |")
    lines.append(f"| Orphan modules | {s['total_orphans']} |")
    lines.append(f"| Community drifts | {s['total_community_drifts']} |")
    lines.append(
        f"| Self-declared layer | "
        f"{s.get('self_declared_layer_count', 0)} / {s['total_modules']} "
        f"({(s.get('self_declared_layer_ratio', 0.0) * 100):.1f}%) |"
    )
    lines.append(
        f"| Purpose declared | "
        f"{s.get('purpose_count', 0)} / {s['total_modules']} "
        f"({(s.get('purpose_ratio', 0.0) * 100):.1f}%) |"
    )
    lines.append("")

    # God nodes
    lines.append("## God Nodes (Top 20 by coupling)")
    lines.append("")
    lines.append(
        "Modules with the highest total degree (in + out). " "High coupling = high change risk."
    )
    lines.append("")
    lines.append("| # | Module | Layer | Src | In | Out | Total | Purpose |")
    lines.append("| ---: | --- | --- | --- | ---: | ---: | ---: | --- |")
    for i, g in enumerate(report["god_nodes"], 1):
        name = g["module"].removeprefix(f"{report['root_package']}.")
        purpose = g.get("purpose", "") or "—"
        src = g.get("layer_source", "fallback")
        lines.append(
            f"| {i} | `{name}` | {g['layer']} | {src} | "
            f"{g['in_degree']} | {g['out_degree']} | **{g['total_degree']}** | {purpose} |"
        )
    lines.append("")

    # Circular dependencies
    if report["cycles"]:
        lines.append("## Circular Dependencies")
        lines.append("")
        lines.append(
            f"Found **{s['total_cycles']}** import cycles. "
            "These make testing and refactoring harder."
        )
        lines.append("")
        for i, c in enumerate(report["cycles"][:15], 1):
            short = [m.removeprefix(f"{report['root_package']}.") for m in c["cycle"]]
            lines.append(f"{i}. `{'` → `'.join(short)}` → (back)")
        if s["total_cycles"] > 15:
            lines.append(f"\n... and {s['total_cycles'] - 15} more")
        lines.append("")

    # Layer violations
    if report["layer_violations"]:
        lines.append("## Layer Boundary Violations")
        lines.append("")
        lines.append("Imports that cross layer boundaries in disallowed directions.")
        lines.append("")
        lines.append("| Source | Source Layer | → | Target | Target Layer |")
        lines.append("| --- | --- | --- | --- | --- |")
        for v in report["layer_violations"][:25]:
            src = v["source"].removeprefix(f"{report['root_package']}.")
            tgt = v["target"].removeprefix(f"{report['root_package']}.")
            lines.append(f"| `{src}` | {v['source_layer']} | → | `{tgt}` | {v['target_layer']} |")
        if len(report["layer_violations"]) > 25:
            lines.append(f"\n... and {len(report['layer_violations']) - 25} more")
        lines.append("")

    # Orphans
    if report["orphans"]:
        lines.append("## Orphan Modules (zero in-degree)")
        lines.append("")
        lines.append("Nobody imports these. Potential dead code or standalone entry points.")
        lines.append("")
        for o in report["orphans"]:
            short = o.removeprefix(f"{report['root_package']}.")
            lines.append(f"- `{short}`")
        lines.append("")

    # Subpackage stats
    lines.append("## Subpackage Stats")
    lines.append("")
    lines.append("| Subpackage | Layer | Files | Lines | Classes | Functions |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: |")
    for pkg, stats in sorted(report["subpackage_stats"].items()):
        layer = LAYER_MAP.get(pkg, "—")
        lines.append(
            f"| `{pkg}` | {layer} | {stats['files']} | "
            f"{stats['lines']:,} | {stats['classes']} | {stats['functions']} |"
        )
    lines.append("")

    # Coupling matrix (top cross-package edges)
    if report["subpackage_coupling"]:
        lines.append("## Cross-Package Coupling (top edges)")
        lines.append("")
        lines.append("| From | To | Edges |")
        lines.append("| --- | --- | ---: |")
        flat = []
        for src_pkg, targets in report["subpackage_coupling"].items():
            for tgt_pkg, count in targets.items():
                if src_pkg != tgt_pkg:
                    flat.append((src_pkg, tgt_pkg, count))
        flat.sort(key=lambda x: -x[2])
        for src_pkg, tgt_pkg, count in flat[:25]:
            lines.append(f"| `{src_pkg}` | `{tgt_pkg}` | {count} |")
        lines.append("")

    # Community drifts
    if report["community_drifts"]:
        lines.append("## Community Drifts")
        lines.append("")
        lines.append(
            "Modules whose import pattern suggests they belong to "
            "a different subpackage than their directory."
        )
        lines.append("")
        lines.append("| Module | Directory | Community |")
        lines.append("| --- | --- | --- |")
        for d in report["community_drifts"][:20]:
            short = d["module"].removeprefix(f"{report['root_package']}.")
            lines.append(f"| `{short}` | {d['directory']} | {d['community']} |")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Full-AST codebase graph analyzer for ToneSoul.")
    parser.add_argument(
        "--root",
        default="tonesoul",
        help="Root package to scan (default: tonesoul)",
    )
    parser.add_argument(
        "--output-dir",
        default="docs/status",
        help="Output directory for reports (default: docs/status)",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Print JSON to stdout, don't write files",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root (default: auto-detect)",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root) if args.repo_root else REPO_ROOT

    # Scan
    modules = scan_all_modules(args.root, repo_root)
    if not modules:
        print(f"No modules found under {args.root}/", file=sys.stderr)
        return 1

    # Analyze
    edges = build_edges(modules)
    degree = compute_degree(modules, edges)
    cycles = find_cycles(edges)
    violations = find_layer_violations(modules, edges)
    orphans = find_orphans(modules, degree)
    coupling = compute_subpackage_coupling(modules, edges)
    communities = detect_communities(modules, edges)

    # Report
    report = build_report(
        modules,
        edges,
        degree,
        cycles,
        violations,
        orphans,
        coupling,
        communities,
        args.root,
    )

    if args.json_only:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    # Write files
    out_dir = repo_root / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "codebase_graph_latest.json"
    md_path = out_dir / "codebase_graph_latest.md"

    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    markdown = render_markdown(report)
    md_path.write_text(markdown, encoding="utf-8")

    s = report["summary"]
    print(f"Scanned {s['total_modules']} modules, {s['total_lines']:,} lines")
    print(f"  Edges: {s['total_edges']}")
    print(
        f"  God node #1: {report['god_nodes'][0]['module']} "
        f"(degree={report['god_nodes'][0]['total_degree']})"
        if report["god_nodes"]
        else "  No edges found"
    )
    print(f"  Cycles: {s['total_cycles']}")
    print(f"  Layer violations: {s['total_layer_violations']}")
    print(f"  Orphans: {s['total_orphans']}")
    print(f"\nReports written to:")
    print(f"  {json_path.relative_to(repo_root)}")
    print(f"  {md_path.relative_to(repo_root)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
