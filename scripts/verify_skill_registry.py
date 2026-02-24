"""
Verify skill registry metadata and integrity for .agent/skills.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ID_PATTERN = re.compile(r"^[a-z0-9_]+$")
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
TRUST_TIERS = {"trusted", "reviewed", "experimental"}


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _emit(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    else:
        print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _as_posix(path: Path) -> str:
    return str(path).replace("\\", "/")


def _normalize_sha256(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def _parse_frontmatter(path: Path) -> dict[str, Any] | None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")

    if not text.startswith("---\n"):
        return None
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return None
    try:
        payload = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None
    return payload if isinstance(payload, dict) else None


def _parse_date(value: str) -> date | None:
    if not DATE_PATTERN.match(value):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            result.append(item.strip())
    return result


def _discover_skill_files(skills_root: Path, repo_root: Path) -> set[str]:
    discovered: set[str] = set()
    if not skills_root.exists():
        return discovered
    for candidate in skills_root.glob("*/SKILL.md"):
        if candidate.is_file():
            discovered.add(_as_posix(candidate.resolve().relative_to(repo_root)))
    return discovered


def _validate_registry_schema_shape(schema_payload: Any) -> tuple[bool, str]:
    if not isinstance(schema_payload, dict):
        return False, "schema payload is missing or invalid JSON object"
    if schema_payload.get("type") != "object":
        return False, "schema root type must be object"
    defs = schema_payload.get("$defs")
    if not isinstance(defs, dict) or "skill" not in defs:
        return False, "schema must define $defs.skill"
    return True, "schema shape accepted"


def evaluate_registry(
    *,
    registry_payload: Any,
    schema_payload: Any,
    repo_root: Path,
    skills_root: Path,
    today: date,
) -> dict[str, Any]:
    checks: list[dict[str, str]] = []

    def add_check(name: str, status: str, detail: str) -> None:
        checks.append({"name": name, "status": status, "detail": detail})

    schema_ok, schema_detail = _validate_registry_schema_shape(schema_payload)
    add_check("schema", "pass" if schema_ok else "fail", schema_detail)

    if not isinstance(registry_payload, dict):
        add_check("registry", "fail", "registry payload is missing or invalid JSON object")
        failed = [item for item in checks if item["status"] == "fail"]
        warnings = [item for item in checks if item["status"] == "warn"]
        return {
            "generated_at": _iso_now(),
            "ok": False,
            "failed_count": len(failed),
            "warning_count": len(warnings),
            "checks": checks,
        }

    registry_version = str(registry_payload.get("registry_version") or "")
    if not SEMVER_PATTERN.match(registry_version):
        add_check("registry_version", "fail", f"invalid semver: {registry_version!r}")
    else:
        add_check("registry_version", "pass", f"registry version={registry_version}")

    max_review_age_days_raw = registry_payload.get("max_review_age_days")
    if not isinstance(max_review_age_days_raw, int) or max_review_age_days_raw < 1:
        add_check("max_review_age_days", "fail", "max_review_age_days must be integer >= 1")
        max_review_age_days = 180
    else:
        max_review_age_days = max_review_age_days_raw
        add_check("max_review_age_days", "pass", f"value={max_review_age_days}")

    skills = registry_payload.get("skills")
    if not isinstance(skills, list) or not skills:
        add_check("skills", "fail", "skills must be a non-empty list")
        skills = []
    else:
        add_check("skills", "pass", f"{len(skills)} skill entries found")

    registry_paths: set[str] = set()
    registry_ids: set[str] = set()
    discovered = _discover_skill_files(skills_root, repo_root)
    if not discovered:
        add_check("discovery", "warn", f"no skill files discovered under {skills_root}")
    else:
        add_check("discovery", "pass", f"discovered {len(discovered)} skill file(s)")

    for index, entry in enumerate(skills):
        label = f"skill[{index}]"
        if not isinstance(entry, dict):
            add_check(label, "fail", "entry must be an object")
            continue

        entry_id = str(entry.get("id") or "")
        if not ID_PATTERN.match(entry_id):
            add_check(f"{label}.id", "fail", f"invalid id: {entry_id!r}")
            continue
        if entry_id in registry_ids:
            add_check(f"{label}.id", "fail", f"duplicate id: {entry_id}")
            continue
        registry_ids.add(entry_id)
        add_check(f"{label}.id", "pass", entry_id)

        version = str(entry.get("version") or "")
        if not SEMVER_PATTERN.match(version):
            add_check(f"{label}.version", "fail", f"invalid semver: {version!r}")
        else:
            add_check(f"{label}.version", "pass", version)

        license_name = str(entry.get("license") or "").strip()
        if not license_name:
            add_check(f"{label}.license", "fail", "license must be non-empty")
        else:
            add_check(f"{label}.license", "pass", license_name)

        triggers = _as_string_list(entry.get("triggers"))
        if not triggers:
            add_check(f"{label}.triggers", "fail", "triggers must contain at least one string")
        else:
            add_check(f"{label}.triggers", "pass", f"{len(triggers)} trigger(s)")

        compatibility = entry.get("compatibility")
        if not isinstance(compatibility, dict):
            add_check(f"{label}.compatibility", "fail", "compatibility must be an object")
        else:
            runtime_values = _as_string_list(compatibility.get("runtime"))
            os_values = _as_string_list(compatibility.get("os"))
            if not runtime_values:
                add_check(f"{label}.compatibility.runtime", "fail", "runtime list is required")
            else:
                add_check(
                    f"{label}.compatibility.runtime",
                    "pass",
                    f"{len(runtime_values)} runtime target(s)",
                )
            if not os_values:
                add_check(f"{label}.compatibility.os", "fail", "os list is required")
            else:
                add_check(
                    f"{label}.compatibility.os",
                    "pass",
                    f"{len(os_values)} os target(s)",
                )

        trust = entry.get("trust")
        reviewed_at_date: date | None = None
        if not isinstance(trust, dict):
            add_check(f"{label}.trust", "fail", "trust must be an object")
        else:
            tier = str(trust.get("tier") or "")
            if tier not in TRUST_TIERS:
                add_check(f"{label}.trust.tier", "fail", f"invalid tier: {tier!r}")
            else:
                add_check(f"{label}.trust.tier", "pass", tier)

            review_owner = str(trust.get("review_owner") or "").strip()
            if not review_owner:
                add_check(f"{label}.trust.review_owner", "fail", "review_owner must be non-empty")
            else:
                add_check(f"{label}.trust.review_owner", "pass", review_owner)

            reviewed_at = str(trust.get("reviewed_at") or "")
            reviewed_at_date = _parse_date(reviewed_at)
            if reviewed_at_date is None:
                add_check(f"{label}.trust.reviewed_at", "fail", f"invalid date: {reviewed_at!r}")
            else:
                age_days = (today - reviewed_at_date).days
                if age_days < 0:
                    add_check(
                        f"{label}.trust.reviewed_at",
                        "fail",
                        f"reviewed_at is in future: {reviewed_at}",
                    )
                elif age_days > max_review_age_days:
                    add_check(
                        f"{label}.trust.reviewed_at",
                        "fail",
                        f"stale review: age_days={age_days}, max={max_review_age_days}",
                    )
                else:
                    add_check(
                        f"{label}.trust.reviewed_at",
                        "pass",
                        f"age_days={age_days}",
                    )

        relative_path = str(entry.get("path") or "").replace("\\", "/")
        if not relative_path:
            add_check(f"{label}.path", "fail", "path must be non-empty")
            continue
        if relative_path in registry_paths:
            add_check(f"{label}.path", "fail", f"duplicate path: {relative_path}")
            continue
        registry_paths.add(relative_path)
        add_check(f"{label}.path", "pass", relative_path)

        absolute_path = (repo_root / relative_path).resolve()
        if not absolute_path.exists() or not absolute_path.is_file():
            add_check(f"{label}.path.exists", "fail", f"file not found: {relative_path}")
            continue

        integrity = entry.get("integrity")
        expected_sha = ""
        if not isinstance(integrity, dict):
            add_check(f"{label}.integrity", "fail", "integrity must be an object")
        else:
            expected_sha = str(integrity.get("sha256") or "")
            if not SHA256_PATTERN.match(expected_sha):
                add_check(f"{label}.integrity.sha256", "fail", "sha256 must be 64 lowercase hex")
            else:
                actual_sha = _normalize_sha256(absolute_path)
                if actual_sha != expected_sha:
                    add_check(
                        f"{label}.integrity.sha256",
                        "fail",
                        f"hash mismatch expected={expected_sha} actual={actual_sha}",
                    )
                else:
                    add_check(f"{label}.integrity.sha256", "pass", "hash matched")

        frontmatter = _parse_frontmatter(absolute_path)
        if not isinstance(frontmatter, dict):
            add_check(f"{label}.frontmatter", "fail", "missing or invalid YAML frontmatter")
            continue

        frontmatter_name = str(frontmatter.get("name") or "").strip().strip('"').strip("'")
        if frontmatter_name != entry_id:
            add_check(
                f"{label}.frontmatter.name",
                "fail",
                f"name mismatch registry={entry_id!r} skill={frontmatter_name!r}",
            )
        else:
            add_check(f"{label}.frontmatter.name", "pass", frontmatter_name)

        frontmatter_description = str(frontmatter.get("description") or "").strip()
        if not frontmatter_description:
            add_check(f"{label}.frontmatter.description", "fail", "description must be non-empty")
        else:
            add_check(f"{label}.frontmatter.description", "pass", "description present")

    missing_registry_entries = sorted(discovered - registry_paths)
    for missing_path in missing_registry_entries:
        add_check(
            "registry_coverage",
            "fail",
            f"discovered skill missing from registry: {missing_path}",
        )

    extra_registry_entries = sorted(registry_paths - discovered)
    for extra_path in extra_registry_entries:
        add_check(
            "registry_coverage",
            "fail",
            f"registry path not discovered under skills root: {extra_path}",
        )

    failed = [item for item in checks if item["status"] == "fail"]
    warnings = [item for item in checks if item["status"] == "warn"]
    return {
        "generated_at": _iso_now(),
        "ok": len(failed) == 0,
        "failed_count": len(failed),
        "warning_count": len(warnings),
        "checks": checks,
        "summary": {
            "discovered_skill_files": len(discovered),
            "registry_entries": len(skills),
            "max_review_age_days": max_review_age_days,
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify skills registry contract.")
    parser.add_argument(
        "--registry",
        default="skills/registry.json",
        help="Skill registry JSON path.",
    )
    parser.add_argument(
        "--schema",
        default="skills/registry.schema.json",
        help="Registry schema JSON path.",
    )
    parser.add_argument(
        "--skills-root",
        default=".agent/skills",
        help="Root directory used for skill file discovery.",
    )
    parser.add_argument(
        "--today",
        default=None,
        help="Date override in YYYY-MM-DD for deterministic checks.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when checks fail.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    today = date.today()
    if args.today:
        parsed = _parse_date(args.today)
        if parsed is None:
            payload = {
                "generated_at": _iso_now(),
                "ok": False,
                "failed_count": 1,
                "warning_count": 0,
                "checks": [
                    {
                        "name": "today",
                        "status": "fail",
                        "detail": f"invalid --today value: {args.today!r}",
                    }
                ],
            }
            _emit(payload)
            return 1
        today = parsed

    repo_root = Path(".").resolve()
    registry_path = Path(args.registry)
    schema_path = Path(args.schema)
    skills_root = Path(args.skills_root).resolve()

    registry_payload = _read_json(registry_path)
    schema_payload = _read_json(schema_path)
    payload = evaluate_registry(
        registry_payload=registry_payload,
        schema_payload=schema_payload,
        repo_root=repo_root,
        skills_root=skills_root,
        today=today,
    )
    try:
        skills_root_display = _as_posix(skills_root.relative_to(repo_root))
    except ValueError:
        skills_root_display = _as_posix(skills_root)
    payload["inputs"] = {
        "registry": _as_posix(registry_path),
        "schema": _as_posix(schema_path),
        "skills_root": skills_root_display,
        "today": today.isoformat(),
    }
    _emit(payload)

    if args.strict and not payload["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
