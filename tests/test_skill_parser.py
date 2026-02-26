from __future__ import annotations

import json
from pathlib import Path

from tonesoul.council.skill_parser import SkillContractParser


def _write_skill(path: Path, *, skill_id: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        (
            "---\n"
            f'name: "{skill_id}"\n'
            'description: "skill description"\n'
            "l1_routing:\n"
            f'  name: "{skill_id}"\n'
            "  triggers:\n"
            '    - "trigger"\n'
            '  intent: "Use trigger for routing."\n'
            "l2_signature:\n"
            "  execution_profile:\n"
            '    - "engineering"\n'
            '  trust_tier: "reviewed"\n'
            "  json_schema:\n"
            '    type: "object"\n'
            "---\n\n"
            f"{body}\n"
        ),
        encoding="utf-8",
    )


def _write_registry(tmp_path: Path, *, skill_path: str, sha256: str) -> Path:
    registry_dir = tmp_path / "skills"
    registry_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "$schema": "./registry.schema.json",
        "registry_version": "1.0.0",
        "max_review_age_days": 180,
        "skills": [
            {
                "id": "local_llm",
                "path": skill_path,
                "version": "1.0.0",
                "license": "Internal-Project",
                "compatibility": {"runtime": ["codex"], "os": ["windows"]},
                "l1_routing": {
                    "name": "Local LLM",
                    "triggers": ["local llm", "ollama"],
                    "intent": "Delegate local llm tasks through ollama safely.",
                },
                "l2_signature": {
                    "execution_profile": ["engineering"],
                    "trust_tier": "reviewed",
                    "json_schema": {"type": "object"},
                },
                "trust": {
                    "tier": "reviewed",
                    "review_owner": "codex",
                    "reviewed_at": "2026-02-24",
                },
                "integrity": {"sha256": sha256},
            }
        ],
    }
    registry_path = registry_dir / "registry.json"
    registry_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return registry_path


def test_skill_parser_returns_l1_l2_l3_layers(tmp_path: Path) -> None:
    skill_path = tmp_path / ".agent" / "skills" / "local_llm" / "SKILL.md"
    _write_skill(skill_path, skill_id="local_llm", body="## Runtime Body\nUse ollama workflow.")
    from scripts.verify_skill_registry import _normalize_sha256

    sha256 = _normalize_sha256(skill_path)
    registry_path = _write_registry(
        tmp_path,
        skill_path=".agent/skills/local_llm/SKILL.md",
        sha256=sha256,
    )
    parser = SkillContractParser(repo_root=tmp_path, registry_path=registry_path)

    routes = parser.get_all_l1_routes()
    assert len(routes) == 1
    assert routes[0]["id"] == "local_llm"
    assert "ollama" in routes[0]["triggers"]

    signature = parser.get_l2_signature("local_llm")
    assert signature["trust_tier"] == "reviewed"
    assert "engineering" in signature["execution_profile"]

    payload = parser.get_l3_payload("local_llm")
    assert "Runtime Body" in payload


def test_skill_parser_resolve_for_request_applies_l1_to_l3_flow(tmp_path: Path) -> None:
    skill_path = tmp_path / ".agent" / "skills" / "local_llm" / "SKILL.md"
    _write_skill(skill_path, skill_id="local_llm", body="Use this payload for engineering mode.")
    from scripts.verify_skill_registry import _normalize_sha256

    registry_path = _write_registry(
        tmp_path,
        skill_path=".agent/skills/local_llm/SKILL.md",
        sha256=_normalize_sha256(skill_path),
    )
    parser = SkillContractParser(repo_root=tmp_path, registry_path=registry_path)

    matches = parser.resolve_for_request(
        query="please run local llm with ollama for this task",
        execution_profile="engineering",
    )
    assert len(matches) == 1
    assert matches[0]["skill_id"] == "local_llm"
    assert matches[0]["matched_trigger"] in {"local llm", "ollama"}
    assert "payload" in matches[0]["l3_excerpt"].lower()

    blocked = parser.resolve_for_request(
        query="please run local llm with ollama for this task",
        execution_profile="interactive",
    )
    assert blocked == []
