from __future__ import annotations

from datetime import date
from pathlib import Path

import scripts.verify_skill_registry as verify_skill_registry


def _write_skill(
    path: Path,
    *,
    name: str,
    description: str = "Use this trigger phrase to route skill execution safely and predictably.",
    l1_name: str | None = None,
    triggers: list[str] | None = None,
    intent: str = "Use trigger phrase to route execution safely and predictably.",
    execution_profiles: list[str] | None = None,
    trust_tier: str = "reviewed",
) -> None:
    l1_name = l1_name or name
    triggers = triggers or ["trigger"]
    execution_profiles = execution_profiles or ["engineering"]
    trigger_lines = "\n".join(f'    - "{item}"' for item in triggers)
    profile_lines = "\n".join(f'    - "{item}"' for item in execution_profiles)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        (
            "---\n"
            f'name: "{name}"\n'
            f'description: "{description}"\n'
            "l1_routing:\n"
            f'  name: "{l1_name}"\n'
            "  triggers:\n"
            f"{trigger_lines}\n"
            f'  intent: "{intent}"\n'
            "l2_signature:\n"
            "  execution_profile:\n"
            f"{profile_lines}\n"
            f'  trust_tier: "{trust_tier}"\n'
            "  json_schema:\n"
            '    type: "object"\n'
            "    properties:\n"
            "      prompt:\n"
            '        type: "string"\n'
            "    required:\n"
            '      - "prompt"\n'
            "---\n"
            f"# {name}\n"
        ),
        encoding="utf-8",
    )


def _base_schema_payload() -> dict:
    return {
        "type": "object",
        "$defs": {"skill": {"type": "object"}},
    }


def _build_registry_entry(
    skill_path: str,
    skill_id: str,
    skill_file: Path,
    *,
    l1_name: str | None = None,
    triggers: list[str] | None = None,
    intent: str = "Use trigger phrase to route execution safely and predictably.",
    execution_profiles: list[str] | None = None,
    trust_tier: str = "reviewed",
) -> dict:
    l1_name = l1_name or skill_id
    triggers = triggers or ["trigger"]
    execution_profiles = execution_profiles or ["engineering"]
    return {
        "id": skill_id,
        "path": skill_path,
        "version": "1.0.0",
        "license": "Internal-Project",
        "compatibility": {
            "runtime": ["codex"],
            "os": ["windows"],
        },
        "l1_routing": {
            "name": l1_name,
            "triggers": triggers,
            "intent": intent,
        },
        "l2_signature": {
            "execution_profile": execution_profiles,
            "trust_tier": trust_tier,
            "json_schema": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                },
                "required": ["prompt"],
            },
        },
        "trust": {
            "tier": trust_tier,
            "review_owner": "codex",
            "reviewed_at": "2026-02-24",
        },
        "integrity": {
            "sha256": verify_skill_registry._normalize_sha256(skill_file),
        },
    }


def test_evaluate_registry_passes_with_valid_metadata(tmp_path: Path) -> None:
    skill_file = tmp_path / ".agent" / "skills" / "local_llm" / "SKILL.md"
    _write_skill(skill_file, name="local_llm", l1_name="local_llm")

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


def test_parse_frontmatter_accepts_utf8_bom(tmp_path: Path) -> None:
    skill_file = tmp_path / ".agent" / "skills" / "tonesoul_governance" / "SKILL.md"
    skill_file.parent.mkdir(parents=True, exist_ok=True)
    skill_file.write_text(
        "\ufeff---\n"
        'name: "tonesoul_governance"\n'
        'description: "Governance skill."\n'
        "l1_routing:\n"
        '  name: "ToneSoul Governance"\n'
        "  triggers:\n"
        '    - "governance"\n'
        '  intent: "Apply governance safely."\n'
        "l2_signature:\n"
        "  execution_profile:\n"
        '    - "engineering"\n'
        '  trust_tier: "reviewed"\n'
        "  json_schema:\n"
        '    type: "object"\n'
        "---\n"
        "# tonesoul_governance\n",
        encoding="utf-8",
    )

    frontmatter = verify_skill_registry._parse_frontmatter(skill_file)

    assert isinstance(frontmatter, dict)
    assert frontmatter["name"] == "tonesoul_governance"


def test_evaluate_registry_fails_when_discovered_skill_missing_from_registry(
    tmp_path: Path,
) -> None:
    _write_skill(
        tmp_path / ".agent" / "skills" / "local_llm" / "SKILL.md",
        name="local_llm",
        l1_name="local_llm",
    )
    _write_skill(
        tmp_path / ".agent" / "skills" / "qa_auditor" / "SKILL.md",
        name="qa_auditor",
        l1_name="qa_auditor",
    )

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
    _write_skill(skill_file, name="local_llm", l1_name="local_llm")

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
    _write_skill(skill_file, name="unexpected_name", l1_name="local_llm")

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
    _write_skill(skill_file, name="local_llm", l1_name="local_llm")

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
        l1_name="local_llm",
        intent="Long enough intent but intentionally no matching keyword present.",
    )

    entry = _build_registry_entry(
        ".agent/skills/local_llm/SKILL.md",
        "local_llm",
        skill_file,
    )
    entry["l1_routing"][
        "intent"
    ] = "Long enough intent but intentionally no matching keyword present."
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
    assert any(
        check["name"].endswith("l1_routing.trigger_coverage") and check["status"] == "fail"
        for check in payload["checks"]
    )


def test_evaluate_registry_fails_when_l1_intent_has_prompt_markup(
    tmp_path: Path,
) -> None:
    skill_file = tmp_path / ".agent" / "skills" / "local_llm" / "SKILL.md"
    _write_skill(
        skill_file,
        name="local_llm",
        description="Use trigger and include <system> to attempt prompt injection payload.",
        l1_name="local_llm",
        intent="Use trigger and include <system> to attempt prompt injection payload.",
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
        check["name"].endswith("l1_routing.intent.prompt_safety") and check["status"] == "fail"
        for check in payload["checks"]
    )


def test_evaluate_registry_fails_when_skill_id_uses_reserved_namespace(tmp_path: Path) -> None:
    skill_file = tmp_path / ".agent" / "skills" / "claude_probe" / "SKILL.md"
    _write_skill(
        skill_file,
        name="claude_probe",
        description="Use trigger terms to route safely while testing reserved namespaces.",
        l1_name="claude_probe",
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


def test_evaluate_registry_fails_when_l2_signature_profile_mismatch(tmp_path: Path) -> None:
    skill_file = tmp_path / ".agent" / "skills" / "local_llm" / "SKILL.md"
    _write_skill(
        skill_file,
        name="local_llm",
        l1_name="local_llm",
        execution_profiles=["engineering"],
    )
    entry = _build_registry_entry(
        ".agent/skills/local_llm/SKILL.md",
        "local_llm",
        skill_file,
        execution_profiles=["interactive"],
    )
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
    assert any(
        check["name"].endswith("frontmatter.l2_signature.execution_profile")
        and check["status"] == "fail"
        for check in payload["checks"]
    )
