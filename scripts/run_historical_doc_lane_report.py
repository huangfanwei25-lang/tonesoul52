#!/usr/bin/env python3
"""Report governance posture for historical archive and chronicle doc lanes."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

JSON_FILENAME = "historical_doc_lane_latest.json"
MARKDOWN_FILENAME = "historical_doc_lane_latest.md"

ARCHIVE_ROOT = Path("docs/archive")
CHRONICLE_ROOT = Path("docs/chronicles")
POLICY_PATH = Path("docs/architecture/HISTORICAL_DOC_LANE_POLICY.md")
CHRONICLE_README = CHRONICLE_ROOT / "README.md"
ARCHIVE_DEPRECATED_README = ARCHIVE_ROOT / "deprecated_modules" / "README.md"

CHRONICLE_MD_RE = re.compile(r"^scribe_chronicle_(\d{8}_\d{6})\.md$")
CHRONICLE_JSON_RE = re.compile(r"^scribe_chronicle_(\d{8}_\d{6})\.json$")
GENERATED_AT_RE = re.compile(r"Generated at\s+([0-9T:\-Z_]+)", re.IGNORECASE)


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _chronicle_timestamp_from_name(path: Path) -> str:
    match = CHRONICLE_MD_RE.match(path.name) or CHRONICLE_JSON_RE.match(path.name)
    return match.group(1) if match else ""


def _generated_marker(text: str) -> str:
    match = GENERATED_AT_RE.search("\n".join(text.splitlines()[:12]))
    return match.group(1) if match else ""


def build_report(repo_root: Path) -> dict[str, Any]:
    archive_root = repo_root / ARCHIVE_ROOT
    chronicle_root = repo_root / CHRONICLE_ROOT

    md_files = sorted(
        path
        for path in chronicle_root.glob("scribe_chronicle_*.md")
        if path.is_file() and CHRONICLE_MD_RE.match(path.name)
    )
    json_index = {
        path.stem: path
        for path in chronicle_root.glob("scribe_chronicle_*.json")
        if path.is_file() and CHRONICLE_JSON_RE.match(path.name)
    }

    chronicle_entries: list[dict[str, Any]] = []
    md_only: list[str] = []
    for md_path in md_files:
        twin = json_index.pop(md_path.stem, None)
        text = _read_text(md_path)
        chronicle_entries.append(
            {
                "path": md_path.relative_to(repo_root).as_posix(),
                "json_twin": twin.relative_to(repo_root).as_posix() if twin else "",
                "has_json_twin": twin is not None,
                "filename_timestamp": _chronicle_timestamp_from_name(md_path),
                "generated_at_marker": _generated_marker(text),
            }
        )
        if twin is None:
            md_only.append(md_path.relative_to(repo_root).as_posix())

    json_only = sorted(path.relative_to(repo_root).as_posix() for path in json_index.values())
    archive_markdown_count = (
        sum(1 for path in archive_root.rglob("*.md") if path.is_file())
        if archive_root.exists()
        else 0
    )

    generated_marker_count = sum(1 for item in chronicle_entries if item["generated_at_marker"])
    filename_timestamp_count = sum(1 for item in chronicle_entries if item["filename_timestamp"])
    primary_status_line = (
        "historical_doc_lane | "
        f"chronicles={len(chronicle_entries)} pairs={sum(1 for item in chronicle_entries if item['has_json_twin'])} "
        f"md_only={len(md_only)} json_only={len(json_only)}"
    )
    runtime_status_line = (
        f"policy={'present' if (repo_root / POLICY_PATH).exists() else 'missing'} "
        f"chronicle_readme={'present' if (repo_root / CHRONICLE_README).exists() else 'missing'} "
        f"archive_readme={'present' if (repo_root / ARCHIVE_DEPRECATED_README).exists() else 'missing'}"
    )
    artifact_policy_status_line = (
        "chronicle_metadata=lane_managed | filename_timestamp_and_generated_at_accepted"
    )

    return {
        "generated_at": _iso_now(),
        "contract": {
            "archive_root": ARCHIVE_ROOT.as_posix(),
            "chronicle_root": CHRONICLE_ROOT.as_posix(),
            "policy_path": POLICY_PATH.as_posix(),
            "chronicle_rule": "generated chronicle files inherit metadata posture from the lane policy and README",
            "archive_rule": "archive surfaces are historical reference, not current authority",
        },
        "metrics": {
            "archive_markdown_count": archive_markdown_count,
            "chronicle_markdown_count": len(chronicle_entries),
            "chronicle_json_pair_count": sum(
                1 for item in chronicle_entries if item["has_json_twin"]
            ),
            "chronicle_md_only_count": len(md_only),
            "chronicle_json_only_count": len(json_only),
            "filename_timestamp_count": filename_timestamp_count,
            "generated_marker_count": generated_marker_count,
        },
        "chronicle_entries": chronicle_entries,
        "chronicle_md_only": md_only,
        "chronicle_json_only": json_only,
        "primary_status_line": primary_status_line,
        "runtime_status_line": runtime_status_line,
        "artifact_policy_status_line": artifact_policy_status_line,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Historical Document Lane Latest",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- primary_status_line: `{payload['primary_status_line']}`",
        f"- runtime_status_line: `{payload['runtime_status_line']}`",
        f"- artifact_policy_status_line: `{payload['artifact_policy_status_line']}`",
        "",
        "## Contract",
        f"- archive_root: `{payload['contract']['archive_root']}`",
        f"- chronicle_root: `{payload['contract']['chronicle_root']}`",
        f"- policy_path: `{payload['contract']['policy_path']}`",
        f"- chronicle_rule: `{payload['contract']['chronicle_rule']}`",
        f"- archive_rule: `{payload['contract']['archive_rule']}`",
        "",
        "## Metrics",
    ]
    for key, value in payload["metrics"].items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(["", "## Chronicle Entries"])
    for entry in payload["chronicle_entries"]:
        lines.append(
            f"- `{entry['path']}` json_twin=`{entry['json_twin'] or 'none'}` "
            f"filename_timestamp=`{entry['filename_timestamp'] or 'missing'}` "
            f"generated_at_marker=`{entry['generated_at_marker'] or 'missing'}`"
        )

    lines.extend(["", "## Markdown Only"])
    for path in payload["chronicle_md_only"]:
        lines.append(f"- `{path}`")

    lines.extend(["", "## JSON Only"])
    for path in payload["chronicle_json_only"]:
        lines.append(f"- `{path}`")

    return "\n".join(lines) + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Report governance posture for historical archive and chronicle doc lanes."
    )
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
