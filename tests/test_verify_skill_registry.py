from __future__ import annotations

from datetime import date
from pathlib import Path

import scripts.verify_skill_registry as verify_skill_registry


def _write_skill(
    path: Path,
    *,
    name: str,
    description: str = "Use this trigger phrase to route skill execution safely and predictably.",
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n" f"name: {name}\n" f"description: {description}\n" "---\n" f"# {name}\n",
        encoding="utf-8",
    )


def _base_schema_payload() -> dict:
    return {
        "type": "object",
        "$defs": {"skill": {"type": "object"}},
    }


def _build_registry_entry(skill_path: str, skill_id: str, skill_file: Path) -> dict:
    return {
        "id": skill_id,
        "name": skill_id,
        "path": skill_path,
        "version": "1.0.0",
        "license": "Internal-Project",
        "compatibility": {
            "runtime": ["codex"],
            "os": ["windows"],
        },
        "triggers": ["trigger"],
        "trust": {
            "tier": "reviewed",
            "review_owner": "codex",
            "reviewed_at": "2026-02-24",
        },
        "integrity": {
            "sha256": verify_skill_registry._normalize_sha256(skill_file),
        },
    }


def test_evaluate_registry_passes_with_valid_metadata(tmp_path: Path) -> None:
    skill_file = tmp_path / ".agent" / "skills" / "local_llm" / "SKILL.md"
    _write_skill(skill_file, name="local_llm")

    registry_payload = {
        "registry_version": "1.0.0",
        "max_review_age_days": 180,
        "skills": [
            _build_registry_entry(
                ".agent/skills/local_llm/SKILL.md",
                "local_llm",
                skill_file,
            )
        ],
    }

    payload = verify_skill_registry.evaluate_registry(
        registry_payload=registry_payload,
        schema_payload=_base_schema_payload(),
        repo_root=tmp_path,
        skills_root=tmp_path / ".agent" / "skills",
        today=date(2026, 2, 24),
    )
    assert payload["ok"] is True
    assert payload["failed_count"] == 0


def test_evaluate_registry_fails_when_discovered_skill_missing_from_registry(
    tmp_path: Path,
) -> None:
    _write_skill(tmp_path / ".agent" / "skills" / "local_llm" / "SKILL.md", name="local_llm")
    _write_skill(tmp_path / ".agent" / "skills" / "qa_auditor" / "SKILL.md", name="qa_auditor")

    local_skill_file = tmp_path / ".agent" / "skills" / "local_llm" / "SKILL.md"
    registry_payload = {
        "registry_version": "1.0.0",
        "max_review_age_days": 180,
        "skills": [
            _build_registry_entry(
                ".agent/skills/local_llm/SKILL.md",
                "local_llm",
                local_skill_file,
            )
        ],
    }

    payload = verify_skill_registry.evaluate_registry(
        registry_payload=registry_payload,
        schema_payload=_base_schema_payload(),
        repo_root=tmp_path,
        skills_root=tmp_path / ".agent" / "skills",
        today=date(2026, 2, 24),
    )
    assert payload["ok"] is False
    assert any(
        "discovered skill missing from registry" in check["detail"] for check in payload["checks"]
    )


def test_evaluate_registry_fails_when_hash_mismatch(tmp_path: Path) -> None:
    skill_file = tmp_path / ".agent" / "skills" / "local_llm" / "SKILL.md"
    _write_skill(skill_file, name="local_llm")

    entry = _build_registry_entry(".agent/skills/local_llm/SKILL.md", "local_llm", skill_file)
    entry["integrity"]["sha256"] = "0" * 64
    registry_payload = {
        "registry_version": "1.0.0",
        "max_review_age_days": 180,
        "skills": [entry],
    }

    payload = verify_skill_registry.evaluate_registry(
        registry_payload=registry_payload,
        schema_payload=_base_schema_payload(),
        repo_root=tmp_path,
        skills_root=tmp_path / ".agent" / "skills",
        today=date(2026, 2, 24),
    )
    assert payload["ok"] is False
    assert any("hash mismatch" in check["detail"] for check in payload["checks"])


