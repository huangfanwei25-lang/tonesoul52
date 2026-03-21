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
RESERVED_NAMESPACE_TERMS = ("claude", "anthropic")
L1_INTENT_MAX_LEN = 160
L2_EXECUTION_PROFILES = {"interactive", "engineering", "any"}


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

    text = text.lstrip("\ufeff")
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


def _contains_prompt_markup(value: str) -> bool:
    return "<" in value or ">" in value


def _contains_reserved_namespace(value: str) -> str | None:
    lowered = value.lower()
    for term in RESERVED_NAMESPACE_TERMS:
        if term in lowered:
            return term
    return None


def _normalize_for_match(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _matched_triggers_in_description(triggers: list[str], description: str) -> list[str]:
    normalized_description = _normalize_for_match(description)
    matched: list[str] = []
    for trigger in triggers:
        normalized_trigger = _normalize_for_match(trigger)
        if normalized_trigger and normalized_trigger in normalized_description:
            matched.append(trigger)
    return matched


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
        reserved_id_term = _contains_reserved_namespace(entry_id)
        if reserved_id_term:
            add_check(
                f"{label}.id.namespace",
                "fail",
                f"id must not use reserved namespace term: {reserved_id_term!r}",
            )
        else:
            add_check(f"{label}.id.namespace", "pass", "no reserved namespace term")

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

        l1_routing = entry.get("l1_routing")
        l1_name = ""
        l1_intent = ""
        triggers: list[str] = []
        if not isinstance(l1_routing, dict):
            add_check(f"{label}.l1_routing", "fail", "l1_routing must be an object")
        else:
            add_check(f"{label}.l1_routing", "pass", "present")
            l1_name = str(l1_routing.get("name") or "").strip()
            if not l1_name:
                add_check(f"{label}.l1_routing.name", "fail", "name must be non-empty")
            else:
                add_check(f"{label}.l1_routing.name", "pass", l1_name)
                if _contains_prompt_markup(l1_name):
                    add_check(
                        f"{label}.l1_routing.name.prompt_safety",
                        "fail",
                        "l1_routing.name must not include < or >",
                    )
                else:
                    add_check(f"{label}.l1_routing.name.prompt_safety", "pass", "safe")

            l1_intent = str(l1_routing.get("intent") or "").strip()
            if not l1_intent:
                add_check(f"{label}.l1_routing.intent", "fail", "intent must be non-empty")
            elif len(l1_intent) > L1_INTENT_MAX_LEN:
                add_check(
                    f"{label}.l1_routing.intent",
                    "fail",
                    f"intent too long ({len(l1_intent)} > {L1_INTENT_MAX_LEN})",
                )
            else:
                add_check(f"{label}.l1_routing.intent", "pass", f"length={len(l1_intent)}")
                if _contains_prompt_markup(l1_intent):
                    add_check(
                        f"{label}.l1_routing.intent.prompt_safety",
                        "fail",
                        "l1_routing.intent must not include < or >",
                    )
                else:
                    add_check(f"{label}.l1_routing.intent.prompt_safety", "pass", "safe")

            triggers = _as_string_list(l1_routing.get("triggers"))
            if not triggers:
                add_check(
                    f"{label}.l1_routing.triggers",
                    "fail",
                    "triggers must contain at least one string",
                )
            else:
                add_check(f"{label}.l1_routing.triggers", "pass", f"{len(triggers)} trigger(s)")
                if len({item.casefold() for item in triggers}) != len(triggers):
                    add_check(
                        f"{label}.l1_routing.triggers.unique",
                        "fail",
                        "duplicate trigger values are not allowed",
                    )
                else:
                    add_check(
                        f"{label}.l1_routing.triggers.unique",
                        "pass",
                        "trigger values are unique",
                    )
                invalid_markup_triggers = [
                    item for item in triggers if _contains_prompt_markup(item)
                ]
                if invalid_markup_triggers:
                    add_check(
                        f"{label}.l1_routing.triggers.prompt_safety",
                        "fail",
                        f"triggers contain prompt-markup tokens: {invalid_markup_triggers}",
                    )
                else:
                    add_check(
                        f"{label}.l1_routing.triggers.prompt_safety",
                        "pass",
                        "no prompt-markup tokens",
                    )

                if l1_intent:
                    matched = _matched_triggers_in_description(triggers, l1_intent)
                    if not matched:
                        add_check(
                            f"{label}.l1_routing.trigger_coverage",
                            "fail",
                            "intent must contain at least one trigger term",
                        )
                    else:
                        add_check(
                            f"{label}.l1_routing.trigger_coverage",
                            "pass",
                            f"matched={matched[0]!r}",
                        )

        l2_signature = entry.get("l2_signature")
        execution_profile_values: list[str] = []
        l2_trust_tier = ""
        if not isinstance(l2_signature, dict):
            add_check(f"{label}.l2_signature", "fail", "l2_signature must be an object")
        else:
            add_check(f"{label}.l2_signature", "pass", "present")
            execution_profile_values = _as_string_list(l2_signature.get("execution_profile"))
            if not execution_profile_values:
                add_check(
                    f"{label}.l2_signature.execution_profile",
                    "fail",
                    "execution_profile list is required",
                )
            else:
                invalid_profiles = [
                    item
                    for item in execution_profile_values
                    if item.lower() not in L2_EXECUTION_PROFILES
                ]
                if invalid_profiles:
                    add_check(
                        f"{label}.l2_signature.execution_profile",
                        "fail",
                        f"invalid execution profiles: {invalid_profiles}",
                    )
                else:
                    add_check(
                        f"{label}.l2_signature.execution_profile",
                        "pass",
                        f"{len(execution_profile_values)} profile(s)",
                    )

            l2_trust_tier = str(l2_signature.get("trust_tier") or "").strip()
            if l2_trust_tier not in TRUST_TIERS:
                add_check(
                    f"{label}.l2_signature.trust_tier",
                    "fail",
                    f"invalid trust_tier: {l2_trust_tier!r}",
                )
            else:
                add_check(f"{label}.l2_signature.trust_tier", "pass", l2_trust_tier)

            json_schema = l2_signature.get("json_schema")
            if not isinstance(json_schema, dict):
                add_check(
                    f"{label}.l2_signature.json_schema",
                    "fail",
                    "json_schema must be an object",
                )
            elif str(json_schema.get("type") or "").strip() != "object":
                add_check(
                    f"{label}.l2_signature.json_schema",
                    "fail",
                    "json_schema.type must be 'object'",
                )
            else:
                add_check(
                    f"{label}.l2_signature.json_schema",
                    "pass",
                    "schema type object",
                )

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
        trust_tier = ""
        if not isinstance(trust, dict):
            add_check(f"{label}.trust", "fail", "trust must be an object")
        else:
            trust_tier = str(trust.get("tier") or "")
            if trust_tier not in TRUST_TIERS:
                add_check(f"{label}.trust.tier", "fail", f"invalid tier: {trust_tier!r}")
            else:
                add_check(f"{label}.trust.tier", "pass", trust_tier)

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
        if l2_trust_tier and trust_tier and l2_trust_tier != trust_tier:
            add_check(
                f"{label}.trust_alignment",
                "fail",
                f"l2_signature.trust_tier={l2_trust_tier!r} must match trust.tier={trust_tier!r}",
            )
        elif l2_trust_tier and trust_tier:
            add_check(f"{label}.trust_alignment", "pass", "l2/trust tiers aligned")

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
        if _contains_prompt_markup(frontmatter_name):
            add_check(
                f"{label}.frontmatter.name.prompt_safety",
                "fail",
                "frontmatter.name must not include < or >",
            )
        else:
            add_check(f"{label}.frontmatter.name.prompt_safety", "pass", "safe")
        reserved_name_term = _contains_reserved_namespace(frontmatter_name)
        if reserved_name_term:
            add_check(
                f"{label}.frontmatter.name.namespace",
                "fail",
                f"frontmatter.name must not use reserved namespace term: {reserved_name_term!r}",
            )
        else:
            add_check(f"{label}.frontmatter.name.namespace", "pass", "no reserved namespace term")

        frontmatter_description = str(frontmatter.get("description") or "").strip()
        if not frontmatter_description:
            add_check(f"{label}.frontmatter.description", "fail", "description must be non-empty")
        else:
            add_check(f"{label}.frontmatter.description", "pass", "description present")

        fm_l1 = frontmatter.get("l1_routing")
        if not isinstance(fm_l1, dict):
            add_check(
                f"{label}.frontmatter.l1_routing", "fail", "frontmatter l1_routing is required"
            )
        else:
            add_check(f"{label}.frontmatter.l1_routing", "pass", "present")
            fm_l1_name = str(fm_l1.get("name") or "").strip()
            if not fm_l1_name:
                add_check(f"{label}.frontmatter.l1_routing.name", "fail", "name must be non-empty")
            elif l1_name and fm_l1_name != l1_name:
                add_check(
                    f"{label}.frontmatter.l1_routing.name",
                    "fail",
                    f"name mismatch registry={l1_name!r} skill={fm_l1_name!r}",
                )
            else:
                add_check(f"{label}.frontmatter.l1_routing.name", "pass", fm_l1_name)
            if _contains_prompt_markup(fm_l1_name):
                add_check(
                    f"{label}.frontmatter.l1_routing.name.prompt_safety",
                    "fail",
                    "l1_routing.name must not include < or >",
                )
            else:
                add_check(
                    f"{label}.frontmatter.l1_routing.name.prompt_safety",
                    "pass",
                    "safe",
                )

            fm_triggers = _as_string_list(fm_l1.get("triggers"))
            if not fm_triggers:
                add_check(
                    f"{label}.frontmatter.l1_routing.triggers",
                    "fail",
                    "triggers must contain at least one string",
                )
            else:
                if triggers and {item.casefold() for item in fm_triggers} != {
                    item.casefold() for item in triggers
                }:
                    add_check(
                        f"{label}.frontmatter.l1_routing.triggers",
                        "fail",
                        "frontmatter triggers must match registry l1_routing.triggers",
                    )
                else:
                    add_check(
                        f"{label}.frontmatter.l1_routing.triggers",
                        "pass",
                        f"{len(fm_triggers)} trigger(s)",
                    )
                invalid_markup_fm_triggers = [
                    item for item in fm_triggers if _contains_prompt_markup(item)
                ]
                if invalid_markup_fm_triggers:
                    add_check(
                        f"{label}.frontmatter.l1_routing.triggers.prompt_safety",
                        "fail",
                        f"triggers contain prompt-markup tokens: {invalid_markup_fm_triggers}",
                    )
                else:
                    add_check(
                        f"{label}.frontmatter.l1_routing.triggers.prompt_safety",
                        "pass",
                        "no prompt-markup tokens",
                    )

            fm_intent = str(fm_l1.get("intent") or "").strip()
            if not fm_intent:
                add_check(
                    f"{label}.frontmatter.l1_routing.intent",
                    "fail",
                    "intent must be non-empty",
                )
            else:
                if l1_intent and fm_intent != l1_intent:
                    add_check(
                        f"{label}.frontmatter.l1_routing.intent",
                        "fail",
                        "frontmatter intent must match registry l1_routing.intent",
                    )
                elif len(fm_intent) > L1_INTENT_MAX_LEN:
                    add_check(
                        f"{label}.frontmatter.l1_routing.intent",
                        "fail",
                        f"intent too long ({len(fm_intent)} > {L1_INTENT_MAX_LEN})",
                    )
                else:
                    add_check(
                        f"{label}.frontmatter.l1_routing.intent",
                        "pass",
                        f"length={len(fm_intent)}",
                    )
                if _contains_prompt_markup(fm_intent):
                    add_check(
                        f"{label}.frontmatter.l1_routing.intent.prompt_safety",
                        "fail",
                        "intent must not include < or >",
                    )
                else:
                    add_check(
                        f"{label}.frontmatter.l1_routing.intent.prompt_safety",
                        "pass",
                        "safe",
                    )

        fm_l2 = frontmatter.get("l2_signature")
        if not isinstance(fm_l2, dict):
            add_check(
                f"{label}.frontmatter.l2_signature", "fail", "frontmatter l2_signature is required"
            )
        else:
            add_check(f"{label}.frontmatter.l2_signature", "pass", "present")
            fm_profiles = _as_string_list(fm_l2.get("execution_profile"))
            if not fm_profiles:
                add_check(
                    f"{label}.frontmatter.l2_signature.execution_profile",
                    "fail",
                    "execution_profile list is required",
                )
            elif execution_profile_values and {item.lower() for item in fm_profiles} != {
                item.lower() for item in execution_profile_values
            }:
                add_check(
                    f"{label}.frontmatter.l2_signature.execution_profile",
                    "fail",
                    "frontmatter execution_profile must match registry l2_signature.execution_profile",
                )
            else:
                add_check(
                    f"{label}.frontmatter.l2_signature.execution_profile",
                    "pass",
                    f"{len(fm_profiles)} profile(s)",
                )

            fm_trust_tier = str(fm_l2.get("trust_tier") or "").strip()
            if not fm_trust_tier:
                add_check(
                    f"{label}.frontmatter.l2_signature.trust_tier",
                    "fail",
                    "trust_tier must be non-empty",
                )
            elif l2_trust_tier and fm_trust_tier != l2_trust_tier:
                add_check(
                    f"{label}.frontmatter.l2_signature.trust_tier",
                    "fail",
                    "frontmatter trust_tier must match registry l2_signature.trust_tier",
                )
            else:
                add_check(
                    f"{label}.frontmatter.l2_signature.trust_tier",
                    "pass",
                    fm_trust_tier,
                )

            fm_json_schema = fm_l2.get("json_schema")
            if not isinstance(fm_json_schema, dict):
                add_check(
                    f"{label}.frontmatter.l2_signature.json_schema",
                    "fail",
                    "json_schema must be an object",
                )
            elif str(fm_json_schema.get("type") or "").strip() != "object":
                add_check(
                    f"{label}.frontmatter.l2_signature.json_schema",
                    "fail",
                    "json_schema.type must be 'object'",
                )
            else:
                add_check(
                    f"{label}.frontmatter.l2_signature.json_schema",
                    "pass",
                    "schema type object",
                )

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
