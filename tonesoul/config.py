import os
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class EntryPoint:
    name: str
    path: str
    command: Optional[str] = None
    notes: Optional[str] = None


WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

KNOWN_ENTRYPOINTS: List[EntryPoint] = [
    EntryPoint(
        name="dashboard",
        path=os.path.join(WORKSPACE_ROOT, "apps", "dashboard", "run_dashboard.py"),
        command="python apps/dashboard/run_dashboard.py",
        notes="Streamlit dashboard launcher.",
    ),
    EntryPoint(
        name="dashboard_alt",
        path=os.path.join(WORKSPACE_ROOT, "apps", "dashboard", "frontend", "app.py"),
        command="python -m streamlit run apps/dashboard/frontend/app.py",
        notes="Direct Streamlit app entrypoint.",
    ),
    EntryPoint(
        name="yuhun_cli",
        path=os.path.join(WORKSPACE_ROOT, "apps", "cli", "yuhun_cli.py"),
        command="python apps/cli/yuhun_cli.py",
        notes="Interactive YuHun CLI.",
    ),
    EntryPoint(
        name="yuhun_loop_test",
        path=os.path.join(WORKSPACE_ROOT, "apps", "cli", "yuhun_cli.py"),
        command="python apps/cli/yuhun_cli.py --help",
        notes="YuHun CLI help smoke check (non-interactive).",
    ),
]


def list_workspace_dirs() -> List[str]:
    items = []
    for name in os.listdir(WORKSPACE_ROOT):
        if name in {"legacy", ".git", ".venv"}:
            continue
        full = os.path.join(WORKSPACE_ROOT, name)
        if os.path.isdir(full):
            items.append(full)
    return sorted(items)


def resolve_readme(folder: str) -> Optional[str]:
    for fname in ("README.md", "README_DEV.md", "HANDOFF.md"):
        candidate = os.path.join(folder, fname)
        if os.path.exists(candidate):
            return candidate
    return None


def entrypoints_index() -> Dict[str, EntryPoint]:
    return {ep.name: ep for ep in KNOWN_ENTRYPOINTS}
