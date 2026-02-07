from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from . import benevolence, council

SkillFn = Callable[[Mapping[str, Any]], dict[str, Any]]


@dataclass(frozen=True, slots=True)
class SkillSpec:
    name: str
    version: str
    description: str
    handler: SkillFn


SKILL_REGISTRY: dict[str, SkillSpec] = {
    benevolence.SKILL_NAME: SkillSpec(
        name=benevolence.SKILL_NAME,
        version=benevolence.SKILL_VERSION,
        description="Run CPT benevolence filter audit for a proposed action.",
        handler=benevolence.run,
    ),
    council.SKILL_NAME: SkillSpec(
        name=council.SKILL_NAME,
        version=council.SKILL_VERSION,
        description="Run ToneSoul multi-perspective council deliberation.",
        handler=council.run,
    ),
}


def list_skills() -> list[dict[str, str]]:
    return [
        {
            "name": spec.name,
            "version": spec.version,
            "description": spec.description,
        }
        for spec in SKILL_REGISTRY.values()
    ]


def invoke_skill(name: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    key = name.strip()
    spec = SKILL_REGISTRY.get(key)
    if spec is None:
        return {
            "ok": False,
            "error": f"Unknown skill: {name}",
            "available_skills": sorted(SKILL_REGISTRY.keys()),
        }
    return spec.handler(payload)
