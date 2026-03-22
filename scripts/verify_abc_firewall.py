#!/usr/bin/env python3
"""Verify the ToneSoul A/B/C firewall doctrine and entrypoint claim boundaries."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

JSON_FILENAME = "abc_firewall_latest.json"
MARKDOWN_FILENAME = "abc_firewall_latest.md"
DOCTRINE_PATH = "docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md"
DOCTRINE_REFERENCE_ALIASES = (
    DOCTRINE_PATH,
    "architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md",
)

ENTRYPOINT_DOCS = (
    "README.md",
    "README.zh-TW.md",
    "AI_ONBOARDING.md",
    "docs/README.md",
    "docs/INDEX.md",
    "docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md",
    "docs/notes/TONESOUL_ARCHITECTURE_MEMORY_ANCHOR_2026-03-22.md",
)

REQUIRED_DOCTRINE_HEADINGS = (
    "## Not A Replacement For The Eight-Layer Map",
    "## Disclaimer-First Protocol",
    "## The A/B/C Firewall",
    "### A Layer: Mechanism Layer",
    "### B Layer: Observable Layer",
    "### C Layer: Interpretation Layer",
    "## Required Writing Template",
)

REQUIRED_DISCLAIMER_TOKENS = (
    "executable governance components",
    "higher-order interpretations",
    "does not automatically describe the currently enforced rule",
)

PROHIBITED_PATTERNS = (
    re.compile(
        r"\b(?:we|tonesoul|mirrortone|語魂|the system|this system)\b.{0,40}"
        r"\b(?:can|will|does|lets?|allows?)\b.{0,40}"
        r"\b(?:edit|modify|rewrite|control|steer|intervene(?:\s+in)?|inject(?:\s+into)?)\b.{0,80}"
        r"\b(?:latent|hidden)\s+state\b",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:we|tonesoul|mirrortone|語魂|the system|this system)\b.{0,40}"
        r"\b(?:can|will|does|lets?|allows?)\b.{0,40}"
        r"\b(?:edit|modify|rewrite|control|steer|inject(?:\s+into)?)\b.{0,80}"
        r"\bmodel weights?\b",
        flags=re.IGNORECASE,
    ),
)

NEGATION_TOKENS = (
    "must not",
    "do not",
    "does not",
    "should not",
    "cannot",
    "can't",
    "never",
    "not claim",
)


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_path(value: str) -> str:
    normalized = str(value or "").strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _references_doctrine(text: str) -> bool:
    return any(alias in text for alias in DOCTRINE_REFERENCE_ALIASES)


def _scan_prohibited_claims(text: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        lowered = line.lower()
        if any(token in lowered for token in NEGATION_TOKENS):
            continue
        for pattern in PROHIBITED_PATTERNS:
            if pattern.search(line):
                findings.append(
                    {
                        "line": line_number,
                        "text": line,
                        "pattern": pattern.pattern,
                    }
                )
                break
    return findings


def build_report(repo_root: Path) -> dict[str, Any]:
    doctrine_file = repo_root / DOCTRINE_PATH
    issues: list[str] = []

    doctrine_exists = doctrine_file.exists()
    doctrine_text = _read(doctrine_file) if doctrine_exists else ""
    doctrine_headings = {
        heading: heading in doctrine_text for heading in REQUIRED_DOCTRINE_HEADINGS
    }
    disclaimer_tokens = {
        token: token in doctrine_text.lower() for token in REQUIRED_DISCLAIMER_TOKENS
    }

    if not doctrine_exists:
        issues.append(f"missing {DOCTRINE_PATH}")
    else:
        for heading, present in doctrine_headings.items():
            if not present:
                issues.append(f"{DOCTRINE_PATH} missing heading: {heading}")
        for token, present in disclaimer_tokens.items():
            if not present:
                issues.append(f"{DOCTRINE_PATH} missing disclaimer token: {token}")

    entrypoints: list[dict[str, Any]] = []
    for relative_path in ENTRYPOINT_DOCS:
        path = repo_root / relative_path
        exists = path.exists()
        text = _read(path) if exists else ""
        references_doctrine = _references_doctrine(text)
        prohibited_claims = _scan_prohibited_claims(text)
        entrypoints.append(
            {
                "path": relative_path,
                "exists": exists,
                "references_doctrine": references_doctrine,
                "prohibited_claim_count": len(prohibited_claims),
                "prohibited_claims": prohibited_claims,
            }
        )
        if not exists:
            issues.append(f"missing entrypoint doc: {relative_path}")
            continue
        if not references_doctrine:
            issues.append(f"{relative_path} missing A/B/C firewall doctrine reference")
        if prohibited_claims:
            issues.append(
                f"{relative_path} contains {len(prohibited_claims)} observable-shell boundary claim(s)"
            )

    reference_count = sum(1 for entry in entrypoints if entry["references_doctrine"])
    prohibited_claim_count = sum(entry["prohibited_claim_count"] for entry in entrypoints)
    primary_status_line = (
        "abc_firewall_ready | "
        f"entrypoint_refs={reference_count}/{len(ENTRYPOINT_DOCS)} "
        f"prohibited_claims={prohibited_claim_count} "
        f"doctrine_exists={'true' if doctrine_exists else 'false'}"
    )
    runtime_status_line = (
        "entrypoints | "
        f"doctrine={DOCTRINE_PATH} "
        "observable_shell=external_only "
        "latent_intervention_claims=forbidden"
    )
    artifact_policy_status_line = (
        "claim_governance=abc_firewall | " "mainline_terms<=3 disclaimer_first=true"
    )

    return {
        "generated_at": _iso_now(),
        "ok": len(issues) == 0,
        "doctrine": {
            "path": DOCTRINE_PATH,
            "exists": doctrine_exists,
            "required_headings": doctrine_headings,
            "disclaimer_tokens": disclaimer_tokens,
        },
        "entrypoints": entrypoints,
        "metrics": {
            "entrypoint_count": len(entrypoints),
            "reference_count": reference_count,
            "missing_reference_count": len(entrypoints) - reference_count,
            "prohibited_claim_count": prohibited_claim_count,
        },
        "primary_status_line": primary_status_line,
        "runtime_status_line": runtime_status_line,
        "artifact_policy_status_line": artifact_policy_status_line,
        "issues": issues,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# A/B/C Firewall Latest",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- ok: `{str(payload['ok']).lower()}`",
        f"- primary_status_line: `{payload['primary_status_line']}`",
        f"- runtime_status_line: `{payload['runtime_status_line']}`",
        f"- artifact_policy_status_line: `{payload['artifact_policy_status_line']}`",
        "",
        "## Doctrine",
        f"- path: `{payload['doctrine']['path']}`",
        f"- exists: `{str(payload['doctrine']['exists']).lower()}`",
    ]
    for heading, present in payload["doctrine"]["required_headings"].items():
        lines.append(f"- heading `{heading}`: `{str(present).lower()}`")
    for token, present in payload["doctrine"]["disclaimer_tokens"].items():
        lines.append(f"- disclaimer token `{token}`: `{str(present).lower()}`")

    lines.extend(["", "## Entrypoints"])
    for entry in payload["entrypoints"]:
        lines.append(f"- `{entry['path']}`")
        lines.append(f"  - references_doctrine: `{str(entry['references_doctrine']).lower()}`")
        lines.append(f"  - prohibited_claim_count: `{entry['prohibited_claim_count']}`")
        for finding in entry.get("prohibited_claims", []):
            lines.append(f"  - line {finding['line']}: {finding['text']}")

    if payload["issues"]:
        lines.extend(["", "## Issues"])
        for issue in payload["issues"]:
            lines.append(f"- {issue}")

    return "\n".join(lines) + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify the ToneSoul A/B/C firewall doctrine.")
    parser.add_argument("--repo-root", default=".", help="Repository root path.")
    parser.add_argument("--out-dir", default="docs/status", help="Output directory for artifacts.")
    parser.add_argument(
        "--strict", action="store_true", help="Exit non-zero if the doctrine check fails."
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    out_dir = (repo_root / args.out_dir).resolve()
    payload = build_report(repo_root)
    _write(out_dir / JSON_FILENAME, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    _write(out_dir / MARKDOWN_FILENAME, render_markdown(payload))
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.strict and not payload["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
