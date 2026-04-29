from __future__ import annotations

from pathlib import Path

import pytest

from tonesoul.schedule_profile import (
    _as_bool,
    _as_float,
    _as_int,
    _as_int_map,
    _as_optional_float,
    _as_optional_int,
    _as_str_list,
    load_schedule_profiles,
    resolve_schedule_profile,
)

# ── _as_str_list ──────────────────────────────────────────────────────────────


class TestAsStrList:
    def test_list_of_strings(self):
        assert _as_str_list(["a", "b"]) == ["a", "b"]

    def test_filters_empty(self):
        assert _as_str_list(["", "  ", "x"]) == ["x"]

    def test_non_list_returns_empty(self):
        assert _as_str_list("not-a-list") == []
        assert _as_str_list(None) == []

    def test_strips_items(self):
        assert _as_str_list(["  x  "]) == ["x"]


# ── _as_bool ──────────────────────────────────────────────────────────────────


class TestAsBool:
    def test_bool_true(self):
        assert _as_bool(True, default=False) is True

    def test_bool_false(self):
        assert _as_bool(False, default=True) is False

    def test_none_uses_default(self):
        assert _as_bool(None, default=True) is True

    def test_string_true_values(self):
        for v in ["true", "1", "yes", "on"]:
            assert _as_bool(v, default=False) is True

    def test_string_false_values(self):
        for v in ["false", "0", "no", "off"]:
            assert _as_bool(v, default=True) is False

    def test_unknown_string_uses_default(self):
        assert _as_bool("maybe", default=True) is True


# ── _as_int ───────────────────────────────────────────────────────────────────


class TestAsInt:
    def test_int_value(self):
        assert _as_int(5, default=1, minimum=0) == 5

    def test_minimum_enforced(self):
        assert _as_int(-10, default=1, minimum=0) == 0

    def test_invalid_uses_default(self):
        assert _as_int("bad", default=3, minimum=0) == 3

    def test_none_uses_default(self):
        assert _as_int(None, default=2, minimum=0) == 2


# ── _as_float ─────────────────────────────────────────────────────────────────


class TestAsFloat:
    def test_float_value(self):
        assert _as_float(0.5, default=1.0, minimum=0.0) == pytest.approx(0.5)

    def test_minimum_enforced(self):
        assert _as_float(-1.0, default=1.0, minimum=0.0) == pytest.approx(0.0)

    def test_invalid_uses_default(self):
        assert _as_float("bad", default=2.5, minimum=0.0) == pytest.approx(2.5)


# ── _as_optional_int ──────────────────────────────────────────────────────────


class TestAsOptionalInt:
    def test_none_returns_none(self):
        assert _as_optional_int(None, minimum=0) is None

    def test_empty_returns_none(self):
        assert _as_optional_int("", minimum=0) is None

    def test_valid_int(self):
        assert _as_optional_int(5, minimum=0) == 5

    def test_minimum_enforced(self):
        assert _as_optional_int(-1, minimum=0) == 0

    def test_invalid_returns_none(self):
        assert _as_optional_int("bad", minimum=0) is None


# ── _as_optional_float ────────────────────────────────────────────────────────


class TestAsOptionalFloat:
    def test_none_returns_none(self):
        assert _as_optional_float(None, minimum=0.0) is None

    def test_empty_returns_none(self):
        assert _as_optional_float("", minimum=0.0) is None

    def test_valid_float(self):
        assert _as_optional_float(0.5, minimum=0.0) == pytest.approx(0.5)

    def test_minimum_enforced(self):
        assert _as_optional_float(-1.0, minimum=0.0) == pytest.approx(0.0)


# ── _as_int_map ───────────────────────────────────────────────────────────────


class TestAsIntMap:
    def test_basic_map(self):
        result = _as_int_map({"a": 2, "b": 3}, minimum=1)
        assert result == {"a": 2, "b": 3}

    def test_non_dict_returns_empty(self):
        assert _as_int_map("not-a-dict", minimum=0) == {}

    def test_minimum_enforced_per_value(self):
        result = _as_int_map({"a": -5}, minimum=0)
        assert result["a"] == 0

    def test_keys_lowercased(self):
        result = _as_int_map({"KEY": 1}, minimum=0)
        assert "key" in result


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