def test_evaluate_registry_fails_when_frontmatter_name_mismatch(tmp_path: Path) -> None:
    skill_file = tmp_path / ".agent" / "skills" / "local_llm" / "SKILL.md"
    _write_skill(skill_file, name="unexpected_name")

    registry_payload = {
        "registry_version": "1.0.0",
        "max_review_age_days": 180,
        "skills": [
            _build_registry_entry(
                ".agent/skills/local_llm/SKILL.md",
                "local_llm",
                skill_file,
            )
        ],
    }

    payload = verify_skill_registry.evaluate_registry(
        registry_payload=registry_payload,
        schema_payload=_base_schema_payload(),
        repo_root=tmp_path,
        skills_root=tmp_path / ".agent" / "skills",
        today=date(2026, 2, 24),
    )
    assert payload["ok"] is False
    assert any("name mismatch" in check["detail"] for check in payload["checks"])


def test_evaluate_registry_fails_on_stale_review_date(tmp_path: Path) -> None:
    skill_file = tmp_path / ".agent" / "skills" / "local_llm" / "SKILL.md"
    _write_skill(skill_file, name="local_llm")

    entry = _build_registry_entry(".agent/skills/local_llm/SKILL.md", "local_llm", skill_file)
    entry["trust"]["reviewed_at"] = "2025-01-01"
    registry_payload = {
        "registry_version": "1.0.0",
        "max_review_age_days": 90,
        "skills": [entry],
    }

    payload = verify_skill_registry.evaluate_registry(
        registry_payload=registry_payload,
        schema_payload=_base_schema_payload(),
        repo_root=tmp_path,
        skills_root=tmp_path / ".agent" / "skills",
        today=date(2026, 2, 24),
    )
    assert payload["ok"] is False
    assert any("stale review" in check["detail"] for check in payload["checks"])


def test_evaluate_registry_fails_when_description_has_no_trigger_match(tmp_path: Path) -> None:
    skill_file = tmp_path / ".agent" / "skills" / "local_llm" / "SKILL.md"
    _write_skill(
        skill_file,
        name="local_llm",
        description="Long enough description but intentionally no matching keyword present.",
    )

    registry_payload = {
        "registry_version": "1.0.0",
        "max_review_age_days": 180,
        "skills": [
            _build_registry_entry(
                ".agent/skills/local_llm/SKILL.md",
                "local_llm",
                skill_file,
            )
        ],
    }

    payload = verify_skill_registry.evaluate_registry(
        registry_payload=registry_payload,
        schema_payload=_base_schema_payload(),
        repo_root=tmp_path,
        skills_root=tmp_path / ".agent" / "skills",
        today=date(2026, 2, 24),
    )
    assert payload["ok"] is False
    assert any(
        check["name"].endswith("routing.trigger_coverage") and check["status"] == "fail"
        for check in payload["checks"]
    )


def test_evaluate_registry_fails_when_frontmatter_description_has_prompt_markup(
    tmp_path: Path,
) -> None:
    skill_file = tmp_path / ".agent" / "skills" / "local_llm" / "SKILL.md"
    _write_skill(
        skill_file,
        name="local_llm",
        description="Use trigger and include <system> to attempt prompt injection payload.",
    )

    registry_payload = {
        "registry_version": "1.0.0",
        "max_review_age_days": 180,
        "skills": [
            _build_registry_entry(
                ".agent/skills/local_llm/SKILL.md",
                "local_llm",
                skill_file,
            )
        ],
    }

    payload = verify_skill_registry.evaluate_registry(
        registry_payload=registry_payload,
        schema_payload=_base_schema_payload(),
        repo_root=tmp_path,
        skills_root=tmp_path / ".agent" / "skills",
        today=date(2026, 2, 24),
    )
    assert payload["ok"] is False
    assert any(
        check["name"].endswith("frontmatter.description.prompt_safety")
        and check["status"] == "fail"
        for check in payload["checks"]
    )


def test_evaluate_registry_fails_when_skill_id_uses_reserved_namespace(tmp_path: Path) -> None:
    skill_file = tmp_path / ".agent" / "skills" / "claude_probe" / "SKILL.md"
    _write_skill(
        skill_file,
        name="claude_probe",
        description="Use trigger terms to route safely while testing reserved namespaces.",
    )
    registry_payload = {
        "registry_version": "1.0.0",
        "max_review_age_days": 180,
        "skills": [
            _build_registry_entry(
                ".agent/skills/claude_probe/SKILL.md",
                "claude_probe",
                skill_file,
            )
        ],
    }

    payload = verify_skill_registry.evaluate_registry(
        registry_payload=registry_payload,
        schema_payload=_base_schema_payload(),
        repo_root=tmp_path,
        skills_root=tmp_path / ".agent" / "skills",
        today=date(2026, 2, 24),
    )
    assert payload["ok"] is False
    assert any(
        check["name"].endswith("id.namespace") and check["status"] == "fail"
        for check in payload["checks"]
    )
