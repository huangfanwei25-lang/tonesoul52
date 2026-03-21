from __future__ import annotations

from pathlib import Path

import pytest

from tonesoul.schedule_profile import load_schedule_profiles, resolve_schedule_profile


def test_load_schedule_profiles_reads_named_profiles() -> None:
    profiles = load_schedule_profiles(Path("spec/registry_schedule_profiles.yaml"))

    assert "baseline" in profiles
    assert "security_watch" in profiles
    assert "runtime_probe_watch" in profiles
    assert profiles["security_watch"].registry_categories == [
        "vulnerability-intel",
        "supply-chain-risk",
        "artifact-signing",
        "supply-chain-hardening",
    ]
    assert profiles["security_watch"].category_weights == {
        "vulnerability-intel": 3,
        "supply-chain-risk": 2,
        "artifact-signing": 1,
        "supply-chain-hardening": 1,
    }
    assert profiles["security_watch"].tension_max_friction_score == 0.7
    assert profiles["security_watch"].tension_max_lyapunov_proxy == 0.2
    assert profiles["security_watch"].tension_max_council_count == 1
    assert profiles["security_watch"].tension_max_llm_preflight_latency_ms == 1800
    assert profiles["security_watch"].tension_max_llm_selection_latency_ms == 700
    assert profiles["security_watch"].tension_max_llm_probe_latency_ms == 1200
    assert profiles["security_watch"].tension_max_llm_timeout_count == 0
    assert profiles["security_watch"].tension_max_consecutive_failure_count is None
    assert profiles["security_watch"].tension_cooldown_cycles == 2


def test_runtime_probe_watch_relaxes_governance_and_keeps_runtime_thresholds() -> None:
    profile = resolve_schedule_profile(
        Path("spec/registry_schedule_profiles.yaml"),
        "runtime_probe_watch",
    )

    assert profile.registry_categories == [
        "vulnerability-intel",
        "supply-chain-risk",
    ]
    assert profile.interval_seconds == 21600.0
    assert profile.entries_per_cycle == 1
    assert profile.urls_per_cycle == 1
    assert profile.revisit_interval_cycles == 0
    assert profile.failure_backoff_cycles == 1
    assert profile.category_weights == {
        "vulnerability-intel": 1,
        "supply-chain-risk": 1,
    }
    assert profile.tension_max_friction_score == 1.0
    assert profile.tension_max_lyapunov_proxy == 1.0
    assert profile.tension_max_council_count == 99
    assert profile.tension_max_llm_preflight_latency_ms == 1800
    assert profile.tension_max_llm_selection_latency_ms == 700
    assert profile.tension_max_llm_probe_latency_ms == 1200
    assert profile.tension_max_llm_timeout_count == 0
    assert profile.tension_max_consecutive_failure_count is None
    assert profile.tension_cooldown_cycles == 2
    assert profile.min_priority == 0.3


def test_resolve_schedule_profile_returns_expected_defaults() -> None:
    profile = resolve_schedule_profile(
        Path("spec/registry_schedule_profiles.yaml"),
        "research_slow_burn",
    )

    assert profile.interval_seconds == 43200.0
    assert profile.entries_per_cycle == 1
    assert profile.urls_per_cycle == 2
    assert profile.revisit_interval_cycles == 4
    assert profile.failure_backoff_cycles == 1
    assert profile.category_weights == {
        "research-archive": 3,
        "open-datasets": 2,
        "scholarly-graph": 1,
        "research-preprint": 1,
    }
    assert profile.category_backoff_multipliers == {
        "research-archive": 1,
        "open-datasets": 1,
        "scholarly-graph": 1,
        "research-preprint": 2,
    }
    assert profile.tension_max_friction_score == 0.8
    assert profile.tension_max_lyapunov_proxy == 0.25
    assert profile.tension_max_council_count == 2
    assert profile.tension_max_llm_preflight_latency_ms == 2500
    assert profile.tension_max_llm_selection_latency_ms == 1000
    assert profile.tension_max_llm_probe_latency_ms == 1800
    assert profile.tension_max_llm_timeout_count == 0
    assert profile.tension_max_consecutive_failure_count is None
    assert profile.tension_cooldown_cycles == 1
    assert profile.min_priority == 0.25


def test_resolve_schedule_profile_rejects_unknown_name() -> None:
    with pytest.raises(ValueError, match="unknown schedule profile"):
        resolve_schedule_profile(Path("spec/registry_schedule_profiles.yaml"), "missing_profile")
