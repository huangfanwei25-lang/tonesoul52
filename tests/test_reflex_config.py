"""Tests for tonesoul.governance.reflex_config."""

from __future__ import annotations

import json
from pathlib import Path

from tonesoul.governance.reflex_config import ReflexConfig, load_reflex_config


def test_defaults_are_governance_safe():
    cfg = ReflexConfig()
    assert cfg.enabled is True
    assert cfg.vow_enforcement_mode == "hard"
    assert cfg.council_block_enforcement is True
    assert cfg.soul_band_thresholds["alert"] == 0.30
    assert cfg.soul_band_thresholds["strained"] == 0.55
    assert cfg.soul_band_thresholds["critical"] == 0.80


def test_to_dict_round_trips():
    cfg = ReflexConfig(
        enabled=False,
        vow_enforcement_mode="soft",
        caution_prompt_threshold=0.5,
        risk_prompt_threshold=0.8,
    )
    d = cfg.to_dict()
    assert d["enabled"] is False
    assert d["vow_enforcement_mode"] == "soft"
    assert d["council_block_enforcement"] is True
    assert d["caution_prompt_threshold"] == 0.5
    assert d["risk_prompt_threshold"] == 0.8


def test_from_dict_applies_governance_floor_on_vow_mode():
    cfg = ReflexConfig.from_dict({"vow_enforcement_mode": "off"})
    assert cfg.vow_enforcement_mode == "soft"


def test_from_dict_council_block_cannot_be_disabled():
    cfg = ReflexConfig.from_dict({"council_block_enforcement": False})
    assert cfg.council_block_enforcement is True


def test_from_dict_custom_thresholds():
    cfg = ReflexConfig.from_dict({
        "soul_band_thresholds": {"alert": 0.20, "strained": 0.50, "critical": 0.75},
        "caution_prompt_threshold": 0.55,
        "risk_prompt_threshold": 0.70,
        "tension_reflection_threshold": 0.65,
        "soul_integral_reflection_threshold": 0.45,
    })
    assert cfg.soul_band_thresholds["alert"] == 0.20
    assert cfg.caution_prompt_threshold == 0.55
    assert cfg.risk_prompt_threshold == 0.70
    assert cfg.tension_reflection_threshold == 0.65
    assert cfg.soul_integral_reflection_threshold == 0.45


def test_from_dict_invalid_threshold_type_falls_back_to_defaults():
    cfg = ReflexConfig.from_dict({"soul_band_thresholds": "not-a-dict"})
    assert cfg.soul_band_thresholds == {"alert": 0.30, "strained": 0.55, "critical": 0.80}


def test_load_reflex_config_missing_file_returns_defaults(tmp_path):
    cfg = load_reflex_config(repo_root=tmp_path)
    assert cfg.vow_enforcement_mode == "hard"
    assert cfg.enabled is True


def test_load_reflex_config_reads_from_json(tmp_path):
    config_data = {
        "enabled": False,
        "vow_enforcement_mode": "soft",
        "caution_prompt_threshold": 0.45,
    }
    (tmp_path / "reflex_config.json").write_text(
        json.dumps(config_data), encoding="utf-8"
    )
    cfg = load_reflex_config(repo_root=tmp_path)
    assert cfg.enabled is False
    assert cfg.vow_enforcement_mode == "soft"
    assert cfg.caution_prompt_threshold == 0.45


def test_load_reflex_config_malformed_json_returns_defaults(tmp_path):
    (tmp_path / "reflex_config.json").write_text("{ broken json }", encoding="utf-8")
    cfg = load_reflex_config(repo_root=tmp_path)
    assert cfg.vow_enforcement_mode == "hard"
