from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import yaml


def _read_yaml(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"schedule profile spec not found: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    items: list[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            items.append(text)
    return items


def _as_bool(value: Any, *, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"true", "1", "yes", "on"}:
            return True
        if text in {"false", "0", "no", "off"}:
            return False
    return default


def _as_int(value: Any, *, default: int, minimum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, parsed)


def _as_float(value: Any, *, default: float, minimum: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, parsed)


def _as_optional_int(value: Any, *, minimum: int) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return max(minimum, parsed)


def _as_optional_float(value: Any, *, minimum: float) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return max(minimum, parsed)


def _as_int_map(value: Any, *, minimum: int) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, int] = {}
    for raw_key, raw_value in value.items():
        key = str(raw_key).strip().lower()
        if not key:
            continue
        result[key] = _as_int(raw_value, default=minimum, minimum=minimum)
    return result


@dataclass(frozen=True)
class ScheduleProfile:
    name: str
    description: str
    registry_entry_ids: list[str]
    registry_categories: list[str]
    include_stale: bool
    interval_seconds: float
    entries_per_cycle: int
    urls_per_cycle: int
    revisit_interval_cycles: int
    failure_backoff_cycles: int
    category_weights: dict[str, int]
    category_backoff_multipliers: dict[str, int]
    tension_max_friction_score: Optional[float]
    tension_max_lyapunov_proxy: Optional[float]
    tension_max_council_count: Optional[int]
    tension_max_llm_preflight_latency_ms: Optional[int]
    tension_max_llm_selection_latency_ms: Optional[int]
    tension_max_llm_probe_latency_ms: Optional[int]
    tension_max_llm_timeout_count: Optional[int]
    tension_max_consecutive_failure_count: Optional[int]
    tension_cooldown_cycles: int
    limit: int
    min_priority: float
    related_limit: int
    crystal_count: int

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "description": self.description,
            "registry": {
                "entry_ids": list(self.registry_entry_ids),
                "categories": list(self.registry_categories),
                "include_stale": bool(self.include_stale),
            },
            "schedule": {
                "interval_seconds": float(self.interval_seconds),
                "entries_per_cycle": int(self.entries_per_cycle),
                "urls_per_cycle": int(self.urls_per_cycle),
                "revisit_interval_cycles": int(self.revisit_interval_cycles),
                "failure_backoff_cycles": int(self.failure_backoff_cycles),
                "category_weights": {
                    key: int(value) for key, value in sorted(self.category_weights.items())
                },
                "category_backoff_multipliers": {
                    key: int(value)
                    for key, value in sorted(self.category_backoff_multipliers.items())
                },
                "tension_max_friction_score": (
                    None
                    if self.tension_max_friction_score is None
                    else float(self.tension_max_friction_score)
                ),
                "tension_max_lyapunov_proxy": (
                    None
                    if self.tension_max_lyapunov_proxy is None
                    else float(self.tension_max_lyapunov_proxy)
                ),
                "tension_max_council_count": (
                    None
                    if self.tension_max_council_count is None
                    else int(self.tension_max_council_count)
                ),
                "tension_max_llm_preflight_latency_ms": (
                    None
                    if self.tension_max_llm_preflight_latency_ms is None
                    else int(self.tension_max_llm_preflight_latency_ms)
                ),
                "tension_max_llm_selection_latency_ms": (
                    None
                    if self.tension_max_llm_selection_latency_ms is None
                    else int(self.tension_max_llm_selection_latency_ms)
                ),
                "tension_max_llm_probe_latency_ms": (
                    None
                    if self.tension_max_llm_probe_latency_ms is None
                    else int(self.tension_max_llm_probe_latency_ms)
                ),
                "tension_max_llm_timeout_count": (
                    None
                    if self.tension_max_llm_timeout_count is None
                    else int(self.tension_max_llm_timeout_count)
                ),
                "tension_max_consecutive_failure_count": (
                    None
                    if self.tension_max_consecutive_failure_count is None
                    else int(self.tension_max_consecutive_failure_count)
                ),
                "tension_cooldown_cycles": int(self.tension_cooldown_cycles),
            },
            "dream": {
                "limit": int(self.limit),
                "min_priority": float(self.min_priority),
                "related_limit": int(self.related_limit),
                "crystal_count": int(self.crystal_count),
            },
        }


