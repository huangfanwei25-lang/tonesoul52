import json
import os
from typing import Dict, List

from .config import KNOWN_ENTRYPOINTS, WORKSPACE_ROOT, list_workspace_dirs, resolve_readme


def build_inventory() -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    for folder in list_workspace_dirs():
        name = os.path.basename(folder)
        entry = {
            "name": name,
            "path": folder,
            "has_git": os.path.isdir(os.path.join(folder, ".git")),
            "readme": resolve_readme(folder),
            "notes": [],
        }

        if name.lower().startswith("tone"):
            entry["notes"].append("ToneSoul-related workspace")

        results.append(entry)
    return results


def entrypoints_status() -> List[Dict[str, object]]:
    status = []
    for ep in KNOWN_ENTRYPOINTS:
        status.append(
            {
                "name": ep.name,
                "path": ep.path,
                "exists": os.path.exists(ep.path),
                "command": ep.command,
                "notes": ep.notes,
            }
        )
    return status


def write_inventory_report(output_dir: str) -> Dict[str, str]:
    os.makedirs(output_dir, exist_ok=True)
    inventory = {
        "workspace_root": WORKSPACE_ROOT,
        "workspaces": build_inventory(),
        "entrypoints": entrypoints_status(),
    }

    json_path = os.path.join(output_dir, "inventory.json")
    md_path = os.path.join(output_dir, "inventory.md")

    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(inventory, handle, indent=2)

    lines = []
    lines.append("# Workspace Inventory\n")
    lines.append(f"Root: `{WORKSPACE_ROOT}`\n")
    lines.append("## Workspaces\n")
    for item in inventory["workspaces"]:
        notes = ", ".join(item["notes"]) if item["notes"] else "-"
        lines.append(f"- {item['name']}: {item['path']}")
        lines.append(f"  - git: {item['has_git']} | readme: {item['readme']} | notes: {notes}")

    lines.append("\n## Entrypoints\n")
    for ep in inventory["entrypoints"]:
        lines.append(f"- {ep['name']}: {ep['path']} (exists: {ep['exists']})")
        if ep.get("command"):
            lines.append(f"  - cmd: {ep['command']}")
        if ep.get("notes"):
            lines.append(f"  - notes: {ep['notes']}")

    with open(md_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))

    return {"json": json_path, "md": md_path}
