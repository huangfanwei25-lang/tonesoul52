from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Sequence

_DEFAULT_REGISTRY_PATH = "skills/registry.json"
_DEFAULT_MAX_MATCHES = 2
_DEFAULT_L3_CHAR_LIMIT = 800
_PROFILE_ANY = "any"


def _as_string_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    result: List[str] = []
    for item in value:
        if isinstance(item, str):
            token = item.strip()
            if token:
                result.append(token)
    return result


def _normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _split_frontmatter(text: str) -> tuple[Dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text.strip()
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return {}, text.strip()
    try:
        import yaml

        payload = yaml.safe_load(parts[1])
    except Exception:
        payload = {}
    frontmatter = payload if isinstance(payload, dict) else {}
    return frontmatter, parts[2].strip()


class SkillContractParser:
    """Three-layer skill contract parser (L1 route, L2 signature, L3 payload)."""

    def __init__(
        self,
        *,
        repo_root: str | Path | None = None,
        registry_path: str | Path = _DEFAULT_REGISTRY_PATH,
    ) -> None:
        self._repo_root = Path(repo_root or ".").resolve()
        self._registry_path = self._resolve_path(registry_path)
        self._registry_payload: Dict[str, Any] | None = None
        self._index: Dict[str, Dict[str, Any]] = {}

    def _resolve_path(self, path: str | Path) -> Path:
        candidate = Path(path)
        if candidate.is_absolute():
            return candidate
        return (self._repo_root / candidate).resolve()

    def _load_registry(self) -> None:
        if self._registry_payload is not None:
            return
        payload = json.loads(self._registry_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("skill registry payload must be an object")
        skills = payload.get("skills")
        if not isinstance(skills, list):
            raise ValueError("skill registry skills must be a list")
        index: Dict[str, Dict[str, Any]] = {}
        for entry in skills:
            if not isinstance(entry, dict):
                continue
            skill_id = str(entry.get("id") or "").strip()
            if not skill_id:
                continue
            index[skill_id] = entry
        self._registry_payload = payload
        self._index = index

    def _require_entry(self, skill_id: str) -> Dict[str, Any]:
        self._load_registry()
        entry = self._index.get(skill_id)
        if not entry:
            raise KeyError(f"skill not found: {skill_id}")
        return entry

    def _skill_file_path(self, skill_id: str) -> Path:
        entry = self._require_entry(skill_id)
        relative = str(entry.get("path") or "").strip()
        if not relative:
            raise ValueError(f"skill path missing: {skill_id}")
        return self._resolve_path(relative)

    def get_all_l1_routes(self) -> List[Dict[str, Any]]:
        self._load_registry()
        routes: List[Dict[str, Any]] = []
        for skill_id in sorted(self._index):
            entry = self._index[skill_id]
            layer = entry.get("l1_routing") if isinstance(entry.get("l1_routing"), dict) else {}
            routes.append(
                {
                    "id": skill_id,
                    "name": str(layer.get("name") or "").strip(),
                    "triggers": _as_string_list(layer.get("triggers")),
                    "intent": str(layer.get("intent") or "").strip(),
                }
            )
        return routes

    def get_l2_signature(self, skill_id: str) -> Dict[str, Any]:
        entry = self._require_entry(skill_id)
        layer = entry.get("l2_signature")
        if not isinstance(layer, dict):
            raise ValueError(f"l2_signature missing for skill: {skill_id}")
        return copy.deepcopy(layer)

    def get_l3_payload(self, skill_id: str) -> str:
        skill_path = self._skill_file_path(skill_id)
        text = skill_path.read_text(encoding="utf-8", errors="replace")
        _, body = _split_frontmatter(text)
        return body

    def resolve_for_request(
        self,
        *,
        query: str,
        execution_profile: str,
        allowed_trust_tiers: Sequence[str] = ("trusted", "reviewed"),
        max_matches: int = _DEFAULT_MAX_MATCHES,
        l3_char_limit: int = _DEFAULT_L3_CHAR_LIMIT,
    ) -> List[Dict[str, Any]]:
        normalized_query = _normalize_text(query)
        profile = str(execution_profile or "").strip().lower()
        allowed = {str(item).strip().lower() for item in allowed_trust_tiers if str(item).strip()}

        matches: List[Dict[str, Any]] = []
        for route in self.get_all_l1_routes():
            triggers = _as_string_list(route.get("triggers"))
            matched_trigger = ""
            for trigger in triggers:
                token = _normalize_text(trigger)
                if token and token in normalized_query:
                    matched_trigger = trigger
                    break
            if not matched_trigger:
                continue

            skill_id = str(route.get("id") or "").strip()
            if not skill_id:
                continue
            signature = self.get_l2_signature(skill_id)
            trust_tier = str(signature.get("trust_tier") or "").strip().lower()
            profiles = [
                item.lower() for item in _as_string_list(signature.get("execution_profile"))
            ]
            profile_allowed = (profile in profiles) or (_PROFILE_ANY in profiles)
            if allowed and trust_tier not in allowed:
                continue
            if not profile_allowed:
                continue

            payload = self.get_l3_payload(skill_id)
            payload_excerpt = payload[: max(1, int(l3_char_limit))].strip()
            if len(payload) > len(payload_excerpt):
                payload_excerpt = f"{payload_excerpt}\n...[truncated]"

            matches.append(
                {
                    "skill_id": skill_id,
                    "matched_trigger": matched_trigger,
                    "l1_routing": route,
                    "l2_signature": signature,
                    "l3_excerpt": payload_excerpt,
                }
            )

        matches.sort(key=lambda item: len(str(item.get("matched_trigger") or "")), reverse=True)
        return matches[: max(1, int(max_matches))]