def _build_profile(name: str, payload: dict[str, Any]) -> ScheduleProfile:
    registry = payload.get("registry", {})
    schedule = payload.get("schedule", {})
    dream = payload.get("dream", {})
    if not isinstance(registry, dict):
        registry = {}
    if not isinstance(schedule, dict):
        schedule = {}
    if not isinstance(dream, dict):
        dream = {}

    return ScheduleProfile(
        name=name,
        description=str(payload.get("description") or ""),
        registry_entry_ids=_as_str_list(registry.get("entry_ids")),
        registry_categories=_as_str_list(registry.get("categories")),
        include_stale=_as_bool(registry.get("include_stale"), default=False),
        interval_seconds=_as_float(schedule.get("interval_seconds"), default=10800.0, minimum=0.0),
        entries_per_cycle=_as_int(schedule.get("entries_per_cycle"), default=1, minimum=1),
        urls_per_cycle=_as_int(schedule.get("urls_per_cycle"), default=3, minimum=1),
        revisit_interval_cycles=_as_int(
            schedule.get("revisit_interval_cycles"),
            default=0,
            minimum=0,
        ),
        failure_backoff_cycles=_as_int(
            schedule.get("failure_backoff_cycles"),
            default=0,
            minimum=0,
        ),
        category_weights=_as_int_map(
            schedule.get("category_weights"),
            minimum=1,
        ),
        category_backoff_multipliers=_as_int_map(
            schedule.get("category_backoff_multipliers"),
            minimum=1,
        ),
        tension_max_friction_score=_as_optional_float(
            schedule.get("tension_max_friction_score"),
            minimum=0.0,
        ),
        tension_max_lyapunov_proxy=_as_optional_float(
            schedule.get("tension_max_lyapunov_proxy"),
            minimum=0.0,
        ),
        tension_max_council_count=_as_optional_int(
            schedule.get("tension_max_council_count"),
            minimum=0,
        ),
        tension_max_llm_preflight_latency_ms=_as_optional_int(
            schedule.get("tension_max_llm_preflight_latency_ms"),
            minimum=0,
        ),
        tension_max_llm_selection_latency_ms=_as_optional_int(
            schedule.get("tension_max_llm_selection_latency_ms"),
            minimum=0,
        ),
        tension_max_llm_probe_latency_ms=_as_optional_int(
            schedule.get("tension_max_llm_probe_latency_ms"),
            minimum=0,
        ),
        tension_max_llm_timeout_count=_as_optional_int(
            schedule.get("tension_max_llm_timeout_count"),
            minimum=0,
        ),
        tension_max_consecutive_failure_count=_as_optional_int(
            schedule.get("tension_max_consecutive_failure_count"),
            minimum=0,
        ),
        tension_cooldown_cycles=_as_int(
            schedule.get("tension_cooldown_cycles"),
            default=0,
            minimum=0,
        ),
        limit=_as_int(dream.get("limit"), default=3, minimum=1),
        min_priority=_as_float(dream.get("min_priority"), default=0.35, minimum=0.0),
        related_limit=_as_int(dream.get("related_limit"), default=5, minimum=1),
        crystal_count=_as_int(dream.get("crystal_count"), default=5, minimum=1),
    )


def load_schedule_profiles(path: Path | str) -> dict[str, ScheduleProfile]:
    payload = _read_yaml(Path(path))
    if not isinstance(payload, dict):
        raise ValueError("schedule profile spec must be a mapping")

    raw_profiles = payload.get("profiles")
    if not isinstance(raw_profiles, dict) or not raw_profiles:
        raise ValueError("schedule profile spec must define a non-empty profiles mapping")

    profiles: dict[str, ScheduleProfile] = {}
    for raw_name, raw_profile in raw_profiles.items():
        name = str(raw_name).strip()
        if not name:
            raise ValueError("schedule profile name must not be empty")
        if not isinstance(raw_profile, dict):
            raise ValueError(f"schedule profile {name!r} must be a mapping")
        profiles[name] = _build_profile(name, raw_profile)
    return profiles


def resolve_schedule_profile(path: Path | str, name: str) -> ScheduleProfile:
    profile_name = str(name).strip()
    if not profile_name:
        raise ValueError("schedule profile name must not be empty")
    profiles = load_schedule_profiles(path)
    if profile_name not in profiles:
        raise ValueError(f"unknown schedule profile: {profile_name}")
    return profiles[profile_name]


__all__ = [
    "ScheduleProfile",
    "load_schedule_profiles",
    "resolve_schedule_profile",
]
