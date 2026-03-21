"""
Verify command registry consistency from tonesoul.config.KNOWN_ENTRYPOINTS.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shlex
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.config import KNOWN_ENTRYPOINTS  # noqa: E402

JSON_FILENAME = "command_registry_latest.json"
MARKDOWN_FILENAME = "command_registry_latest.md"


def _is_python_executable(token: str) -> bool:
    normalized = token.replace("\\", "/").lower()
    return (
        normalized.endswith("/python")
        or normalized.endswith("/python.exe")
        or token
        in {
            "python",
            "python3",
        }
    )


def _tokenize(command: str) -> list[str]:
    try:
        return shlex.split(command, posix=False)
    except ValueError:
        return command.split()


def _resolve_path(repo_root: Path, raw: str) -> Path:
    path = Path(raw)
    if path.is_absolute():
        return path
    return (repo_root / path).resolve()


def _entry_payload(entry_name: str, command: str, path: str) -> dict[str, Any]:
    return {
        "name": entry_name,
        "path": path,
        "command": command,
        "issues": [],
        "warnings": [],
    }


def _append_issue(payload: dict[str, Any], message: str) -> None:
    payload["issues"].append(message)


def _append_warning(payload: dict[str, Any], message: str) -> None:
    payload["warnings"].append(message)


def _check_script_target(
    payload: dict[str, Any],
    repo_root: Path,
    script_token: str,
    *,
    label: str,
) -> None:
    resolved = _resolve_path(repo_root, script_token)
    key = f"{label}_resolved"
    payload[key] = str(resolved)
    payload[f"{label}_exists"] = resolved.exists()
    if not resolved.exists():
        _append_issue(payload, f"{label} target missing: {script_token}")


def _check_module_target(payload: dict[str, Any], module_name: str) -> None:
    payload["module_name"] = module_name
    if module_name.startswith("tonesoul"):
        spec = importlib.util.find_spec(module_name)
        payload["module_resolvable"] = spec is not None
        if spec is None:
            _append_issue(payload, f"module target not importable: {module_name}")
        return
    _append_warning(payload, f"external module target not validated: {module_name}")


def _iter_entry_records(repo_root: Path, entrypoints: Sequence[Any]) -> Iterable[dict[str, Any]]:
    seen_names: set[str] = set()
    duplicate_names: set[str] = set()
    for entry in entrypoints:
        name = str(getattr(entry, "name", ""))
        if name in seen_names:
            duplicate_names.add(name)
        seen_names.add(name)

    for entry in entrypoints:
        name = str(getattr(entry, "name", ""))
        path = str(getattr(entry, "path", ""))
        command = str(getattr(entry, "command", "") or "")
        payload = _entry_payload(name, command, path)

        resolved_entry_path = _resolve_path(repo_root, path)
        payload["resolved_path"] = str(resolved_entry_path)
        payload["path_exists"] = resolved_entry_path.exists()
        if not payload["path_exists"]:
            _append_issue(payload, f"entry path missing: {path}")

        if name in duplicate_names:
            _append_issue(payload, f"duplicate entrypoint name: {name}")

        if not command.strip():
            _append_issue(payload, "missing command")
            yield payload
            continue

        tokens = _tokenize(command)
        payload["command_tokens"] = tokens
        if not tokens:
            _append_issue(payload, "empty command after tokenization")
            yield payload
            continue

        if _is_python_executable(tokens[0]) and len(tokens) >= 2:
            if tokens[1] == "-m":
                if len(tokens) >= 3:
                    _check_module_target(payload, tokens[2])
                    if len(tokens) >= 5 and tokens[3] == "run":
                        _check_script_target(payload, repo_root, tokens[4], label="run_script")
                else:
                    _append_issue(payload, "python -m command missing module token")
            elif tokens[1].endswith(".py"):
                _check_script_target(payload, repo_root, tokens[1], label="script")
            else:
                _append_warning(
                    payload,
                    f"python command uses unsupported target format: {tokens[1]}",
                )
        else:
            _append_warning(payload, f"non-python command not validated: {tokens[0]}")

        yield payload


def build_report(repo_root: Path, entrypoints: Sequence[Any] | None = None) -> dict[str, Any]:
    targets = list(KNOWN_ENTRYPOINTS if entrypoints is None else entrypoints)
    entries = list(_iter_entry_records(repo_root, targets))
    issue_count = sum(len(entry["issues"]) for entry in entries)
    warning_count = sum(len(entry["warnings"]) for entry in entries)
    return {
        "overall_ok": issue_count == 0,
        "repo_root": str(repo_root),
        "entrypoint_count": len(entries),
        "issue_count": issue_count,
        "warning_count": warning_count,
        "entries": entries,
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Command Registry Latest",
        "",
        f"- overall_ok: {str(payload['overall_ok']).lower()}",
        f"- entrypoint_count: {payload['entrypoint_count']}",
        f"- issue_count: {payload['issue_count']}",
        f"- warning_count: {payload['warning_count']}",
        "",
    ]
    if payload["issue_count"] == 0:
        lines.append("## Issues")
        lines.append("- None")
    else:
        lines.append("## Issues")
        for entry in payload["entries"]:
            for message in entry["issues"]:
                lines.append(f"- `{entry['name']}`: {message}")

    if payload["warning_count"] > 0:
        lines.append("")
        lines.append("## Warnings")
        for entry in payload["entries"]:
            for message in entry["warnings"]:
                lines.append(f"- `{entry['name']}`: {message}")

    return "\n".join(lines) + "\n"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_markdown(payload), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify configured command entrypoints.")
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--out-dir", default="docs/status", help="Output directory for artifacts.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when registry issues are found.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo_root).resolve()
    out_dir = (repo_root / args.out_dir).resolve()
    payload = build_report(repo_root=repo_root)
    _write_json(out_dir / JSON_FILENAME, payload)
    _write_markdown(out_dir / MARKDOWN_FILENAME, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.strict and not payload["overall_ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
