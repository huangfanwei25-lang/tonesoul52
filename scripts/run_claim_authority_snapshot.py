#!/usr/bin/env python3
"""Generate a machine-readable claim-authority snapshot from distillation docs."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

MATRIX_PATH = Path("docs/architecture/TONESOUL_CLAIM_AUTHORITY_MATRIX.md")
BOUNDARY_PATH = Path("docs/architecture/TONESOUL_LAW_RUNTIME_BOUNDARY_CONTRACT.md")

JSON_FILENAME = "claim_authority_latest.json"
MARKDOWN_FILENAME = "claim_authority_latest.md"

CATEGORY_LABELS = {
    "1": "Active Runtime / Audit Dependency",
    "2": "Active Governance Vocabulary",
    "3": "Theory / Research Lane",
    "4": "Projection / Narrative / Worldview Lane",
}

PATH_PATTERN = re.compile(r"[A-Za-z0-9_./-]+\.(?:md|py|json|jsonl|txt|yaml|yml)")


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_text(repo_root: Path, rel_path: Path) -> str:
    return (repo_root / rel_path).read_text(encoding="utf-8")


def _clean_inline(value: str) -> str:
    cleaned = value.replace("**", "").replace("`", "").strip()
    return re.sub(r"\s+", " ", cleaned)


def _split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_separator_line(line: str) -> bool:
    cells = _split_markdown_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells)


def _extract_tables(text: str) -> list[dict[str, Any]]:
    tables: list[dict[str, Any]] = []
    heading = ""
    lines = text.splitlines()
    index = 0

    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            index += 1
            continue

        if (
            stripped.startswith("|")
            and index + 1 < len(lines)
            and _is_separator_line(lines[index + 1])
        ):
            headers = [_clean_inline(cell) for cell in _split_markdown_row(lines[index])]
            index += 2
            rows: list[dict[str, str]] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                row_line = lines[index].strip()
                if _is_separator_line(row_line):
                    index += 1
                    continue
                cells = [_clean_inline(cell) for cell in _split_markdown_row(row_line)]
                if len(cells) < len(headers):
                    cells.extend([""] * (len(headers) - len(cells)))
                elif len(cells) > len(headers):
                    prefix = cells[: len(headers) - 1]
                    suffix = " | ".join(cells[len(headers) - 1 :])
                    cells = prefix + [suffix]
                rows.append(dict(zip(headers, cells)))
                index += 1
            tables.append({"heading": heading, "headers": headers, "rows": rows})
            continue

        index += 1

    return tables


def _normalize_term_key(value: str) -> str:
    cleaned = _clean_inline(value).replace("’", "'")
    normalized = unicodedata.normalize("NFKD", cleaned)
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower()
    return re.sub(r"[^a-z0-9]+", "", normalized)


def _term_aliases(value: str) -> list[str]:
    cleaned = _clean_inline(value)
    aliases = {
        _normalize_term_key(cleaned),
        _normalize_term_key(re.sub(r"\s*\([^)]*\)", "", cleaned).strip()),
        _normalize_term_key(cleaned.split(":", 1)[0].strip()),
    }

    first_token = re.split(r"\s+", cleaned, maxsplit=1)[0].strip()
    aliases.add(_normalize_term_key(first_token))

    paradox_match = re.search(r"paradox[_\s-]*0*(\d+)", cleaned, re.IGNORECASE)
    if paradox_match:
        aliases.add(_normalize_term_key(f"PARADOX_{int(paradox_match.group(1)):03d}"))

    return [alias for alias in aliases if alias]


def _parse_int(value: str) -> int | None:
    digits = re.sub(r"[^0-9]", "", value or "")
    return int(digits) if digits else None


def _extract_paths(value: str) -> list[str]:
    paths = []
    seen: set[str] = set()
    for match in PATH_PATTERN.findall(value):
        if match not in seen:
            paths.append(match)
            seen.add(match)
    return paths


def _rely_level(value: str) -> str:
    lowered = value.lower()
    if lowered.startswith("yes"):
        return "yes"
    if lowered.startswith("only with verification"):
        return "verify"
    if lowered.startswith("no"):
        return "no"
    return "mixed"


def _status_bucket(value: str) -> str:
    lowered = value.lower().strip()
    if lowered.startswith("hard runtime"):
        return "hard runtime"
    if lowered.startswith("runtime-adjacent"):
        return "runtime-adjacent"
    if lowered.startswith("test-backed"):
        return "test-backed"
    if lowered.startswith("doc-only"):
        return "doc-only"
    if lowered.startswith("research/theory"):
        return "research/theory"
    if lowered.startswith("projection-only"):
        return "projection-only"
    return value


def _build_matrix_terms(text: str) -> list[dict[str, Any]]:
    terms: list[dict[str, Any]] = []
    for table in _extract_tables(text):
        heading = table["heading"]
        if not heading.startswith("Matrix:"):
            continue
        section = heading.split("Matrix:", 1)[1].strip()
        for row in table["rows"]:
            terms.append(
                {
                    "matrix_index": _parse_int(row.get("#", "")),
                    "term": row.get("Term", ""),
                    "section": section,
                    "authority_roles": [
                        part.strip() for part in row.get("Authority", "").split(",") if part.strip()
                    ],
                    "implementation_status": row.get("Status", ""),
                    "status_bucket": _status_bucket(row.get("Status", "")),
                    "source_files": _extract_paths(row.get("Source Files", "")),
                    "source_files_raw": row.get("Source Files", ""),
                    "rely_guidance": row.get("Rely?", ""),
                    "rely_level": _rely_level(row.get("Rely?", "")),
                }
            )

    identifiers: Counter[str] = Counter()
    for term in terms:
        base = _normalize_term_key(term["term"]) or f"term{term.get('matrix_index') or 'unknown'}"
        identifiers[base] += 1
        term["id"] = base if identifiers[base] == 1 else f"{base}_{identifiers[base]}"

    return terms


def _build_boundary_lookup(text: str) -> list[dict[str, Any]]:
    for table in _extract_tables(text):
        if table["heading"] != "Decision Table: Quick Lookup":
            continue
        entries: list[dict[str, Any]] = []
        for row in table["rows"]:
            category_raw = row.get("Category", "").strip()
            category_code = re.sub(r"[^0-9]", "", category_raw)
            entries.append(
                {
                    "term": row.get("Term", ""),
                    "category_code": category_code,
                    "category_label": CATEGORY_LABELS.get(category_code, ""),
                    "partially_implemented": "*" in category_raw,
                    "verdict": row.get("One-Line Verdict", ""),
                    "aliases": _term_aliases(row.get("Term", "")),
                }
            )
        return entries
    return []


def _build_alias_map(entries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    alias_map: dict[str, dict[str, Any]] = {}
    for entry in entries:
        for alias in entry["aliases"]:
            alias_map.setdefault(alias, entry)
    return alias_map


def _find_boundary_entry(term: str, alias_map: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    aliases = _term_aliases(term)
    for alias in aliases:
        if alias in alias_map:
            return alias_map[alias]
    for alias in aliases:
        for mapped_alias, entry in alias_map.items():
            if alias.startswith(mapped_alias) or mapped_alias.startswith(alias):
                return entry
    return None


def _extract_named_table(text: str, heading_name: str) -> list[dict[str, str]]:
    for table in _extract_tables(text):
        if table["heading"] == heading_name:
            return table["rows"]
    return []


def build_report(repo_root: Path) -> dict[str, Any]:
    matrix_text = _read_text(repo_root, MATRIX_PATH)
    boundary_text = _read_text(repo_root, BOUNDARY_PATH)

    terms = _build_matrix_terms(matrix_text)
    boundary_entries = _build_boundary_lookup(boundary_text)
    alias_map = _build_alias_map(boundary_entries)

    for term in terms:
        boundary_entry = _find_boundary_entry(term["term"], alias_map)
        if boundary_entry is None:
            term["boundary_category_code"] = ""
            term["boundary_category_label"] = ""
            term["boundary_partially_implemented"] = False
            term["boundary_verdict"] = ""
            continue
        term["boundary_category_code"] = boundary_entry["category_code"]
        term["boundary_category_label"] = boundary_entry["category_label"]
        term["boundary_partially_implemented"] = boundary_entry["partially_implemented"]
        term["boundary_verdict"] = boundary_entry["verdict"]

    top_risks = _extract_named_table(matrix_text, "Top 10 Overclaiming Risks")

    raw_status_counts = Counter(term["implementation_status"] for term in terms)
    status_counts = Counter(term["status_bucket"] for term in terms)
    authority_role_counts = Counter(
        role for term in terms for role in term["authority_roles"] if role
    )
    category_counts = Counter(
        entry["category_code"] for entry in boundary_entries if entry["category_code"]
    )

    safe_reliance_terms = [term["term"] for term in terms if term["rely_level"] == "yes"]
    verification_required_terms = [
        term["term"] for term in terms if term["rely_level"] in {"verify", "mixed"}
    ]

    primary_status_line = (
        "claim_authority_snapshot | "
        f"terms={len(terms)} hard_runtime={status_counts.get('hard runtime', 0)} "
        f"runtime_adjacent={status_counts.get('runtime-adjacent', 0)} "
        f"test_backed={status_counts.get('test-backed', 0)} "
        f"doc_only={status_counts.get('doc-only', 0)} "
        f"research_theory={status_counts.get('research/theory', 0)} "
        f"projection_only={status_counts.get('projection-only', 0)}"
    )
    runtime_status_line = (
        "claim_authority_lookup | "
        f"high_confusion_terms={len(boundary_entries)} "
        f"safe_reliance={len(safe_reliance_terms)} "
        f"verification_required={len(verification_required_terms)} "
        f"overclaiming_risks={len(top_risks)}"
    )
    artifact_policy_status_line = (
        "boundary_snapshot=subordinate_to_code_tests_axioms_and_canonical_contracts | "
        "machine_lookup=true"
    )

    return {
        "generated_at": _iso_now(),
        "source_documents": {
            "matrix": MATRIX_PATH.as_posix(),
            "boundary_contract": BOUNDARY_PATH.as_posix(),
        },
        "metrics": {
            "term_count": len(terms),
            "high_confusion_term_count": len(boundary_entries),
            "safe_reliance_term_count": len(safe_reliance_terms),
            "verification_required_term_count": len(verification_required_terms),
            "top_overclaiming_risk_count": len(top_risks),
            "status_counts": dict(sorted(status_counts.items())),
            "raw_status_counts": dict(sorted(raw_status_counts.items())),
            "authority_role_counts": dict(sorted(authority_role_counts.items())),
            "boundary_category_counts": dict(sorted(category_counts.items())),
        },
        "terms": terms,
        "high_confusion_lookup": [
            {
                "term": entry["term"],
                "category_code": entry["category_code"],
                "category_label": entry["category_label"],
                "partially_implemented": entry["partially_implemented"],
                "verdict": entry["verdict"],
            }
            for entry in boundary_entries
        ],
        "top_overclaiming_risks": top_risks,
        "safe_reliance_terms": safe_reliance_terms,
        "verification_required_terms": verification_required_terms,
        "primary_status_line": primary_status_line,
        "runtime_status_line": runtime_status_line,
        "artifact_policy_status_line": artifact_policy_status_line,
    }


def _escape_cell(value: Any) -> str:
    return str(value).replace("|", "\\|")


def render_markdown(payload: dict[str, Any]) -> str:
    metrics = payload["metrics"]
    lines = [
        "# Claim Authority Latest",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- primary_status_line: `{payload['primary_status_line']}`",
        f"- runtime_status_line: `{payload['runtime_status_line']}`",
        f"- artifact_policy_status_line: `{payload['artifact_policy_status_line']}`",
        "",
        "## Metrics",
        f"- `term_count`: `{metrics['term_count']}`",
        f"- `high_confusion_term_count`: `{metrics['high_confusion_term_count']}`",
        f"- `safe_reliance_term_count`: `{metrics['safe_reliance_term_count']}`",
        f"- `verification_required_term_count`: "
        f"`{metrics['verification_required_term_count']}`",
        f"- `top_overclaiming_risk_count`: `{metrics['top_overclaiming_risk_count']}`",
        "",
        "## High-Confusion Quick Lookup",
        "",
        "| Term | Category | Partial | Verdict |",
        "|------|----------|---------|---------|",
    ]

    for entry in payload["high_confusion_lookup"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_cell(entry["term"]),
                    _escape_cell(entry["category_label"] or entry["category_code"]),
                    "yes" if entry["partially_implemented"] else "no",
                    _escape_cell(entry["verdict"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Top Overclaiming Risks",
            "",
            "| Risk | Term | What It Sounds Like | What It Actually Is |",
            "|------|------|---------------------|---------------------|",
        ]
    )

    for row in payload["top_overclaiming_risks"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_cell(row.get("Risk", "")),
                    _escape_cell(row.get("Term", "")),
                    _escape_cell(row.get("What It Sounds Like", "")),
                    _escape_cell(row.get("What It Actually Is", "")),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Safe Reliance Terms"])
    for term in payload["safe_reliance_terms"]:
        lines.append(f"- `{term}`")

    lines.extend(
        [
            "",
            "## Full Term Table",
            "",
            "| # | Term | Section | Status | Rely | Boundary Category |",
            "|---|------|---------|--------|------|-------------------|",
        ]
    )

    for term in payload["terms"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    _escape_cell(term.get("matrix_index", "")),
                    _escape_cell(term["term"]),
                    _escape_cell(term["section"]),
                    _escape_cell(term["implementation_status"]),
                    _escape_cell(term["rely_guidance"]),
                    _escape_cell(
                        term["boundary_category_label"] or term["boundary_category_code"] or "-"
                    ),
                ]
            )
            + " |"
        )

    return "\n".join(lines) + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a machine-readable claim-authority status snapshot."
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
