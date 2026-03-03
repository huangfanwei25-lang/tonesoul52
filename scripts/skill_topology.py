"""
Generate a lightweight topology map for ToneSoul modules and skill packages.

Outputs:
  - CLI tree text
  - JSON graph (default: docs/status/skill_topology.json)
  - Mermaid graph (default: docs/status/skill_topology.mmd)

Usage:
  python scripts/skill_topology.py
  python scripts/skill_topology.py --format json
  python scripts/skill_topology.py --format mermaid
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_ROOT = Path("tonesoul")
DEFAULT_SKILLS_DIR = Path(".agent/skills")
DEFAULT_WORKFLOWS_DIR = Path(".agent/workflows")
DEFAULT_JSON_OUT = Path("docs/status/skill_topology.json")
DEFAULT_MERMAID_OUT = Path("docs/status/skill_topology.mmd")

GROUP_LABELS: dict[str, str] = {
    "core": "Core Engine",
    "council": "Council",
    "memory": "Memory",
    "gates": "Gates",
    "skills": "Skills",
    "workflows": "Workflows",
}

GROUP_ORDER = ["core", "council", "memory", "gates", "skills", "workflows"]


@dataclass(frozen=True)
class Node:
    id: str
    label: str
    group: str
    file: str
    lines: int
    kind: str


@dataclass(frozen=True)
class Link:
    source: str
    target: str
    type: str


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def _module_name(root: Path, path: Path) -> str:
    relative = path.relative_to(root).with_suffix("")
    parts = ["tonesoul", *relative.parts]
    return ".".join(parts)


def _module_group(module_name: str) -> str:
    if module_name.startswith("tonesoul.council"):
        return "council"
    if module_name.startswith("tonesoul.memory"):
        return "memory"
    if module_name.startswith("tonesoul.gates"):
        return "gates"
    return "core"


def _parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}, text

    lines = text.splitlines()
    if len(lines) < 3:
        return {}, text

    end_index = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_index = idx
            break
    if end_index is None:
        return {}, text

    metadata: dict[str, str] = {}
    for line in lines[1:end_index]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("-"):
            continue
        if line.startswith(" ") or line.startswith("\t"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")

    body = "\n".join(lines[end_index + 1 :])
    return metadata, body


def _resolve_relative_import(current_module: str, module: str | None, level: int) -> str | None:
    if level <= 0:
        return module
    package = current_module.rsplit(".", 1)[0]
    parts = package.split(".")
    up = level - 1
    if up > len(parts):
        return None
    base_parts = parts[: len(parts) - up]
    if module:
        base_parts.extend(module.split("."))
    return ".".join(part for part in base_parts if part)


def _nearest_known_module(name: str, known_modules: set[str]) -> str | None:
    candidate = name
    while candidate:
        if candidate in known_modules:
            return candidate
        if "." not in candidate:
            return None
        candidate = candidate.rsplit(".", 1)[0]
    return None


def _extract_internal_imports(
    path: Path,
    module_name: str,
    known_modules: set[str],
) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return set()

    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name.strip()
                if not name.startswith("tonesoul"):
                    continue
                resolved = _nearest_known_module(name, known_modules)
                if resolved and resolved != module_name:
                    imports.add(resolved)
        elif isinstance(node, ast.ImportFrom):
            base = _resolve_relative_import(module_name, node.module, node.level)
            if not base or not base.startswith("tonesoul"):
                continue

            candidates: set[str] = set()
            if base in known_modules:
                candidates.add(base)

            for alias in node.names:
                if alias.name == "*":
                    continue
                alias_candidate = f"{base}.{alias.name}"
                resolved = _nearest_known_module(alias_candidate, known_modules)
                if resolved:
                    candidates.add(resolved)

            if not candidates:
                resolved = _nearest_known_module(base, known_modules)
                if resolved:
                    candidates.add(resolved)

            for candidate in candidates:
                if candidate != module_name:
                    imports.add(candidate)

    return imports


def _scan_python_modules(root: Path) -> tuple[list[Node], list[Link], dict[str, str]]:
    if not root.exists():
        return [], [], {}

    python_files = sorted(
        path for path in root.rglob("*.py") if path.is_file() and path.name != "__init__.py"
    )
    module_map: dict[str, Path] = {_module_name(root, path): path for path in python_files}
    known_modules = set(module_map)

    nodes: list[Node] = []
    links: list[Link] = []
    module_to_node_id: dict[str, str] = {}

    for module_name, path in sorted(module_map.items()):
        rel_path = path.as_posix()
        group = _module_group(module_name)
        node_id = module_name
        module_to_node_id[module_name] = node_id
        line_count = sum(1 for _ in path.open("r", encoding="utf-8", errors="replace"))
        nodes.append(
            Node(
                id=node_id,
                label=path.name,
                group=group,
                file=rel_path,
                lines=line_count,
                kind="python_module",
            )
        )

    for module_name, path in sorted(module_map.items()):
        source_id = module_to_node_id[module_name]
        imports = _extract_internal_imports(path, module_name, known_modules)
        for imported_module in sorted(imports):
            target_id = module_to_node_id.get(imported_module)
            if not target_id:
                continue
            links.append(Link(source=source_id, target=target_id, type="import"))

    return nodes, links, module_to_node_id


def _extract_module_mentions(content: str, module_to_node_id: dict[str, str]) -> set[str]:
    mentions: set[str] = set()

    for match in re.findall(r"tonesoul/[A-Za-z0-9_./-]+\.py", content):
        module = "tonesoul." + match[len("tonesoul/") : -3].replace("/", ".")
        node_id = module_to_node_id.get(module)
        if node_id:
            mentions.add(node_id)

    import_pattern = re.compile(
        r"(?:from\s+(tonesoul(?:\.[A-Za-z0-9_]+)+)\s+import)|(?:import\s+(tonesoul(?:\.[A-Za-z0-9_]+)+))"
    )
    for match in import_pattern.finditer(content):
        raw = match.group(1) or match.group(2)
        if not raw:
            continue
        candidate = raw.strip()
        while candidate:
            node_id = module_to_node_id.get(candidate)
            if node_id:
                mentions.add(node_id)
                break
            if "." not in candidate:
                break
            candidate = candidate.rsplit(".", 1)[0]

    return mentions


def _scan_skills(
    skills_dir: Path,
    module_to_node_id: dict[str, str],
) -> tuple[list[Node], list[Link]]:
    if not skills_dir.exists():
        return [], []

    nodes: list[Node] = []
    links: list[Link] = []

    for skill_file in sorted(skills_dir.glob("*/SKILL.md")):
        metadata, body = _parse_frontmatter(skill_file)
        skill_name = metadata.get("name") or skill_file.parent.name
        node_id = f"skill:{skill_name}"
        line_count = sum(1 for _ in skill_file.open("r", encoding="utf-8", errors="replace"))
        nodes.append(
            Node(
                id=node_id,
                label=skill_name,
                group="skills",
                file=skill_file.as_posix(),
                lines=line_count,
                kind="skill",
            )
        )

        mentions = _extract_module_mentions(body, module_to_node_id)
        for target in sorted(mentions):
            links.append(Link(source=node_id, target=target, type="mentions"))

    return nodes, links


def _scan_workflows(workflows_dir: Path) -> list[Node]:
    if not workflows_dir.exists():
        return []

    nodes: list[Node] = []
    for workflow_file in sorted(workflows_dir.glob("*.md")):
        metadata, _ = _parse_frontmatter(workflow_file)
        workflow_name = metadata.get("name") or workflow_file.stem
        line_count = sum(1 for _ in workflow_file.open("r", encoding="utf-8", errors="replace"))
        nodes.append(
            Node(
                id=f"workflow:{workflow_file.stem}",
                label=workflow_name,
                group="workflows",
                file=workflow_file.as_posix(),
                lines=line_count,
                kind="workflow",
            )
        )
    return nodes


def build_topology(
    root: Path = DEFAULT_ROOT,
    skills_dir: Path = DEFAULT_SKILLS_DIR,
    workflows_dir: Path = DEFAULT_WORKFLOWS_DIR,
) -> dict[str, Any]:
    py_nodes, py_links, module_to_node_id = _scan_python_modules(root)
    skill_nodes, skill_links = _scan_skills(skills_dir, module_to_node_id)
    workflow_nodes = _scan_workflows(workflows_dir)

    all_nodes = py_nodes + skill_nodes + workflow_nodes
    all_links = py_links + skill_links

    node_dicts: list[dict[str, Any]] = []
    for node in all_nodes:
        node_dicts.append(
            {
                "id": node.id,
                "label": node.label,
                "group": node.group,
                "file": node.file,
                "lines": node.lines,
                "kind": node.kind,
            }
        )

    link_dicts: list[dict[str, Any]] = []
    for link in all_links:
        link_dicts.append({"source": link.source, "target": link.target, "type": link.type})

    return {
        "meta": {
            "root": root.as_posix(),
            "skills_dir": skills_dir.as_posix(),
            "workflows_dir": workflows_dir.as_posix(),
            "node_count": len(node_dicts),
            "link_count": len(link_dicts),
        },
        "nodes": node_dicts,
        "links": link_dicts,
    }


def _short_module_id(module_id: str) -> str:
    if module_id.startswith("tonesoul."):
        return module_id.replace("tonesoul.", "", 1)
    return module_id


def render_tree(payload: dict[str, Any]) -> str:
    nodes = payload.get("nodes", [])
    links = payload.get("links", [])
    imports_by_source: dict[str, set[str]] = defaultdict(set)
    for link in links:
        if link.get("type") != "import":
            continue
        source = str(link.get("source", ""))
        target = str(link.get("target", ""))
        if source and target:
            imports_by_source[source].add(target)

    lines = ["ToneSoul Skill Topology", "|"]
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        grouped[str(node.get("group", "core"))].append(node)

    rendered_groups = [group for group in GROUP_ORDER if grouped.get(group)]
    for g_index, group in enumerate(rendered_groups):
        is_last_group = g_index == len(rendered_groups) - 1
        group_connector = "`- " if is_last_group else "+- "
        lines.append(f"{group_connector}{GROUP_LABELS.get(group, group.title())}")
        item_prefix_base = "   " if is_last_group else "|  "
        group_nodes = sorted(grouped[group], key=lambda item: str(item.get("label", "")))
        for n_index, node in enumerate(group_nodes):
            is_last_node = n_index == len(group_nodes) - 1
            node_connector = "`- " if is_last_node else "+- "
            node_id = str(node.get("id", ""))
            label = str(node.get("label", ""))
            if group in {"core", "council", "memory", "gates"}:
                imports = sorted(
                    _short_module_id(value) for value in imports_by_source.get(node_id, set())
                )
                suffix = f" (imports: {', '.join(imports)})" if imports else " (imports: none)"
                lines.append(f"{item_prefix_base}{node_connector}{label}{suffix}")
            else:
                lines.append(f"{item_prefix_base}{node_connector}{label}")
    return "\n".join(lines)


def render_mermaid(payload: dict[str, Any]) -> str:
    nodes = payload.get("nodes", [])
    links = payload.get("links", [])
    id_map: dict[str, str] = {}

    lines = ["graph TD"]
    for index, node in enumerate(nodes, start=1):
        raw_id = str(node.get("id", ""))
        label = str(node.get("label", raw_id)).replace('"', "'")
        mermaid_id = f"N{index}"
        id_map[raw_id] = mermaid_id
        lines.append(f'    {mermaid_id}["{label}"]')

    for link in links:
        source = str(link.get("source", ""))
        target = str(link.get("target", ""))
        link_type = str(link.get("type", ""))
        source_id = id_map.get(source)
        target_id = id_map.get(target)
        if not source_id or not target_id:
            continue
        if link_type == "import":
            lines.append(f"    {source_id} --> {target_id}")
        else:
            lines.append(f"    {source_id} -.-> {target_id}")

    return "\n".join(lines)


def write_outputs(payload: dict[str, Any], json_out: Path, mermaid_out: Path) -> None:
    json_out.parent.mkdir(parents=True, exist_ok=True)
    mermaid_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    mermaid_out.write_text(render_mermaid(payload) + "\n", encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate ToneSoul skill topology.")
    parser.add_argument(
        "--format",
        choices=["text", "json", "mermaid"],
        default="text",
        help="Output format for stdout.",
    )
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="Python module root to scan.")
    parser.add_argument(
        "--skills-dir",
        default=str(DEFAULT_SKILLS_DIR),
        help="Skill directory containing SKILL.md files.",
    )
    parser.add_argument(
        "--workflows-dir",
        default=str(DEFAULT_WORKFLOWS_DIR),
        help="Workflow markdown directory.",
    )
    parser.add_argument(
        "--json-out",
        default=str(DEFAULT_JSON_OUT),
        help="Path to write JSON topology.",
    )
    parser.add_argument(
        "--mermaid-out",
        default=str(DEFAULT_MERMAID_OUT),
        help="Path to write Mermaid topology.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    payload = build_topology(
        root=Path(args.root),
        skills_dir=Path(args.skills_dir),
        workflows_dir=Path(args.workflows_dir),
    )
    write_outputs(payload, json_out=Path(args.json_out), mermaid_out=Path(args.mermaid_out))

    if args.format == "json":
        _emit(payload)
    elif args.format == "mermaid":
        print(render_mermaid(payload))
    else:
        print(render_tree(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
